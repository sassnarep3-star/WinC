from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'public_site'
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir()
for name in ('index.html', 'sitemap.xml', 'feed.xml', 'robots.txt'):
    shutil.copy2(ROOT / name, OUT / name)
for directory in ('pages', 'assets'):
    shutil.copytree(ROOT / directory, OUT / directory)
print(f'Built static publication into {OUT.relative_to(ROOT)}')
