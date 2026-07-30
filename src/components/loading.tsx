import { View, Text, ActivityIndicator, StyleSheet } from "react-native";
import { spacing, typography } from "@/constants/theme";
import { useTheme, useThemedStyles } from "@/hooks/use-theme";
import type { ThemeColors } from "@/hooks/use-theme";

interface LoadingProps {
  message?: string;
  size?: "small" | "large";
}

export function Loading({ message, size = "large" }: LoadingProps) {
  const { colors } = useTheme();
  const styles = useThemedStyles(makeStyles);

  return (
    <View style={styles.container}>
      <ActivityIndicator size={size} color={colors.primary} />
      {message && <Text style={styles.message}>{message}</Text>}
    </View>
  );
}

export function LoadingOverlay({ message }: { message?: string }) {
  const { colors } = useTheme();
  const styles = useThemedStyles(makeOverlayStyles);

  return (
    <View style={styles.overlay}>
      <View style={styles.overlayContent}>
        <ActivityIndicator size="large" color={colors.primary} />
        {message && <Text style={styles.message}>{message}</Text>}
      </View>
    </View>
  );
}

function makeStyles(c: ThemeColors) {
  return StyleSheet.create({
    container: {
      flex: 1,
      alignItems: "center",
      justifyContent: "center",
      padding: spacing.xl,
    },
    message: {
      ...typography.body,
      color: c.textSecondary,
      marginTop: spacing.md,
      textAlign: "center",
    },
  });
}

function makeOverlayStyles(c: ThemeColors) {
  return StyleSheet.create({
    overlay: {
      ...StyleSheet.absoluteFillObject,
      backgroundColor: "rgba(0,0,0,0.4)",
      alignItems: "center",
      justifyContent: "center",
      zIndex: 100,
    },
    overlayContent: {
      backgroundColor: c.surface,
      borderRadius: 16,
      padding: spacing.xl,
      alignItems: "center",
      minWidth: 160,
    },
    message: {
      ...typography.body,
      color: c.textSecondary,
      marginTop: spacing.md,
      textAlign: "center",
    },
  });
}
