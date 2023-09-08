import requests
from bs4 import BeautifulSoup
import json
import openai

# Error code handling
def check_status(response):

    if response.status_code == 200:
        return True
    else:
        print(f"Error: Unable to fetch the search results. Status code: {response.status_code}")
        return False
    
# Read api_key to judy class
def read_api_key():
    key_path = "openai.key"
    try:
        with open(key_path, 'r') as key_file:
            api_key = key_file.read()

        return api_key
    except:
        raise ValueError('OpenAI API key not found')
    
# Get clean text from html
def fetch_text(url, headers):

    # Get text from URL
    response = requests.get(url, headers = headers)

    # Clean the response
    if response.ok:
        soup = BeautifulSoup(response.text, 'html.parser')
        text_list = soup.get_text(separator = '|#|').split('|#|')
        text = ''
        for t in text_list:
            if t not in ['\n','',' ']:
                text += ' ' + t.strip()
                
        return text

def structure_data(text, api_key):

    # Set up the OpenAI API client
    openai.api_key = api_key

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": 
             """Fill in as much of the json as possible. Set null if not found.{"People":[{"Name":"","Role": "" (Defendent, Plaintiff, Attorney, Judge, etc.),"Aliases":[""],"DOB": "","Phone":"","Address":""}],"Case Information":{"Case Title":""(usually something like Description, X vs Y),"Case Number":"","Case Type":"","Cross-Reference": "","Citation Number": "","Date Filed": "","Case Status": ""},"Charges":[{"Name":"" (should match a person in People list),"Description":"","Statute":"","Level":"","Offense Date": ""}],"External Ref":[<hyperlinks not from judyrecords.com>]}"""},
            {"role": "user", "content": text },
        ]
    )

    data = json.loads(response["choices"][0]["message"]["content"])

    return data

class judy:

    def __init__(self) -> None:
        self.addSearch_Url = "https://www.judyrecords.com/addSearchJob"
        self.searchStatus_Url = "https://www.judyrecords.com/getSearchJobStatus"
        self.results_Url = "https://www.judyrecords.com/getSearchResults/?page="
        self.headers = { 
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        self.cookies = None
        self.api_key = read_api_key()

    # Create a search
    def addSearchJob(self, search_terms, input_type):

        # Construct the search URL
        if input_type == "name":
            search_terms_encoded = '+'.join(search_terms.split()) + '%2C'*3
        if input_type == "phrase":
            search_terms_encoded = '%22' + '+'.join(search_terms.split()) + '%22'
        search_url = f"{self.addSearch_Url}?search={search_terms_encoded}"

        # Send the search request
        response = requests.get(search_url, headers=self.headers)

        # Return cookies of successful response
        if check_status(response):
            self.cookies = response.cookies

    # Check job status
    def checkJobStatus(self):

        response = requests.get(self.searchStatus_Url, headers=self.headers, cookies=self.cookies)

        # Return cookies of successful response
        if check_status(response):
            return json.loads(response.content.decode('utf-8'))
        
    # Scrape search result URLs
    def getSearchResults(self, page):

        response = requests.get(self.results_Url + str(page), headers=self.headers, cookies=self.cookies)

        # Parse response for urls
        soup = BeautifulSoup(response.content, 'html.parser')
        results = {
            "records": [],
            "last_page": page
        }
        
        for item in soup.find_all('div', class_='searchResultItem'):

            snippet_elements = item.find_all('div', class_='snippet')
            snippet_texts = [snippet.get_text() for snippet in snippet_elements]
            concatenated_snippet = ' '.join(snippet_texts)

            a_tag = item.find('a')

            record = {
                "Record": a_tag.get_text(),
                "url": "https://judyrecords.com" + a_tag['href'],
                "snippet": concatenated_snippet
            }

            results["records"].append(record)

        # Identify the number of pages
        page_urls = soup.find_all('a', {'data-ref-page': True})
        if page_urls:
            last_div = page_urls[-1]
            last_page_value = last_div['data-ref-page']
            results["last_page"] = last_page_value

        return results
    
    # Aggregate results of multiple pages
    def aggregateResults(self, status):

        if status == "succeeded":
            page = 1
            results = self.getSearchResults(page)

            while page <= int(results["last_page"]):
                page += 1
                results["records"].extend(self.getSearchResults(page)['records'])

            return results["records"]
        
    # Scrape case details from URL
    def caseDetails(self, record: dict):

        # Retreive cleaned text from record at url
        text = fetch_text(record["url"], headers=self.headers)

        # Utilize openai to structure the data
        data = structure_data(text, self.api_key)
        record.update(data)

        return record

