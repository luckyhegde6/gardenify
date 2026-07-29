import { test, expect } from "@playwright/test";
import * as fs from "fs";
import * as path from "path";

const API_BASE = process.env.API_BASE_URL || "http://localhost:8000";
const FIXTURES = path.resolve(__dirname, "fixtures");

function loadFixture(name: string): Buffer {
  return fs.readFileSync(path.join(FIXTURES, name));
}

test.describe("Full Plant Identification Flow", () => {
  test("complete identification workflow", async ({ request }) => {
    const healthResponse = await request.get(`${API_BASE}/api/health`);
    expect(healthResponse.ok()).toBeTruthy();

    const debugResponse = await request.get(`${API_BASE}/api/debug`);
    expect(debugResponse.ok()).toBeTruthy();

    const identifyResponse = await request.post(`${API_BASE}/api/identify`, {
      multipart: {
        images: {
          name: "flower.jpg",
          mimeType: "image/jpeg",
          buffer: loadFixture("flower.jpg"),
        },
        organs: '["flower"]',
      },
    });

    expect([200, 502]).toContain(identifyResponse.status());

    if (identifyResponse.status() === 200) {
      const data = await identifyResponse.json();
      expect(data).toHaveProperty("best_match");
      expect(data).toHaveProperty("results");
      expect(data).toHaveProperty("cached");
      expect(data).toHaveProperty("identification_id");
      expect(data).toHaveProperty("source");
      expect(data.metadata).toBeInstanceOf(Array);
      expect(data.metadata.length).toBe(1);

      const m = data.metadata[0];
      expect(m).toHaveProperty("filename", "flower.jpg");
      expect(m).toHaveProperty("size_bytes");
      expect(m).toHaveProperty("compressed_size_bytes");
      expect(m).toHaveProperty("thumbnail_size_bytes");
      expect(m).toHaveProperty("compression_ratio");
      expect(m).toHaveProperty("width");
      expect(m).toHaveProperty("height");
      expect(m).toHaveProperty("format", "JPEG");
      expect(m).toHaveProperty("hash_sha256");
      expect(m).toHaveProperty("opencv");
      expect(m.opencv.valid).toBe(true);
      expect(m.opencv.is_plant_like).toBe(true);
      expect(typeof m.opencv.edges_detected).toBe("number");
      expect(typeof m.opencv.content_score).toBe("number");
      expect(m.opencv.dominant_colors).toBeInstanceOf(Array);
      expect(m.opencv.mean_color).toBeInstanceOf(Array);
      expect(m).toHaveProperty("exif");
      expect(typeof m.exif).toBe("object");
      expect(m).toHaveProperty("storage");
      expect(m.storage).toHaveProperty("upload_id");
      expect(m.storage).toHaveProperty("original");
      expect(m.storage).toHaveProperty("compressed");
      expect(m.storage).toHaveProperty("thumbnail");
    }
  });

  test("caching works for repeated requests", async ({ request }) => {
    const base = loadFixture("leaf.jpg");
    const tag = crypto.randomUUID().slice(0, 8);
    const unique = Buffer.concat([base, Buffer.from(tag)]);

    const formData = {
      images: {
        name: "leaf.jpg",
        mimeType: "image/jpeg",
        buffer: unique,
      },
      organs: '["leaf"]',
    };

    const response1 = await request.post(`${API_BASE}/api/identify`, {
      multipart: formData,
    });

    if (response1.status() === 200) {
      const data1 = await response1.json();
      expect(data1.cached).toBe(false);

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

test.describe("Error Recovery", () => {
  test("server recovers after invalid request", async ({ request }) => {
    const invalidResponse = await request.post(`${API_BASE}/api/identify`, {
      multipart: {
        images: {
          name: "test.txt",
          mimeType: "text/plain",
          buffer: Buffer.from("not an image"),
        },
        organs: '["leaf"]',
      },
    });
    expect(invalidResponse.status()).toBe(400);

    const healthResponse = await request.get(`${API_BASE}/api/health`);
    expect(healthResponse.ok()).toBeTruthy();
  });

  test("concurrent requests do not crash server", async ({ request }) => {
    const requests = Array(5)
      .fill(null)
      .map(() => request.get(`${API_BASE}/api/health`));

    const responses = await Promise.all(requests);
    responses.forEach((response) => {
      expect(response.ok()).toBeTruthy();
    });
  });
});

test.describe("Security Headers", () => {
  test("API does not expose sensitive headers", async ({ request }) => {
    const response = await request.get(`${API_BASE}/api/health`);
    const headers = response.headers();

    expect(headers["server"]).toBeUndefined();
    expect(headers["x-powered-by"]).toBeUndefined();
  });

  test("Correlation ID is unique per request", async ({ request }) => {
    const response1 = await request.get(`${API_BASE}/api/health`);
    const response2 = await request.get(`${API_BASE}/api/health`);

    const cid1 = response1.headers()["x-correlation-id"];
    const cid2 = response2.headers()["x-correlation-id"];

    expect(cid1).toBeTruthy();
    expect(cid2).toBeTruthy();
    expect(cid1).not.toBe(cid2);
  });
});
