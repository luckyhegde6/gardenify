export const lightColors = {
  primary: "#208AEF",
  primaryDark: "#1A75CC",
  primaryLight: "#6BB3F5",
  secondary: "#34C759",
  secondaryDark: "#2DB14F",
  secondaryLight: "#6FD98A",

  background: "#F5F7FA",
  surface: "#FFFFFF",
  surfaceElevated: "#FFFFFF",

  text: "#1A1A2E",
  textSecondary: "#6B7280",
  textTertiary: "#9CA3AF",
  textInverse: "#FFFFFF",

  border: "#E5E7EB",
  borderLight: "#F3F4F6",
  divider: "#E5E7EB",

  error: "#EF4444",
  errorLight: "#FEE2E2",
  warning: "#F59E0B",
  warningLight: "#FEF3C7",
  success: "#10B981",
  successLight: "#D1FAE5",
  info: "#3B82F6",
  infoLight: "#DBEAFE",

  confidenceHigh: "#10B981",
  confidenceMedium: "#F59E0B",
  confidenceLow: "#EF4444",

  favorite: "#EF4444",
  favoriteLight: "#FEE2E2",

  tabBarBackground: "#FFFFFF",
  tabBarBorder: "#E5E7EB",
  tabBarInactive: "#9CA3AF",
  tabBarActive: "#208AEF",
};

export const darkColors = {
  primary: "#3B9EFF",
  primaryDark: "#208AEF",
  primaryLight: "#1E3A5F",
  secondary: "#34C759",
  secondaryDark: "#2DB14F",
  secondaryLight: "#1A3A2E",

  background: "#0F0F1A",
  surface: "#1A1A2E",
  surfaceElevated: "#242442",

  text: "#E8E8F0",
  textSecondary: "#9CA3AF",
  textTertiary: "#6B7280",
  textInverse: "#FFFFFF",

  border: "#2D2D44",
  borderLight: "#1E1E32",
  divider: "#2D2D44",

  error: "#F87171",
  errorLight: "#3D1A1A",
  warning: "#FBBF24",
  warningLight: "#3D2E0A",
  success: "#34D399",
  successLight: "#0D3328",
  info: "#60A5FA",
  infoLight: "#0D1B3D",

  confidenceHigh: "#34D399",
  confidenceMedium: "#FBBF24",
  confidenceLow: "#F87171",

  favorite: "#F87171",
  favoriteLight: "#3D1A1A",

  tabBarBackground: "#1A1A2E",
  tabBarBorder: "#2D2D44",
  tabBarInactive: "#6B7280",
  tabBarActive: "#3B9EFF",
};

export const colors = lightColors;

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
};

export const borderRadius = {
  sm: 8,
  md: 12,
  lg: 16,
  xl: 24,
  full: 9999,
};

export const typography = {
  h1: {
    fontSize: 28,
    fontWeight: "700" as const,
    lineHeight: 34,
  },
  h2: {
    fontSize: 22,
    fontWeight: "700" as const,
    lineHeight: 28,
  },
  h3: {
    fontSize: 18,
    fontWeight: "600" as const,
    lineHeight: 24,
  },
  body: {
    fontSize: 16,
    fontWeight: "400" as const,
    lineHeight: 22,
  },
  bodySmall: {
    fontSize: 14,
    fontWeight: "400" as const,
    lineHeight: 20,
  },
  caption: {
    fontSize: 12,
    fontWeight: "400" as const,
    lineHeight: 16,
  },
  label: {
    fontSize: 14,
    fontWeight: "600" as const,
    lineHeight: 18,
  },
  button: {
    fontSize: 16,
    fontWeight: "600" as const,
    lineHeight: 20,
  },
};

export const shadows = {
  sm: {
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  md: {
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  lg: {
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 5,
  },
};
