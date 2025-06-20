import React, { useState } from 'react';
import { View, Text, StyleSheet, TextInput, Pressable } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Card } from '../shared/Card';
import { designTokens } from '../../theme/tokens';

interface WeeklyGoalCardProps {
  goalTarget: number;
  currentProgress: number;
  onUpdateTarget: (target: number) => void;
  onPress: () => void;
}

export const WeeklyGoalCard: React.FC<WeeklyGoalCardProps> = ({
  goalTarget,
  currentProgress,
  onUpdateTarget,
  onPress,
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(goalTarget.toString());

  const progressPercentage = Math.min((currentProgress / goalTarget) * 100, 100);

  const handleSaveTarget = () => {
    const newTarget = parseInt(editValue, 10);
    if (!isNaN(newTarget) && newTarget > 0) {
      onUpdateTarget(newTarget);
    } else {
      setEditValue(goalTarget.toString());
    }
    setIsEditing(false);
  };

  const handleCancelEdit = () => {
    setEditValue(goalTarget.toString());
    setIsEditing(false);
  };

  return (
    <Card onPress={onPress}>
      <View style={styles.header}>
        <Ionicons name="flag" size={20} color={designTokens.colors.accent} />
        <Text style={styles.title}>Weekly Goal</Text>
      </View>

      <View style={styles.goalText}>
        <Text style={styles.goalLabel}>Apply to </Text>
        
        {isEditing ? (
          <View style={styles.editContainer}>
            <TextInput
              style={styles.editInput}
              value={editValue}
              onChangeText={setEditValue}
              keyboardType="numeric"
              selectTextOnFocus
              autoFocus
              onSubmitEditing={handleSaveTarget}
              onBlur={handleCancelEdit}
            />
            <Pressable onPress={handleSaveTarget} style={styles.saveButton}>
              <Ionicons name="checkmark" size={16} color={designTokens.colors.accentSoft} />
            </Pressable>
          </View>
        ) : (
          <Pressable onPress={() => setIsEditing(true)}>
            <Text style={styles.goalNumber}>{goalTarget}</Text>
          </Pressable>
        )}
        
        <Text style={styles.goalLabel}> roles</Text>
      </View>

      <View style={styles.progressSection}>
        <View style={styles.progressBar}>
          <View 
            style={[
              styles.progressFill,
              { width: `${progressPercentage}%` }
            ]} 
          />
        </View>
        
        <View style={styles.progressStats}>
          <Text style={styles.progressText}>
            {currentProgress} of {goalTarget} completed
          </Text>
          <Text style={styles.progressPercentage}>
            {Math.round(progressPercentage)}%
          </Text>
        </View>
      </View>

      {progressPercentage >= 100 && (
        <View style={styles.successBadge}>
          <Ionicons name="trophy" size={16} color={designTokens.colors.highlight} />
          <Text style={styles.successText}>Goal Achieved!</Text>
        </View>
      )}
    </Card>
  );
};

const styles = StyleSheet.create({
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  title: {
    fontSize: 16,
    fontWeight: '600',
    color: designTokens.colors.textPrimary,
    marginLeft: 8,
  },
  goalText: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 20,
    flexWrap: 'wrap',
  },
  goalLabel: {
    fontSize: 18,
    color: designTokens.colors.textPrimary,
  },
  goalNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: designTokens.colors.accent,
    paddingHorizontal: 4,
    paddingVertical: 2,
    borderRadius: 4,
    backgroundColor: designTokens.colors.accent + '20',
  },
  editContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  editInput: {
    fontSize: 24,
    fontWeight: 'bold',
    color: designTokens.colors.accent,
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 4,
    backgroundColor: designTokens.colors.bgPrimary,
    borderWidth: 2,
    borderColor: designTokens.colors.accent,
    minWidth: 40,
    textAlign: 'center',
  },
  saveButton: {
    marginLeft: 4,
    padding: 4,
  },
  progressSection: {
    marginBottom: 16,
  },
  progressBar: {
    height: 8,
    backgroundColor: designTokens.colors.textSecondary + '20',
    borderRadius: 4,
    overflow: 'hidden',
    marginBottom: 8,
  },
  progressFill: {
    height: '100%',
    backgroundColor: designTokens.colors.accentSoft,
    borderRadius: 4,
  },
  progressStats: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  progressText: {
    fontSize: 12,
    color: designTokens.colors.textSecondary,
  },
  progressPercentage: {
    fontSize: 14,
    fontWeight: '600',
    color: designTokens.colors.accentSoft,
  },
  successBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: designTokens.colors.highlight + '30',
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 20,
  },
  successText: {
    fontSize: 14,
    fontWeight: '600',
    color: designTokens.colors.highlight,
    marginLeft: 6,
  },
}); 