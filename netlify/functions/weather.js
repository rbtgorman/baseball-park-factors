const fs = require('fs');
const path = require('path');

export async function handler() {
  const res = await fetch(`https://api.weatherapi.com/v1/current.json?key=${process.env.API_KEY}&q=Newark`);
  const data = await res.json();

  return {
    statusCode: 200,
    body: JSON.stringify(data),
  };
}


exports.handler = async (event, context) => {
  const { team } = event.queryStringParameters || {};
  
  if (!team) {
    return {
      statusCode: 400,
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
      body: JSON.stringify({ 
        error: 'Team parameter required',
        usage: 'GET /.netlify/functions/weather?team=BOS'
      })
    };
  }
  
  try {
    const dataPath = path.join(process.cwd(), 'data/park-factors.json');
    if (fs.existsSync(dataPath)) {
      const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
      const teamData = data.factors.find(f => f.team === team.toUpperCase());
      
      if (teamData) {
        return {
          statusCode: 200,
          headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
          body: JSON.stringify({
            team: teamData.team, ballpark: teamData.ballpark,
            weather: {
              temperature: teamData.temperatureRange,
              condition: teamData.weatherCondition,
              wind: `${teamData.windDirection} ${teamData.windSpeed}mph`
            }
          })
        };
      }
    }
    
    return {
      statusCode: 404,
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
      body: JSON.stringify({ error: 'Team not found' })
    };
    
  } catch (error) {
    return {
      statusCode: 500,
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
      body: JSON.stringify({ error: error.message })
    };
  }
};