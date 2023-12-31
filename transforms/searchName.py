import trio
from maltego_trx.maltego import MaltegoTransform, MaltegoMsg
from maltego_trx.transform import DiscoverableTransform
from extensions import registry, judy_set
from modules import lookup

@registry.register_transform(
    display_name="Get judyrecords search records [judy]", 
    input_entity="maltego.Person",
    description='Returns search records from www.judyrecords.com using name',
    settings=[],
    output_entities=["maltego.Unknown"],
    transform_set=judy_set
    )
class searchName(DiscoverableTransform):
    
    @classmethod
    def create_entities(cls, request: MaltegoMsg, response: MaltegoTransform):

        async def main():

            # Retrieve name from entity
            search_terms = request.Value

            # Conduct search from judyrecords
            judy = lookup.judy()
            judy.addSearchJob(search_terms, "name")
            status = judy.checkJobStatus()["status"]
            records = judy.aggregateResults(status)

            # Convert records to entities
            for record in records:
                judyrecord = response.addEntity("maltego.judyRecord")
                judyrecord.addProperty("Record", value = record["Record"])
                judyrecord.addProperty("properties.url", value = record["url"])
                judyrecord.addProperty("snippet", value = record["snippet"])

        trio.run(main) # running our async code in a non-async code