import { useState, useCallback } from "react"
import { apiClient } from "@/lib/api-client"
import type {
  IdentificationResponse,
  OrganType,
} from "@/lib/types"

interface IdentifyOptions {
  organs?: OrganType[]
  lang?: string
}

export function useIdentification() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<IdentificationResponse | null>(null)

  const identify = useCallback(
    async (images: { uri: string }[], options: IdentifyOptions = {}) => {
      setLoading(true)
      setError(null)
      setResult(null)
      try {
        const organs = options.organs ?? images.map(() => "auto" as OrganType)
        const lang = options.lang ?? "en"
        const response = await apiClient.identify(images, organs, lang)
        setResult(response)
        return response
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "Identification failed"
        setError(message)
        throw err
      } finally {
        setLoading(false)
      }
    },
    []
  )

  const reset = useCallback(() => {
    setResult(null)
    setError(null)
    setLoading(false)
  }, [])

  return { identify, loading, error, result, reset }
}
