"""Independent frozen Rush packet/caller reexecution, with exact qualifiers."""
from pathlib import Path
import contextlib,hashlib,io,json,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'agent49-rush-h-a';O=V/'root49-rush-root-review-gw'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
def main():
 assert not O.exists();O.mkdir()
 packet=H/'mechanics-freeze-r.json';assert sha(packet)=='bec997191e0c697046e60c036b8acbc4562acaf62622de1fa8c2c2ac49798ae6';j=read(packet)
 for n,h in j['source_catalog'].items():assert sha(R/j['source_path']/n)==h,n
 for n,z in j['artifacts'].items():assert sha(H/n)==z['sha256']and(H/n).stat().st_size==z['bytes'],n
 for n,z in j['receipts'].items():assert sha(H/n)==z['sha256']and(H/n).stat().st_size==z['bytes'],n
 for n,h in j['source_receipts'].items():assert sha(R/n)==h,n
 for n,h in j['changes'].items():assert sha(H/j['overlay']/n)==h['after'],n
 reports=[]
 for n in j['receipts']:
  if not Path(n).name.startswith('caller-review-')or not n.endswith('.json'):continue
  z=read(H/n)
  if z.get('status')=='PASS_ACTUAL_RUSH_CALLERS_COMPILED_REEXECUTION_AND_SOURCE_ORACLES':reports.append((n,z))
 assert sum(len(z['calls'])for _,z in reports)==143
 groups=[]
 for i,(n,report)in enumerate(reports):
  original=H/('review_j.py'if'foreign-j'in n else'review_h.py');code=original.read_text(encoding='utf-8')
  old="dest=H/f'caller-review-{a.suffix}.json'";assert code.count(old)==1
  modified=code.replace(old,"dest=ROOT_OUTPUT/f'caller-review-{a.suffix}.json'")
  target=O/(original.name+'.txt')
  if not target.exists():target.write_text(modified,encoding='utf-8')
  previous=sys.argv;suffix=f'{i:02d}';sys.argv=[str(original),'--tag',report['tag'],'--suffix',suffix];stream=io.StringIO()
  try:
   with contextlib.redirect_stdout(stream):exec(compile(modified,str(original),'exec'),{'__name__':'__main__','__file__':str(original),'ROOT_OUTPUT':O})
  finally:sys.argv=previous
  (O/f'caller-{i:02d}.log').write_text(stream.getvalue(),encoding='utf-8')
  got=read(O/f'caller-review-{suffix}.json');assert got==report
  assert all(z['native_cycles']==z['instruction_cycles']for z in got['calls'])
  groups.append(dict(tag=report['tag'],calls=len(got['calls']),report_sha256=sha(O/f'caller-review-{suffix}.json'),all_original_report_fields_literal=True))
  print('ROOT_RUSH_CALLERS',report['tag'],len(got['calls']),flush=True)
 original=H/'review_q.py';code=original.read_text(encoding='utf-8');old="p=H/'review-q.json'";assert code.count(old)==1
 modified=code.replace(old,"p=ROOT_OUTPUT/'review-q.json'");(O/'review_q.py.txt').write_text(modified,encoding='utf-8');stream=io.StringIO()
 with contextlib.redirect_stdout(stream):exec(compile(modified,str(original),'exec'),{'__name__':'__main__','__file__':str(original),'ROOT_OUTPUT':O})
 (O/'edge-foreign-lifetime.log').write_text(stream.getvalue(),encoding='utf-8')
 q=read(O/'review-q.json');assert q==read(H/'review-q.json')
 assert len(q['foreign'])==4 and len(q['stack_liveness'])==8 and len(q['isolated_source_edges'])==560
 out=O/'review.json';out.write_text(json.dumps(dict(status='PASS_ROOT_FROZEN_RUSH_COMPONENT_143_EXACT_NATIVE_CALLER_REEXECUTIONS_AND_560_SOURCE_EDGES',script_sha256=sha(__file__),packet_sha256=sha(packet),source_files=len(j['source_catalog']),artifacts=len(j['artifacts']),raw_receipt_files=len(j['receipts']),source_receipts=len(j['source_receipts']),groups=groups,source_edge_foreign_lifetime_sha256=sha(O/'review-q.json'),source_rules=j['source_rules'],layout=j['layout'],costs=j['costs'],limits=j['limits'],verifier_change='Only output destinations redirected outside immutable frozen phase; every original assertion and every result field remains literal. Exact143 native fullcall AXYP/SP/PC/all10240RAM/orderedwrite/mapper reexecutions plus560 authored source edges, four bound relocation pairs and eight opcode/SP dummy-read lifetimes.',main_changed=False,installed=False,goal_complete=False),indent=2)+'\n',encoding='utf-8')
 print('ROOT_RUSH_REVIEW',sha(out),flush=True)
if __name__=='__main__':main()
