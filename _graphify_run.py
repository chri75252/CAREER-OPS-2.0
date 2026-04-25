import sys, json, time, os
sys.path.insert(0, r'C:\Users\chris\AppData\Roaming\Python\Python313\site-packages')
from graphify.detect import detect
from pathlib import Path

start = time.time()
result = detect(Path('.'))
elapsed = time.time() - start

with open('.graphify_detect.json','w') as f:
    json.dump(result,f,indent=2)

with open('graphify_run_log.txt','w') as f:
    f.write(f"Elapsed: {elapsed:.1f}s\n")
    f.write(f"Total files: {result['total_files']}\n")
    f.write(f"Total words: {result['total_words']}\n")
    code_files = result.get('files',{}).get('code',[])
    doc_files = result.get('files',{}).get('document',[])
    f.write(f"Code files: {len(code_files)}\n")
    f.write(f"Doc files: {len(doc_files)}\n")
    f.write(f"Warning: {result.get('warning','')}\n")

print(f"Done in {elapsed:.1f}s, {result['total_files']} files")
