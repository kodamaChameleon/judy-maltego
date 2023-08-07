<img src="./img/judy-maltego2.png">

### Retrieve Judyrecord.com Results in Maltego

[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)

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
   git clone https://github.com/kodamaChameleon/twilio-maltego.git
   cd twilio-maltego
   python3 setup.py
```

Import Judy-Maltego.mtz and entities from the entities folder into Maltego to begin running locally.

## 🧙 Features

<img src="./img/judy_demo.png" width="600px">

| Name               | Description                                                       | Input              |
|--------------------|-------------------------------------------------------------------|--------------------|
| searchName         | Returns search results from www.judyrecords.com using name        | maltego.Person     |
| toCaseDetails      | Extracts case details from judyrecords.com using url              | maltego.judyRecord |

   
## 📜 License
<img src="https://creativecommons.org/images/deed/FreeCulturalWorks_seal_x2.jpg" height="100px">

[Creative Commons Attribution-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-sa/4.0/)  
Copyright (C) 2023 KodamaChameleon
