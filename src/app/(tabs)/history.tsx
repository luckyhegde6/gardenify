import { useState, useCallback } from "react"
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  RefreshControl,
} from "react-native"
import { router } from "expo-router"
import { supabase } from "@/lib/supabase"
import { useAuth } from "@/hooks/use-auth"
import { PlantCard } from "@/components/plant-card"
import { Loading } from "@/components/loading"
import { Button } from "@/components/button"
import { colors, spacing, typography } from "@/constants/theme"
import type { IdentificationRecord } from "@/lib/types"

export default function HistoryScreen() {
  const { user } = useAuth()
  const [identifications, setIdentifications] = useState<IdentificationRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  const fetchHistory = useCallback(async () => {
    if (!user) return
    try {
      const { data, error } = await supabase
        .from("identifications")
        .select("*")
        .eq("user_id", user.id)
        .order("created_at", { ascending: false })
        .limit(50)

      if (error) throw error
      setIdentifications(data ?? [])
    } catch (err) {
      console.error("Failed to fetch history:", err)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [user])

  const handleRefresh = useCallback(() => {
    setRefreshing(true)
    fetchHistory()
  }, [fetchHistory])

  if (loading) return <Loading message="Loading history..." />

  const renderItem = ({ item }: { item: IdentificationRecord }) => {
    let result: { results?: { score: number; species: { scientific_name: string; common_names: string[] } }[] } | null = null
    try {
      result = JSON.parse(item.results_json)
    } catch {}

    const best = result?.results?.[0]
    const score = best?.score ?? item.confidence
    const commonNames = best?.species?.common_names ?? []
    const imageUrl = item.image_urls?.[0]

    return (
      <PlantCard
        scientificName={item.species_scientific_name}
        commonNames={commonNames.length > 0 ? commonNames : [item.species_common_names]}
        confidence={score}
        imageUrl={imageUrl}
        onPress={() => router.push(`/identification/${item.id}` as any)}
      />
    )
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>History</Text>
        <Text style={styles.subtitle}>
          {identifications.length} identification{identifications.length !== 1 ? "s" : ""}
        </Text>
      </View>

      {identifications.length === 0 ? (
        <View style={styles.empty}>
          <Text style={styles.emptyIcon}>📋</Text>
          <Text style={styles.emptyTitle}>No Identifications Yet</Text>
          <Text style={styles.emptyText}>
            Start by identifying a plant on the Scan tab
          </Text>
          <Button
            title="Scan a Plant"
            onPress={() => router.push("/" as any)}
            style={styles.emptyButton}
          />
        </View>
      ) : (
        <FlatList
          data={identifications}
          renderItem={renderItem}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.list}
          ItemSeparatorComponent={() => <View style={styles.separator} />}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={handleRefresh}
              tintColor={colors.primary}
            />
          }
        />
      )}
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    padding: spacing.lg,
    paddingTop: spacing.xxl,
    paddingBottom: spacing.md,
  },
  title: {
    ...typography.h1,
    color: colors.text,
  },
  subtitle: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  list: {
    padding: spacing.lg,
    paddingTop: 0,
  },
  separator: {
    height: spacing.sm,
  },
  empty: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    padding: spacing.xl,
  },
  emptyIcon: {
    fontSize: 64,
    marginBottom: spacing.md,
  },
  emptyTitle: {
    ...typography.h2,
    color: colors.text,
    marginBottom: spacing.sm,
  },
  emptyText: {
    ...typography.body,
    color: colors.textSecondary,
    textAlign: "center",
    marginBottom: spacing.lg,
  },
  emptyButton: {
    minWidth: 160,
  },
})
