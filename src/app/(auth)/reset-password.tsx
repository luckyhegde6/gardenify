import { useState } from "react";
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  Alert,
} from "react-native";
import { router, useLocalSearchParams } from "expo-router";
import { apiClient } from "@/lib/api-client";
import { Button } from "@/components/button";
import { spacing, borderRadius, typography } from "@/constants/theme";
import { useTheme } from "@/hooks/use-theme";

export default function ResetPasswordScreen() {
  const params = useLocalSearchParams<{
    code?: string;
    email?: string;
    token?: string;
    access_token?: string;
  }>();
  // Supabase recovery deep links arrive as `token=...` (verify link) or
  // `access_token=...` (magic-link fragment); accept any of them as the code.
  const code =
    (typeof params.code === "string" ? params.code : "") ||
    (typeof params.token === "string" ? params.token : "") ||
    (typeof params.access_token === "string" ? params.access_token : "") ||
    "";
  const linkEmail = typeof params.email === "string" ? params.email : "";
  const { colors } = useTheme();
  const [email, setEmail] = useState(linkEmail);
  const [newPassword, setNewPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [loading, setLoading] = useState(false);

  const handleReset = async () => {
    if (!email.trim() || !newPassword || !confirm) {
      Alert.alert("Error", "Please fill in all fields");
      return;
    }
    if (newPassword.length < 6) {
      Alert.alert("Error", "Password must be at least 6 characters");
      return;
    }
    if (newPassword !== confirm) {
      Alert.alert("Error", "Passwords do not match");
      return;
    }
    if (!code) {
      Alert.alert("Invalid Link", "This reset link is invalid or has expired.");
      return;
    }
    setLoading(true);
    try {
      await apiClient.resetPassword(email.trim(), code, newPassword);
      Alert.alert(
        "Password Updated",
        "You can now log in with your new password.",
        [{ text: "OK", onPress: () => router.replace("/login" as any) }],
      );
    } catch (err) {
      Alert.alert(
        "Reset Failed",
        err instanceof Error ? err.message : "Could not reset password",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={[styles.container, { backgroundColor: colors.background }]}
      behavior={Platform.OS === "ios" ? "padding" : "height"}
    >
      <View style={styles.content}>
        <Text style={[styles.title, { color: colors.text }]}>
          Choose a New Password
        </Text>
        <Text style={[styles.subtitle, { color: colors.textSecondary }]}>
          Complete the verification by setting a new password for your account.
        </Text>

        <View style={[styles.form, { backgroundColor: colors.surface }]}>
          <View style={styles.inputGroup}>
            <Text style={[styles.label, { color: colors.text }]}>Email</Text>
            <TextInput
              style={[
                styles.input,
                {
                  backgroundColor: colors.background,
                  color: colors.text,
                  borderColor: colors.border,
                },
              ]}
              placeholder="your@email.com"
              placeholderTextColor={colors.textTertiary}
              value={email}
              onChangeText={setEmail}
              keyboardType="email-address"
              autoCapitalize="none"
              autoCorrect={false}
            />
          </View>

          <View style={styles.inputGroup}>
            <Text style={[styles.label, { color: colors.text }]}>
              New Password
            </Text>
            <TextInput
              style={[
                styles.input,
                {
                  backgroundColor: colors.background,
                  color: colors.text,
                  borderColor: colors.border,
                },
              ]}
              placeholder="At least 6 characters"
              placeholderTextColor={colors.textTertiary}
              value={newPassword}
              onChangeText={setNewPassword}
              secureTextEntry
            />
          </View>

          <View style={styles.inputGroup}>
            <Text style={[styles.label, { color: colors.text }]}>
              Confirm Password
            </Text>
            <TextInput
              style={[
                styles.input,
                {
                  backgroundColor: colors.background,
                  color: colors.text,
                  borderColor: colors.border,
                },
              ]}
              placeholder="Re-enter your new password"
              placeholderTextColor={colors.textTertiary}
              value={confirm}
              onChangeText={setConfirm}
              secureTextEntry
            />
          </View>

          <Button
            title="Reset Password"
            onPress={handleReset}
            loading={loading}
            size="lg"
            style={styles.submitButton}
          />
        </View>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  content: {
    flex: 1,
    justifyContent: "center",
    paddingHorizontal: spacing.lg,
  },
  title: { ...typography.h2, marginBottom: spacing.xs },
  subtitle: { ...typography.body, marginBottom: spacing.lg },
  form: { borderRadius: borderRadius.xl, padding: spacing.lg },
  inputGroup: { marginBottom: spacing.md },
  label: { ...typography.label, marginBottom: spacing.xs },
  input: {
    borderRadius: borderRadius.sm,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.md - 4,
    fontSize: 16,
    borderWidth: 1,
  },
  submitButton: { marginTop: spacing.md },
});
