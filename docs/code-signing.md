# Code Signing Setup with SignPath Foundation

Windows Defender SmartScreen flags unsigned `.exe` installers downloaded from the internet as *"Windows protected your PC / Unknown publisher"*. Because [SignPath Foundation](https://about.signpath.io/product/open-source/) sponsors free CA-trusted Authenticode code signing for eligible public open-source GitHub repositories, Strawberry integrates directly with SignPath via GitHub Actions in [.github/workflows/release.yml](../.github/workflows/release.yml).

---

## 1. Prerequisites Already Configured in Repository
* **MIT License:** [LICENSE](../LICENSE)
* **Public Repository:** `https://github.com/Kittyboy06/Strawberry`
* **Attribution, Team Roles & Privacy Policy:** Included in [README.md](../README.md#code-signing--privacy-policy) as required for SignPath Foundation review.
* **Verifiable GitHub-Hosted CI Build:** Builds strictly from source on `windows-latest` inside GitHub Actions.
* **PE Metadata & Icon:** [installer/strawberry.ico](../installer/strawberry.ico) and [installer/version_info.txt](../installer/version_info.txt).

---

## 2. Onboarding Checklist (One-Time Setup)

1. **Apply to SignPath Foundation:**
   * Submit an open-source project request at **https://about.signpath.io/product/open-source/** referencing `https://github.com/Kittyboy06/Strawberry`.
2. **Install the SignPath GitHub App:**
   * After approval, install the **SignPath GitHub App** on `Kittyboy06/Strawberry` so SignPath can verify build provenance.
3. **Configure SignPath Dashboard:**
   * Create a Project (recommended slug: `strawberry`).
   * Create an Artifact Configuration matching `strawberry-unsigned` containing `Strawberry_Setup.exe` and `strawberry.exe`.
   * Create a Release Signing Policy (`release-signing`) using the SignPath Foundation certificate.
4. **Configure GitHub Repository Secrets & Variables** (`Settings -> Secrets and variables -> Actions`):
   * **Secrets:**
     * `SIGNPATH_API_TOKEN` — API token from your SignPath submitter account.
   * **Variables:**
     * `SIGNPATH_ORGANIZATION_ID` — Your SignPath Organization UUID.
     * `STRAWBERRY_SUPABASE_URL` — Public Supabase project URL.
     * `STRAWBERRY_SUPABASE_PUBLISHABLE_KEY` — Public `sb_publishable_...` key (**never** add `SECRET_KEY`).
     * Optional overrides if your SignPath slugs differ from defaults: `SIGNPATH_PROJECT_SLUG`, `SIGNPATH_SIGNING_POLICY_SLUG`, `SIGNPATH_ARTIFACT_CONFIG_SLUG`.
5. **Trigger Signed Release `v0.2.0`:**
   ```bash
   git tag -a v0.2.0 -m "Strawberry v0.2.0"
   git push origin v0.2.0
   ```
   GitHub Actions builds on `windows-latest`, submits the artifact to SignPath Foundation, verifies signatures, computes `SHA256SUMS.txt`, and publishes the signed release to GitHub Releases.
