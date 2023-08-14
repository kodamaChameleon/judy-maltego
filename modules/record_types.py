import json

# Normalize record
def normalize(key_transforms, record):
    new_record = {}  # Create a new dictionary to store the modified record
    
    for key, value in record.items():
        if key in key_transforms:
            new_key = key_transforms[key]
            new_record[new_key] = value
        else:
            new_record[key] = value
    
    return new_record

# Create new list if list does not exist
def check_key(record, key, value):
    if value:
        if key in record:
            record[key].append(value)
        else:
            record[key] = [value]

    return record

# Extract data from tables
def extract_table(table, record):

    headers = ['#']
    rows = []
    if table.find_all('th'):
        for th_element in table.find_all('th'):
            text = th_element.get_text().split(':')[0].strip()
            if text:
                headers.append(text)
        
        for td_element in table.find_all('td'):
            text = td_element.get_text().strip()
            if text:
                rows.append(text)
    else:
        row_elements = table.find_all('tr')
        for th_element in row_elements[0].find_all('td'):
            text = th_element.get_text().split(':')[0].strip()
            if text:
                headers.append(text)
        
        for row in row_elements[1:]:
            for td_element in row.find_all('td'):
                text = td_element.get_text().strip()
                if text:
                    rows.append(text)


    for i in range(len(rows)):

        # Match rows and headers
        effective_header_index = i % len(headers)
        current_row = rows[i]
        current_header = headers[effective_header_index]

        record = check_key(record, current_header, current_row)

    return record

# Classify record type by fingerprint
def fingerprint(soup):

    # Initialize variable
    record_type = None

    try:

        # Test at least 3 metrics
        if (soup.find('div', class_="ssCaseDetailROA", text="Register of Actions")\
            or soup.find('div', class_="ssCaseDetailROA", text="Chronological Case Summary"))\
            and soup.find('caption', text="Party Information")\
            and soup.find('caption', text="Events & Orders of the Court"):

            record_type = 1

        elif soup.find(id="titleBar")\
            and soup.find(id="caseHeader")\
            and soup.find(id="CaseDetailPanelTabSection"):

            record_type = 2

        elif soup.find('div', class_="pageCopy")\
            and soup.find('div', class_="accessInstructions")\
            and soup.find('p', class_="toAccessThisRecordDirectly"):

            record_type = 3

        elif soup.find(id="divCaseInformation_header")\
            and (soup.find('div', class_="col-md-4") or soup.find('div', class_="col-md-8") or soup.find('div', class_="col-md-12"))\
            and soup.find(id="divCaseInformation_body"):

            record_type = 4

        elif soup.find('td', text="Trial Court Case ID")\
            and soup.find('td', text="Speedy Trial")\
            and soup.find('td', text="Microfilm Ref")\
            and len(soup.find_all('table')) == 2:

            record_type = 5

        elif (soup.find('div', class_="ssCaseDetailROA", text="Register of Actions")\
            or soup.find('div', class_="ssCaseDetailROA", text="Chronological Case Summary"))\
            and soup.find('div', class_="ssCaseDetailSectionTitle", text="Party Information")\
            and soup.find('div', class_="ssCaseDetailSectionTitle",  text="Events & Orders of the Court"):

            record_type = 6

    except:
        pass

    return record_type

# Update supported_records json
def update_supported(record):

    json_file_path = "data/supported_records.json"
    with open(json_file_path, 'r') as f:
        record_types = json.load(f)

    if isinstance(record_types, dict):
        record_types[record["Record"]] = record["Type"]
        sorted_unique_record_types = dict(sorted(record_types.items()))

        with open(json_file_path, 'w') as f:
            record_types = sorted_unique_record_types
            json.dump(record_types, f, indent=4)

# Handle records using generic format names
def type_1(record, soup):

    record_page = soup.find('article', class_="record page")
    
    try:
        record["Case Number"] = [record_page.find('div', class_='ssCaseDetailCaseNbr').find('span').get_text().strip()]
    except:
        pass

    fields = {
        "Case Type:",
        "Subtype:",
        "Date Filed:",
        "Location:",
        "Cross-Reference Case Number:"
    }
    
    for field_name in fields:
        try:
            value = record_page.find('th', text=field_name).find_parent('tr').find('td').text.strip()
            record.update({field_name: [value]})
        except:
            pass
    
    party_element = record_page.find('div', text='Party Information')
    if party_element:
        table = party_element.find_parent('table')

        for tr_element in table.find_all('tr'):
            th_elements = tr_element.find_all('th')
            try:
                header, value = [th_elements[n].get_text().strip() for n in range(2)]
                record = check_key(record, header, value)
            except:
                pass

    charges_element = record_page.find('div', text='Charge Information')
    if charges_element:

        table = charges_element.find_parent('table')
        record = extract_table(table, record)

    key_transforms = {
        "Case Type:": "Case Type",
        "Subtype:": "SubType",
        "Date Filed:": "Date Filed",
        "Location:": "Location",
        "Cross-Reference Case Number:": "Cross Reference",
        "Date": "Offense Date"
    }

    return normalize(key_transforms, record)

def type_2(record, soup):

    record_page = soup.find('article', class_="record page")

    field_extraction = [
        ("Case Type:", ""),
        ("Case Status:", ""),
        ("Case Judge:", ""),
        ("Offense Date", ""),
        ("DOB", "ptyPersInfo"),
        ("Address", "ptyContactInfo"),
        ("Phone", "ptyContactInfo")
    ]

    for key, class_id in field_extraction:
        try:
            key_elements = record_page.find('li', text=key)
            for element in key_elements:
                if class_id:
                    value = element.find_next('li', class_=class_id).text.strip()
                    record = check_key(record, key, value)
                else:
                    value = element.find_next('li').text.strip()
                    record = check_key(record, key, value)
        except:
            pass

    # Find parties involved
    party_info = record_page.find(id='ptyInfo')
    member_type = [text.get_text().strip() for text in party_info.find_all('div', class_="ptyType")]
    member_name = [text.get_text().strip() for text in party_info.find_all('div', class_="ptyInfoLabel")]
    for i in range(len(member_type)):
        record = check_key(record, member_type[i], member_name[i])

    # Find charges
    try:
        record["Charges"] = [text.get_text().strip() for text in record_page.find(id="chgInfo").find_all('div', class_="chrg")]
    except:
        pass

    key_transforms = {
        "Case Type:": "Case Type",
        "Case Status:": "Case Status",
        "Case Judge:": "Judge",
        "- DEFENDANT": "Defendant",
        "- Defendant": "Defendant"
    }

    return normalize(key_transforms, record)

def type_3(record, soup):

    try:
        record["Reference Link"] = [soup.find('div', class_="accessInstructions").find('a')['href']]
    except:
        None

    return record

def type_4(record, soup):

    record_page = soup.find('article', class_="record page")


    # Locate items by key phrase where key and value are in same element
    target_classes = ['col-md-12', 'col-md-4', 'col-md-8']

    key_phrase = {
        "Case Number",
        "File Date",
        "Case Type",
        "Plaintiff/Petitioner",
        "Defendant/Respondant",
        "Judicial Officer",
        "Plaintiff",
        "Defendant",
        "DOB",
        "Case Status",
        "File Date",
        "Respondent",
        "Petitioner"
    }

    for class_ in target_classes:
        div_elements = record_page.find_all('div', class_ = class_)
        
        for div_element in div_elements:
            p_elements = div_element.find_all('p')

            for p_element in p_elements:
                text = p_element.get_text().strip()

                for key in key_phrase:
                    if key in text:
                        text = text.replace(key, "").strip()
                        record = check_key(record, key, text)

    # Extract charges table
    try:
        table = record_page.find(id="chargeInformationDiv").find("table")
        record = extract_table(table, record)
    except:
        pass
    
    key_transforms = {
        "Case Number": "Case Number",
        "File Date": "Date Filed",
        "Case Type": "Case Type",
        "Plaintiff/Petitioner": "Plaintiff",
        "Defendant/Respondant": "Defendant",
        "Judicial Officer": "Judge",
        "Description": "Charges",
        "Date": "Offense Date"
    }

    return normalize(key_transforms, record)


def type_5(record, soup):

    table_elements = soup.find('article', class_="record page").find_all("table")
    
    # Get Case details
    rows = table_elements[0].find_all('tr')
    headers = []
    data = []
    for x in range(len(rows)):
        if x in [1,3]:
            for column in rows[x].find_all('td'):
                headers.append(column.get_text().strip())
        elif x in [2,4]:
            for column in rows[x].find_all('td'):
                data.append(column.get_text().strip())

    for x in range(len(headers)):
        if data[x]:
            record = check_key(record, headers[x], data[x])

    for row in table_elements[1].find_all('tr')[2:]:
        columns = row.find_all('td')

        # Add party information
        record = check_key(record, columns[1].get_text().strip(), columns[0].get_text().replace("County Specific Financial Summary Search", "").strip())

        # Add DOB(s)
        record = check_key(record, "DOB", columns[2].get_text().strip())
        record["Case Status"] = [columns[3].get_text().strip()]

    key_transforms = {
        "Trial Court Case ID": "Case Number",
        "Created": "Date Filed",
        "Originating County": "Location",
        "Citation Number": "Citation",
        "DEFENDANT": "Defendant",
        "PLAINTIFF": "Plaintiff"
    }

    return normalize(key_transforms, record)

def type_6(record, soup):

    record_page = soup.find('article', class_="record page")
    
    try:
        record["Case Number"] = [record_page.find('div', class_='ssCaseDetailCaseNbr').find('span').get_text().strip()]
    except:
        pass

    fields = {
        "Case Type:",
        "Subtype:",
        "Date Filed:",
        "Location:",
        "Cross-Reference Case Number:",
        "Judicial Officer:",
        "Uniform Case Number:"
    }
    
    for field_name in fields:
        try:
            value = record_page.find('td', text=field_name).find_next('td').text.strip()
            record.update({field_name: [value]})
        except:
            pass
    
    party_element = record_page.find('div', text='Party Information')
    if party_element:
        table = party_element.next_sibling

        for tr_element in table.find_all('tr'):
            th_elements = tr_element.find_all('th')
            try:
                header, value = [th_elements[n].get_text().strip() for n in range(2)]
                record = check_key(record, header, value)
            except:
                pass

    charges_element = record_page.find('div', text='Charge Information')
    if charges_element:

        table = charges_element.next_sibling
        record = extract_table(table, record)

    key_transforms = {
        "Case Type:": "Case Type",
        "Subtype:": "SubType",
        "Date Filed:": "Date Filed",
        "Location:": "Location",
        "Cross-Reference Case Number:": "Cross Reference",
        "Date": "Offense Date",
        "Judicial Officer:": "Judge"
    }

    return normalize(key_transforms, record)