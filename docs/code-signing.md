# Independent Windows Code Signing with Azure Trusted Signing

Windows Defender SmartScreen flags unsigned `.exe` downloads as *"Windows protected your PC / Unknown publisher"*. Using **Microsoft Azure Trusted Signing** (Azure Artifact Signing), you can sign `strawberry.exe` and `Strawberry_Setup.exe` independently with your own verified publisher identity—both **from GitHub Actions CI** and **locally on Windows** via `build-release.bat`.

---

## 1. Azure Portal One-Time Setup

1. Create a **Trusted Signing Account** (`Microsoft.CodeSigning/codeSigningAccounts`) in the [Azure Portal](https://portal.azure.com) (supported regions include East US `https://eus.codesigning.azure.net/`, West US 2 `https://wus2.codesigning.azure.net/`, West Europe `https://weu.codesigning.azure.net/`, North Europe `https://neu.codesigning.azure.net/`).
2. Complete **Identity Validation** (Individual or Organization) under your Trusted Signing Account.
3. Create a **Certificate Profile** of type **Public Trust** (used for Windows Authenticode & SmartScreen).
4. Grant RBAC role **`Trusted Signing Certificate Profile Signer`** on the Certificate Profile to:
   * Your own Azure user account (for local signing via `az login` + `build-release.bat`), **and**
   * A Microsoft Entra App Registration / Federated Identity for GitHub Actions OIDC (`Kittyboy06/Strawberry`).

---

## 2. Local Signing on Windows (`build-release.bat`)

1. Install prerequisites once:
   ```powershell
   winget install -e --id Microsoft.Azure.ArtifactSigningClientTools
   winget install -e --id Microsoft.AzureCLI
   az login
   ```
2. Add your non-secret Trusted Signing identifiers to your local `.env` (gitignored) or shell environment before running `build-release.bat`:
   ```dotenv
   AZURE_SIGNING_ENDPOINT=https://eus.codesigning.azure.net/
   AZURE_SIGNING_ACCOUNT=your-trusted-signing-account
   AZURE_SIGNING_PROFILE=your-certificate-profile
   ```
3. Run `build-release.bat`. It automatically signs `strawberry-cli\dist\strawberry.exe`, bundles it into `dist\Strawberry_Setup.exe`, and signs `dist\Strawberry_Setup.exe` using `signtool.exe` + `Azure.CodeSigning.Dlib.dll` and RFC 3161 timestamping (`http://timestamp.acs.microsoft.com`).

---

## 3. Automated Signing in GitHub Actions

Configure your repository in **GitHub → Settings → Secrets and variables → Actions**:

* **Secrets:**
  * `AZURE_CLIENT_ID` — Entra App (Client) ID with OIDC federated credential for `repo:Kittyboy06/Strawberry:ref:refs/tags/*`
  * `AZURE_TENANT_ID` — Azure Tenant ID
  * `AZURE_SUBSCRIPTION_ID` — Azure Subscription ID
* **Variables:**
  * `AZURE_SIGNING_ENDPOINT` — Regional URI (e.g., `https://eus.codesigning.azure.net/`)
  * `AZURE_SIGNING_ACCOUNT` — Trusted Signing Account name
  * `AZURE_SIGNING_PROFILE` — Public Trust Certificate Profile name
  * `STRAWBERRY_SUPABASE_URL` — Public Supabase URL (already configured)
  * `STRAWBERRY_SUPABASE_PUBLISHABLE_KEY` — Public `sb_publishable_...` key (already configured)

Push a version tag to build, sign, hash, and publish automatically:
```bash
git tag -a v0.2.0 -m "Strawberry v0.2.0"
git push origin v0.2.0
```
