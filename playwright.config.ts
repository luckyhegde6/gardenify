import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html', { outputFolder: 'e2e/report' }],
    ['list'],
  ],
  use: {
    baseURL: process.env.API_BASE_URL || 'http://localhost:8000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'api-tests',
      testDir: './e2e/api-tests',
      use: {
        ...devices['Desktop Chrome'],
        baseURL: process.env.API_BASE_URL || 'http://localhost:8000',
      },
    },
    {
      name: 'visual-tests',
      testDir: './e2e/visual',
      use: {
        ...devices['Desktop Chrome'],
        baseURL: process.env.API_BASE_URL || 'http://localhost:8000',
      },
    },
  ],
  outputDir: 'e2e/results',
});
