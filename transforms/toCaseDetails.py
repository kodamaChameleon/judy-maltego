import trio
from maltego_trx.maltego import MaltegoTransform, MaltegoMsg
from maltego_trx.transform import DiscoverableTransform
from extensions import registry, judy_set
import judyRecords

# Define how to convert data types
class tranx:

    def __init__(self, record, response) -> None:
        self.record = record
        self.response = response
        pass

    def case_number(self):
        caseNumber = self.response.addEntity("maltego.UniqueIdentifier", value = self.record["case_number"])
        caseNumber.addProperty("identifierType", value = "Case Number")

    def charges(self):
        self.response.addEntity("maltego.Phrase", value = self.record["Charges"])

    def statute(self):
        statute_number = self.response.addEntity("maltego.UniqueIdentifier", value = self.record["Statute"])
        statute_number.addProperty("identifierType", value = "Statute")

    def level(self):
        self.response.addEntity("maltego.hashtag", value = self.record["Level"])

    def defendent(self):
        self.response.addEntity("maltego.Person", value = self.record["defendent"])

    def date(self):
        self.response.addEntity("maltego.DateTime", value = self.record["Date"])


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
            record_url = {
                "url": request.Value,
            }

            # Conduct search from judyrecords
            judy = judyRecords.judy()
            record = judy.caseDetails(record_url)
            
            # 
            convert_records = tranx(record, response)
            available_entities = {
                "case_number": convert_records.case_number(),
                "Charges": convert_records.charges(),
                "Statue": convert_records.statute(),
                "Level": convert_records.level(),
                "defendent": convert_records.defendent(),
                "Date": convert_records.date(),
            }

            # Convert results to entities
            for key in record:
                if record[key] and key in available_entities:
                    available_entities[key]
            

        trio.run(main) # running our async code in a non-async code