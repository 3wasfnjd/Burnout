import runpy
import urllib.request

opener = urllib.request.build_opener()
opener.addheaders = [
    ('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/140 Safari/537.36'),
    ('Accept', 'application/json,text/plain,*/*'),
    ('Referer', 'https://polyhaven.com/'),
]
urllib.request.install_opener(opener)
runpy.run_path('.github/scripts/premium_room1_direct.py', run_name='__main__')
