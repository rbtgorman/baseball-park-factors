const { spawn } = require('child_process');
const path = require('path');

exports.handler = async (event, context) => {
  try {
    // Run Python script to generate fresh park factors data
    const pythonScript = path.join(__dirname, '../../python/calculate_park_factors.py');
    const parkFactors = await runPythonScript(pythonScript);

    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Cache-Control': 'no-cache' // Ensure fresh data
      },
      body: JSON.stringify(parkFactors)
    };
  } catch (error) {
    return {
      statusCode: 500,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      body: JSON.stringify({ 
        error: 'Failed to calculate park factors',
        details: error.message 
      })
    };
  }
};

function runPythonScript(scriptPath) {
  return new Promise((resolve, reject) => {
    const python = spawn('python3', [scriptPath]);
    let output = '';
    let error = '';

    python.stdout.on('data', (data) => {
      output += data.toString();
    });

    python.stderr.on('data', (data) => {
      error += data.toString();
    });

    python.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`Python script failed with code ${code}: ${error}`));
      } else {
        try {
          // Parse the JSON output from your Python script
          const result = JSON.parse(output);
          resolve(result);
        } catch (e) {
          reject(new Error(`Failed to parse Python output: ${e.message}\nOutput: ${output}`));
        }
      }
    });

    // Set timeout to prevent hanging
    setTimeout(() => {
      python.kill();
      reject(new Error('Python script timed out'));
    }, 30000); // 30 second timeout
  });
}