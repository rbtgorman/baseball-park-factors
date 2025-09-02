const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

module.exports = function() {
  try {
    const dataPath = path.join(process.cwd(), 'data/park-factors.json');
    
    let needsUpdate = true;
    if (fs.existsSync(dataPath)) {
      const stats = fs.statSync(dataPath);
      const hoursSinceUpdate = (Date.now() - stats.mtime) / (1000 * 60 * 60);
      needsUpdate = hoursSinceUpdate > 1;
    }
    
    if (needsUpdate) {
      console.log('Generating fresh park factors data...');
      try {
        execSync('python3 python/calculate_park_factors.py', { 
          cwd: process.cwd(), stdio: 'inherit'
        });
      } catch (error) {
        console.warn('Python script failed, checking for existing data...');
      }
    }
    
    if (fs.existsSync(dataPath)) {
      return JSON.parse(fs.readFileSync(dataPath, 'utf8'));
    } else {
      throw new Error('No park factors data available');
    }
    
  } catch (error) {
    console.error('Error loading park factors:', error.message);
    return {
      factors: [],
      error: 'Unable to load current park factors data. Please check back later.',
      lastUpdated: new Date().toISOString(),
      date: new Date().toLocaleDateString('en-US', { 
        weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' 
      })
    };
  }
};