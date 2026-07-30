import { useState, useEffect, useCallback } from "react";
import {
  View,
  Text,
  FlatList,
  TextInput,
  TouchableOpacity,
  Alert,
  StyleSheet,
  ActivityIndicator,
} from "react-native";
import { useAuth } from "@/hooks/use-auth";
import { apiClient } from "@/lib/api-client";
import type { AdminUser } from "@/lib/types";
import { spacing, borderRadius, typography } from "@/constants/theme";
import { useTheme } from "@/hooks/use-theme";

export default function AdminScreen() {
  const { session, isAdmin, loading: authLoading } = useAuth();
  const { colors } = useTheme();
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  const fetchUsers = useCallback(async () => {
    if (!session?.access_token) return;
    setLoading(true);
    try {
      const resp = await apiClient.adminGetUsers(
        session.access_token,
        0,
        20,
        search || undefined,
      );
      setUsers(resp.users);
      setTotal(resp.total);
    } catch (e) {
      Alert.alert(
        "Error",
        e instanceof Error ? e.message : "Failed to load users",
      );
    } finally {
      setLoading(false);
    }
  }, [session?.access_token, search]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  const toggleAdmin = async (user: AdminUser) => {
    if (!session?.access_token) return;
    try {
      await apiClient.adminUpdateUser(session.access_token, user.id, {
        is_admin: !user.is_admin,
      });
      fetchUsers();
    } catch (e) {
      Alert.alert("Error", e instanceof Error ? e.message : "Update failed");
    }
  };

  const changeTier = (user: AdminUser) => {
    const tiers = ["free", "pro", "premium"];
    const current = tiers.indexOf(user.subscription_tier);
    const next = tiers[(current + 1) % tiers.length];
    Alert.alert("Change Tier", `Set ${user.email} to ${next}?`, [
      { text: "Cancel", style: "cancel" },
      {
        text: "Change",
        onPress: async () => {
          if (!session?.access_token) return;
          try {
            await apiClient.adminUpdateUser(session.access_token, user.id, {
              subscription_tier: next,
            });
            fetchUsers();
          } catch (e) {
            Alert.alert(
              "Error",
              e instanceof Error ? e.message : "Update failed",
            );
          }
        },
      },
    ]);
  };

  const deleteUser = (user: AdminUser) => {
    Alert.alert(
      "Delete User",
      `Deactivate ${user.email}? This cannot be undone.`,
      [
        { text: "Cancel", style: "cancel" },
        {
          text: "Delete",
          style: "destructive",
          onPress: async () => {
            if (!session?.access_token) return;
            try {
              await apiClient.adminDeleteUser(session.access_token, user.id);
              fetchUsers();
            } catch (e) {
              Alert.alert(
                "Error",
                e instanceof Error ? e.message : "Delete failed",
              );
            }
          },
        },
      ],
    );
  };

  if (authLoading)
    return (
      <ActivityIndicator
        style={[styles.centered, { backgroundColor: colors.background }]}
      />
    );
  if (!isAdmin) {
    return (
      <View style={[styles.centered, { backgroundColor: colors.background }]}>
        <Text style={[styles.errorText, { color: colors.error }]}>
          Access Denied
        </Text>
      </View>
    );
  }

  return (
    <View style={[styles.container, { backgroundColor: colors.background }]}>
      <Text style={[styles.title, { color: colors.text }]}>
        User Management ({total})
      </Text>
      <TextInput
        style={[
          styles.searchInput,
          {
            backgroundColor: colors.surface,
            color: colors.text,
          },
        ]}
        placeholder="Search by email..."
        placeholderTextColor={colors.textTertiary}
        value={search}
        onChangeText={setSearch}
        onSubmitEditing={fetchUsers}
      />
      <FlatList
        data={users}
        keyExtractor={(u) => u.id}
        refreshing={loading}
        onRefresh={fetchUsers}
        renderItem={({ item }) => (
          <View style={[styles.card, { backgroundColor: colors.surface }]}>
            <View style={styles.cardHeader}>
              <Text style={[styles.email, { color: colors.text, flex: 1 }]}>
                {item.email}
              </Text>
              <Text
                style={[
                  styles.tier,
                  {
                    color: colors.primary,
                    backgroundColor: colors.primaryLight,
                  },
                ]}
              >
                {item.subscription_tier}
              </Text>
            </View>
            <Text style={[styles.meta, { color: colors.textSecondary }]}>
              Full name: {item.full_name || "—"}
            </Text>
            <Text style={[styles.meta, { color: colors.textSecondary }]}>
              Admin: {item.is_admin ? "Yes" : "No"} | Since:{" "}
              {item.created_at.slice(0, 10)}
            </Text>
            <View style={styles.actions}>
              <TouchableOpacity
                style={[
                  styles.actionBtn,
                  { backgroundColor: colors.primaryLight },
                ]}
                onPress={() => toggleAdmin(item)}
              >
                <Text style={[styles.actionText, { color: colors.primary }]}>
                  {item.is_admin ? "Revoke Admin" : "Make Admin"}
                </Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[
                  styles.actionBtn,
                  { backgroundColor: colors.primaryLight },
                ]}
                onPress={() => changeTier(item)}
              >
                <Text style={[styles.actionText, { color: colors.primary }]}>
                  Change Tier
                </Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[
                  styles.actionBtn,
                  styles.deleteBtn,
                  { backgroundColor: colors.errorLight },
                ]}
                onPress={() => deleteUser(item)}
              >
                <Text
                  style={[
                    styles.actionText,
                    styles.deleteText,
                    { color: colors.error },
                  ]}
                >
                  Delete
                </Text>
              </TouchableOpacity>
            </View>
          </View>
        )}
        ListEmptyComponent={
          <Text style={[styles.empty, { color: colors.textTertiary }]}>
            No users found
          </Text>
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: spacing.md },
  centered: { flex: 1, alignItems: "center", justifyContent: "center" },
  errorText: { ...typography.h3 },
  title: { ...typography.h2, marginBottom: spacing.md },
  searchInput: {
    borderRadius: borderRadius.md,
    padding: spacing.sm,
    ...typography.body,
    marginBottom: spacing.md,
  },
  card: {
    borderRadius: borderRadius.md,
    padding: spacing.md,
    marginBottom: spacing.sm,
  },
  cardHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: spacing.xs,
  },
  email: { ...typography.body, fontWeight: "600" },
  tier: {
    ...typography.label,
    paddingHorizontal: spacing.sm,
    borderRadius: borderRadius.sm,
    overflow: "hidden",
  },
  meta: { ...typography.caption, marginBottom: 2 },
  actions: { flexDirection: "row", gap: spacing.sm, marginTop: spacing.sm },
  actionBtn: {
    paddingVertical: spacing.xs,
    paddingHorizontal: spacing.md,
    borderRadius: borderRadius.sm,
  },
  actionText: { ...typography.label, fontSize: 12 },
  deleteBtn: {},
  deleteText: {},
  empty: { ...typography.body, textAlign: "center", marginTop: spacing.xl },
});
