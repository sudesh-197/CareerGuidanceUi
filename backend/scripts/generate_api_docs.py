"""Regenerate docs/API.md from the route decorators.

Usage (from the backend folder):  python scripts/generate_api_docs.py
"""
import ast, glob, os, re
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.dirname(B)
def write(p,s): os.makedirs(os.path.dirname(p),exist_ok=True); open(p,'w',encoding='utf-8',newline='\n').write(s)
rows=[]
def scan(path,bpvar,prefix=''):
    t=ast.parse(open(path,encoding='utf-8').read())
    for n in t.body:
        if not isinstance(n,ast.FunctionDef): continue
        decos=[ast.unparse(d) for d in n.decorator_list]
        auth='token' if any(d in('token_required','_token_required_wrapper') for d in decos) else 'public'
        lim=[re.search(r"\((.*)\)",d).group(1).strip("'\"") for d in decos if d.startswith('limiter.limit')]
        doc=(ast.get_docstring(n) or '').strip().split('\n')[0]
        for d in n.decorator_list:
            if isinstance(d,ast.Call) and ast.unparse(d.func)==f'{bpvar}.route':
                url=prefix+d.args[0].value
                m=[k.value for k in d.keywords if k.arg=='methods']
                methods=[e.value for e in m[0].elts] if m else ['GET']
                rows.append((os.path.basename(path)[:-3] if bpvar=='bp' else 'explore',url,'/'.join(methods),auth,lim[0] if lim else '',doc))
for p in sorted(glob.glob(f'{B}/app/routes/*.py')):
    if not p.endswith('__init__.py'): scan(p,'bp')
scan(f'{B}/app/explore/routes.py','explore_bp','/api/explore')
out=["# API reference","","Generated from the route decorators in `backend/app/routes/` and `backend/app/explore/routes.py`.",
"All JSON endpoints return `{ \"success\": bool, ... }`. **token** = send `Authorization: Bearer <JWT>` (from `/api/login` or `/api/signup`).","",
f"{len(rows)} routes.",""]
cur=None
for mod,url,meth,auth,lim,doc in sorted(rows,key=lambda r:(r[0]!='auth',r[0],r[1])):
    if mod!=cur:
        cur=mod; out+=["",f"## {mod}","","| Method | Path | Auth | Rate limit | Summary |","|---|---|---|---|---|"]
    out.append(f"| {meth} | `{url}` | {auth} | {lim} | {doc} |")
write(f'{D}/docs/API.md','\n'.join(out)+'\n'); print(len(rows),'routes documented')
