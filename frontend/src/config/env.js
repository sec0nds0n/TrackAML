// Environment configuration
const config = {
  development: {
    API_BASE_URL: 'http://203.194.113.33',
    API_TIMEOUT: 10000,
    ENABLE_LOGGING: true,
    ENABLE_QUICK_LOGIN: true,
  },
  production: {
    API_BASE_URL: 'http://203.194.113.33',
    API_TIMEOUT: 15000,
    ENABLE_LOGGING: false,
    ENABLE_QUICK_LOGIN: false,
  },
  staging: {
    API_BASE_URL: 'http://203.194.113.33',
    API_TIMEOUT: 12000,
    ENABLE_LOGGING: true,
    ENABLE_QUICK_LOGIN: true,
  }
};

const currentEnv = process.env.NODE_ENV || 'development';
const envConfig = config[currentEnv] || config.development;

export default {
  ...envConfig,
  NODE_ENV: currentEnv,
  isDevelopment: currentEnv === 'development',
  isProduction: currentEnv === 'production',
  isStaging: currentEnv === 'staging',
};