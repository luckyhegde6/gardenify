import { useState, useEffect, useCallback } from "react";
import { View, Text, ScrollView, StyleSheet, Alert, Share } from "react-native";
import { useLocalSearchParams, router } from "expo-router";
import { supabase } from "@/lib/supabase";
import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/button";
import { Loading } from "@/components/loading";
import { spacing, borderRadius, typography } from "@/constants/theme";
import { useTheme, useThemedStyles } from "@/hooks/use-theme";
import * as Haptics from "expo-haptics";
import type { IdentificationResponse } from "@/lib/types";
import type { ThemeColors } from "@/hooks/use-theme";

export default function IdentificationDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { user } = useAuth();
  const { colors } = useTheme();
  const styles = useThemedStyles(makeStyles);
  const sectionStyles = useThemedStyles(makeSectionStyles);
  const careStyles = useThemedStyles(makeCareStyles);
  const infoStyles = useThemedStyles(makeInfoStyles);
  const [result, setResult] = useState<IdentificationResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isFavorite, setIsFavorite] = useState(false);
  const [favoriteLoading, setFavoriteLoading] = useState(false);

  const fetchResult = useCallback(async () => {
    if (!id || !user) return;
    setLoading(true);
    setError(null);
    try {
      const { data, error } = await supabase
        .from("identifications")
        .select("results_json, image_urls")
        .eq("id", id)
        .eq("user_id", user.id)
        .single();

      if (error) throw error;
      if (data?.results_json) {
        const parsed = JSON.parse(data.results_json) as IdentificationResponse;
        setResult(parsed);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load result");
    } finally {
      setLoading(false);
    }
  }, [id, user]);

  const checkFavorite = useCallback(async () => {
    if (!result?.best_match || !user) return;
    const { data } = await supabase
      .from("favorites")
      .select("id")
      .eq("user_id", user.id)
      .eq("species_scientific_name", result.best_match)
      .single();
    setIsFavorite(!!data);
  }, [result, user]);

  const toggleFavorite = async () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    if (!result?.best_match || !user) return;
    setFavoriteLoading(true);
    try {
      if (isFavorite) {
        await supabase
          .from("favorites")
          .delete()
          .eq("user_id", user.id)
          .eq("species_scientific_name", result.best_match);
        setIsFavorite(false);
      } else {
        await supabase.from("favorites").insert({
          user_id: user.id,
          species_scientific_name: result.best_match,
          species_common_name:
            result.results[0]?.species?.common_names?.[0] ?? "",
          species_family: result.results[0]?.species?.family ?? "",
          species_genus: result.results[0]?.species?.genus ?? "",
        });
        setIsFavorite(true);
      }
    } catch {
      Alert.alert("Error", "Could not update favorite");
    } finally {
      setFavoriteLoading(false);
    }
  };

  useEffect(() => {
    fetchResult();
  }, [fetchResult]);

  useEffect(() => {
    if (result) checkFavorite();
  }, [result, checkFavorite]);

  if (loading) return <Loading message="Loading result..." />;
  if (error) {
    return (
      <View style={[styles.center, { backgroundColor: colors.background }]}>
        <Text style={[styles.errorText, { color: colors.error }]}>{error}</Text>
        <Button title="Go Back" onPress={() => router.back()} />
      </View>
    );
  }
  if (!result) {
    return (
      <View style={[styles.center, { backgroundColor: colors.background }]}>
        <Text style={[styles.errorText, { color: colors.error }]}>
          Result not found
        </Text>
        <Button title="Go Back" onPress={() => router.back()} />
      </View>
    );
  }

  const best = result.results?.[0];
  if (!best) {
    return (
      <View style={[styles.center, { backgroundColor: colors.background }]}>
        <Text style={styles.noResultIcon}>🔍</Text>
        <Text style={[styles.noResultTitle, { color: colors.text }]}>
          No Match Found
        </Text>
        <Text style={[styles.errorText, { color: colors.error }]}>
          Could not identify the plant from this image. Try a clearer photo of a
          leaf, flower, or fruit.
        </Text>
        <Button title="🔄 Try Again" onPress={() => router.back()} />
        <Button
          title="🏠 Home"
          onPress={() => router.replace("/")}
          variant="ghost"
        />
      </View>
    );
  }

  const confidenceColor = getConfidenceColor(best.score, colors);
  const displayName =
    best.species.common_names.length > 0
      ? best.species.common_names[0]
      : best.species.scientific_name;

  return (
    <ScrollView
      style={[styles.container, { backgroundColor: colors.background }]}
      contentContainerStyle={styles.content}
    >
      <View style={styles.header}>
        <Text style={[styles.speciesName, { color: colors.text }]}>
          {displayName}
        </Text>
        <Text style={[styles.scientificName, { color: colors.textSecondary }]}>
          {best.species.scientific_name}
        </Text>

        <View style={styles.confidenceRow}>
          <View
            style={[
              styles.confidenceBadge,
              { backgroundColor: confidenceColor + "20" },
            ]}
          >
            <Text style={[styles.confidenceScore, { color: confidenceColor }]}>
              {result.source === "local"
                ? "Offline"
                : `${(best.score * 100).toFixed(1)}%`}
            </Text>
          </View>
          <Text style={[styles.sourceLabel, { color: colors.textTertiary }]}>
            {result.source === "plantnet"
              ? "PlantNet"
              : result.source === "cache"
                ? "Cached"
                : "Local DB"}
          </Text>
        </View>

        <View style={styles.actionRow}>
          <Button
            title={isFavorite ? "❤️ Saved" : "🤍 Save"}
            onPress={toggleFavorite}
            variant={isFavorite ? "ghost" : "outline"}
            size="sm"
            loading={favoriteLoading}
            style={styles.actionButton}
          />
          <Button
            title="📤 Share"
            onPress={async () => {
              Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
              const name =
                best.species.common_names[0] || best.species.scientific_name;
              await Share.share({
                message: `🌿 I identified this plant as ${name} (${best.species.scientific_name}) using Gardenify!`,
              });
            }}
            variant="outline"
            size="sm"
            style={styles.actionButton}
          />
        </View>
      </View>

      <View style={sectionStyles.container}>
        <Text style={[sectionStyles.title, { color: colors.textSecondary }]}>
          Taxonomy
        </Text>
        <InfoRow
          label="Family"
          value={best.species.family}
          infoStyles={infoStyles}
          colors={colors}
        />
        <InfoRow
          label="Genus"
          value={best.species.genus}
          infoStyles={infoStyles}
          colors={colors}
        />
        <InfoRow
          label="Scientific Name"
          value={best.species.scientific_name}
          italic
          infoStyles={infoStyles}
          colors={colors}
        />
      </View>

      {result.disease && result.disease.name && (
        <View style={sectionStyles.container}>
          <Text style={[sectionStyles.title, { color: colors.textSecondary }]}>
            Disease Detection
          </Text>
          <View
            style={[styles.diseaseCard, { backgroundColor: colors.errorLight }]}
          >
            <Text style={[styles.diseaseName, { color: colors.error }]}>
              {result.disease.name}
            </Text>
            {result.disease.confidence > 0 && (
              <Text style={[styles.diseaseConfidence, { color: colors.error }]}>
                {(result.disease.confidence * 100).toFixed(1)}% confidence
              </Text>
            )}
            {result.disease.description && (
              <Text style={[styles.diseaseDescription, { color: colors.text }]}>
                {result.disease.description}
              </Text>
            )}
            {result.disease.treatment && (
              <View
                style={[
                  styles.treatmentSection,
                  { borderTopColor: colors.error + "30" },
                ]}
              >
                <Text style={[styles.treatmentTitle, { color: colors.error }]}>
                  Treatment
                </Text>
                <Text
                  style={[styles.diseaseDescription, { color: colors.text }]}
                >
                  {result.disease.treatment}
                </Text>
              </View>
            )}
          </View>
        </View>
      )}

      {result.care && (
        <>
          <View style={sectionStyles.container}>
            <Text
              style={[sectionStyles.title, { color: colors.textSecondary }]}
            >
              Care Instructions
            </Text>
            <CareSection
              title="💧 Watering"
              careStyles={careStyles}
              colors={colors}
            >
              <InfoRow
                label="Frequency"
                value={result.care.watering.frequency}
                infoStyles={infoStyles}
                colors={colors}
              />
              <InfoRow
                label="Amount"
                value={result.care.watering.amount}
                infoStyles={infoStyles}
                colors={colors}
              />
              <InfoRow
                label="Method"
                value={result.care.watering.method}
                infoStyles={infoStyles}
                colors={colors}
              />
            </CareSection>

            <CareSection
              title="☀️ Sunlight"
              careStyles={careStyles}
              colors={colors}
            >
              <InfoRow
                label="Preference"
                value={result.care.sunlight.preference}
                infoStyles={infoStyles}
                colors={colors}
              />
              <InfoRow
                label="Hours"
                value={result.care.sunlight.hours_per_day}
                infoStyles={infoStyles}
                colors={colors}
              />
            </CareSection>

            <CareSection
              title="🌱 Soil"
              careStyles={careStyles}
              colors={colors}
            >
              <InfoRow
                label="Type"
                value={result.care.soil.type}
                infoStyles={infoStyles}
                colors={colors}
              />
              <InfoRow
                label="pH"
                value={result.care.soil.ph}
                infoStyles={infoStyles}
                colors={colors}
              />
              <InfoRow
                label="Drainage"
                value={result.care.soil.drainage}
                infoStyles={infoStyles}
                colors={colors}
              />
            </CareSection>

            <CareSection
              title="🌡 Temperature"
              careStyles={careStyles}
              colors={colors}
            >
              <InfoRow
                label="Range"
                value={formatTemp(result.care.temperature)}
                infoStyles={infoStyles}
                colors={colors}
              />
              {result.care.temperature.frost_tender && (
                <InfoRow
                  label="Frost"
                  value="Tender"
                  infoStyles={infoStyles}
                  colors={colors}
                />
              )}
            </CareSection>

            <CareSection
              title="📏 Growth"
              careStyles={careStyles}
              colors={colors}
            >
              <InfoRow
                label="Height"
                value={result.care.growth.mature_height}
                infoStyles={infoStyles}
                colors={colors}
              />
              <InfoRow
                label="Spread"
                value={result.care.growth.spread}
                infoStyles={infoStyles}
                colors={colors}
              />
              <InfoRow
                label="Rate"
                value={result.care.growth.growth_rate}
                infoStyles={infoStyles}
                colors={colors}
              />
              <InfoRow
                label="Bloom"
                value={result.care.growth.bloom_season}
                infoStyles={infoStyles}
                colors={colors}
              />
            </CareSection>
          </View>

          <View style={styles.speciesLinkContainer}>
            <Button
              title="View Species Details →"
              onPress={() => {
                const name = encodeURIComponent(best.species.scientific_name);
                router.push(`/species/${name}` as any);
              }}
              variant="ghost"
              style={styles.speciesLink}
            />
          </View>
        </>
      )}

      {result.cached && (
        <View style={styles.cacheBadge}>
          <Text style={[styles.cacheText, { color: colors.textTertiary }]}>
            Cached result
          </Text>
        </View>
      )}
    </ScrollView>
  );
}

function getConfidenceColor(score: number, colors: ThemeColors): string {
  if (score >= 0.8) return colors.confidenceHigh;
  if (score >= 0.5) return colors.confidenceMedium;
  return colors.confidenceLow;
}

function formatTemp(temp: {
  min_fahrenheit: number | null;
  max_fahrenheit: number | null;
  notes: string;
}): string {
  if (temp.min_fahrenheit && temp.max_fahrenheit) {
    return `${temp.min_fahrenheit}°F - ${temp.max_fahrenheit}°F`;
  }
  if (temp.notes) return temp.notes;
  return "—";
}

function CareSection({
  title,
  children,
  careStyles,
  colors,
}: {
  title: string;
  children: React.ReactNode;
  careStyles: any;
  colors: ThemeColors;
}) {
  return (
    <View style={[careStyles.container, { backgroundColor: colors.surface }]}>
      <Text style={[careStyles.title, { color: colors.text }]}>{title}</Text>
      {children}
    </View>
  );
}

function InfoRow({
  label,
  value,
  italic,
  infoStyles,
  colors,
}: {
  label: string;
  value: string;
  italic?: boolean;
  infoStyles: any;
  colors: ThemeColors;
}) {
  if (!value || value === "—") return null;
  return (
    <View style={infoStyles.row}>
      <Text style={[infoStyles.label, { color: colors.textSecondary }]}>
        {label}
      </Text>
      <Text
        style={[
          infoStyles.value,
          { color: colors.text },
          italic && { fontStyle: "italic" },
        ]}
      >
        {value}
      </Text>
    </View>
  );
}

function makeStyles(c: ThemeColors) {
  return StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: c.background,
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
      gap: spacing.md,
    },
    header: {
      alignItems: "center",
      marginBottom: spacing.xl,
    },
    speciesName: {
      ...typography.h1,
      textAlign: "center",
    },
    scientificName: {
      ...typography.body,
      fontStyle: "italic",
      marginTop: spacing.xs,
    },
    confidenceRow: {
      flexDirection: "row",
      alignItems: "center",
      gap: spacing.sm,
      marginTop: spacing.md,
    },
    confidenceBadge: {
      paddingHorizontal: spacing.md,
      paddingVertical: spacing.xs,
      borderRadius: borderRadius.full,
    },
    confidenceScore: {
      ...typography.label,
      fontWeight: "700",
    },
    sourceLabel: {
      ...typography.caption,
    },
    actionRow: {
      flexDirection: "row",
      gap: spacing.sm,
      marginTop: spacing.md,
    },
    actionButton: {
      paddingHorizontal: spacing.md,
    },
    diseaseCard: {
      borderRadius: borderRadius.md,
      padding: spacing.md,
    },
    diseaseName: {
      ...typography.h3,
    },
    diseaseConfidence: {
      ...typography.bodySmall,
      marginTop: spacing.xs,
    },
    diseaseDescription: {
      ...typography.body,
      marginTop: spacing.sm,
    },
    treatmentSection: {
      marginTop: spacing.md,
      paddingTop: spacing.md,
      borderTopWidth: 1,
    },
    treatmentTitle: {
      ...typography.label,
      marginBottom: spacing.xs,
    },
    speciesLinkContainer: {
      alignItems: "center",
      marginTop: spacing.md,
    },
    speciesLink: {
      width: "100%",
    },
    cacheBadge: {
      alignItems: "center",
      marginTop: spacing.md,
    },
    cacheText: {
      ...typography.caption,
    },
    noResultIcon: {
      fontSize: 64,
      marginBottom: spacing.md,
    },
    noResultTitle: {
      ...typography.h2,
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
  });
}

function makeCareStyles(c: ThemeColors) {
  return StyleSheet.create({
    container: {
      borderRadius: borderRadius.md,
      padding: spacing.md,
      marginBottom: spacing.sm,
    },
    title: {
      ...typography.h3,
      marginBottom: spacing.sm,
    },
  });
}

function makeInfoStyles(c: ThemeColors) {
  return StyleSheet.create({
    row: {
      flexDirection: "row",
      justifyContent: "space-between",
      paddingVertical: 4,
    },
    label: {
      ...typography.bodySmall,
      flex: 1,
    },
    value: {
      ...typography.bodySmall,
      flex: 1.5,
      textAlign: "right",
    },
  });
}
