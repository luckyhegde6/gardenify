# Lessons — Architecture & Decisions

Initial architecture decisions made on 2026-07-27. Each entry: **Context → Decision → Rationale**.

## PlantNet API over OpenAI GPT-4o

- **Context:** Designing the Gardenify plant identification app architecture
- **Decision:** PlantNet API (free tier 500/day) over OpenAI GPT-4o for plant identification
- **Rationale:** Free tier sufficient for MVP, 50K+ species, specialized for plants, no per-call cost
- **Severity:** important | **Status:** active

## Supabase Over Firebase

- **Context:** Choosing backend-as-a-service provider
- **Decision:** Supabase (PostgreSQL + Auth + Storage) over Firebase
- **Rationale:** PostgreSQL gives us RLS, SQL queries, and type safety. Generous free tier (500MB DB, 1GB storage, 50K MAU). Better for data-heavy apps with complex queries.
- **Severity:** important | **Status:** active

## Python Backend as API Proxy

- **Context:** Deciding where PlantNet API calls happen
- **Decision:** Python FastAPI backend on Vercel proxies all PlantNet calls
- **Rationale:** Keeps PlantNet API key server-side. Enables result caching, rate limiting, and future enrichment (LLM care tips). PlantNet responses are fast (~2-5s), so Vercel's 60s timeout is fine.
- **Severity:** important | **Status:** active

## Local AI as Future Enhancement

- **Context:** User asked about Android local AI for plant identification
- **Decision:** Start with PlantNet API only. Consider hybrid local+API in Phase 3+ if quota becomes an issue.
- **Rationale:** Local TFLite models are 50-100MB, cover fewer species (~10K vs 50K), and require Expo dev client builds. Not worth the complexity for MVP.
- **Severity:** minor | **Status:** active

## Image Compression Before Upload

- **Context:** Designing image storage pipeline
- **Decision:** Compress images client-side to max 1024px, JPEG quality 0.8 before upload
- **Rationale:** Reduces ~3MB photos to ~200KB. Saves Supabase storage (1GB free), reduces upload time on mobile networks, and PlantNet accepts compressed images fine.
- **Severity:** important | **Status:** active

## Image Hash Caching for Deduplication

- **Context:** Stretching PlantNet's 500/day free quota
- **Decision:** Compute SHA-256 hash of compressed images before sending to PlantNet
- **Rationale:** If same image was identified before, return cached result without API call. Eliminates duplicate identifications from re-captures.
- **Severity:** important | **Status:** active

## Disease Detection via PlantNet Diseases API

- **Context:** User wanted disease detection alongside species identification
- **Decision:** Use PlantNet's separate diseases endpoint (`/v2/diseases/identify`) in parallel with species identification
- **Rationale:** Same image format, no additional API key needed. Returns disease name, confidence, description, and treatment. Runs after species ID so it doesn't block the primary flow.
- **Severity:** important | **Status:** active

## Plant Care Analysis Engine

- **Context:** User wanted watering, sunlight, soil, growth, and propagation info
- **Decision:** Build a taxonomy-based care profile lookup system (genus → family → default)
- **Rationale:** PlantNet doesn't provide care instructions. We maintain care profiles keyed by genus/family. In production, this could connect to a plant database API (Trefle, Perenual) or LLM-generated care guides.
- **Severity:** important | **Status:** active

## EXIF and GPS Metadata Extraction

- **Context:** User wanted image metadata capture (camera, date, GPS, dimensions)
- **Decision:** Use Pillow to extract EXIF data and image dimensions from uploaded images
- **Rationale:** EXIF gives us camera model, date taken, and GPS coordinates. Useful for: (1) helping identify where a plant was found, (2) tracking when photos were taken, (3) future features like location-based plant recommendations.
- **Severity:** medium | **Status:** active

## In-Memory Result Caching

- **Context:** Avoid re-identifying the same images within a short window
- **Decision:** Cache identification results in-memory with 1-hour TTL, keyed by image hashes + organs + language
- **Rationale:** Simple first step before Redis/Supabase caching. Saves PlantNet quota for repeated identical uploads. Cache key includes organ selection since same image with different organ tags may yield different results.
- **Severity:** medium | **Status:** active

## MEMORY.md for Agent Context Efficiency

- **Context:** Agents were burning context re-reading large files at session start
- **Decision:** Create MEMORY.md as a quick-recap file with key facts, current state, file references, and testing instructions
- **Rationale:** Agents can read MEMORY.md (200 lines) instead of AGENTS.md + architecture.md + phase TODOs (500+ lines). Saves ~60% context on session start.
- **Severity:** important | **Status:** active

## Swagger UI for Local API Testing

- **Context:** Need a way to test the identify endpoint with file uploads locally
- **Decision:** FastAPI's built-in Swagger UI at `/docs` supports multipart file upload testing
- **Rationale:** No need for Postman or curl — Swagger UI lets you upload images, set organ types, and see full request/response. Works with `vercel dev` locally.
- **Severity:** minor | **Status:** active
