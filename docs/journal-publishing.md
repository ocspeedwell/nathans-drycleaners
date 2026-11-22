# Nathans Journal editorial publishing

The journal uses **Decap CMS** at `/admin/`, with GitHub as its content repository. New articles are stored as Markdown files in `content/journal/`. The GitHub Actions workflow validates and converts these files into static HTML pages at `/journal/<slug>/`, and adds URLs to the sitemap.

## Before enabling the dashboard

1. Configure a trusted, hosted GitHub OAuth service for Decap CMS. Put its actual `base_url` and `auth_endpoint` in `admin/config.yml`. **Do not store OAuth client secrets or access tokens in the repository.**
2. Limit GitHub repository write access to authorised Nathans editors. Use branch protection and reviews if publishing needs approval.
3. Verify GitHub Actions has permission to write repository contents. Test the workflow on the feature branch.
4. When the feature branch is merged, ensure `admin/config.yml` points to `main`.
5. Review article content and image rights before publishing. Confirm all branch contact details with Nathans.

## Publishing

Once OAuth is configured, an authorised editor can open `/admin/`, sign in through GitHub, create an article, enter a title, SEO description, category and body, then save it. A commit under `content/journal/` triggers the workflow. The workflow generates the article HTML and updates the sitemap. Hosting must deploy the resulting commit for the page to become public.

**Existing ten editorial pages** were written directly as static HTML. They are not yet represented as CMS Markdown records. Editing them through the dashboard requires importing them as Markdown, which will replace their generated HTML on the next build. The journal index currently uses a hard-coded article catalogue, so new CMS posts will have their own URL but will not appear in journal search until the index is wired to the generated catalogue.

## Security

Do not enable anonymous writes, put GitHub tokens in client-side JavaScript, or expose OAuth secrets. The generator sanitizes Markdown HTML and validates basic metadata and image paths, but editorial review is still necessary.
