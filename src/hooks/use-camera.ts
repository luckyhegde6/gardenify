import { useState, useCallback } from "react"
import * as ImagePicker from "expo-image-picker"

interface UseCameraOptions {
  allowsEditing?: boolean
  quality?: ImagePicker.ImagePickerOptions["quality"]
}

export function useCamera(options: UseCameraOptions = {}) {
  const [image, setImage] = useState<ImagePicker.ImagePickerAsset | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const { allowsEditing = false, quality = 0.8 } = options

  const pickFromGallery = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const permission =
        await ImagePicker.requestMediaLibraryPermissionsAsync()
      if (!permission.granted) {
        throw new Error("Gallery permission is required")
      }

      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ["images"],
        allowsEditing,
        quality,
      })

      if (!result.canceled && result.assets[0]) {
        const asset = result.assets[0]
        setImage(asset)
        return asset
      }
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to pick image"
      setError(message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [allowsEditing, quality])

  const takePhoto = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const permission = await ImagePicker.requestCameraPermissionsAsync()
      if (!permission.granted) {
        throw new Error("Camera permission is required")
      }

      const result = await ImagePicker.launchCameraAsync({
        allowsEditing,
        quality,
      })

      if (!result.canceled && result.assets[0]) {
        const asset = result.assets[0]
        setImage(asset)
        return asset
      }
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to take photo"
      setError(message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [allowsEditing, quality])

  const clearImage = useCallback(() => {
    setImage(null)
    setError(null)
  }, [])

  return {
    image,
    loading,
    error,
    pickFromGallery,
    takePhoto,
    clearImage,
  }
}
