# Android Emulator Testing Guide

> Test Gardenify APK on Android emulator before production.

## Prerequisites

```bash
# Install Android SDK (macOS)
brew install --cask android-commandlinetools
sdkmanager "platform-tools" "platforms;android-34" "build-tools;34.0.0"

# Or use Android Studio (recommended)
# Download: https://developer.android.com/studio
```

## 1. Create Emulator

```bash
# List available system images
sdkmanager --list | grep "system-images"

# Install system image (Google APIs, ARM64)
sdkmanager "system-images;android-34;google_apis;arm64-v8a"

# Create AVD (Android Virtual Device)
avdmanager create avd -n gardenify_test -k "system-images;android-34;google_apis;arm64-v8a" -d "pixel_7"

# Start emulator
emulator -avd gardenify_test -no-window -no-audio -gpu swiftshader_indirect
```

## 2. Build APK

```bash
# Development build (faster)
npx expo run:android

# Preview build (EAS)
npx eas-cli build -p android --profile preview

# Production build (EAS)
npx eas-cli build -p android --profile production
```

## 3. Install APK on Emulator

```bash
# Wait for emulator to boot
adb wait-for-device

# Check emulator is ready
adb shell getprop sys.boot_completed
# Should return 1

# Install APK
adb install path/to/gardenify.apk

# Or if using EAS build, download from build URL
adb install ~/Downloads/gardenify.apk
```

## 4. Run App

```bash
# Launch app
adb shell am start -n com.gardenify/.MainActivity

# Take screenshot
adb shell screencap -p /sdcard/screenshot.png
adb pull /sdcard/screenshot.png ./screenshots/

# Record video
adb shell screenrecord /sdcard/recording.mp4
# Press Ctrl+C to stop
adb pull /sdcard/recording.mp4 ./recordings/
```

## 5. Automated Testing

### Using Maestro (Recommended)

```bash
# Install Maestro
curl -Ls "https://get.maestro.mobile.dev" | bash

# Create test flow
cat > .maestro/flow.yaml << EOF
appId: com.gardenify
---
- launchApp
- takeScreenshot
- tapOn: "Get Started"
- tapOn: "Email"
- inputText: "test@gardenify.app"
- tapOn: "Password"
- inputText: "password123"
- tapOn: "Sign In"
- takeScreenshot
EOF

# Run test
maestro test .maestro/flow.yaml
```

### Using Appium

```bash
# Install Appium
npm install -g appium

# Start Appium server
appium &

# Run tests
npx wdio run wdio.conf.ts
```

## 6. Visual Regression

```bash
# Capture baseline screenshots
adb shell screencap -p /sdcard/baseline.png
adb pull /sdcard/baseline.png ./screenshots/baseline/

# After changes, capture new screenshots
adb shell screencap -p /sdcard/current.png
adb pull /sdcard/current.png ./screenshots/current/

# Compare (using ImageMagick)
compare -metric AE baseline.png current.png diff.png
```

## 7. Performance Testing

```bash
# Monitor CPU usage
adb shell top -n 1 | grep gardenify

# Monitor memory
adb shell dumpsys meminfo com.gardenify

# Monitor battery
adb shell dumpsys batterystats

# FPS monitoring
adb shell dumpsys gfxinfo com.gardenify
```

## 8. Debug Logs

```bash
# View logcat
adb logcat | grep gardenify

# Filter by level
adb logcat *:E  # Errors only
adb logcat *:W  # Warnings and above

# Clear logcat
adb logcat -c
```

## 9. CI/CD Integration

### GitHub Actions Workflow

```yaml
name: Android E2E Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
      
      - name: Setup Android SDK
        uses: android-actions/setup-android@v3
      
      - name: Enable KVM
        run: |
          echo 'KERNEL=="kvm", GROUP="kvm", MODE="0666", OPTIONS+="static_node=kvm"' | sudo tee /etc/udev/rules.d/99-kvm4all.rules
          sudo udevadm control --reload-rules
          sudo udevadm trigger --name-match=kvm
      
      - name: Run AVD Actions
        uses: reactivecircus/android-emulator-runner@v2
        with:
          api-level: 34
          arch: x86_64
          script: |
            adb wait-for-device
            adb shell getprop sys.boot_completed
            
            # Build and install APK
            npx expo prebuild
            cd android && ./gradlew assembleDebug
            adb install app/build/outputs/apk/debug/app-debug.apk
            
            # Run Maestro tests
            curl -Ls "https://get.maestro.mobile.dev" | bash
            export PATH="$PATH:$HOME/.maestro/bin"
            maestro test .maestro/
```

## 10. Quick Commands

```bash
# Start emulator
emulator -avd gardenify_test

# Install and launch
adb install app.apk
adb shell am start -n com.gardenify/.MainActivity

# Capture screenshots
adb shell screencap -p /sdcard/screen.png && adb pull /sdcard/screen.png

# View logs
adb logcat -s Gardenify

# Stop emulator
adb emu kill
```
