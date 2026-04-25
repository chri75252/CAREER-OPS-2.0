import json, sys, time
sys.path.insert(0, r'C:\Users\chris\AppData\Roaming\Python\Python313\site-packages')
from graphify.cache import check_semantic_cache
from pathlib import Path

detect = json.loads(Path('.graphify_detect.json').read_text())
all_files = [f for files in detect['files'].values() for f in files]

start = time.time()
cached_nodes, cached_edges, cached_hyperedges, uncached = check_semantic_cache(all_files)
elapsed = time.time() - start

if cached_nodes or cached_edges or cached_hyperedges:
    Path('.graphify_cached.json').write_text(json.dumps({'nodes': cached_nodes, 'edges': cached_edges, 'hyperedges': cached_hyperedges}))
Path('.graphify_uncached.txt').write_text('\n'.join(uncached))

with open('graphify_cache.txt','w') as f:
    f.write(f'Cache check done in {elapsed:.1f}s\n')
    f.write(f'Cached: {len(cached_nodes)} nodes, {len(cached_edges)} edges, {len(cached_hyperedges)} hyperedges\n')
    f.write(f'Uncached: {len(uncached)} files\n')
    f.write(f'Total files checked: {len(all_files)}\n')

print(f'Cache: {len(all_files)-len(uncached)} hit, {len(uncached)} need extraction')
