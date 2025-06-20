import React from 'react';
import { createStackNavigator, CardStyleInterpolators } from '@react-navigation/stack';
import { View, StyleSheet } from 'react-native';
import LandingScreen from '../screens/LandingScreen';
import LoginScreen from '../screens/LoginScreen';
import DashboardScreen from '../screens/DashboardScreen';
import { LinearGradient } from 'expo-linear-gradient';
import { designTokens } from '../theme/tokens';

const Stack = createStackNavigator();

function AppBackground({ children }: { children: React.ReactNode }) {
  return (
    <View style={styles.background}>
      {children}
    </View>
  );
}

function GradientBackground({ children }: { children: React.ReactNode }) {
  return (
    <LinearGradient
      colors={["#0f2027", "#2c5364"]}
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 1 }}
      style={styles.gradientBg}
    >
      {children}
    </LinearGradient>
  );
}

const customCardStyleInterpolator = ({ current, layouts }: any) => {
  const translateX = current.progress.interpolate({
    inputRange: [0, 1],
    outputRange: [layouts.screen.width, 0],
  });
  return {
    cardStyle: {
      transform: [{ translateX }],
    },
  };
};

const LandingWithGradient = (props: any) => (
  <GradientBackground>
    <LandingScreen {...props} />
  </GradientBackground>
);

const LoginWithGradient = (props: any) => (
  <GradientBackground>
    <LoginScreen {...props} />
  </GradientBackground>
);

export default function MainNavigator() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
        cardStyleInterpolator: customCardStyleInterpolator,
        transitionSpec: {
          open: { animation: 'timing', config: { duration: 400 } },
          close: { animation: 'timing', config: { duration: 350 } },
        },
        gestureEnabled: true,
        gestureDirection: 'horizontal',
      }}
    >
      <Stack.Screen 
        name="Landing" 
        component={LandingWithGradient}
      />
      <Stack.Screen 
        name="Login" 
        component={LoginWithGradient}
      />
      <Stack.Screen 
        name="Dashboard" 
        component={DashboardScreen}
        options={{ 
          cardStyle: { backgroundColor: designTokens.colors.bgPrimary }
        }}
      />
    </Stack.Navigator>
  );
}

const styles = StyleSheet.create({
  background: {
    flex: 1,
    backgroundColor: designTokens.colors.bgPrimary,
  },
  gradientBg: {
    flex: 1,
  },
});
