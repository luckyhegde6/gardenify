import { colors, spacing, borderRadius, typography } from "@/constants/theme"

describe("theme", () => {
  describe("colors", () => {
    it("has primary color defined", () => {
      expect(colors.primary).toBeDefined()
      expect(colors.primary).toBe("#208AEF")
    })

    it("has all required color keys", () => {
      const requiredKeys = [
        "primary",
        "secondary",
        "background",
        "surface",
        "text",
        "textSecondary",
        "error",
        "success",
        "warning",
      ]
      for (const key of requiredKeys) {
        expect(colors).toHaveProperty(key)
      }
    })

    it("has valid hex colors", () => {
      const hexRegex = /^#[0-9A-Fa-f]{6}$/
      for (const value of Object.values(colors)) {
        if (typeof value === "string") {
          expect(value).toMatch(hexRegex)
        }
      }
    })
  })

  describe("spacing", () => {
    it("has all spacing values", () => {
      expect(spacing.xs).toBe(4)
      expect(spacing.sm).toBe(8)
      expect(spacing.md).toBe(16)
      expect(spacing.lg).toBe(24)
      expect(spacing.xl).toBe(32)
      expect(spacing.xxl).toBe(48)
    })

    it("values increase monotonically", () => {
      const values = Object.values(spacing)
      for (let i = 1; i < values.length; i++) {
        expect(values[i]).toBeGreaterThan(values[i - 1])
      }
    })
  })

  describe("borderRadius", () => {
    it("has all border radius values", () => {
      expect(borderRadius.sm).toBe(8)
      expect(borderRadius.md).toBe(12)
      expect(borderRadius.lg).toBe(16)
      expect(borderRadius.xl).toBe(24)
      expect(borderRadius.full).toBe(9999)
    })
  })

  describe("typography", () => {
    it("has all typography styles", () => {
      expect(typography).toHaveProperty("h1")
      expect(typography).toHaveProperty("h2")
      expect(typography).toHaveProperty("h3")
      expect(typography).toHaveProperty("body")
      expect(typography).toHaveProperty("bodySmall")
      expect(typography).toHaveProperty("caption")
      expect(typography).toHaveProperty("label")
      expect(typography).toHaveProperty("button")
    })

    it("each style has required font properties", () => {
      for (const [name, style] of Object.entries(typography)) {
        expect(style).toHaveProperty("fontSize")
        expect(style).toHaveProperty("fontWeight")
        expect(style).toHaveProperty("lineHeight")
      }
    })

    it("heading sizes decrease appropriately", () => {
      expect(typography.h1.fontSize).toBeGreaterThan(typography.h2.fontSize)
      expect(typography.h2.fontSize).toBeGreaterThan(typography.h3.fontSize)
    })
  })
})
