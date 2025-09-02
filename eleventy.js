module.exports = function(eleventyConfig) {
  // Copy static assets
  eleventyConfig.addPassthroughCopy("src/assets");
  eleventyConfig.addPassthroughCopy("data");
  
  // Add filters
  eleventyConfig.addFilter("dateFormat", function(date) {
    return new Date(date).toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  });
  
  eleventyConfig.addFilter("timeFormat", function(date) {
    return new Date(date).toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  });
  
  eleventyConfig.addFilter("percentage", function(value) {
    const diff = value - 100;
    const sign = diff > 0 ? '+' : '';
    return `${sign}${diff.toFixed(0)}%`;
  });
  
  eleventyConfig.addFilter("factorClass", function(value) {
    if (value > 105) return "factor-positive";
    if (value < 95) return "factor-negative";
    return "factor-neutral";
  });

  return {
    dir: {
      input: "src",
      output: "dist",
      includes: "_includes",
      data: "_data"
    }
  };
};