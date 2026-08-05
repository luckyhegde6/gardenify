import { useEffect, useState } from "react";
import { Stack, useRouter, useSegments } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { AuthProvider, useAuth } from "@/hooks/use-auth";
import { ThemeProvider, useTheme } from "@/hooks/use-theme";
import { Loading } from "@/components/loading";

function RootNavigator() {
  const { user, loading } = useAuth();
  const { colors, isDark } = useTheme();
  const [ready, setReady] = useState(false);
  const segments = useSegments();
  const router = useRouter();

  useEffect(() => {
    if (!loading) setReady(true);
  }, [loading]);

  useEffect(() => {
    if (loading) return;
    const inAuthGroup = segments[0] === "(auth)";
    const onResetScreen = segments.join("/").includes("reset-password");
    if (!user && !inAuthGroup) {
      router.replace("/(auth)/login");
    } else if (user && inAuthGroup && !onResetScreen) {
      router.replace("/(tabs)");
    }
  }, [user, loading, segments, router]);

  if (!ready) return <Loading message="Loading..." />;

  return (
    <>
      <StatusBar style={isDark ? "light" : "dark"} />
      <Stack screenOptions={{ headerShown: false }}>
        <Stack.Screen name="index" options={{ headerShown: false }} />
        <Stack.Screen name="(auth)" options={{ headerShown: false }} />
        <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
        <Stack.Screen
          name="identification/[id]"
          options={{
            headerShown: true,
            headerTitle: "Identification",
            headerTintColor: colors.text,
            headerStyle: { backgroundColor: colors.background },
            presentation: "card",
          }}
        />
        <Stack.Screen
          name="species/[name]"
          options={{
            headerShown: true,
            headerTitle: "Species Details",
            headerTintColor: colors.text,
            headerStyle: { backgroundColor: colors.background },
            presentation: "card",
          }}
        />
        <Stack.Screen
          name="admin"
          options={{
            headerShown: true,
            headerTitle: "Admin",
            headerTintColor: colors.text,
            headerStyle: { backgroundColor: colors.background },
            presentation: "card",
          }}
        />
      </Stack>
    </>
  );
}

export default function RootLayout() {
  return (
    <AuthProvider>
      <ThemeProvider>
        <RootNavigator />
      </ThemeProvider>
    </AuthProvider>
  );
}
