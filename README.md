<img src="./img/judy-maltego2.png">

### Retrieve Judyrecord.com Results in Maltego

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

Version: 1.0.0-beta

## 💎 About

Retreives search results from [judyrecords](https://judyrecords.com). For more information about the terms of judyrecords, see [terms](https://judyrecords.com/terms).

Please use this tool ethically by respecting people's privacy and only collecting intelligence where explicit permission has been granted or otherwise legally qualified to do so. We are not responsible for any illegal use.

## 🛠️ Setup

### Requirements
- Maltego 4.3.0
- [Python 3.11.2](./requirements.txt)

   
### Installation
```
   git clone https://github.com/kodamaChameleon/judy-maltego.git
   cd judy-maltego
   python3 setup.py
```

Import Judy-Maltego.mtz and entities from the entities folder into Maltego to begin running locally.

## 🧙 Features

<img src="./img/judy_demo.png" width="600px">

| Name               | Description                                                       | Input              |
|--------------------|-------------------------------------------------------------------|--------------------|
| searchName         | Returns search results from www.judyrecords.com using name        | maltego.Person     |
| searchPhrase       | Returns search results from www.judyrecords.com using a phrase    | maltego.Phrase     |
| toCaseDetails      | Extracts case details from judyrecords.com using url              | maltego.judyRecord |

**Supported Records**  
Judyrecords advertises millions of records making it virtually impossible to cover every record type. If a record type is not supported, results will still come back using searchName or searchPhrase; however, toCaseDetails will return "Unsupported Record Type."  
- Las Vegas, Nevada Justice Court Record
- Clark County, Nevada Court Record
- North Las Vegas, Nevada Municipal Court Record
- District Court, E.D. Pennsylvania Record
- District Court, N.D. Illinois Record
- District Court, N.D. Indiana Record
- District Court, D. New Jersey Record
- Chatham County, Georgia Court Record
- Grand Rapids, Michigan District Court Record
- Missouri Court Record
- United States Bankruptcy Court, S.D. Mississippi Record

Don't see a record you are interested in? Create an issue for us with the name of the record type and an example record you want added (i.e. `https://judyrecords.com/record/<record number here>`)
   
## 📜 License
<img src="https://creativecommons.org/images/deed/FreeCulturalWorks_seal_x2.jpg" height="100px">

[Creative Commons Attribution-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-sa/4.0/)  
Copyright (C) 2023 KodamaChameleon
