import trio
from maltego_trx.maltego import MaltegoTransform, MaltegoMsg
from maltego_trx.transform import DiscoverableTransform
from extensions import registry, judy_set
import judge
from datetime import datetime
import re
import geocoder

def format_text(input_str:str, proper=False):
    # List of articles to exclude from capitalization
    articles = ["a", "an", "the", "of", "for", "by", "on"]

    if proper:
        # Split the input string into words
        words = input_str.split()

        # Capitalize the first letter of each word (except articles)
        formatted_words = []
        for word in words:
            if word.lower() not in articles:
                formatted_words.append(word.capitalize())
            else:
                formatted_words.append(word.lower())

        # Join the formatted words back into a string
        result_str = " ".join(formatted_words)
    else:
        # Convert the input string to lowercase
        result_str = input_str.lower()

    return result_str

def format_dates(date_str):
    # Define a list of date formats to try parsing
    date_formats = ["%m/%d/%Y", "%m-%d-%Y", "%m.%d.%Y", "%m/%d/%y", "%m-%d-%y", "%m.%d.%y"]
    
    for date_format in date_formats:
        try:
            # Try to parse the date string using the current format
            parsed_date = datetime.strptime(date_str, date_format)
            
            # If successful, format it in MM/DD/YYYY and return
            return parsed_date.strftime("%m/%d/%Y")
        except ValueError:
            continue
    
    # If none of the formats match, return None or raise an exception
    raise ValueError("Unable to parse the date string")

def format_phone_number(phone_number):
    # Remove all non-digit characters from the phone number
    digits_only = re.sub(r"\D", "", phone_number)

    # Check the length of the cleaned phone number
    if len(digits_only) == 10:
        # Standardize to (XXX) XXX-XXXX format
        standardized_number = f"({digits_only[0:3]}) {digits_only[3:6]}-{digits_only[6:]}"
    elif len(digits_only) > 10:
        # Standardize to 1-XXX-XXX-XXXX format
        standardized_number = f"+{digits_only[0:-10]} ({digits_only[-10:-7]}) {digits_only[-7:-4]}-{digits_only[-4:]}"
    else:
        # If the phone number doesn"t match a known format, return it as is
        standardized_number = phone_number

    return standardized_number

# Format locations with geocoder
def format_location(address):
    maltego_dict= {}
    geocoder_dict =  geocoder.osm(address).json
    if geocoder_dict.get("status") == "OK":
        maltego_dict["country"] = geocoder_dict.get("country")
        maltego_dict["city"] = geocoder_dict.get("city") or geocoder_dict.get("region") or geocoder_dict.get("state")
        maltego_dict["streetaddress"] = geocoder_dict.get("street", "") + " " + geocoder_dict.get("housenumber", "")
        maltego_dict["location.areacode"] = geocoder_dict.get("postal", "")
        maltego_dict["area"] = geocoder_dict.get("county", "")
        maltego_dict["countrycode"] = geocoder_dict.get("country_code", "")
        maltego_dict["longitude"] = geocoder_dict.get("lng", "")
        maltego_dict["latitude"] = geocoder_dict.get("lat", "")

    return maltego_dict


@registry.register_transform(
    display_name="Extrapolate record details [judy]", 
    input_entity="maltego.judyRecord",
    description="Extracts case details from judyrecords.com using url",
    settings=[],
    output_entities=["maltego.Unknown"],
    transform_set=judy_set
    )
class toCaseDetails(DiscoverableTransform):
    
    @classmethod
    def create_entities(cls, request: MaltegoMsg, response: MaltegoTransform):

        async def main():

            # Retrieve name from entity
            record = {
                "url": request.Value,
                "Record": request.getProperty("Record")
            }

            # Conduct search from judyrecords
            judy = judge.judy()
            record = judy.caseDetails(record)
            
            # Iterate through People results
            for person in record["People"]:
                if person["Name"]:

                    # Create person entity with link describing role
                    name = format_text(person["Name"], proper = True)
                    person_entity = response.addEntity("maltego.Person", value = name)
                    if person["Role"]:
                        person_entity.setLinkLabel(format_text(person["Role"]))
                    
                    # Create additional PII entities with link label describing to whom they belong (combining in dynamic properties risk overwriting details)
                    person_details = {}
                    for x in range(len(person["Aliases"])):
                        if person["Aliases"][x]:
                            person_details["alias_"+x] = response.addEntity("maltego.Alias", value = format_text(person["Aliases"][x], proper = True))

                    if person["DOB"]:
                        person_details["DOB"] = response.addEntity("maltego.DateTime", value = format_dates(person["DOB"]))

                    if person["Phone"]:
                        person_details["Phone"] = response.addEntity("maltego.PhoneNumber", value = format_phone_number(person["Phone"]))

                    if person["Address"]:
                        person_details["Address"] = response.addEntity("maltego.Location", value = format_text(person["Address"], proper = True))

                        location_data = format_location(person["Address"])
                        for property,value in location_data.items():
                            person_details["Address"].addProperty(property, value = value)

                    for entity in person_details:
                        person_details[entity].addProperty("Associated_with", value = name)

            # Iterate through case descriptors
            case_entity = False
            if record["Case Information"]["Case Number"]:
                case_entity = response.addEntity("maltego.UniqueIdentifier", value = record["Case Information"]["Case Number"])
                case_entity.addProperty("identifierType", value = "Case Number")
            elif record["Case Information"]["Case Title"]:
                case_entity = response.addEntity("maltego.UniqueIdentifier", value = record["Case Information"]["Case Title"])
                case_entity.addProperty("identifierType", value = "Case Number")
            if case_entity:
                for key,value in record["Case Information"].items():
                    if value and value != case_entity.value:
                        case_entity.addProperty(key, value = format_text(value))
            
            # Iterate through charges
            for charge in record["Charges"]:
                if charge["Description"]:
                    charge_entity = response.addEntity("maltego.Phrase", value = charge["Description"])

                    for key, value in charge.items():
                        if key != "Description" and value:
                            if key in ["Name"]:
                                charge_entity.addProperty(key, value = format_text(value, proper = True))
                            else:
                                charge_entity.addProperty(key, value = format_text(value))

            # Iterate external references
            for ref in record["External Ref"]:
                response.addEntity("maltego.Website", value = ref)

        trio.run(main) # running our async code in a non-async code