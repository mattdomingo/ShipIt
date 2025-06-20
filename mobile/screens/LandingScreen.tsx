import React, { useState, useRef } from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View, Pressable, Dimensions, ScrollView, Animated } from 'react-native';
import { designTokens } from '../theme/tokens';
import { AnimatedBackground } from '../components/shared/AnimatedBackground';
import type { StackNavigationProp } from '@react-navigation/stack';

const { width: screenWidth } = Dimensions.get('window');

type LandingScreenNavigationProp = StackNavigationProp<any, any>;

export default function LandingScreen({ navigation }: { navigation: LandingScreenNavigationProp }) {
  const [loginHovered, setLoginHovered] = useState(false);
  const [aboutHovered, setAboutHovered] = useState(false);
  const scrollViewRef = useRef<ScrollView>(null);
  const slideAnim = useRef(new Animated.Value(0)).current;

  const handleLoginPress = () => {
    // Elastic slide transition
    Animated.spring(slideAnim, {
      toValue: -screenWidth,
      speed: 12,
      bounciness: 8,
      useNativeDriver: true,
    }).start(() => {
      navigation.navigate('Login', { from: 'Landing' });
      // Reset animation for return
      slideAnim.setValue(0);
    });
  };

  const handleLearnMorePress = () => {
    scrollViewRef.current?.scrollTo({
      y: 600, // Approximate position of About section
      animated: true,
    });
  };

  const isTablet = screenWidth > 768;

  return (
    <AnimatedBackground>
      <Animated.View 
        style={[
          styles.container,
          {
            transform: [{ translateX: slideAnim }],
          },
        ]}
      >
        <StatusBar style="dark" />
        
        <ScrollView 
          ref={scrollViewRef}
          style={styles.scrollView}
          showsVerticalScrollIndicator={false}
        >
          {/* Hero Section */}
          <View style={[styles.heroSection, isTablet && styles.heroSectionTablet]}>
            <View style={styles.heroContent}>
              <Text style={styles.logo}>ShipIt</Text>
              <Text style={styles.headline}>
                Your home for the{'\n'}internship hunt
              </Text>
              <Text style={styles.subheadline}>
                Track applications, discover opportunities, and land your dream internship with our comprehensive platform designed for ambitious students.
              </Text>
              
              <View style={styles.ctaContainer}>
                <Pressable
                  style={[styles.primaryButton, loginHovered && styles.buttonHovered]}
                  onHoverIn={() => setLoginHovered(true)}
                  onHoverOut={() => setLoginHovered(false)}
                  onPress={handleLoginPress}
                >
                  <Text style={styles.primaryButtonText}>Log In</Text>
                </Pressable>
                
                <Pressable
                  style={[styles.secondaryButton, aboutHovered && styles.secondaryButtonHovered]}
                  onHoverIn={() => setAboutHovered(true)}
                  onHoverOut={() => setAboutHovered(false)}
                  onPress={handleLearnMorePress}
                >
                  <Text style={styles.secondaryButtonText}>Learn More</Text>
                </Pressable>
              </View>
            </View>
          </View>
          
          {/* About Section */}
          <View style={styles.aboutSection}>
            <View style={[styles.aboutContent, isTablet && styles.aboutContentTablet]}>
              {/* Left Column - Text */}
              <View style={[styles.aboutTextColumn, isTablet && styles.aboutTextColumnTablet]}>
                <Text style={styles.aboutTitle}>About Me</Text>
                <Text style={styles.aboutText}>
                  Matthew Domingo – Computer Science major at UW-Madison with minors in Economics & Mathematics. Former TruStage intern with interests in software, data, UX, and high-quality product design.
                </Text>
                
                <Text style={styles.aboutTitle}>About ShipIt</Text>
                <Text style={styles.aboutText}>
                  ShipIt is a sleek platform that lets ambitious students track internship applications, set weekly 'apply-to-X' goals, and surface new opportunities – all in one modern dashboard.
                </Text>
              </View>
              
              {/* Right Column - Illustration */}
              <View style={[styles.aboutIllustrationColumn, isTablet && styles.aboutIllustrationColumnTablet]}>
                <View style={styles.mockupContainer}>
                  <View style={styles.mockupCard}>
                    <View style={styles.mockupHeader}>
                      <View style={styles.mockupDot} />
                      <View style={styles.mockupDot} />
                      <View style={styles.mockupDot} />
                    </View>
                    <View style={styles.mockupContent}>
                      <View style={styles.mockupBar} />
                      <View style={[styles.mockupBar, styles.mockupBarShort]} />
                      <View style={[styles.mockupBar, styles.mockupBarMedium]} />
                    </View>
                  </View>
                  
                  <View style={[styles.mockupCard, styles.mockupCardSmall]}>
                    <View style={styles.mockupCircle} />
                    <View style={styles.mockupTextLine} />
                    <View style={[styles.mockupTextLine, styles.mockupTextLineShort]} />
                  </View>
                </View>
              </View>
            </View>
          </View>
        </ScrollView>
      </Animated.View>
    </AnimatedBackground>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollView: {
    flex: 1,
  },
  heroSection: {
    minHeight: 600,
    paddingHorizontal: 24,
    paddingTop: 60,
    paddingBottom: 40,
    justifyContent: 'center',
  },
  heroSectionTablet: {
    paddingHorizontal: 48,
    maxWidth: 1200,
    alignSelf: 'center',
    width: '100%',
  },
  heroContent: {
    alignItems: 'flex-start',
  },
  logo: {
    fontSize: 24,
    fontWeight: '800',
    color: designTokens.colors.accent,
    letterSpacing: 1,
    marginBottom: 32,
    fontFamily: designTokens.typography.fontFamily,
  },
  headline: {
    fontSize: designTokens.typography.h1Size,
    fontWeight: '800',
    color: designTokens.colors.textPrimary,
    lineHeight: 40,
    marginBottom: 16,
    fontFamily: designTokens.typography.fontFamily,
  },
  subheadline: {
    fontSize: 18,
    color: designTokens.colors.textSecondary,
    lineHeight: 28,
    marginBottom: 40,
    fontFamily: designTokens.typography.fontFamily,
    maxWidth: 480,
  },
  ctaContainer: {
    flexDirection: 'row',
    gap: 16,
    flexWrap: 'wrap',
  },
  primaryButton: {
    backgroundColor: designTokens.colors.accentSoft,
    paddingVertical: 16,
    paddingHorizontal: 32,
    borderRadius: 8,
    minWidth: 140,
    alignItems: 'center',
    ...designTokens.shadows.card,
  },
  secondaryButton: {
    backgroundColor: 'transparent',
    paddingVertical: 16,
    paddingHorizontal: 32,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: designTokens.colors.textSecondary + '40',
    minWidth: 140,
    alignItems: 'center',
  },
  buttonHovered: {
    transform: [{ scale: 1.02 }],
    ...designTokens.shadows.cardHover,
  },
  secondaryButtonHovered: {
    backgroundColor: designTokens.colors.textPrimary + '05',
    borderColor: designTokens.colors.textPrimary + '60',
  },
  primaryButtonText: {
    color: designTokens.colors.bgPrimary,
    fontSize: 16,
    fontWeight: '600',
    letterSpacing: 0.5,
  },
  secondaryButtonText: {
    color: designTokens.colors.textPrimary,
    fontSize: 16,
    fontWeight: '600',
    letterSpacing: 0.5,
  },
  aboutSection: {
    paddingHorizontal: 24,
    paddingVertical: 60,
    backgroundColor: designTokens.colors.bgPrimary + '20',
  },
  aboutContent: {
    maxWidth: 1200,
    alignSelf: 'center',
    width: '100%',
  },
  aboutContentTablet: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 48,
  },
  aboutTextColumn: {
    flex: 1,
  },
  aboutTextColumnTablet: {
    flex: 1,
  },
  aboutIllustrationColumn: {
    marginTop: 40,
  },
  aboutIllustrationColumnTablet: {
    flex: 1,
    marginTop: 0,
  },
  aboutTitle: {
    fontSize: designTokens.typography.h2Size,
    fontWeight: '700',
    color: designTokens.colors.textPrimary,
    marginBottom: 16,
    marginTop: 32,
    fontFamily: designTokens.typography.fontFamily,
  },
  aboutText: {
    fontSize: 16,
    color: designTokens.colors.textSecondary,
    lineHeight: 24,
    fontFamily: designTokens.typography.fontFamily,
  },
  mockupContainer: {
    alignItems: 'center',
    gap: 24,
  },
  mockupCard: {
    backgroundColor: designTokens.colors.bgPrimary,
    borderRadius: 12,
    padding: 20,
    width: 240,
    ...designTokens.shadows.card,
  },
  mockupCardSmall: {
    width: 180,
    padding: 16,
  },
  mockupHeader: {
    flexDirection: 'row',
    gap: 6,
    marginBottom: 16,
  },
  mockupDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: designTokens.colors.textSecondary + '30',
  },
  mockupContent: {
    gap: 12,
  },
  mockupBar: {
    height: 8,
    backgroundColor: designTokens.colors.accent + '40',
    borderRadius: 4,
  },
  mockupBarShort: {
    width: '60%',
  },
  mockupBarMedium: {
    width: '80%',
  },
  mockupCircle: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: designTokens.colors.accentSoft,
    marginBottom: 12,
  },
  mockupTextLine: {
    height: 6,
    backgroundColor: designTokens.colors.textSecondary + '20',
    borderRadius: 3,
    marginBottom: 8,
  },
  mockupTextLineShort: {
    width: '70%',
  },
});
