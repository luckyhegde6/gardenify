import { useState } from "react";
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  TouchableOpacity,
  Alert,
} from "react-native";
import { router } from "expo-router";
import { apiClient } from "@/lib/api-client";
import { Button } from "@/components/button";
import { spacing, borderRadius, typography } from "@/constants/theme";
import { useTheme } from "@/hooks/use-theme";

export default function ForgotPasswordScreen() {
  const { colors } = useTheme();
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!email.trim()) {
      Alert.alert("Error", "Please enter your email address");
      return;
    }
    setLoading(true);
    try {
      await apiClient.forgotPassword(email.trim());
      Alert.alert(
        "Reset Link Sent",
        "If an account exists for that email, a password reset link was sent. " +
          "While a reset is pending, you cannot request another one until it is completed.",
        [{ text: "OK", onPress: () => router.back() }],
      );
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to send reset link";
      Alert.alert("Could Not Send Reset Link", message);
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
          Reset Password
        </Text>
        <Text style={[styles.subtitle, { color: colors.textSecondary }]}>
          Enter your account email and we will send you a recovery link to set a
          new password.
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

          <Button
            title="Send Reset Link"
            onPress={handleSend}
            loading={loading}
            size="lg"
            style={styles.submitButton}
          />
        </View>

        <TouchableOpacity
          style={styles.backButton}
          onPress={() => router.back()}
        >
          <Text style={[styles.backText, { color: colors.primary }]}>
            Back to Login
          </Text>
        </TouchableOpacity>
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
  form: {
    borderRadius: borderRadius.xl,
    padding: spacing.lg,
  },
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
  backButton: {
    alignSelf: "center",
    marginTop: spacing.lg,
    padding: spacing.xs,
  },
  backText: { ...typography.body, fontWeight: "600" },
});
