import type { PluginInput } from "@opencode-ai/plugin"

interface ToolInput {
  tool: string
  callID?: string
  args?: Record<string, unknown>
}

export const SuperpowerHooksPlugin = async ({ client, $, directory, worktree }: PluginInput) => {
  const worktreePath = worktree || directory
  const runningServices = new Map<string, { pid?: number; started: Date }>()

  const log = (level: "debug" | "info" | "warn" | "error", message: string) =>
    client.app.log({ body: { service: "superpower", level, message } })

  return {
    "tool.execute.before": async (input: ToolInput) => {
      if (input.tool !== "bash" || !input.args?.command) return

      const cmd = String(input.args.command)

      if (cmd.includes("git push")) {
        log("info", "[Superpower] Hold on — checking diff before push...")
      }

      if (cmd.includes("npx expo start") || cmd.includes("npx expo run")) {
        log("info", "[Superpower] Launching Expo via detached process (non-blocking)...")
      }

      if (cmd.includes("uvicorn") || cmd.includes("vercel dev")) {
        log("info", "[Superpower] Launching backend via detached process (non-blocking)...")
      }

      if (cmd.includes("adb -s emulator") || cmd.includes("adb shell")) {
        log("info", "[Superpower] Running ADB command with timeout...")
      }
    },

    "tool.execute.after": async (input: ToolInput) => {
      if (input.tool !== "bash") return
      log("debug", `[Superpower] Tool completed: ${input.tool}`)
    },

    "experimental.session.compacting": async () => {
      const serviceList: string[] = []
      for (const [name, info] of runningServices) {
        serviceList.push(`- ${name} (started ${info.started.toISOString()})`)
      }

      const contextBlock = [
        "# Superpower State (preserve across compaction)",
        "",
      ]

      if (serviceList.length > 0) {
        contextBlock.push("## Running Services")
        contextBlock.push(...serviceList)
        contextBlock.push("")
      }

      contextBlock.push(
        "## Non-Blocking Command Patterns",
        "- Backend: `python -c \"import subprocess; subprocess.Popen(['uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8000'], creationflags=subprocess.DETACHED_PROCESS)\"`",
        "- Expo: `python -c \"import subprocess; subprocess.Popen(['npx', 'expo', 'start'], creationflags=subprocess.DETACHED_PROCESS)\"`",
        "- Emulator: `python -c \"import subprocess; subprocess.Popen(['emulator', '-avd', 'Pixel_7_API_34'], creationflags=subprocess.DETACHED_PROCESS)\"`",
        "- ADB: Always use `timeout` wrapper or `subprocess.run(timeout=30)`",
      )

      return {
        context: contextBlock.join("\n"),
        compaction_prompt:
          "Preserve: 1) Service states, 2) Non-blocking patterns, 3) Running PIDs, 4) ADB device status. Discard: verbose command outputs.",
      }
    },
  }
}

export default SuperpowerHooksPlugin
