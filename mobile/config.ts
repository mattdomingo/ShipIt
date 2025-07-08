/**
 * Environment Configuration for ShipIt Mobile App
 *
 * This file manages environment-specific variables, such as the API endpoint.
 * Using this file centralizes configuration and makes it easy to switch between development and production.
 */

import { Platform } from 'react-native';

/**
 * =============================================================================
 * Development Configuration
 * =============================================================================
 *
 * The development API URL is read from the `DEV_API_URL` environment variable.
 * The `start_mobile.sh` script sets this automatically based on your computer's IP address.
 */
/**
 * Development API URL
 *
 * When running the app locally, the backend URL can be provided via the
 * `DEV_API_URL` environment variable. The `start_mobile.sh` script sets this
 * automatically based on your computer's IP address. If the variable is not
 * set, we fall back to `http://localhost:8000/v1` which works when running in
 * a web browser.
 */
const DEV_API_URL = process.env.DEV_API_URL || 'http://localhost:8000/v1';

/**
 * For production builds, you would use your actual production API URL.
 */
const PROD_API_URL = 'https://api.example.com/v1'; // Replace with your actual production URL

/**
 * We use the `__DEV__` global variable provided by React Native to determine
 * if the app is running in a development environment.
 */
const isDevelopment = __DEV__;

/**
 * Determines the correct API base URL based on the environment (development or production)
 * and the platform (web or native).
 */
const getApiBaseUrl = (): string => {
  if (isDevelopment) {
    // When running in a web browser during development, 'localhost' is accessible.
    if (Platform.OS === 'web') {
      return 'http://localhost:8000/v1';
    }
    // When running on a physical mobile device, you must use your computer's local IP.
    return DEV_API_URL;
  }
  // For production builds, always use the production URL.
  return PROD_API_URL;
};

// Export the configured API base URL for use throughout the app.
export const API_BASE_URL = getApiBaseUrl();
