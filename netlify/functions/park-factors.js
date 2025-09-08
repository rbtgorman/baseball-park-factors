const fs = require('fs');
const path = require('path');

exports.handler = async (event, context) => {
  try {
    const dataPath = path.join(process.cwd(), 'data/park-factors.json');
    
    // Add debugging info
    console.log('Current working directory:', process.cwd());
    console.log('Looking for file at:', dataPath);
    console.log('File exists?', fs.existsSync(dataPath));
    
    // List what files are actually there
    try {
      const files = fs.readdirSync(process.cwd());
      console.log('Files in root:', files);
      
      if (fs.existsSync('data')) {
        const dataFiles = fs.readdirSync('data');
        console.log('Files in data directory:', dataFiles);
      }
    } catch (e) {
      console.log('Error listing files:', e.message);
    }
    
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
          message: 'Data file has not been generated yet',
          debugInfo: {
            cwd: process.cwd(),
            dataPath: dataPath,
            fileExists: fs.existsSync(dataPath)
          }
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