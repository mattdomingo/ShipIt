/**
 * Integration Test for Resume Upload Functionality
 * Tests the complete flow from frontend to backend processing
 */

import ApiService, { apiService } from '../services/api';

// Mock file data for testing
const mockPDFFile = {
  uri: 'file:///path/to/test-resume.pdf',
  name: 'test-resume.pdf',
  mimeType: 'application/pdf',
  size: 1024000, // 1MB
};

const mockDOCXFile = {
  uri: 'file:///path/to/test-resume.docx',
  name: 'test-resume.docx',
  mimeType: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  size: 2048000, // 2MB
};

const mockLargeFile = {
  uri: 'file:///path/to/large-resume.pdf',
  name: 'large-resume.pdf',
  mimeType: 'application/pdf',
  size: 6 * 1024 * 1024, // 6MB (exceeds 5MB limit)
};

const mockInvalidFile = {
  uri: 'file:///path/to/document.txt',
  name: 'document.txt',
  mimeType: 'text/plain',
  size: 1024,
};

// Test configuration
const TEST_CONFIG = {
  apiBaseUrl: 'http://localhost:8000/v1',
  timeout: 30000, // 30 seconds
  pollingInterval: 1000, // 1 second
  maxPollingAttempts: 30,
};

class UploadIntegrationTest {
  private apiService: ApiService;
  private testResults: Array<{
    testName: string;
    passed: boolean;
    error?: string;
    details?: any;
  }> = [];

  constructor() {
    this.apiService = new ApiService(TEST_CONFIG.apiBaseUrl);
  }

  /**
   * Simulate file validation (client-side)
   */
  private validateFile(file: typeof mockPDFFile): { valid: boolean; error?: string } {
    const allowedTypes = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ];
    const maxSize = 5 * 1024 * 1024; // 5MB

    if (!allowedTypes.includes(file.mimeType)) {
      return { valid: false, error: 'Invalid file type' };
    }

    if (file.size > maxSize) {
      return { valid: false, error: 'File too large' };
    }

    const allowedExtensions = ['.pdf', '.docx'];
    const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
    
    if (!allowedExtensions.includes(fileExtension)) {
      return { valid: false, error: 'Invalid file extension' };
    }

    return { valid: true };
  }

  /**
   * Test authentication flow
   */
  async testAuthentication(): Promise<void> {
    console.log('Testing authentication...');
    
    try {
      const token = await this.apiService.getDemoToken();
      
      if (!token || typeof token !== 'string') {
        throw new Error('Invalid token received');
      }

      this.testResults.push({
        testName: 'Authentication',
        passed: true,
        details: { tokenReceived: true }
      });

      console.log('✅ Authentication test passed');
    } catch (error) {
      this.testResults.push({
        testName: 'Authentication',
        passed: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      });

      console.log('❌ Authentication test failed:', error);
      throw error; // Authentication is required for other tests
    }
  }

  /**
   * Test file validation logic
   */
  async testFileValidation(): Promise<void> {
    console.log('Testing file validation...');

    const tests = [
      { file: mockPDFFile, shouldPass: true, name: 'Valid PDF' },
      { file: mockDOCXFile, shouldPass: true, name: 'Valid DOCX' },
      { file: mockLargeFile, shouldPass: false, name: 'Large file rejection' },
      { file: mockInvalidFile, shouldPass: false, name: 'Invalid file type rejection' },
    ];

    for (const test of tests) {
      const validation = this.validateFile(test.file);
      const passed = validation.valid === test.shouldPass;

      this.testResults.push({
        testName: `File Validation - ${test.name}`,
        passed,
        details: { validation, file: test.file.name }
      });

      if (passed) {
        console.log(`✅ ${test.name} validation test passed`);
      } else {
        console.log(`❌ ${test.name} validation test failed`);
      }
    }
  }

  /**
   * Test successful file upload
   */
  async testSuccessfulUpload(): Promise<string | null> {
    console.log('Testing successful file upload...');

    try {
      // Note: In a real test environment, we would need actual file URIs
      // For now, we'll test the API contract and error handling
      
      const uploadResponse = await this.apiService.uploadResume(
        mockPDFFile.uri,
        mockPDFFile.name,
        mockPDFFile.mimeType
      );

      if (!uploadResponse.upload_id || !uploadResponse.filename) {
        throw new Error('Invalid upload response structure');
      }

      this.testResults.push({
        testName: 'Successful Upload',
        passed: true,
        details: uploadResponse
      });

      console.log('✅ Upload test passed:', uploadResponse);
      return uploadResponse.upload_id;

    } catch (error) {
      this.testResults.push({
        testName: 'Successful Upload',
        passed: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      });

      console.log('❌ Upload test failed:', error);
      return null;
    }
  }

  /**
   * Test upload status polling
   */
  async testUploadStatusPolling(uploadId: string): Promise<void> {
    console.log('Testing upload status polling...');

    try {
      let attempts = 0;
      let finalStatus = null;

      while (attempts < TEST_CONFIG.maxPollingAttempts) {
        const statusResponse = await this.apiService.getUploadStatus(uploadId);
        
        if (!statusResponse.upload_id || !statusResponse.status) {
          throw new Error('Invalid status response structure');
        }

        finalStatus = statusResponse.status;

        if (['PARSED', 'READY', 'FAILED'].includes(statusResponse.status)) {
          break;
        }

        attempts++;
        await new Promise(resolve => setTimeout(resolve, TEST_CONFIG.pollingInterval));
      }

      const passed = finalStatus !== null && finalStatus !== 'FAILED';

      this.testResults.push({
        testName: 'Upload Status Polling',
        passed,
        details: { finalStatus, attempts, uploadId }
      });

      if (passed) {
        console.log(`✅ Status polling test passed. Final status: ${finalStatus}`);
      } else {
        console.log(`❌ Status polling test failed. Final status: ${finalStatus}`);
      }

    } catch (error) {
      this.testResults.push({
        testName: 'Upload Status Polling',
        passed: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      });

      console.log('❌ Status polling test failed:', error);
    }
  }

  /**
   * Test error handling for invalid uploads
   */
  async testErrorHandling(): Promise<void> {
    console.log('Testing error handling...');

    try {
      // Test upload with invalid file
      await this.apiService.uploadResume(
        mockInvalidFile.uri,
        mockInvalidFile.name,
        mockInvalidFile.mimeType
      );

      // If we get here, the server didn't reject the invalid file
      this.testResults.push({
        testName: 'Error Handling',
        passed: false,
        error: 'Server accepted invalid file type'
      });

      console.log('❌ Error handling test failed: Server accepted invalid file');

    } catch (error) {
      // This is expected - the server should reject invalid files
      this.testResults.push({
        testName: 'Error Handling',
        passed: true,
        details: { expectedError: error instanceof Error ? error.message : 'Unknown error' }
      });

      console.log('✅ Error handling test passed: Server correctly rejected invalid file');
    }
  }

  /**
   * Run all tests
   */
  async runAllTests(): Promise<void> {
    console.log('🚀 Starting Upload Integration Tests...\n');

    try {
      // Authentication is required for all other tests
      await this.testAuthentication();

      // Run validation tests (these don't require server)
      await this.testFileValidation();

      // Run server interaction tests
      const uploadId = await this.testSuccessfulUpload();
      
      if (uploadId) {
        await this.testUploadStatusPolling(uploadId);
      }

      await this.testErrorHandling();

    } catch (error) {
      console.log('💥 Test suite failed early:', error);
    }

    this.printResults();
  }

  /**
   * Print test results summary
   */
  private printResults(): void {
    console.log('\n📊 Test Results Summary:');
    console.log('========================');

    const passed = this.testResults.filter(r => r.passed).length;
    const total = this.testResults.length;

    for (const result of this.testResults) {
      const status = result.passed ? '✅' : '❌';
      console.log(`${status} ${result.testName}`);
      
      if (!result.passed && result.error) {
        console.log(`   Error: ${result.error}`);
      }
    }

    console.log(`\n${passed}/${total} tests passed`);

    if (passed === total) {
      console.log('🎉 All tests passed! Upload functionality is working correctly.');
    } else {
      console.log('⚠️  Some tests failed. Please check the issues above.');
    }
  }
}

// Export for use in test runner
export { UploadIntegrationTest };

// If running directly
if (require.main === module) {
  const testRunner = new UploadIntegrationTest();
  testRunner.runAllTests().catch(console.error);
} 