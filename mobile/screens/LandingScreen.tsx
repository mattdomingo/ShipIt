import React, { useState, useRef } from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View, Pressable, Dimensions, Animated } from 'react-native';
import { designTokens } from '../theme/tokens';
import { AnimatedBackground } from '../components/shared/AnimatedBackground';
import type { StackNavigationProp } from '@react-navigation/stack';

const { width: screenWidth } = Dimensions.get('window');

type LandingScreenNavigationProp = StackNavigationProp<any, any>;

export default function LandingScreen({ navigation }: { navigation: LandingScreenNavigationProp }) {
  const [loginHovered, setLoginHovered] = useState(false);
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
                <Text style={styles.primaryButtonText}>Get Started</Text>
              </Pressable>
            </View>
          </View>
        </View>
      </Animated.View>
    </AnimatedBackground>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  heroSection: {
    flex: 1,
    paddingHorizontal: 32,
    paddingVertical: 80,
    justifyContent: 'center',
    alignItems: 'center',
    maxWidth: 800,
    width: '100%',
  },
  heroSectionTablet: {
    paddingHorizontal: 64,
    maxWidth: 1000,
  },
  heroContent: {
    alignItems: 'center',
    textAlign: 'center',
  },
  logo: {
    fontSize: 36,
    fontWeight: '800',
    color: designTokens.colors.accent,
    letterSpacing: 1.5,
    marginBottom: 48,
    fontFamily: designTokens.typography.fontFamily,
  },
  headline: {
    fontSize: 48,
    fontWeight: '800',
    color: designTokens.colors.textPrimary,
    lineHeight: 56,
    marginBottom: 24,
    fontFamily: designTokens.typography.fontFamily,
    textAlign: 'center',
  },
  subheadline: {
    fontSize: 22,
    color: designTokens.colors.textSecondary,
    lineHeight: 32,
    marginBottom: 56,
    fontFamily: designTokens.typography.fontFamily,
    textAlign: 'center',
    maxWidth: 600,
  },
  ctaContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 20,
    flexWrap: 'wrap',
  },
  primaryButton: {
    backgroundColor: designTokens.colors.accentSoft,
    paddingVertical: 20,
    paddingHorizontal: 48,
    borderRadius: 12,
    minWidth: 200,
    alignItems: 'center',
    ...designTokens.shadows.card,
  },
  buttonHovered: {
    transform: [{ scale: 1.05 }],
    ...designTokens.shadows.cardHover,
  },
  primaryButtonText: {
    color: designTokens.colors.bgPrimary,
    fontSize: 18,
    fontWeight: '700',
    letterSpacing: 0.5,
  },
});
