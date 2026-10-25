from pathlib import Path
D=Path(__file__).resolve().parent
s=(D/'replay_mmc3_ship_routes_v25.py').read_text(encoding='utf-8')
s=s.replace("V=D/'mmc3-ship-lives-v25';O=V/'direct-v1'","V=D/'mmc3-static-call-v37';O=V/'direct-sophia-v1'")
old="source=V/'native-routes-v1/proof.json';q=json.loads(source.read_text());assert q['passed']and q['complete']and len(q['runs'])==4"
new="""source=V/'native-sophia-v2/proof.json';q=json.loads(source.read_text());assert q['passed']and q['complete']
route=V/'native-sophia-v2/fresh'
q=dict(runs=[dict(identity='sophia',mode='easy',folder=str(route),manifest_sha256=sha(route/'manifest.json'))])"""
assert s.count(old)==1
s=s.replace(old,new).replace('Four independent fixed-input native MMC3 full1-1 replays','One independent fixed-input native MMC3 Sophia full1-1 replay')
anchor="for n in ('inputs.csv','trace.csv'):assert(out/n).read_bytes()==(route/n).read_bytes(),n"
replacement="""for n in ('inputs.csv','trace.csv'):assert(out/n).read_bytes()==(route/n).read_bytes(),n
  tiny=json.loads((out/'full-smc-guard.json').read_text());assert tiny['passed']and tiny['minimum_SP_from_stack_write_addresses']>=tiny['stack_floor']
  committed=json.loads((out/'completed-loop-motion.json').read_text())if(out/'completed-loop-motion.json').exists()else None
  entry['full_tiny_stack_guard']=tiny"""
assert s.count(anchor)==1
s=s.replace(anchor,replacement)
exec(compile(s,str(D/'replay_mmc3_ship_routes_v25.py'),'exec'),globals())
