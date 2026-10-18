#!/usr/bin/env python3
"""Download CampusFin AI Pexels photos to local files for reliable offline demo.

Requires internet on the computer running it, but no third-party Python modules.
Source links and license: docs/IMAGE_SOURCES.md. Do not imply endorsement by
any individuals pictured. Run: py scripts/download_photos.py
"""
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError

BASE=Path(__file__).resolve().parents[1]
DEST=BASE/'frontend'/'public'/'photos'
DEST.mkdir(parents=True,exist_ok=True)
IMAGES={
    'hero':(6684514,1500),
    'companion':(5940711,1100),
    'funding':(5940829,1500),
    'planning':(7972948,1500),
    'rescue':(8199167,1500),
    'transfers':(7102,1500),
    'family':(5965686,1100),
    'copilot':(16420237,1100),
    'campus':(6146987,1200),
}

def main():
    successes=0
    for slug,(photo_id,width) in IMAGES.items():
        target=DEST/(slug+'.jpg')
        if target.is_file() and target.stat().st_size>10000:
            print(f'SKIP {slug}: already downloaded')
            successes+=1
            continue
        url=f'https://images.pexels.com/photos/{photo_id}/pexels-photo-{photo_id}.jpeg?auto=compress&cs=tinysrgb&w={width}'
        try:
            req=Request(url,headers={'User-Agent':'Mozilla/5.0 (compatible; CampusFinDemoImageCache/1.0)'})
            with urlopen(req,timeout=30) as response:
                if not response.headers.get('content-type','').lower().startswith('image/'):
                    raise ValueError('Response was not an image')
                payload=response.read(12*1024*1024+1)
            if len(payload)<10000 or len(payload)>12*1024*1024 or not payload.startswith(b'\xff\xd8\xff'):
                raise ValueError('Unexpected image data; refusing to cache')
            target.write_bytes(payload)
            print(f'OK   {slug}: {len(payload)//1024} KiB -> {target.relative_to(BASE)}')
            successes+=1
        except (URLError,TimeoutError,ValueError,OSError) as exc:
            print(f'WARN {slug}: {type(exc).__name__}: {exc}')
    print(f'\nCached {successes}/{len(IMAGES)} photos.')
    if successes!=len(IMAGES):
        print('The app can still use remote Pexels images for missing files when online.')
        raise SystemExit(1)

if __name__=='__main__':main()
