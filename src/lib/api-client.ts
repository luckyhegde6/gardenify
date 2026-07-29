import type {
  IdentificationResponse,
  SpeciesSearchResponse,
  SpeciesListItem,
} from "@/lib/types"

const API_URL =
  process.env.EXPO_PUBLIC_API_URL ?? "http://localhost:8000/api"

type UploadImage = {
  uri: string
  name?: string
  type?: string
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const body = await response.text()
    let message = `HTTP ${response.status}`
    try {
      const parsed = JSON.parse(body)
      message = parsed.detail ?? message
    } catch {}
    throw new Error(message)
  }
  return response.json() as Promise<T>
}

export const apiClient = {
  async identify(
    images: UploadImage[],
    organs: string[] = ["auto"],
    lang: string = "en"
  ): Promise<IdentificationResponse> {
    const formData = new FormData()
    for (let i = 0; i < images.length; i++) {
      const img = images[i]
      formData.append("images", {
        uri: img.uri,
        name: img.name ?? `image_${i}.jpg`,
        type: img.type ?? "image/jpeg",
      } as unknown as Blob)
    }
    formData.append("organs", JSON.stringify(organs))
    formData.append("lang", lang)

    const response = await fetch(`${API_URL}/identify`, {
      method: "POST",
      body: formData,
    })
    return handleResponse<IdentificationResponse>(response)
  },

  async searchSpecies(
    query: string,
    limit: number = 20
  ): Promise<SpeciesSearchResponse> {
    const params = new URLSearchParams({ q: query, limit: String(limit) })
    const response = await fetch(`${API_URL}/species?${params}`)
    return handleResponse<SpeciesSearchResponse>(response)
  },

  async getSpeciesDetail(speciesId: number): Promise<SpeciesListItem> {
    const response = await fetch(`${API_URL}/species/${speciesId}`)
    return handleResponse<SpeciesListItem>(response)
  },

  async getSpeciesByName(
    scientificName: string
  ): Promise<SpeciesListItem> {
    const response = await fetch(
      `${API_URL}/species/by-name/${encodeURIComponent(scientificName)}`
    )
    return handleResponse<SpeciesListItem>(response)
  },

  async healthCheck(): Promise<{ status: string; version: string }> {
    const response = await fetch(`${API_URL}/health`)
    return handleResponse<{ status: string; version: string }>(response)
  },

  // Admin
  async adminGetUsers(
    token: string,
    offset: number = 0,
    limit: number = 20,
    search?: string
  ): Promise<import("@/lib/types").AdminUserListResponse> {
    const params = new URLSearchParams({ offset: String(offset), limit: String(limit) })
    if (search) params.set("search", search)
    const response = await fetch(`${API_URL}/admin/users?${params}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    return handleResponse<import("@/lib/types").AdminUserListResponse>(response)
  },

  async adminUpdateUser(
    token: string,
    userId: string,
    update: import("@/lib/types").AdminUserUpdate
  ): Promise<import("@/lib/types").AdminUser> {
    const response = await fetch(`${API_URL}/admin/users/${userId}`, {
      method: "PATCH",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify(update),
    })
    return handleResponse<import("@/lib/types").AdminUser>(response)
  },

  async adminDeleteUser(token: string, userId: string): Promise<void> {
    const response = await fetch(`${API_URL}/admin/users/${userId}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!response.ok) {
      const body = await response.text()
      let message = `HTTP ${response.status}`
      try { const parsed = JSON.parse(body); message = parsed.detail ?? message } catch {}
      throw new Error(message)
    }
  },
}
