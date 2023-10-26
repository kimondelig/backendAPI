const express = require('express');
const axios = require('axios');
const app = express();
const http = require('http');
const https = require('https');
// First port on V2 
const port = 3019;
const API_KEY = 'cf23df2207d99a74fbe169e3eba035e633b65d94'; 
// const username = 'brd-customer-hl_e7275c4d-zone-dropchecker';
// const password = 'tbosd0xrywgv';
const username = 'brd-customer-hl_e7275c4d-zone-padelis_web_unlocker_main';
const password = 'tikqvzik1t9p'
const proxyPort = 22225;

const httpAgent = new http.Agent({ keepAlive: true });
const httpsAgent = new https.Agent({ keepAlive: true, rejectUnauthorized: false });

app.use(express.json());

const { Pool } = require('pg');

const pool = new Pool({
    host: 'database-1-instance-1.cwysyy38ldpw.us-east-2.rds.amazonaws.com',
    database: 'tryAgain',
    user: 'isdsar',
    password: 'Outeclanisdsar123*',
    port: 5432
});

async function getEndpointURL(event_code, link_id) {
  const query = `
    SELECT DISTINCT
        p.event_code,
        p.link_id,
        p.data_acc_id,
        p.distributor_id,
        CONCAT(
            'https://',
            p.venue_name,
            '.evenue.net/cgi-bin/ncommerce3/SEPyos?linkID=',
            p.link_id,
            '&get=sect&itC=',
            p.event_code,
            '&data_acc_id=',
            p.data_acc_id,
            '&link_id=',
            p.link_id,
            '&distributor_id=',
            p.distributor_id,
            '&eventcode_id=', 
            p.event_code
        ) AS sections_link_url
    FROM
        production_evenuemap p  
    INNER JOIN tmEvents t on p.event_code = t.event_code 
    WHERE 
        t.start_date IS NOT NULL 
        AND p.event_code = $1
        AND p.link_id = $2;
  `;

  const { rows } = await pool.query(query, [event_code, link_id]);
  return rows[0].sections_link_url;
}

async function makeRequest(data, res) {
  try {
    
    const parts = data.split('?');
    const url = parts[0] + '?' + parts[1];  // construct URL up to event code
    
    // const parts = data.split('+');
    // const url = parts[0];
    // const searchParams = new URLSearchParams(parts[1]); // treat remaining parts as the parameters
    console.log(url);
    // console.log(searchParams);
    const searchParams = new URLSearchParams(url.split('?')[1]); // treat remaining parts as the parameters
    const venue_name_id = url.match(/https:\/\/(.*?)\.evenue\.net/)[1]; 
    const link_id = searchParams.get('link_id');
    const data_acc_id = searchParams.get('data_acc_id');
    const distributor_id = searchParams.get('distributor_id');
    const eventcode_id = searchParams.get('eventcode_id');

    const session_id = (1000000 * Math.random()) | 0;
    // 198.13.33.79
    // const super_proxy_url = `http://${username}-session-${session_id}:${password}@198.13.33.79:${proxyPort}`;
    const super_proxy_url = `http://${username}-session-${session_id}:${password}@brd.superproxy.io:${proxyPort}`;
    const superProxyUrl = new URL(super_proxy_url);

    const options = {
      method: 'get',
      url: url,
      proxy: {
        host: superProxyUrl.hostname,
        port: superProxyUrl.port,
        auth: {
          username: superProxyUrl.username,
          password: superProxyUrl.password,
        },
      },
      httpAgent: httpAgent, // use the shared agent
      httpsAgent: httpsAgent, // use the shared agent
      headers: {
        'Pac-Context-Data': JSON.stringify({
          distributorId: distributor_id,
          dataAccountId: data_acc_id,
          siteId: "ev_"+link_id, 
        }),
        'Pac-Authz-Data': JSON.stringify({
            distributorId: distributor_id,
            dataAccountId: data_acc_id,
            iProfileId: ""
        }),
      },
    }

    let response = await axios(options);
    // console.log(response);
    // Handle the response
    if (response.status === 200) {
        response = response.data; 
        console.log(`Successful GETSECTIONS request for: ${eventcode_id} and ${link_id}\n`);
        const front_end_url = `http://${venue_name_id}.evenue.net/cgi-bin/ncommerce3/SEGetEventInfo?linkID=${link_id}&ticketCode=${eventcode_id}&groupCode=&shopperContext=&pc=&caller=&appCode=&cgc=&prc=&ppc=&psc=&sm=1&dataAccId=${data_acc_id}&siteId=ev_${link_id}`;    
        // add the additional properties to the response object
        response.event_code = eventcode_id; 
        response.data_acc_id = data_acc_id; 
        response.link_id = link_id; 
        response.venue_name = venue_name_id; 
        response.status = 200; 

        // check if the response has the specific status and message
        if (response.status.mg === 'Unable to get seat map information.  Please try again later.') {
          console.log('Seatmap blocked: '+front_end_url+'\n');
          res.write(`${JSON.stringify(null)}\n\n`);
          res.end();
        }
        else {      
          res.write(`${JSON.stringify(response)}\n\n`);
          res.end();        
        } 
      }

  } catch (error) {    
    // console.log(error);
    // Check if error.response exists, meaning the server responded with an error status code
    if (error.response) {
        // Extract status code and message from the error response
        const { status, statusText } = error.response;
        
        // Handle different HTTP status codes
        if (status === 400) {
            res.write(`${JSON.stringify({ error: 'Bad Request', message: statusText, 'status': status })}\n\n`);
        } else if (status === 403) {
            res.write(`${JSON.stringify({ error: 'Forbidden', message: statusText, 'status': status })}\n\n`);
        } else if (status === 500) {
            res.write(`${JSON.stringify({ error: 'Internal Server Error', message: statusText, 'status': status })}\n\n`);
        } else if (status === 404) {
            res.write(`${JSON.stringify({ error: 'Not Found', message: statusText, 'status': status })}\n\n`);
        } else {
            // Default case for other status codes
            res.write(`${JSON.stringify({ error: 'Error in making request', message: statusText, 'status': status })}\n\n`);
        }
    } else if (error.request) {
        // The request was made but no response was received
        res.write(`${JSON.stringify({ error: 'No response received from server', message: 'The server did not respond to the request' })}\n\n`);
    } else {
        // Something happened in setting up the request that triggered an Error
        res.write(`${JSON.stringify({ error: 'Request Setup Error', message: error.message })}\n\n`);
    }
    res.end();
    }
}

app.use((req, res, next) => {
  const apiKey = req.header('X-API-Key');
  if (!apiKey || apiKey !== API_KEY) res.status(401).json({ message: 'Not Authorized' });
  else next();
});

app.get('/production-isolatedsections', async (req, res) => {
  res.setHeader('Content-Type', 'application/json'); // application/json text/event-stream
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  res.flushHeaders();

  try {
    const { event_code, link_id } = req.query;
    const data = await getEndpointURL(event_code, link_id);
    await makeRequest(data, res);

  } catch (err) {
    console.error('Error:', err);
    if (!res.headersSent) res.status(500).send('Internal Server Error');
  } 
});

app.listen(port, () => console.log(`SECTIONS DETAILS V2 Server is running on port ${port}\n`));