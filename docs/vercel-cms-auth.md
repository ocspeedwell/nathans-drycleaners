# Nathans CMS authentication on Vercel

This deployment uses Vercel Functions under `/api/cms/auth` and `/api/cms/callback`, instead of a separate Cloudflare Worker.

## Administrator access
The callback verifies the GitHub identity against the allowlist **ocspeedwell**. GitHub repository permissions remain necessary for publishing. Do not grant write access to other accounts unless the allowlist and permissions are deliberately reviewed.

## One-time activation
1. Create a **GitHub OAuth App** (GitHub Settings > Developer settings > OAuth Apps).
2. Set Homepage URL to `https://nathansdrycleaners.com` and Authorization callback URL to `https://nathansdrycleaners.com/api/cms/callback`.
3. In the **Vercel project**, add `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` as server-side environment variables. Do not prefix them with `NEXT_PUBLIC_` or `VITE_`. Do not commit them.
4. Redeploy the Vercel project after saving the variables.
5. Verify `/api/cms/auth` redirects to GitHub and test `/admin/` sign-in with `ocspeedwell`.
6. Test article editing and publication on the feature branch before changing the CMS backend branch to `main` for production.

The OAuth App requests the GitHub `repo` scope, which can grant broad access to private repositories owned by the signed-in account. For tighter permissions, use a dedicated editorial GitHub account/repository or a GitHub App with fine-grained permissions.

**Not yet deployed or tested.** The callback restricts successful login to `ocspeedwell`, but the public admin page itself is visible; its protected actions require authentication. Confirm that Vercel recognises these functions in the project's actual framework and build configuration before merging.
