import React from 'react';
import { View, Text, Button } from 'react-native';

export default function UploadScreen({ navigation }) {
  return (
    <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
      <Text style={{ fontSize: 24, marginBottom: 20 }}>Upload Your Resume</Text>
      {/* TODO: Add file picker and upload logic */}
      <Button title="Go to Results" onPress={() => navigation.navigate('Results')} />
    </View>
  );
}
