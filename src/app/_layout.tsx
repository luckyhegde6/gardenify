import { useEffect, useState } from "react";
import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { AuthProvider, useAuth } from "@/hooks/use-auth";
import { ThemeProvider, useTheme } from "@/hooks/use-theme";
import { Loading } from "@/components/loading";

function RootNavigator() {
  const { loading } = useAuth();
  const { colors, isDark } = useTheme();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (!loading) setReady(true);
  }, [loading]);

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
