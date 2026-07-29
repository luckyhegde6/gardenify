module.exports = {
  preset: "jest-expo",
  transformIgnorePatterns: [
    "node_modules/(?!(react-native|@react-native|@react-navigation|expo.*|@expo.*|@supabase.*)/)",
  ],
  moduleNameMapper: {
    "^@/(.*)$": "<rootDir>/src/$1",
    "^@/assets/(.*)$": "<rootDir>/assets/$1",
    "^@react-native-async-storage/async-storage$": "<rootDir>/__mocks__/async-storage.js",
  },
  moduleFileExtensions: ["ts", "tsx", "js", "jsx", "json"],
  collectCoverageFrom: [
    "src/**/*.{ts,tsx}",
    "!src/**/*.d.ts",
    "!src/app/**",
    "!src/types/**",
  ],
  testMatch: ["**/__tests__/**/*.test.{ts,tsx}"],
}
