import { useState, useEffect, useCallback } from "react"
import { View, Text, ScrollView, StyleSheet, Linking } from "react-native"
import { useLocalSearchParams } from "expo-router"
import { apiClient } from "@/lib/api-client"
import { Button } from "@/components/button"
import { Loading } from "@/components/loading"
import { colors, spacing, borderRadius, typography } from "@/constants/theme"
import type { SpeciesListItem } from "@/lib/types"

export default function SpeciesDetailScreen() {
  const { name } = useLocalSearchParams<{ name: string }>()
  const [species, setSpecies] = useState<SpeciesListItem | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchSpecies = useCallback(async () => {
    if (!name) return
    setLoading(true)
    setError(null)
    try {
      const decodedName = decodeURIComponent(name)
      const result = await apiClient.getSpeciesByName(decodedName)
      setSpecies(result)
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Species not found"
      )
    } finally {
      setLoading(false)
    }
  }, [name])

  useEffect(() => {
    fetchSpecies()
  }, [fetchSpecies])

  if (loading) return <Loading message="Loading species info..." />
  if (error) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>{error}</Text>
      </View>
    )
  }
  if (!species) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>Species not found</Text>
      </View>
    )
  }

  const commonNames = species.common_names
    ? species.common_names.split(",").map((s) => s.trim())
    : []
  const wikipediaUrl = `https://en.wikipedia.org/wiki/${encodeURIComponent(
    species.scientific_name
  )}`
  const gbifUrl = `https://www.gbif.org/species/search?q=${encodeURIComponent(
    species.scientific_name
  )}`

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <Text style={styles.scientificName}>{species.scientific_name}</Text>
        {commonNames.length > 0 && (
          <Text style={styles.commonNames}>{commonNames.join(", ")}</Text>
        )}
      </View>

      <Section title="Taxonomy">
        <InfoRow label="Family" value={species.family} />
        <InfoRow label="Genus" value={species.genus} />
        <InfoRow label="Scientific Name" value={species.scientific_name} />
      </Section>

      <Section title="External Links">
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
      </Section>

      {species.id > 0 && (
        <Section title="Database Info">
          <InfoRow label="Species ID" value={String(species.id)} />
          <InfoRow label="Database" value="Local Plant Database" />
        </Section>
      )}
    </ScrollView>
  )
}

function Section({
  title,
  children,
}: {
  title: string
  children: React.ReactNode
}) {
  return (
    <View style={sectionStyles.container}>
      <Text style={sectionStyles.title}>{title}</Text>
      <View style={sectionStyles.content}>{children}</View>
    </View>
  )
}

const sectionStyles = StyleSheet.create({
  container: {
    marginBottom: spacing.lg,
  },
  title: {
    ...typography.label,
    color: colors.textSecondary,
    textTransform: "uppercase",
    marginBottom: spacing.sm,
  },
  content: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.md,
    padding: spacing.md,
  },
})

function InfoRow({
  label,
  value,
}: {
  label: string
  value: string
}) {
  if (!value) return null
  return (
    <View style={infoStyles.row}>
      <Text style={infoStyles.label}>{label}</Text>
      <Text style={infoStyles.value}>{value}</Text>
    </View>
  )
}

const infoStyles = StyleSheet.create({
  row: {
    flexDirection: "row",
    justifyContent: "space-between",
    paddingVertical: 6,
  },
  label: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    flex: 1,
  },
  value: {
    ...typography.bodySmall,
    color: colors.text,
    flex: 2,
    textAlign: "right",
  },
})

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
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
    color: colors.text,
    fontStyle: "italic",
  },
  commonNames: {
    ...typography.body,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  linkButton: {
    marginBottom: spacing.sm,
  },
  errorText: {
    ...typography.body,
    color: colors.error,
    textAlign: "center",
  },
})
