import json,glob,os,sys
root=r"C:\Users\lyuho\Downloads\GRACE_v2\GRACE_whitepaper_data"
out=open(sys.argv[1],'w',encoding='utf-8')
for d in sorted(glob.glob(root+r"\*\*_claude-sonnet-4-*")):
    b=json.load(open(os.path.join(d,'benchmark_result.json'),encoding='utf-8'))
    t=b.get('task')
    out.write("=== "+os.path.relpath(d,root)+"\n")
    out.write(json.dumps(t,indent=1,ensure_ascii=False)[:4000]+"\n")
    rep=os.path.join(d,'academic_report.md')
    out.write("REPORT words: %d\n"%len(open(rep,encoding='utf-8').read().split()))
