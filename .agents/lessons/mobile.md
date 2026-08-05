# Lessons — Mobile (Expo Router, React Native, APK)

## 2026-08-06: expo-router Initial-Route Redirect Only Fires Once — Guard the Root Layout for Auth Navigation

**Context:** After shipping auth, two symptoms looked like separate bugs: (1) Sign Out left the app on Profile showing "Unknown" instead of returning to Login, and (2) after tapping Log In the app stayed on the login form until force-stop/relaunch.

**Root cause:** `src/app/index.tsx` used `<Redirect href={user ? "/(tabs)" : "/(auth)/login"} />` — but the `/` index route only renders on **initial** navigation. Once the user moved to `(auth)/login` or `(tabs)`, no code watched the auth state, so `signOut()`/`signIn()` updating `user` in context never triggered navigation. The session was actually cleared/persisted correctly (verified: force-stop + relaunch behaved correctly); it was purely a navigation gap.

**Fix:** Add an auth guard in the root `RootNavigator` (`src/app/_layout.tsx`) using `useSegments()` + `useRouter()`:

```tsx
const segments = useSegments();
const router = useRouter();
useEffect(() => {
  if (loading) return;
  const inAuthGroup = segments[0] === "(auth)";
  const onResetScreen = segments.join("/").includes("reset-password");
  if (!user && !inAuthGroup) {
    router.replace("/(auth)/login");
  } else if (user && inAuthGroup && !onResetScreen) {
    router.replace("/(tabs)");
  }
}, [user, loading, segments, router]);
```

**Rules going forward:**

- **An initial-route `<Redirect>` is not an auth guard.** It only runs at app launch. Any screen reachable after navigation must be protected by a route-watching guard (root layout is the single place to do this).
- **The guard fixes both directions** (sign-out → login, sign-in → tabs) because both are the same missing reactive check.
- **Carve out deep links:** reset-password lives in `(auth)` but must not be bounced to `(tabs)` when a stale session exists.
- **`useSegments()` narrowing can trip on stale typed-routes:** `.expo/types/router.d.ts` didn't include `reset-password`, so `segments[1] === "reset-password"` was a TS narrowing error. Use `segments.join("/").includes("reset-password")` instead.
- **EAS build can hang at "Computing project fingerprint"** (before the build is created). Submit with `EAS_SKIP_AUTO_FINGERPRINT=1`. If you kill the CLI mid-fingerprint, a duplicate build may still appear — cancel it (`eas build:cancel <id>`).

**Verification:** prod-baked build `e4cd16d5` on emulator: Sign Out → Login (and stays after force-stop); login → Home in-app (no restart); force-stop + relaunch → Home.

## 2026-07-31: Leftover Expo Template Placeholder Overrode the Entire App

**Context:** Production APK launched to a blank screen reading "Edit src/app/index.tsx to edit this screen." instead of the Gardenify app.

**Issue:** `src/app/index.tsx` was the default `create-expo-app` template placeholder. In expo-router, `/` resolves to `index.tsx`, so it rendered instead of the real app.

**Fix:** Replace `src/app/index.tsx` with an auth-aware redirect (`Redirect` to `/(auth)/login` or `/(tabs)` via `useAuth()`).

**Pattern:** Always audit `app/` routes (especially root `index.tsx`) before shipping — the Expo template leaves a placeholder that overrides routing. Verify by installing the built APK, not just via `npx expo start`.

## 2026-07-31: Verify Installed APK Actually Replaced the Old One (adb)

**Issue:** After `adb install -r` reported Success, relaunching still showed the old template screen. Root cause: stale adb server after `taskkill /f /im adb.exe`.

**Fix:** Verify the installed APK matches your build by comparing MD5:

```
adb shell pm path com.gardenify.app        # get base.apk path
adb pull <path> device_base.apk
certutil -hashfile device_base.apk MD5
certutil -hashfile my-build.apk MD5         # must match
```

If they differ: `adb uninstall com.gardenify.app` then `adb install -r`, re-verify.

**Pattern:** Never trust `adb install` Success alone — compare hashes of installed vs intended APK.

## 2026-07-31: Verify Built APK Contains the Correct Env Config

**Issue:** Suspected the production APK had wrong/missing Supabase or API config.

**Fix:** Extract `assets/index.android.bundle` from the APK and grep for expected strings:

```
7z x -y -o<out> app.apk "assets/*"
python -c "data=open('.../index.android.bundle','rb').read(); print(data.find(b'supabase.co'))"
```

Confirm expected Supabase URL present, `localhost:54321` fallback ABSENT, API URL present.

**Pattern:** Before debugging a "broken on device" report, rule out build config by inspecting the compiled bundle. Hermes bytecode keeps string literals searchable.

## 2026-07-31: Android Emulator Input via `adb shell input` Is Unreliable After Reboot

**Issue:** `adb shell input tap` + `input text` failed to populate fields — field coordinates shift when the soft keyboard opens, and focus doesn't always land where tapped.

**Fix:** Use `adb shell uiautomator dump` to read actual element bounds, then tap those exact centers. Re-dump after each interaction (layout shifts with the keyboard). Prefer `uiautomator dump` text assertions over pixel coordinates.

**Pattern:** UI assertions via `uiautomator dump` are the most reliable non-visual signal on the emulator.

## 2026-07-29: Gallery Crop Removed via `allowsEditing: false`

**Issue:** `expo-image-picker` shows a crop/edit UI when `allowsEditing: true`. Requires user to crop before the image is returned.

**Fix:** Set `allowsEditing: false` (default) so the gallery returns immediately with the selected image. The Scan screen's image preview + Identify button serves as the confirmation step.

## 2026-07-28: JSX Requires .tsx Extension

**Issue:** TypeScript compilation failed with syntax errors on JSX content in `.ts` files.

**Fix:** Always use `.tsx` extension for any file containing JSX, including hook files that return JSX (like context providers). `use-auth.ts` → `use-auth.tsx`.

## 2026-07-28: Typed Routes + Dynamic Segments

**Issue:** `experiments.typedRoutes` generates strict route types that don't include parameterized dynamic segments, causing TypeScript errors on `router.push()`.

**Fix:** Cast dynamic route strings with `as any`: `router.push(`/identification/${id}` as any)`.

**Tradeoff:** Loses type safety on route params — verify manually.

## 2026-07-28: expo-image-picker SDK 55 API Changes

**Issue:** `maxWidth`/`maxHeight` options don't exist in `ImagePickerOptions`, `mimeType` is nullable.

**Fix:** Use `ImagePickerOptions["quality"]` for type-safe quality option, accept full asset object instead of custom interface.

**Pattern:** Don't invent custom interfaces — use `ImagePickerAsset` directly from the library.

## CSS Module Imports Need TypeScript Declarations (web)

**Issue:** `.web.tsx` file imports a CSS module; TS error "Cannot find module './*.module.css'".

**Fix:** Create `src/types/css-module.d.ts` with `declare module '*.module.css'` and add to `tsconfig.json` includes.
