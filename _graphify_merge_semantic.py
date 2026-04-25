import json, sys, time
sys.path.insert(0, r'C:\Users\chris\AppData\Roaming\Python\Python313\site-packages')
from pathlib import Path

start = time.time()

# Load cached + all chunk results
cached = json.loads(Path('.graphify_cached.json').read_text()) if Path('.graphify_cached.json').exists() else {'nodes':[],'edges':[],'hyperedges':[]}

chunk_files = [
    'graphify-out/.graphify_chunk_1.json',
    'graphify-out/.graphify_chunk_2.json',
    'graphify-out/.graphify_chunk_3.json',
    'graphify-out/.graphify_chunk_4.json',
    'graphify-out/.graphify_chunk_5.json',
]

all_nodes = list(cached['nodes'])
all_edges = list(cached['edges'])
all_hyperedges = list(cached.get('hyperedges', []))

for cf in chunk_files:
    p = Path(cf)
    if p.exists():
        try:
            data = json.loads(p.read_text())
            all_nodes.extend(data.get('nodes', []))
            all_edges.extend(data.get('edges', []))
            all_hyperedges.extend(data.get('hyperedges', []))
            print(f'Loaded {cf}: {len(data.get("nodes",[]))} nodes')
        except Exception as e:
            print(f'Error loading {cf}: {e}')

# Deduplicate by id
seen = set()
deduped = []
for n in all_nodes:
    if n['id'] not in seen:
        seen.add(n['id'])
        deduped.append(n)

merged = {
    'nodes': deduped,
    'edges': all_edges,
    'hyperedges': all_hyperedges,
    'input_tokens': 0,
    'output_tokens': 0,
}
Path('.graphify_semantic.json').write_text(json.dumps(merged, indent=2))

elapsed = time.time() - start
print(f'\nMerge complete in {elapsed:.1f}s')
print(f'Total nodes: {len(deduped)}')
print(f'Total edges: {len(all_edges)}')
print(f'Total hyperedges: {len(all_hyperedges)}')
