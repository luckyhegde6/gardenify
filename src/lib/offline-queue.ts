import AsyncStorage from "@react-native-async-storage/async-storage";

const QUEUE_KEY = "gardenify:offline_queue";

interface QueuedScan {
  id: string;
  imageUris: string[];
  organs: string[];
  timestamp: number;
}

export const offlineQueue = {
  async add(item: Omit<QueuedScan, "timestamp">): Promise<void> {
    try {
      const queue = await this.getAll();
      queue.push({ ...item, timestamp: Date.now() });
      await AsyncStorage.setItem(QUEUE_KEY, JSON.stringify(queue));
    } catch {
      console.error("Failed to add to offline queue");
    }
  },

  async getAll(): Promise<QueuedScan[]> {
    try {
      const raw = await AsyncStorage.getItem(QUEUE_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch {
      return [];
    }
  },

  async remove(id: string): Promise<void> {
    try {
      const queue = await this.getAll();
      const filtered = queue.filter((item) => item.id !== id);
      await AsyncStorage.setItem(QUEUE_KEY, JSON.stringify(filtered));
    } catch {
      console.error("Failed to remove from offline queue");
    }
  },

  async clear(): Promise<void> {
    try {
      await AsyncStorage.removeItem(QUEUE_KEY);
    } catch {}
  },

  async count(): Promise<number> {
    const queue = await this.getAll();
    return queue.length;
  },
};
