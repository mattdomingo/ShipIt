import React from 'react';
import { createStackNavigator, CardStyleInterpolators } from '@react-navigation/stack';
import { View, StyleSheet } from 'react-native';
import LandingScreen from '../screens/LandingScreen';
import LoginScreen from '../screens/LoginScreen';
import FavoritesScreen from '../screens/FavoritesScreen';
import { LinearGradient } from 'expo-linear-gradient';

const Stack = createStackNavigator();

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

export default function MainNavigator() {
  return (
    <GradientBackground>
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
          cardStyle: { backgroundColor: 'transparent' },
        }}
      >
        <Stack.Screen name="Landing" component={LandingScreen} />
        <Stack.Screen name="Login" component={LoginScreen} />
        <Stack.Screen name="Favorites" component={FavoritesScreen} />
        <Stack.Screen name="Dashboard" component={() => null} />
      </Stack.Navigator>
    </GradientBackground>
  );
}

const styles = StyleSheet.create({
  gradientBg: {
    flex: 1,
  },
});
