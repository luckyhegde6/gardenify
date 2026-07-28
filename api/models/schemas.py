from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"


class IdentificationRequest(BaseModel):
    organs: list[str] = Field(
        default_factory=lambda: ["auto"],
        description="Plant organ for each image: leaf, flower, fruit, bark, or auto",
    )
    lang: str = Field(default="en", description="Response language code")


class SpeciesInfo(BaseModel):
    scientific_name: str
    common_names: list[str] = []
    family: str = ""
    genus: str = ""


class IdentificationResult(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
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


class ImageMetadata(BaseModel):
    filename: str = ""
    size_bytes: int = 0
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


class IdentificationResponse(BaseModel):
    best_match: str
    results: list[IdentificationResult]
    disease: DiseaseResult | None = None
    care: CareInfo | None = None
    metadata: list[ImageMetadata] = Field(default_factory=list)
    remaining_quota: int | None = None
    version: str = ""
    cached: bool = False
    identification_id: str | None = None
    source: str = "plantnet"


class ErrorResponse(BaseModel):
    detail: str
    code: str = "unknown"
