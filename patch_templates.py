from pathlib import Path
import re

base = Path('HTML')
for path in base.glob('*.html'):
    text = path.read_text(encoding='utf-8')
    # Replace all CSS references to the unified theme
    text = text.replace('style1.css', 'neon.css')
    text = text.replace('style3.css', 'neon.css')
    text = text.replace('style4.css', 'neon.css')
    text = text.replace('style.css', 'neon.css')

    # Replace old google fonts import with Inter
    text = text.replace(
        '<link rel="stylesheet" type="text/css" href="https://fonts.googleapis.com/css?family=Open+Sans|Raleway|Candal">',
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">'
    )

    # Remove CDN JS includes from head
    text = re.sub(r'<script src="//maxcdn\.bootstrapcdn\.com/bootstrap/4\.1\.1/js/bootstrap\.min\.js"></script>\s*<script src="//cdnjs\.cloudflare\.com/ajax/libs/jquery/3\.2\.1/jquery\.min\.js"></script>', '', text)
    text = re.sub(r'<script src="//cdnjs\.cloudflare\.com/ajax/libs/jquery/3\.2\.1/jquery\.min\.js"></script>\s*<script src="//maxcdn\.bootstrapcdn\.com/bootstrap/4\.1\.1/js/bootstrap\.min\.js"></script>', '', text)

    # Normalize script order at bottom and add custom.js if missing
    if '{{ url_for(\'static\',filename=\'js/bootstrap.min.js\') }}' in text and '{{ url_for(\'static\',filename=\'js/jquery.min.js\') }}' in text:
        text = re.sub(
            r'<script src="\{\{\s*url_for\(\'static\',filename=\'js/jquery\.min\.js\'\)\s*\}\}"></script>\s*<script src="\{\{\s*url_for\(\'static\',filename=\'js/bootstrap\.min\.js\'\)\s*\}\}"></script>',
            '<script src="{{ url_for(\'static\', filename=\'js/jquery.min.js') }}"></script>\n  <script src="{{ url_for(\'static\', filename=\'js/bootstrap.min.js') }}"></script>\n  <script src="{{ url_for(\'static\', filename=\'js/jquery.easing.min.js') }}"></script>\n  <script src="{{ url_for(\'static\', filename=\'js/custom.js') }}"></script>',
            text
        )
    if '{{ url_for(\'static\', filename=\'js/custom.js') }}' not in text and '</body>' in text:
        text = text.replace('</body>', '  <script src="{{ url_for(\'static\', filename=\'js/custom.js') }}"></script>\n</body>')

    path.write_text(text, encoding='utf-8')
    print(f'Patched {path.name}')
