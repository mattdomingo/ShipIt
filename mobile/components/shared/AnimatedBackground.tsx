import React, { useRef, useEffect } from 'react';
import { View, StyleSheet, Animated, Dimensions, AccessibilityInfo } from 'react-native';
import Svg, { Defs, Pattern, Path, Rect } from 'react-native-svg';
import { designTokens } from '../../theme/tokens';

const { width: screenWidth, height: screenHeight } = Dimensions.get('window');

interface AnimatedBackgroundProps {
  children: React.ReactNode;
}

export const AnimatedBackground: React.FC<AnimatedBackgroundProps> = ({ children }) => {
  const translateX = useRef(new Animated.Value(0)).current;
  const translateY = useRef(new Animated.Value(0)).current;
  const [motionReduced, setMotionReduced] = React.useState(false);

  useEffect(() => {
    // Check for reduced motion preference
    const checkMotionPreference = async () => {
      try {
        const isReducedMotionEnabled = await AccessibilityInfo.isReduceMotionEnabled();
        setMotionReduced(isReducedMotionEnabled);
      } catch (error) {
        // Fallback: assume motion is allowed
        setMotionReduced(false);
      }
    };
    
    checkMotionPreference();
  }, []);

  useEffect(() => {
    if (motionReduced) return;

    // Slow, continuous drift animation
    const animateBackground = () => {
      Animated.loop(
        Animated.parallel([
          Animated.timing(translateX, {
            toValue: 100,
            duration: 15000,
            useNativeDriver: true,
          }),
          Animated.timing(translateY, {
            toValue: 50,
            duration: 12000,
            useNativeDriver: true,
          }),
        ])
      ).start();
    };

    animateBackground();
  }, [motionReduced, translateX, translateY]);

  const createZigZagPath = () => {
    const zigWidth = 40;
    const zigHeight = 20;
    const patternWidth = zigWidth * 2;
    const patternHeight = zigHeight * 2;
    
    return `M 0,${zigHeight} L ${zigWidth},0 L ${patternWidth},${zigHeight} L ${zigWidth},${patternHeight} Z`;
  };

  return (
    <View style={styles.container}>
      {/* Base background */}
      <View style={styles.baseBackground} />
      
      {/* Animated geometric pattern - fixed during transitions */}
      <View style={styles.patternContainerFixed}>
        <Animated.View 
          style={[
            styles.patternContainer,
            !motionReduced && {
              transform: [
                { translateX },
                { translateY },
              ],
            },
          ]}
        >
          <Svg
            width={screenWidth + 200}
            height={screenHeight + 200}
            style={styles.svgPattern}
          >
            <Defs>
              <Pattern
                id="zigzag1"
                patternUnits="userSpaceOnUse"
                width="80"
                height="40"
              >
                <Path
                  d={createZigZagPath()}
                  fill={designTokens.colors.accent + '0C'}
                  stroke={designTokens.colors.accent + '18'}
                  strokeWidth="0.5"
                />
              </Pattern>
              
              <Pattern
                id="zigzag2"
                patternUnits="userSpaceOnUse"
                width="60"
                height="30"
              >
                <Path
                  d="M 0,15 L 30,0 L 60,15 L 30,30 Z"
                  fill={designTokens.colors.accent + '08'}
                  stroke={designTokens.colors.accent + '14'}
                  strokeWidth="0.5"
                />
              </Pattern>
            </Defs>
            
            <Rect
              width="100%"
              height="100%"
              fill="url(#zigzag1)"
            />
            
            <Rect
              width="100%"
              height="100%"
              fill="url(#zigzag2)"
              transform="translate(40, 20)"
            />
          </Svg>
        </Animated.View>
      </View>
      
      {/* Content overlay */}
      <View style={styles.contentContainer}>
        {children}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    position: 'relative',
  },
  baseBackground: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: designTokens.colors.bgMuted,
  },
  patternContainerFixed: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    overflow: 'hidden',
  },
  patternContainer: {
    position: 'absolute',
    top: -100,
    left: -100,
    width: screenWidth + 200,
    height: screenHeight + 200,
  },
  svgPattern: {
    width: '100%',
    height: '100%',
  },
  contentContainer: {
    flex: 1,
    zIndex: 1,
  },
}); 