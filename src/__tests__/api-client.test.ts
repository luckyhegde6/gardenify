import { apiClient } from "@/lib/api-client";
import type { IdentificationResponse } from "@/lib/types";

const mockIdentifyResponse: IdentificationResponse = {
  best_match: "Rosa damascena",
  results: [
    {
      score: 0.95,
      species: {
        scientific_name: "Rosa damascena",
        common_names: ["Damask Rose"],
        family: "Rosaceae",
        genus: "Rosa",
      },
    },
  ],
  disease: null,
  care: null,
  metadata: [],
  remaining_quota: 490,
  version: "1.0",
  cached: false,
  identification_id: "uuid-123",
  source: "plantnet",
};

const mockSpeciesResponse = {
  count: 2,
  total_species: 100,
  total_hashes: 50,
  results: [
    {
      id: 1,
      scientific_name: "Rosa damascena",
      common_names: ["Damask Rose"],
      family: "Rosaceae",
      genus: "Rosa",
      common_name: "Damask Rose",
    },
    {
      id: 2,
      scientific_name: "Rosa gallica",
      common_names: ["French Rose"],
      family: "Rosaceae",
      genus: "Rosa",
      common_name: "French Rose",
    },
  ],
};

const mockHealthResponse = { status: "ok", version: "1.1.0" };

function mockFetch(response: unknown, status = 200) {
  return (global.fetch = jest.fn().mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    json: async () => response,
    text: async () => JSON.stringify(response),
  }) as jest.Mock);
}

describe("apiClient", () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  describe("healthCheck", () => {
    it("returns health status", async () => {
      mockFetch(mockHealthResponse);
      const result = await apiClient.healthCheck();
      expect(result).toEqual(mockHealthResponse);
      expect(fetch).toHaveBeenCalledWith(expect.stringContaining("/health"));
    });
  });

  describe("identify", () => {
    it("sends POST request with form data", async () => {
      mockFetch(mockIdentifyResponse);
      const images = [{ uri: "file:///test.jpg" }];

      const result = await apiClient.identify(images);

      expect(result).toEqual(mockIdentifyResponse);
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining("/identify"),
        expect.objectContaining({ method: "POST", body: expect.any(FormData) }),
      );
    });

    it("includes organs and lang in form data", async () => {
      mockFetch(mockIdentifyResponse);
      const images = [{ uri: "file:///leaf.jpg" }];

      await apiClient.identify(images, ["leaf"], "fr");

      const callArgs = (fetch as jest.Mock).mock.calls[0];
      const formData = callArgs[1].body as FormData;
      expect(formData.get("organs")).toBe(JSON.stringify(["leaf"]));
      expect(formData.get("lang")).toBe("fr");
    });

    it("throws on non-ok response", async () => {
      mockFetch({ detail: "Bad request" }, 400);
      const images = [{ uri: "file:///test.jpg" }];

      await expect(apiClient.identify(images)).rejects.toThrow("Bad request");
    });
  });

  describe("searchSpecies", () => {
    it("sends GET request with query params", async () => {
      mockFetch(mockSpeciesResponse);

      const result = await apiClient.searchSpecies("Rosa");

      expect(result.count).toBe(2);
      expect(fetch).toHaveBeenCalledWith(expect.stringContaining("q=Rosa"));
    });

    it("includes limit parameter", async () => {
      mockFetch(mockSpeciesResponse);

      await apiClient.searchSpecies("Rosa", 5);

      expect(fetch).toHaveBeenCalledWith(expect.stringContaining("limit=5"));
    });
  });

  describe("getSpeciesByName", () => {
    it("encodes the species name", async () => {
      mockFetch(mockSpeciesResponse.results[0]);

      await apiClient.getSpeciesByName("Rosa damascena");

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining(encodeURIComponent("Rosa damascena")),
      );
    });

    it("returns species data", async () => {
      const species = mockSpeciesResponse.results[0];
      mockFetch(species);

      const result = await apiClient.getSpeciesByName("Rosa damascena");
      expect(result.scientific_name).toBe("Rosa damascena");
      expect(result.family).toBe("Rosaceae");
    });
  });
});
