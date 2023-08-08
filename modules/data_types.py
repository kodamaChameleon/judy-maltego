# Handle records from Las Vegas, Nevada Justice Court Record
def nevada_courts(record, soup):

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