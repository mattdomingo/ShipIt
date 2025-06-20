import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, ScrollView, Animated } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Card } from '../shared/Card';
import { designTokens } from '../../theme/tokens';

interface JobPosting {
  id: string;
  title: string;
  company: string;
  postedDate: string;
  source: string;
  isNew?: boolean;
}

interface NewPostingsCardProps {
  postings: JobPosting[];
  onPress: () => void;
}

// Dummy data
const dummyPostings: JobPosting[] = [
  {
    id: '1',
    title: 'Software Engineer Intern',
    company: 'Google',
    postedDate: '2h',
    source: 'LinkedIn',
    isNew: true,
  },
  {
    id: '2',
    title: 'Product Manager Intern',
    company: 'Microsoft',
    postedDate: '4h',
    source: 'Indeed',
    isNew: true,
  },
  {
    id: '3',
    title: 'Data Science Intern',
    company: 'Meta',
    postedDate: '1d',
    source: 'Glassdoor',
  },
  {
    id: '4',
    title: 'UX Design Intern',
    company: 'Apple',
    postedDate: '2d',
    source: 'LinkedIn',
  },
  {
    id: '5',
    title: 'Marketing Intern',
    company: 'Amazon',
    postedDate: '3d',
    source: 'Indeed',
  },
  {
    id: '6',
    title: 'Finance Intern',
    company: 'JPMorgan Chase',
    postedDate: '3d',
    source: 'Company Site',
  },
];

const JobPostingItem: React.FC<{ posting: JobPosting }> = ({ posting }) => {
  const highlightAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (posting.isNew) {
      // Highlight animation for new jobs
      Animated.sequence([
        Animated.timing(highlightAnim, {
          toValue: 1,
          duration: 300,
          useNativeDriver: false,
        }),
        Animated.delay(3000),
        Animated.timing(highlightAnim, {
          toValue: 0,
          duration: 500,
          useNativeDriver: false,
        }),
      ]).start();
    }
  }, [posting.isNew, highlightAnim]);

  const animatedBackgroundColor = highlightAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ['transparent', designTokens.colors.highlight + '30'],
  });

  return (
    <Animated.View 
      style={[
        styles.postingItem,
        { backgroundColor: animatedBackgroundColor }
      ]}
    >
      <View style={styles.postingHeader}>
        <Text style={styles.jobTitle} numberOfLines={1}>
          {posting.title}
        </Text>
        {posting.isNew && (
          <View style={styles.newBadge}>
            <Text style={styles.newBadgeText}>NEW</Text>
          </View>
        )}
      </View>
      
      <Text style={styles.companyName} numberOfLines={1}>
        {posting.company}
      </Text>
      
      <View style={styles.postingMeta}>
        <View style={styles.sourceContainer}>
          <Ionicons name="business-outline" size={12} color={designTokens.colors.textSecondary} />
          <Text style={styles.sourceText}>{posting.source}</Text>
        </View>
        <Text style={styles.postedDate}>{posting.postedDate}</Text>
      </View>
    </Animated.View>
  );
};

export const NewPostingsCard: React.FC<NewPostingsCardProps> = ({ 
  postings = dummyPostings, 
  onPress 
}) => {
  const displayedPostings = postings.slice(0, 6);

  return (
    <Card onPress={onPress}>
      <View style={styles.header}>
        <View style={styles.titleContainer}>
          <Ionicons name="briefcase-outline" size={20} color={designTokens.colors.accent} />
          <Text style={styles.title}>New Postings</Text>
        </View>
        <Text style={styles.count}>{postings.length} available</Text>
      </View>

      <ScrollView 
        style={styles.scrollContainer}
        showsVerticalScrollIndicator={false}
      >
        {displayedPostings.map((posting) => (
          <JobPostingItem key={posting.id} posting={posting} />
        ))}
        
        {postings.length > 6 && (
          <View style={styles.moreIndicator}>
            <Text style={styles.moreText}>
              +{postings.length - 6} more postings
            </Text>
            <Ionicons name="arrow-forward" size={14} color={designTokens.colors.accent} />
          </View>
        )}
      </ScrollView>
    </Card>
  );
};

const styles = StyleSheet.create({
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  titleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  title: {
    fontSize: 18,
    fontWeight: '600',
    color: designTokens.colors.textPrimary,
    marginLeft: 8,
  },
  count: {
    fontSize: 12,
    color: designTokens.colors.textSecondary,
    backgroundColor: designTokens.colors.accent + '20',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  scrollContainer: {
    maxHeight: 280,
  },
  postingItem: {
    paddingVertical: 12,
    paddingHorizontal: 4,
    borderBottomWidth: 1,
    borderBottomColor: designTokens.colors.textSecondary + '20',
    borderRadius: 6,
  },
  postingHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  jobTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: designTokens.colors.textPrimary,
    flex: 1,
    marginRight: 8,
  },
  newBadge: {
    backgroundColor: designTokens.colors.highlight,
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 8,
  },
  newBadgeText: {
    fontSize: 10,
    fontWeight: 'bold',
    color: designTokens.colors.bgPrimary,
  },
  companyName: {
    fontSize: 13,
    color: designTokens.colors.textSecondary,
    marginBottom: 6,
  },
  postingMeta: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  sourceContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  sourceText: {
    fontSize: 11,
    color: designTokens.colors.textSecondary,
    marginLeft: 4,
  },
  postedDate: {
    fontSize: 11,
    color: designTokens.colors.textSecondary,
  },
  moreIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    marginTop: 8,
  },
  moreText: {
    fontSize: 14,
    color: designTokens.colors.accent,
    marginRight: 4,
  },
}); 