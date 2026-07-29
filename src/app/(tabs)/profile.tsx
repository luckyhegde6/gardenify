import { View, Text, StyleSheet, Alert, TouchableOpacity } from "react-native"
import { useAuth } from "@/hooks/use-auth"
import { Button } from "@/components/button"
import { colors, spacing, borderRadius, typography } from "@/constants/theme"
import { router } from "expo-router"

export default function ProfileScreen() {
  const { user, signOut, isAdmin } = useAuth()

  const handleSignOut = () => {
    Alert.alert("Sign Out", "Are you sure you want to sign out?", [
      { text: "Cancel", style: "cancel" },
      {
        text: "Sign Out",
        style: "destructive",
        onPress: async () => {
          try {
            await signOut()
          } catch (err) {
            Alert.alert(
              "Error",
              err instanceof Error ? err.message : "Failed to sign out"
            )
          }
        },
      },
    ])
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View style={styles.avatar}>
          <Text style={styles.avatarText}>
            {user?.email?.charAt(0).toUpperCase() ?? "?"}
          </Text>
        </View>
        <Text style={styles.email}>{user?.email ?? "Unknown"}</Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Account</Text>
        <View style={styles.card}>
          <View style={styles.row}>
            <Text style={styles.rowLabel}>Email</Text>
            <Text style={styles.rowValue}>{user?.email}</Text>
          </View>
          <View style={styles.divider} />
          <View style={styles.row}>
            <Text style={styles.rowLabel}>User ID</Text>
            <Text style={styles.rowValue} numberOfLines={1}>
              {user?.id.slice(0, 12)}...
            </Text>
          </View>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Settings</Text>
        <View style={styles.card}>
          <View style={styles.row}>
            <Text style={styles.rowLabel}>Language</Text>
            <Text style={styles.rowValue}>English</Text>
          </View>
          <View style={styles.divider} />
          <View style={styles.row}>
            <Text style={styles.rowLabel}>Theme</Text>
            <Text style={styles.rowValue}>Light</Text>
          </View>
        </View>
      </View>

      {isAdmin && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Admin</Text>
          <TouchableOpacity
            style={styles.card}
            onPress={() => router.push("/admin")}
          >
            <View style={styles.row}>
              <Text style={styles.rowLabel}>User Management</Text>
              <Text style={styles.chevron}>›</Text>
            </View>
          </TouchableOpacity>
        </View>
      )}

      <View style={styles.signOutContainer}>
        <Button
          title="Sign Out"
          onPress={handleSignOut}
          variant="danger"
          size="lg"
          style={styles.signOutButton}
        />
      </View>

      <Text style={styles.version}>Gardenify v1.0.0</Text>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    alignItems: "center",
    paddingTop: spacing.xxl + 20,
    paddingBottom: spacing.xl,
    paddingHorizontal: spacing.lg,
  },
  avatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: colors.primary,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: spacing.md,
  },
  avatarText: {
    fontSize: 32,
    fontWeight: "700",
    color: colors.textInverse,
  },
  email: {
    ...typography.h3,
    color: colors.text,
  },
  section: {
    paddingHorizontal: spacing.lg,
    marginBottom: spacing.lg,
  },
  sectionTitle: {
    ...typography.label,
    color: colors.textSecondary,
    textTransform: "uppercase",
    marginBottom: spacing.sm,
  },
  card: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.md,
    overflow: "hidden",
  },
  row: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.md - 2,
  },
  rowLabel: {
    ...typography.body,
    color: colors.text,
  },
  rowValue: {
    ...typography.body,
    color: colors.textSecondary,
    maxWidth: "60%",
    textAlign: "right",
  },
  chevron: {
    ...typography.body,
    color: colors.textSecondary,
    fontSize: 20,
  },
  divider: {
    height: 1,
    backgroundColor: colors.divider,
    marginHorizontal: spacing.md,
  },
  signOutContainer: {
    paddingHorizontal: spacing.lg,
    marginTop: spacing.md,
  },
  signOutButton: {
    width: "100%",
  },
  version: {
    ...typography.caption,
    color: colors.textTertiary,
    textAlign: "center",
    marginTop: spacing.lg,
    marginBottom: spacing.xl,
  },
})
