from pathlib import Path
import urllib.request

opener = urllib.request.build_opener()
opener.addheaders = [
    ('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/140 Safari/537.36'),
    ('Accept', 'application/json,text/plain,*/*'),
    ('Referer', 'https://polyhaven.com/'),
]
urllib.request.install_opener(opener)

script_path = Path('.github/scripts/premium_room1_direct.py')
code = script_path.read_text()
old = "en = s.index('}else if(i===1)', st) + 1"
new = '''open_brace = s.index('{', st)\ndepth = 0\nen = None\nin_string = None\nescaped = False\nfor idx in range(open_brace, len(s)):\n    ch = s[idx]\n    if in_string:\n        if escaped:\n            escaped = False\n        elif ch == '\\\\':\n            escaped = True\n        elif ch == in_string:\n            in_string = None\n        continue\n    if ch in (\"'\", '\"', '`'):\n        in_string = ch\n        continue\n    if ch == '{':\n        depth += 1\n    elif ch == '}':\n        depth -= 1\n        if depth == 0:\n            en = idx + 1\n            break\nif en is None:\n    raise RuntimeError('room 1 dress block end not found')'''
if old not in code:
    raise RuntimeError('expected dress marker patch line missing')
code = code.replace(old, new, 1)
exec(compile(code, str(script_path), 'exec'), {'__name__': '__main__'})
