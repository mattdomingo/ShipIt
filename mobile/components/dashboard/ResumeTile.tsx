import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, Pressable, ActivityIndicator, Alert, Linking } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Card } from '../shared/Card';
import { designTokens } from '../../theme/tokens';
import { UploadStatusResponse, ParsedResumeData, apiService } from '../../services/api';

interface ResumeTileProps {
  resume: UploadStatusResponse;
  onPress: (resume: UploadStatusResponse) => void;
}

export const ResumeTile: React.FC<ResumeTileProps> = ({ resume, onPress }) => {
  const [parsedData, setParsedData] = useState<ParsedResumeData | null>(null);
  const [isLoadingData, setIsLoadingData] = useState(false);

  useEffect(() => {
    if (resume.status === 'PARSED') {
      loadParsedData();
    }
  }, [resume.status]);

  const loadParsedData = async () => {
    try {
      setIsLoadingData(true);
      const data = await apiService.getParsedResumeData(resume.upload_id);
      setParsedData(data);
    } catch (error) {
      console.error('Failed to load parsed data:', error);
      // Silently fail - the tile will just show basic info
    } finally {
      setIsLoadingData(false);
    }
  };

  const formatDate = (dateStr: string | null): string => {
    if (!dateStr) return '';
    try {
      return new Date(dateStr).toLocaleDateString();
    } catch {
      return dateStr;
    }
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'PARSED':
        return '#10B981'; // Green
      case 'PENDING':
        return '#F59E0B'; // Orange
      case 'FAILED':
        return '#EF4444'; // Red
      default:
        return designTokens.colors.textSecondary;
    }
  };

  const getStatusIcon = (status: string): keyof typeof Ionicons.glyphMap => {
    switch (status) {
      case 'PARSED':
        return 'checkmark-circle';
      case 'PENDING':
        return 'time-outline';
      case 'FAILED':
        return 'close-circle';
      default:
        return 'document-text-outline';
    }
  };

  const handleViewPDF = async () => {
    try {
      // Get demo token first
      await apiService.getDemoToken();
      
      // Construct the PDF URL
      const pdfUrl = `${apiService.getBaseURL()}/v1/uploads/resume/${resume.upload_id}/file`;
      
      // For mobile devices, we can open with the system's default PDF viewer
      const canOpen = await Linking.canOpenURL(pdfUrl);
      
      if (canOpen) {
        await Linking.openURL(pdfUrl);
      } else {
        Alert.alert(
          'Cannot Open PDF', 
          'Unable to open PDF viewer. Please check if you have a PDF reader installed.',
          [{ text: 'OK' }]
        );
      }
    } catch (error) {
      console.error('Failed to open PDF:', error);
      Alert.alert(
        'Error',
        'Failed to open PDF. Please try again.',
        [{ text: 'OK' }]
      );
    }
  };

  const handleTilePress = () => {
    if (resume.status === 'PARSED') {
      // Show options for parsed resumes
      Alert.alert(
        'Resume Options',
        `${resume.filename}\nStatus: ${resume.status}`,
        [
          { text: 'View PDF', onPress: handleViewPDF },
          { text: 'View Details', onPress: () => onPress(resume) },
          { text: 'Cancel', style: 'cancel' }
        ]
      );
    } else if (resume.mime_type === 'application/pdf') {
      // For PDFs that aren't parsed yet, offer to view PDF or show details
      Alert.alert(
        'Resume Actions',
        `${resume.filename}\nStatus: ${resume.status}`,
        [
          { text: 'View PDF', onPress: handleViewPDF },
          { text: 'View Details', onPress: () => onPress(resume) },
          { text: 'Cancel', style: 'cancel' }
        ]
      );
    } else {
      // For non-PDF files, just show basic info
      onPress(resume);
    }
  };

  const renderBasicInfo = () => (
    <View style={styles.content}>
      <View style={styles.header}>
        <Text style={styles.filename} numberOfLines={1}>
          {resume.filename}
        </Text>
        <View style={styles.statusBadge}>
          <Ionicons 
            name={getStatusIcon(resume.status)} 
            size={14} 
            color={getStatusColor(resume.status)} 
          />
          <Text style={[styles.statusText, { color: getStatusColor(resume.status) }]}>
            {resume.status}
          </Text>
        </View>
      </View>
      
      <Text style={styles.mimeType}>{resume.mime_type}</Text>
      
      {resume.status !== 'PARSED' && (
        <Text style={styles.statusMessage}>
          {resume.status === 'PENDING' && 'Processing your resume...'}
          {resume.status === 'FAILED' && 'Failed to process resume'}
        </Text>
      )}

      {resume.mime_type === 'application/pdf' && (
        <View style={styles.actionHint}>
          <Ionicons name="eye-outline" size={16} color={designTokens.colors.accent} />
          <Text style={styles.actionHintText}>Tap to view PDF</Text>
        </View>
      )}
    </View>
  );

  const renderParsedInfo = () => {
    if (isLoadingData) {
      return (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="small" color={designTokens.colors.accent} />
          <Text style={styles.loadingText}>Loading details...</Text>
        </View>
      );
    }

    if (!parsedData) {
      return renderBasicInfo();
    }

    return (
      <View style={styles.content}>
        <View style={styles.header}>
          <Text style={styles.filename} numberOfLines={1}>
            {resume.filename}
          </Text>
          <View style={styles.statusBadge}>
            <Ionicons 
              name={getStatusIcon(resume.status)} 
              size={14} 
              color={getStatusColor(resume.status)} 
            />
            <Text style={[styles.statusText, { color: getStatusColor(resume.status) }]}>
              {resume.status}
            </Text>
          </View>
        </View>

        {parsedData.contact.name && (
          <Text style={styles.contactName} numberOfLines={1}>
            {parsedData.contact.name}
          </Text>
        )}

        {parsedData.contact.email && (
          <Text style={styles.contactInfo} numberOfLines={1}>
            {parsedData.contact.email}
          </Text>
        )}

        <View style={styles.summaryRow}>
          <View style={styles.summaryItem}>
            <Text style={styles.summaryCount}>{parsedData.experience.length}</Text>
            <Text style={styles.summaryLabel}>Experience</Text>
          </View>
          <View style={styles.summaryItem}>
            <Text style={styles.summaryCount}>{parsedData.education.length}</Text>
            <Text style={styles.summaryLabel}>Education</Text>
          </View>
          <View style={styles.summaryItem}>
            <Text style={styles.summaryCount}>{parsedData.skills.length}</Text>
            <Text style={styles.summaryLabel}>Skills</Text>
          </View>
        </View>

        {parsedData.experience.length > 0 && (
          <View style={styles.latestExperience}>
            <Text style={styles.sectionLabel}>Latest Experience:</Text>
            <Text style={styles.experienceText} numberOfLines={1}>
              {parsedData.experience[0].role} at {parsedData.experience[0].company}
            </Text>
          </View>
        )}

        <View style={styles.actionHint}>
          <Ionicons name="eye-outline" size={16} color={designTokens.colors.accent} />
          <Text style={styles.actionHintText}>Tap to view PDF</Text>
        </View>
      </View>
    );
  };

  return (
    <Card onPress={handleTilePress} style={styles.card}>
      {resume.status === 'PARSED' ? renderParsedInfo() : renderBasicInfo()}
    </Card>
  );
};

const styles = StyleSheet.create({
  card: {
    minHeight: 180,
    borderWidth: 1,
    borderColor: designTokens.colors.textSecondary + '20',
  },
  content: {
    flex: 1,
    padding: designTokens.spacing.cardPadding,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  filename: {
    fontSize: 16,
    fontWeight: '600',
    color: designTokens.colors.textPrimary,
    flex: 1,
    marginRight: 8,
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: designTokens.colors.bgMuted,
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusText: {
    fontSize: 12,
    fontWeight: '500',
    marginLeft: 4,
  },
  mimeType: {
    fontSize: 12,
    color: designTokens.colors.textSecondary,
    marginBottom: 8,
  },
  statusMessage: {
    fontSize: 14,
    color: designTokens.colors.textSecondary,
    fontStyle: 'italic',
  },
  loadingContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: designTokens.spacing.cardPadding,
  },
  loadingText: {
    fontSize: 14,
    color: designTokens.colors.textSecondary,
    marginTop: 8,
  },
  contactName: {
    fontSize: 18,
    fontWeight: '600',
    color: designTokens.colors.textPrimary,
    marginBottom: 4,
  },
  contactInfo: {
    fontSize: 14,
    color: designTokens.colors.textSecondary,
    marginBottom: 16,
  },
  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingVertical: 12,
    borderTopWidth: 1,
    borderBottomWidth: 1,
    borderColor: designTokens.colors.textSecondary + '20',
    marginBottom: 12,
  },
  summaryItem: {
    alignItems: 'center',
  },
  summaryCount: {
    fontSize: 20,
    fontWeight: 'bold',
    color: designTokens.colors.accent,
  },
  summaryLabel: {
    fontSize: 12,
    color: designTokens.colors.textSecondary,
    marginTop: 2,
  },
  latestExperience: {
    marginTop: 8,
  },
  sectionLabel: {
    fontSize: 12,
    color: designTokens.colors.textSecondary,
    marginBottom: 4,
  },
  experienceText: {
    fontSize: 14,
    color: designTokens.colors.textPrimary,
    fontWeight: '500',
  },
  actionHint: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 12,
    paddingVertical: 8,
    paddingHorizontal: 12,
    backgroundColor: designTokens.colors.bgMuted,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: designTokens.colors.accent + '20',
  },
  actionHintText: {
    fontSize: 14,
    color: designTokens.colors.accent,
    marginLeft: 8,
  },
}); 