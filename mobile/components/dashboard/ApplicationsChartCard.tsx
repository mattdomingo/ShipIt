import React, { useState } from 'react';
import { View, Text, StyleSheet, Pressable } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Card } from '../shared/Card';
import { designTokens } from '../../theme/tokens';

interface ApplicationsChartCardProps {
  onPress: () => void;
}

type TimeRange = 'week' | 'month' | 'quarter' | 'custom';

// Dummy data for the chart
const chartData = {
  week: [2, 4, 1, 6, 3, 8, 5],
  month: [15, 20, 18, 25, 22, 30, 28],
  quarter: [60, 75, 85, 70, 90, 95, 80],
  custom: [10, 15, 12, 20, 18, 25, 22],
};

export const ApplicationsChartCard: React.FC<ApplicationsChartCardProps> = ({ onPress }) => {
  const [selectedRange, setSelectedRange] = useState<TimeRange>('week');
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const ranges = [
    { key: 'week' as TimeRange, label: 'This Week' },
    { key: 'month' as TimeRange, label: 'Last 4 Weeks' },
    { key: 'quarter' as TimeRange, label: 'Quarter' },
    { key: 'custom' as TimeRange, label: 'Custom' },
  ];

  const currentData = chartData[selectedRange];
  const maxValue = Math.max(...currentData);
  const totalApps = currentData.reduce((sum, val) => sum + val, 0);

  const renderMiniChart = () => {
    return (
      <View style={styles.chartContainer}>
        <View style={styles.chart}>
          {currentData.map((value, index) => {
            const height = (value / maxValue) * 40;
            return (
              <View key={index} style={styles.chartBarContainer}>
                <View 
                  style={[
                    styles.chartBar, 
                    { height: height || 2 }
                  ]} 
                />
              </View>
            );
          })}
        </View>
        
        {currentData.length === 0 && (
          <View style={styles.emptyState}>
            <Ionicons name="bar-chart-outline" size={32} color={designTokens.colors.textSecondary} />
            <Text style={styles.emptyText}>No data yet</Text>
          </View>
        )}
      </View>
    );
  };

  return (
    <Card onPress={onPress}>
      <View style={styles.header}>
        <View>
          <Text style={styles.title}>Applications</Text>
          <Text style={styles.subtitle}>Apps per day</Text>
        </View>
        
        <View style={styles.dropdownContainer}>
          <Pressable 
            style={styles.dropdown}
            onPress={() => setDropdownOpen(!dropdownOpen)}
          >
            <Text style={styles.dropdownText}>
              {ranges.find(r => r.key === selectedRange)?.label}
            </Text>
            <Ionicons 
              name={dropdownOpen ? "chevron-up" : "chevron-down"} 
              size={16} 
              color={designTokens.colors.textSecondary} 
            />
          </Pressable>
          
          {dropdownOpen && (
            <View style={styles.dropdownMenu}>
              {ranges.map((range) => (
                <Pressable
                  key={range.key}
                  style={[
                    styles.dropdownItem,
                    selectedRange === range.key && styles.dropdownItemActive
                  ]}
                  onPress={() => {
                    setSelectedRange(range.key);
                    setDropdownOpen(false);
                  }}
                >
                  <Text style={[
                    styles.dropdownItemText,
                    selectedRange === range.key && styles.dropdownItemTextActive
                  ]}>
                    {range.label}
                  </Text>
                </Pressable>
              ))}
            </View>
          )}
        </View>
      </View>
      
      <View style={styles.statsContainer}>
        <Text style={styles.totalNumber}>{totalApps}</Text>
        <Text style={styles.totalLabel}>Total Applications</Text>
      </View>
      
      {renderMiniChart()}
    </Card>
  );
};

const styles = StyleSheet.create({
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 16,
  },
  title: {
    fontSize: 18,
    fontWeight: '600',
    color: designTokens.colors.textPrimary,
    marginBottom: 2,
  },
  subtitle: {
    fontSize: 14,
    color: designTokens.colors.textSecondary,
  },
  dropdownContainer: {
    position: 'relative',
    zIndex: 1000,
  },
  dropdown: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 8,
    backgroundColor: designTokens.colors.bgPrimary,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: designTokens.colors.textSecondary + '30',
  },
  dropdownText: {
    fontSize: 14,
    color: designTokens.colors.textPrimary,
    marginRight: 6,
  },
  dropdownMenu: {
    position: 'absolute',
    top: '100%',
    right: 0,
    backgroundColor: designTokens.colors.bgPrimary,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: designTokens.colors.textSecondary + '30',
    ...designTokens.shadows.card,
    minWidth: 120,
  },
  dropdownItem: {
    paddingHorizontal: 12,
    paddingVertical: 10,
  },
  dropdownItemActive: {
    backgroundColor: designTokens.colors.accent + '20',
  },
  dropdownItemText: {
    fontSize: 14,
    color: designTokens.colors.textPrimary,
  },
  dropdownItemTextActive: {
    color: designTokens.colors.accent,
    fontWeight: '600',
  },
  statsContainer: {
    alignItems: 'center',
    marginBottom: 20,
  },
  totalNumber: {
    fontSize: 28,
    fontWeight: 'bold',
    color: designTokens.colors.textPrimary,
  },
  totalLabel: {
    fontSize: 12,
    color: designTokens.colors.textSecondary,
    marginTop: 2,
  },
  chartContainer: {
    height: 60,
    marginTop: 8,
  },
  chart: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    height: 50,
    paddingHorizontal: 4,
  },
  chartBarContainer: {
    flex: 1,
    alignItems: 'center',
    marginHorizontal: 1,
  },
  chartBar: {
    backgroundColor: designTokens.colors.accent,
    width: 8,
    borderRadius: 2,
    minHeight: 2,
  },
  emptyState: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  emptyText: {
    fontSize: 14,
    color: designTokens.colors.textSecondary,
    marginTop: 8,
  },
}); 