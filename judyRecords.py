import requests
from bs4 import BeautifulSoup
import json

# Error code handling
def check_status(response):

    if response.status_code == 200:
        return True
    else:
        print(f"Error: Unable to fetch the search results. Status code: {response.status_code}")
        return False

class judy:

    def __init__(self) -> None:
        self.addSearch_Url = "https://www.judyrecords.com/addSearchJob"
        self.searchStatus_Url = "https://www.judyrecords.com/getSearchJobStatus"
        self.results_Url = "https://www.judyrecords.com/getSearchResults/?page="
        self.headers = { 
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        self.cookies = None

    # Create a search
    def addSearchJob(self, search_terms):

        # Construct the search URL
        search_terms_encoded = '+'.join(search_terms.split())
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
                "Title": a_tag.get_text(),
                "url": "https://judyrecords.com" + a_tag['href'],
                "snippet": concatenated_snippet
            }

            results["records"].append(record)

        # Identify the number of pages
        page_urls = soup.find_all('a', {'data-ref-page': True})
        if page_urls:
            last_div = page_urls[-1]
            last_page_value = last_div['data-ref-page']

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

        # Send the search request
        response = requests.get(record["url"], headers=self.headers)

        # Parse response for urls
        soup = BeautifulSoup(response.content, 'html.parser')

        # Identify case number by class="ssCaseDetailCaseNbr"
        record["case_number"] = soup.find('div', class_='ssCaseDetailCaseNbr').find('span').get_text()
        record["defendent"] = soup.find('th', class_='ssTableHeader', id='PIr11').get_text()

        charges_element = soup.find('caption', text='Charge Information')
        if charges_element:

            tbody = charges_element.find_parent('table')
            headers = []
            for th_element in tbody.find_all('th'):
                text = th_element.get_text().replace(record['defendent'], "").strip()
                if text:
                    headers.append(text)
            rows = []
            for td_element in tbody.find_all('td'):
                text = td_element.get_text().strip()
                if text:
                    rows.append(text)

            charges = dict(zip(headers, rows[1:]))
            record.update(charges)

        return record


# if __name__ == "__main__":
#     search_terms = input("Enter your search terms separated by spaces: ")
#     judy = judy()
#     judy.addSearchJob(search_terms)
#     status = judy.checkJobStatus()["status"]
#     records = judy.aggregateResults(status)
#     for record in records:
#         judy.caseDetails(record)