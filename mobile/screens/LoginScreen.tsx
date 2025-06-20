import React, { useState, useRef, useEffect } from 'react';
import { StyleSheet, Text, View, Pressable, TextInput, KeyboardAvoidingView, Platform, Animated, Dimensions, AccessibilityInfo } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { designTokens } from '../theme/tokens';
import { AnimatedBackground } from '../components/shared/AnimatedBackground';
import type { StackNavigationProp } from '@react-navigation/stack';

const { width: screenWidth } = Dimensions.get('window');

export default function LoginScreen({ navigation, route }: { navigation: StackNavigationProp<any, any>, route: any }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loginHovered, setLoginHovered] = useState(false);
  const [motionReduced, setMotionReduced] = useState(false);
  const emailInputRef = useRef<TextInput>(null);
  const slideAnim = useRef(new Animated.Value(screenWidth)).current;

  useEffect(() => {
    // Check for reduced motion preference
    const checkMotionPreference = async () => {
      try {
        const isReducedMotionEnabled = await AccessibilityInfo.isReduceMotionEnabled();
        setMotionReduced(isReducedMotionEnabled);
      } catch (error) {
        setMotionReduced(false);
      }
    };
    
    checkMotionPreference();
  }, []);

  useEffect(() => {
    // Slide in animation when screen loads
    if (route?.params?.from === 'Landing') {
      if (motionReduced) {
        slideAnim.setValue(0);
        // Focus first input after short delay for accessibility
        setTimeout(() => {
          emailInputRef.current?.focus();
        }, 100);
      } else {
        Animated.spring(slideAnim, {
          toValue: 0,
          speed: 12,
          bounciness: 8,
          useNativeDriver: true,
        }).start(() => {
          // Focus first input after animation completes
          emailInputRef.current?.focus();
        });
      }
    } else {
      slideAnim.setValue(0);
      // Focus first input for direct navigation
      setTimeout(() => {
        emailInputRef.current?.focus();
      }, 100);
    }
  }, [route, motionReduced, slideAnim]);

  const handleBack = () => {
    if (motionReduced) {
      navigation.goBack();
    } else {
      // Elastic slide out
      Animated.spring(slideAnim, {
        toValue: screenWidth,
        speed: 12,
        bounciness: 8,
        useNativeDriver: true,
      }).start(() => {
        navigation.goBack();
      });
    }
  };

  const handleLogin = () => {
    navigation.navigate('Dashboard');
  };

  return (
    <AnimatedBackground>
      <Animated.View
        style={[
          styles.animatedContainer,
          {
            transform: [{ translateX: slideAnim }],
          },
        ]}
      >
        <KeyboardAvoidingView
          behavior={Platform.OS === 'ios' ? 'padding' : undefined}
          style={styles.container}
        >
          <View style={styles.loginCard}>
            {/* Header with back button */}
            <View style={styles.header}>
              <Pressable onPress={handleBack} style={styles.backButton}>
                <Ionicons name="arrow-back" size={24} color={designTokens.colors.textSecondary} />
              </Pressable>
            </View>
            
            {/* Logo */}
            <View style={styles.logoContainer}>
              <Text style={styles.logo}>ShipIt</Text>
            </View>
            
            {/* Title */}
            <Text style={styles.title}>Sign in</Text>
            
            {/* Form */}
            <View style={styles.form}>
              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Email</Text>
                <TextInput
                  ref={emailInputRef}
                  style={styles.input}
                  placeholder="Enter your email"
                  placeholderTextColor={designTokens.colors.textSecondary + '80'}
                  value={email}
                  onChangeText={setEmail}
                  autoCapitalize="none"
                  keyboardType="email-address"
                  autoComplete="email"
                  returnKeyType="next"
                  onSubmitEditing={() => {
                    // Focus password field when done with email
                  }}
                />
              </View>
              
              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Password</Text>
                <TextInput
                  style={styles.input}
                  placeholder="Enter your password"
                  placeholderTextColor={designTokens.colors.textSecondary + '80'}
                  value={password}
                  onChangeText={setPassword}
                  secureTextEntry
                  autoComplete="password"
                  returnKeyType="done"
                  onSubmitEditing={handleLogin}
                />
              </View>
              
              <Pressable
                style={[styles.loginButton, loginHovered && styles.loginButtonHovered]}
                onHoverIn={() => setLoginHovered(true)}
                onHoverOut={() => setLoginHovered(false)}
                onPress={handleLogin}
              >
                <Text style={styles.loginButtonText}>Sign In</Text>
              </Pressable>
              
              {/* Forgot password link */}
              <Pressable style={styles.forgotPasswordContainer}>
                <Text style={styles.forgotPasswordText}>Forgot password?</Text>
              </Pressable>
            </View>
          </View>
        </KeyboardAvoidingView>
      </Animated.View>
    </AnimatedBackground>
  );
}

const styles = StyleSheet.create({
  animatedContainer: {
    flex: 1,
  },
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 24,
  },
  loginCard: {
    backgroundColor: designTokens.colors.bgPrimary,
    borderRadius: designTokens.borderRadius.card,
    padding: 32,
    width: '100%',
    maxWidth: 440,
    ...designTokens.shadows.card,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 24,
  },
  backButton: {
    padding: 8,
    marginLeft: -8,
    borderRadius: 6,
  },
  logoContainer: {
    alignItems: 'center',
    marginBottom: 32,
  },
  logo: {
    fontSize: 32,
    fontWeight: '800',
    color: designTokens.colors.accent,
    letterSpacing: 1,
    fontFamily: designTokens.typography.fontFamily,
  },
  title: {
    fontSize: designTokens.typography.h2Size,
    fontWeight: '700',
    color: designTokens.colors.textPrimary,
    marginBottom: 32,
    textAlign: 'center',
    fontFamily: designTokens.typography.fontFamily,
  },
  form: {
    width: '100%',
  },
  inputGroup: {
    marginBottom: 20,
  },
  inputLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: designTokens.colors.textPrimary,
    marginBottom: 8,
    fontFamily: designTokens.typography.fontFamily,
  },
  input: {
    backgroundColor: designTokens.colors.bgMuted,
    borderRadius: 8,
    paddingVertical: 16,
    paddingHorizontal: 16,
    fontSize: 16,
    color: designTokens.colors.textPrimary,
    borderWidth: 1,
    borderColor: designTokens.colors.textSecondary + '20',
    fontFamily: designTokens.typography.fontFamily,
  },
  loginButton: {
    backgroundColor: designTokens.colors.accentSoft,
    paddingVertical: 16,
    paddingHorizontal: 32,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 8,
    marginBottom: 24,
    ...designTokens.shadows.card,
  },
  loginButtonHovered: {
    transform: [{ scale: 1.02 }],
    ...designTokens.shadows.cardHover,
  },
  loginButtonText: {
    color: designTokens.colors.bgPrimary,
    fontSize: 16,
    fontWeight: '600',
    letterSpacing: 0.5,
    fontFamily: designTokens.typography.fontFamily,
  },
  forgotPasswordContainer: {
    alignItems: 'center',
  },
  forgotPasswordText: {
    color: designTokens.colors.accent,
    fontSize: 14,
    fontWeight: '500',
    fontFamily: designTokens.typography.fontFamily,
  },
});
