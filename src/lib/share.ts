import { Share, Alert } from "react-native"
import * as Sharing from "expo-sharing"
import type { IdentificationResponse } from "@/lib/types"

export async function shareIdentification(
  result: IdentificationResponse
): Promise<void> {
  const best = result.results[0]
  const displayName =
    best.species.common_names.length > 0
      ? best.species.common_names[0]
      : best.species.scientific_name

  const text = [
    `🌿 ${displayName} (${best.species.scientific_name})`,
    `Confidence: ${(best.score * 100).toFixed(1)}%`,
    best.species.family ? `Family: ${best.species.family}` : "",
    best.species.genus ? `Genus: ${best.species.genus}` : "",
    "",
    "Identified with Gardenify",
  ]
    .filter(Boolean)
    .join("\n")

  try {
    await Share.share(
      { message: text, title: `Gardenify: ${displayName}` },
      { dialogTitle: "Share Identification" }
    )
  } catch (err) {
    if (err instanceof Error && err.message !== "User did not share") {
      Alert.alert("Share Failed", "Could not share the result")
    }
  }
}

export async function shareImage(imageUri: string): Promise<void> {
  const isAvailable = await Sharing.isAvailableAsync()
  if (!isAvailable) {
    Alert.alert("Sharing Not Available", "Sharing is not available on this device")
    return
  }

  try {
    await Sharing.shareAsync(imageUri, {
      mimeType: "image/jpeg",
      dialogTitle: "Share Plant Photo",
    })
  } catch (err) {
    if (err instanceof Error && err.message !== "User did not share") {
      Alert.alert("Share Failed", "Could not share the image")
    }
  }
}
