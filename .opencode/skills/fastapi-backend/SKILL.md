---
name: fastapi-backend
description: Python FastAPI backend patterns for Gardenify. Covers routes, services, models, and Vercel deployment.
---

## What I do
Guide FastAPI development following Python best practices, Pydantic models, and Vercel serverless patterns.

## When to use me
Use this when creating new API routes, services, models, or modifying the Python backend.

## Key Patterns

### Route Structure
```
api/
  main.py           # Vercel entrypoint + middleware
  config.py         # Settings with env vars
  routes/
    health.py       # GET /api/health, GET /api/debug
    identify.py     # POST /api/identify
  services/
    plantnet.py     # PlantNet API client
    plant_care.py   # Taxonomy-based care profiles
    cache.py        # SHA-256 hashing + in-memory cache
  models/
    schemas.py      # All Pydantic models
```

### Route Pattern
```python
from fastapi import APIRouter, File, UploadFile, HTTPException
from ..models.schemas import IdentifyResponse

router = APIRouter()

@router.post("/identify", response_model=IdentifyResponse)
async def identify_plant(file: File(...)):
    try:
        result = await plantnet_service.identify(file)
        return IdentifyResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### Pydantic Model Pattern
```python
from pydantic import BaseModel, Field

class IdentifyResponse(BaseModel):
    species: str = Field(..., description="Common name")
    scientific_name: str = Field(..., description="Scientific name")
    confidence: float = Field(..., ge=0, le=1)
    family: str | None = None
    genus: str | None = None
```

### Config Pattern
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    plantnet_api_key: str = ""
    supabase_url: str = ""
    environment: str = "local"
    use_remote: bool = False

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

settings = Settings()
```

## Rules
- Type hints on ALL functions — no exceptions
- Pydantic models for every request and response
- Use `logging` module — never `print()`
- No bare `except` — always specify exception type
- Write tests for every API route
- Validate input at the boundary (FastAPI dependency injection)
