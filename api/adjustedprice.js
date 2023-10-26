const express = require('express');
const axios = require('axios');
const app = express();
const http = require('http');
const https = require('https');
const moment = require('moment');
// First port on V2 
const port = 3018;
const API_KEY = 'cf23df2207d99a74fbe169e3eba035e633b65d94'; 
const username = 'brd-customer-hl_e7275c4d-zone-padelis_web_unlocker_main';
const password = 'tikqvzik1t9p';
const proxyPort = 22225;
const UserAgent= require('user-agents');
const { response } = require('express');
const httpAgent = new http.Agent({ keepAlive: true });
const httpsAgent = new https.Agent({ keepAlive: true, rejectUnauthorized: false });

app.use(express.json());

/*
curl -X GET "http://18.219.201.252:3018/production-getadjustedprices?url=https%3A%2F%2Fppac.evenue.net%2Fwww%2Fev_pfm-ppac%2Fss%2Fevenue%2Fcustomize%2Fev_pfm-ppac%2Fscript%2FnetCommerce%2Fcustomization%2FdisplayEventInfoCC.js%3Flink_id%3Dpfm-ppac%26distributor_id%3DPPAC%26eventcode_id%3DGS%3APPAC%3AP23%3ASTIRV4%3A%26data_acc_id%3D896" -H "X-API-Key: cf23df2207d99a74fbe169e3eba035e633b65d94"

curl -X GET "http://18.219.201.252:3018/production-getadjustedprices?url=https%3A%2F%2F12thmanfoundation.evenue.net%2Fwww%2Fev_tamu%2Fss%2Fevenue%2Fcustomize%2Fev_tamu%2Fscript%2FnetCommerce%2Fcustomization%2FpyoCC.js%3Flink_id%3Dtamu%26distributor_id%3DTAMU%26eventcode_id%3DGS%3ATAMU%3AF23%3AF09%3A%26data_acc_id%3D837" -H "X-API-Key: cf23df2207d99a74fbe169e3eba035e633b65d94"
*/

async function makeRequest(data, res) {
  try {
    const link = data.url; 
    const url = link.split('?')[0];
    console.log(`Requesting: ${url}\n`)
    const searchParams = new URLSearchParams(link.split('?')[1]); 
    const venue_name_id = url.match(/https:\/\/(.*?)\.evenue\.net/)[1]; 
    const link_id = searchParams.get('link_id');
    const data_acc_id = searchParams.get('data_acc_id');
    const distributor_id = searchParams.get('distributor_id');
    const eventcode_id = searchParams.get('eventcode_id');

    const session_id = (1000000 * Math.random()) | 0;
    const super_proxy_url = `http://${username}-session-${session_id}:${password}@brd.superproxy.io:${proxyPort}`;
    const superProxyUrl = new URL(super_proxy_url);

    // console.log(data_acc_id);
    // console.log(distributor_id);

    // unsure about the headers here 
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
        // 'Cookie': `client_cookie=${link_id}`,
        // 'User-Agent': new UserAgent().toString(),
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
        // 'pac-context-data': JSON.stringify({
        //     distributorId: distributor_id,
        //     dataAccountId: data_acc_id,
        //     "daylightSavingsTime": true, 
        //   }),
      },
    }

    let response = await axios(options);
    const front_end_url = `http://${venue_name_id}.evenue.net/cgi-bin/ncommerce3/SEGetEventInfo?linkID=${link_id}&ticketCode=${eventcode_id}&groupCode=&shopperContext=&pc=&caller=&appCode=&cgc=&prc=&ppc=&psc=&sm=1&dataAccId=${data_acc_id}&siteId=ev_${link_id}`;    
    // Handle the response
    if (response.status === 200) {
        response = response.data; 
        console.log(`Successful request for: ${eventcode_id} and ${link_id}\n`);

        if (response.includes("setInterval")) {
            const pricePattern = /case '(.*?)':\s*jq\('.ev_PriceCol \[id\*="price_"\]'\)\.text\('\$(.*?)'\);/g;
            let priceMatch;
            const priceMapping = {};
        
            while (priceMatch = pricePattern.exec(response)) {
                priceMapping[priceMatch[1]] = priceMatch[2];
            }
    
            // console.log(priceMapping); 
        
            const hasPriceAdjustment = Object.keys(priceMapping).length > 0;
            const priceMappingReturn = {
                [front_end_url]: hasPriceAdjustment
            };
        
            priceMappingReturn['status'] = 200; 
            // Write the price mapping to the response
            res.write(`${JSON.stringify(priceMappingReturn)}\n\n`);
        } else if (response.includes("sectionsList")) {
            // Check for the presence of a sectionsList
            const sectionsPattern = /sectionsList\s?=\s?\[.*?\];/s;
        
            if (sectionsPattern.test(response)) {
                // Check if 'per seat donation' message exists inside the block
                const donationPattern = /per seat donation/i;
                const hasDonation = donationPattern.test(response);
                
                // Create the donation mapping based on the existence of the 'per seat donation' message
                const donationMapping = {
                    [front_end_url]: hasDonation
                };

                donationMapping['status'] = 200; 
                // Write the donation mapping to the response
                // console.log(donationMapping);
                res.write(`${JSON.stringify(donationMapping)}\n\n`);
            }
        }
        else {
              // Based on the URL from the options, create the appropriate mapping
              if (url.includes("displayEventInfoCC.js")) {
                  const noPriceAdjustedMapping = {
                      [front_end_url]: false, // 'NO PRICE ADJUSTED'
                  };
                  noPriceAdjustedMapping['status'] = 200; 
                  res.write(`${JSON.stringify(noPriceAdjustedMapping)}\n\n`);
              } else if (url.includes("pyoCC.js")) {
                  const noDonationMapping = {
                      [front_end_url]: false,
                  };
                  noDonationMapping['status'] = 200; 
                  res.write(`${JSON.stringify(noDonationMapping)}\n\n`);
              }
        }
        res.end();
      }

  } catch (error) {
    // console.error('Error in making request:', error);
    
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
        console.log(error); 
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

app.get('/production-getadjustedprices', async (req, res) => {
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

app.listen(port, () => console.log(`FRONT END ADJUSTMENTS V2 Server is running on port ${port}\n`));