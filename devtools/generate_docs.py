from pathlib import Path
import markdown
import subprocess

def extract_title(md_text: str) -> str:
    for line in md_text.splitlines():
        if line.startswith('# '):
            return line[2:].strip()
    return "Page"

def get_releases_url(root: Path) -> str:
    try:
        remote_url = subprocess.check_output(
            ['git', '-C', str(root), 'config', '--get', 'remote.origin.url'],
            text=True
        ).strip()
        if remote_url.endswith('.git'):
            remote_url = remote_url[:-4]
        if remote_url.startswith('git@github.com:'):
            repo_path = remote_url.split(':', 1)[1]
        elif remote_url.startswith('https://github.com/'):
            repo_path = remote_url.split('github.com/', 1)[1]
        else:
            repo_path = ''
        if repo_path:
            return f'https://github.com/{repo_path}/releases'
    except Exception:
        pass
    return ''

import re

def fix_asset_paths(html: str) -> str:

    html = re.sub(r'(src|href)="docs/assets/', r'\1="assets/', html)
    return html

def main():
    root = Path(__file__).resolve().parent.parent
    readme_path = root / 'README.md'
    docs_path = root / 'docs'
    html_path = docs_path / 'index.html'
    css_path = 'assets/css/style.css'

    md_text = readme_path.read_text(encoding='utf-8')
    project_title = extract_title(md_text)
    body_html = markdown.markdown(md_text, extensions=['extra', 'toc', 'tables'])

    releases_url = get_releases_url(root)
    footer = f'&copy; {project_title}. MIT License.'
    if releases_url:
        footer += f'<br><a href="{releases_url}" target="_blank">Alle Releases auf GitHub</a>'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{project_title}</title>
  <link rel="stylesheet" href="{css_path}">
</head>
<body>
  <div class="container">
    <header>
      <h1>{project_title}</h1>
    </header>
    {body_html}
    <footer>
      {footer}
    </footer>
  </div>
</body>
</html>
"""

    html = fix_asset_paths(html)
    docs_path.mkdir(exist_ok=True)
    html_path.write_text(html, encoding='utf-8')

if __name__ == "__main__":
    main()