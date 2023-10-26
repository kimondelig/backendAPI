import psycopg2
import aiohttp
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
API_URL = f'{server_address}:3016/production-getholdcts'

def connectdb_getholdcodes():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        query = """
            SELECT
                CONCAT(
                    'https://',
                    ve.venue_name,
                    '.evenue.net/pac-api/seat-availability/event-id/',
                    ve.data_acc_id,
                    ':',
                    SPLIT_PART(ve.event_code, ':', 3),
                    ':',
                    SPLIT_PART(ve.event_code, ':', 4),
                    '/',
                    'pricelevel?distributorId=',
                    ve.distributor_id,
                    '&data_acc_id=',
                    ve.data_acc_id,
                    '&link_id=',
                    ve.link_id,
                    '&distributor_id=',
                    ve.distributor_id,
                    '&eventcode_id=', 
                    ve.event_code
                ) AS link_url
            FROM
                production_evenuemap ve
            WHERE
                NOT EXISTS (
                    SELECT 1
                    FROM production_holdingcodes_v2 ph
                    WHERE ph.frontend_url = CONCAT(
                        'http://',
                        ve.venue_name,
                        '.evenue.net/cgi-bin/ncommerce3/SEGetEventInfo?linkID=',
                        ve.link_id,
                        '&ticketCode=',
                        ve.event_code,
                        '&groupCode=&shopperContext=&pc=&caller=&appCode=&cgc=&prc=&ppc=&psc=&sm=1&dataAccId=',
                        ve.data_acc_id,
                        '&siteId=ev_',
                        ve.link_id
                    )
                );
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

        for values in data:
            # Define the INSERT ... ON CONFLICT statement
            query = """
                INSERT INTO production_holdingCodes_v2 (frontend_url, code, venue_name, event_code, link_id, data_acc_id, last_updated)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (frontend_url) 
                DO UPDATE SET
                    code = EXCLUDED.code,
                    venue_name = EXCLUDED.venue_name,
                    event_code = EXCLUDED.event_code,
                    link_id = EXCLUDED.link_id,
                    data_acc_id = EXCLUDED.data_acc_id,
                    last_updated = EXCLUDED.last_updated;
            """
            
            # Execute the statement with the given values
            cur.execute(query, values)

        # Commit the transaction
        conn.commit()

    except Exception as e:
        print(f"Error during database operation: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

async def fetch(session, url, retries=6):
    headers = {"X-API-Key": API_KEY}
    
    for i in range(retries + 1):
        async with session.get(API_URL, params={'url': url}, headers=headers) as response:
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
                print(f"Retrying {i+1}... {url[:url.index('&')]}")
                if i == retries:
                    return content # Return the error content after the last retry.
            else:
                return content # Return the error content if it's a different error.

async def main_holdcodes():
    urls_holdcodes = connectdb_getholdcodes()

    if not urls_holdcodes:
        return
    
    connector = aiohttp.TCPConnector(limit=len(urls_holdcodes))

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks_holdcodes = [fetch(session, url) for url in urls_holdcodes]
        
        responses_holdcodes = await asyncio.gather(*tasks_holdcodes, return_exceptions=True)

    # Initialize containers for processed responses
    processed_responses_holdcodes = []

    # Process responses for holdcodes
    for response, url in zip(responses_holdcodes, urls_holdcodes):
        if isinstance(response, Exception):
            print(f"Error fetching {url[:url.index('&')]}: {response}")
        else:
            # Assume response is a dictionary, adjust as necessary
            try: 
                status = response.get('status')
            except: 
                print(response)
                continue
            
            if status == 200:
                # print(f"Successful response for {url}: {response}")
                processed_responses_holdcodes.append(response['values'])
            elif status == 403:
                print(f"Forbidden response for {url[:url.index('&')]}: {response}")
            else:
                print(f"Other Error for {url[:url.index('&')]}: {response}")

    upsert_values(processed_responses_holdcodes)
    print('\n')
    print("-" * 50) 
    print('Phase 1: Successfully processed + updated data for holdcodes!')
    print('Input data size: ', str(len(urls_holdcodes)))
    print('Processed responses for holdcodes size:', str(len(processed_responses_holdcodes)))
    print("-" * 50) 

# Run the async main function
asyncio.run(main_holdcodes())