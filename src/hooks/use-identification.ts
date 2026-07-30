import { useState, useCallback, useEffect, useRef } from "react";
import { apiClient } from "@/lib/api-client";
import { resultCache } from "@/lib/cache";
import { offlineQueue } from "@/lib/offline-queue";
import { useNetworkStatus } from "@/hooks/use-network-status";
import type { IdentificationResponse, OrganType } from "@/lib/types";

interface IdentifyOptions {
  organs?: OrganType[];
  lang?: string;
}

export function useIdentification() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<IdentificationResponse | null>(null);
  const { isConnected } = useNetworkStatus();
  const [queued, setQueued] = useState(false);

  const identify = useCallback(
    async (images: { uri: string }[], options: IdentifyOptions = {}) => {
      setLoading(true);
      setError(null);
      setResult(null);
      setQueued(false);

      const organs = options.organs ?? images.map(() => "auto" as OrganType);
      const lang = options.lang ?? "en";

      if (!isConnected) {
        const queueItem = {
          id: `${Date.now()}_${Math.random().toString(36).slice(2, 8)}`,
          imageUris: images.map((i) => i.uri),
          organs,
        };
        await offlineQueue.add(queueItem);
        setQueued(true);
        setLoading(false);
        throw new Error("OFFLINE_QUEUED");
      }

      try {
        const response = await apiClient.identify(images, organs, lang);
        if (response.identification_id) {
          await resultCache.set(response.identification_id, response);
        }
        setResult(response);
        return response;
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "Identification failed";
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [isConnected],
  );

  const processQueue = useCallback(async () => {
    const queue = await offlineQueue.getAll();
    if (queue.length === 0) return { processed: 0, failed: 0 };

    let processed = 0;
    let failed = 0;

    for (const item of queue) {
      try {
        const images = item.imageUris.map((uri) => ({ uri }));
        await apiClient.identify(images, item.organs, "en");
        await offlineQueue.remove(item.id);
        processed++;
      } catch {
        failed++;
      }
    }

    return { processed, failed };
  }, []);

  const wasOffline = useRef(false);

  useEffect(() => {
    if (wasOffline.current && isConnected) {
      processQueue();
    }
    wasOffline.current = !isConnected;
  }, [isConnected, processQueue]);

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
    setLoading(false);
    setQueued(false);
  }, []);

  return {
    identify,
    processQueue,
    loading,
    error,
    result,
    queued,
    reset,
    isConnected,
  };
}
