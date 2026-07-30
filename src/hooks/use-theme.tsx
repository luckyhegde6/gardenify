import { createContext, useContext, useMemo } from "react";
import { StyleSheet } from "react-native";
import { lightColors, darkColors } from "@/constants/theme";
import { useSettings } from "@/hooks/use-settings";

type Theme = "light" | "dark";
type ThemeColors = typeof lightColors;

interface ThemeState {
  theme: Theme;
  colors: ThemeColors;
  toggleTheme: () => void;
  isDark: boolean;
}

const ThemeContext = createContext<ThemeState | undefined>(undefined);

export function useThemedStyles<T extends StyleSheet.NamedStyles<T>>(
  factory: (colors: ThemeColors) => T,
): T {
  const { colors } = useTheme();
  return useMemo(() => StyleSheet.create(factory(colors)), [colors, factory]);
}

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const { theme, updateTheme, supportedThemes } = useSettings();

  const value = useMemo<ThemeState>(() => {
    const currentTheme: Theme = theme === "dark" ? "dark" : "light";
    return {
      theme: currentTheme,
      colors: currentTheme === "dark" ? darkColors : lightColors,
      toggleTheme: () => {
        const next = currentTheme === "dark" ? "light" : "dark";
        if (supportedThemes.includes(next)) updateTheme(next);
      },
      isDark: currentTheme === "dark",
    };
  }, [theme, updateTheme, supportedThemes]);

  return (
    <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
  );
}

export function useTheme(): ThemeState {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return context;
}

export type { ThemeColors };
