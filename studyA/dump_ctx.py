import json,glob,os,sys
root=r"C:\Users\lyuho\Downloads\GRACE_v2\GRACE_whitepaper_data"
out=open(sys.argv[1],'w',encoding='utf-8')
for d in sorted(glob.glob(root+r"\*\*_claude-sonnet-4-*")):
    if 'higgs' in d: continue
    t=json.load(open(os.path.join(d,'benchmark_result.json'),encoding='utf-8'))['task']
    c=t.get('context','')
    out.write("=== "+os.path.relpath(d,root)+"\n"+c[1500:]+"\n")
