"""
FOR DEVELOPMENT PURPOSES ONLY

These methods are used to test record collection, data scraping, and sort supported record types.

"""
from modules import lookup
import json


# Test record scrapes
def scrape_record(record):

    judy = lookup.judy()
    record = judy.caseDetails(record)
    
    return record


 # Test search functions
def search_records(search_terms, type_):
    judy = lookup.judy()
    judy.addSearchJob(search_terms, "name")
    status = judy.checkJobStatus()["status"]
    records = judy.aggregateResults(status)

    return records

# Sort supported record types
def sort_and_remove_duplicates(json_file_path):
    with open(json_file_path, 'r') as f:
        record_types = json.load(f)

    if isinstance(record_types, dict):
        sorted_unique_record_types = dict(sorted(record_types.items()))

        with open(json_file_path, 'w') as f:
            record_types = sorted_unique_record_types
            json.dump(record_types, f, indent=4)

        print(f"Sorted and unique 'Record Types' written back to {json_file_path}")
    else:
        print("No 'Record Types' found in the JSON data.")


# Uncomment to test
# search_records("Al Capone", "name")
# scrape_record({"url":"https://www.judyrecords.com/record/cyn1an4bd3", "Record": "Gonzales County, Texas Jail Record"})
# sort_and_remove_duplicates("data/record_types.json")

with open("test_cases.json", "r") as json_file:
    test_cases = json.load(json_file)
for case in test_cases:
    scrape_record(case)