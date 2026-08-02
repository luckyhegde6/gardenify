import { useState, useCallback, useEffect } from "react";
import { View, Text, Image, StyleSheet, ScrollView, Alert } from "react-native";
import { router } from "expo-router";
import * as Haptics from "expo-haptics";
import { supabase } from "@/lib/supabase";
import { useCamera } from "@/hooks/use-camera";
import { useIdentification } from "@/hooks/use-identification";
import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/button";
import { Loading } from "@/components/loading";
import { spacing, borderRadius, typography } from "@/constants/theme";
import { useTheme, useThemedStyles } from "@/hooks/use-theme";
import { offlineQueue } from "@/lib/offline-queue";
import type { OrganType } from "@/lib/types";
import type { ThemeColors } from "@/hooks/use-theme";

const ORGAN_OPTIONS: { label: string; value: OrganType }[] = [
  { label: "Auto", value: "auto" },
  { label: "Leaf", value: "leaf" },
  { label: "Flower", value: "flower" },
  { label: "Fruit", value: "fruit" },
  { label: "Bark", value: "bark" },
];

export default function ScanScreen() {
  const camera = useCamera({ quality: 0.8 });
  const identification = useIdentification();
  const { user } = useAuth();
  const { colors } = useTheme();
  const styles = useThemedStyles(makeStyles);
  const [selectedOrgan, setSelectedOrgan] = useState<OrganType>("auto");

  const handleIdentify = useCallback(async () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    if (!camera.image) {
      Alert.alert(
        "No Image",
        "Take a photo or pick one from your gallery first",
      );
      return;
    }

    try {
      const result = await identification.identify(
        [{ uri: camera.image.uri }],
        { organs: [selectedOrgan] },
      );
      const best = result.results?.[0];

      if (!best) {
        Alert.alert(
          "No Match",
          "Could not identify the plant. Try a clearer photo of a leaf, flower, or fruit.",
        );
        return;
      }

      if (user) {
        const thumbnails =
          result.metadata
            ?.map((m) => m.thumbnail_data_url ?? "")
            .filter(Boolean) ?? [];

        const { data: inserted, error } = await supabase
          .from("identifications")
          .insert({
            user_id: user.id,
            image_urls: [camera.image.uri],
            image_thumbnails: thumbnails,
            best_match: result.best_match || "Unknown",
            score: best?.score ?? 0,
            species_scientific_name:
              best?.species?.scientific_name || result.best_match || "Unknown",
            species_common_names: best?.species?.common_names || [],
            species_family: best?.species?.family || "",
            species_genus: best?.species?.genus || "",
            organs: [selectedOrgan],
            results_json: JSON.stringify(result),
          })
          .select("id")
          .single();

        if (error) throw error;
        if (inserted?.id) {
          router.push(`/identification/${inserted.id}` as any);
          return;
        }
      }

      if (result.identification_id) {
        router.push(`/identification/${result.identification_id}` as any);
      }
    } catch (err) {
      if (err instanceof Error && err.message === "OFFLINE_QUEUED") {
        Alert.alert(
          "Queued for Later",
          "You're offline. Your scan will be processed automatically when you're back online.",
        );
        return;
      }
      Alert.alert(
        "Identification Failed",
        "Could not identify the plant. Please try again with a clearer photo.",
      );
    }
  }, [camera.image, selectedOrgan, identification, user]);

  const [queueCount, setQueueCount] = useState(0);

  useEffect(() => {
    offlineQueue.count().then(setQueueCount);
  }, [identification.queued]);

  return (
    <ScrollView
      style={[styles.container, { backgroundColor: colors.background }]}
      contentContainerStyle={styles.content}
    >
      {!identification.isConnected && (
        <View
          style={[
            styles.offlineBanner,
            { backgroundColor: colors.warningLight },
          ]}
        >
          <Text style={[styles.offlineBannerText, { color: colors.warning }]}>
            You are offline. Scans will be queued and processed later.
          </Text>
        </View>
      )}

      {identification.queued && (
        <View
          style={[styles.queuedBadge, { backgroundColor: colors.infoLight }]}
        >
          <Text style={[styles.queuedBadgeText, { color: colors.info }]}>
            Scan queued for processing when online.
          </Text>
        </View>
      )}

      {queueCount > 0 && (
        <View
          style={[styles.queuedBadge, { backgroundColor: colors.warningLight }]}
        >
          <Text style={[styles.queuedBadgeText, { color: colors.warning }]}>
            {queueCount} scan{queueCount > 1 ? "s" : ""} pending. Reconnect to
            process.
          </Text>
        </View>
      )}

      <View style={styles.header}>
        <Text style={[styles.appName, { color: colors.primary }]}>
          Gardenify
        </Text>
        <Text style={[styles.tagline, { color: colors.textSecondary }]}>
          Identify any plant in seconds
        </Text>
      </View>

      <View style={styles.imageContainer}>
        {camera.image ? (
          <Image source={{ uri: camera.image.uri }} style={styles.image} />
        ) : (
          <View
            style={[
              styles.imagePlaceholder,
              {
                backgroundColor: colors.borderLight,
                borderColor: colors.border,
              },
            ]}
          >
            <Text style={styles.placeholderIcon}>🌿</Text>
            <Text
              style={[styles.placeholderText, { color: colors.textTertiary }]}
            >
              Take a photo or pick from gallery
            </Text>
          </View>
        )}
      </View>

      <View style={styles.actions}>
        <View style={styles.buttonRow}>
          <Button
            title="📷 Camera"
            onPress={() => {
              Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
              camera.takePhoto();
            }}
            variant="primary"
            style={styles.actionButton}
            loading={camera.loading}
          />
          <Button
            title="🖼 Gallery"
            onPress={() => {
              Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
              camera.pickFromGallery();
            }}
            variant="outline"
            style={styles.actionButton}
            loading={camera.loading}
          />
        </View>

        {camera.image && (
          <>
            <Text style={[styles.organLabel, { color: colors.text }]}>
              Plant Organ
            </Text>
            <View style={styles.organRow}>
              {ORGAN_OPTIONS.map((opt) => (
                <Button
                  key={opt.value}
                  title={opt.label}
                  onPress={() => setSelectedOrgan(opt.value)}
                  variant={selectedOrgan === opt.value ? "primary" : "ghost"}
                  size="sm"
                  style={styles.organButton}
                />
              ))}
            </View>

            <View style={styles.identifyRow}>
              <Button
                title={
                  identification.loading
                    ? "Identifying..."
                    : "🌱 Identify Plant"
                }
                onPress={handleIdentify}
                variant="secondary"
                size="lg"
                loading={identification.loading}
                style={styles.identifyButton}
              />
              <Button
                title="Clear"
                onPress={() => {
                  Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
                  camera.clearImage();
                }}
                variant="ghost"
                style={styles.clearButton}
              />
            </View>
          </>
        )}
      </View>

      {identification.loading && <Loading message="Analyzing plant..." />}
    </ScrollView>
  );
}

function makeStyles(c: ThemeColors) {
  return StyleSheet.create({
    container: {
      flex: 1,
    },
    offlineBanner: {
      padding: spacing.sm + 2,
      borderRadius: borderRadius.sm,
      marginBottom: spacing.sm,
      alignItems: "center",
    },
    offlineBannerText: {
      ...typography.caption,
      fontWeight: "600",
      textAlign: "center",
    },
    queuedBadge: {
      padding: spacing.sm + 2,
      borderRadius: borderRadius.sm,
      marginBottom: spacing.sm,
      alignItems: "center",
    },
    queuedBadgeText: {
      ...typography.caption,
      fontWeight: "600",
      textAlign: "center",
    },
    content: {
      padding: spacing.lg,
      paddingTop: spacing.xxl,
    },
    header: {
      alignItems: "center",
      marginBottom: spacing.lg,
    },
    appName: {
      fontSize: 32,
      fontWeight: "800",
    },
    tagline: {
      ...typography.body,
    },
    imageContainer: {
      marginBottom: spacing.lg,
    },
    image: {
      width: "100%",
      aspectRatio: 1,
      borderRadius: borderRadius.lg,
      backgroundColor: c.borderLight,
    },
    imagePlaceholder: {
      width: "100%",
      aspectRatio: 1,
      borderRadius: borderRadius.lg,
      alignItems: "center",
      justifyContent: "center",
      borderWidth: 2,
      borderStyle: "dashed",
    },
    placeholderIcon: {
      fontSize: 64,
      marginBottom: spacing.md,
    },
    placeholderText: {
      ...typography.body,
      textAlign: "center",
    },
    actions: {
      gap: spacing.md,
    },
    buttonRow: {
      flexDirection: "row",
      gap: spacing.sm,
    },
    actionButton: {
      flex: 1,
    },
    organLabel: {
      ...typography.label,
      marginTop: spacing.sm,
    },
    organRow: {
      flexDirection: "row",
      flexWrap: "wrap",
      gap: spacing.xs,
    },
    organButton: {
      paddingHorizontal: spacing.md,
    },
    identifyRow: {
      flexDirection: "row",
      alignItems: "center",
      gap: spacing.sm,
      marginTop: spacing.md,
    },
    identifyButton: {
      flex: 1,
    },
    clearButton: {
      paddingHorizontal: spacing.md,
    },
  });
}
