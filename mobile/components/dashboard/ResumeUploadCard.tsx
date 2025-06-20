import React, { useState } from 'react';
import { View, Text, StyleSheet, Pressable, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Card } from '../shared/Card';
import { designTokens } from '../../theme/tokens';

interface ResumeUploadCardProps {
  lastFileName?: string;
  lastUploadedAt?: Date;
  onPress: () => void;
}

export const ResumeUploadCard: React.FC<ResumeUploadCardProps> = ({
  lastFileName,
  lastUploadedAt,
  onPress,
}) => {
  const [isDragOver, setIsDragOver] = useState(false);

  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  const handleChooseFile = () => {
    // This would integrate with document picker
    Alert.alert('File Upload', 'Document picker would open here');
  };

  return (
    <Card onPress={onPress} style={[styles.card, isDragOver && styles.cardDragOver]}>
      <View style={styles.uploadZone}>
        <View style={[styles.iconContainer, isDragOver && styles.iconContainerActive]}>
          <Ionicons 
            name="cloud-upload-outline" 
            size={32} 
            color={isDragOver ? designTokens.colors.accent : designTokens.colors.textSecondary} 
          />
        </View>
        
        <Text style={styles.title}>Resume Upload</Text>
        
        <View style={styles.dropZone}>
          <Text style={styles.dropText}>
            {isDragOver ? 'Drop your resume here' : 'Drag & drop your resume'}
          </Text>
          <Text style={styles.orText}>or</Text>
          
          <Pressable style={styles.chooseButton} onPress={handleChooseFile}>
            <Text style={styles.chooseButtonText}>Choose File</Text>
          </Pressable>
        </View>
        
        {lastFileName && lastUploadedAt && (
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
  chooseButtonText: {
    color: designTokens.colors.bgPrimary,
    fontSize: 16,
    fontWeight: '600',
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