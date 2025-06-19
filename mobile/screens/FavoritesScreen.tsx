import React from 'react';
import { View, Text } from 'react-native';

export default function FavoritesScreen() {
  return (
    <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
      <Text style={{ fontSize: 24 }}>Saved Favorites</Text>
      {/* TODO: Display saved internships */}
    </View>
  );
}
