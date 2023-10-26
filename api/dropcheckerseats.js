const express = require('express');
const axios = require('axios');
const app = express();
const http = require('http');
const https = require('https');
// First port on V2 
const port = 3014;
const API_KEY = 'cf23df2207d99a74fbe169e3eba035e633b65d94'; 
const username = 'brd-customer-hl_e7275c4d-zone-dropchecker';
const password = 'tbosd0xrywgv';
const proxyPort = 22225;

const httpAgent = new http.Agent({ keepAlive: true });
const httpsAgent = new https.Agent({ keepAlive: true, rejectUnauthorized: false });

app.use(express.json());

async function makeRequest(data, res) {
  try {
    const url = data.url; 
    console.log(url);
    const session_id = (1000000 * Math.random()) | 0;
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
      // headers: {
      //   'Pac-Context-Data': JSON.stringify({
      //     distributorId: distributor_id,
      //     dataAccountId: data_acc_id,
      //     siteId: "ev_"+link_id, 
      //   }),
      //   'Pac-Authz-Data': JSON.stringify({
      //       distributorId: distributor_id,
      //       dataAccountId: data_acc_id,
      //       iProfileId: ""
      //   }),
      // },
    }

    let response = await axios(options);
    // Handle the response --> there shouldn't be a non successful request 
    if (response.status === 200) {
        response = response.data; 
        console.log(`Successful GETSEATS request for!\n`);

        res.write(`${JSON.stringify(response)}\n\n`);
        res.end();        
      }
  } catch (error) {    
    // Check if error.response exists, meaning the server responded with an error status code
    if (error.response) {
        // Extract status code and message from the error response
        const { status, statusText } = error.response;
        
        // Handle different HTTP status codes
        if (status === 400) {
            // res.write(`${JSON.stringify({ error: 'Bad Request', message: statusText, 'status': status })}\n\n`);
            res.write(`${JSON.stringify(null)}\n\n`);
        } else if (status === 403) {
            // res.write(`${JSON.stringify({ error: 'Forbidden', message: statusText, 'status': status })}\n\n`);
            res.write(`${JSON.stringify(null)}\n\n`);
        } else if (status === 500) {
            // res.write(`${JSON.stringify({ error: 'Internal Server Error', message: statusText, 'status': status })}\n\n`);
            res.write(`${JSON.stringify(null)}\n\n`);
        } else if (status === 404) {
            // res.write(`${JSON.stringify({ error: 'Not Found', message: statusText, 'status': status })}\n\n`);
            res.write(`${JSON.stringify(null)}\n\n`);
        } else {
            // Default case for other status codes
            // res.write(`${JSON.stringify({ error: 'Error in making request', message: statusText, 'status': status })}\n\n`);
            res.write(`${JSON.stringify(null)}\n\n`);
        }
    } else if (error.request) {
        // The request was made but no response was received
        // res.write(`${JSON.stringify({ error: 'No response received from server', message: 'The server did not respond to the request' })}\n\n`);
        res.write(`${JSON.stringify(null)}\n\n`);
    } else {
        // Something happened in setting up the request that triggered an Error
        // res.write(`${JSON.stringify({ error: 'Request Setup Error', message: error.message })}\n\n`);
        res.write(`${JSON.stringify(null)}\n\n`);
    }
    res.end();
    }
}

app.use((req, res, next) => {
  const apiKey = req.header('X-API-Key');
  if (!apiKey || apiKey !== API_KEY) res.status(401).json({ message: 'Not Authorized' });
  else next();
});

app.get('/production-getseatsinfov2', async (req, res) => {
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

app.listen(port, () => console.log(`DROPCHECKER SEATS DETAILS V2 Server is running on port ${port}\n`));