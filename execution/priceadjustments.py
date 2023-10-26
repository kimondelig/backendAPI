import psycopg2
import aiohttp
import asyncio
import json 
from datetime import datetime, date
import string 
import random 
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
API = f'{server_address}:3018/production-getadjustedprices'

def connect_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        query = """
            SELECT
                CONCAT(
                    'https://',
                    pe.venue_name,
                    '.evenue.net/www/ev_',
                    pe.link_id,
                    '/ss/evenue/customize/ev_',
                    pe.link_id,
                    '/script/netCommerce/customization/displayEventInfoCC.js',
                    '?link_id=',
                    pe.link_id,
                    '&distributor_id=',
                    pe.distributor_id,
                    '&eventcode_id=',
                    pe.event_code,
                    '&data_acc_id=',
                    pe.data_acc_id
                ) AS link_url
            FROM
                production_evenuemap pe
            INNER JOIN
                tmevents AS tm
            ON
                pe.event_code = tm.event_code  -- corrected here
            WHERE
                tm.on_skybox = True
                AND tm.temp_on_skybox = True
                AND tm.start_date >= current_date
            ORDER BY RANDOM();  -- corrected here
        """

        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        url_l = []

        for row in rows:
            url = row[0]
            url_l.append(url)

        return url_l
    except (psycopg2.Error, Exception) as e:
        print("Error connecting to the database:", str(e))
        return []

def upsert_values(data):
    try:
        # Connect to the database
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        data_added_count = 0 
        for item in data:
            frontend_url = list(item.keys())[0]
            adjustment = item[frontend_url]

            # Define the INSERT ... ON CONFLICT statement
            query = """
                INSERT INTO production_holdingCodes_v2 (frontend_url, pricechanges)
                VALUES (%s, %s)
                ON CONFLICT (frontend_url) 
                DO UPDATE SET pricechanges = EXCLUDED.pricechanges;
            """
            # Execute the statement with the given values
            cur.execute(query, (frontend_url, adjustment))
            if cur.rowcount > 0:  # Check if any row is affected (i.e., a new row is added)
                data_added_count += 1
                print(str(data_added_count) + '...Row added for: ' + frontend_url + ' PRICE ADJUSTMENT: '+str(adjustment))  

        # Commit the transaction
        conn.commit()

        return data_added_count
    except Exception as e:
        print(f"Error during database operation: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


async def fetch(session, url, retries=3):
    headers = {"X-API-Key": API_KEY}
    
    for i in range(retries + 1):
        async with session.get(API, params={'url': url}, headers=headers) as response:
            if response.content_type == 'application/json':
                try:
                    content = await response.json()
                except json.JSONDecodeError:
                    return f"Error: Invalid JSON received from {url[:url.index('?')]}"
            else:
                content = await response.text()
            if response.status == 200 and 'error' not in content and '403' not in content:
                return content # Return immediately upon successful response.
            
            elif '403' in content or ('error' in content and content['error'] == 'Forbidden'):
                print(f"Retrying {i+1}... {url[:url.index('?')]}")
                if i == retries:
                    return content # Return the error content after the last retry.
            else:
                return content # Return the error content if it's a different error.

async def main_eventinfo():
    urls = connect_db()

    if not urls:
        return
    
    connector = aiohttp.TCPConnector(limit=len(urls))

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [fetch(session, url) for url in urls]
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)

    # Initialize containers for processed responses
    processed_responses = []

    # Process responses for eventinfo
    for response, url in zip(responses, urls):
        if isinstance(response, Exception):
            print(f"Error fetching {url[:url.index('?')]}: {response}")
        else:
            # Assume response is a dictionary, adjust as necessary
            try: 
                status = response.get('status')
            except: 
                continue
            
            if status == 200:
                # print(f"Successful response for {url[:url.index('?')]}: {response}")
                processed_responses.append(response)
            elif status == 403:
                print(f"Forbidden response for {url[:url.index('?')]}: {response}")
            else:
                print(f"Other Error for {url[:url.index('?')]}: {response}")

    count = upsert_values(processed_responses)
    print('\n')
    print("-" * 50) 
    print('Phase 1: Successfully processed + updated data for FRONT END PRICE CHANGES!')
    print('Input data size: ', str(len(urls)))
    print('Processed responses for secondary sales size:', str(len(processed_responses)))
    print('Upsert values:', str(count))
    print('Errored responses for secondary sales size:', str(len(urls)-len(processed_responses)))
    print("-" * 50) 


# Run the async main functions
asyncio.run(main_eventinfo())