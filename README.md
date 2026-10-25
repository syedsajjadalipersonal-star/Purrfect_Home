# Purrfect Home – app project

Files: `index.html` (the whole game), `vendor/three.min.js` (3D engine, bundled so the game never depends on a CDN),
`sw.js` + `manifest.webmanifest` (installable + works offline), `icons/`.

## Run locally
    python3 -m http.server 8080      # then open http://localhost:8080 (service worker needs http/https, not file://)

## Get it on Android (free)
1. Put this folder in a GitHub repo.  2. Actions tab -> "Android build" -> Run workflow.  3. Download the APK artifact and install it.
(Untested in this workspace: it has no Android SDK. First run may need small fixes.)
For Google Play you also need a signed release bundle (.aab) and a $25 developer account.

## Before launch
Change `appId` in `capacitor.config.json` (reverse-domain you own), check the "Purrfect Home" name for trademark conflicts, add a privacy policy.
