const fs = require('fs');
const path = require('path');

exports.handler = async (event, context) => {
  try {
    const dataPath = path.join(process.cwd(), 'data/park-factors.json');
    
    if (fs.existsSync(dataPath)) {
      const parkFactorsData = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
      return {
        statusCode: 200,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
          'Cache-Control': 'public, max-age=3600'
        },
        body: JSON.stringify(parkFactorsData)
      };
    } else {
      return {
        statusCode: 404,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        },
        body: JSON.stringify({ 
          error: 'Park factors data not found',
          message: 'Data file has not been generated yet'
        })
      };
    }
  } catch (error) {
    return {
      statusCode: 500,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      body: JSON.stringify({ error: 'Internal server error', message: error.message })
    };
  }
};