import trio
from maltego_trx.maltego import MaltegoTransform, MaltegoMsg
from maltego_trx.transform import DiscoverableTransform
from extensions import registry, judy_set
import judyRecords

@registry.register_transform(
    display_name="Get judyrecords search results [judy]", 
    input_entity="maltego.Person",
    description='Returns search results from www.judyrecords.com using name',
    settings=[],
    output_entities=["maltego.Unknown"],
    transform_set=judy_set
    )
class searchName(DiscoverableTransform):
    
    @classmethod
    def create_entities(cls, request: MaltegoMsg, response: MaltegoTransform):

        async def main():

            # Retrieve name from entity
            name = request.Value

            # Conduct search from judyrecords
            judy = judyRecords.judy()
            judy.addSearchJob(name)
            status = judy.checkJobStatus()["status"]
            records = judy.aggregateResults(status)

            # Convert results to entities
            for record in records:
                judyRecord = response.addEntity("maltego.judyRecord")
                judyRecord.addProperty("title", value = record["Title"])
                judyRecord.addProperty("properties.url", value = record["link"])
                judyRecord.addProperty("snippet", value = record["snippet"])

        trio.run(main) # running our async code in a non-async code