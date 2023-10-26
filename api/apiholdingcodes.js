const express = require('express');
const axios = require('axios');
const app = express();
const http = require('http');
const https = require('https');
const moment = require('moment');
// First port on V2 
const port = 3016;
const API_KEY = 'cf23df2207d99a74fbe169e3eba035e633b65d94'; 
const username = 'brd-customer-hl_e7275c4d-zone-padelis_web_unlocker_main';
const password = 'tikqvzik1t9p';
const proxyPort = 22225;

const httpAgent = new http.Agent({ keepAlive: true });
const httpsAgent = new https.Agent({ keepAlive: true, rejectUnauthorized: false });

app.use(express.json());

async function makeRequest(data, res) {
  try {
    const url = data.url.split('&')[0];
    const searchParams = new URLSearchParams(data.url.split('?')[1]); 
    const session_id = (1000000 * Math.random()) | 0;
    const super_proxy_url = `http://${username}-session-${session_id}:${password}@brd.superproxy.io:${proxyPort}`;
    const superProxyUrl = new URL(super_proxy_url);
    const venue_name_id = url.match(/https:\/\/(.*?)\.evenue\.net/)[1]; 
    const link_id = searchParams.get('link_id');
    const data_acc_id = searchParams.get('data_acc_id');
    const distributor_id = searchParams.get('distributor_id');
    const eventcode_id = searchParams.get('eventcode_id');

    // console.log(url);
    // console.log(searchParams);

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
    //   headers: {
    //     'Pac-Context-Data': JSON.stringify({
    //       distributorId: distributor_id,
    //       dataAccountId: data_acc_id,
    //       siteId: "ev_"+link_id, 
    //     }),
    //     'Pac-Authz-Data': JSON.stringify({
    //         distributorId: distributor_id,
    //         dataAccountId: data_acc_id,
    //         iProfileId: ""
    //     }),
    //   },
    }

    let response = await axios(options);
    let result = {} 
    // Handle the response --> there shouldn't be a non successful request 
    if (response.status === 200) {
        response = response.data; 
        console.log(`Successful GETHOLDINGCODES request for: ${eventcode_id} and ${link_id}\n`);
        const front_end_url = `http://${venue_name_id}.evenue.net/cgi-bin/ncommerce3/SEGetEventInfo?linkID=${link_id}&ticketCode=${eventcode_id}&groupCode=&shopperContext=&pc=&caller=&appCode=&cgc=&prc=&ppc=&psc=&sm=1&dataAccId=${data_acc_id}&siteId=ev_${link_id}`;    
        
        response.venue_name = venue_name_id; 
        response.data_acc_id = data_acc_id; 
        response.event_code = eventcode_id; 
        response.link_id = link_id; 
        response.distributor_id = distributor_id; 

        result['values'] = [front_end_url, response.holdCds[0], venue_name_id, eventcode_id, link_id, data_acc_id, moment().format('YYYY-MM-DD HH:mm')];
        result['status'] = 200; 

        res.write(`${JSON.stringify(result)}\n\n`);
        res.end();        
      }
  } catch (error) {    
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

app.get('/production-getholdcts', async (req, res) => {
    res.setHeader('Content-Type', 'application/json'); // application/json text/event-stream
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    res.flushHeaders();

    try {
        const data = { url: req.query.url };
        await makeRequest(data, res);

    } catch (err) {
        console.error('Error:', err);
        if (!res.headersSent) res.status(500).send('Internal Server Error');
    } 
    });

app.listen(port, () => console.log(`HOLDINGCODES Server is running on port ${port}\n`));