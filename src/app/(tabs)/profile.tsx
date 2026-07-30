import { View, Text, StyleSheet, Alert, TouchableOpacity } from "react-native";
import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/button";
import { spacing, borderRadius, typography } from "@/constants/theme";
import { useTheme, useThemedStyles } from "@/hooks/use-theme";
import type { ThemeColors } from "@/hooks/use-theme";
import { router } from "expo-router";

export default function ProfileScreen() {
  const { user, signOut, isAdmin } = useAuth();
  const { colors, theme, toggleTheme } = useTheme();
  const styles = useThemedStyles(makeStyles);

  const handleSignOut = () => {
    Alert.alert("Sign Out", "Are you sure you want to sign out?", [
      { text: "Cancel", style: "cancel" },
      {
        text: "Sign Out",
        style: "destructive",
        onPress: async () => {
          try {
            await signOut();
          } catch (err) {
            Alert.alert(
              "Error",
              err instanceof Error ? err.message : "Failed to sign out",
            );
          }
        },
      },
    ]);
  };

  return (
    <View style={[styles.container, { backgroundColor: colors.background }]}>
      <View style={styles.header}>
        <View style={[styles.avatar, { backgroundColor: colors.primary }]}>
          <Text style={[styles.avatarText, { color: colors.textInverse }]}>
            {user?.email?.charAt(0).toUpperCase() ?? "?"}
          </Text>
        </View>
        <Text style={[styles.email, { color: colors.text }]}>
          {user?.email ?? "Unknown"}
        </Text>
      </View>

      <View style={styles.section}>
        <Text style={[styles.sectionTitle, { color: colors.textSecondary }]}>
          Account
        </Text>
        <View style={[styles.card, { backgroundColor: colors.surface }]}>
          <View style={styles.row}>
            <Text style={[styles.rowLabel, { color: colors.text }]}>Email</Text>
            <Text style={[styles.rowValue, { color: colors.textSecondary }]}>
              {user?.email}
            </Text>
          </View>
          <View style={[styles.divider, { backgroundColor: colors.divider }]} />
          <View style={styles.row}>
            <Text style={[styles.rowLabel, { color: colors.text }]}>
              User ID
            </Text>
            <Text
              style={[styles.rowValue, { color: colors.textSecondary }]}
              numberOfLines={1}
            >
              {user?.id.slice(0, 12)}...
            </Text>
          </View>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={[styles.sectionTitle, { color: colors.textSecondary }]}>
          Settings
        </Text>
        <View style={[styles.card, { backgroundColor: colors.surface }]}>
          <View style={styles.row}>
            <Text style={[styles.rowLabel, { color: colors.text }]}>
              Language
            </Text>
            <Text style={[styles.rowValue, { color: colors.textSecondary }]}>
              English
            </Text>
          </View>
          <View style={[styles.divider, { backgroundColor: colors.divider }]} />
          <TouchableOpacity style={styles.row} onPress={toggleTheme}>
            <Text style={[styles.rowLabel, { color: colors.text }]}>Theme</Text>
            <Text style={[styles.rowValue, { color: colors.primary }]}>
              {theme === "dark" ? "🌙 Dark" : "☀️ Light"}
            </Text>
          </TouchableOpacity>
        </View>
      </View>

      {isAdmin && (
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.textSecondary }]}>
            Admin
          </Text>
          <TouchableOpacity
            style={[styles.card, { backgroundColor: colors.surface }]}
            onPress={() => router.push("/admin")}
          >
            <View style={styles.row}>
              <Text style={[styles.rowLabel, { color: colors.text }]}>
                User Management
              </Text>
              <Text style={[styles.chevron, { color: colors.textSecondary }]}>
                ›
              </Text>
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

      <Text style={[styles.version, { color: colors.textTertiary }]}>
        Gardenify v1.0.0
      </Text>
    </View>
  );
}

function makeStyles(c: ThemeColors) {
  return StyleSheet.create({
    container: {
      flex: 1,
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
      alignItems: "center",
      justifyContent: "center",
      marginBottom: spacing.md,
    },
    avatarText: {
      fontSize: 32,
      fontWeight: "700",
    },
    email: {
      ...typography.h3,
    },
    section: {
      paddingHorizontal: spacing.lg,
      marginBottom: spacing.lg,
    },
    sectionTitle: {
      ...typography.label,
      textTransform: "uppercase",
      marginBottom: spacing.sm,
    },
    card: {
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
    },
    rowValue: {
      ...typography.body,
      maxWidth: "60%",
      textAlign: "right",
    },
    chevron: {
      ...typography.body,
      fontSize: 20,
    },
    divider: {
      height: 1,
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
      textAlign: "center",
      marginTop: spacing.lg,
      marginBottom: spacing.xl,
    },
  });
}
