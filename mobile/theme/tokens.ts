export const designTokens = {
  colors: {
    bgPrimary: '#FFFFFF',
    bgMuted: '#F5F7FA',
    textPrimary: '#1C1C1E',
    textSecondary: '#4E5560',
    accent: '#A7C4FF',
    accentSoft: '#7FD1AE',
    highlight: '#FFCACE',
  },
  typography: {
    fontFamily: 'System',
    rootSize: 16,
    h1Size: 32,
    h2Size: 24,
  },
  spacing: {
    cardPadding: 24,
    gridGap: 24,
  },
  borderRadius: {
    card: 12,
  },
  shadows: {
    card: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.1,
      shadowRadius: 8,
      elevation: 3,
    },
    cardHover: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 6 },
      shadowOpacity: 0.15,
      shadowRadius: 12,
      elevation: 8,
    },
  },
  animation: {
    timing: {
      fast: 250,
      medium: 350,
    },
    spring: {
      damping: 18,
      stiffness: 120,
    },
  },
} as const;

export type DesignTokens = typeof designTokens; 