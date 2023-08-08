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

        # Select the format for the appropriate record type
        record_types = {
            "Las Vegas, Nevada Justice Court Record": lasVegas_nevada_justiceCourt(record, soup)
        }

        record = record_types[record["Title"]]

        return record
    
# Handle records from Las Vegas, Nevada Justice Court Record
def lasVegas_nevada_justiceCourt(record, soup):

    try:
        record["Case_Number"] = soup.find('div', class_='ssCaseDetailCaseNbr').find('span').get_text()
    except AttributeError:
        record["Case_Number"] = ""

    try:
        record["Case_Type"] = soup.find('th', text='Case Type:').find_parent('tr').find('td').text.strip()
    except AttributeError:
        record["Case_Type"] = ""

    try:
        record["Subtype"] = soup.find('th', text='Subtype:').find_parent('tr').find('td').text.strip()
    except AttributeError:
        record["Subtype"] = ""

    try:
        record["Date_Filed"] = soup.find('th', text='Date Filed:').find_parent('tr').find('td').text.strip()
    except AttributeError:
        record["Date_Filed"] = ""

    try:
        record["Location"] = soup.find('th', text='Location:').find_parent('tr').find('td').text.strip()
    except AttributeError:
        record["Location"] = ""

    try:
        record["Cross_Reference"] = soup.find('th', text='Cross-Reference Case Number:').find_parent('tr').find('td').text.strip()
    except AttributeError:
        record["Cross_Reference"] = ""

    defendants = soup.find_all('th', text='Defendant')
    if defendants:
        record["Defendent"] = []

        for defendant in defendants:
            name = defendant.find_next('th').text.strip()
            record["Defendent"].append(name)

    plaintiffs = soup.find_all('th', text='Plaintiff')
    if plaintiffs:
        record["Plaintiff"] = []

        for plaintiff in plaintiffs:
            name = plaintiff.find_next('th').text.strip()
            record["Plaintiff"].append(name)

    others = soup.find_all('th', text='Other')
    if others:
        record["Other"] = []

        for other in others:
            name = other.find_next('th').text.strip()
            record["Other"].append(name)

    charges_element = soup.find('caption', text='Charge Information')
    if charges_element:

        tbody = charges_element.find_parent('table')
        headers = []
        for th_element in tbody.find_all('th'):
            text = th_element.get_text().split(':')[0].strip()
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

    

#     def case_type(self, soup):

#         try:
#             
#         except:
#             try:
#                 record = {
#                     "Case_Type": soup.find('li', text='Case Type:').find_next('li').text.strip()
#                 }

#                 return record
#             except:
#                 None

#     def dob(self, soup):

#         try:
#             record = {
#                 "DOB": soup.find('li', text='DOB', class_="ptyAttyLabel").find_next('li', class_="ptyAttyInfo").text.strip()
#             }

#             return record
#         except:
#             None

#     def address(self, soup):

#         try:
#             record = {
#                 "Address": soup.find('li', text='Address', class_="ptyAttyLabel").find_next('li', class_="ptyAttyInfo").text.strip()
#             }

#             return record
#         except:
#             None

#     def phone(self, soup):

#         try:
#             record = {
#                 "Phone": soup.find('li', text='Phone', class_="ptyAttyLabel").find_next('li', class_="ptyAttyInfo").text.strip()
#             }

#             return record
#         except:
#             None

#     def cross_reference(self, soup):

#         try:
#             record = {
#                 "Cross_Reference": soup.find('th', text='Cross-Reference Case Number:').find_parent('tr').find('td').text.strip()
#             }

#             return record
#         except:
#             None

#     def date_filed(self, soup):

#         try:
#             record = {
#                 "Date_Filed": soup.find('th', text='Date Filed:').find_parent('tr').find('td').text.strip()
#             }

#             return record
#         except:
#             try:
#                 record = {
#                     "Date_Filed": soup.find('li', text='File Date:').find_next('li').text.strip()
#                 }

#                 return record
#             except:
#                 None

#     def defendent(self, soup):

#         try:
            
#             else:
#                 target_strings = [' - DEFENDANT ', ' - defendant ', ' - Defendant ']
#                 defendants = []
#                 for item in target_strings:
#                     defendants += soup.find_all('div', text=item)

#                 for defendant in defendants:
#                     name = defendant.parent.find('div').text.strip()
#                     record["Defendent"].append(name)

#             if record["Defendent"]:
#                 return record
#         except:
#             None
    
#     def plaintiff(self, soup):

#         try:
            
#             else:
#                 target_strings = [' - PLAINTIFF ', ' - plaintiff ', ' - Plaintiff ']
#                 plaintiffs = []
#                 for item in target_strings:
#                     plaintiffs += soup.find_all('div', text=item)

#                 for plaintiff in plaintiffs:
#                     name = plaintiff.parent.find('div').text.strip()
#                     record["Plaintiff"].append(name)

#             if record["Plaintiff"]:
#                 return record
#         except:
#             None
        
    
#     def charges(self, soup):

#         charges_element = soup.find('caption', text='Charge Information')
#         if charges_element:

#             tbody = charges_element.find_parent('table')
#             headers = []
#             for th_element in tbody.find_all('th'):
#                 text = th_element.get_text().split(':')[0].strip()
#                 if text:
#                     headers.append(text)
#             rows = []
#             for td_element in tbody.find_all('td'):
#                 text = td_element.get_text().strip()
#                 if text:
#                     rows.append(text)

#             charges = dict(zip(headers, rows[1:]))
#         else:
#             charges_element = soup.find('caption', text='Charges')

#             return charges
        
#     def location(self, soup):

#         try:
#             record = {
#                 "Location": soup.find('th', text='Location:').find_parent('tr').find('td').text.strip()
#             }

#             return record
#         except:
#             None