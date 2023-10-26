# import requests
# import json
# import psycopg2.extras
# import psycopg2
# from concurrent.futures import ThreadPoolExecutor
# import time
# import string 
# import random 
# import pickle 
# from datetime import datetime, date
# import schedule
# from urllib.parse import urlparse, parse_qs
# import re
# import aiohttp
# import asyncio
# #----------------------------------------------------------------------------------------------------------------------------
# '''
# Globalized host variables 
# '''
# host_name = "database-1-instance-1.cwysyy38ldpw.us-east-2.rds.amazonaws.com"
# database = "tryAgain"
# username = "isdsar"
# password = "Outeclanisdsar123*"
# port = "5432"
# #----------------------------------------------------------------------------------------------------------------------------

# def connectdb_geteventinfo():
#     try:
#         conn = psycopg2.connect(
#             host=host_name,
#             database=database,
#             user=username,
#             password=password,
#             port=port
#         )
#         cursor = conn.cursor()

#         query = """
#             SELECT
#                 link_url
#             FROM
#                 (
#                     SELECT
#                         CONCAT(
#                             'https://',
#                             venue_name,
#                             '.evenue.net/pac-api/catalog/eventDetailMPT/',
#                             SPLIT_PART(event_code, ':', 3),
#                             '/',
#                             SPLIT_PART(event_code, ':', 4),
#                             '?data_acc_id=',
#                             data_acc_id,
#                             '&link_id=',
#                             link_id,
#                             '&distributor_id=',
#                             distributor_id,
#                             '&eventcode_id=',
#                             event_code
#                         ) AS link_url,
#                         CONCAT(
#                             venue_name,
#                             '.evenue.net/cgi-bin/ncommerce3/SEGetEventInfo?linkID=',
#                             link_id,
#                             '&ticketCode=',
#                             event_code,
#                             '&groupCode=&shopperContext=&pc=&caller=&appCode=&cgc=&prc=&ppc='
#                         ) AS check_url
#                     FROM
#                         production_evenuemap AS pem
#                 ) AS links_to_check
#             WHERE
#                 check_url NOT IN (
#                     SELECT DISTINCT
#                         LEFT(REGEXP_REPLACE(url, 'https?://', ''), POSITION('&psc=' IN REGEXP_REPLACE(url, 'https?://', '')) - 1) AS truncated_url
#                     FROM
#                         tmEvents
#                     WHERE
#                         url IS NOT NULL
#                         AND source = 'EV'
#                 )
#             ORDER BY RANDOM()
#             LIMIT 5; 
#         """

#         cursor.execute(query)
#         rows = cursor.fetchall()
#         cursor.close()
#         conn.close()

#         url_l = []

#         for row in rows:
#             url = row[0]
#             url_l.append(url)

#         return url_l
#     except (psycopg2.Error, Exception) as e:
#         print("Error connecting to the database:", str(e))
#         return []

# async def fetch(session, url, retries=3):
#     headers = {"X-API-Key": "cf23df2207d99a74fbe169e3eba035e633b65d94"}
    
#     for i in range(retries + 1):  # +1 to include the first attempt
#         async with session.get('http://18.219.201.252:3012/production-geteventinfo', params={'url': url}, headers=headers) as response:
#             if response.content_type == 'application/json':
#                 content = await response.json()
#             else:
#                 content = await response.text()
            
#             # Checking the content of the response for error messages or '403'
#             if response.status == 200 and 'error' not in content and '403' not in content:
#                 return content
            
#             elif '403' in content or ('error' in content and content['error'] == 'Forbidden'):
#                 print(f"Retrying {i+1}... {url}")
#                 if i == retries:  # if this is the last retry, return the error
#                     return f"Error: {content}"
#                 # await asyncio.sleep(1)  # Optional: add a delay before retrying
#             else:
#                 return f"Error: {content}"

# async def main():
#     urls = connectdb_geteventinfo()  # Your function to retrieve links
#     if not urls:
#         return
#     async with aiohttp.ClientSession() as session:
#         tasks = [fetch(session, url) for url in urls]
#         responses = await asyncio.gather(*tasks, return_exceptions=True)
#         for response, url in zip(responses, urls):
#             if isinstance(response, Exception):
#                 print(f"Error fetching {url}: {response}")
#             else:
#                 print(f"Response from {url}: {response}")

# # Run the async main function
# asyncio.run(main())


# ## ** OLD VERSIONS 

# # async def fetch(session, url, retries=3):
# #     headers = {"X-API-Key": "cf23df2207d99a74fbe169e3eba035e633b65d94"}
    
# #     async with session.get('http://18.219.201.252:3012/production-geteventinfo', params={'url': url}, headers=headers) as response:
# #         if response.status == 200:
# #             if response.content_type == 'application/json':
# #                 return await response.json()
# #             else:
# #                 return await response.text()
# #         elif response.status == 403 and retries:
# #             print(f"Retrying...{url}")
# #             return await fetch(session, url, retries - 1)
# #         else:
# #             return f"Error: {response.status}, {response.reason}"

import psycopg2
import aiohttp
from aiohttp import ClientSession, ClientTimeout, ClientError
import asyncio
import json 
from datetime import datetime, date
import string 
import random 
import psycopg2.extras
import re 

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
API_URL = f'{server_address}:3012/production-geteventinfo'


def connectdb_geteventinfo():
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
                            venue_name,
                            '.evenue.net/pac-api/catalog/eventDetailMPT/',
                            SPLIT_PART(event_code, ':', 3),
                            '/',
                            SPLIT_PART(event_code, ':', 4),
                            '?data_acc_id=',
                            data_acc_id,
                            '&link_id=',
                            link_id,
                            '&distributor_id=',
                            distributor_id,
                            '&eventcode_id=',
                            event_code
                        ) AS link_url,
                        CONCAT(
                            venue_name,
                            '.evenue.net/cgi-bin/ncommerce3/SEGetEventInfo?linkID=',
                            link_id,
                            '&ticketCode=',
                            event_code,
                            '&groupCode=&shopperContext=&pc=&caller=&appCode=&cgc=&prc=&ppc='
                        ) AS check_url
                    FROM
                        production_evenuemap AS pem
                ) AS links_to_check
            WHERE
                check_url NOT IN (
                    SELECT DISTINCT
                        LEFT(REGEXP_REPLACE(url, 'https?://', ''), POSITION('&psc=' IN REGEXP_REPLACE(url, 'https?://', '')) - 1) AS truncated_url
                    FROM
                        tmEvents
                    WHERE
                        url IS NOT NULL
                        AND source = 'EV'
                )
            ORDER BY RANDOM();
        """

        # query = """
        #     SELECT
        #         link_url
        #     FROM
        #         (
        #             SELECT
        #                 CONCAT(
        #                     'https://',
        #                     venue_name,
        #                     '.evenue.net/pac-api/catalog/eventDetailMPT/',
        #                     SPLIT_PART(event_code, ':', 3),
        #                     '/',
        #                     SPLIT_PART(event_code, ':', 4),
        #                     '?data_acc_id=',
        #                     data_acc_id,
        #                     '&link_id=',
        #                     link_id,
        #                     '&distributor_id=',
        #                     distributor_id,
        #                     '&eventcode_id=',
        #                     event_code
        #                 ) AS link_url,
        #                 CONCAT(
        #                     venue_name,
        #                     '.evenue.net/cgi-bin/ncommerce3/SEGetEventInfo?linkID=',
        #                     link_id,
        #                     '&ticketCode=',
        #                     event_code,
        #                     '&groupCode=&shopperContext=&pc=&caller=&appCode=&cgc=&prc=&ppc='
        #                 ) AS check_url
        #             FROM
        #                 production_evenuemap AS pem
        #             WHERE event_code = 'GS:UMD:B23:B02:'
        #         ) AS links_to_check;
        # """
        
        cursor.execute(query)
        urls = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()

        return urls
    except (psycopg2.Error, Exception) as e:
        print("Error connecting to the database:", str(e))
        return []

def insertdata_geteventinfo(data_evenuemap):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        insert_script = """
        INSERT INTO tmEvents (event_id, event_code, name, url, start_date, start_time, post_code, state_code, last_update, on_skybox, temp_on_skybox, tm_city, tm_venue, country_code, black_list, availability, source, link_id) 
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (event_id) DO NOTHING
        """

        for event in data_evenuemap:
            x = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
            code = event.get('code', '')
            nameofevent = event.get('nameofevent', '')
            url = event.get('url', '')
            timeofevent = event.get('timeofevent', '')
            lastupdated = event.get('lastupdated', '')
            facility = event.get('facility', '')
            sold_on_secondaries = event.get('SOLD_ON_SECONDARY', '')
            link_id = event.get('link_id', '')
            
            if timeofevent is not None:
                if len(timeofevent.split(' ')) >= 2:
                    start_date, start_time = timeofevent.split(' ', 1)
                else:
                    start_date = date.today()
                    start_time = datetime.now().time()
            else: 
                start_date = date.today() 
                start_time = datetime.now().time() 

            insert_value = (
                x,
                code,
                nameofevent,
                url,
                start_date,
                start_time,
                None,
                None,
                '1990-01-01 20:00:00',
                'False',
                'False',
                None,
                facility,
                'US',
                False,
                True,
                'EV',
                link_id
            )

            cursor.execute(insert_script, insert_value)

        conn.commit()
    except (psycopg2.Error, Exception) as e:
        print("Error inserting data:", str(e))
    finally:
        if cursor:
            cursor.close()
        if conn:
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
                    return f"Error: Invalid JSON received from {url[:url.index('?')]}"
            else: # this is a bit unecessary 
                content = await response.text()
            #successful response 

            link_id_pattern = r'link_id=([^&]+)'
            distributor_id_pattern = r'distributor_id=([^&]+)'
            data_acc_id_pattern = r'data_acc_id=([^&]+)'
            event_code_pattern = r'eventcode_id=([^&]+)'
            venue_name_pattern = r'https://([^\.]+)\.evenue\.net'
            link_id_match = re.search(link_id_pattern, url)
            distributor_id_match = re.search(distributor_id_pattern, url)
            data_acc_id_match = re.search(data_acc_id_pattern, url)
            event_code_match = re.search(event_code_pattern, url)
            venue_name_match = re.search(venue_name_pattern, url)

            # Check if matches were found and extract the values
            if link_id_match:
                link_id = link_id_match.group(1)
            else:
                link_id = None

            if distributor_id_match:
                distributor_id = distributor_id_match.group(1)
            else:
                distributor_id = None

            if data_acc_id_match:
                data_acc_id = data_acc_id_match.group(1)
            else:
                data_acc_id = None

            if event_code_match:
                event_code = event_code_match.group(1)
            else:
                event_code = None

            if venue_name_match:
                venue_name = venue_name_match.group(1)
            else:
                venue_name = None

            front_end_url = f'http://{venue_name}.evenue.net/cgi-bin/ncommerce3/SEGetEventInfo?linkID={link_id}&ticketCode={event_code}&groupCode=&shopperContext=&pc=&caller=&appCode=&cgc=&prc=&ppc=&psc=&sm=1&dataAccId={data_acc_id}&siteId=ev_{link_id}'

            if response.status == 200 and 'error' not in content and '403' not in content:
                return content
            
            elif '403' in content or ('error' in content and content['error'] == 'Forbidden'):
                print(f"403: Retrying {i+1}... {front_end_url}")
                if i == retries:
                    return content
            elif content['status'] == 502:
                ## Can we print out URL here 
                print(f"502: Retrying {i+1}... {front_end_url}")
                if i == retries: 
                    return content 
            else:
                if content['message'] == 'The server did not respond to the request':
                    print(f"ECONERESSET: Retrying {i+1}... {front_end_url}")
                    if i == retries: 
                        return content 
                else: 
                    return content # f"Error: {content}"

async def main():
    all_data = [] 
    error_data = 0 
    data_unaivalable_data = 0 
    other_error = 0 
    error_502_data = 0 

    urls = connectdb_geteventinfo()
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
                    print(f"ECONERESSET: Error fetching {url[:url.index('?')]}: \n{response}\n")
                    other_error += 1 
                elif response['error'] == 'Request Setup Error': 
                    print(f"BAD SET-UP ERROR: Error fetching {url[:url.index('?')]}: \n{response}\n")
                    other_error += 1 
                elif response['status'] == 502: 
                    error_502_data += 1 #uknown error ++ pings here 
                elif response['status'] == 403: 
                    error_data += 1 
                else: 
                    other_error += 1
            except:
                if not isinstance(response, dict): #** HAVEN'T BEEN ABLE TO FIGURE OUT THIS ERROR YET 
                    print(response, url)
                    print('Undefined response status.')
                elif response['status'] == 200: 
                    # print(f"Response from {url[:url.index('?')]}: {response}")
                    all_data.append(response)
                elif response['status'] == 999: # Dated blocked 
                    # print(f"Response from {url[:url.index('?')]}: {response['Date block']}")
                    data_unaivalable_data += 1 
                elif response['status'] == 998: # Undefined blocked 
                    # print(f"Response from {url[:url.index('?')]}: {response['Undefined block']}")
                    data_unaivalable_data += 1 
                # elif response['status'] == 502: 
                #     error_502_data += 1 
                else: ###This hits ! 
                    other_error += 1 

    insertdata_geteventinfo(all_data)
    print('\n')
    print("-" * 50) 
    print('Phase 1: Successfully added data to tmEvents!')
    print('Input data size: '+str(len(urls)))
    print('Successful data size: '+str(len(all_data)))
    print('403 error size: '+str(error_data))
    print('502 error size: '+str(error_502_data))
    print('Other error size: '+str(other_error))
    print('Not on sale yet size: '+str(data_unaivalable_data))
    print("-" * 50) 


# Run the async main function
asyncio.run(main())
