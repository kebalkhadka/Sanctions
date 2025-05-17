# # import mysql.connector
# import pymysql
# from dotenv import load_dotenv
# import os

# load_dotenv()

# def connect_db():
#     try:
#         conn = pymysql.connect(
#             # host='localhost',
#             # user='root',
#             # password='',
#             # database='sanctions'
#             host=os.getenv("DB_HOST", "localhost"),
#             user=os.getenv("DB_USER", "root"),
#             password=os.getenv("DB_PASSWORD", ""),
#             database=os.getenv("DB_NAME", "sanctions"),
#             charset='utf8mb4',
#             cursorclass=pymysql.cursors.DictCursor
#         )
#         print("Connected to database successfully")
#         return conn
#     except pymysql.MySQLError as err:
#         print(f"Error: {err}")
#         return None

# # def insert_entity(cursor, record):
# #     # Check if entity already exists
# #     cursor.execute("""
# #         SELECT entity_id FROM sanctioned_entities
# #         WHERE name = %s AND designation = %s AND source = %s
# #     """, (
# #         record['Name'],
# #         record['Designation'],
# #         record['Source']
# #     ))

# #     existing = cursor.fetchone()
# #     if existing:
# #         return existing[0]  # return existing entity_id

# #     # Else insert new
# #     query = """
# #         INSERT INTO sanctioned_entities (name, designation,source)
# #         VALUES (%s, %s, %s)
# #     """
# #     cursor.execute(query, (
# #         record['Name'],
# #         record['Designation'],
# #         record['Source']
# #     ))
# #     return cursor.lastrowid

# # def insert_aliases(cursor, entity_id, aliases):
# #     if not aliases:
# #         return
# #     for alias in aliases.split(', '):
# #         alias = alias.strip()
# #         cursor.execute(
# #             "SELECT 1 FROM aliases WHERE entity_id = %s AND alias_name = %s",
# #             (entity_id, alias)
# #         )
# #         if not cursor.fetchone():
# #             cursor.execute(
# #                 "INSERT INTO aliases (entity_id, alias_name) VALUES (%s, %s)",
# #                 (entity_id, alias)
# #             )

# # def insert_sanction_types(cursor, entity_id, sanction_str):
# #     """Split comma-separated sanction types and insert one row per type."""
# #     if not sanction_str:
# #         return
# #     for stype in [s.strip() for s in sanction_str.split(',') if s.strip()]:
# #         cursor.execute(
# #             "INSERT INTO sanction_types (entity_id, sanction_type) VALUES (%s, %s)",
# #             (entity_id, stype)
# #         )


# # def insert_nationalities(cursor, entity_id, nationality_str):
# #     """
# #     Inserts nationalities into the nationalities table.
# #     Accepts a comma-separated string and inserts each nationality.
# #     Skips duplicates.
# #     """
# #     if not nationality_str:
# #         return

# #     for nat in [n.strip() for n in nationality_str.split(',') if n.strip()]:
# #         # Check if this nationality for this entity already exists
# #         cursor.execute("""
# #             SELECT 1 FROM nationalities
# #             WHERE entity_id = %s AND nationality = %s
# #         """, (entity_id, nat))

# #         if not cursor.fetchone():
# #             # Insert if not already present
# #             cursor.execute(
# #                 "INSERT INTO nationalities (entity_id, nationality) VALUES (%s, %s)",
# #                 (entity_id, nat)
# #             )



# if __name__ == "__main__":
#     conn = connect_db()
#     if conn:
#         conn.close()

import pymysql
from dotenv import load_dotenv
import os
import time

load_dotenv()

def connect_db(max_retries=3, retry_delay=5):
    for attempt in range(max_retries):
        try:
            conn = pymysql.connect(
                host=os.getenv("DB_HOST", "localhost"),
                user=os.getenv("DB_USER", "root"),
                password=os.getenv("DB_PASSWORD", ""),
                database=os.getenv("DB_NAME", "sanctions"),
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
                connect_timeout=10
            )
            print("Connected to database successfully")
            return conn
        except pymysql.MySQLError as err:
            print(f"Error: {err}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
    print("Failed to connect to database after retries")
    return None

def insert_entity(cursor, record):
    if not record.get('Name'):
        print(f"Skipping record with missing Name: {record}")
        return None
    cursor.execute("""
        SELECT entity_id FROM sanctioned_entities
        WHERE name = %s AND designation = %s AND source = %s
    """, (
        record['Name'],
        record.get('Designation'),
        record.get('Source')
    ))
    existing = cursor.fetchone()
    if existing:
        return existing['entity_id']
    query = """
        INSERT INTO sanctioned_entities (name, designation, source)
        VALUES (%s, %s, %s)
    """
    cursor.execute(query, (
        record['Name'],
        record.get('Designation'),
        record.get('Source')
    ))
    return cursor.lastrowid

def insert_aliases(cursor, entity_id, aliases):
    if not aliases or aliases.strip() == '':
        return
    for alias in aliases.split(', '):
        alias = alias.strip()
        if not alias:
            continue
        cursor.execute(
            "SELECT COUNT(*) as count FROM aliases WHERE entity_id = %s AND alias_name = %s",
            (entity_id, alias)
        )
        if cursor.fetchone()['count'] == 0:
            cursor.execute(
                "INSERT INTO aliases (entity_id, alias_name) VALUES (%s, %s)",
                (entity_id, alias)
            )

def insert_nationalities(cursor, entity_id, nationality_str):
    if not nationality_str or nationality_str.strip() == '':
        return
    for nat in [n.strip() for n in nationality_str.split(',') if n.strip()]:
        cursor.execute(
            "SELECT COUNT(*) as count FROM nationalities WHERE entity_id = %s AND nationality = %s",
            (entity_id, nat)
        )
        if cursor.fetchone()['count'] == 0:
            cursor.execute(
                "INSERT INTO nationalities (entity_id, nationality) VALUES (%s, %s)",
                (entity_id, nat)
            )

def insert_sanction_types(cursor, entity_id, sanction_str):
    if not sanction_str or sanction_str.strip() == '':
        return
    for stype in [s.strip() for s in sanction_str.split(',') if s.strip()]:
        cursor.execute(
            "SELECT COUNT(*) as count FROM sanction_types WHERE entity_id = %s AND sanction_type = %s",
            (entity_id, stype)
        )
        if cursor.fetchone()['count'] == 0:
            cursor.execute(
                "INSERT INTO sanction_types (entity_id, sanction_type) VALUES (%s, %s)",
                (entity_id, stype)
            )

if __name__ == "__main__":
    conn = connect_db()
    if conn:
        conn.close()
