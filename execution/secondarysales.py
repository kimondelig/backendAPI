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
API_URL_EVENTINFO = f'{server_address}:3017/production-geteventinfo'

def connectdb_getSS():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        query = """
            SELECT
                link_url
            FROM
                (
                    SELECT
                        CONCAT(
                            'https://',
                            pem.venue_name,
                            '.evenue.net/pac-api/catalog/eventDetailMPT/',
                            SPLIT_PART(pem.event_code, ':', 3),
                            '/',
                            SPLIT_PART(pem.event_code, ':', 4),
                            '?data_acc_id=',
                            pem.data_acc_id,
                            '&link_id=',
                            pem.link_id,
                            '&distributor_id=',
                            pem.distributor_id,
                            '&eventcode_id=',
                            pem.event_code
                        ) AS link_url,
                        CONCAT(
                            pem.venue_name,
                            '.evenue.net/cgi-bin/ncommerce3/SEGetEventInfo?linkID=',
                            pem.link_id,
                            '&ticketCode=',
                            pem.event_code,
                            '&groupCode=&shopperContext=&pc=&caller=&appCode=&cgc=&prc=&ppc='
                        ) AS check_url
                    FROM
                        production_evenuemap AS pem
                    INNER JOIN
                        tmevents AS tm
                    ON
                        pem.event_code = tm.event_code
                    WHERE
                        tm.on_skybox = True
                        AND tm.temp_on_skybox = True
                        AND tm.start_date >= current_date
                ) AS links_to_check;
        """

        '''
                    INNER JOIN
                        tmevents AS tm
                    ON
                        pem.event_code = tm.event_code
                    WHERE
                        tm.on_skybox = True
                        AND tm.temp_on_skybox = True
                        AND tm.start_date >= current_date         
        '''

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
                INSERT INTO production_holdingCodes_v2 (frontend_url, secondaries, venue_name, event_code, link_id, data_acc_id, last_updated, start_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (frontend_url) 
                DO UPDATE SET
                    secondaries = EXCLUDED.secondaries,
                    venue_name = EXCLUDED.venue_name,
                    event_code = EXCLUDED.event_code,
                    link_id = EXCLUDED.link_id,
                    data_acc_id = EXCLUDED.data_acc_id,
                    last_updated = EXCLUDED.last_updated,
                    start_date = EXCLUDED.start_date;
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

async def fetch_eventinfo(session, url, retries=5):
    headers = {"X-API-Key": API_KEY}
    
    for i in range(retries + 1):
        async with session.get(API_URL_EVENTINFO, params={'url': url}, headers=headers) as response:
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
    urls_eventinfo = connectdb_getSS()

    if not urls_eventinfo:
        return
    
    connector = aiohttp.TCPConnector(limit=len(urls_eventinfo))

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks_eventinfo = [fetch_eventinfo(session, url) for url in urls_eventinfo]
        
        responses_eventinfo = await asyncio.gather(*tasks_eventinfo, return_exceptions=True)

    # Initialize containers for processed responses
    processed_responses_eventinfo = []

    # Process responses for eventinfo
    for response, url in zip(responses_eventinfo, urls_eventinfo):
        if isinstance(response, Exception):
            print(f"Error fetching {url[:url.index('?')]}: {response}")
        else:
            # Assume response is a dictionary, adjust as necessary
            try: 
                status = response.get('status')
            except: 
                print(response)
                continue
            
            if status == 200:
                # print(f"Successful response for {url[:url.index('?')]}: {response}")
                processed_responses_eventinfo.append(response['values'])
            elif status == 403:
                print(f"Forbidden response for {url[:url.index('?')]}: {response}")
            else:
                print(f"Other Error for {url[:url.index('?')]}: {response}")

    upsert_values(processed_responses_eventinfo)
    print('\n')
    print("-" * 50) 
    print('Phase 1: Successfully processed + updated data for secondary sales!')
    print('Input data size: ', str(len(urls_eventinfo)))
    print('Processed responses for secondary sales size:', str(len(processed_responses_eventinfo)))
    print('Errored responses for secondary sales size:', str(len(urls_eventinfo)-len(processed_responses_eventinfo)))
    print("-" * 50) 


# Run the async main functions
asyncio.run(main_eventinfo())