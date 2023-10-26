from flask import Flask, request, jsonify
import requests
import psycopg2
import psycopg2.extras

# Your previous code here (e.g., DB_CONFIG, API_KEY, HEADERS, and all the defined functions)

# '''
# curl -X GET "http://18.219.201.252:3015/get-evenue-dropchecker?event_code=GS:FTA:BAA23:MJM1024E:&link_id=fta" -H "X-API-Key: cf23df2207d99a74fbe169e3eba035e633b65d94"
# curl -X GET "http://18.222.178.85:3015/get-evenue-dropchecker?event_code=GS:WASHST:MB23:M09:&link_id=washst" -H "X-API-Key: cf23df2207d99a74fbe169e3eba035e633b65d94"

# '''

DB_CONFIG = {
    "host": "database-1-instance-1.cwysyy38ldpw.us-east-2.rds.amazonaws.com",
    "dbname": "tryAgain",
    "user": "isdsar",
    "password": "Outeclanisdsar123*",
    "port": "5432"
}

API_KEY = 'cf23df2207d99a74fbe169e3eba035e633b65d94'
HEADERS = {
    'X-API-Key': 'cf23df2207d99a74fbe169e3eba035e633b65d94'
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def fetch_from_db(query, values):
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(query, values)
            return cur.fetchall()

def api_request(url, params={}):
    retries = 4  # Number of retries    
    for attempt in range(retries + 1):
        try:
            response = requests.get(url, params=params, headers=HEADERS)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            if attempt < retries:  # If this isn't the last attempt, wait for a bit before retrying
                continue
            else:  # If this is the last attempt, log the error and return None
                print(f"Error in API request to {url}:", str(e))
                return None

def get_availability_codes(event_code, link_id):
    query = "SELECT code, secondaries FROM production_holdingcodes_v2 WHERE event_code = %s and link_id = %s"
    results = fetch_from_db(query, (event_code, link_id))

    if results:
        return results[0]['code'], results[0]['secondaries']
    return 'O', False

def getreq_getsectionsinfo(event_code, link_id):
    url = "http://18.222.178.85:3013/production-getsectionsinfov2"
    params = {"event_code": event_code, "link_id": link_id}
    return api_request(url, params)

def getreq_getseatsinfo(endpointurl):
    url = "http://18.222.178.85:3014/production-getseatsinfov2"
    params = {"url": endpointurl}
    return api_request(url, params)

def process_seat(seat, availability_code):
    """Helper function to process a seat and return its count if it matches the availability_code."""
    seatslist = seat.split(':')
    row = seatslist[0]
    seats = seatslist[1].split(',')
    availability = seatslist[2]

    if availability == availability_code:
        return row, len(seats)
    return None, 0

def update_result_dict(result_dict, event, row, seat_count):
    """Helper function to update the result dictionary with the processed seat data."""
    if event not in result_dict:
        result_dict[event] = {}
    if row not in result_dict[event]:
        result_dict[event][row] = 0
    result_dict[event][row] += seat_count

def get_drop_checker_count(avail_seats_json, event_code, link_id):
    availability_code, boolean_code = get_availability_codes(event_code, link_id)

    if not avail_seats_json or boolean_code:
        return {}

    result_dict = {}

    for event, seat_data in avail_seats_json.items():
        try:
            price_levels = seat_data.get('pl', [])
            for price_level in price_levels:
                for seat in price_level.get('seats', []):
                    row, seat_count = process_seat(seat, availability_code)
                    if seat_count > 1:
                        update_result_dict(result_dict, event, row, seat_count)
        except Exception:
            continue  

    #formating such that we get section after semicolon 
    flattened_dict = {f"{event.split(':')[1]} {row}": count for event, rows in result_dict.items() for row, count in rows.items()}
    # flattened_dict = {f"{event} {row}": count for event, rows in result_dict.items() for row, count in rows.items()} #formating such that we get section after semicolon 

    return flattened_dict

app = Flask(__name__)

@app.route('/get-evenue-dropchecker', methods=['GET'])
def get_flat_dict():
    # Get event_code and link_id from the query parameters
    event_code = request.args.get('event_code')
    link_id = request.args.get('link_id')
    
    if not event_code or not link_id:
        return jsonify({"error": "event_code and link_id are required!"}), 400

    data_sections = getreq_getsectionsinfo(event_code, link_id)
    if not data_sections: # NULL RESPONSE 
        return jsonify({"error": "Failed to get data sections!"}), 500

    sections = list(data_sections['value'].keys())
    base_url = f"https://{data_sections['venue_name']}.evenue.net/cgi-bin/ncommerce3/SEPyos?linkID={link_id}&get=seat&itC={event_code}"

    for i, s in enumerate(sections):
        base_url += '&sec_' + str(i) + '=' + s

    seats = getreq_getseatsinfo([base_url,])
    if not seats: # NULL RESPONSE 
        return jsonify({"error": "Failed to get seats!"}), 500

    flat_dict = get_drop_checker_count(seats['value'], event_code, link_id)

    return jsonify(flat_dict)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=3015)