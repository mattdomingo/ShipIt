/**
 * API Service for ShipIt Mobile App
 * Handles all API communication with the backend
 */

import { Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_BASE_URL } from '../config';

export interface UploadResponse {
  upload_id: string;
  filename: string;
  mime_type: string;
  status: 'PENDING' | 'PARSED' | 'READY' | 'FAILED';
}

export interface UploadStatusResponse extends UploadResponse {}

export interface ParsedContact {
  name: string | null;
  email: string | null;
  phone: string | null;
  linkedin: string | null;
  github: string | null;
}

export interface ParsedEducation {
  degree: string;
  field: string | null;
  institution: string;
  graduation_year: number | null;
  gpa: number | null;
}

export interface ParsedExperience {
  company: string;
  role: string | null;
  start_date: string | null;
  end_date: string | null;
  location: string | null;
  description: string | null;
  skills_used: string[];
}

export interface ParsedResumeData {
  upload_id: string;
  filename: string;
  contact: ParsedContact;
  education: ParsedEducation[];
  experience: ParsedExperience[];
  skills: string[];
  additional_sections: Record<string, any>;
}

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
   * Get the base URL for API calls
   */
  getBaseURL(): string {
    return this.baseURL;
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

      const uploadData = await response.json();
      await this.storeUploadRecord(uploadData);
      return uploadData;
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

  /**
   * Get parsed resume data for a specific upload
   */
  async getParsedResumeData(uploadId: string): Promise<ParsedResumeData> {
    try {
      const response = await fetch(`${this.baseURL}/uploads/resume/${uploadId}/parsed-data`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...this.getAuthHeaders(),
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `Failed to get parsed resume data: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Get parsed resume data error:', error);
      throw error;
    }
  }

  /**
   * Get all uploaded resumes for the current user
   */
  async getAllResumes(): Promise<UploadStatusResponse[]> {
    try {
      // Get from local storage for now
      const storedUploads = await this.getStoredUploads();
      
      // Update status for each upload by fetching from server
      const updatedUploads = await Promise.all(
        storedUploads.map(async (upload) => {
          try {
            const currentStatus = await this.getUploadStatus(upload.upload_id);
            return currentStatus;
          } catch (error) {
            // If we can't fetch status, return the stored version
            console.warn(`Could not fetch status for upload ${upload.upload_id}:`, error);
            return upload;
          }
        })
      );
      
      return updatedUploads;
    } catch (error) {
      console.error('Get all resumes error:', error);
      throw error;
    }
  }

  /**
   * Store uploaded resume record locally
   */
  private async storeUploadRecord(uploadData: UploadResponse): Promise<void> {
    try {
      const existingUploads = await this.getStoredUploads();
      const updatedUploads = [uploadData, ...existingUploads.filter(u => u.upload_id !== uploadData.upload_id)];
      await AsyncStorage.setItem('uploaded_resumes', JSON.stringify(updatedUploads));
    } catch (error) {
      console.error('Error storing upload record:', error);
    }
  }

  /**
   * Get all stored uploads from local storage
   */
  private async getStoredUploads(): Promise<UploadStatusResponse[]> {
    try {
      const stored = await AsyncStorage.getItem('uploaded_resumes');
      return stored ? JSON.parse(stored) : [];
    } catch (error) {
      console.error('Error getting stored uploads:', error);
      return [];
    }
  }
}

// Export singleton instance
export const apiService = new ApiService();

// Export class for testing
export default ApiService; 