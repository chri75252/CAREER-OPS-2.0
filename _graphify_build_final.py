import json, sys, time
sys.path.insert(0, r'C:\Users\chris\AppData\Roaming\Python\Python313\site-packages')
from graphify.build import build_from_json
from graphify.cluster import cluster, score_all
from graphify.analyze import god_nodes, surprising_connections, suggest_questions
from graphify.report import generate
from graphify.export import to_json, to_html
from pathlib import Path

start = time.time()

extraction = json.loads(Path('.graphify_extract.json').read_text())
detection = json.loads(Path('.graphify_detect.json').read_text())

G = build_from_json(extraction)
communities = cluster(G)
cohesion = score_all(G, communities)
tokens = {'input': extraction.get('input_tokens', 0), 'output': extraction.get('output_tokens', 0)}
gods = god_nodes(G)
surprises = surprising_connections(G, communities)

community_labels = {
    0: "Pipeline UI Models",
    1: "Discovery Data Models",
    2: "Career-Ops Modes & Data",
    3: "Internationalization (DE/FR/JA/PT/RU)",
    4: "Dashboard Tests",
    5: "Project Documentation",
    6: "Career Data Processing",
    7: "Table Viewer Models",
    8: "Job Feed Fetcher",
    9: "Workflow Status Screen",
    10: "Progress Models",
    11: "Career-Ops System (Branding)",
    12: "Dashboard App Models",
    13: "Help Screen Models",
    14: "Evaluation Framework",
    15: "Workflow Status UI Models",
    16: "Pipeline Orchestrator",
    17: "Workflow Section Models",
    18: "JobSpy Scraper",
    19: "Merger & Dedupe",
    20: "Workflow Reports",
    21: "Temp: Pipeline Utils",
    22: "Theme: Catppuccin Mocha",
    23: "Theme: Catppuccin Latte",
    24: "Ingest to Career-Ops",
    25: "Dashboard Truth Reports",
    26: "PolyAI Agent Design Evals",
    27: "PolyAI Account Mgmt Evals",
    28: "Setup & Customization Guides",
    29: "Greenhouse ATS & Test",
    30: "Pipeline Analysis",
    31: "Graphify Run Script",
    32: "Temp: Probe Utils",
    33: "Changelog",
    34: "Ofertas Mode",
    35: "Project Mode",
    36: "Training Mode",
    37: "Profile Template",
    38: "PolyAI Director Compliance",
}

questions = suggest_questions(G, communities, community_labels)
report = generate(G, communities, cohesion, community_labels, gods, surprises, detection, tokens, '.', suggested_questions=questions)

Path('graphify-out/GRAPH_REPORT.md').write_text(report, encoding='utf-8')
to_json(G, communities, 'graphify-out/graph.json')
to_html(G, communities, 'graphify-out/graph.html', community_labels=community_labels)

analysis = {
    'communities': {str(k): v for k, v in communities.items()},
    'cohesion': {str(k): v for k, v in cohesion.items()},
    'gods': gods,
    'surprises': surprises,
    'questions': questions,
}
Path('.graphify_analysis.json').write_text(json.dumps(analysis, indent=2), encoding='utf-8')
Path('.graphify_labels.json').write_text(json.dumps(community_labels, indent=2), encoding='utf-8')

elapsed = time.time() - start
if G.number_of_nodes() == 0:
    print('ERROR: Graph is empty')
    sys.exit(1)

print(f'Graph build done in {elapsed:.1f}s')
print(f'Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges, {len(communities)} communities')
print(f'God nodes: {len(gods)}')
print(f'Surprising connections: {len(surprises)}')
print(f'HTML: graphify-out/graph.html')
print(f'JSON: graphify-out/graph.json')
print(f'Report: graphify-out/GRAPH_REPORT.md')
