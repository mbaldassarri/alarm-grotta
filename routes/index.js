var express = require('express');
var conf = require("../config-example.json")
var router = express.Router();
const axios = require('axios');

const PIN = conf.pin
const LOGIN_USER = conf.username
const LOGIN_PWD = conf.password
const BASE_URL = conf.baseUrl
const AUTH_URL = BASE_URL + '/authenticate'
const ACTION_URL = BASE_URL + '/action'
const TRANSMITTER_ID = conf.transmitterId
const STATUS_KO = 'KO'
const CONNECTION_TYPE = "1"
const NB_GROUPS = 5

router.get('/alarm', function(req, res, next) {
  const cmd = req.query.status
  const delay = req.query.delay
  if(cmd !== undefined && delay !== undefined && !isNaN(delay) && delay >= 0 && (cmd === 'on' || cmd === 'off')) {
    console.log('Delay in minutes: ' + delay)
    res.end();  // Alexa systems need to get the response ASAP. Can't wait for the delay to be scheduled!
    changeAlarmStatus(cmd, delay)
      .then(cmd => console.log(cmd))
      .catch(err => console.log({message: "A Generic Error accurred", error: err}))
  } else {
    console.log({message: "Malformed URL - Wrong parameter"})
  }
});

const timeout = ms => new Promise(res => setTimeout(res, ms))

const changeAlarmStatus = async (cmd, delay) => {
  await timeout(delay*60*1000)
  let response
  try {
    const loginRes = await login();
    console.log("LOGIN -> sessionId: " + JSON.stringify(loginRes.data.sessionId, null, 1));
    const connectRes = await connect(loginRes.data.sessionId);
    console.log("CONNECT -> Connect Response: " + JSON.stringify(connectRes.data, null, 1));
    if(connectRes.data.status === STATUS_KO) {
      return {message: "Error: session already opened"}
    }
    const alarmCmd = await stateCommand(connectRes.data.ttmSessionId, cmd);
    response = alarmCmd.data.status;

    console.log("STATE COMMAND -> Change status Response: " + JSON.stringify(alarmCmd.data, null, 1))
    const disconnectRes = await disconnect(connectRes.data.ttmSessionId, loginRes.data.sessionId);
    console.log("DISCONNECT -> Disconnection data: " +  JSON.stringify(disconnectRes.data, null, 1));
  } catch (err) {
    return {message: "Error while changing status", error: err};
  }
  return {message: response};
}

const login = () => {
  return axios.post(AUTH_URL + '/login', {
    username: LOGIN_USER,
    password: LOGIN_PWD
  });
}

const connect = sessionId => {
  return axios.post(AUTH_URL + '/connect', {
    masterCode: PIN,
    transmitterId: TRANSMITTER_ID,
    sessionId: sessionId,
    connectionType: CONNECTION_TYPE
  });
}

const disconnect = (ttmSessionId, sessionId) => {
  return axios.post(AUTH_URL + '/disconnect', {
    sessionId: sessionId,
    ttmSessionId: ttmSessionId
  });
}

const stateCommand = (ttmSessionId, cmd) => {
  return axios.post(ACTION_URL + '/stateCommand', {
    ttmSessionId: ttmSessionId,
    systemState: cmd,
    currentGroup: [],
    nbGroups: NB_GROUPS
  });
}

module.exports = router;