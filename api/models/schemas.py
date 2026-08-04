from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.1.0"


class IdentificationRequest(BaseModel):
    organs: list[str] = Field(
        default_factory=lambda: ["auto"],
        description="Plant organ for each image: leaf, flower, fruit, bark, or auto",
        json_schema_extra={"example": ["leaf"]},
    )
    lang: str = Field(default="en", description="Response language: en, fr, es", json_schema_extra={"example": "en"})


class SpeciesInfo(BaseModel):
    scientific_name: str
    common_names: list[str] = []
    family: str = ""
    genus: str = ""


class IdentificationResult(BaseModel):
    score: float = Field(ge=0.0, le=1.0, description="Confidence score 0.0-1.0")
    species: SpeciesInfo


class DiseaseResult(BaseModel):
    name: str = ""
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    description: str = ""
    treatment: str = ""


class WateringInfo(BaseModel):
    frequency: str = ""
    amount: str = ""
    method: str = ""
    seasonal_notes: str = ""


class SunlightInfo(BaseModel):
    preference: str = ""
    hours_per_day: str = ""
    notes: str = ""


class SoilInfo(BaseModel):
    type: str = ""
    ph: str = ""
    drainage: str = ""
    notes: str = ""


class TemperatureInfo(BaseModel):
    min_fahrenheit: float | None = None
    max_fahrenheit: float | None = None
    frost_tender: bool = False
    notes: str = ""


class GrowthInfo(BaseModel):
    mature_height: str = ""
    spread: str = ""
    growth_rate: str = ""
    bloom_season: str = ""
    bloom_color: str = ""


class PropagationInfo(BaseModel):
    methods: list[str] = []
    difficulty: str = ""
    notes: str = ""


class CareInfo(BaseModel):
    watering: WateringInfo = Field(default_factory=WateringInfo)
    sunlight: SunlightInfo = Field(default_factory=SunlightInfo)
    soil: SoilInfo = Field(default_factory=SoilInfo)
    temperature: TemperatureInfo = Field(default_factory=TemperatureInfo)
    growth: GrowthInfo = Field(default_factory=GrowthInfo)
    propagation: PropagationInfo = Field(default_factory=PropagationInfo)
    humidity: str = ""
    toxicity: str = ""
    common_pests: list[str] = []
    general_tips: str = ""


class OpenCVResult(BaseModel):
    valid: bool = Field(description="Image decoded successfully by OpenCV")
    width: int | None = Field(description="Image width in pixels")
    height: int | None = Field(description="Image height in pixels")
    edges_detected: int = Field(description="Number of edge pixels (Canny edge detection)")
    total_pixels: int = Field(description="Total pixel count")
    content_score: float = Field(description="Content complexity score 0.0-1.0 (higher = more structure)")
    is_plant_like: bool = Field(description="Heuristic: image likely contains a plant subject")
    sharpness: float = Field(default=0.0, description="Variance of Laplacian focus measure (higher = more in-focus)")
    is_blurry: bool = Field(default=True, description="Flagged blurry when sharpness is below threshold")
    green_ratio: float = Field(default=0.0, description="Share of green (foliage) pixels in HSV, 0.0-1.0")
    mean_color: list[float] = Field(description="Mean BGR color values")
    dominant_colors: list[dict] = Field(description="Top dominant BGR colors via k-means clustering")


class ImageStorage(BaseModel):
    upload_id: str = Field(description="Upload batch identifier")
    original: str = Field(description="Path to original image on server")
    compressed: str = Field(description="Path to compressed version")
    thumbnail: str = Field(description="Path to thumbnail version (256x256)")


class ImageMetadata(BaseModel):
    filename: str = ""
    size_bytes: int = 0
    compressed_size_bytes: int | None = Field(default=None, description="Size after compression")
    thumbnail_size_bytes: int | None = Field(default=None, description="Thumbnail file size")
    compression_ratio: float | None = Field(default=None, description="compressed/original size ratio")
    width: int | None = None
    height: int | None = None
    format: str = ""
    hash_sha256: str = ""
    exif_camera: str = ""
    exif_date_taken: str = ""
    gps_latitude: float | None = None
    gps_longitude: float | None = None
    device_platform: str = ""
    app_version: str = ""
    exif: dict = Field(default_factory=dict, description="Full EXIF tag dump")
    opencv: OpenCVResult | None = Field(default=None, description="OpenCV analysis results")
    storage: ImageStorage | None = Field(default=None, description="Server-side file paths")
    thumbnail_data_url: str = Field(default="", description="Base64 data URL of the 256x256 JPEG thumbnail")


class IdentificationResponse(BaseModel):
    best_match: str = Field(description="Top species scientific name")
    results: list[IdentificationResult] = Field(description="Ranked identification results")
    disease: DiseaseResult | None = Field(default=None, description="Disease detection result")
    care: CareInfo | None = Field(default=None, description="Plant care instructions")
    metadata: list[ImageMetadata] = Field(default_factory=list, description="Per-image processing metadata")
    remaining_quota: int | None = Field(default=None, description="PlantNet API daily quota remaining")
    version: str = ""
    cached: bool = False
    identification_id: str | None = Field(default=None, description="Unique ID for this identification")
    source: str = Field(default="plantnet", description="Data source: plantnet, local, or cache")


class ErrorResponse(BaseModel):
    detail: str
    code: str = "unknown"


class HistoryRecord(BaseModel):
    id: str
    best_match: str
    score: float
    species_scientific_name: str
    species_common_names: list[str] = []
    species_family: str = ""
    species_genus: str = ""
    image_urls: list[str] = []
    thumbnail_urls: list[str] = []
    organs: list[str] = []
    source: str = ""
    created_at: str = ""


class HistoryListResponse(BaseModel):
    records: list[HistoryRecord]
    total: int


class HistoryDetailResponse(BaseModel):
    id: str
    best_match: str
    results: list[IdentificationResult]
    disease: DiseaseResult | None = None
    care: CareInfo | None = None
    metadata: list[ImageMetadata] = []
    source: str = ""
    created_at: str = ""


# ── Auth schemas ─────────────────────────────────────────────

class AuthUserResponse(BaseModel):
    id: str
    email: str
    is_admin: bool = False


class LoginRequest(BaseModel):
    email: str = Field(description="Email address")
    password: str = Field(description="Password")


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_at: int | None = None
    user: AuthUserResponse | None = None


class ForgotPasswordRequest(BaseModel):
    email: str = Field(description="Email address to send a recovery link to")


class ResetPasswordRequest(BaseModel):
    email: str = Field(description="Email address of the account being recovered")
    code: str = Field(description="Recovery code from the reset email link")
    new_password: str = Field(min_length=6, description="New password (min 6 characters)")


class ForgotPasswordResponse(BaseModel):
    detail: str = "sent"


# ── Admin schemas ─────────────────────────────────────────────

class AdminUserResponse(BaseModel):
    id: str
    email: str
    full_name: str = ""
    subscription_tier: str = "free"
    is_admin: bool = False
    created_at: str = ""


class AdminUserListResponse(BaseModel):
    users: list[AdminUserResponse]
    total: int


class AdminUserUpdate(BaseModel):
    full_name: str | None = None
    subscription_tier: str | None = None
    is_admin: bool | None = None
