/**
 * Environment Configuration for ShipIt Mobile App
 *
 * This file manages environment-specific variables, such as the API endpoint.
 * Using this file centralizes configuration and makes it easy to switch between development and production.
 */

import { Platform } from 'react-native';

/**
 * ====================================================================================
 * !! IMPORTANT !! - SET YOUR DEVELOPMENT API URL HERE
 * ====================================================================================
 *
 * To connect the mobile app to your local backend server, you must replace the
 * placeholder IP address with your computer's local network IP address.
 *
 * How to find your local IP address:
 *   - On macOS: Go to System Settings > Network > Wi-Fi. Your IP address is listed there.
 *   - On Windows: Open Command Prompt and type `ipconfig`. Look for the "IPv4 Address".
 *
 * The IP address will likely look like `192.168.x.x` or `10.0.x.x`.
 *
 * ====================================================================================
 */
const DEV_API_URL = 'http://172.16.0.169:8000/v1';

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
