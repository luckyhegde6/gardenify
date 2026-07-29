import { useState, useCallback } from "react"
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  RefreshControl,
  Alert,
} from "react-native"
import { router, useFocusEffect } from "expo-router"
import { supabase } from "@/lib/supabase"
import { useAuth } from "@/hooks/use-auth"
import { Button } from "@/components/button"
import { Loading } from "@/components/loading"
import { colors, spacing, borderRadius, typography } from "@/constants/theme"
import type { Favorite } from "@/lib/types"

export default function FavoritesScreen() {
  const { user } = useAuth()
  const [favorites, setFavorites] = useState<Favorite[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  const fetchFavorites = useCallback(async () => {
    if (!user) return
    try {
      const { data, error } = await supabase
        .from("favorites")
        .select("*")
        .eq("user_id", user.id)
        .order("created_at", { ascending: false })

      if (error) throw error
      setFavorites(data ?? [])
    } catch (err) {
      console.error("Failed to fetch favorites:", err)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [user])

  useFocusEffect(
    useCallback(() => {
      fetchFavorites()
    }, [fetchFavorites])
  )

  const handleRemove = async (fav: Favorite) => {
    Alert.alert(
      "Remove Favorite",
      `Remove ${fav.species_common_name || fav.species_scientific_name} from favorites?`,
      [
        { text: "Cancel", style: "cancel" },
        {
          text: "Remove",
          style: "destructive",
          onPress: async () => {
            try {
              await supabase
                .from("favorites")
                .delete()
                .eq("id", fav.id)
                .eq("user_id", user?.id)
              setFavorites((prev) => prev.filter((f) => f.id !== fav.id))
            } catch {
              Alert.alert("Error", "Could not remove favorite")
            }
          },
        },
      ]
    )
  }

  if (loading) return <Loading message="Loading favorites..." />

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Saved</Text>
        <Text style={styles.subtitle}>
          {favorites.length} saved plant{favorites.length !== 1 ? "s" : ""}
        </Text>
      </View>

      {favorites.length === 0 ? (
        <View style={styles.empty}>
          <Text style={styles.emptyIcon}>❤️</Text>
          <Text style={styles.emptyTitle}>No Saved Plants</Text>
          <Text style={styles.emptyText}>
            Tap the heart icon on any identification result to save it here
          </Text>
          <Button
            title="Identify a Plant"
            onPress={() => router.push("/" as any)}
            style={styles.emptyButton}
          />
        </View>
      ) : (
        <FlatList
          data={favorites}
          renderItem={({ item }) => (
            <View style={styles.card}>
              <View style={styles.cardContent}>
                <Text style={styles.speciesName}>
                  {item.species_common_name || item.species_scientific_name}
                </Text>
                <Text style={styles.cardSubtitle}>
                  {item.species_scientific_name}
                </Text>
                {item.species_family && (
                  <Text style={styles.cardFamily}>{item.species_family}</Text>
                )}
              </View>
              <View style={styles.cardActions}>
                <Button
                  title="View"
                  onPress={() =>
                    router.push(
                      `/species/${encodeURIComponent(item.species_scientific_name)}` as any
                    )
                  }
                  variant="outline"
                  size="sm"
                />
                <Button
                  title="Remove"
                  onPress={() => handleRemove(item)}
                  variant="ghost"
                  size="sm"
                />
              </View>
            </View>
          )}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.list}
          ItemSeparatorComponent={() => <View style={styles.separator} />}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={() => {
                setRefreshing(true)
                fetchFavorites()
              }}
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
  card: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.md,
    padding: spacing.md,
  },
  cardContent: {
    marginBottom: spacing.sm,
  },
  speciesName: {
    ...typography.h3,
    color: colors.text,
  },
  cardSubtitle: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    fontStyle: "italic",
    marginTop: 2,
  },
  cardFamily: {
    ...typography.caption,
    color: colors.textTertiary,
    marginTop: 2,
  },
  cardActions: {
    flexDirection: "row",
    gap: spacing.sm,
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
