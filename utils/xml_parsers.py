
import xml.etree.ElementTree as ET

def parse_un(xml_data: str, source: str):
    """
    Parses the UN Sanctions List (both individuals and entities) into unified flat records.
    """
    root = ET.fromstring(xml_data)
    records = []

    # Handle INDIVIDUALS
    for individual in root.findall('.//INDIVIDUAL'):
        first = individual.findtext('FIRST_NAME', '').strip()
        second = individual.findtext('SECOND_NAME', '').strip()
        third = individual.findtext('THIRD_NAME', '').strip()
        full_name = ' '.join(filter(None, [first, second, third])) or 'Unknown'

        alias_elements = individual.findall('INDIVIDUAL_ALIAS')
        alias = alias_elements[0].findtext('ALIAS_NAME').strip() if alias_elements else None

        nationality_elements = individual.findall('NATIONALITY/VALUE')
        nationality = nationality_elements[0].text.strip() if nationality_elements else 'Unknown'

        designation_elements = individual.findall('DESIGNATION/VALUE')
        designation = designation_elements[0].text.strip() if designation_elements else 'individual'

        sanction_type = individual.findtext('UN_LIST_TYPE', 'Unknown').strip()

        records.append({
            "Name": full_name,
            "Alias": alias,
            "Nationality": nationality,
            "Designation": designation,
            "Sanction Type": sanction_type,
            "Source": source
        })

    # Handle ENTITIES
    for entity in root.findall('.//ENTITY'):
        name = entity.findtext('FIRST_NAME', 'Unknown').strip()

        alias_elements = entity.findall('ENTITY_ALIAS')
        alias = alias_elements[0].findtext('ALIAS_NAME').strip() if alias_elements else None

        nationality_elements = entity.findall('NATIONALITY/VALUE')
        nationality = nationality_elements[0].text.strip() if nationality_elements else 'Unknown'

        designation = 'entity'

        sanction_type = entity.findtext('UN_LIST_TYPE', 'Unknown').strip()

        records.append({
            "Name": name,
            "Alias": alias,
            "Nationality": nationality,
            "Designation": designation,
            "Sanction Type": sanction_type,
            "Source": source
        })

    return records


def parse_xml(xml_data: str, source: str):

    """
    Parses an OFAC SDN feed and returns a list of dicts with keys:
      Name, Alias, Nationality, Designation, Sanction Type, Source, Date of Birth, Place of Birth
    """
    ns_uri = ET.fromstring(xml_data).tag
    ns = {'ns': ns_uri[ns_uri.find("{")+1 : ns_uri.find("}")]}
    
    records = []
    for entry in ET.fromstring(xml_data).findall(".//ns:sdnEntry", ns):
        # 1) Name
        fn = entry.findtext("ns:firstName", default="", namespaces=ns)
        ln = entry.findtext("ns:lastName",  default="", namespaces=ns)
        name = f"{fn} {ln}".strip() or entry.findtext("ns:programList", default="Unknown", namespaces=ns)
        
        # 2) Alias
        aka = entry.findtext("ns:akaList/ns:aka/ns:lastName", default="None", namespaces=ns)
        
        # 3) Nationality
        nationality = entry.findtext(
            "ns:nationalityList/ns:nationality/ns:country",
            default="Unknown",
            namespaces=ns
        )
        
        # 4) Designation (sdnType)
        designation = entry.findtext("ns:sdnType", default="Unknown", namespaces=ns)
        
        # 5) Sanction Type(s) = all <program> under <programList>
        programs = entry.findall("ns:programList/ns:program", ns)
        sanction_types = [p.text for p in programs if p is not None]
        sanction_type_str = ", ".join(sanction_types) if sanction_types else "Unknown"
        
        # # 6) Date / Place of Birth (you already have these)
        # dob = entry.findtext("ns:dateOfBirthList/ns:dateOfBirthItem/ns:dateOfBirth",
        #                      default="Unknown", namespaces=ns)
        # pob = entry.findtext("ns:placeOfBirthList/ns:placeOfBirthItem/ns:placeOfBirth",
        #                      default="Unknown", namespaces=ns)
        
        # 7) Source (constant passed in)
        source_val = source
        
        records.append({
            "Name":           name,
            "Alias":          aka,
            "Nationality":    nationality,
            "Designation":    designation,
            "Sanction Type":  sanction_type_str,
            "Source":         source_val,
            # "Date of Birth":  dob,
            # "Place of Birth": pob
        })
    
    return records


def parse_sdn(xml_data: bytes, source: str):
    """
    Parses the usoafc-sdn Sanctions List into the unified schema:
      Name, Alias, Nationality, Designation, Sanction Type, Source
    """
    root = ET.fromstring(xml_data)

    # 1) Build a map of sanctions-set IDs → English description
    set_map = {}
    for prog in root.findall('sanctions-program'):
        for s in prog.findall("sanctions-set[@lang='eng']"):
            sid = s.get('ssid')
            set_map[sid] = s.text.strip()

    records = []
    # 2) Loop over each <target>
    for tgt in root.findall('target'):
        # a) collect all referenced sanctions-set IDs, map to text
        sids = [e.text for e in tgt.findall('sanctions-set-id')]
        sanction_types = [ set_map.get(sid, sid) for sid in sids ]
        sanction_type_str = ', '.join(sanction_types) if sanction_types else 'Unknown'

        # b) find the individual node
        indiv = tgt.find('individual')
        if indiv is None:
            continue

        # c) Name: identity/name/name-part/value
        name = indiv.findtext(
            'identity/name/name-part/value',
            default='Unknown'
        ).strip()

        # d) Alias: not present in this feed, so we'll default to None
        alias = None

        # e) Nationality: identity/nationality/country
        nationality = indiv.findtext(
            'identity/nationality/country',
            default='Unknown'
        ).strip()

        # f) Designation: the fact that this is an <individual>
        designation = 'individual'

        records.append({
            "Name":           name,
            "Alias":          alias,
            "Nationality":    nationality,
            "Designation":    designation,
            "Sanction Type":  sanction_type_str,
            "Source":         source
        })

    return records

# this function parses the xml file as this had missing value so we will predict the missing value and will be using that.
# def parse_uk(xml_data: str, source: str):
#     """
#     Parses the UK Sanctions List into a unified schema:
#     Name, Alias, Nationality, Designation, Sanction Type, Source.

#     - Keeps 'Alias' key as None if missing.
#     - Skips rows where 'Nationality' is missing.
#     """
#     root = ET.fromstring(xml_data)
#     results = []

#     for designation in root.findall('Designation'):
#         # --- Names ---
#         name = None
#         aliases = []
#         names_element = designation.find('Names')

#         if names_element is not None:
#             for name_el in names_element.findall('Name'):
#                 name_text = (name_el.findtext('Name6') or '').strip()
#                 name_type = (name_el.findtext('NameType') or '').strip()

#                 if name_type == 'Primary Name' and name_text:
#                     name = name_text
#                 elif (name_text and name_text.strip() and 
#                       name_text not in ['-', 'None', 'N/A', '', ' ']):  # Strict alias validation
#                     aliases.append(name_text)

#         if not name and aliases:
#             name = aliases.pop(0)

#         alias_str = None if not aliases else ', '.join(aliases)

#         # --- Nationality ---
#         nationality = []
#         for addr in designation.findall('Addresses/Address'):
#             country = (addr.findtext('AddressCountry') or '').strip()
#             if country:
#                 nationality.append(country)

#         if not nationality:
#             continue

#         nationality_str = ', '.join(sorted(set(nationality)))

#         # --- Other fields ---
#         regime_name = (designation.findtext('RegimeName') or '').strip()
#         sanction_type = regime_name if 'Regulations' in regime_name else None
#         designation_name = None
#         positions = designation.findall('.//Positions/Position')
#         if positions:
#             designation_name = positions[0].text.strip()

#         raw_sanctions = (designation.findtext('SanctionsImposed') or '').strip()
#         sanctions_imposed = ', '.join([s.strip() for s in raw_sanctions.split('|') if s.strip()]) or None

#         entry = {
#             "Name": name or None,
#             "Alias": alias_str,
#             "Nationality": nationality_str,
#             "Designation": designation_name,
#             "Sanction Type": sanction_type or sanctions_imposed,
#             "Source": source
#         }

#         results.append(entry)

#     return results


def parse_swiss(xml_data: str, source: str):
    """
    Parses the Swiss Sanctions List into the unified schema:
    Name, Alias, Nationality, Designation, Sanction Type, Source
    """
    root = ET.fromstring(xml_data)
    records = []

    # Build a mapping from sanctions-set-id to designation (sanction type)
    ssid_to_designation = {}
    for prog in root.findall('sanctions-program'):
        for sset in prog.findall('sanctions-set'):
            ssid = sset.attrib.get('ssid')
            designation = sset.text.strip() if sset.text else ''
            ssid_to_designation[ssid] = designation

    # Parse each target (person/organization)
    for target in root.findall('target'):
        name = ''
        aliases = []
        nationalities = []

        # Get only one designation (first before comma)
        designation = None
        for ssid_elem in target.findall('sanctions-set-id'):
            ssid = ssid_elem.text
            if ssid and ssid in ssid_to_designation:
                full_designation = ssid_to_designation[ssid]
                designation = full_designation.split(',')[0].strip()
                break  # stop after first

        # Extract identity
        individual = target.find('individual')
        if individual is not None:
            identity = individual.find("identity[@main='true']")
            if identity is not None:
                # Get primary name
                name_elem = identity.find("name[@name-type='primary-name']")
                if name_elem is not None:
                    name_part = name_elem.find("name-part")
                    if name_part is not None and name_part.find("value") is not None:
                        name = name_part.find("value").text.strip()

                # Collect aliases
                for alt_name in identity.findall("name[@name-type!='primary-name']"):
                    part = alt_name.find("name-part")
                    if part is not None and part.find("value") is not None:
                        aliases.append(part.find("value").text.strip())

                # Get nationality
                for nat in identity.findall("nationality"):
                    for country in nat.findall("country"):
                        if country.text:
                            nationalities.append(country.text.strip())

        # Prepare alias string or None if empty
        alias_str = ', '.join(aliases).strip()
        if not alias_str:
            alias_str = None

        # Append record
        records.append({
            'Name': name if name else None,
            'Alias': alias_str,
            'Nationality': ', '.join(nationalities) if nationalities else None,
            'Designation': designation,
            'Sanction Type': 'Individual',
            'Source': source
        })

    return records