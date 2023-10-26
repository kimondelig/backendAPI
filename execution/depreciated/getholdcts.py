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

API_KEY = "cf23df2207d99a74fbe169e3eba035e633b65d94"
API_URL = 'http://18.219.201.252:3016/production-getholdcts'
API_URL_EVENTINFO = 'http://18.219.201.252:3012/production-geteventinfo'

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
            JOIN
                tmevents tm
            ON
                ve.event_code = tm.event_code
            WHERE
                tm.on_skybox = True
                AND tm.temp_on_skybox = True
            LIMIT 5; 
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
                ) AS links_to_check
            LIMIT 5; 
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

async def fetch(session, url, retries=3):
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
                print(f"Retrying {i+1}... {url[:url.index('?')]}")
                if i == retries:
                    return content # Return the error content after the last retry.
            else:
                return content # Return the error content if it's a different error.

async def fetch_eventinfo(session, url, retries=3):
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

async def main():
    urls_holdcodes = connectdb_getholdcodes()
    urls_eventinfo = connectdb_getSS()

    if not urls_holdcodes or not urls_eventinfo:
        return
    
    connector = aiohttp.TCPConnector(limit=max(len(urls_holdcodes), len(urls_eventinfo)))

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks_holdcodes = [fetch(session, url) for url in urls_holdcodes]
        tasks_eventinfo = [fetch_eventinfo(session, url) for url in urls_eventinfo]
       
        # Combining both lists of tasks
        all_tasks = tasks_holdcodes + tasks_eventinfo
        
        responses = await asyncio.gather(*all_tasks, return_exceptions=True)

    responses_holdcodes = responses[:len(tasks_holdcodes)]
    responses_eventinfo = responses[len(tasks_holdcodes):]
    
    # Initialize containers for processed responses
    processed_responses_holdcodes = []
    processed_responses_eventinfo = []

    # Process responses for holdcodes
    for response, url in zip(responses_holdcodes, urls_holdcodes):
        if isinstance(response, Exception):
            print(f"Error fetching {url}: {response}")
        else:
            # Assume response is a dictionary, adjust as necessary
            status = response.get('status')
            if status == 200:
                print(f"Successful response for {url}: {response}")
                processed_responses_holdcodes.append(response)
            elif status == 403:
                print(f"Forbidden response for {url}: {response}")
            else:
                print(f"Other Error for {url}: {response}")

    # Process responses for eventinfo
    for response, url in zip(responses_eventinfo, urls_eventinfo):
        if isinstance(response, Exception):
            print(f"Error fetching {url}: {response}")
        else:
            # Assume response is a dictionary, adjust as necessary
            status = response.get('status')
            if status == 200:
                print(f"Successful response for {url}: {response}")
                processed_responses_eventinfo.append(response)
            elif status == 403:
                print(f"Forbidden response for {url}: {response}")
            else:
                print(f"Other Error for {url}: {response}")

    print('\n')
    print("-" * 50) 
    print('Phase 1: Successfully added data to production_holdingcodes_v2!')
    print('Processed Responses for Holdcodes:', str(len(processed_responses_holdcodes)))
    print('Processed Responses for Eventinfo:', str(len(processed_responses_eventinfo)))
    print("-" * 50) 


# Run the async main function
asyncio.run(main())