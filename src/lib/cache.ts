import AsyncStorage from "@react-native-async-storage/async-storage"
import type { IdentificationResponse } from "@/lib/types"

const CACHE_PREFIX = "gardenify:identify:"
const CACHE_TTL_MS = 24 * 60 * 60 * 1000

interface CacheEntry {
  data: IdentificationResponse
  timestamp: number
}

export const resultCache = {
  async get(key: string): Promise<IdentificationResponse | null> {
    try {
      const raw = await AsyncStorage.getItem(CACHE_PREFIX + key)
      if (!raw) return null

      const entry: CacheEntry = JSON.parse(raw)
      const age = Date.now() - entry.timestamp

      if (age > CACHE_TTL_MS) {
        await AsyncStorage.removeItem(CACHE_PREFIX + key)
        return null
      }

      return entry.data
    } catch {
      return null
    }
  },

  async set(key: string, data: IdentificationResponse): Promise<void> {
    try {
      const entry: CacheEntry = { data, timestamp: Date.now() }
      await AsyncStorage.setItem(CACHE_PREFIX + key, JSON.stringify(entry))
    } catch {
      // Silently fail on cache write errors
    }
  },

  async getRecent(limit = 10): Promise<IdentificationResponse[]> {
    try {
      const keys = await AsyncStorage.getAllKeys()
      const cacheKeys = keys.filter((k) => k.startsWith(CACHE_PREFIX))
      cacheKeys.sort()

      const recent: IdentificationResponse[] = []
      for (const key of cacheKeys.slice(-limit)) {
        const raw = await AsyncStorage.getItem(key)
        if (!raw) continue
        try {
          const entry: CacheEntry = JSON.parse(raw)
          if (Date.now() - entry.timestamp <= CACHE_TTL_MS) {
            recent.push(entry.data)
          }
        } catch {}
      }
      return recent.reverse()
    } catch {
      return []
    }
  },

  async clear(): Promise<void> {
    try {
      const keys = await AsyncStorage.getAllKeys()
      const cacheKeys = keys.filter((k) => k.startsWith(CACHE_PREFIX))
      await AsyncStorage.multiRemove(cacheKeys)
    } catch {}
  },
}
