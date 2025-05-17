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
