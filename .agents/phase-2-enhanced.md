# Phase 2: Enhanced Experience

> Goal: Enrich the identification experience with disease detection, favorites, species details, and sharing.

## Features

- [ ] Disease detection
  - [ ] Add `POST /api/identify/disease` route (PlantNet `/v2/diseases/identify`)
  - [ ] Add disease result UI component
  - [ ] Show disease confidence scores and descriptions
- [ ] Favorites system
  - [ ] Create `favorites` table migration
  - [ ] Add favorite/unfavorite button on result screen
  - [ ] Build favorites list screen
  - [ ] Quick re-identify from favorites
- [ ] Species detail pages
  - [ ] Add `GET /api/species/{scientific_name}` route
  - [ ] Enrich with GBIF data (external API)
  - [ ] Build species detail screen with:
    - [ ] Scientific name + authority
    - [ ] Common names (multi-language)
    - [ ] Family + genus taxonomy
    - [ ] GBIF/Wikipedia links
    - [ ] Similar species
- [ ] Share results
  - [ ] Generate shareable card image (species + confidence + photo)
  - [ ] Use `react-native-view-shot` for screen capture
  - [ ] Share via `expo-sharing`
- [ ] Multi-language support
  - [ ] Use PlantNet `lang` parameter
  - [ ] Support English, French, Spanish
  - [ ] Language selector in settings
- [ ] Image cropping
  - [ ] Add `allowsEditing: true` to image picker
  - [ ] Crop to square for better identification
- [ ] Result caching
  - [ ] Hash-based deduplication in backend
  - [ ] Cache in Supabase (same image → same result)
  - [ ] Local AsyncStorage cache for instant repeat views
