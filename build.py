"""Generate a static Stremio addon (manifest + catalogs + meta + streams) for free US live TV
from the public iptv-org index (https://github.com/iptv-org/iptv). Run: python build.py [outdir]   (default: docs)"""
import json, sys, os, re, urllib.request
out = sys.argv[1] if len(sys.argv) > 1 else 'docs'
API = 'https://iptv-org.github.io/api/'
def L(n):
    with urllib.request.urlopen(API + n, timeout=60) as r: return json.load(r)
streams, channels, logos, categories = L('streams.json'), L('channels.json'), L('logos.json'), L('categories.json')
cat_name = {c['id']: c['name'] for c in categories}
us = {c['id']: c for c in channels if c.get('country') == 'US' and not c.get('closed') and not c.get('is_nsfw')}
logo = {}
for l in logos:
    if l['channel'] in us and l['channel'] not in logo: logo[l['channel']] = l['url']
by_chan = {}
for s in streams:
    cid = s.get('channel')
    if cid in us: by_chan.setdefault(cid, []).append(s)
def slug(x): return re.sub(r'[^a-z0-9]+', '-', x.lower()).strip('-')
metas, streamfiles = [], {}
for cid, ss in by_chan.items():
    c = us[cid]; cats = c.get('categories') or ['general']
    mid = 'usltv-' + slug(cid)
    metas.append({'id': mid, 'type': 'tv', 'name': c['name'], 'poster': logo.get(cid), 'logo': logo.get(cid),
                  'background': logo.get(cid), 'posterShape': 'square', 'genres': [cat_name.get(k, k) for k in cats],
                  'description': f"{c['name']} — free live stream via the public iptv-org index. Category: {', '.join(cat_name.get(k,k) for k in cats)}.",
                  '_cats': cats})
    streamfiles[mid] = [{'url': s['url'], 'name': 'US Live TV', 'title': f"{c['name']} ({s.get('quality') or 'auto'})",
                         'behaviorHints': {'notWebReady': True, **({'proxyHeaders': {'request': {k: v for k, v in [('Referer', s.get('referrer')), ('User-Agent', s.get('user_agent'))] if v}}} if (s.get('referrer') or s.get('user_agent')) else {})}}
                        for s in ss]
metas.sort(key=lambda m: m['name'].lower())
top = ['news', 'sports', 'entertainment', 'movies', 'series', 'kids', 'music', 'documentary', 'general']
cat_defs = [{'type': 'tv', 'id': 'usltv_all', 'name': 'US Live TV (all)', 'extra': [{'name': 'skip'}]}]
for k in top:
    if any(k in m['_cats'] for m in metas): cat_defs.append({'type': 'tv', 'id': f'usltv_{k}', 'name': f'US Live TV: {cat_name.get(k,k)}', 'extra': [{'name': 'skip'}]})
manifest = {'id': 'community.us-live-tv.iptvorg', 'version': '1.0.1', 'name': 'US Live TV (iptv-org)',
            'description': f'{len(metas)} free US live TV channels from the public iptv-org index, grouped by category. Built by Claude for personal use.',
            'logo': 'https://iptv-org.github.io/assets/logo.png', 'resources': ['catalog', 'meta', 'stream'], 'types': ['tv'], 'idPrefixes': ['usltv-'],
            'catalogs': cat_defs, 'behaviorHints': {'configurable': False}}
def w(p, o):
    os.makedirs(os.path.dirname(p), exist_ok=True); json.dump(o, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
w(f'{out}/manifest.json', manifest)
clean = lambda m: {k: v for k, v in m.items() if k != '_cats'}
PAGE = 100
def write_catalog(cid, items):
    for i in range(0, max(len(items), 1), PAGE):
        page = [clean(m) for m in items[i:i+PAGE]]
        w(f'{out}/catalog/tv/{cid}.json' if i == 0 else f'{out}/catalog/tv/{cid}/skip={i}.json', {'metas': page})
write_catalog('usltv_all', metas)
for k in top: write_catalog(f'usltv_{k}', [m for m in metas if k in m['_cats']])
for m in metas:
    w(f'{out}/meta/tv/{m["id"]}.json', {'meta': clean(m)})
    w(f'{out}/stream/tv/{m["id"]}.json', {'streams': streamfiles[m['id']]})
print(f'channels: {len(metas)}, streams: {sum(len(v) for v in streamfiles.values())}, catalogs: {len(cat_defs)}')
