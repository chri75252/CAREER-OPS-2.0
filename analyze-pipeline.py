import re, pathlib, collections, json

text = pathlib.Path(r'career-ops/data/pipeline.md').read_text(encoding='utf-8')
lines = [ln for ln in text.splitlines() if ln.startswith('- [ ] ')]
entries = []
for ln in lines:
    m = re.match(r'- \[ \]\s+([^|]+)\|\s*([^|]+)\|\s*(.+)$', ln)
    if m:
        entries.append((m.group(1).strip(), m.group(2).strip(), m.group(3).strip()))

primary_kw = ['solutions engineer', 'solutions consultant', 'technical account manager', 
              'implementation manager', 'implementation consultant', 'professional services',
              'customer engineer', 'customer success architect']

secondary_kw = ['solutions architect', 'technical program manager', 'delivery manager',
                'product operations', 'revenue operations', 'business systems',
                'ai operations', 'implementation', 'deployment strategist']

noise_kw = ['software engineer', 'ml engineer', 'machine learning engineer', 'research scientist',
            'applied scientist', 'data scientist', 'backend engineer', 'frontend engineer',
            'account executive', 'sales development', 'bdr', 'recruiter']

primary = []
secondary = []
noise = []
other = []

for url, company, title in entries:
    t = title.lower()
    if any(k in t for k in primary_kw):
        primary.append((url, company, title))
    elif any(k in t for k in secondary_kw):
        secondary.append((url, company, title))
    elif any(k in t for k in noise_kw):
        noise.append((url, company, title))
    else:
        other.append((url, company, title))

emea_remote = []
for url, company, title in primary:
    t = title.lower()
    if any(k in t for k in ['emea', 'europe', 'uk', 'germany', 'remote', 'london', 'berlin', 'dublin']):
        emea_remote.append((url, company, title))

report = {
    'total_pending': len(entries),
    'primary_fit_count': len(primary),
    'secondary_fit_count': len(secondary),
    'noise_count': len(noise),
    'other_count': len(other),
    'emea_remote_primary': len(emea_remote),
    'primary_by_company': collections.Counter(c for _, c, _ in primary).most_common(10),
    'secondary_by_company': collections.Counter(c for _, c, _ in secondary).most_common(10),
    'top_primary': [{'company': c, 'title': t, 'url': u} for u, c, t in primary[:25]],
    'top_secondary': [{'company': c, 'title': t, 'url': u} for u, c, t in secondary[:15]],
    'top_emea_remote': [{'company': c, 'title': t, 'url': u} for u, c, t in emea_remote[:20]]
}

pathlib.Path(r'career-ops/data/test-run-analysis.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(f"Analysis complete: {len(entries)} total, {len(primary)} primary, {len(secondary)} secondary, {len(noise)} noise")
print(f"EMEA/Remote primary fit: {len(emea_remote)}")
print("Report saved to career-ops/data/test-run-analysis.json")
