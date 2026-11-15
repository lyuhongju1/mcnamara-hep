import json,glob,os,sys
root=r"C:\Users\lyuho\Downloads\GRACE_v2\GRACE_whitepaper_data"
out=open(sys.argv[1],'w',encoding='utf-8')
for d in sorted(glob.glob(root+r"\opticks*\*_claude-sonnet-4-*"))+sorted(glob.glob(root+r"\celeritas*\*_claude-sonnet-4-*")):
    if 'higgs' in d: continue
    t=json.load(open(os.path.join(d,'benchmark_result.json'),encoding='utf-8'))['task']
    out.write("=== "+os.path.relpath(d,root)+"\n"+t.get('context','')[900:2000]+"\n")
