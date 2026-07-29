/**
 * Gardenify Plugin Hooks for OpenCode
 *
 * Auto-format, typecheck, security checks, and session management.
 * Adapted from ECC (affaan-m/ECC) patterns for Gardenify's Expo + FastAPI stack.
 *
 * Hook Event Mapping:
 * - PreToolUse -> tool.execute.before
 * - PostToolUse -> tool.execute.after
 * - Stop -> session.idle / session.status
 * - SessionStart -> session.created
 * - SessionEnd -> session.deleted
 */

import type { PluginInput } from "@opencode-ai/plugin"
import * as fs from "fs"
import * as path from "path"

interface ToolArgs {
  filePath?: string
  file_path?: string
  path?: string
  command?: string
  [key: string]: unknown
}

interface ToolInput {
  tool: string
  callID?: string
  args?: ToolArgs
}

export const GardenifyHooksPlugin = async ({
  client,
  $,
  directory,
  worktree,
}: PluginInput) => {
  const worktreePath = worktree || directory
  const editedFiles = new Set<string>()

  function resolvePath(p: string): string {
    if (path.isAbsolute(p)) return p
    return path.join(worktreePath, p)
  }

  function hasProjectFile(relativePath: string): boolean {
    try {
      return fs.statSync(resolvePath(relativePath)).isFile()
    } catch {
      return false
    }
  }

  const log = (level: "debug" | "info" | "warn" | "error", message: string) =>
    client.app.log({ body: { service: "gardenify", level, message } })

  return {
    /**
     * File Edit Hook
     * Tracks edited files and warns about console.log.
     * Formatting is handled by the built-in formatter (prettier/ruff).
     */
    "file.edited": async (event: { path: string }) => {
      editedFiles.add(event.path)

      if (!event.path.match(/\.(ts|tsx|js|jsx)$/)) return

      try {
        const result = await $`grep -n "console\\.log" ${event.path} 2>/dev/null`.text()
        if (result.trim()) {
          const lines = result.trim().split("\n").length
          log(
            "warn",
            `[Gardenify] console.log found in ${event.path} (${lines} occurrence${lines > 1 ? "s" : ""})`
          )
        }
      } catch {
        // No console.log found - good
      }
    },

    /**
     * Post-Tool Hook
     * Runs typecheck after TS file edits.
     */
    "tool.execute.after": async (input: ToolInput) => {
      // TypeScript check after editing .ts/.tsx files
      if (
        input.tool === "edit" &&
        input.args?.filePath?.match(/\.tsx?$/)
      ) {
        try {
          await $`npx tsc --noEmit 2>&1`
          log("info", "[Gardenify] TypeScript check passed")
        } catch (error: unknown) {
          log("warn", "[Gardenify] TypeScript errors detected")
          try {
            const out = (error as { message?: string }).message || ""
            out.split("\n").slice(0, 5).forEach((line: string) => {
              if (line.trim()) log("warn", `  ${line}`)
            })
          } catch {
            log("warn", "[Gardenify] Could not parse tsc output")
          }
        }
      }

      // Python lint check after editing .py files
      if (
        input.tool === "edit" &&
        input.args?.filePath?.match(/\.py$/)
      ) {
        try {
          await $`cd api && python -m ruff check ${input.args.filePath} 2>&1`
          log("info", "[Gardenify] Python lint check passed")
        } catch {
          log("warn", "[Gardenify] Python lint issues detected")
        }
      }
    },

    /**
     * Pre-Tool Security Hook
     * Warns about potential security issues before tool execution.
     */
    "tool.execute.before": async (input: ToolInput) => {
      // Warn on git push
      if (
        input.tool === "bash" &&
        input.args?.toString().includes("git push")
      ) {
        log(
          "info",
          "[Gardenify] Review changes before pushing: git diff origin/main...HEAD"
        )
      }

      // Warn on writing .env files
      if (
        input.tool === "write" &&
        input.args?.filePath &&
        typeof input.args.filePath === "string" &&
        input.args.filePath.includes(".env")
      ) {
        log(
          "warn",
          `[Gardenify] Writing ${input.args.filePath} - ensure no secrets are hardcoded`
        )
      }

      // Warn on writing documentation files
      if (
        input.tool === "write" &&
        input.args?.filePath &&
        typeof input.args.filePath === "string" &&
        input.args.filePath.match(/\.(md|txt)$/i) &&
        !input.args.filePath.includes("README") &&
        !input.args.filePath.includes("CHANGELOG")
      ) {
        log(
          "warn",
          `[Gardenify] Creating ${input.args.filePath} - consider if this documentation is necessary`
        )
      }
    },

    /**
     * Session Created Hook
     * Logs session start and checks for project context.
     */
    "session.created": async () => {
      log("info", "[Gardenify] Session started")

      if (hasProjectFile("CLAUDE.md")) {
        log("info", "[Gardenify] Found CLAUDE.md - loading project context")
      }
      if (hasProjectFile("AGENTS.md")) {
        log("info", "[Gardenify] Found AGENTS.md - loading agent instructions")
      }
    },

    /**
     * Session Idle Hook
     * Runs console.log audit on all edited files when task completes.
     */
    "session.idle": async () => {
      if (editedFiles.size === 0) return

      log("info", "[Gardenify] Session idle - running audit")

      let totalConsoleLogCount = 0
      const filesWithConsoleLogs: string[] = []

      for (const file of editedFiles) {
        if (!file.match(/\.(ts|tsx|js|jsx)$/)) continue

        try {
          const result = await $`grep -c "console\\.log" ${file} 2>/dev/null`.text()
          const count = parseInt(result.trim(), 10)
          if (count > 0) {
            totalConsoleLogCount += count
            filesWithConsoleLogs.push(file)
          }
        } catch {
          // No console.log found
        }
      }

      if (totalConsoleLogCount > 0) {
        log(
          "warn",
          `[Gardenify] Audit: ${totalConsoleLogCount} console.log in ${filesWithConsoleLogs.length} file(s)`
        )
        filesWithConsoleLogs.forEach((f) => log("warn", `  - ${f}`))
        log("warn", "[Gardenify] Remove console.log before committing")
      } else {
        log("info", "[Gardenify] Audit passed: No console.log found")
      }

      editedFiles.clear()
    },

    /**
     * Session Deleted Hook
     * Cleanup on session end.
     */
    "session.deleted": async () => {
      log("info", "[Gardenify] Session ended - cleaning up")
      editedFiles.clear()
    },

    /**
     * Shell Environment Hook
     * Injects project context into shell commands.
     */
    "shell.env": async () => {
      const env: Record<string, string> = {
        PROJECT_ROOT: worktreePath,
        GARDENIFY_PROJECT: "true",
      }

      // Detect package manager
      const lockfiles: Record<string, string> = {
        "bun.lockb": "bun",
        "pnpm-lock.yaml": "pnpm",
        "yarn.lock": "yarn",
        "package-lock.json": "npm",
      }
      for (const [lockfile, pm] of Object.entries(lockfiles)) {
        if (hasProjectFile(lockfile)) {
          env.PACKAGE_MANAGER = pm
          break
        }
      }

      // Detect languages
      const detected: string[] = []
      if (hasProjectFile("tsconfig.json")) detected.push("typescript")
      if (hasProjectFile("api/requirements.txt")) detected.push("python")
      if (detected.length > 0) {
        env.DETECTED_LANGUAGES = detected.join(",")
        env.PRIMARY_LANGUAGE = detected[0]
      }

      return env
    },

    /**
     * Session Compacting Hook
     * Preserves context across compaction.
     */
    "experimental.session.compacting": async () => {
      const contextBlock = [
        "# Gardenify Context (preserve across compaction)",
        "",
        "## Stack: Expo SDK 55 + FastAPI + Supabase + PlantNet",
        "- Mobile: TypeScript, expo-router, Android-first",
        "- Backend: Python FastAPI, Vercel serverless",
        "- Database: Supabase PostgreSQL with RLS",
        "- Plant AI: PlantNet API v2 (500/day)",
        "",
        "## Key Principles",
        "- TDD: write tests first, 80%+ coverage",
        "- Security: RLS on every table, no secrets in client",
        "- Simplicity: minimum code, no speculative abstractions",
        "",
      ]

      if (editedFiles.size > 0) {
        contextBlock.push("## Recently Edited Files")
        for (const f of editedFiles) {
          contextBlock.push(`- ${f}`)
        }
        contextBlock.push("")
      }

      return {
        context: contextBlock.join("\n"),
        compaction_prompt:
          "Focus on preserving: 1) Current task status, 2) Key decisions, 3) Files modified, 4) Remaining work, 5) Security concerns. Discard: verbose tool outputs, intermediate exploration.",
      }
    },
  }
}

export default GardenifyHooksPlugin
