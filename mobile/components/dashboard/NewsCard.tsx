import React, { useRef, useEffect, useState } from 'react';
import { View, Text, StyleSheet, Animated, Pressable } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Card } from '../shared/Card';
import { designTokens } from '../../theme/tokens';

interface NewsItem {
  id: string;
  headline: string;
  source: string;
  time: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  snippet?: string;
}

interface NewsCardProps {
  news: NewsItem[];
  onPress: () => void;
}

// Dummy news data
const dummyNews: NewsItem[] = [
  {
    id: '1',
    headline: 'Tech hiring surges 25% in Q1 2024',
    source: 'TechCrunch',
    time: '2h',
    sentiment: 'positive',
    snippet: 'Major tech companies increase internship programs...',
  },
  {
    id: '2',
    headline: 'New AI tools transforming recruitment',
    source: 'Forbes',
    time: '4h',
    sentiment: 'positive',
    snippet: 'Machine learning algorithms helping match candidates...',
  },
  {
    id: '3',
    headline: 'Remote work policies affecting intern programs',
    source: 'Business Insider',
    time: '6h',
    sentiment: 'neutral',
    snippet: 'Companies adapting to hybrid work models...',
  },
  {
    id: '4',
    headline: 'Skills gap widens in tech industry',
    source: 'Wall Street Journal',
    time: '8h',
    sentiment: 'negative',
    snippet: 'Employers struggling to find qualified candidates...',
  },
  {
    id: '5',
    headline: 'Startup funding reaches new heights',
    source: 'VentureBeat',
    time: '12h',
    sentiment: 'positive',
    snippet: 'Record-breaking quarter for venture capital...',
  },
];

const NewsItemComponent: React.FC<{ 
  item: NewsItem; 
  isHovered: boolean; 
  onHover: (hovered: boolean) => void;
}> = ({ item, isHovered, onHover }) => {
  const getSentimentIcon = (sentiment: string) => {
    switch (sentiment) {
      case 'positive':
        return { name: 'trending-up' as const, color: designTokens.colors.accentSoft };
      case 'negative':
        return { name: 'trending-down' as const, color: designTokens.colors.highlight };
      default:
        return { name: 'remove' as const, color: designTokens.colors.textSecondary };
    }
  };

  const sentimentIcon = getSentimentIcon(item.sentiment);

  return (
    <Pressable
      style={styles.newsItem}
      onPressIn={() => onHover(true)}
      onPressOut={() => onHover(false)}
    >
      <View style={styles.newsHeader}>
        <Ionicons 
          name={sentimentIcon.name} 
          size={16} 
          color={sentimentIcon.color} 
        />
        <View style={styles.newsMeta}>
          <Text style={styles.newsSource}>{item.source}</Text>
          <Text style={styles.newsTime}>• {item.time}</Text>
        </View>
      </View>
      
      <Text style={styles.newsHeadline} numberOfLines={isHovered ? undefined : 2}>
        {item.headline}
      </Text>
      
      {isHovered && item.snippet && (
        <Text style={styles.newsSnippet}>
          {item.snippet}
        </Text>
      )}
    </Pressable>
  );
};

export const NewsCard: React.FC<NewsCardProps> = ({ 
  news = dummyNews, 
  onPress 
}) => {
  const scrollAnim = useRef(new Animated.Value(0)).current;
  const [isPaused, setIsPaused] = useState(false);
  const [hoveredItem, setHoveredItem] = useState<string | null>(null);

  useEffect(() => {
    if (!isPaused && news.length > 3) {
      const animation = Animated.loop(
        Animated.timing(scrollAnim, {
          toValue: -news.length * 80, // Approximate height per item
          duration: news.length * 3000, // 3 seconds per item
          useNativeDriver: true,
        }),
        { iterations: -1 }
      );
      
      animation.start();
      
      return () => animation.stop();
    }
  }, [isPaused, news.length, scrollAnim]);

  const handleItemHover = (itemId: string, hovered: boolean) => {
    setHoveredItem(hovered ? itemId : null);
    setIsPaused(hovered);
  };

  return (
    <Card onPress={onPress}>
      <View style={styles.header}>
        <View style={styles.titleContainer}>
          <Ionicons name="newspaper-outline" size={20} color={designTokens.colors.accent} />
          <Text style={styles.title}>Industry News</Text>
        </View>
        
        <View style={styles.statusIndicator}>
          {isPaused ? (
            <Ionicons name="pause" size={12} color={designTokens.colors.textSecondary} />
          ) : (
            <View style={styles.liveDot} />
          )}
        </View>
      </View>

      <View style={styles.newsContainer}>
        <Animated.View 
          style={[
            styles.scrollingContent,
            { transform: [{ translateY: scrollAnim }] }
          ]}
        >
          {news.map((item) => (
            <NewsItemComponent
              key={item.id}
              item={item}
              isHovered={hoveredItem === item.id}
              onHover={(hovered) => handleItemHover(item.id, hovered)}
            />
          ))}
          
          {/* Duplicate items for seamless loop */}
          {news.map((item) => (
            <NewsItemComponent
              key={`${item.id}-duplicate`}
              item={item}
              isHovered={hoveredItem === `${item.id}-duplicate`}
              onHover={(hovered) => handleItemHover(`${item.id}-duplicate`, hovered)}
            />
          ))}
        </Animated.View>
      </View>
    </Card>
  );
};

const styles = StyleSheet.create({
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  titleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  title: {
    fontSize: 18,
    fontWeight: '600',
    color: designTokens.colors.textPrimary,
    marginLeft: 8,
  },
  statusIndicator: {
    width: 20,
    height: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  liveDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: designTokens.colors.accentSoft,
  },
  newsContainer: {
    height: 240,
    overflow: 'hidden',
  },
  scrollingContent: {
    paddingBottom: 240, // Add padding to ensure smooth looping
  },
  newsItem: {
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: designTokens.colors.textSecondary + '20',
    minHeight: 80,
  },
  newsHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 6,
  },
  newsMeta: {
    flexDirection: 'row',
    marginLeft: 8,
    flex: 1,
  },
  newsSource: {
    fontSize: 12,
    fontWeight: '600',
    color: designTokens.colors.textSecondary,
  },
  newsTime: {
    fontSize: 12,
    color: designTokens.colors.textSecondary,
    marginLeft: 4,
  },
  newsHeadline: {
    fontSize: 14,
    fontWeight: '500',
    color: designTokens.colors.textPrimary,
    lineHeight: 20,
    marginBottom: 4,
  },
  newsSnippet: {
    fontSize: 12,
    color: designTokens.colors.textSecondary,
    lineHeight: 16,
    marginTop: 4,
  },
}); 