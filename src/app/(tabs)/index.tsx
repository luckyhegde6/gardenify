import { useState, useCallback } from "react"
import {
  View,
  Text,
  Image,
  StyleSheet,
  ScrollView,
  Alert,
} from "react-native"
import { router } from "expo-router"
import * as Haptics from "expo-haptics"
import { supabase } from "@/lib/supabase"
import { useCamera } from "@/hooks/use-camera"
import { useIdentification } from "@/hooks/use-identification"
import { useAuth } from "@/hooks/use-auth"
import { Button } from "@/components/button"
import { Loading } from "@/components/loading"
import { colors, spacing, borderRadius, typography } from "@/constants/theme"
import type { OrganType } from "@/lib/types"

const ORGAN_OPTIONS: { label: string; value: OrganType }[] = [
  { label: "Auto", value: "auto" },
  { label: "Leaf", value: "leaf" },
  { label: "Flower", value: "flower" },
  { label: "Fruit", value: "fruit" },
  { label: "Bark", value: "bark" },
]

export default function ScanScreen() {
  const camera = useCamera({ quality: 0.8 })
  const identification = useIdentification()
  const { user } = useAuth()
  const [selectedOrgan, setSelectedOrgan] = useState<OrganType>("auto")

  const handleIdentify = useCallback(async () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium)
    if (!camera.image) {
      Alert.alert("No Image", "Take a photo or pick one from your gallery first")
      return
    }

    try {
      const result = await identification.identify(
        [{ uri: camera.image.uri }],
        { organs: [selectedOrgan] }
      )
      const best = result.results?.[0]

      if (!best) {
        Alert.alert(
          "No Match",
          "Could not identify the plant. Try a clearer photo of a leaf, flower, or fruit."
        )
        return
      }

      if (user) {
        const { data: inserted, error } = await supabase
          .from("identifications")
          .insert({
            user_id: user.id,
            image_urls: [camera.image.uri],
            best_match: result.best_match || "Unknown",
            score: best?.score ?? 0,
            species_scientific_name: best?.species?.scientific_name || result.best_match || "Unknown",
            species_common_names: best?.species?.common_names || [],
            species_family: best?.species?.family || "",
            species_genus: best?.species?.genus || "",
            organs: [selectedOrgan],
            results_json: JSON.stringify(result),
          })
          .select("id")
          .single()

        if (error) throw error
        if (inserted?.id) {
          router.push(`/identification/${inserted.id}` as any)
          return
        }
      }

      if (result.identification_id) {
        router.push(`/identification/${result.identification_id}` as any)
      }
    } catch {
      Alert.alert(
        "Identification Failed",
        "Could not identify the plant. Please try again with a clearer photo."
      )
    }
  }, [camera.image, selectedOrgan, identification, user])

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
    >
      <View style={styles.header}>
        <Text style={styles.appName}>Gardenify</Text>
        <Text style={styles.tagline}>Identify any plant in seconds</Text>
      </View>

      <View style={styles.imageContainer}>
        {camera.image ? (
          <Image source={{ uri: camera.image.uri }} style={styles.image} />
        ) : (
          <View style={styles.imagePlaceholder}>
            <Text style={styles.placeholderIcon}>🌿</Text>
            <Text style={styles.placeholderText}>
              Take a photo or pick from gallery
            </Text>
          </View>
        )}
      </View>

      <View style={styles.actions}>
        <View style={styles.buttonRow}>
          <Button
            title="📷 Camera"
            onPress={() => { Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light); camera.takePhoto() }}
            variant="primary"
            style={styles.actionButton}
            loading={camera.loading}
          />
          <Button
            title="🖼 Gallery"
            onPress={() => { Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light); camera.pickFromGallery() }}
            variant="outline"
            style={styles.actionButton}
            loading={camera.loading}
          />
        </View>

        {camera.image && (
          <>
            <Text style={styles.organLabel}>Plant Organ</Text>
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
                title={identification.loading ? "Identifying..." : "🌱 Identify Plant"}
                onPress={handleIdentify}
                variant="secondary"
                size="lg"
                loading={identification.loading}
                style={styles.identifyButton}
              />
              <Button
                title="Clear"
                onPress={() => { Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light); camera.clearImage() }}
                variant="ghost"
                style={styles.clearButton}
              />
            </View>
          </>
        )}
      </View>

      {identification.loading && (
        <Loading message="Analyzing plant..." />
      )}
    </ScrollView>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
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
    color: colors.primary,
  },
  tagline: {
    ...typography.body,
    color: colors.textSecondary,
  },
  imageContainer: {
    marginBottom: spacing.lg,
  },
  image: {
    width: "100%",
    aspectRatio: 1,
    borderRadius: borderRadius.lg,
    backgroundColor: colors.borderLight,
  },
  imagePlaceholder: {
    width: "100%",
    aspectRatio: 1,
    borderRadius: borderRadius.lg,
    backgroundColor: colors.borderLight,
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 2,
    borderColor: colors.border,
    borderStyle: "dashed",
  },
  placeholderIcon: {
    fontSize: 64,
    marginBottom: spacing.md,
  },
  placeholderText: {
    ...typography.body,
    color: colors.textTertiary,
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
    color: colors.text,
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
})
