import { View, Text, Image, TouchableOpacity, StyleSheet } from "react-native";
import { spacing, borderRadius, typography, shadows } from "@/constants/theme";
import { useTheme, useThemedStyles } from "@/hooks/use-theme";
import type { ThemeColors } from "@/hooks/use-theme";

interface PlantCardProps {
  scientificName: string;
  commonNames: string[];
  confidence: number;
  imageUrl?: string;
  onPress?: () => void;
}

export function PlantCard({
  scientificName,
  commonNames,
  confidence,
  imageUrl,
  onPress,
}: PlantCardProps) {
  const { colors } = useTheme();
  const styles = useThemedStyles((c) => makeStyles(c));

  const confidencePercent = (confidence * 100).toFixed(1);
  const confidenceColor = getConfidenceColor(confidence, colors);
  const displayName = commonNames.length > 0 ? commonNames[0] : scientificName;

  return (
    <TouchableOpacity
      onPress={onPress}
      activeOpacity={0.7}
      style={[styles.card, shadows.md]}
    >
      {imageUrl ? (
        <Image source={{ uri: imageUrl }} style={styles.image} />
      ) : (
        <View style={styles.imagePlaceholder}>
          <Text style={styles.placeholderIcon}>🌿</Text>
        </View>
      )}
      <View style={styles.info}>
        <Text style={styles.commonName} numberOfLines={1}>
          {displayName}
        </Text>
        <Text style={styles.scientificName} numberOfLines={1}>
          {scientificName}
        </Text>
        <View style={styles.confidenceRow}>
          <View
            style={[
              styles.confidenceBar,
              { backgroundColor: confidenceColor + "30" },
            ]}
          >
            <View
              style={[
                styles.confidenceFill,
                { width: `${confidence}%`, backgroundColor: confidenceColor },
              ]}
            />
          </View>
          <Text style={[styles.confidenceText, { color: confidenceColor }]}>
            {confidencePercent}%
          </Text>
        </View>
      </View>
    </TouchableOpacity>
  );
}

function getConfidenceColor(score: number, colors: ThemeColors): string {
  if (score >= 0.8) return colors.confidenceHigh;
  if (score >= 0.5) return colors.confidenceMedium;
  return colors.confidenceLow;
}

function makeStyles(c: ThemeColors) {
  return StyleSheet.create({
    card: {
      flexDirection: "row",
      backgroundColor: c.surface,
      borderRadius: borderRadius.lg,
      overflow: "hidden",
    },
    image: {
      width: 100,
      height: 100,
    },
    imagePlaceholder: {
      width: 100,
      height: 100,
      backgroundColor: c.infoLight,
      alignItems: "center",
      justifyContent: "center",
    },
    placeholderIcon: {
      fontSize: 36,
    },
    info: {
      flex: 1,
      padding: spacing.md,
      justifyContent: "center",
    },
    commonName: {
      ...typography.h3,
      color: c.text,
      marginBottom: 2,
    },
    scientificName: {
      ...typography.bodySmall,
      color: c.textSecondary,
      fontStyle: "italic",
      marginBottom: spacing.sm,
    },
    confidenceRow: {
      flexDirection: "row",
      alignItems: "center",
      gap: spacing.sm,
    },
    confidenceBar: {
      flex: 1,
      height: 6,
      borderRadius: 3,
      overflow: "hidden",
    },
    confidenceFill: {
      height: "100%",
      borderRadius: 3,
    },
    confidenceText: {
      ...typography.caption,
      fontWeight: "600",
      minWidth: 44,
      textAlign: "right",
    },
  });
}
