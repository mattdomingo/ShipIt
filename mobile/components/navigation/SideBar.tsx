import React, { useState, useRef, useEffect } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  Pressable, 
  Animated, 
  Dimensions,
  Platform
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { designTokens } from '../../theme/tokens';
import AsyncStorage from '@react-native-async-storage/async-storage';

const { width: screenWidth } = Dimensions.get('window');
const SIDEBAR_EXPANDED_WIDTH = 240;
const SIDEBAR_COLLAPSED_WIDTH = 72;
const MOBILE_BREAKPOINT = 768;

interface NavItem {
  id: string;
  label: string;
  icon: keyof typeof Ionicons.glyphMap;
  route: string;
}

const navItems: NavItem[] = [
  { id: 'dashboard', label: 'Dashboard', icon: 'grid-outline', route: 'Dashboard' },
  { id: 'applications', label: 'Applications', icon: 'document-text-outline', route: 'Applications' },
  { id: 'goals', label: 'Goals', icon: 'flag-outline', route: 'Goals' },
  { id: 'postings', label: 'Postings', icon: 'briefcase-outline', route: 'Postings' },
  { id: 'resume', label: 'Resume', icon: 'person-outline', route: 'Resume' },
  { id: 'news', label: 'News', icon: 'newspaper-outline', route: 'News' },
];

interface SideBarProps {
  activeRoute: string;
  onNavigate: (route: string) => void;
}

export const SideBar: React.FC<SideBarProps> = ({ activeRoute, onNavigate }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMobileDrawer, setIsMobileDrawer] = useState(screenWidth <= MOBILE_BREAKPOINT);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  
  const widthAnim = useRef(new Animated.Value(SIDEBAR_EXPANDED_WIDTH)).current;
  const drawerAnim = useRef(new Animated.Value(-SIDEBAR_EXPANDED_WIDTH)).current;

  useEffect(() => {
    loadCollapsedState();
    
    const updateLayout = () => {
      const isMobile = screenWidth <= MOBILE_BREAKPOINT;
      setIsMobileDrawer(isMobile);
      if (isMobile) {
        setIsDrawerOpen(false);
      }
    };
    
    updateLayout();
  }, []);

  const loadCollapsedState = async () => {
    try {
      const saved = await AsyncStorage.getItem('sidebarCollapsed');
      if (saved !== null) {
        const collapsed = JSON.parse(saved);
        setIsCollapsed(collapsed);
        widthAnim.setValue(collapsed ? SIDEBAR_COLLAPSED_WIDTH : SIDEBAR_EXPANDED_WIDTH);
      }
    } catch (error) {
      console.error('Error loading sidebar state:', error);
    }
  };

  const saveCollapsedState = async (collapsed: boolean) => {
    try {
      await AsyncStorage.setItem('sidebarCollapsed', JSON.stringify(collapsed));
    } catch (error) {
      console.error('Error saving sidebar state:', error);
    }
  };

  const toggleCollapse = () => {
    const newCollapsed = !isCollapsed;
    setIsCollapsed(newCollapsed);
    saveCollapsedState(newCollapsed);
    
    Animated.spring(widthAnim, {
      toValue: newCollapsed ? SIDEBAR_COLLAPSED_WIDTH : SIDEBAR_EXPANDED_WIDTH,
      useNativeDriver: false,
      ...designTokens.animation.spring,
    }).start();
  };

  const toggleDrawer = () => {
    const newOpen = !isDrawerOpen;
    setIsDrawerOpen(newOpen);
    
    Animated.spring(drawerAnim, {
      toValue: newOpen ? 0 : -SIDEBAR_EXPANDED_WIDTH,
      useNativeDriver: false,
      ...designTokens.animation.spring,
    }).start();
  };

  const handleNavItemPress = (route: string) => {
    onNavigate(route);
    if (isMobileDrawer) {
      setIsDrawerOpen(false);
      drawerAnim.setValue(-SIDEBAR_EXPANDED_WIDTH);
    }
  };

  const renderNavItem = (item: NavItem) => {
    const isActive = activeRoute === item.route;
    
    return (
      <Pressable
        key={item.id}
        style={[
          styles.navItem,
          isActive && styles.navItemActive,
          isCollapsed && !isMobileDrawer && styles.navItemCollapsed,
        ]}
        onPress={() => handleNavItemPress(item.route)}
      >
        <Ionicons
          name={item.icon}
          size={24}
          color={isActive ? designTokens.colors.accent : designTokens.colors.textSecondary}
        />
        {(!isCollapsed || isMobileDrawer) && (
          <Animated.Text 
            style={[
              styles.navLabel,
              isActive && styles.navLabelActive,
            ]}
          >
            {item.label}
          </Animated.Text>
        )}
      </Pressable>
    );
  };

  if (isMobileDrawer) {
    return (
      <>
        <Pressable style={styles.mobileMenuButton} onPress={toggleDrawer}>
          <Ionicons name="menu" size={24} color={designTokens.colors.textPrimary} />
        </Pressable>
        
        {isDrawerOpen && (
          <Pressable style={styles.drawerOverlay} onPress={toggleDrawer} />
        )}
        
        <Animated.View 
          style={[
            styles.mobileDrawer,
            { transform: [{ translateX: drawerAnim }] }
          ]}
        >
          <View style={styles.drawerHeader}>
            <Text style={styles.logo}>ShipIt</Text>
            <Pressable onPress={toggleDrawer}>
              <Ionicons name="close" size={24} color={designTokens.colors.textPrimary} />
            </Pressable>
          </View>
          
          <View style={styles.navSection}>
            {navItems.map(renderNavItem)}
          </View>
          
          <View style={styles.userSection}>
            <View style={styles.userAvatar} />
            <Text style={styles.userName}>John Doe</Text>
          </View>
        </Animated.View>
      </>
    );
  }

  return (
    <Animated.View style={[styles.sidebar, { width: widthAnim }]}>
      <View style={styles.logoSection}>
        {!isCollapsed && <Text style={styles.logo}>ShipIt</Text>}
        {isCollapsed && <Text style={styles.logoCollapsed}>S</Text>}
      </View>
      
      <View style={styles.navSection}>
        {navItems.map(renderNavItem)}
      </View>
      
      <View style={styles.bottomSection}>
        <Pressable style={styles.collapseButton} onPress={toggleCollapse}>
          <Ionicons
            name={isCollapsed ? "chevron-forward" : "chevron-back"}
            size={20}
            color={designTokens.colors.textSecondary}
          />
        </Pressable>
        
        <View style={[styles.userSection, isCollapsed && styles.userSectionCollapsed]}>
          <View style={styles.userAvatar} />
          {!isCollapsed && <Text style={styles.userName}>John Doe</Text>}
        </View>
      </View>
    </Animated.View>
  );
};

const styles = StyleSheet.create({
  sidebar: {
    backgroundColor: designTokens.colors.bgPrimary,
    borderRightWidth: 1,
    borderRightColor: '#E5E7EB',
    paddingVertical: 20,
    paddingHorizontal: 16,
    justifyContent: 'space-between',
  },
  mobileMenuButton: {
    position: 'absolute',
    top: Platform.OS === 'ios' ? 50 : 30,
    left: 20,
    zIndex: 1000,
    padding: 8,
    backgroundColor: designTokens.colors.bgPrimary,
    borderRadius: 8,
    ...designTokens.shadows.card,
  },
  drawerOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.5)',
    zIndex: 999,
  },
  mobileDrawer: {
    position: 'absolute',
    top: 0,
    left: 0,
    bottom: 0,
    width: SIDEBAR_EXPANDED_WIDTH,
    backgroundColor: designTokens.colors.bgPrimary,
    paddingVertical: Platform.OS === 'ios' ? 50 : 30,
    paddingHorizontal: 16,
    zIndex: 1000,
    ...designTokens.shadows.cardHover,
  },
  drawerHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingBottom: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
    marginBottom: 20,
  },
  logoSection: {
    paddingBottom: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  logo: {
    fontSize: 24,
    fontWeight: 'bold',
    color: designTokens.colors.textPrimary,
    fontFamily: designTokens.typography.fontFamily,
  },
  logoCollapsed: {
    fontSize: 20,
    fontWeight: 'bold',
    color: designTokens.colors.textPrimary,
    textAlign: 'center',
  },
  navSection: {
    flex: 1,
    paddingTop: 20,
  },
  navItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    marginBottom: 4,
  },
  navItemActive: {
    backgroundColor: designTokens.colors.accent + '20',
  },
  navItemCollapsed: {
    justifyContent: 'center',
    paddingHorizontal: 8,
  },
  navLabel: {
    marginLeft: 12,
    fontSize: 16,
    color: designTokens.colors.textSecondary,
    fontFamily: designTokens.typography.fontFamily,
  },
  navLabelActive: {
    color: designTokens.colors.accent,
    fontWeight: '600',
  },
  bottomSection: {
    paddingTop: 20,
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
  },
  collapseButton: {
    alignItems: 'center',
    paddingVertical: 8,
    marginBottom: 16,
  },
  userSection: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  userSectionCollapsed: {
    justifyContent: 'center',
  },
  userAvatar: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: designTokens.colors.accentSoft,
  },
  userName: {
    marginLeft: 12,
    fontSize: 14,
    color: designTokens.colors.textPrimary,
    fontWeight: '500',
  },
}); 