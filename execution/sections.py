import psycopg2
import aiohttp
from aiohttp import ClientSession, ClientTimeout, ClientError
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

API_URL = f'{server_address}:3019/production-isolatedsections'  # Updated API URL
API_KEY = "cf23df2207d99a74fbe169e3eba035e633b65d94"

def connect_db():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    query = """
        SELECT pe.event_code, pe.link_id
        FROM production_evenuemap as pe
        JOIN tmevents tm ON pe.event_code = tm.event_code
        WHERE tm.on_skybox = True AND tm.temp_on_skybox = True AND tm.start_date >= current_date
        LIMIT 10; 
    """
    cursor.execute(query)
    urls = [{"event_code": row[0], "link_id": row[1]} for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return urls

async def fetch(session, params, retries=8):
    headers = {"X-API-Key": API_KEY}
    for i in range(retries + 1):
        async with session.get(API_URL, params=params, headers=headers) as response:
            # Invalid Format error 
            if response.content_type == 'application/json':
                try:
                    content = await response.json()
                except json.JSONDecodeError:
                    return f"Error: Invalid JSON received"
            else: # this is a bit unecessary 
                content = await response.text()
            #successful response 
            if response.status == 200 and 'error' not in content and '403' not in content:
                return content
            
            elif '403' in content or ('error' in content and content['error'] == 'Forbidden'):
                print(f"403: Retrying {i+1}... ")
                if i == retries:
                    return content
            else:
                if content['message'] == 'The server did not respond to the request':
                    print(f"ECONERESSET: Retrying {i+1}... ")
                    if i == retries: 
                        return content 
                else: 
                    return content # f"Error: {content}"

async def main():
    all_data = [] 
    error_data = 0  
    data_unaivalable_data = 0 
    other_error = 0 

    urls = connect_db()
    if not urls:
        return
    
    connector = aiohttp.TCPConnector(limit=len(urls))  # Set the limit to the number of URLs.
    timeout = ClientTimeout(total=15)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [fetch(session, url) for url in urls]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        for response, url in zip(responses, urls):
            # if isinstance(response, Exception):
            try: 
                if response['error'] == 'No response received from server': 
                    print(f"ECONERESSET: Error fetching {url}: \n{response}\n")
                    other_error += 1 
                elif response['error'] == 'Request Setup Error': 
                    print(f"BAD SET-UP ERROR: Error fetching {url}: \n{response}\n")
                    other_error += 1 
                else: 
                    print(f"UKNOWN ERROR: Error fetching {url}: \n{response}\n")
                    other_error += 1 
            except:
                if response['status'] == 403: 
                    error_data += 1 
                elif response['status'] == 200: 
                    print(f"Response from {url}: {response}")
                    all_data.append(response)
                else: 
                    other_error += 1 
    print('\n')
    print("-" * 50) 
    print('Phase 1: Successfully added data to tmEvents!')
    print('Input data size: '+str(len(urls)))
    print('Successful data size: '+str(len(all_data)))
    print('403 error size: '+str(error_data))
    print('Other error size: '+str(other_error))
    print('Not on sale yet size: '+str(data_unaivalable_data))
    print("-" * 50) 

asyncio.run(main())
