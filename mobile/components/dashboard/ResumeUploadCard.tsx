import React, { useState, useCallback } from 'react';
import { View, Text, StyleSheet, Pressable, Alert, ActivityIndicator } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as DocumentPicker from 'expo-document-picker';
import { Card } from '../shared/Card';
import { designTokens } from '../../theme/tokens';
import { apiService, UploadResponse } from '../../services/api';

interface ResumeUploadCardProps {
  lastFileName?: string;
  lastUploadedAt?: Date;
  onPress: () => void;
  onUploadSuccess?: (uploadData: UploadResponse) => void;
  onUploadError?: (error: string) => void;
}

export const ResumeUploadCard: React.FC<ResumeUploadCardProps> = ({
  lastFileName,
  lastUploadedAt,
  onPress,
  onUploadSuccess,
  onUploadError,
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  const validateFile = (file: DocumentPicker.DocumentPickerAsset): boolean => {
    // Check file type
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    const allowedExtensions = ['.pdf', '.docx'];
    
    if (!allowedTypes.includes(file.mimeType || '')) {
      Alert.alert(
        'Invalid File Type',
        'Please select a PDF or DOCX file.',
        [{ text: 'OK' }]
      );
      return false;
    }

    // Check file extension as backup
    const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
    if (!allowedExtensions.includes(fileExtension)) {
      Alert.alert(
        'Invalid File Extension',
        'File must have .pdf or .docx extension.',
        [{ text: 'OK' }]
      );
      return false;
    }

    // Check file size (5MB limit)
    const maxSize = 5 * 1024 * 1024; // 5MB
    if (file.size && file.size > maxSize) {
      Alert.alert(
        'File Too Large',
        `File size must be less than 5MB. Your file is ${(file.size / 1024 / 1024).toFixed(2)}MB.`,
        [{ text: 'OK' }]
      );
      return false;
    }

    return true;
  };

  const handleFileUpload = useCallback(async (file: DocumentPicker.DocumentPickerAsset) => {
    if (!validateFile(file)) {
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);

    try {
      // Get demo token first (in production, this would be handled by authentication)
      await apiService.getDemoToken();

      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      // Upload the file
      const uploadResponse = await apiService.uploadResume(
        file.uri,
        file.name,
        file.mimeType || 'application/pdf'
      );

      // Complete progress
      clearInterval(progressInterval);
      setUploadProgress(100);

      // Success feedback
      Alert.alert(
        'Upload Successful',
        `Resume "${file.name}" has been uploaded successfully and is being processed.`,
        [{ text: 'OK' }]
      );

      // Callback to parent component
      onUploadSuccess?.(uploadResponse);

      // Optional: Poll for processing status
      setTimeout(() => {
        pollUploadStatus(uploadResponse.upload_id);
      }, 2000);

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Upload failed';
      
      Alert.alert(
        'Upload Failed',
        errorMessage,
        [{ text: 'OK' }]
      );

      onUploadError?.(errorMessage);
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  }, [onUploadSuccess, onUploadError]);

  const pollUploadStatus = async (uploadId: string) => {
    try {
      const status = await apiService.getUploadStatus(uploadId);
      
      if (status.status === 'PARSED' || status.status === 'READY') {
        Alert.alert(
          'Processing Complete',
          'Your resume has been successfully processed and is ready for use.',
          [{ text: 'OK' }]
        );
      } else if (status.status === 'FAILED') {
        Alert.alert(
          'Processing Failed',
          'There was an error processing your resume. Please try uploading again.',
          [{ text: 'OK' }]
        );
      } else if (status.status === 'PENDING') {
        // Continue polling after 3 seconds
        setTimeout(() => pollUploadStatus(uploadId), 3000);
      }
    } catch (error) {
      console.warn('Failed to check upload status:', error);
    }
  };

  const handleChooseFile = useCallback(async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
        copyToCacheDirectory: true,
        multiple: false,
      });

      if (!result.canceled && result.assets && result.assets.length > 0) {
        const file = result.assets[0];
        console.log('DocumentPicker result:', {
          uri: file.uri,
          name: file.name,
          size: file.size,
          mimeType: file.mimeType,
        });
        await handleFileUpload(file);
      }
    } catch (error) {
      console.error('Document picker error:', error);
      Alert.alert(
        'Error',
        'Failed to open document picker. Please try again.',
        [{ text: 'OK' }]
      );
    }
  }, [handleFileUpload]);

  // Note: React Native doesn't support real drag and drop like web browsers
  // For mobile apps, we'll focus on the file picker functionality
  // The drag styling is kept for visual consistency but won't be functional on mobile

  return (
    <Card onPress={onPress} style={[styles.card, isDragOver && styles.cardDragOver]}>
      <View style={styles.uploadZone}>
        <View style={[styles.iconContainer, isDragOver && styles.iconContainerActive]}>
          {isUploading ? (
            <ActivityIndicator 
              size={32} 
              color={designTokens.colors.accent} 
            />
          ) : (
            <Ionicons 
              name="cloud-upload-outline" 
              size={32} 
              color={isDragOver ? designTokens.colors.accent : designTokens.colors.textSecondary} 
            />
          )}
        </View>
        
        <Text style={styles.title}>Resume Upload</Text>
        
        {isUploading ? (
          <View style={styles.uploadProgress}>
            <Text style={styles.uploadText}>
              Uploading... {uploadProgress}%
            </Text>
            <View style={styles.progressBar}>
              <View 
                style={[
                  styles.progressFill, 
                  { width: `${uploadProgress}%` }
                ]} 
              />
            </View>
          </View>
        ) : (
          <View style={styles.dropZone}>
            <Text style={styles.dropText}>
              {isDragOver ? 'Drop your resume here' : 'Tap to select your resume'}
            </Text>
            <Text style={styles.orText}>PDF or DOCX files only</Text>
            
            <Pressable 
              style={[styles.chooseButton, isUploading && styles.chooseButtonDisabled]} 
              onPress={handleChooseFile}
              disabled={isUploading}
            >
              <Text style={styles.chooseButtonText}>Choose File</Text>
            </Pressable>
          </View>
        )}
        
        {lastFileName && lastUploadedAt && !isUploading && (
          <View style={styles.lastUpload}>
            <View style={styles.fileInfo}>
              <Ionicons name="document-text" size={16} color={designTokens.colors.accentSoft} />
              <Text style={styles.fileName}>{lastFileName}</Text>
            </View>
            <Text style={styles.uploadDate}>
              Uploaded {formatDate(lastUploadedAt)}
            </Text>
          </View>
        )}
      </View>
    </Card>
  );
};

const styles = StyleSheet.create({
  card: {
    minHeight: 200,
    borderWidth: 2,
    borderColor: 'transparent',
    borderStyle: 'dashed',
  },
  cardDragOver: {
    borderColor: designTokens.colors.accent,
    backgroundColor: designTokens.colors.accent + '10',
  },
  uploadZone: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  iconContainer: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: designTokens.colors.bgMuted,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
    borderWidth: 2,
    borderColor: designTokens.colors.textSecondary + '30',
  },
  iconContainerActive: {
    backgroundColor: designTokens.colors.accent + '20',
    borderColor: designTokens.colors.accent,
  },
  title: {
    fontSize: 20,
    fontWeight: '600',
    color: designTokens.colors.textPrimary,
    marginBottom: 16,
  },
  dropZone: {
    alignItems: 'center',
    marginBottom: 20,
  },
  dropText: {
    fontSize: 16,
    color: designTokens.colors.textSecondary,
    marginBottom: 8,
  },
  orText: {
    fontSize: 14,
    color: designTokens.colors.textSecondary,
    marginBottom: 12,
  },
  chooseButton: {
    backgroundColor: designTokens.colors.accentSoft,
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  chooseButtonDisabled: {
    opacity: 0.5,
  },
  chooseButtonText: {
    color: designTokens.colors.bgPrimary,
    fontSize: 16,
    fontWeight: '600',
  },
  uploadProgress: {
    alignItems: 'center',
    width: '100%',
    marginBottom: 20,
  },
  uploadText: {
    fontSize: 16,
    color: designTokens.colors.textPrimary,
    marginBottom: 12,
  },
  progressBar: {
    width: '80%',
    height: 8,
    backgroundColor: designTokens.colors.bgMuted,
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: designTokens.colors.accent,
    borderRadius: 4,
  },
  lastUpload: {
    alignItems: 'center',
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: designTokens.colors.textSecondary + '20',
    width: '100%',
  },
  fileInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  fileName: {
    marginLeft: 8,
    fontSize: 14,
    fontWeight: '500',
    color: designTokens.colors.textPrimary,
  },
  uploadDate: {
    fontSize: 12,
    color: designTokens.colors.textSecondary,
  },
}); 