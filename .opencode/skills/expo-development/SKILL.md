---
name: expo-development
description: Expo SDK 55 development patterns for Gardenify. Covers navigation, components, hooks, and platform-specific code.
---

## What I do
Guide Expo development following SDK 55 best practices, typed routes, and React Native conventions.

## When to use me
Use this when creating new screens, components, hooks, or any React Native code in Gardenify.

## Key Patterns

### File-Based Routing (expo-router)
```
src/app/
  (auth)/          # Auth screens (login, register)
  (tabs)/          # Main tab screens
  identification/  # Result detail screens
```

### Typed Routes
- Enabled in `app.json` via `experiments.typedRoutes`
- Use `href` with typed route strings
- Platform-specific: `.ios.tsx`, `.android.tsx`, `.web.tsx`

### Component Pattern
```tsx
// src/components/plant-card.tsx
import { View, Text, Image } from 'react-native'

interface PlantCardProps {
  name: string
  confidence: number
  imageUrl: string
}

export function PlantCard({ name, confidence, imageUrl }: PlantCardProps) {
  return (
    <View>
      <Image source={{ uri: imageUrl }} />
      <Text>{name}</Text>
      <Text>{(confidence * 100).toFixed(1)}%</Text>
    </View>
  )
}
```

### Custom Hook Pattern
```tsx
// src/hooks/use-identification.ts
import { useState } from 'react'
import { apiClient } from '@/lib/api-client'

export function useIdentification() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const identify = async (imageUri: string) => {
    setLoading(true)
    setError(null)
    try {
      const result = await apiClient.identify(imageUri)
      return result
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Identification failed')
      throw err
    } finally {
      setLoading(false)
    }
  }

  return { identify, loading, error }
}
```

## Rules
- Always use `npx expo install` — never `npm install`
- Use `expo-secure-store` for tokens — never `AsyncStorage`
- Functional components only — no class components
- Use `@/` path alias for internal imports
- Test on physical device for camera features
