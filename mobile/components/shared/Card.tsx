import React, { useRef } from 'react';
import { View, StyleSheet, Animated, Pressable } from 'react-native';
import { designTokens } from '../../theme/tokens';

interface CardProps {
  children: React.ReactNode;
  onPress?: () => void;
  style?: any;
  animated?: boolean;
}

export const Card: React.FC<CardProps> = ({ 
  children, 
  onPress, 
  style, 
  animated = true 
}) => {
  const scaleAnim = useRef(new Animated.Value(1)).current;
  const elevationAnim = useRef(new Animated.Value(0)).current;

  const handlePressIn = () => {
    if (!animated) return;
    Animated.parallel([
      Animated.spring(scaleAnim, {
        toValue: 1.02,
        useNativeDriver: true,
        ...designTokens.animation.spring,
      }),
      Animated.spring(elevationAnim, {
        toValue: 1,
        useNativeDriver: false,
      }),
    ]).start();
  };

  const handlePressOut = () => {
    if (!animated) return;
    Animated.parallel([
      Animated.spring(scaleAnim, {
        toValue: 1,
        useNativeDriver: true,
        ...designTokens.animation.spring,
      }),
      Animated.spring(elevationAnim, {
        toValue: 0,
        useNativeDriver: false,
      }),
    ]).start();
  };

  const animatedStyle = {
    transform: [{ scale: scaleAnim }],
    shadowOffset: {
      width: 0,
      height: elevationAnim.interpolate({
        inputRange: [0, 1],
        outputRange: [2, 6],
      }),
    },
    shadowOpacity: elevationAnim.interpolate({
      inputRange: [0, 1],
      outputRange: [0.1, 0.15],
    }),
    shadowRadius: elevationAnim.interpolate({
      inputRange: [0, 1],
      outputRange: [8, 12],
    }),
    elevation: elevationAnim.interpolate({
      inputRange: [0, 1],
      outputRange: [3, 8],
    }),
  };

  if (onPress) {
    return (
      <Pressable
        onPressIn={handlePressIn}
        onPressOut={handlePressOut}
        onPress={onPress}
        style={[styles.pressable]}
      >
        <Animated.View style={[styles.card, animatedStyle, style]}>
          {children}
        </Animated.View>
      </Pressable>
    );
  }

  return (
    <Animated.View style={[styles.card, animated && animatedStyle, style]}>
      {children}
    </Animated.View>
  );
};

const styles = StyleSheet.create({
  pressable: {
    borderRadius: designTokens.borderRadius.card,
  },
  card: {
    backgroundColor: designTokens.colors.bgMuted,
    borderRadius: designTokens.borderRadius.card,
    padding: designTokens.spacing.cardPadding,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
}); 