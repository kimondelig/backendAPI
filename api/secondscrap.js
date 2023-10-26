const express = require('express');
const axios = require('axios');
const app = express();
const http = require('http');
const https = require('https');
const moment = require('moment');
const cheerio = require('cheerio');
const port = 3020;
const API_KEY = 'cf23df2207d99a74fbe169e3eba035e633b65d94'; 
const username = 'brd-customer-hl_e7275c4d-zone-padelis_web_unlocker_main';
const password = 'tikqvzik1t9p';
// const username = 'brd-customer-hl_e7275c4d-zone-paciolan_web_unlocker';
// const password = '2n4bgb6sdap8';
const proxyPort = 22225;

const httpAgent = new http.Agent({ keepAlive: true });
const httpsAgent = new https.Agent({ keepAlive: true, rejectUnauthorized: false });

app.use(express.json());

/*
curl -X GET "http://18.219.201.252:3020/production-getevenueurls?url=https%3A%2F%2Ffoxtheatre.evenue.net%2Fcgi-bin%2Fncommerce3%2FSEGetEventList%3FlinkID%3Dfta%26timeDateFrom%3D2023-09-28-00.00.00%26timeDateTo%3D2023-12-31-23.59.59%26shopperContext%3D%26format%3Dmini" -H "X-API-Key: cf23df2207d99a74fbe169e3eba035e633b65d94"
*/

function eventINFO(response, url) {
    let $ = cheerio.load(response);
    let scripts = $('script');
    let dataAccId = '';
    let ticketItems = [];
  
    for (let i = 0; i < scripts.length; i++) {
        let element = scripts[i];
        if ($(element).attr('type') === 'text/javascript') {
            let match = $(element).html().match(/&dataAccId=([^&]+)&locale=en_US&siteId=/);
            if (match) {
                dataAccId = match[1];
                break;  // Found the first matching script, so break from the loop
            } else {
                let alternativeMatch = $(element).html().match(/var\s+dataAccId\s*=\s*"[^"]*"\s*\|\|\s*"[^"]*";/);
                if (alternativeMatch) {
                    dataAccId = alternativeMatch[0].match(/"(\d+)"/)[1];
                    break;  // Found the first matching script, so break from the loop
                }
            }
        }
    }
  
    for (let i = 0; i < scripts.length; i++) {
        let element = scripts[i];
        if ($(element).attr('language') === 'JavaScript') {
            let event_list_pattern = $(element).html().match(/eventList\[\d+\]= new TicketItem\((.*?)\)/gs);
            if (event_list_pattern) {
                event_list_pattern.forEach((c) => {
                  let items = c.split(',');
                  let ticketItem = {
                    'eventCode': '',
                    'linkId': '',
                    'dataAccId': '',
                    'distributorId': '',
                    'url': '',
                    'venueName': '',
                    'lastupdate': moment().format('YYYY-MM-DD HH:mm')
                  };
                  
                  try {
                        ticketItem.eventCode = items[1] ? items[1].match(/"([^"]*)"/)[1] : '';
                  } catch (error) {
                        ticketItem.eventCode = '';
                  }
                
                  try {
                    ticketItem.dataAccId = dataAccId;
                  } catch (error) {
                    ticketItem.dataAccId = '';
                  }
                  
                  try {
                    ticketItem.distributorId = ticketItem.eventCode.split(':')[1];
                  } catch (error) {
                    ticketItem.distributorId = '';
                  }
                  
                  const venuenamepattern = /https:\/\/([^.]*)\./;
                  const extractedvenuename = url.match(venuenamepattern)?.[1] || '';
                  
                  const linkidpattern = /linkID=([^&]+)/;
                  const extractedlinkid = url.match(linkidpattern)?.[1] || '';
                  
                  ticketItem.linkId = extractedlinkid;
                  ticketItem.venueName = extractedvenuename; 
                  ticketItem.url = extractedvenuename ? `https://${extractedvenuename}.evenue.net/cgi-bin/ncommerce3/SEGetEventInfo?linkID=${ticketItem.linkId}&ticketCode=${ticketItem.eventCode}&groupCode=&shopperContext=&pc=&caller=&appCode=&cgc=&prc=&ppc=&psc=` : '';
                  
                  // Only push to the array if all properties are filled
                  if (Object.values(ticketItem).every(val => val)) {
                    ticketItems.push(ticketItem);
                  }                
                });
                break;  // Found the first matching script, so break from the loop
            }
        }
    }
  
    return ticketItems;
  }

async function makeRequest(data, res) {
  try {
    const url = data.url; 

    console.log('...Requesting: \n')
    console.log(url);
    console.log('\n')


    const session_id = (1000000 * Math.random()) | 0;
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
    const output = {} 
    // Handle the response
    if (response.status === 200) {
        console.log(`Successful SCRAP EVENTS request for: ${url}\n`);
        response = eventINFO(response.data, url); 
        output['data'] = response;
        output['status'] = 200; 
        res.write(JSON.stringify(output));
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

app.get('/production-getevenueurls', async (req, res) => {
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

app.listen(port, () => console.log(`EVENUE URLs V2 Server is running on port ${port}\n`));