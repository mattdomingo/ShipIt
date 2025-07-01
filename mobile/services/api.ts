/**
 * API Service for ShipIt Mobile App
 * Handles all API communication with the backend
 */

import { Platform } from 'react-native';
import { API_BASE_URL } from '../config';

export interface UploadResponse {
  upload_id: string;
  filename: string;
  mime_type: string;
  status: 'PENDING' | 'PARSED' | 'READY' | 'FAILED';
}

export interface UploadStatusResponse extends UploadResponse {}

export interface ApiError {
  code: string;
  message: string;
  details?: string | object;
}

class ApiService {
  private baseURL: string;
  private authToken: string | null = null;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  /**
   * Set authentication token (JWT)
   */
  setAuthToken(token: string) {
    this.authToken = token;
  }

  /**
   * Get authentication headers
   */
  private getAuthHeaders(): HeadersInit {
    const headers: HeadersInit = {};
    if (this.authToken) {
      headers['Authorization'] = `Bearer ${this.authToken}`;
    }
    return headers;
  }

  /**
   * Upload a resume file
   */
  async uploadResume(fileUri: string, fileName: string, mimeType: string): Promise<UploadResponse> {
    try {
      const formData = new FormData();
      const endpoint = `${this.baseURL}/uploads/resume`;

      console.log('Upload parameters:', { fileUri, fileName, mimeType, endpoint });

      if (Platform.OS === 'web') {
        // Web-based upload (e.g., running in a browser with `npm run web`)
        const response = await fetch(fileUri);
        const blob = await response.blob();
        const file = new File([blob], fileName, { type: mimeType });
        formData.append('file', file);
      } else {
        // Native mobile upload (iOS/Android)
        const file = {
          uri: fileUri,
          type: mimeType || 'application/pdf',
          name: fileName,
        };
        formData.append('file', file as any);
      }

      const headers: any = {};
      if (this.authToken) {
        headers['Authorization'] = `Bearer ${this.authToken}`;
      }

      console.log('Sending request with headers:', headers);

      const response = await fetch(endpoint, {
        method: 'POST',
        headers,
        body: formData,
      });

      if (!response.ok) {
        let errorMessage = `Upload failed with status ${response.status}`;
        try {
          const errorData = await response.json();
          console.error('Upload error response:', errorData);
          errorMessage = errorData.message || errorMessage;
          if (errorData.details) {
            console.error('Error details:', errorData.details);
          }
        } catch (e) {
          console.error('Failed to parse error response:', e);
        }
        throw new Error(errorMessage);
      }

      return await response.json();
    } catch (error) {
      console.error('Upload error:', error);
      throw error;
    }
  }

  /**
   * Check upload status
   */
  async getUploadStatus(uploadId: string): Promise<UploadStatusResponse> {
    try {
      const response = await fetch(`${this.baseURL}/uploads/resume/${uploadId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...this.getAuthHeaders(),
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `Failed to get upload status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Get upload status error:', error);
      throw error;
    }
  }

  /**
   * Get demo authentication token
   */
  async getDemoToken(): Promise<string> {
    try {
      const response = await fetch(`${this.baseURL}/auth/demo-token`, {
        method: 'GET',
        // Simple GET with no custom headers avoids CORS pre-flight issues
      });

      if (!response.ok) {
        throw new Error(`Failed to get demo token: ${response.status}`);
      }

      const data = await response.json();
      this.setAuthToken(data.access_token);
      return data.access_token;
    } catch (error) {
      console.error('Demo token error:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const apiService = new ApiService();

// Export class for testing
export default ApiService; 