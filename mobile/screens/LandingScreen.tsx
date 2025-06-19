import React, { useState, useRef, useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View, Pressable, Animated, Easing, Dimensions } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import type { StackNavigationProp } from '@react-navigation/stack';

const SCREEN_WIDTH = Dimensions.get('window').width;

type LandingScreenNavigationProp = StackNavigationProp<any, any>;

export default function LandingScreen({ navigation }: { navigation: LandingScreenNavigationProp }) {
  const [loginHovered, setLoginHovered] = useState(false);
  const [aboutHovered, setAboutHovered] = useState(false);
  const slideAnim = useRef(new Animated.Value(0)).current;
  const [isSliding, setIsSliding] = useState(false);

  useEffect(() => {
    const unsubscribe = navigation.addListener('focus', () => {
      slideAnim.setValue(0);
      setIsSliding(false);
    });
    return unsubscribe;
  }, [navigation, slideAnim]);

  const handleLoginPress = () => {
    setIsSliding(true);
    Animated.timing(slideAnim, {
      toValue: -SCREEN_WIDTH,
      duration: 400,
      easing: Easing.out(Easing.cubic),
      useNativeDriver: true,
    }).start(() => {
      navigation.navigate('Login', { from: 'Landing' });
    });
  };

  return (
    <LinearGradient
      colors={["#0f2027", "#2c5364"]}
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 1 }}
      style={styles.gradientBg}
    >
      <Animated.View style={[styles.container, { transform: [{ translateX: slideAnim }] }]}> 
        <Text style={styles.title}>ShipIt</Text>
        <Text style={styles.subtitle}>Your home for the internship hunt</Text>
        <View style={styles.buttonContainer}>
          <Pressable
            style={[styles.button, loginHovered && styles.buttonHovered]}
            onHoverIn={() => setLoginHovered(true)}
            onHoverOut={() => setLoginHovered(false)}
            onPress={handleLoginPress}
            disabled={isSliding}
          >
            <Text style={styles.buttonText}>Log In</Text>
          </Pressable>
          <Pressable
            style={[styles.button, aboutHovered && styles.buttonHovered]}
            onHoverIn={() => setAboutHovered(true)}
            onHoverOut={() => setAboutHovered(false)}
            disabled={isSliding}
          >
            <Text style={styles.buttonText}>About</Text>
          </Pressable>
        </View>
        <StatusBar style="light" />
      </Animated.View>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  gradientBg: {
    flex: 1,
    minHeight: '100%',
    minWidth: '100%',
    justifyContent: 'center',
    alignItems: 'center',
  },
  container: {
    backgroundColor: 'rgba(255,255,255,0.08)',
    borderRadius: 32,
    padding: 48,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 12 },
    shadowOpacity: 0.18,
    shadowRadius: 24,
    elevation: 8,
    minWidth: 340,
    maxWidth: 400,
  },
  title: {
    fontSize: 54,
    fontWeight: '800',
    color: '#fff',
    letterSpacing: 2,
    marginBottom: 12,
    fontFamily: 'System',
    textShadowColor: 'rgba(44,83,100,0.25)',
    textShadowOffset: { width: 0, height: 4 },
    textShadowRadius: 12,
  },
  subtitle: {
    fontSize: 18,
    color: '#e0e0e0',
    marginBottom: 40,
    fontWeight: '400',
    letterSpacing: 1,
    textAlign: 'center',
  },
  buttonContainer: {
    width: '100%',
    alignItems: 'center',
    gap: 20,
    marginBottom: 10,
  },
  button: {
    backgroundColor: 'rgba(255,255,255,0.12)',
    paddingVertical: 16,
    paddingHorizontal: 64,
    borderRadius: 16,
    marginVertical: 10,
    minWidth: 220,
    alignItems: 'center',
    borderWidth: 1.5,
    borderColor: 'rgba(255,255,255,0.18)',
    shadowColor: '#fff',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 8,
  },
  buttonHovered: {
    backgroundColor: 'rgba(255,255,255,0.22)',
    transform: [{ scale: 1.05 }],
    shadowOpacity: 0.18,
    borderColor: '#fff',
  },
  buttonText: {
    color: '#fff',
    fontSize: 20,
    fontWeight: '700',
    letterSpacing: 1,
    textShadowColor: 'rgba(44,83,100,0.18)',
    textShadowOffset: { width: 0, height: 2 },
    textShadowRadius: 6,
  },
});
