import trio
from maltego_trx.maltego import MaltegoTransform, MaltegoMsg
from maltego_trx.transform import DiscoverableTransform
from extensions import registry, judy_set
from modules import lookup
import json

# Error Handling
def add_entity(entity_meta, value: list, response):
    try:
        for item in value:
            if item:
                new_entity = response.addEntity(entity_meta["type"], value=item)
                if entity_meta["additional_properties"]:
                    for prop_key, prop_value in entity_meta["additional_properties"].items():
                        new_entity.addProperty(prop_key, value=prop_value)
                if entity_meta["label_link"]:
                    new_entity.setLinkLabel(entity_meta["key"])
    except Exception as e:
        response.addUIMessage("Conversion to {} entity failed: {}".format(entity_meta["type"], str(e)))


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

            with open("data/entity_types.json", "r") as json_file:
                entity_types = json.load(json_file)

            # Conduct search from judyrecords
            judy = lookup.judy()
            record = judy.caseDetails(record)
            
            for entity in entity_types:
                if entity["key"] in record and record[entity["key"]]:
                    add_entity(entity, record[entity["key"]], response)
            
        trio.run(main) # running our async code in a non-async code