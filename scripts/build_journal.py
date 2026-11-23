#!/usr/bin/env python3
"""Build Nathans journal pages from editorial Markdown using a safe, repeatable build."""
from pathlib import Path
from html import escape
import json
import re
import sys
import yaml
import markdown
import bleach

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content" / "journal"
OUTPUT = ROOT / "journal"
SITE = "https://nathansdrycleaners.com"
CATEGORIES = {"Fabric Care & Stain Removal", "Professional Dry Cleaning", "Laundry & Lifestyle", "Nathans Locations & Services"}
ALLOWED_TAGS = set(bleach.sanitizer.ALLOWED_TAGS) | {"p", "h2", "h3", "h4", "br", "hr", "img", "blockquote"}
ALLOWED_ATTRS = {"a": ["href", "title"], "img": ["src", "alt", "title"]}
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
IMAGE = re.compile(r"^/assets/journal/[a-zA-Z0-9_./-]+\.(?:png|jpe?g|webp|svg)$")

def parse(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path}: expected YAML front matter")
    _, header, body = text.split("---", 2)
    meta = yaml.safe_load(header)
    if not isinstance(meta, dict):
        raise ValueError(f"{path}: invalid front matter")
    slug = path.stem
    if not SLUG.fullmatch(slug):
        raise ValueError(f"{path}: invalid slug")
    for field in ("title", "description", "category"):
        if not isinstance(meta.get(field), str) or not meta[field].strip():
            raise ValueError(f"{path}: missing {field}")
    if meta["category"] not in CATEGORIES:
        raise ValueError(f"{path}: unsupported category")
    if len(meta["title"]) > 140 or len(meta["description"]) > 320:
        raise ValueError(f"{path}: metadata too long")
    if not body.strip():
        raise ValueError(f"{path}: article body is empty")
    image = meta.get("image") or "/assets/nathans-hero.webp"
    if image != "/assets/nathans-hero.webp" and not IMAGE.fullmatch(image):
        raise ValueError(f"{path}: image must be inside /assets/journal/")
    html = markdown.markdown(body, extensions=["extra", "sane_lists"], output_format="html")
    clean = bleach.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, protocols=["https", "http"], strip=True)
    return dict(slug=slug, title=meta["title"], description=meta["description"], category=meta["category"], image=image, html=clean)

def render(a):
    e = escape
    url = f'{SITE}/journal/{a["slug"]}/'
    schema = json.dumps({"@context": "https://schema.org", "@type": "Article", "headline": a["title"], "description": a["description"], "mainEntityOfPage": url, "author": {"@type": "Organization", "name": "Nathans Dry Cleaners"}, "publisher": {"@type": "Organization", "name": "Nathans Dry Cleaners"}}, ensure_ascii=False).replace("<", "\\u003c")
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(a["title"])} | The Nathans Journal</title><meta name="description" content="{e(a["description"], quote=True)}"><link rel="canonical" href="{url}"><meta property="og:type" content="article"><meta property="og:title" content="{e(a["title"], quote=True)}"><meta property="og:description" content="{e(a["description"], quote=True)}"><meta property="og:image" content="{SITE}{e(a["image"], quote=True)}"><script type="application/ld+json">{schema}</script><style>body{{margin:0;background:#faf9f6;color:#192a42;font:17px/1.75 Arial,sans-serif}}header,footer{{background:#071b3a;color:#fff;padding:22px 6%}}main{{max-width:800px;margin:auto;padding:50px 24px}}h1{{font:clamp(34px,5vw,55px)/1.15 Georgia,serif}}h2{{font:28px Georgia,serif}}a{{color:inherit}}.tag{{color:#9b7730;font-weight:bold;text-transform:uppercase;font-size:12px}}.cta{{background:#071b3a;color:white;padding:25px;border-radius:9px;margin:30px 0}}.cta a{{color:#f4d392}}</style></head><body><header><a href="/">NATHANS DRY CLEANERS</a> · <a href="/journal/">The Nathans Journal</a></header><main><p class="tag">{e(a["category"])}</p><h1>{e(a["title"])}</h1><figure style="margin:25px 0 35px"><img src="{e(a["image"], quote=True)}" alt="Editorial illustration for {e(a["title"], quote=True)}" style="display:block;width:100%;height:auto;max-height:470px;object-fit:cover;border-radius:12px" loading="eager"></figure><article>{a["html"]}</article><aside class="cta">For professional garment care and current quotations, <a href="/#locations">contact your preferred Nathans branch</a>.</aside><p><a href="/journal/">← All journal articles</a></p></main><footer>© Nathans Dry Cleaners · Since 1997</footer></body></html>'''

def main():
    articles = [parse(p) for p in sorted(CONTENT.glob("*.md")) if p.name.lower() != "readme.md"]
    if not articles:
        print("No editorial articles to build")
        return
    for a in articles:
        dest = OUTPUT / a["slug"] / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(render(a), encoding="utf-8")
        print("Built", dest.relative_to(ROOT))
    catalogue = [{"title": a["title"], "category": a["category"], "slug": a["slug"], "description": a["description"], "image": a["image"]} for a in articles]
    (OUTPUT / "articles.json").write_text(json.dumps(catalogue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    sitemap = ROOT / "sitemap.xml"
    if sitemap.exists():
        existing = sitemap.read_text(encoding="utf-8")
        new_urls = [f"{SITE}/journal/{a['slug']}/" for a in articles]
        for url in new_urls:
            if f"<loc>{url}</loc>" not in existing:
                existing = existing.replace("</urlset>", f"  <url><loc>{url}</loc></url>\n</urlset>")
        sitemap.write_text(existing, encoding="utf-8")

if __name__ == "__main__":
    try:
        main()
    except (ValueError, yaml.YAMLError) as exc:
        print(f"Journal build failed: {exc}", file=sys.stderr)
        sys.exit(1)
