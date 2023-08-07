import trio
from maltego_trx.maltego import MaltegoTransform, MaltegoMsg
from maltego_trx.transform import DiscoverableTransform
from extensions import registry, judy_set
import judyRecords

# Error Handling
def add_entity(entity_type, value, response, additional_properties=None):
    try:
        entity = response.addEntity(entity_type, value=value)
        if additional_properties:
            for prop_key, prop_value in additional_properties.items():
                entity.addProperty(prop_key, value=prop_value)
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

            # List available entity types
            available = [
                {
                    "key": "case_number",
                    "type": "maltego.UniqueIdentifier",
                    "additional_properties": {
                        "identifierType": "Case Number"
                    }
                },
                {
                    "key": "Charges",
                    "type": "maltego.Phrase",
                    "additional_properties": {}
                },
                {
                    "key": "Statute",
                    "type": "maltego.UniqueIdentifier",
                    "additional_properties": {
                        "identifierType": "Statute"
                    }
                },
                {
                    "key": "Level",
                    "type": "maltego.hashtag",
                    "additional_properties": {}
                },
                {
                    "key": "defendent",
                    "type": "maltego.Person",
                    "additional_properties": {}
                },
                {
                    "key": "Date",
                    "type": "maltego.DateTime",
                    "additional_properties": {}
                },
            ]

            for entity in available:
                if entity["key"] in record:
                    add_entity(entity["type"], record[entity["key"]], response, entity["additional_properties"])
            

        trio.run(main) # running our async code in a non-async code