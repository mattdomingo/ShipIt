import React, { useState, useRef, useEffect } from 'react';
import { StyleSheet, Text, View, Pressable, TextInput, KeyboardAvoidingView, Platform, Animated, Easing, Dimensions } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import type { StackNavigationProp } from '@react-navigation/stack';

const SCREEN_WIDTH = Dimensions.get('window').width;

export default function LoginScreen({ navigation, route }: { navigation: StackNavigationProp<any, any>, route: any }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loginHovered, setLoginHovered] = useState(false);
  const slideAnim = useRef(new Animated.Value(SCREEN_WIDTH)).current;
  const [isSliding, setIsSliding] = useState(false);

  useEffect(() => {
    Animated.timing(slideAnim, {
      toValue: 0,
      duration: 400,
      easing: Easing.out(Easing.cubic),
      useNativeDriver: true,
    }).start();
  }, []);

  const handleBack = () => {
    setIsSliding(true);
    Animated.timing(slideAnim, {
      toValue: SCREEN_WIDTH,
      duration: 400,
      easing: Easing.out(Easing.cubic),
      useNativeDriver: true,
    }).start(() => {
      navigation.goBack();
    });
  };

  return (
    <LinearGradient
      colors={["#0f2027", "#2c5364"]}
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 1 }}
      style={styles.gradientBg}
    >
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}
      >
        <Animated.View style={[styles.container, { transform: [{ translateX: slideAnim }] }]}> 
          <View style={styles.header}>
            <Pressable onPress={handleBack} style={styles.backArrow} disabled={isSliding}>
              <Ionicons name="arrow-back" size={28} color="#2a4d7a" />
            </Pressable>
          </View>
          <Text style={styles.title}>Log In</Text>
          <TextInput
            style={styles.input}
            placeholder="Email"
            placeholderTextColor="#b0b8c1"
            value={email}
            onChangeText={setEmail}
            autoCapitalize="none"
            keyboardType="email-address"
          />
          <TextInput
            style={styles.input}
            placeholder="Password"
            placeholderTextColor="#b0b8c1"
            value={password}
            onChangeText={setPassword}
            secureTextEntry
          />
          <Pressable
            style={[styles.button, loginHovered && styles.buttonHovered]}
            onHoverIn={() => setLoginHovered(true)}
            onHoverOut={() => setLoginHovered(false)}
            onPress={() => navigation.navigate('Dashboard')}
            disabled={isSliding}
          >
            <Text style={styles.buttonText}>Log In</Text>
          </Pressable>
        </Animated.View>
      </KeyboardAvoidingView>
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
    marginBottom: 32,
    fontFamily: 'System',
    textShadowColor: 'rgba(44,83,100,0.25)',
    textShadowOffset: { width: 0, height: 4 },
    textShadowRadius: 12,
  },
  input: {
    width: '100%',
    backgroundColor: 'rgba(255,255,255,0.18)',
    borderRadius: 12,
    paddingVertical: 14,
    paddingHorizontal: 18,
    fontSize: 18,
    color: '#fff',
    marginBottom: 18,
    borderWidth: 1.2,
    borderColor: 'rgba(255,255,255,0.22)',
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
  header: {
    position: 'absolute',
    top: 40,
    left: 20,
    width: '100%',
    flexDirection: 'row',
    alignItems: 'center',
  },
  backArrow: {
    padding: 8,
  },
});
