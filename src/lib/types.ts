export interface SpeciesInfo {
  scientific_name: string;
  common_names: string[];
  family: string;
  genus: string;
}

export interface IdentificationResult {
  score: number;
  species: SpeciesInfo;
}

export interface DiseaseResult {
  name: string;
  confidence: number;
  description: string;
  treatment: string;
}

export interface WateringInfo {
  frequency: string;
  amount: string;
  method: string;
  seasonal_notes: string;
}

export interface SunlightInfo {
  preference: string;
  hours_per_day: string;
  notes: string;
}

export interface SoilInfo {
  type: string;
  ph: string;
  drainage: string;
  notes: string;
}

export interface TemperatureInfo {
  min_fahrenheit: number | null;
  max_fahrenheit: number | null;
  frost_tender: boolean;
  notes: string;
}

export interface GrowthInfo {
  mature_height: string;
  spread: string;
  growth_rate: string;
  bloom_season: string;
  bloom_color: string;
}

export interface PropagationInfo {
  methods: string[];
  difficulty: string;
  notes: string;
}

export interface CareInfo {
  watering: WateringInfo;
  sunlight: SunlightInfo;
  soil: SoilInfo;
  temperature: TemperatureInfo;
  growth: GrowthInfo;
  propagation: PropagationInfo;
  humidity: string;
  toxicity: string;
  common_pests: string[];
  general_tips: string;
}

export interface ImageMetadata {
  filename: string;
  size_bytes: number;
  width: number | null;
  height: number | null;
  format: string;
  hash_sha256: string;
  exif_camera: string;
  exif_date_taken: string;
  gps_latitude: number | null;
  gps_longitude: number | null;
  device_platform: string;
  app_version: string;
  thumbnail_data_url?: string;
}

export interface IdentificationResponse {
  best_match: string;
  results: IdentificationResult[];
  disease: DiseaseResult | null;
  care: CareInfo | null;
  metadata: ImageMetadata[];
  remaining_quota: number | null;
  version: string;
  cached: boolean;
  identification_id: string;
  source: string;
}

export interface SpeciesListItem {
  id: number;
  scientific_name: string;
  common_names: string[];
  family: string;
  genus: string;
  common_name: string;
}

export interface SpeciesSearchResponse {
  count: number;
  total_species: number;
  total_hashes: number;
  results: SpeciesListItem[];
}

export interface Profile {
  id: string;
  username: string | null;
  avatar_url: string | null;
  updated_at: string | null;
}

export interface IdentificationRecord {
  id: string;
  user_id: string;
  image_urls: string[];
  image_thumbnails?: string[];
  species_scientific_name: string;
  species_common_names: string;
  confidence: number;
  results_json: string;
  created_at: string;
}

export interface Favorite {
  id: string;
  user_id: string;
  species_scientific_name: string;
  species_common_name: string;
  species_family: string;
  species_genus: string;
  image_url: string;
  notes: string;
  created_at: string;
}

export interface UserSettings {
  id: string;
  user_id: string;
  language: string;
  theme: string;
  push_token: string | null;
  notifications_enabled: boolean;
  created_at: string;
  updated_at: string;
}

export type OrganType = "auto" | "leaf" | "flower" | "fruit" | "bark";

export interface AdminUser {
  id: string;
  email: string;
  full_name: string;
  subscription_tier: string;
  is_admin: boolean;
  created_at: string;
}

export interface AdminUserListResponse {
  users: AdminUser[];
  total: number;
}

export interface AdminUserUpdate {
  full_name?: string;
  subscription_tier?: string;
  is_admin?: boolean;
}
