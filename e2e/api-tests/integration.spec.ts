import { test, expect } from '@playwright/test';

const API_BASE = process.env.API_BASE_URL || 'http://localhost:8000';

// Test data for API testing
const TEST_JPEG = Buffer.from([
  0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01,
  0x01, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0xFF, 0xD9,
]);

test.describe('Full Plant Identification Flow', () => {
  test('complete identification workflow', async ({ request }) => {
    // Step 1: Check health
    const healthResponse = await request.get(`${API_BASE}/api/health`);
    expect(healthResponse.ok()).toBeTruthy();

    // Step 2: Check debug info
    const debugResponse = await request.get(`${API_BASE}/api/debug`);
    expect(debugResponse.ok()).toBeTruthy();

    // Step 3: Attempt identification
    const identifyResponse = await request.post(`${API_BASE}/api/identify`, {
      multipart: {
        images: {
          name: 'rose.jpg',
          mimeType: 'image/jpeg',
          buffer: TEST_JPEG,
        },
        organs: '["flower"]',
      },
    });

    // Should return 200 (success) or 502 (PlantNet API error)
    expect([200, 502]).toContain(identifyResponse.status());

    if (identifyResponse.status() === 200) {
      const data = await identifyResponse.json();
      expect(data).toHaveProperty('best_match');
      expect(data).toHaveProperty('results');
      expect(data).toHaveProperty('cached');
      expect(data).toHaveProperty('identification_id');
    }
  });

  test('caching works for repeated requests', async ({ request }) => {
    const formData = {
      images: {
        name: 'test.jpg',
        mimeType: 'image/jpeg',
        buffer: TEST_JPEG,
      },
      organs: '["leaf"]',
    };

    // First request
    const response1 = await request.post(`${API_BASE}/api/identify`, {
      multipart: formData,
    });

    if (response1.status() === 200) {
      const data1 = await response1.json();
      expect(data1.cached).toBe(false);

      // Second request (should be cached)
      const response2 = await request.post(`${API_BASE}/api/identify`, {
        multipart: formData,
      });

      if (response2.status() === 200) {
        const data2 = await response2.json();
        expect(data2.cached).toBe(true);
        expect(data2.identification_id).toBe(data1.identification_id);
      }
    }
  });
});

test.describe('Error Recovery', () => {
  test('server recovers after invalid request', async ({ request }) => {
    // Send invalid request
    const invalidResponse = await request.post(`${API_BASE}/api/identify`, {
      multipart: {
        images: {
          name: 'test.txt',
          mimeType: 'text/plain',
          buffer: Buffer.from('not an image'),
        },
        organs: '["leaf"]',
      },
    });
    expect(invalidResponse.status()).toBe(400);

    // Server should still be healthy
    const healthResponse = await request.get(`${API_BASE}/api/health`);
    expect(healthResponse.ok()).toBeTruthy();
  });

  test('concurrent requests do not crash server', async ({ request }) => {
    const requests = Array(5).fill(null).map(() =>
      request.get(`${API_BASE}/api/health`)
    );

    const responses = await Promise.all(requests);
    responses.forEach(response => {
      expect(response.ok()).toBeTruthy();
    });
  });
});

test.describe('Security Headers', () => {
  test('API does not expose sensitive headers', async ({ request }) => {
    const response = await request.get(`${API_BASE}/api/health`);
    const headers = response.headers();

    // Should not expose server details
    expect(headers['server']).toBeUndefined();
    expect(headers['x-powered-by']).toBeUndefined();
  });

  test('Correlation ID is unique per request', async ({ request }) => {
    const response1 = await request.get(`${API_BASE}/api/health`);
    const response2 = await request.get(`${API_BASE}/api/health`);

    const cid1 = response1.headers()['x-correlation-id'];
    const cid2 = response2.headers()['x-correlation-id'];

    expect(cid1).toBeTruthy();
    expect(cid2).toBeTruthy();
    expect(cid1).not.toBe(cid2);
  });
});
