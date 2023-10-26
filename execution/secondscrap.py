import psycopg2
import aiohttp
from aiohttp import ClientSession, ClientTimeout, ClientError
import asyncio
import json 
from datetime import datetime, date
import psycopg2.extras

# Database Connection Variables
DB_CONFIG = {
    "host": "database-1-instance-1.cwysyy38ldpw.us-east-2.rds.amazonaws.com",
    "database": "tryAgain",
    "user": "isdsar",
    "password": "Outeclanisdsar123*",
    "port": "5432"
}

server_address = 'http://18.222.178.85'

API_KEY = "cf23df2207d99a74fbe169e3eba035e633b65d94"
API_URL = f'{server_address}:3020/production-getevenueurls'


def connect_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        #This is missing reno-rodeo and ticket-atlantic 
        query = """
            SELECT
                CONCAT(
                    'https://',
                    venue,
                    '.evenue.net/cgi-bin/ncommerce3/SEGetEventList?linkID=',
                    link_id,
                    '&timeDateFrom=',
                    TO_CHAR(CURRENT_DATE, 'YYYY-MM-DD-00.00.00'),
                    '&timeDateTo=2024-04-30-23.59.59&shopperContext=&format=mini'
                ) AS link_url
            FROM
                production_first_scrap
            WHERE
                link_id IN (
                    SELECT DISTINCT link_id
                    FROM production_evenuemap 
                )
            ORDER by link_url;
        """
        
        cursor.execute(query)
        urls = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()

        return urls
    except (psycopg2.Error, Exception) as e:
        print("Error connecting to the database:", str(e))
        return []

def createtable_getevenuemap(delete=False):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Drop the table if it exists
        if delete: 
            drop_script = """
            DROP TABLE IF EXISTS production_evenuemap;
            """
            cursor.execute(drop_script)
            conn.commit()
        
        # Create the table
        create_script = """
        CREATE TABLE IF NOT EXISTS production_evenuemap (
            event_code VARCHAR(60) NOT NULL, 
            link_id VARCHAR(20),
            data_acc_id INT,
            venue_name VARCHAR(200),
            distributor_id VARCHAR(20),
            CONSTRAINT unique_event_code_link_id UNIQUE (event_code, link_id)
        );
        """
        cursor.execute(create_script)
        conn.commit()
        
        cursor.close()
        conn.close()
        
        print("Table 'production_evenuemap' created successfully!")
        
    except (psycopg2.Error, Exception) as e:
        print("Error creating table:", str(e))

def insertdata_db(data): 
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        insert_script = """
        INSERT INTO production_evenuemap (event_code, link_id, data_acc_id, venue_name, distributor_id)
        VALUES (%(event_code)s, %(link_id)s, %(data_acc_id)s, %(venue_name)s, %(distributor_id)s)
        ON CONFLICT (event_code, link_id) DO NOTHING
        """

        data_added_count = 0
        for item in data:
            try:
                cursor.execute(insert_script, {
                    'event_code': item['eventCode'],
                    'link_id': item['linkId'],
                    'data_acc_id': int(item['dataAccId']),
                    'venue_name': item['venueName'],
                    'distributor_id': item['distributorId']
                })

                if cursor.rowcount > 0:  # Check if any row is affected (i.e., a new row is added)
                    data_added_count += 1
                    print(str(data_added_count) + '...Row added ' + str(item))  
            except KeyError as ke:
                print(f"Missing key {ke} in data item")

        conn.commit()

        return data_added_count
    except (psycopg2.Error, Exception) as e:
        print("Error inserting data:", str(e))
    finally:
        cursor.close()
        conn.close()

async def fetch(session, url, retries=4):
    headers = {"X-API-Key": API_KEY}
    
    for i in range(retries + 1):
        async with session.get(API_URL, params={'url': url}, headers=headers) as response:
            # Invalid Format error 
            if response.content_type == 'application/json':
                try:
                    content = await response.json()
                except json.JSONDecodeError:
                    return f"Error: Invalid JSON received from {url}"
            else: # this is a bit unecessary 
                content = await response.text()
            #successful response 
            if response.status == 200 and 'error' not in content and '403' not in content:
                return content
            
            elif '403' in content or ('error' in content and content['error'] == 'Forbidden'):
                print(f"403: Retrying {i+1}... {url}")
                if i == retries:
                    return content
            else:
                if content['message'] == 'The server did not respond to the request':
                    print(f"ECONERESSET: Retrying {i+1}... {url}")
                    if i == retries: 
                        return content 
                else: 
                    return content # f"Error: {content}"

async def main():
    all_data = [] 
    error_data = 0 
    other_error = 0 
    counter = 0

    urls = connect_db()
    if not urls:
        return
    
    connector = aiohttp.TCPConnector(limit=len(urls))  # Set the limit to the number of URLs.
    # timeout = ClientTimeout(total=15)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [fetch(session, url) for url in urls]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        for response, url in zip(responses, urls):
            # if isinstance(response, Exception):
            try: 
                if response['error'] == 'No response received from server': 
                    print(f"ECONERESSET: Error fetching {url}: \n{response}\n")
                    other_error += 1 
                if response['error'] == 'Request Setup Error': 
                    print(f"BAD SET-UP ERROR: Error fetching {url}: \n{response}\n")
                    other_error += 1 
            except:
                if response['status'] == 200: 
                    # print(f"Response from {url}: {response}")
                    all_data.extend(response['data'])
                    if len(response['data'])>0:
                        counter += 1 
                elif response['status'] == 403: 
                    error_data += 1 
                else: 
                    other_error += 1 

    data_added_count = insertdata_db(all_data)
    print('\n')
    print("-" * 50) 
    print('Phase 1: Successfully appended data to PRODUCTION EVENUEMAP!')
    print('Input data size: '+str(len(urls)))
    print('Successful data size: '+str(counter))
    print('Successful data size APPENDED: '+str(data_added_count))
    print('403 error size: '+str(error_data))
    print('Other error size: '+str(other_error))
    print("-" * 50) 


# Run the async main function
asyncio.run(main())