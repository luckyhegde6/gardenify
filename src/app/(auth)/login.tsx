import { useState } from "react"
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  TouchableOpacity,
  Alert,
} from "react-native"
import { router } from "expo-router"
import { useAuth } from "@/hooks/use-auth"
import { Button } from "@/components/button"
import { colors, spacing, borderRadius, typography } from "@/constants/theme"

export default function LoginScreen() {
  const { signIn } = useAuth()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [loading, setLoading] = useState(false)

  const handleLogin = async () => {
    if (!email.trim() || !password.trim()) {
      Alert.alert("Error", "Please enter email and password")
      return
    }
    setLoading(true)
    try {
      await signIn(email.trim(), password)
    } catch (err) {
      Alert.alert(
        "Login Failed",
        err instanceof Error ? err.message : "Invalid credentials"
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === "ios" ? "padding" : "height"}
    >
      <View style={styles.content}>
        <View style={styles.header}>
          <Text style={styles.appName}>Gardenify</Text>
          <Text style={styles.tagline}>Identify any plant in seconds</Text>
        </View>

        <View style={styles.form}>
          <Text style={styles.title}>Welcome Back</Text>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Email</Text>
            <TextInput
              style={styles.input}
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
            <Text style={styles.label}>Password</Text>
            <TextInput
              style={styles.input}
              placeholder="Enter your password"
              placeholderTextColor={colors.textTertiary}
              value={password}
              onChangeText={setPassword}
              secureTextEntry
            />
          </View>

          <Button
            title="Log In"
            onPress={handleLogin}
            loading={loading}
            size="lg"
            style={styles.submitButton}
          />
        </View>

        <View style={styles.footer}>
          <Text style={styles.footerText}>Don{"'"}t have an account? </Text>
          <TouchableOpacity onPress={() => router.push("/register" as any)}>
            <Text style={styles.footerLink}>Sign up</Text>
          </TouchableOpacity>
        </View>
      </View>
    </KeyboardAvoidingView>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
    flex: 1,
    justifyContent: "center",
    paddingHorizontal: spacing.lg,
  },
  header: {
    alignItems: "center",
    marginBottom: spacing.xxl,
  },
  appName: {
    fontSize: 36,
    fontWeight: "800",
    color: colors.primary,
    marginBottom: spacing.xs,
  },
  tagline: {
    ...typography.body,
    color: colors.textSecondary,
  },
  form: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.xl,
    padding: spacing.lg,
  },
  title: {
    ...typography.h2,
    color: colors.text,
    marginBottom: spacing.lg,
  },
  inputGroup: {
    marginBottom: spacing.md,
  },
  label: {
    ...typography.label,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  input: {
    backgroundColor: colors.background,
    borderRadius: borderRadius.sm,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.md - 4,
    fontSize: 16,
    color: colors.text,
    borderWidth: 1,
    borderColor: colors.border,
  },
  submitButton: {
    marginTop: spacing.md,
  },
  footer: {
    flexDirection: "row",
    justifyContent: "center",
    marginTop: spacing.xl,
  },
  footerText: {
    ...typography.body,
    color: colors.textSecondary,
  },
  footerLink: {
    ...typography.body,
    color: colors.primary,
    fontWeight: "600",
  },
})
