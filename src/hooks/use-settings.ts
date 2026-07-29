import { useState, useEffect, useCallback } from "react"
import { supabase } from "@/lib/supabase"
import { useAuth } from "@/hooks/use-auth"
import type { UserSettings } from "@/lib/types"

const DEFAULT_LANGUAGE = "en"
const SUPPORTED_LANGUAGES = ["en", "fr", "es"]

export function useSettings() {
  const { user } = useAuth()
  const [settings, setSettings] = useState<UserSettings | null>(null)
  const [language, setLanguageState] = useState(DEFAULT_LANGUAGE)
  const [loading, setLoading] = useState(true)

  const fetchSettings = useCallback(async () => {
    if (!user) {
      setLoading(false)
      return
    }
    try {
      const { data, error } = await supabase
        .from("user_settings")
        .select("*")
        .eq("user_id", user.id)
        .single()

      if (error && error.code !== "PGRST116") {
        console.error("Failed to fetch settings:", error)
      }
      if (data) {
        setSettings(data)
        setLanguageState(data.language || DEFAULT_LANGUAGE)
      }
    } finally {
      setLoading(false)
    }
  }, [user])

  const updateLanguage = useCallback(
    async (lang: string) => {
      if (!SUPPORTED_LANGUAGES.includes(lang)) return
      if (!user) return

      setLanguageState(lang)
      try {
        await supabase.from("user_settings").upsert(
          {
            user_id: user.id,
            language: lang,
          },
          { onConflict: "user_id" }
        )
      } catch {
        console.error("Failed to update language setting")
      }
    },
    [user]
  )

  useEffect(() => {
    fetchSettings()
  }, [fetchSettings])

  return {
    settings,
    language,
    loading,
    updateLanguage,
    supportedLanguages: SUPPORTED_LANGUAGES,
  }
}
