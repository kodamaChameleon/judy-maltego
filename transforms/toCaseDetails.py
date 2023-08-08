import trio
from maltego_trx.maltego import MaltegoTransform, MaltegoMsg
from maltego_trx.transform import DiscoverableTransform
from extensions import registry, judy_set
import judyRecords
import json

# Error Handling
def add_entity(key, entity_type, value, response, additional_properties=None):
    try:
        if isinstance(value, list):
            for item in value:
                entity = response.addEntity(entity_type, value=item)
                if additional_properties:
                    for prop_key, prop_value in additional_properties.items():
                        entity.addProperty(prop_key, value=prop_value)
                if key in ["Defendent", "Plaintiff", "Date", "Date_Filed", "DOB"]:
                    entity.setLinkLabel(key)
        else:
            entity = response.addEntity(entity_type, value=value)
            if additional_properties:
                for prop_key, prop_value in additional_properties.items():
                    entity.addProperty(prop_key, value=prop_value)
            if key in ["Defendent", "Date", "Date_Filed"]:
                entity.setLinkLabel(key)
    except KeyError as e:
        response.addUIMessage("Conversion to {} entity failed: {}".format(entity_type, str(e)))


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

            # From list of entity types, convert scraped data to entities
            with open("entity_types.json", "r") as json_file:
                entities_available = json.load(json_file)

            for entity in entities_available:
                if entity["key"] in record and record[entity["key"]]:
                    add_entity(entity["key"], entity["type"], record[entity["key"]], response, entity["additional_properties"])
            

        trio.run(main) # running our async code in a non-async code