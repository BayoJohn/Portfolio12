"""Copy only public files into Vercel's static output directory."""
from pathlib import Path
from shutil import copy2, copytree

root = Path(__file__).resolve().parents[1]
output = root / "public"
output.mkdir(exist_ok=True)
for folder in ("assets", "about", "academy", "ai", "blog", "contact", "cybersecurity", "projects", "reviews",
               "search", "shop", "software", "writing", "Doc", "editorial-standards", "corrections", "privacy", "disclosures"):
    if (root / folder).is_dir():
        copytree(root / folder, output / folder, dirs_exist_ok=True)
for path in [*root.glob("*.html"), root / "robots.txt", root / "sitemap.xml"]:
    copy2(path, output / path.name)
