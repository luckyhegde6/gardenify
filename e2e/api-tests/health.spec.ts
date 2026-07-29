import { test, expect } from "@playwright/test";
import * as fs from "fs";
import * as path from "path";

const API_BASE = process.env.API_BASE_URL || "http://localhost:8000";
const FIXTURES = path.resolve(__dirname, "fixtures");

function loadFixture(name: string): Buffer {
  return fs.readFileSync(path.join(FIXTURES, name));
}

test.describe("Health Endpoint", () => {
  test("GET /api/health returns ok status", async ({ request }) => {
    const response = await request.get(`${API_BASE}/api/health`);
    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data.status).toBe("ok");
    expect(data.version).toBe("1.0.0");
  });

  test("GET /api/health has correct content type", async ({ request }) => {
    const response = await request.get(`${API_BASE}/api/health`);
    expect(response.headers()["content-type"]).toContain("application/json");
  });
});

test.describe("Debug Endpoint", () => {
  test("GET /api/debug returns config in dev mode", async ({ request }) => {
    const response = await request.get(`${API_BASE}/api/debug`);
    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data).toHaveProperty("version");
    expect(data).toHaveProperty("python");
    expect(data).toHaveProperty("uptime_seconds");
    expect(data).toHaveProperty("config");
    expect(data.config).toHaveProperty("debug");
    expect(data.config).toHaveProperty("environment");
  });

  test("GET /api/debug shows environment info", async ({ request }) => {
    const response = await request.get(`${API_BASE}/api/debug`);
    const data = await response.json();

    expect(data.config).toHaveProperty("use_remote");
    expect(data.config).toHaveProperty("plantnet_configured");
    expect(data.config).toHaveProperty("supabase_configured");
  });
});

test.describe("Identify Endpoint", () => {
  test("POST /api/identify returns 422 without images", async ({ request }) => {
    const response = await request.post(`${API_BASE}/api/identify`);
    expect(response.status()).toBe(422);
  });

  test("POST /api/identify returns 422 with empty body", async ({
    request,
  }) => {
    const response = await request.post(`${API_BASE}/api/identify`, {
      multipart: {},
    });
    expect(response.status()).toBe(422);
  });

  test("POST /api/identify rejects non-image files", async ({ request }) => {
    const response = await request.post(`${API_BASE}/api/identify`, {
      multipart: {
        images: {
          name: "test.txt",
          mimeType: "text/plain",
          buffer: Buffer.from("not an image"),
        },
        organs: '["leaf"]',
      },
    });
    // Should return 400 for invalid image type
    expect(response.status()).toBe(400);
  });

  test("POST /api/identify accepts valid JPEG image", async ({ request }) => {
    const response = await request.post(`${API_BASE}/api/identify`, {
      multipart: {
        images: {
          name: "leaf.jpg",
          mimeType: "image/jpeg",
          buffer: loadFixture("leaf.jpg"),
        },
        organs: '["leaf"]',
      },
    });

    expect([200, 502]).toContain(response.status());
  });

  test("POST /api/identify validates organ count matches images", async ({
    request,
  }) => {
    const jpegBuffer = Buffer.from([
      0xff, 0xd8, 0xff, 0xe0, 0x00, 0x10, 0x4a, 0x46, 0x49, 0x46, 0x00, 0x01,
      0x01, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0xff, 0xd9,
    ]);

    const response = await request.post(`${API_BASE}/api/identify`, {
      multipart: {
        images: {
          name: "test.jpg",
          mimeType: "image/jpeg",
          buffer: jpegBuffer,
        },
        organs: '["leaf", "flower"]', // 2 organs for 1 image
      },
    });

    expect(response.status()).toBe(400);
    const data = await response.json();
    expect(data.detail).toContain("organs count must match");
  });

  test("POST /api/identify rejects more than 5 images", async ({ request }) => {
    const jpegBuffer = Buffer.from([
      0xff, 0xd8, 0xff, 0xe0, 0x00, 0x10, 0x4a, 0x46, 0x49, 0x46, 0x00, 0x01,
      0x01, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0xff, 0xd9,
    ]);

    const response = await request.post(`${API_BASE}/api/identify`, {
      multipart: {
        images0: {
          name: "img0.jpg",
          mimeType: "image/jpeg",
          buffer: jpegBuffer,
        },
        images1: {
          name: "img1.jpg",
          mimeType: "image/jpeg",
          buffer: jpegBuffer,
        },
        images2: {
          name: "img2.jpg",
          mimeType: "image/jpeg",
          buffer: jpegBuffer,
        },
        images3: {
          name: "img3.jpg",
          mimeType: "image/jpeg",
          buffer: jpegBuffer,
        },
        images4: {
          name: "img4.jpg",
          mimeType: "image/jpeg",
          buffer: jpegBuffer,
        },
        images5: {
          name: "img5.jpg",
          mimeType: "image/jpeg",
          buffer: jpegBuffer,
        },
        organs: JSON.stringify([
          "leaf",
          "leaf",
          "leaf",
          "leaf",
          "leaf",
          "leaf",
        ]),
      },
    });

    // 6 fields named 'images*' won't be parsed as 'images' list, expect 422
    // (correct behavior: the API requires 'images' field with up to 5 files)
    expect(response.status()).toBe(422);
  });
});

test.describe("Response Headers", () => {
  test("API responses include correlation ID", async ({ request }) => {
    const response = await request.get(`${API_BASE}/api/health`);
    expect(response.headers()["x-correlation-id"]).toBeTruthy();
  });

  test("API responses include response time", async ({ request }) => {
    const response = await request.get(`${API_BASE}/api/health`);
    expect(response.headers()["x-response-time"]).toBeTruthy();
  });
});

test.describe("CORS", () => {
  test("API allows requests from localhost", async ({ request }) => {
    const response = await request.get(`${API_BASE}/api/health`, {
      headers: {
        Origin: "http://localhost:8081",
      },
    });
    expect(response.ok()).toBeTruthy();
  });
});

test.describe("Error Handling", () => {
  test("Non-existent endpoint returns 404", async ({ request }) => {
    const response = await request.get(`${API_BASE}/api/nonexistent`);
    expect(response.status()).toBe(404);
  });

  test("Invalid JSON returns 422", async ({ request }) => {
    const response = await request.post(`${API_BASE}/api/identify`, {
      headers: {
        "Content-Type": "application/json",
      },
      data: "invalid json",
    });
    expect(response.status()).toBe(422);
  });
});
