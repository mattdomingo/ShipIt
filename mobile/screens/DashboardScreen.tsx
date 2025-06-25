import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Dimensions,
  Animated,
  SafeAreaView,
} from 'react-native';
import { designTokens } from '../theme/tokens';
import { SideBar } from '../components/navigation/SideBar';
import { ResumeUploadCard } from '../components/dashboard/ResumeUploadCard';
import { ApplicationsChartCard } from '../components/dashboard/ApplicationsChartCard';
import { WeeklyGoalCard } from '../components/dashboard/WeeklyGoalCard';
import { NewPostingsCard } from '../components/dashboard/NewPostingsCard';
import { NewsCard } from '../components/dashboard/NewsCard';
import { UploadResponse } from '../services/api';

const { width: screenWidth } = Dimensions.get('window');

interface DashboardScreenProps {
  navigation: any;
}

export default function DashboardScreen({ navigation }: DashboardScreenProps) {
  const [goalTarget, setGoalTarget] = useState(5);
  const [currentProgress, setCurrentProgress] = useState(3);
  
  // Upload state management
  const [lastUpload, setLastUpload] = useState<{
    fileName: string;
    uploadedAt: Date;
    uploadId: string;
  } | null>({
    fileName: "John_Doe_Resume_v3.pdf",
    uploadedAt: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
    uploadId: "demo-upload-id"
  });
  
  // Animation refs for entrance animations
  const fadeAnims = useRef([
    new Animated.Value(0),
    new Animated.Value(0),
    new Animated.Value(0),
    new Animated.Value(0),
    new Animated.Value(0),
    new Animated.Value(0),
  ]).current;
  
  const slideAnims = useRef([
    new Animated.Value(24),
    new Animated.Value(24),
    new Animated.Value(24),
    new Animated.Value(24),
    new Animated.Value(24),
    new Animated.Value(24),
  ]).current;

  useEffect(() => {
    // Staggered entrance animation
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
  }, []);

  const handleNavigation = (route: string) => {
    navigation.navigate(route);
  };

  const handleUpdateGoal = (target: number) => {
    setGoalTarget(target);
  };

  const handleUploadSuccess = (uploadData: UploadResponse) => {
    setLastUpload({
      fileName: uploadData.filename,
      uploadedAt: new Date(),
      uploadId: uploadData.upload_id,
    });

    console.log('Upload successful:', uploadData);
    
    // You could also update other parts of the dashboard
    // or navigate to a specific screen for the uploaded resume
  };

  const handleUploadError = (error: string) => {
    console.error('Upload error:', error);
    // Could show a toast notification or update error state
  };

  const getGridItemLayoutStyle = (colSpan: number) => {
    const isMobile = screenWidth <= 768;
    
    if (isMobile) {
      return { width: '100%', marginBottom: designTokens.spacing.gridGap };
    }
    
    // Grid layout for tablet/desktop
    const columnWidth = (screenWidth - 240 - (designTokens.spacing.gridGap * 5)) / 12;
    const width = columnWidth * colSpan + designTokens.spacing.gridGap * (colSpan - 1);
    
    return { width, marginBottom: designTokens.spacing.gridGap };
  };

  const getGridItemAnimationStyle = (index: number) => ({
    opacity: fadeAnims[index],
    transform: [{ translateY: slideAnims[index] }],
  });

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.layout}>
        <SideBar activeRoute="Dashboard" onNavigate={handleNavigation} />
        
        <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
          <View style={styles.header}>
            <Text style={styles.pageTitle}>Dashboard</Text>
            <Text style={styles.pageSubtitle}>
              Track your internship application progress
            </Text>
          </View>

          <View style={[styles.grid, screenWidth <= 768 && styles.gridMobile]}>
            {/* Resume Upload Card - A */}
            <View style={getGridItemLayoutStyle(6)}>
              <Animated.View style={getGridItemAnimationStyle(0)}>
                <ResumeUploadCard
                  lastFileName={lastUpload?.fileName}
                  lastUploadedAt={lastUpload?.uploadedAt}
                  onPress={() => handleNavigation('Resume')}
                  onUploadSuccess={handleUploadSuccess}
                  onUploadError={handleUploadError}
                />
              </Animated.View>
            </View>

            {/* Applications Chart Card - B */}
            <View style={getGridItemLayoutStyle(4)}>
              <Animated.View style={getGridItemAnimationStyle(1)}>
                <ApplicationsChartCard
                  onPress={() => handleNavigation('Applications')}
                />
              </Animated.View>
            </View>

            {/* Weekly Goal Card - C */}
            <View style={getGridItemLayoutStyle(2)}>
              <Animated.View style={getGridItemAnimationStyle(2)}>
                <WeeklyGoalCard
                  goalTarget={goalTarget}
                  currentProgress={currentProgress}
                  onUpdateTarget={handleUpdateGoal}
                  onPress={() => handleNavigation('Goals')}
                />
              </Animated.View>
            </View>

            {/* New Postings Card - D */}
            <View style={getGridItemLayoutStyle(6)}>
              <Animated.View style={getGridItemAnimationStyle(3)}>
                <NewPostingsCard
                  postings={[]} // Uses dummy data from component
                  onPress={() => handleNavigation('Postings')}
                />
              </Animated.View>
            </View>

            {/* News Card - E */}
            <View style={getGridItemLayoutStyle(4)}>
              <Animated.View style={getGridItemAnimationStyle(4)}>
                <NewsCard
                  news={[]} // Uses dummy data from component
                  onPress={() => handleNavigation('News')}
                />
              </Animated.View>
            </View>

            {/* Spacer/Future Widget - F */}
            <View style={getGridItemLayoutStyle(2)}>
              <Animated.View style={getGridItemAnimationStyle(5)}>
                <View style={styles.spacerCard}>
                  <Text style={styles.spacerText}>Future Widget</Text>
                </View>
              </Animated.View>
            </View>
          </View>
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
  spacerCard: {
    backgroundColor: designTokens.colors.bgMuted,
    borderRadius: designTokens.borderRadius.card,
    padding: designTokens.spacing.cardPadding,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 120,
    borderWidth: 2,
    borderColor: designTokens.colors.textSecondary + '20',
    borderStyle: 'dashed',
  },
  spacerText: {
    fontSize: 14,
    color: designTokens.colors.textSecondary,
    fontStyle: 'italic',
  },
}); 