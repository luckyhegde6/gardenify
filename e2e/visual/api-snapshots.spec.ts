import { test, expect } from '@playwright/test';

const API_BASE = process.env.API_BASE_URL || 'http://localhost:8000';

test.describe('API Visual Snapshot Tests', () => {
  test('Health endpoint response structure', async ({ request }) => {
    const response = await request.get(`${API_BASE}/api/health`);
    const data = await response.json();

    // Snapshot the response structure
    expect(data).toMatchObject({
      status: expect.any(String),
      version: expect.any(String),
    });
  });

  test('Debug endpoint response structure', async ({ request }) => {
    const response = await request.get(`${API_BASE}/api/debug`);
    const data = await response.json();

    // Snapshot the full debug response
    expect(data).toMatchObject({
      version: expect.any(String),
      python: expect.any(String),
      uptime_seconds: expect.any(Number),
      timestamp: expect.any(String),
      config: {
        debug: expect.any(Boolean),
        environment: expect.any(String),
        use_remote: expect.any(Boolean),
        plantnet_configured: expect.any(Boolean),
        supabase_configured: expect.any(Boolean),
        max_images: expect.any(Number),
        cors_origins: expect.any(Array),
      },
      cache: {
        total_entries: expect.any(Number),
        alive_entries: expect.any(Number),
        ttl_seconds: expect.any(Number),
      },
    });
  });

  test('Identify endpoint error response structure', async ({ request }) => {
    const response = await request.post(`${API_BASE}/api/identify`);
    const data = await response.json();

    // 422 validation error structure
    expect(data).toHaveProperty('detail');
  });
});

test.describe('API Response Time Tests', () => {
  test('Health endpoint responds within 100ms', async ({ request }) => {
    const start = Date.now();
    const response = await request.get(`${API_BASE}/api/health`);
    const duration = Date.now() - start;

    expect(response.ok()).toBeTruthy();
    expect(duration).toBeLessThan(100);
  });

  test('Debug endpoint responds within 200ms', async ({ request }) => {
    const start = Date.now();
    const response = await request.get(`${API_BASE}/api/debug`);
    const duration = Date.now() - start;

    expect(response.ok()).toBeTruthy();
    expect(duration).toBeLessThan(200);
  });

  test('Identify endpoint responds within 5000ms (validation only)', async ({ request }) => {
    const start = Date.now();
    const response = await request.post(`${API_BASE}/api/identify`);
    const duration = Date.now() - start;

    // Validation error should be fast
    expect(duration).toBeLessThan(5000);
  });
});

test.describe('API Consistency Tests', () => {
  test('Health endpoint returns consistent data', async ({ request }) => {
    const response1 = await request.get(`${API_BASE}/api/health`);
    const response2 = await request.get(`${API_BASE}/api/health`);

    const data1 = await response1.json();
    const data2 = await response2.json();

    // Status and version should be identical
    expect(data1.status).toBe(data2.status);
    expect(data1.version).toBe(data2.version);
  });

  test('Debug endpoint uptime increases', async ({ request }) => {
    const response1 = await request.get(`${API_BASE}/api/debug`);
    const data1 = await response1.json();

    // Wait 1 second
    await new Promise(resolve => setTimeout(resolve, 1000));

    const response2 = await request.get(`${API_BASE}/api/debug`);
    const data2 = await response2.json();

    expect(data2.uptime_seconds).toBeGreaterThanOrEqual(data1.uptime_seconds);
  });
});
