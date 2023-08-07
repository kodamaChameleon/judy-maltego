import trio
from maltego_trx.maltego import MaltegoTransform, MaltegoMsg
from maltego_trx.transform import DiscoverableTransform
from extensions import registry, judy_set
import judyRecords

@registry.register_transform(
    display_name="Get judyrecords search results [judy]", 
    input_entity="maltego.Phrase",
    description='Returns search results from www.judyrecords.com using phrase',
    settings=[],
    output_entities=["maltego.Unknown"],
    transform_set=judy_set
    )
class searchPhrase(DiscoverableTransform):
    
    @classmethod
    def create_entities(cls, request: MaltegoMsg, response: MaltegoTransform):

        async def main():

            # Retrieve name from entity
            search_terms = request.Value

            # Conduct search from judyrecords
            judy = judyRecords.judy()
            judy.addSearchJob(search_terms, "phrase")
            status = judy.checkJobStatus()["status"]
            records = judy.aggregateResults(status)

            # Convert results to entities
            for record in records:
                judyRecord = response.addEntity("maltego.judyRecord")
                judyRecord.addProperty("title", value = record["Title"])
                judyRecord.addProperty("properties.url", value = record["url"])
                judyRecord.addProperty("snippet", value = record["snippet"])

        trio.run(main) # running our async code in a non-async code