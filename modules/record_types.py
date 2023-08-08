# Handle records using generic format names
def type_1(record, soup):

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

def type_2(record, soup):

    try:
        record["Case_Type"] = soup.find('li', text='Case Type:').find_next('li').text.strip()
    except AttributeError:
        record["Case_Type"] = ""

    try:
        record["Judge"] = soup.find('li', text='Case Judge:').find_next('li').text.strip()
    except AttributeError:
        record["Judge"] = ""

    try:
        record["DOB"] = soup.find('li', text='DOB').find_next('li', class_="ptyPersInfo").text.strip()
    except AttributeError:
        record["DOB"] = ""

    try:
        record["Address"] = soup.find('li', text='Address').find_next('li', class_="ptyContactInfo").text.strip()
    except AttributeError:
        record["Address"] = ""

    try:
        record["Phone"] = soup.find('li', text='Phone').find_next('li', class_="ptyContactInfo").text.strip()
    except AttributeError:
        record["Phone"] = ""

    target_strings = [' - DEFENDANT ', ' - defendant ', ' - Defendant ']
    defendants = []
    for item in target_strings:
        defendants += soup.find_all('div', text=item, class_="ptyType")

    if defendants:
        record["Defendent"] = []

        for defendant in defendants:
            name = defendant.parent.find('div').text.strip()
            record["Defendent"].append(name)

    target_strings = [' - PLAINTIFF ', ' - plaintiff ', ' - Plaintiff ']
    plaintiffs = []
    for item in target_strings:
        plaintiffs += soup.find_all('div', text=item, class_="ptyType")

    if plaintiffs:
        record["Plaintiff"] = []

        for plaintiff in plaintiffs:
            name = plaintiff.parent.find('div').text.strip()
            record["Plaintiff"].append(name)

    return record

def type_3(record, soup):

    try:
        record["Reference_Link"] = soup.find('div', class_="accessInstructions").find('a')['href']
    except:
        None

    return record

def type_4(record, soup):

    target_classes = ['col-md-12', 'col-md-4', 'col-md-8']
    key_phrase = {
        "Case Number": "Case_Number",
        "File Date": "Date_Filed",
        "Case Type": "Case_Type",
        "Plaintiff/Petitioner": "Plaintiff",
        "Defendant/Respondant": "Defendant",
        "Judicial Officer": "Judge"
    }

    for class_ in target_classes:
        elements = soup.find_all('div', class_ = class_)
        for element in elements:
            text = element.get_text().strip()
            if text:
                for key, value in key_phrase.items():
                    if key in text and value in ["Plaintiff", "Defendant"]:
                        if value in record:
                            record[value].append(text.replace(key, "").strip())
                        else:
                            record[value] = [text.replace(key, "").strip()]

                    elif key in text:
                        record[value] = text.replace(key, "").strip()

    return record

def type_5(record, soup):

    tables = soup.find_all('table')
    for table in tables:
        columns = len(table.find_all('td'))
        rows = len(table.find_all('tr'))
        
        if rows == 2:
            for column_index in range(columns):
                record[table.find_all('tr')[0].find_all('td')[column_index]] = table.find_all('tr')[1].find_all('td')[column_index]

        print("hello")

    return record
