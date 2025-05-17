
import json
import requests
import pandas as pd
from utils.xml_parsers import parse_xml, parse_sdn, parse_swiss, parse_un
from db.db_utils import connect_db, insert_entity, insert_aliases, insert_nationalities, insert_sanction_types

# Map parser keys to functions
PARSERS = {
    "ofac": parse_xml,
    "un": parse_un,
    "sdn": parse_sdn,
       # not used since UK CSV is handled separately
    "swiss": parse_swiss
}

def is_html(content):
    try:
        return b"<html" in content.lower()
    except Exception:
        return False

def read_csv_data(csv_file):
    """Read CSV, converting empty or 'null' values to None."""
    df = pd.read_csv(csv_file, keep_default_na=True, na_values=['', 'null', 'NULL', 'N/A'])
    df = df.rename(columns={
        'SanctionType': 'Sanction Type',
    })
    df = df.where(pd.notnull(df), None)
    return df.to_dict('records')


def main():
    # Load source list
    with open("config/sources.json") as f:
        sources = json.load(f)

    # Open DB connection once
    conn = connect_db()
    cursor = conn.cursor()
    print("Connected to database successfully")

    # Process each source
    for src in sources:
        source_name = src["sanction_type"]
        parser_key = src.get("parser")
        parser_func = PARSERS.get(parser_key)

        print(f"→ Processing {source_name} with parser '{parser_key}'")

        # Handle UK directly from CSV, bypass parser since there missing value present in column desingation so we predicted and used that value. 
        if source_name.lower() == "uk":
            try:
                csv_path = r'C:\Users\acer\OneDrive\Desktop\New folder\New folder (3)\designation_predic.csv'
                records = read_csv_data(csv_path)
                print(f"  [DEBUG] Loaded {len(records)} records from CSV for UK")
            except Exception as e:
                print(f"  [ERROR] Failed to load CSV for {source_name}: {e}")
                continue
        else:
            if not parser_func:
                print(f"  [ERROR] No parser available for '{parser_key}', skipping {source_name}")
                continue

            # Fetch XML content (URL or local file)
            try:
                if "url" in src:
                    resp = requests.get(src["url"])
                    content = resp.content
                    if is_html(content):
                        print(f"  [WARN] {source_name} URL returned HTML, skipping.")
                        continue
                else:
                    with open(src["path"], "rb") as f:
                        content = f.read()
            except Exception as e:
                print(f"  [ERROR] Fetch failed for {source_name}: {e}")
                continue

            # Parse XML content
            try:
                records = parser_func(content, source_name)
                print(f"  [DEBUG] Parsed {len(records)} records from XML for {source_name}")
            except Exception as e:
                print(f"  [ERROR] Parsing failed for {source_name}: {e}")
                continue

        # Insert records into DB
        for rec in records:
            eid = insert_entity(cursor, rec)
            insert_aliases(cursor, eid, rec.get("Alias"))
            insert_nationalities(cursor, eid, rec.get("Nationality"))
            insert_sanction_types(cursor, eid, rec.get("Sanction Type"))

        conn.commit()
        print(f"  ✔ Inserted {len(records)} records for {source_name}\n")

    # Clean up
    cursor.close()
    conn.close()
    print("All sources processed.")

if __name__ == "__main__":
    main()
