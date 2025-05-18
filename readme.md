# SanctionWatch Project README

## Overview

This readme file docmuents the data sources, assumptions,sample queries and instruction for restoring the database dump

## Data Sources Used

The following five sanctions sources were used to extract data:

1. **US OFAC - Consolidated**

   - URL: (https://ofac.treasury.gov/consolidated-sanctions-list-non-sdn-lists)
   - Format: XML
   - Description: Contains individuals and entities subject to US sanctions

2. **UN**

- URL : (https://www.un.org/securitycouncil/content/un-sc-consolidated-list)
- Format: XML
- Description: Contains individuals and entities subject to UN sanctions

3.  **US OFAC - SDN**

- URL: (https://ofac.treasury.gov/specially-designated-nationals-and-blocked-persons-list-sdn-human-readable-lists)
- Format: XML
- Description: Contains individuals and entities subject to US sanctions

4.  **UK HMT**

- URL : (https://www.gov.uk/government/publications/the-uk-sanctions-list)
- Format :XML
- Description : Contains individuals and entities subject to UK sanctions

5.  **Switzerland SECO**

- URL : (https://www.seco.admin.ch/seco/en/home/Aussenwirtschaftspolitik_Wirtschaftliche_Zusammenarbeit/Wirtschaftsbeziehungen/exportkontrollen-und-sanktionen/sanktionen-embargos.html)
- Format :XML
- Description : Contains individuals and entities subject to Switzerland sanctions

## Assumptions Made While Transforming Data

1. **Unified Schema Mapping**:

   - Fields like `name`, `nationality`, and `sanction_type` were mapped from source-specific fields (e.g., UN’s `FULL_NAME` to `name`). If a field was missing, it was set to NULL or “Unknown” (e.g., `alias` in some records).

2. **Missing Data Handling**:

   - For UK’s `designation` column (54% missing), a linear logistic model was trained on non-missing data using features from `name` (TF-IDF encoded) and `additional_info` (text features). Predicted values were used to fill missing entries. Acurracy of 69% was obtained.

3. **Duplicate Handling**:

   - Entities appearing in multiple sources (e.g., same individual in UN and OFAC) were assigned unique `entity_id` values unless clear evidence (e.g., identical names and nationalities) indicated they were the same entity.

4. **Handling Ambiguous or Multi-Valued Fields**:

   - Assumed that fields with multiple values (e.g., multiple nationalities in EU sanctions) would be split into separate rows in the nationalities table, prioritizing normalization over storing comma-separated values in a single field.

## Sample Sql query for browsing the dataset

Sanction database contains three tables : `sanctioned_entities`,`aliases`,`nationalities` and `sanction_types`
here sanctioned_entities is the primary tables and other and reference table

Below are the sample query to explore the data:

1. **List all the sanctioned_entities from specific source**:
   ```sql
   SELECT *
   FROM sanctioned_entities
   WHERE source = 'UN'
   LIMIT 20;
   ```
2. **Find entities with a specific nationality**:

   ```sql
   SELECT e.entity_id, e.name, n.nationality
   FROM sanctioned_entities e
   JOIN nationalities n ON e.entity_id = n.entity_id
   WHERE n.nationality = 'Pakistan';
   ```

3. **Retrieve aliases for a specific entity**:

   ```sql
   SELECT e.name, a.alias_name
   FROM sanctioned_entities e
   JOIN aliases a ON e.entity_id = a.entity_id
   WHERE e.name LIKE '%Zafar%';

   ```

4. **Find Entities with Specific Designations:**

   ```sql
   SELECT entity_id, name, designation, source
   FROM sanctioned_entities
   WHERE source = 'UN' AND designation = 'Individual'
   LIMIT 10;

   ```

5. **Count entities by source**:
   ```sql
   SELECT source, COUNT(*) AS entity_count
   FROM sanctioned_entities
   GROUP BY source;
   ```
6. **Identify Entities with Multiple Nationalities:Finds entities with more than one nationality**
   ```sql
   SELECT e.entity_id, e.name, COUNT(n.nat_id) AS nationality_count
   FROM sanctioned_entities e
   JOIN nationalities n ON e.entity_id = n.entity_id
   GROUP BY e.entity_id, e.name
   HAVING nationality_count > 1
   LIMIT 5;
   ```

## Instructions to Restore the .sql Dump

To restore the `sanctionwatch.sql` database dump to a MySQL instance, follow these steps:

1. **Ensure MySQL is Installed**:

   - Verify MySQL Server is running on your system.

2. **Create a New Schema**

   - Open MySQL Workbench or use the command line to create a new schema
   - eg: restored_sanctions

3. **Edit the SQL Dump File**

   - Edit the mysql dump file
     - Find the line
     ```sql
     USE sanctions;
     ```
     - Replace it with
     ```sql
     USE restored_sanctions;
     ```
   - Save the file

4. **Go to server**

   - Click on Data import
   - Click on Import from self contained file and provide the path
   - Click import

5. **Verify Tables**

   - Open MySQL Workbench.
   - Go to the restored_sanctions schema.
   - Click "Refresh" to view imported tables.
