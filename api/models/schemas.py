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


class IdentificationResponse(BaseModel):
    best_match: str
    results: list[IdentificationResult]
    remaining_quota: int | None = None
    version: str = ""


class ErrorResponse(BaseModel):
    detail: str
    code: str = "unknown"
