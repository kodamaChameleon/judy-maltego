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
    if key in record:
        record[key].append(value)
    else:
        record[key] = [value]

    return record

# Extract data from tables
def extract_table(table, record):

    headers = ['#']
    for th_element in table.find_all('th'):
        text = th_element.get_text().split(':')[0].strip()
        if text:
            headers.append(text)
    rows = []
    for td_element in table.find_all('td'):
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
    
    party_element = record_page.find('caption', text='Party Information')
    if party_element:
        table = party_element.find_parent('table')
        for tr_element in table.find_all('tr'):
            th_elements = tr_element.find_all('th')
            try:
                header, value = [th_elements[n].get_text().strip() for n in range(2)]
                record = check_key(record, header, value)
            except:
                pass

    charges_element = record_page.find('caption', text='Charge Information')
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

    target_tables = soup.find_all('table')
    header_conversion = {
        "Case Number": "Case_Number",
        "Date": "Date_Filed",
        "Date Filed": "Date_Filed",
        "Offense Date": "Date",
        "Mailing address": "Address",
        "Attorney Phone": "Phone",
        "Offense Description": "Charges",
        "Case": "Cross_Reference",
        "Judge/Magistrate": "Judge",
    }
    for table in target_tables:
        try:
            headers = [header.get_text().strip() for header in table.select('tr:nth-of-type(1) > td')]
            converted_headers = [header_conversion[header] if header in header_conversion else header for header in headers]
            data = [cell.get_text().strip() for cell in table.select('tr:nth-of-type(2) > td')]
            if len(data) == len(converted_headers):
                record.update(dict(zip(converted_headers, data)))

            # if header in header_conversion:
            #     header = header_conversion[header]

        except:
            continue

    return record
