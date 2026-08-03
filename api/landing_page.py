"""Static HTML pages for sasyakashi.vercel.app."""

NOT_FOUND_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>404 — Page Not Found | Gardenify</title>
    <style>
        :root {
            --green-600: #16a34a; --green-700: #15803d; --green-800: #166534;
            --gray-50: #f9fafb; --gray-200: #e5e7eb; --gray-500: #6b7280;
            --gray-600: #4b5563; --gray-800: #1f2937;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: var(--gray-800); background: var(--gray-50); line-height: 1.6; min-height: 100vh; display: flex; flex-direction: column; }
        .hero { background: linear-gradient(135deg, var(--green-800), var(--green-600)); color: white; text-align: center; padding: 4.5rem 1.5rem 3.5rem; }
        .hero h1 { font-size: 5rem; font-weight: 800; line-height: 1; margin-bottom: 0.5rem; }
        .hero p { font-size: 1.2rem; opacity: 0.95; }
        .container { max-width: 720px; margin: 0 auto; padding: 3rem 1.5rem; text-align: center; flex: 1; }
        .container p { color: var(--gray-600); margin-bottom: 1.5rem; }
        .links { display: flex; gap: 0.75rem; justify-content: center; flex-wrap: wrap; }
        .btn { display: inline-block; background: var(--green-600); color: white; padding: 0.6rem 1.25rem; border-radius: 8px; font-weight: 600; text-decoration: none; }
        .btn:hover { background: var(--green-700); text-decoration: none; }
        .btn-secondary { background: white; color: var(--green-600); border: 1px solid var(--gray-200); }
        .btn-secondary:hover { background: var(--gray-50); }
        footer { text-align: center; padding: 2rem; color: var(--gray-500); font-size: 0.85rem; border-top: 1px solid var(--gray-200); background: white; }
        footer a { color: var(--green-600); }
        @media (max-width: 640px) { .hero h1 { font-size: 3.5rem; } }
    </style>
</head>
<body>
<div class="hero">
    <h1>404</h1>
    <p>🌿 Page not found</p>
</div>
<div class="container">
    <p>The page you're looking for doesn't exist or has moved. Head back to a page that does.</p>
    <div class="links">
        <a href="/" class="btn">Back to Home</a>
        <a href="/docs" class="btn btn-secondary">API Docs</a>
        <a href="/onboarding" class="btn btn-secondary">How It Works</a>
        <a href="/about" class="btn btn-secondary">About</a>
    </div>
</div>
<footer>
    <p>Gardenify &copy; 2026 &middot; <a href="https://github.com/luckyhegde6/gardenify" target="_blank">GitHub</a> &middot; <a href="/api/health">API Status</a></p>
</footer>
</body>
</html>"""

LANDING_PAGE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gardenify — Identify Any Plant</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🌿</text></svg>">
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

        .hero { background: linear-gradient(135deg, var(--green-800), var(--green-600)); color: white; text-align: center; padding: 4.5rem 1.5rem 3.5rem; }
        .hero h1 { font-size: 2.75rem; font-weight: 800; margin-bottom: 0.75rem; }
        .hero .tagline { font-size: 1.2rem; opacity: 0.9; max-width: 560px; margin: 0 auto 1.5rem; }
        .hero .badges { display: flex; gap: 0.75rem; justify-content: center; flex-wrap: wrap; margin-bottom: 1.5rem; }
        .hero .badges a, .hero .badges span { display: inline-flex; align-items: center; gap: 0.4rem; background: rgba(255,255,255,0.15); backdrop-filter: blur(4px); padding: 0.45rem 1rem; border-radius: 999px; color: white; font-size: 0.85rem; font-weight: 500; transition: background 0.2s; text-decoration: none; }
        .hero .badges a:hover { background: rgba(255,255,255,0.25); }
        .hero .nav-links { display: flex; gap: 1.25rem; justify-content: center; flex-wrap: wrap; font-size: 0.95rem; }
        .hero .nav-links a { color: rgba(255,255,255,0.85); text-decoration: none; }
        .hero .nav-links a:hover { color: white; text-decoration: underline; }

        .container { max-width: 960px; margin: 0 auto; padding: 0 1.5rem; }
        section { padding: 3.5rem 0; }
        section:nth-child(even) { background: var(--gray-50); }
        section h2 { font-size: 1.75rem; font-weight: 700; margin-bottom: 0.5rem; color: var(--green-800); }
        section .subtitle { color: var(--gray-500); font-size: 1rem; margin-bottom: 1.75rem; }

        .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.25rem; }
        .card { background: white; border: 1px solid var(--gray-200); border-radius: 12px; padding: 1.5rem; transition: box-shadow 0.2s; }
        .card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.08); }
        .card h3 { font-size: 1.1rem; margin-bottom: 0.5rem; color: var(--gray-900); }
        .card p { font-size: 0.9rem; color: var(--gray-500); margin-bottom: 0.75rem; }
        .card a { font-weight: 600; font-size: 0.9rem; }

        .endpoint-table { width: 100%; border-collapse: collapse; background: white; border-radius: 12px; overflow: hidden; border: 1px solid var(--gray-200); }
        .endpoint-table th, .endpoint-table td { padding: 0.7rem 1rem; text-align: left; border-bottom: 1px solid var(--gray-100); font-size: 0.9rem; }
        .endpoint-table th { background: var(--green-50); font-weight: 600; font-size: 0.85rem; color: var(--gray-700); }
        .endpoint-table code { font-size: 0.85rem; background: var(--gray-100); padding: 0.15rem 0.4rem; border-radius: 4px; }
        .method { display: inline-block; padding: 0.15rem 0.45rem; border-radius: 4px; font-size: 0.75rem; font-weight: 700; font-family: monospace; }
        .method-get { background: #dbeafe; color: #1e40af; }
        .method-post { background: #d1fae5; color: #065f46; }
        .method-patch { background: #fef3c7; color: #92400e; }
        .method-delete { background: #fee2e2; color: #991b1b; }

        .download-section { text-align: center; }
        .download-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: center; max-width: 700px; margin: 0 auto; }
        .download-qr img { width: 200px; height: 200px; border-radius: 12px; border: 2px solid var(--gray-200); }
        .download-info { text-align: left; }
        .download-info h3 { font-size: 1.25rem; margin-bottom: 0.5rem; }
        .download-info p { color: var(--gray-500); font-size: 0.9rem; margin-bottom: 1rem; }
        .download-btn { display: inline-block; background: var(--green-600); color: white; padding: 0.75rem 1.5rem; border-radius: 8px; font-weight: 600; text-decoration: none; transition: background 0.2s; }
        .download-btn:hover { background: var(--green-700); text-decoration: none; }
        .download-steps { text-align: left; font-size: 0.9rem; color: var(--gray-600); }
        .download-steps ol { padding-left: 1.25rem; }
        .download-steps li { margin-bottom: 0.4rem; }
        .badge-release { display: inline-block; background: var(--green-100); color: var(--green-800); font-size: 0.85rem; padding: 0.25rem 0.75rem; border-radius: 999px; font-weight: 600; margin-bottom: 0.75rem; }

        .about-content { max-width: 700px; margin: 0 auto; }
        .about-content p { margin-bottom: 1rem; color: var(--gray-600); }
        .about-content .profile { display: flex; align-items: center; gap: 1.5rem; background: white; border: 1px solid var(--gray-200); border-radius: 12px; padding: 1.5rem; margin-top: 1.5rem; }
        .about-content .profile .avatar { width: 64px; height: 64px; border-radius: 50%; background: var(--green-100); display: flex; align-items: center; justify-content: center; font-size: 2rem; flex-shrink: 0; }
        .about-content .profile .info h3 { margin-bottom: 0.25rem; }
        .about-content .profile .info p { color: var(--gray-500); font-size: 0.9rem; margin-bottom: 0; }

        .tech-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; }
        .tech-item { background: white; border: 1px solid var(--gray-200); border-radius: 8px; padding: 1rem; text-align: center; }
        .tech-item .label { font-size: 0.8rem; color: var(--gray-400); text-transform: uppercase; letter-spacing: 0.05em; }
        .tech-item .value { font-size: 1rem; font-weight: 600; color: var(--gray-800); margin-top: 0.25rem; }

        .contributing { background: white; border: 1px solid var(--gray-200); border-radius: 12px; padding: 2rem; margin-top: 2rem; }
        .contributing h3 { margin-bottom: 0.75rem; }
        .contributing p { color: var(--gray-600); font-size: 0.9rem; margin-bottom: 0.75rem; }
        .contributing a { font-weight: 600; }

        footer { text-align: center; padding: 2rem; color: var(--gray-400); font-size: 0.85rem; border-top: 1px solid var(--gray-200); background: white; }
        footer a { color: var(--green-600); }
        footer .footer-links { display: flex; gap: 1.5rem; justify-content: center; flex-wrap: wrap; margin-top: 0.75rem; font-size: 0.9rem; }

        @media (max-width: 640px) {
            .hero h1 { font-size: 2rem; }
            .hero { padding: 3rem 1rem 2.5rem; }
            .download-grid { grid-template-columns: 1fr; text-align: center; }
            .download-info { text-align: center; }
            .download-steps { text-align: left; }
            .about-content .profile { flex-direction: column; text-align: center; }
        }
    </style>
</head>
<body>
<header class="hero">
    <h1>🌿 Gardenify</h1>
    <p class="tagline">Identify any plant, flower, leaf, or fruit with your camera. Powered by PlantNet AI and a database of 50,000+ species.</p>
    <div class="badges">
        <span>v1.0.0</span>
        <a href="/docs">Swagger API</a>
        <a href="https://github.com/luckyhegde6/gardenify" target="_blank">GitHub</a>
        <a href="https://github.com/luckyhegde6/gardenify/releases" target="_blank">Download APK</a>
    </div>
    <div class="nav-links">
        <a href="#features">Features</a>
        <a href="#api">API</a>
        <a href="#download">Download</a>
        <a href="#about">About</a>
        <a href="#tech">Tech</a>
        <a href="/onboarding">How It Works</a>
    </div>
</header>

<section id="features">
    <div class="container">
        <h2>Features</h2>
        <p class="subtitle">Everything you need to identify and care for plants</p>
        <div class="cards">
            <div class="card">
                <h3>📷 Identify Any Plant</h3>
                <p>Snap a photo of a leaf, flower, fruit, or bark and get instant species identification with confidence scores.</p>
                <a href="/docs/#/default/identify_plant_identify_post">Try the API &rarr;</a>
            </div>
            <div class="card">
                <h3>🔬 Disease Detection</h3>
                <p>Automatically detects plant diseases alongside species identification. Get treatment recommendations.</p>
                <a href="/docs/#/default/identify_plant_identify_post">Learn more &rarr;</a>
            </div>
            <div class="card">
                <h3>🌱 Plant Care Guides</h3>
                <p>Watering frequency, sunlight needs, soil type, temperature range, and propagation tips for every species.</p>
                <a href="/docs/#/Species/list_species_species_get">Browse species &rarr;</a>
            </div>
            <div class="card">
                <h3>📊 Species Database</h3>
                <p>Search over 10,000 species by scientific name, common name, genus, or family with fuzzy matching.</p>
                <a href="/docs/#/Species/list_species_species_get">Explore &rarr;</a>
            </div>
            <div class="card">
                <h3>⚡ Instant Matching</h3>
                <p>Previous identifications are cached for quick re-checking, and a perceptual-hash species store matches known plants before PlantNet is called.</p>
                <a href="https://github.com/luckyhegde6/gardenify" target="_blank">Read more &rarr;</a>
            </div>
            <div class="card">
                <h3>🔐 Admin Dashboard</h3>
                <p>User management with role-based access control. Promote users, manage tiers, and monitor activity.</p>
                <a href="/docs/#/Admin/list_users_admin_users_get">Admin API &rarr;</a>
            </div>
        </div>
    </div>
</section>

<section id="api" style="background: var(--gray-50);">
    <div class="container">
        <h2>API Endpoints</h2>
        <p class="subtitle">REST API available at <code style="background:var(--gray-200);padding:0.15rem 0.4rem;border-radius:4px;">https://sasyakashi.vercel.app</code></p>
        <table class="endpoint-table">
            <thead><tr><th>Method</th><th>Endpoint</th><th>Description</th></tr></thead>
            <tbody>
                <tr><td><span class="method method-get">GET</span></td><td><code>/api/health</code></td><td>Health check, version, and debug info</td></tr>
                <tr><td><span class="method method-post">POST</span></td><td><code>/api/identify</code></td><td>Identify plant from images (multipart/form-data)</td></tr>
                <tr><td><span class="method method-get">GET</span></td><td><code>/api/species?q={query}&amp;limit={n}</code></td><td>Fuzzy search 10,000+ species</td></tr>
                <tr><td><span class="method method-get">GET</span></td><td><code>/api/species/{id}</code></td><td>Species details by ID</td></tr>
                <tr><td><span class="method method-get">GET</span></td><td><code>/api/species/by-name/{name}</code></td><td>Species by scientific name</td></tr>
                <tr><td><span class="method method-get">GET</span></td><td><code>/api/history</code></td><td>Past identifications (list + detail + thumbnails)</td></tr>
                <tr><td><span class="method method-get">GET</span></td><td><code>/api/admin/users</code></td><td>List all users <em>(admin, JWT)</em></td></tr>
                <tr><td><span class="method method-patch">PATCH</span></td><td><code>/api/admin/users/{id}</code></td><td>Update user role or tier <em>(admin, JWT)</em></td></tr>
                <tr><td><span class="method method-delete">DELETE</span></td><td><code>/api/admin/users/{id}</code></td><td>Soft-delete user <em>(admin, JWT)</em></td></tr>
            </tbody>
        </table>
        <p style="margin-top: 1rem; font-size: 0.9rem; color: var(--gray-500);">
            Full interactive documentation at <a href="/docs">Swagger UI</a>
        </p>
    </div>
</section>

<section id="download">
    <div class="container download-section">
        <h2>Download the App</h2>
        <p class="subtitle">Get Gardenify on your Android device</p>
        <div class="download-grid">
            <div class="download-qr">
                <img src="https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=https://github.com/luckyhegde6/gardenify/releases&bgcolor=ffffff&color=166534" alt="QR Code pointing to GitHub Releases">
                <p style="margin-top: 0.5rem; color: var(--gray-400); font-size: 0.8rem;">Scan to download the latest APK</p>
            </div>
            <div class="download-info">
                <div class="badge-release">Latest Release</div>
                <h3>Android APK</h3>
                <p>Download the latest APK from GitHub Releases. No Play Store required — direct installation via APK.</p>
                <a href="https://github.com/luckyhegde6/gardenify/releases" target="_blank" class="download-btn">⬇ Download APK</a>
                <div class="download-steps" style="margin-top: 1rem;">
                    <p style="font-weight: 600; margin-bottom: 0.25rem;">Installation steps:</p>
                    <ol>
                        <li>Download the APK from GitHub Releases</li>
                        <li>On Android: enable <strong>Install from unknown sources</strong></li>
                        <li>Open the APK file to install</li>
                    </ol>
                </div>
            </div>
        </div>
    </div>
</section>

<section id="about" style="background: var(--gray-50);">
    <div class="container">
        <h2>About Gardenify</h2>
        <p class="subtitle">An open-source plant identification app built with modern tools</p>
        <div class="about-content">
            <p>Gardenify is a free and open-source plant identification application. It combines computer vision, a comprehensive species database, and the PlantNet API to provide accurate plant identification with disease detection and care recommendations.</p>
            <p>The entire project is open-source and available on GitHub. Contributions, bug reports, and feature requests are welcome.</p>

            <div class="profile">
                <div class="avatar">👤</div>
                <div class="info">
                    <h3>Created by Lucky Hegde</h3>
                    <p>Full-stack developer and plant enthusiast. Built Gardenify to combine a love for nature with modern mobile and AI technologies.</p>
                    <p style="margin-top: 0.5rem;">
                        <a href="https://github.com/luckyhegde6" target="_blank">GitHub &rarr;</a>
                    </p>
                </div>
            </div>

            <div class="contributing">
                <h3>🤝 Contributing</h3>
                <p>Gardenify is open-source and welcomes contributions of all kinds — bug fixes, new features, documentation improvements, and more.</p>
                <p>To contribute:</p>
                <ol style="padding-left: 1.25rem; color: var(--gray-600); font-size: 0.9rem;">
                    <li>Fork the <a href="https://github.com/luckyhegde6/gardenify" target="_blank">repository</a></li>
                    <li>Create a feature branch</li>
                    <li>Make your changes</li>
                    <li>Submit a pull request</li>
                </ol>
                <p style="margin-top: 0.75rem;">
                    <a href="https://github.com/luckyhegde6/gardenify/blob/main/README.md" target="_blank">View the README &rarr;</a> &middot;
                    <a href="https://github.com/luckyhegde6/gardenify/issues" target="_blank">Report an Issue &rarr;</a>
                </p>
            </div>
        </div>
    </div>
</section>

<section id="tech">
    <div class="container">
        <h2>Technology Stack</h2>
        <p class="subtitle">Built with modern, scalable technologies</p>
        <div class="tech-grid">
            <div class="tech-item"><div class="label">Mobile</div><div class="value">Expo SDK 55</div></div>
            <div class="tech-item"><div class="label">Language</div><div class="value">TypeScript 5.9</div></div>
            <div class="tech-item"><div class="label">Backend</div><div class="value">FastAPI + Python</div></div>
            <div class="tech-item"><div class="label">Database</div><div class="value">Supabase (PostgreSQL)</div></div>
            <div class="tech-item"><div class="label">Plant AI</div><div class="value">PlantNet API v2</div></div>
            <div class="tech-item"><div class="label">Auth</div><div class="value">Supabase Auth</div></div>
            <div class="tech-item"><div class="label">Build</div><div class="value">EAS Build</div></div>
            <div class="tech-item"><div class="label">CI/CD</div><div class="value">GitHub Actions</div></div>
            <div class="tech-item"><div class="label">Hosting</div><div class="value">Vercel Serverless</div></div>
            <div class="tech-item"><div class="label">Storage</div><div class="value">Supabase Storage</div></div>
        </div>
    </div>
</section>

<footer>
    <p>Gardenify &copy; 2026 &mdash; Open source and free for everyone</p>
    <div class="footer-links">
        <a href="https://github.com/luckyhegde6/gardenify" target="_blank">GitHub</a>
        <a href="/docs">API Docs</a>
        <a href="/api/health">API Status</a>
        <a href="/onboarding">How It Works</a>
        <a href="/about">About</a>
        <a href="https://github.com/luckyhegde6" target="_blank">Author</a>
        <a href="https://github.com/luckyhegde6/gardenify/releases" target="_blank">Downloads</a>
    </div>
</footer>
</body>
</html>"""

ABOUT_PAGE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>About — Gardenify</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🌿</text></svg>">
    <style>
        :root {
            --green-600: #16a34a; --green-700: #15803d; --green-800: #166534;
            --gray-50: #f9fafb; --gray-100: #f3f4f6; --gray-200: #e5e7eb;
            --gray-400: #9ca3af; --gray-500: #6b7280; --gray-600: #4b5563;
            --gray-700: #374151; --gray-800: #1f2937; --gray-900: #111827;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: var(--gray-800); background: var(--gray-50); line-height: 1.6; }
        a { color: var(--green-600); text-decoration: none; }
        a:hover { text-decoration: underline; }
        .header { background: linear-gradient(135deg, var(--green-800), var(--green-600)); color: white; padding: 2rem 1.5rem; text-align: center; }
        .header a { color: rgba(255,255,255,0.85); }
        .header a:hover { color: white; }
        .container { max-width: 720px; margin: 0 auto; padding: 3rem 1.5rem; }
        section { margin-bottom: 2.5rem; }
        h1 { font-size: 2rem; margin-bottom: 0.25rem; }
        h2 { font-size: 1.4rem; color: var(--green-800); margin-bottom: 1rem; }
        p { color: var(--gray-600); margin-bottom: 1rem; }
        .profile { display: flex; align-items: center; gap: 1.5rem; background: white; border: 1px solid var(--gray-200); border-radius: 12px; padding: 1.5rem; margin: 1.5rem 0; }
        .profile .avatar { width: 72px; height: 72px; border-radius: 50%; background: var(--gray-100); display: flex; align-items: center; justify-content: center; font-size: 2.25rem; flex-shrink: 0; }
        .profile .info h3 { margin-bottom: 0.25rem; }
        .profile .info p { color: var(--gray-500); font-size: 0.9rem; margin-bottom: 0; }
        .card { background: white; border: 1px solid var(--gray-200); border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; }
        .card h3 { margin-bottom: 0.5rem; }
        .card p { font-size: 0.9rem; }
        .card a { font-weight: 600; }
        .card ol { padding-left: 1.25rem; color: var(--gray-600); font-size: 0.9rem; }
        .card ol li { margin-bottom: 0.3rem; }
        footer { text-align: center; padding: 2rem; color: var(--gray-400); font-size: 0.85rem; border-top: 1px solid var(--gray-200); }
        footer a { color: var(--green-600); }
        .btn { display: inline-block; background: var(--green-600); color: white; padding: 0.6rem 1.25rem; border-radius: 8px; font-weight: 600; text-decoration: none; }
        .btn:hover { background: var(--green-700); text-decoration: none; }
        @media (max-width: 640px) { .profile { flex-direction: column; text-align: center; } }
    </style>
</head>
<body>
<div class="header">
    <h1>🌿 About Gardenify</h1>
    <p><a href="/">&larr; Back to Home</a></p>
</div>
<div class="container">
    <section>
        <h2>The Project</h2>
        <p>Gardenify is a free and open-source plant identification application. It uses computer vision and the PlantNet API to identify plants, detect diseases, and provide care recommendations from photos captured on your phone.</p>
        <p>The entire stack is modern and open: an <strong>Expo React Native</strong> mobile app, a <strong>FastAPI</strong> Python backend on Vercel, <strong>Supabase</strong> for authentication and database, and <strong>PlantNet</strong> for AI-powered species identification.</p>
    </section>

    <section>
        <h2>Creator</h2>
        <div class="profile">
            <div class="avatar">👤</div>
            <div class="info">
                <h3>Lucky Hegde</h3>
                <p>Full-stack developer passionate about building useful tools that connect people with nature. Gardenify combines software engineering with a love for plants and the outdoors.</p>
                <p style="margin-top: 0.5rem;">
                    <a href="https://github.com/luckyhegde6" target="_blank">GitHub Profile &rarr;</a>
                    &middot;
                    <a href="https://github.com/luckyhegde6/gardenify" target="_blank">Project Repository &rarr;</a>
                </p>
            </div>
        </div>
    </section>

    <section>
        <h2>Contributing</h2>
        <div class="card">
            <h3>🤝 How to Contribute</h3>
            <p>Gardenify welcomes contributions from the community. Whether you're fixing a bug, adding a feature, improving documentation, or writing tests — every contribution helps.</p>
            <ol>
                <li>Fork the <a href="https://github.com/luckyhegde6/gardenify" target="_blank">repository</a> on GitHub</li>
                <li>Create a branch: <code>feat/your-feature</code> or <code>bugfix/your-fix</code></li>
                <li>Make your changes following the project's conventions</li>
                <li>Run tests: <code>npx tsc --noEmit && pytest && npx jest --no-cache</code></li>
                <li>Submit a <a href="https://github.com/luckyhegde6/gardenify/pulls" target="_blank">pull request</a></li>
            </ol>
            <p style="margin-top: 0.75rem;">
                <a href="https://github.com/luckyhegde6/gardenify/blob/main/README.md" target="_blank">📖 Read the README &rarr;</a>
                &middot;
                <a href="https://github.com/luckyhegde6/gardenify/issues" target="_blank">🐛 Report an Issue &rarr;</a>
            </p>
        </div>

        <div class="card">
            <h3>📋 Development Setup</h3>
            <p>To set up the project locally:</p>
            <ol>
                <li><code>git clone https://github.com/luckyhegde6/gardenify.git</code></li>
                <li><code>npm install</code></li>
                <li><code>pip install -r api/requirements.txt</code></li>
                <li><code>cp .env.example .env</code> and fill in your keys</li>
                <li><code>uvicorn api.main:app --reload --port 8000</code> (backend)</li>
                <li><code>npx expo start</code> (mobile app)</li>
            </ol>
            <p style="margin-top: 0.75rem;">
                <a href="https://github.com/luckyhegde6/gardenify/blob/main/README.md" target="_blank">Full setup guide &rarr;</a>
            </p>
        </div>
    </section>

    <section style="text-align: center;">
        <a href="https://github.com/luckyhegde6/gardenify" target="_blank" class="btn">View on GitHub</a>
        &ensp;
        <a href="https://github.com/luckyhegde6/gardenify/releases" target="_blank" class="btn" style="background: var(--gray-700);">Download APK</a>
    </section>
</div>
<footer>
    <p>Gardenify &copy; 2026 &middot; <a href="https://github.com/luckyhegde6" target="_blank">Lucky Hegde</a> &middot; <a href="/">Home</a> &middot; <a href="/onboarding">How It Works</a></p>
</footer>
</body>
</html>"""
