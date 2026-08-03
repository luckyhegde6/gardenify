"""Onboarding page with architecture and workflow diagrams."""

ONBOARDING_PAGE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>How Gardenify Works — Architecture & Workflows</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🌿</text></svg>">
    <script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
    <style>
        :root {
            --green-50: #f0fdf4; --green-100: #dcfce7; --green-500: #22c55e;
            --green-600: #16a34a; --green-700: #15803d; --green-800: #166534;
            --gray-50: #f9fafb; --gray-100: #f3f4f6; --gray-200: #e5e7eb;
            --gray-400: #9ca3af; --gray-500: #6b7280; --gray-600: #4b5563;
            --gray-700: #374151; --gray-800: #1f2937; --gray-900: #111827;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: var(--gray-800); background: white; line-height: 1.6; }
        a { color: var(--green-600); text-decoration: none; }
        a:hover { text-decoration: underline; }

        .header { background: linear-gradient(135deg, var(--green-800), var(--green-600)); color: white; padding: 2.5rem 1.5rem; text-align: center; }
        .header h1 { font-size: 2.25rem; margin-bottom: 0.5rem; }
        .header p { opacity: 0.9; max-width: 600px; margin: 0 auto; }
        .header .links { margin-top: 1rem; display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap; }
        .header .links a { color: rgba(255,255,255,0.85); font-size: 0.9rem; }
        .header .links a:hover { color: white; }

        .container { max-width: 960px; margin: 0 auto; padding: 0 1.5rem; }
        section { padding: 3rem 0; }
        section:nth-child(even) { background: var(--gray-50); }
        section h2 { font-size: 1.6rem; font-weight: 700; margin-bottom: 0.5rem; color: var(--green-800); }
        section .subtitle { color: var(--gray-500); font-size: 1rem; margin-bottom: 1.5rem; }
        section p { color: var(--gray-600); margin-bottom: 1rem; max-width: 720px; }

        .diagram { background: white; border: 1px solid var(--gray-200); border-radius: 12px; padding: 1.5rem; margin: 1.5rem 0; overflow-x: auto; }
        .diagram .caption { font-size: 0.85rem; color: var(--gray-400); text-align: center; margin-top: 0.75rem; }

        .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1.25rem; margin: 1.5rem 0; }
        .card { background: white; border: 1px solid var(--gray-200); border-radius: 12px; padding: 1.5rem; transition: box-shadow 0.2s; }
        .card h3 { font-size: 1.1rem; margin-bottom: 0.5rem; }
        .card p { font-size: 0.9rem; color: var(--gray-500); margin-bottom: 0; }

        .step-list { list-style: none; padding: 0; }
        .step-list li { display: flex; gap: 1rem; padding: 0.75rem 0; border-bottom: 1px solid var(--gray-100); }
        .step-list li:last-child { border-bottom: none; }
        .step-list .num { flex-shrink: 0; width: 28px; height: 28px; background: var(--green-100); color: var(--green-800); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.85rem; }
        .step-list .text { font-size: 0.9rem; color: var(--gray-600); }
        .step-list .text strong { color: var(--gray-800); }

        footer { text-align: center; padding: 2rem; color: var(--gray-400); font-size: 0.85rem; border-top: 1px solid var(--gray-200); }
        footer a { color: var(--green-600); }

        @media (max-width: 640px) {
            .header h1 { font-size: 1.6rem; }
            section { padding: 2rem 0; }
            .diagram { padding: 1rem; }
        }
    </style>
</head>
<body>
<div class="header">
    <h1>🌿 How Gardenify Works</h1>
    <p>Architecture, workflows, and data flow — from snapping a photo to getting a plant identification result.</p>
    <div class="links">
        <a href="/">&larr; Home</a>
        <a href="#overview">Overview</a>
        <a href="#architecture">Architecture</a>
        <a href="#identify">Identification Flow</a>
        <a href="#offline">Fallback &amp; Matching</a>
        <a href="#auth">Auth Flow</a>
        <a href="#release">Release Pipeline</a>
    </div>
</div>

<section id="overview">
    <div class="container">
        <h2>App Overview</h2>
        <p class="subtitle">What Gardenify does and how it helps</p>
        <p>Gardenify is a plant identification mobile app for Android. Users capture or upload a photo of a plant, and the app returns:</p>
        <div class="cards">
            <div class="card">
                <h3>🌱 Species Identification</h3>
                <p>Scientific name, common names, family, genus, and confidence score from PlantNet's 50,000+ species database.</p>
            </div>
            <div class="card">
                <h3>🩺 Disease Detection</h3>
                <p>If the plant shows signs of disease, Gardenify identifies the condition and provides treatment recommendations.</p>
            </div>
            <div class="card">
                <h3>📋 Care Instructions</h3>
                <p>Watering frequency, sunlight preferences, soil type, temperature range, propagation methods, and toxicity info.</p>
            </div>
            <div class="card">
                <h3>📜 History & Favorites</h3>
                <p>All identifications are saved to history. Users can bookmark favorites and revisit past results anytime.</p>
            </div>
        </div>
        <div class="diagram">
            <div class="mermaid">
flowchart LR
    A["📱 User snaps photo"] --> B["🔍 Identify"]
    B --> C["🌿 Species Name"]
    B --> D["🩺 Disease Info"]
    B --> E["📋 Care Guide"]
    C --> F["💾 Save to History"]
    D --> F
    E --> F
    F --> G["⭐ Favorite"]
    </div>
            <p class="caption">High-level app flow</p>
        </div>
    </div>
</section>

<section id="architecture">
    <div class="container">
        <h2>System Architecture</h2>
        <p class="subtitle">How the components fit together</p>
        <p>Gardenify follows a three-tier architecture: a mobile frontend built with Expo (React Native), a Python/FastAPI backend deployed on Vercel, and Supabase for authentication, database, and file storage. The PlantNet API provides AI-powered species identification.</p>
        <div class="diagram">
            <div class="mermaid">
architecture-beta
    group api[API Layer]
    group mobile[Mobile Layer]
    group data[Data Layer]
    group external[External Services]

    service expo(mobile: Expo App) in mobile
    service fastapi(server: FastAPI) in api
    service supabase(database: Supabase) in data
    service plantnet(cloud: PlantNet API) in external
    service vercel(globe: Vercel) in api

    expo:R -- --> fastapi:L
    expo:B -- --> supabase:T
    fastapi:R -- --> plantnet:L
    fastapi:B -- --> supabase:T
    vercel:T -- --> fastapi:B
            </div>
            <p class="caption">System architecture showing the three tiers and external integrations</p>
        </div>

        <h3 style="margin-top: 2rem; color: var(--green-800);">Component Breakdown</h3>
        <div class="cards" style="margin-top: 1rem;">
            <div class="card">
                <h3>📱 Expo App</h3>
                <p>React Native mobile app with file-based routing (expo-router), camera/gallery integration, and secure token storage. Communicates with FastAPI backend via REST and Supabase directly for auth.</p>
            </div>
            <div class="card">
                <h3>⚡ FastAPI Backend</h3>
                <p>Python async server deployed on Vercel Serverless. Handles image validation (OpenCV), PlantNet proxying, caching, Supabase species matching, and history management.</p>
            </div>
            <div class="card">
                <h3>🗄️ Supabase</h3>
                <p>PostgreSQL database with Row Level Security. Stores users, identifications, favorites, settings, and species data. Also provides Auth (email/password) and Storage for images.</p>
            </div>
            <div class="card">
                <h3>🌐 PlantNet API</h3>
                <p>AI-powered plant identification (50,000+ species). Free tier allows 500 identifications per day. Used as a fallback when Supabase species matching has no match.</p>
            </div>
        </div>
    </div>
</section>

<section id="identify" style="background: var(--gray-50);">
    <div class="container">
        <h2>Plant Identification Flow</h2>
        <p class="subtitle">What happens when you identify a plant</p>
        <p>The identification pipeline follows a multi-stage process designed to save PlantNet API quota while maximizing accuracy:</p>
        <ol class="step-list">
            <li>
                <span class="num">1</span>
                <div class="text"><strong>Capture or upload</strong> — User takes a photo or selects from gallery. Image is compressed client-side (max 1024px, JPEG quality 0.8) and sent to backend.</div>
            </li>
            <li>
                <span class="num">2</span>
                <div class="text"><strong>Image validation</strong> — Backend runs OpenCV edge detection and color analysis to confirm the image contains plant-like content. Non-plant images are rejected early.</div>
            </li>
            <li>
                <span class="num">3</span>
                <div class="text"><strong>Cache check</strong> — Backend computes an SHA-256 hash of the image. If the same image was identified within the last hour, the cached result is returned immediately.</div>
            </li>
            <li>
                <span class="num">4</span>
                <div class="text"><strong>Species store match</strong> — The backend searches the Supabase species database (10,008 species, perceptual-hash indexed) using pHash matching. On a match, the result is returned as <code>source: "local"</code> without calling PlantNet.</div>
            </li>
            <li>
                <span class="num">5</span>
                <div class="text"><strong>PlantNet API call</strong> — If the species store has no match, PlantNet API is queried. The result is returned as <code>source: "plantnet"</code> and cached for future requests.</div>
            </li>
            <li>
                <span class="num">6</span>
                <div class="text"><strong>Disease detection</strong> — Runs in parallel with species identification. If a disease is found, treatment recommendations are included in the response.</div>
            </li>
            <li>
                <span class="num">7</span>
                <div class="text"><strong>Care instructions</strong> — Taxonomy-based care profiles are looked up by genus/family, providing watering, sunlight, soil, and temperature recommendations.</div>
            </li>
        </ol>

        <div class="diagram">
            <div class="mermaid">
sequenceDiagram
    participant User
    participant App as Expo App
    participant Backend as FastAPI<br>Backend
    participant Store as Supabase<br>Species Store
    participant PlantNet

    User->>App: Take / upload photo
    App->>App: Compress image<br>(1024px, JPEG 0.8)
    App->>Backend: POST /api/identify

    Backend->>Backend: OpenCV validation<br>(edge detection + color)
    alt Invalid image
        Backend-->>App: 400 Bad Request
        App-->>User: "Not a plant photo"
    end

    Backend->>Backend: SHA-256 cache check
    alt Cache hit
        Backend-->>App: Cached result
        App-->>User: Show identification
    end

    Backend->>Store: pHash lookup
    alt Store match found
        Store-->>Backend: Species data
        Backend-->>App: Result (source: "local")
    else No store match
        Backend->>PlantNet: Identify via API
        PlantNet-->>Backend: Species results
        Backend->>Backend: Cache result
        Backend-->>App: Result (source: "plantnet")
    end

    Backend->>Backend: Lookup care profile<br>by genus/family
    Backend-->>App: Full response<br>(species + disease + care)

    App->>User: Display results
            </div>
            <p class="caption">Sequence diagram of the plant identification pipeline</p>
        </div>
    </div>
</section>

<section id="offline">
    <div class="container">
        <h2>Fallback &amp; Matching Strategy</h2>
        <p class="subtitle">How PlantNet quota is saved while staying fast</p>
        <p>Gardenify matches photos against a curated Supabase species database (10,008 species, of which 1,960 have perceptual hashes). A perceptual-hash hit returns immediately without consuming PlantNet API quota; the cloud species store means no server-side disk database is needed.</p>
        <div class="diagram">
            <div class="mermaid">
flowchart TD
    A["📱 User sends image"] --> B{"OpenCV gate<br>passes?"}
    B -->|"No"| C["❌ Reject: not plant-like"]
    B -->|"Yes"| D{"SHA-256 cache<br>hit?"}
    D -->|"Yes"| E["✅ Return cached result"]
    D -->|"No"| F{"pHash match<br>in Supabase store?"}
    F -->|"Yes"| G["✅ Return local result<br>(source: local)"]
    F -->|"No"| H{"PlantNet API<br>available?"}
    H -->|"Yes"| I["🔌 Query PlantNet API"]
    I --> J["✅ Return PlantNet result<br>(source: plantnet)"]
    J --> K["🔄 Cache for future"]
    H -->|"No (offline)"| L["❌ No match found<br>(return empty)"]
    G --> M["📊 Enrich with<br>care profiles"]
    E --> M
    J --> M
    L --> M
    M --> N["📱 Display to user"]
            </div>
            <p class="caption">Decision tree for the identification pipeline, showing online/fallback behavior</p>
        </div>
        <p>Key features of the fallback strategy:</p>
        <ul style="color: var(--gray-600); font-size: 0.9rem; padding-left: 1.25rem;">
            <li><strong>OpenCV gate</strong> rejects non-plant images before any API calls are made</li>
            <li><strong>SHA-256 cache</strong> prevents duplicate PlantNet API calls for the same image</li>
            <li><strong>Perceptual hash matching</strong> (dHash + pHash) hits 1,960 species stored in Supabase before PlantNet is called</li>
            <li><strong>Graceful degradation</strong> — if PlantNet is unreachable, the app falls back gracefully with what it has</li>
            <li><strong>Care profiles</strong> are determined by taxonomy (genus → family → default)</li>
        </ul>
    </div>
</section>

<section id="auth" style="background: var(--gray-50);">
    <div class="container">
        <h2>Authentication Flow</h2>
        <p class="subtitle">How users sign up, log in, and stay authenticated</p>
        <p>Authentication is handled entirely by Supabase Auth. The app uses email/password authentication with JWT tokens stored securely using <code>expo-secure-store</code> (not AsyncStorage).</p>
        <div class="diagram">
            <div class="mermaid">
sequenceDiagram
    participant User
    participant App as Expo App
    participant Supabase
    participant Backend as FastAPI<br>Backend

    rect rgb(240, 253, 244)
        Note over User,Backend: Registration
        User->>App: Enter email + password
        App->>Supabase: signUp(email, password)
        Supabase-->>App: User + session
        App->>Supabase: Insert profile into public.users
        App-->>User: Account created
    end

    rect rgb(239, 246, 255)
        Note over User,Backend: Login
        User->>App: Enter email + password
        App->>Supabase: signInWithPassword(email, password)
        Supabase-->>App: JWT + refresh token
        App->>App: Store in SecureStore
        App->>Supabase: Fetch public.users profile
        Supabase-->>App: Profile (role, tier, is_admin)
        App-->>User: Dashboard
    end

    rect rgb(254, 243, 199)
        Note over User,Backend: Authenticated Requests
        User->>App: Open app (cold start)
        App->>App: Load session from SecureStore
        App->>Supabase: getSession()
        alt Session valid
            Supabase-->>App: Session OK
        else Expired
            App->>Supabase: Refresh token
            Supabase-->>App: New JWT
        end
        App-->>User: Continue session
    end

    rect rgb(254, 242, 242)
        Note over User,Backend: Admin Actions
        App->>Backend: GET /api/admin/users<br>Authorization: Bearer JWT
        Backend->>Supabase: Verify JWT + is_admin check
        Supabase-->>Backend: Admin confirmed
        Backend-->>App: Admin response
    end
            </div>
            <p class="caption">Authentication flow showing registration, login, session persistence, and admin access</p>
        </div>
        <p>Security measures:</p>
        <ul style="color: var(--gray-600); font-size: 0.9rem; padding-left: 1.25rem;">
            <li>JWT tokens stored in <strong>SecureStore</strong> (hardware-backed encryption on Android)</li>
            <li>All database access goes through <strong>Row Level Security (RLS)</strong> policies</li>
            <li>Admin routes use <strong>security definer</strong> functions to prevent RLS recursion</li>
            <li>Supabase service key is <strong>never exposed</strong> to the client — only used server-side</li>
        </ul>
    </div>
</section>

<section id="release">
    <div class="container">
        <h2>Release & Deployment Pipeline</h2>
        <p class="subtitle">From code to APK — how Gardenify gets to your phone</p>
        <p>Gardenify uses fully automated CI/CD. All code changes go through pull requests, and releases are triggered by git tags.</p>
        <div class="diagram">
            <div class="mermaid">
flowchart LR
    A["👨‍💻 Developer commits"] --> B["🔀 Pull Request"]
    B --> C["✅ CI Checks<br>(lint, typecheck, tests)"]
    C --> D["🔀 Merge to main"]
    D --> E["🚀 Deploy Backend<br>(Vercel)"]
    D --> F["🏷️ Tag v* push"]
    F --> G["📦 Build APK<br>(EAS)"]
    G --> H["📥 Download artifact"]
    H --> I["🏷️ Create GitHub Release<br>+ attach APK"]
    I --> J["📱 User downloads<br>APK from Releases"]

    style A fill:#dbeafe
    style J fill:#d1fae5
    style I fill:#fef3c7
            </div>
            <p class="caption">CI/CD pipeline from commit to APK distribution</p>
        </div>

        <h3 style="margin-top: 2rem; color: var(--green-800);">Workflow Details</h3>
        <div class="diagram">
            <div class="mermaid">
sequenceDiagram
    participant Dev
    participant GH as GitHub
    participant CI as GitHub Actions
    participant EAS as EAS Build
    participant Vercel
    participant Release as GitHub Releases

    Dev->>GH: Push to feat/* branch
    GH->>CI: Trigger EAS Update (preview)
    CI-->>Dev: OTA preview published

    Dev->>GH: Create PR to main
    GH->>CI: Run lint + tests
    CI-->>GH: ✅ Green

    GH->>GH: Merge PR
    GH->>Vercel: Deploy backend (api/* changed)
    Vercel-->>GH: ✅ Deployed

    Dev->>GH: git tag v1.0.0
    GH->>CI: Trigger Release workflow
    CI->>EAS: Build production APK
    CI-->>EAS: Wait for completion
    EAS-->>CI: APK ready
    CI->>CI: Download APK artifact
    CI->>Release: Create Release + attach APK
    Release-->>Dev: ✅ Release published
            </div>
            <p class="caption">Full release pipeline sequence</p>
        </div>

        <div class="cards" style="margin-top: 1.5rem;">
            <div class="card">
                <h3>📱 APK Distribution</h3>
                <p>APKs are built via EAS Build, downloaded, and attached directly to GitHub Releases. No Play Store required — users download and install the APK manually.</p>
            </div>
            <div class="card">
                <h3>⚡ OTA Updates</h3>
                <p>Preview branches (feat/*, bugfix/*, chore/*) publish OTA updates automatically via EAS Update. Production does NOT use OTA — only full APK releases.</p>
            </div>
            <div class="card">
                <h3>🔐 Environment Secrets</h3>
                <p>All API keys and tokens are stored as GitHub Actions secrets: EXPO_TOKEN, VERCEL_TOKEN, SUPABASE_ACCESS_TOKEN, and PLANTNET_API_KEY.</p>
            </div>
        </div>
    </div>
</section>

<section id="tech">
    <div class="container">
        <h2>Technology Stack</h2>
        <p class="subtitle">Every tool and framework that powers Gardenify</p>
        <div class="cards">
            <div class="card">
                <h3>📱 Mobile</h3>
                <p><strong>Expo SDK 55</strong> with TypeScript 5.9, expo-router for file-based navigation, and React Native for cross-platform UI (Android-first).</p>
            </div>
            <div class="card">
                <h3>⚙️ Backend</h3>
                <p><strong>FastAPI</strong> (Python 3.12) deployed on Vercel Serverless. Async endpoints, Pydantic validation, OpenCV image processing, and Supabase species matching.</p>
            </div>
            <div class="card">
                <h3>🗄️ Database</h3>
                <p><strong>Supabase</strong> (PostgreSQL) with Row Level Security. 10,008 species from GBIF imported, 1,960 indexed with perceptual hashes for instant matching.</p>
            </div>
            <div class="card">
                <h3>🤖 Plant AI</h3>
                <p><strong>PlantNet API v2</strong> — 50,000+ plant species, disease detection, and organ-specific identification (leaf, flower, fruit, bark). 500 free identifications per day.</p>
            </div>
            <div class="card">
                <h3>🔐 Auth</h3>
                <p><strong>Supabase Auth</strong> with email/password. JWT tokens stored in expo-secure-store. RLS policies on all tables. Admin roles via security definer functions.</p>
            </div>
            <div class="card">
                <h3>🚀 CI/CD</h3>
                <p><strong>GitHub Actions</strong> with 6 workflows: lint & typecheck, Python tests, EAS build, EAS update, Vercel deploy, and Supabase migrations.</p>
            </div>
            <div class="card">
                <h3>✅ Testing</h3>
                <p><strong>73 Python tests</strong> (pytest), <strong>41 frontend tests</strong> (Jest + testing-library), <strong>21 E2E tests</strong> (Playwright API tests).</p>
            </div>
            <div class="card">
                <h3>📦 Build</h3>
                <p><strong>EAS Build</strong> for Android APK production builds. Development builds via eas-cli. All artifacts attached to GitHub Releases.</p>
            </div>
        </div>
    </div>
</section>

<footer>
    <p>Gardenify &copy; 2026 &middot; <a href="https://github.com/luckyhegde6/gardenify" target="_blank">GitHub</a> &middot; <a href="/">Home</a> &middot; <a href="/about">About</a></p>
</footer>

<script>
    mermaid.initialize({
        startOnLoad: true,
        theme: 'default',
        themeVariables: {
            primaryColor: '#16a34a',
            primaryBorderColor: '#15803d',
            primaryTextColor: '#1f2937',
            lineColor: '#9ca3af',
            secondaryColor: '#f0fdf4',
            tertiaryColor: '#f9fafb',
            fontSize: '14px'
        },
        sequence: {
            showSequenceNumbers: true
        }
    });
</script>
</body>
</html>"""