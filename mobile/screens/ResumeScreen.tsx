import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Dimensions,
  Animated,
  SafeAreaView,
  RefreshControl,
  Alert,
} from 'react-native';
import { designTokens } from '../theme/tokens';
import { SideBar } from '../components/navigation/SideBar';
import { ResumeTile } from '../components/dashboard/ResumeTile';
import { apiService, UploadStatusResponse } from '../services/api';

const { width: screenWidth } = Dimensions.get('window');

interface ResumeScreenProps {
  navigation: any;
}

export default function ResumeScreen({ navigation }: ResumeScreenProps) {
  const [resumes, setResumes] = useState<UploadStatusResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  
  // Animation refs for entrance animations
  const fadeAnims = useRef<Animated.Value[]>([]).current;
  const slideAnims = useRef<Animated.Value[]>([]).current;

  useEffect(() => {
    loadResumes();
  }, []);

  useEffect(() => {
    // Initialize animations for current resumes
    const numResumes = resumes.length;
    
    // Clear existing animations
    fadeAnims.length = 0;
    slideAnims.length = 0;
    
    // Create new animations
    for (let i = 0; i < numResumes; i++) {
      fadeAnims.push(new Animated.Value(0));
      slideAnims.push(new Animated.Value(24));
    }
    
    // Start entrance animations
    if (numResumes > 0) {
      const animations = fadeAnims.map((fadeAnim, index) => {
        const slideAnim = slideAnims[index];
        return Animated.parallel([
          Animated.timing(fadeAnim, {
            toValue: 1,
            duration: 600,
            delay: index * 100,
            useNativeDriver: true,
          }),
          Animated.spring(slideAnim, {
            toValue: 0,
            delay: index * 100,
            tension: 100,
            friction: 8,
            useNativeDriver: true,
          }),
        ]);
      });

      Animated.stagger(50, animations).start();
    }
  }, [resumes]);

  const loadResumes = async () => {
    try {
      setIsLoading(true);
      
      // Get demo token first
      await apiService.getDemoToken();
      
      // Fetch all resumes
      const resumeList = await apiService.getAllResumes();
      setResumes(resumeList);
    } catch (error) {
      console.error('Failed to load resumes:', error);
      Alert.alert(
        'Error',
        'Failed to load your resumes. Please try again.',
        [{ text: 'OK' }]
      );
    } finally {
      setIsLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadResumes();
    setRefreshing(false);
  };

  const handleNavigation = (route: string) => {
    navigation.navigate(route);
  };

  const handleResumePress = (resume: UploadStatusResponse) => {
    // For now, just show an alert with resume info
    Alert.alert(
      'Resume Details',
      `File: ${resume.filename}\nStatus: ${resume.status}`,
      [{ text: 'OK' }]
    );
  };

  const getGridItemLayoutStyle = (colSpan: number) => {
    const isMobile = screenWidth <= 768;
    
    if (isMobile) {
      return { width: '100%' as const, marginBottom: designTokens.spacing.gridGap };
    }
    
    // Grid layout for tablet/desktop
    const columnWidth = (screenWidth - 240 - (designTokens.spacing.gridGap * 5)) / 12;
    const width = columnWidth * colSpan + designTokens.spacing.gridGap * (colSpan - 1);
    
    return { width, marginBottom: designTokens.spacing.gridGap };
  };

  const getGridItemAnimationStyle = (index: number) => {
    if (index >= fadeAnims.length) return {};
    
    return {
      opacity: fadeAnims[index],
      transform: [{ translateY: slideAnims[index] }],
    };
  };

  const renderEmptyState = () => (
    <View style={styles.emptyState}>
      <Text style={styles.emptyTitle}>No Resumes Yet</Text>
      <Text style={styles.emptySubtitle}>
        Upload your first resume from the Dashboard to get started
      </Text>
    </View>
  );

  const renderResumeGrid = () => (
    <View style={[styles.grid, screenWidth <= 768 && styles.gridMobile]}>
      {resumes.map((resume, index) => (
        <View key={resume.upload_id} style={getGridItemLayoutStyle(4)}>
          <Animated.View style={getGridItemAnimationStyle(index)}>
            <ResumeTile
              resume={resume}
              onPress={() => handleResumePress(resume)}
            />
          </Animated.View>
        </View>
      ))}
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.layout}>
        <SideBar activeRoute="Resume" onNavigate={handleNavigation} />
        
        <ScrollView 
          style={styles.content} 
          showsVerticalScrollIndicator={false}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={onRefresh}
              tintColor={designTokens.colors.accent}
            />
          }
        >
          <View style={styles.header}>
            <Text style={styles.pageTitle}>My Resumes</Text>
            <Text style={styles.pageSubtitle}>
              Manage and view your uploaded resumes
            </Text>
          </View>

          {isLoading ? (
            <View style={styles.loadingState}>
              <Text style={styles.loadingText}>Loading resumes...</Text>
            </View>
          ) : resumes.length === 0 ? (
            renderEmptyState()
          ) : (
            renderResumeGrid()
          )}
        </ScrollView>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: designTokens.colors.bgPrimary,
  },
  layout: {
    flex: 1,
    flexDirection: 'row',
  },
  content: {
    flex: 1,
    paddingHorizontal: designTokens.spacing.gridGap,
    paddingTop: 20,
  },
  header: {
    marginBottom: 32,
  },
  pageTitle: {
    fontSize: designTokens.typography.h1Size,
    fontWeight: 'bold',
    color: designTokens.colors.textPrimary,
    marginBottom: 8,
  },
  pageSubtitle: {
    fontSize: 16,
    color: designTokens.colors.textSecondary,
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    paddingBottom: 40,
  },
  gridMobile: {
    flexDirection: 'column',
    alignItems: 'stretch',
  },
  loadingState: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingTop: 100,
  },
  loadingText: {
    fontSize: 16,
    color: designTokens.colors.textSecondary,
  },
  emptyState: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingTop: 100,
  },
  emptyTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: designTokens.colors.textPrimary,
    marginBottom: 12,
  },
  emptySubtitle: {
    fontSize: 16,
    color: designTokens.colors.textSecondary,
    textAlign: 'center',
    lineHeight: 24,
  },
}); 