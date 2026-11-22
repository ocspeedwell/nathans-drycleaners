# Secure Nathans Journal administrator sign-in

The repository includes a **Cloudflare Worker OAuth bridge template** at `cloudflare/nathans-cms-oauth-worker.js`. It is **not deployed**. Do not enable the CMS until the bridge is deployed and tested.

## Setup checklist

1. Create a GitHub OAuth App in the GitHub account that owns the Nathans repository. Set Homepage URL to the final website origin and Authorization callback URL to `https://<your-worker-domain>/callback`.
2. Deploy the worker code to a dedicated Cloudflare Worker. Configure `CMS_ORIGIN` as the exact HTTPS website origin. Set `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` as **Worker secrets**, not repository files or frontend variables.
3. In `admin/config.yml`, set `base_url: https://<your-worker-domain>` and `auth_endpoint: auth` under `backend`.
4. Ensure only trusted Nathans editors have write permission to the GitHub repository. The OAuth app requests GitHub's broad `repo` scope. Consider a dedicated GitHub organisation/repository with least-privilege access if this scope is unacceptable.
5. Test login, a new article draft, image upload, build workflow and website deployment on the development branch before merging. Switch the CMS branch to `main` only after approval.

## Security limitations

The bridge uses a 10-minute random state cookie, HTTPS-only cookie flags and a fixed postMessage origin. It does not provide its own user account database. GitHub repository permissions are the publishing authorisation boundary. This is a deployment template, **not a claim that authentication has been configured or audited**.

Do not paste OAuth client secrets into ChatGPT, GitHub issues, or frontend code. Enter secrets only into the hosting provider's secret-management interface.
