jest.mock("@/lib/supabase", () => ({
  supabase: {
    auth: {
      getSession: jest
        .fn()
        .mockResolvedValue({ data: { session: null }, error: null }),
      onAuthStateChange: jest
        .fn()
        .mockReturnValue({
          data: { subscription: { unsubscribe: jest.fn() } },
        }),
      signUp: jest.fn(),
      signInWithPassword: jest.fn(),
      signOut: jest.fn(),
    },
    from: jest.fn().mockReturnValue({
      select: jest.fn().mockReturnThis(),
      insert: jest.fn().mockReturnThis(),
      update: jest.fn().mockReturnThis(),
      delete: jest.fn().mockReturnThis(),
      eq: jest.fn().mockReturnThis(),
      single: jest.fn().mockReturnThis(),
      order: jest.fn().mockReturnThis(),
      limit: jest.fn().mockReturnThis(),
      maybeSingle: jest.fn().mockResolvedValue({ data: null, error: null }),
      upsert: jest.fn().mockResolvedValue({ error: null }),
    }),
  },
}));

jest.mock("@/hooks/use-theme", () => {
  const actual = jest.requireActual("@/constants/theme");
  return {
    useTheme: () => ({
      theme: "light",
      colors: actual.lightColors,
      isDark: false,
      toggleTheme: jest.fn(),
    }),
    useThemedStyles: (factory) => {
      const { StyleSheet } = require("react-native");
      return StyleSheet.create(factory(actual.lightColors));
    },
    ThemeProvider: ({ children }) => children,
  };
});
