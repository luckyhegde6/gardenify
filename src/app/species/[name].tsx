import { useState, useEffect, useCallback } from "react";
import { View, Text, ScrollView, StyleSheet, Linking } from "react-native";
import { useLocalSearchParams } from "expo-router";
import { apiClient } from "@/lib/api-client";
import { Button } from "@/components/button";
import { Loading } from "@/components/loading";
import { spacing, borderRadius, typography } from "@/constants/theme";
import { useTheme, useThemedStyles } from "@/hooks/use-theme";
import type { SpeciesListItem } from "@/lib/types";
import type { ThemeColors } from "@/hooks/use-theme";

export default function SpeciesDetailScreen() {
  const { name } = useLocalSearchParams<{ name: string }>();
  const { colors } = useTheme();
  const styles = useThemedStyles(makeStyles);
  const sectionStyles = useThemedStyles(makeSectionStyles);
  const infoStyles = useThemedStyles(makeInfoStyles);
  const [species, setSpecies] = useState<SpeciesListItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSpecies = useCallback(async () => {
    if (!name) return;
    setLoading(true);
    setError(null);
    try {
      const decodedName = decodeURIComponent(name);
      const result = await apiClient.getSpeciesByName(decodedName);
      setSpecies(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Species not found");
    } finally {
      setLoading(false);
    }
  }, [name]);

  useEffect(() => {
    fetchSpecies();
  }, [fetchSpecies]);

  if (loading) return <Loading message="Loading species info..." />;
  if (error) {
    return (
      <View style={[styles.center, { backgroundColor: colors.background }]}>
        <Text style={[styles.errorText, { color: colors.error }]}>{error}</Text>
      </View>
    );
  }
  if (!species) {
    return (
      <View style={[styles.center, { backgroundColor: colors.background }]}>
        <Text style={[styles.errorText, { color: colors.error }]}>
          Species not found
        </Text>
      </View>
    );
  }

  const commonNames = species.common_names ?? [];
  const wikipediaUrl = `https://en.wikipedia.org/wiki/${encodeURIComponent(
    species.scientific_name,
  )}`;
  const gbifUrl = `https://www.gbif.org/species/search?q=${encodeURIComponent(
    species.scientific_name,
  )}`;

  return (
    <ScrollView
      style={[styles.container, { backgroundColor: colors.background }]}
      contentContainerStyle={styles.content}
    >
      <View style={styles.header}>
        <Text style={[styles.scientificName, { color: colors.text }]}>
          {species.scientific_name}
        </Text>
        {commonNames.length > 0 && (
          <Text style={[styles.commonNames, { color: colors.textSecondary }]}>
            {commonNames.join(", ")}
          </Text>
        )}
      </View>

      <View style={sectionStyles.container}>
        <Text style={[sectionStyles.title, { color: colors.textSecondary }]}>
          Taxonomy
        </Text>
        <View
          style={[sectionStyles.content, { backgroundColor: colors.surface }]}
        >
          <InfoRow
            label="Family"
            value={species.family}
            infoStyles={infoStyles}
            colors={colors}
          />
          <InfoRow
            label="Genus"
            value={species.genus}
            infoStyles={infoStyles}
            colors={colors}
          />
          <InfoRow
            label="Scientific Name"
            value={species.scientific_name}
            infoStyles={infoStyles}
            colors={colors}
          />
        </View>
      </View>

      <View style={sectionStyles.container}>
        <Text style={[sectionStyles.title, { color: colors.textSecondary }]}>
          External Links
        </Text>
        <Button
          title="View on Wikipedia"
          onPress={() => Linking.openURL(wikipediaUrl)}
          variant="outline"
          size="sm"
          style={styles.linkButton}
        />
        <Button
          title="View on GBIF"
          onPress={() => Linking.openURL(gbifUrl)}
          variant="outline"
          size="sm"
          style={styles.linkButton}
        />
      </View>

      {species.id > 0 && (
        <View style={sectionStyles.container}>
          <Text style={[sectionStyles.title, { color: colors.textSecondary }]}>
            Database Info
          </Text>
          <View
            style={[sectionStyles.content, { backgroundColor: colors.surface }]}
          >
            <InfoRow
              label="Species ID"
              value={String(species.id)}
              infoStyles={infoStyles}
              colors={colors}
            />
            <InfoRow
              label="Database"
              value="Local Plant Database"
              infoStyles={infoStyles}
              colors={colors}
            />
          </View>
        </View>
      )}
    </ScrollView>
  );
}

function InfoRow({
  label,
  value,
  infoStyles,
  colors,
}: {
  label: string;
  value: string;
  infoStyles: any;
  colors: ThemeColors;
}) {
  if (!value) return null;
  return (
    <View style={infoStyles.row}>
      <Text style={[infoStyles.label, { color: colors.textSecondary }]}>
        {label}
      </Text>
      <Text style={[infoStyles.value, { color: colors.text }]}>{value}</Text>
    </View>
  );
}

function makeStyles(c: ThemeColors) {
  return StyleSheet.create({
    container: {
      flex: 1,
    },
    content: {
      padding: spacing.lg,
      paddingBottom: spacing.xxl,
    },
    center: {
      flex: 1,
      alignItems: "center",
      justifyContent: "center",
      padding: spacing.lg,
    },
    header: {
      marginBottom: spacing.xl,
    },
    scientificName: {
      ...typography.h1,
      fontStyle: "italic",
    },
    commonNames: {
      ...typography.body,
      marginTop: spacing.xs,
    },
    linkButton: {
      marginBottom: spacing.sm,
    },
    errorText: {
      ...typography.body,
      textAlign: "center",
    },
  });
}

function makeSectionStyles(c: ThemeColors) {
  return StyleSheet.create({
    container: {
      marginBottom: spacing.lg,
    },
    title: {
      ...typography.label,
      textTransform: "uppercase",
      marginBottom: spacing.sm,
    },
    content: {
      borderRadius: borderRadius.md,
      padding: spacing.md,
    },
  });
}

function makeInfoStyles(c: ThemeColors) {
  return StyleSheet.create({
    row: {
      flexDirection: "row",
      justifyContent: "space-between",
      paddingVertical: 6,
    },
    label: {
      ...typography.bodySmall,
      flex: 1,
    },
    value: {
      ...typography.bodySmall,
      flex: 2,
      textAlign: "right",
    },
  });
}
