import { resultCache } from "@/lib/cache"
import type { IdentificationResponse } from "@/lib/types"

const mockResult: IdentificationResponse = {
  best_match: "Rosa damascena",
  results: [
    {
      score: 0.95,
      species: {
        scientific_name: "Rosa damascena",
        common_names: ["Damask Rose", "Rose"],
        family: "Rosaceae",
        genus: "Rosa",
      },
    },
  ],
  disease: null,
  care: null,
  metadata: [],
  remaining_quota: 490,
  version: "1.0",
  cached: false,
  identification_id: "test-123",
  source: "plantnet",
}

describe("resultCache", () => {
  beforeEach(async () => {
    await resultCache.clear()
  })

  describe("set and get", () => {
    it("stores and retrieves a result", async () => {
      await resultCache.set("test-key", mockResult)
      const retrieved = await resultCache.get("test-key")
      expect(retrieved).not.toBeNull()
      expect(retrieved?.best_match).toBe("Rosa damascena")
      expect(retrieved?.results[0].score).toBe(0.95)
    })

    it("returns null for missing key", async () => {
      const result = await resultCache.get("nonexistent")
      expect(result).toBeNull()
    })

    it("overwrites existing key", async () => {
      const updated = { ...mockResult, best_match: "Tulipa gesneriana" }
      await resultCache.set("test-key", mockResult)
      await resultCache.set("test-key", updated)
      const retrieved = await resultCache.get("test-key")
      expect(retrieved?.best_match).toBe("Tulipa gesneriana")
    })
  })

  describe("getRecent", () => {
    it("returns empty array when no entries", async () => {
      const recent = await resultCache.getRecent()
      expect(recent).toEqual([])
    })

    it("returns stored results in reverse order", async () => {
      const first = { ...mockResult, identification_id: "first" }
      const second = { ...mockResult, identification_id: "second" }

      await resultCache.set("key1", first)
      await resultCache.set("key2", second)

      const recent = await resultCache.getRecent(10)
      expect(recent.length).toBe(2)
      expect(recent[0].identification_id).toBe("second")
      expect(recent[1].identification_id).toBe("first")
    })

    it("respects limit parameter", async () => {
      for (let i = 0; i < 5; i++) {
        await resultCache.set(`key${i}`, {
          ...mockResult,
          identification_id: `id-${i}`,
        })
      }

      const recent = await resultCache.getRecent(3)
      expect(recent.length).toBe(3)
    })
  })

  describe("clear", () => {
    it("removes all cached entries", async () => {
      await resultCache.set("key1", mockResult)
      await resultCache.set("key2", mockResult)

      await resultCache.clear()

      const r1 = await resultCache.get("key1")
      const r2 = await resultCache.get("key2")
      expect(r1).toBeNull()
      expect(r2).toBeNull()
    })
  })
})
