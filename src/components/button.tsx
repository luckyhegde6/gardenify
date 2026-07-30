import {
  TouchableOpacity,
  Text,
  StyleSheet,
  ActivityIndicator,
  ViewStyle,
  TextStyle,
} from "react-native";
import { spacing, borderRadius, typography } from "@/constants/theme";
import { useTheme, useThemedStyles } from "@/hooks/use-theme";
import type { ThemeColors } from "@/hooks/use-theme";

interface ButtonProps {
  title: string;
  onPress: () => void;
  variant?: "primary" | "secondary" | "outline" | "ghost" | "danger";
  size?: "sm" | "md" | "lg";
  loading?: boolean;
  disabled?: boolean;
  style?: ViewStyle;
  textStyle?: TextStyle;
}

export function Button({
  title,
  onPress,
  variant = "primary",
  size = "md",
  loading = false,
  disabled = false,
  style,
  textStyle,
}: ButtonProps) {
  const { colors } = useTheme();
  const styles = useThemedStyles(makeStyles);
  const isDisabled = disabled || loading;

  return (
    <TouchableOpacity
      onPress={onPress}
      disabled={isDisabled}
      activeOpacity={0.7}
      style={[
        styles.base,
        styles[`variant_${variant}`],
        styles[`size_${size}`],
        isDisabled && styles.disabled,
        style,
      ]}
    >
      {loading ? (
        <ActivityIndicator
          color={variant === "primary" ? colors.textInverse : colors.primary}
          size="small"
        />
      ) : (
        <Text
          style={[
            styles.text,
            styles[`text_${variant}`],
            styles[`textSize_${size}`],
            isDisabled && styles.textDisabled,
            textStyle,
          ]}
        >
          {title}
        </Text>
      )}
    </TouchableOpacity>
  );
}

function makeStyles(c: ThemeColors) {
  return StyleSheet.create({
    base: {
      alignItems: "center",
      justifyContent: "center",
      borderRadius: borderRadius.md,
    },
    variant_primary: {
      backgroundColor: c.primary,
    },
    variant_secondary: {
      backgroundColor: c.secondary,
    },
    variant_outline: {
      backgroundColor: "transparent",
      borderWidth: 1.5,
      borderColor: c.primary,
    },
    variant_ghost: {
      backgroundColor: "transparent",
    },
    variant_danger: {
      backgroundColor: c.error,
    },
    size_sm: {
      paddingVertical: spacing.sm,
      paddingHorizontal: spacing.md,
    },
    size_md: {
      paddingVertical: spacing.md - 4,
      paddingHorizontal: spacing.lg,
    },
    size_lg: {
      paddingVertical: spacing.md,
      paddingHorizontal: spacing.xl,
    },
    disabled: {
      opacity: 0.5,
    },
    text: {
      ...typography.button,
    },
    text_primary: {
      color: c.textInverse,
    },
    text_secondary: {
      color: c.textInverse,
    },
    text_outline: {
      color: c.primary,
    },
    text_ghost: {
      color: c.primary,
    },
    text_danger: {
      color: c.textInverse,
    },
    textSize_sm: {
      fontSize: 14,
    },
    textSize_md: {
      fontSize: 16,
    },
    textSize_lg: {
      fontSize: 18,
    },
    textDisabled: {
      opacity: 0.7,
    },
  });
}
