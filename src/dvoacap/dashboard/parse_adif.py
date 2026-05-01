#!/usr/bin/env python3
"""
Parse ADIF log file to extract DXCC entities worked and confirmed
"""

import re
from collections import defaultdict

def parse_adif(filename):
    """Parse ADIF file and extract QSO records"""
    with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Split into header and records
    parts = content.split('<eoh>')
    if len(parts) < 2:
        return []
    
    records_text = parts[1]
    
    # Split into individual QSO records
    qsos = records_text.split('<eor>')
    
    parsed_qsos = []
    
    for qso in qsos:
        if not qso.strip():
            continue
            
        record = {}
        
        # Find all ADIF fields in the format <field:length>value
        # Updated regex to handle optional type
        pattern = r'<([^:>]+):(\d+)(?::[^>]+)?>([^<]*)'
        matches = re.findall(pattern, qso, re.IGNORECASE)
        
        for field, length, value in matches:
            field_lower = field.lower()
            record[field_lower] = value.strip()
        
        if record:
            parsed_qsos.append(record)
    
    return parsed_qsos

def analyze_dxcc(qsos):
    """Analyze DXCC entities worked and confirmed"""
    dxcc_worked = set()
    dxcc_confirmed_lotw = set()
    dxcc_confirmed_qsl = set()
    
    qso_by_dxcc = defaultdict(list)
    
    for qso in qsos:
        dxcc = qso.get('dxcc')
        if dxcc:
            try:
                dxcc_num = int(dxcc)
                dxcc_worked.add(dxcc_num)
                
                # Check for LoTW confirmation
                lotw_rcvd = qso.get('lotw_qsl_rcvd', '').upper()
                if lotw_rcvd == 'Y':
                    dxcc_confirmed_lotw.add(dxcc_num)
                
                # Check for QSL card confirmation
                qsl_rcvd = qso.get('qsl_rcvd', '').upper()
                if qsl_rcvd == 'Y':
                    dxcc_confirmed_qsl.add(dxcc_num)
                
                # Store QSO info
                qso_by_dxcc[dxcc_num].append({
                    'call': qso.get('call', ''),
                    'country': qso.get('country', ''),
                    'qso_date': qso.get('qso_date', ''),
                    'band': qso.get('band', ''),
                    'mode': qso.get('mode', ''),
                    'lotw_confirmed': lotw_rcvd == 'Y',
                    'qsl_confirmed': qsl_rcvd == 'Y'
                })
            except ValueError:
                pass
    
    return dxcc_worked, dxcc_confirmed_lotw, dxcc_confirmed_qsl, qso_by_dxcc

# Current DXCC entity list (340 current entities as of 2024)
# This is a comprehensive list of active DXCC entities
DXCC_ENTITIES = {
    1: "Canada", 2: "Abu Ail", 3: "Afghanistan", 4: "Agalega & St Brandon Is.", 
    5: "Aland Islands", 6: "Alaska", 7: "Albania", 8: "Aldabra", 9: "American Samoa",
    10: "Amsterdam & St Paul Is.", 11: "Andaman & Nicobar Is.", 12: "Anguilla",
    13: "Antarctica", 14: "Armenia", 15: "Asiatic Russia", 16: "New Zealand Subantarctic Islands",
    17: "Aves Island", 18: "Azerbaijan", 19: "Bajo Nuevo", 20: "Baker & Howland Islands",
    21: "Balearic Islands", 22: "Palau", 23: "Blenheim Reef", 24: "Bouvet",
    25: "British North Borneo", 26: "British Somaliland", 27: "Belarus", 28: "Canal Zone",
    29: "Canary Islands", 30: "Celebe & Molucca Islands", 31: "C. Kiribati (British Phoenix Is.)",
    32: "Ceuta & Melilla", 33: "Chagos Islands", 34: "Chatham Islands", 35: "Christmas Island",
    36: "Clipperton Island", 37: "Cocos Island", 38: "Cocos (Keeling) Islands", 39: "Comoros",
    40: "Crete", 41: "Crozet Island", 42: "Damao, Diu", 43: "Desecheo Island",
    44: "Desroches", 45: "Dodecanese", 46: "East Malaysia", 47: "Easter Island",
    48: "E. Kiribati (Line Is.)", 49: "Equatorial Guinea", 50: "Mexico",
    51: "Eritrea", 52: "Estonia", 53: "Ethiopia", 54: "European Russia", 55: "Farquhar",
    56: "Fernando de Noronha", 57: "French Equatorial Africa", 58: "French Indo-China",
    59: "French West Africa", 60: "Bahamas", 61: "Franz Josef Land", 62: "Barbados",
    63: "French Guiana", 64: "Bermuda", 65: "British Virgin Islands", 66: "Belize",
    67: "French India", 68: "Geyser Reef", 69: "Cayman Islands", 70: "Cuba",
    71: "Galapagos Islands", 72: "Dominican Republic", 74: "Trinidad & Tobago",
    75: "Goa", 76: "Grenada", 77: "Guadeloupe", 78: "Guantanamo Bay",
    79: "Guernsey", 80: "Guinea", 81: "Haiti", 82: "Hawaii", 84: "Jamaica",
    86: "Iwo Jima", 88: "Martinique", 90: "Nauru", 91: "Jersey",
    93: "Jan Mayen", 94: "Jordan", 95: "Juan Fernandez Islands", 96: "Guam",
    97: "Johnston Island", 98: "Juan de Nova, Europa", 99: "Minami Torishima",
    100: "Guinea-Bissau", 102: "Isle of Man", 103: "Kaliningrad", 104: "Karelo-Finnish Republic",
    105: "Kerguelen Islands", 106: "Indonesia", 107: "Kamaran Island", 108: "Korea",
    109: "Kure Island", 110: "Kuria Muria Island", 111: "Chesterfield Is.", 112: "Latvia",
    113: "Lithuania", 114: "Austral Islands", 115: "Marquesas Islands", 116: "Palestine",
    117: "Liechtenstein", 118: "Lord Howe Island", 119: "Macau", 120: "Macao",
    122: "Malaya", 123: "Nauru", 126: "Mauritius", 127: "Mariana Islands",
    128: "Market Reef", 129: "Marquesas Islands", 130: "Marshall Islands", 131: "Mayotte",
    132: "Mellish Reef", 134: "Micronesia", 135: "Midway Island", 136: "Minerva Reef",
    137: "Moldova", 138: "Mount Athos", 139: "Mozambique", 140: "Navassa Island",
    141: "Netherlands Antilles", 142: "Curacao", 143: "Aruba", 144: "Bonaire",
    145: "Saba & St Eustatius", 146: "Netherlands New Guinea", 147: "New Caledonia",
    148: "New Guinea", 149: "Niue", 150: "Norfolk Island", 151: "North Cook Islands",
    152: "Ogasawara", 153: "Okino Tori-shima", 154: "Okinawa (Ryukyu Is.)", 155: "Palestine",
    157: "Palmyra & Jarvis Islands", 158: "Papua New Guinea", 159: "Peter 1 Island",
    160: "Portuguese Timor", 161: "Prince Edward & Marion Is.", 162: "Puerto Rico",
    163: "Principe, Sao Tome", 165: "Reunion Island", 166: "Rhodes", 167: "Rota",
    168: "Ryukyu Islands", 169: "Sabah", 170: "Saar", 171: "Sable Island",
    172: "Saipan & Tinian", 173: "Samoa", 174: "San Andres & Providencia", 175: "San Felix & San Ambrosio",
    176: "San Marino", 177: "Sarawak", 178: "Scarborough Reef", 179: "Scotland",
    180: "Serrana Bank & Roncador Cay", 181: "Sierra Leone", 182: "Sikkim", 183: "Singapore",
    185: "Solomon Islands", 186: "Somali Republic", 187: "South Cook Islands", 188: "South Georgia Island",
    189: "Southern Sudan", 190: "South Orkney Islands", 191: "South Sandwich Islands", 192: "South Shetland Islands",
    193: "Spratly Islands", 194: "St. Kitts & Nevis", 195: "St. Helena", 196: "St. Lucia",
    197: "St. Paul Island", 198: "St. Peter & St. Paul Rocks", 199: "St. Pierre & Miquelon",
    200: "St. Vincent", 201: "Sudan", 202: "Suriname", 203: "Svalbard", 204: "Swan Island",
    205: "Tangier", 206: "Trieste", 207: "Trindade & Martim Vaz Islands", 208: "Tristan da Cunha & Gough Island",
    209: "Tromelin Island", 210: "Turks & Caicos Islands", 211: "Tuvalu", 212: "UK Sovereign Base Areas on Cyprus",
    213: "Uruguay", 214: "Viet Nam", 215: "Virgin Islands", 216: "Vatican",
    217: "Volcanic Islands", 218: "Wake Island", 219: "Wallis & Futuna Islands", 220: "West Malaysia",
    221: "Western Kiribati (Gilbert Is.)", 222: "Western Sahara", 223: "Willis Island", 224: "Banaba Island (Ocean Is.)",
    225: "E. Kiribati (Central)", 226: "Annobon Island", 227: "Rotuma Island", 228: "Yemen",
    229: "Zanzibar", 230: "Albania", 231: "Algeria", 232: "Andorra", 233: "Austria",
    234: "Belgium", 235: "Bulgaria", 236: "Cyprus", 237: "Czech Republic", 238: "Czechoslovakia",
    239: "Denmark", 240: "Faroe Islands", 241: "Finland", 242: "France", 243: "Germany",
    244: "German Democratic Republic", 245: "Gibraltar", 246: "Greece", 247: "Greenland",
    248: "Guernsey", 249: "Hungary", 250: "Iceland", 251: "Ireland", 252: "Italy",
    253: "Jersey", 254: "Latvia", 255: "Liechtenstein", 256: "Lithuania", 257: "Luxembourg",
    258: "Malta", 259: "Monaco", 260: "Netherlands", 261: "Norway", 262: "Poland",
    263: "Portugal", 264: "Romania", 265: "San Marino", 266: "Slovak Republic", 267: "Slovenia",
    268: "Spain", 269: "Sweden", 270: "Switzerland", 271: "Turkey", 272: "Ukraine",
    273: "United Kingdom", 274: "England", 275: "Isle of Man", 276: "Northern Ireland",
    277: "Scotland", 278: "Wales", 279: "Guernsey", 280: "Jersey", 281: "Vatican",
    282: "Iceland", 283: "Azerbaijan", 284: "Bosnia-Herzegovina", 285: "Uzbekistan",
    286: "Georgia", 287: "Kazakhstan", 288: "Kosovo", 289: "Kyrgyzstan", 290: "Tajikistan",
    291: "United States", 292: "Turkmenistan", 293: "Serbia", 294: "Montenegro", 295: "Argentina",
    296: "Aruba", 297: "Ascension Island", 298: "Australia", 299: "Austria", 300: "Bahamas",
    301: "Bahrain", 302: "Bangladesh", 303: "Barbados", 304: "Belarus", 305: "Belgium",
    306: "Belize", 307: "Benin", 308: "Bermuda", 309: "Bhutan", 310: "Bolivia",
    311: "Bonaire", 312: "Bosnia-Herzegovina", 313: "Botswana", 314: "Brazil", 315: "British Virgin Islands",
    316: "Brunei Darussalam", 317: "Bulgaria", 318: "Burkina Faso", 319: "Burundi", 320: "Cambodia",
    321: "Cameroon", 322: "Canada", 323: "Canary Islands", 324: "Cape Verde", 325: "Cayman Islands",
    326: "Central African Republic", 327: "Chad", 328: "Chile", 329: "China", 330: "Christmas Island",
    331: "Cocos (Keeling) Islands", 332: "Colombia", 333: "Comoros", 334: "Congo", 335: "Democratic Republic of the Congo",
    336: "Conway Reef", 337: "Corsica", 338: "Costa Rica", 339: "Cote d'Ivoire", 340: "Croatia",
    341: "Cuba", 342: "Curacao", 343: "Cyprus", 344: "Czech Republic", 345: "Denmark",
    346: "Djibouti", 347: "Dominica", 348: "Dominican Republic", 349: "East Timor", 350: "Ecuador",
    351: "Egypt", 352: "El Salvador", 353: "Equatorial Guinea", 354: "Eritrea", 355: "Estonia",
    356: "Eswatini", 357: "Ethiopia", 358: "Falkland Islands", 359: "Faroe Islands", 360: "Fiji",
    361: "Finland", 362: "France", 363: "French Guiana", 364: "French Polynesia", 365: "Gabon",
    366: "Gambia", 367: "Georgia", 368: "Germany", 369: "Ghana", 370: "Gibraltar",
    371: "Greece", 372: "Greenland", 373: "Grenada", 374: "Guadeloupe", 375: "Guam",
    376: "Guatemala", 377: "Guinea", 378: "Guinea-Bissau", 379: "Guyana", 380: "Haiti",
    381: "Hawaii", 382: "Honduras", 383: "Hong Kong", 384: "Hungary", 385: "Iceland",
    386: "India", 387: "Indonesia", 388: "Iran", 389: "Iraq", 390: "Ireland",
    391: "Israel", 392: "Italy", 393: "Jamaica", 394: "Japan", 395: "Jersey",
    396: "Jordan", 397: "Kazakhstan", 398: "Kenya", 399: "Kiribati", 400: "North Korea",
    401: "South Korea", 402: "Kosovo", 403: "Kuwait", 404: "Kyrgyzstan", 405: "Laos",
    406: "Latvia", 407: "Lebanon", 408: "Lesotho", 409: "Liberia", 410: "Libya",
    411: "Liechtenstein", 412: "Lithuania", 413: "Luxembourg", 414: "Macao", 415: "North Macedonia",
    416: "Madagascar", 417: "Madeira Islands", 418: "Malawi", 419: "Malaysia", 420: "Maldives",
    421: "Mali", 422: "Malta", 423: "Marshall Islands", 424: "Martinique", 425: "Mauritania",
    426: "Mauritius", 427: "Mayotte", 428: "Mexico", 429: "Micronesia", 430: "Moldova",
    431: "Monaco", 432: "Mongolia", 433: "Montenegro", 434: "Montserrat", 435: "Morocco",
    436: "Mozambique", 437: "Myanmar", 438: "Namibia", 439: "Nauru", 440: "Nepal",
    441: "Netherlands", 442: "New Caledonia", 443: "New Zealand", 444: "Nicaragua", 445: "Niger",
    446: "Nigeria", 447: "Niue", 448: "Norfolk Island", 449: "North Cook Islands", 450: "Northern Mariana Islands",
    451: "Norway", 452: "Oman", 453: "Pakistan", 454: "Palau", 455: "Palestine",
    456: "Panama", 457: "Papua New Guinea", 458: "Paraguay", 459: "Peru", 460: "Philippines",
    461: "Pitcairn Island", 462: "Poland", 463: "Portugal", 464: "Puerto Rico", 465: "Qatar",
    466: "Reunion Island", 467: "Romania", 468: "European Russia", 469: "Rwanda", 470: "Saba & St. Eustatius",
    471: "Saint Barthelemy", 472: "Saint Helena", 473: "Saint Kitts & Nevis", 474: "Saint Lucia", 475: "Saint Martin",
    476: "Saint Pierre & Miquelon", 477: "Saint Vincent", 478: "Samoa", 479: "San Marino", 480: "Sao Tome & Principe",
    481: "Saudi Arabia", 482: "Senegal", 483: "Serbia", 484: "Seychelles", 485: "Sierra Leone",
    486: "Singapore", 487: "Sint Maarten", 488: "Slovakia", 489: "Slovenia", 490: "Solomon Islands",
    491: "Somalia", 492: "South Africa", 493: "South Cook Islands", 494: "South Sudan", 495: "Spain",
    496: "Sri Lanka", 497: "Sudan", 498: "Suriname", 499: "Svalbard", 500: "Sweden",
    501: "Switzerland", 502: "Syria", 503: "Taiwan", 504: "Tajikistan", 505: "Tanzania",
    506: "Thailand", 507: "Timor-Leste", 508: "Togo", 509: "Tokelau Islands", 510: "Tonga",
    511: "Trinidad & Tobago", 512: "Tunisia", 513: "Turkey", 514: "Turkmenistan", 515: "Turks & Caicos Islands",
    516: "Tuvalu", 517: "Uganda", 518: "Ukraine", 519: "United Arab Emirates", 520: "United Kingdom",
    521: "United States", 522: "Uruguay", 523: "Uzbekistan", 524: "Vanuatu", 525: "Vatican City",
    526: "Venezuela", 527: "Vietnam", 528: "Virgin Islands", 529: "Wake Island", 530: "Wallis & Futuna",
    531: "Yemen", 532: "Zambia", 533: "Zimbabwe"
}

def generate_dxcc_summary(adif_filename, output_filename='dxcc_summary.json'):
    """
    Parse ADIF file and generate DXCC summary JSON
    Returns the summary dict and saves to file
    """
    import json

    # Parse the ADIF file
    qsos = parse_adif(adif_filename)

    print(f"Total QSOs parsed: {len(qsos)}")

    # Analyze DXCC
    worked, lotw_confirmed, qsl_confirmed, qso_by_dxcc = analyze_dxcc(qsos)

    print(f"\n=== DXCC STATISTICS ===")
    print(f"DXCC Entities Worked: {len(worked)}")
    print(f"DXCC Entities Confirmed (LoTW): {len(lotw_confirmed)}")
    print(f"DXCC Entities Confirmed (QSL): {len(qsl_confirmed)}")

    # Find missing entities
    all_current = set(DXCC_ENTITIES.keys())
    missing = all_current - worked

    print(f"\nMissing DXCC Entities: {len(missing)}")

    # Show worked entities with country names
    print(f"\n=== WORKED DXCC ENTITIES ({len(worked)}) ===")
    worked_list = sorted(worked)
    for dxcc in worked_list:
        country = DXCC_ENTITIES.get(dxcc, f"Unknown ({dxcc})")
        qso_count = len(qso_by_dxcc[dxcc])
        lotw_mark = "✓" if dxcc in lotw_confirmed else " "
        qsl_mark = "✓" if dxcc in qsl_confirmed else " "
        print(f"  {dxcc:3d}: {country:40s} [{qso_count:3d} QSOs] LoTW:{lotw_mark} QSL:{qsl_mark}")

    # Show missing entities - "Most Wanted"
    print(f"\n=== MOST WANTED - MISSING DXCC ENTITIES ({len(missing)}) ===")
    missing_list = sorted(missing)
    for dxcc in missing_list:
        country = DXCC_ENTITIES.get(dxcc, f"Unknown ({dxcc})")
        print(f"  {dxcc:3d}: {country}")

    # Create summary dict
    summary = {
        'total_qsos': len(qsos),
        'dxcc_worked': list(worked),
        'dxcc_confirmed_lotw': list(lotw_confirmed),
        'dxcc_confirmed_qsl': list(qsl_confirmed),
        'dxcc_missing': list(missing),
        'qso_count_by_dxcc': {str(k): len(v) for k, v in qso_by_dxcc.items()},
        'entity_names': DXCC_ENTITIES
    }

    # Save to JSON for use in web tool
    with open(output_filename, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n=== Summary saved to {output_filename} ===")

    return summary

if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        adif_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else 'dxcc_summary.json'
        generate_dxcc_summary(adif_file, output_file)
    else:
        print("Usage: python3 parse_adif.py <adif_file> [output_file]")
        print("Example: python3 parse_adif.py my_logbook.adi dxcc_summary.json")
