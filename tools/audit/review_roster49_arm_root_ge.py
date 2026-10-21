"""Root read-only raw packet rehash and full compiled native-caller replay."""
from pathlib import Path
import contextlib,hashlib,io,json,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'agent49-super-arm-h-a';O=V/'root49-arm-root-review-ge'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
def main():
 assert not O.exists();O.mkdir()
 packet=H/'implementation-freeze-s.json';assert sha(packet)=='9056be7f01c2b1cb8b0ca443c2fcbb12f17fec15096bc5d66b5212de230dd09c'
 seen={}
 def check(desc):
  n=Path(desc['path']);p=n if n.is_absolute()else R/n if(R/n).exists()else H/n
  assert p.exists(),p
  assert sha(p)==desc['sha256'],p
  if 'bytes'in desc:assert p.stat().st_size==desc['bytes']
  seen[str(p.relative_to(R))]=desc['sha256'];return p
 def walk(x):
  if isinstance(x,dict):
   if 'path'in x and 'sha256'in x:check(x)
   for v in x.values():walk(v)
  elif isinstance(x,list):
   for v in x:walk(v)
 j=read(packet);walk(j)
 for k in ['source_catalog','production_overlay','artifact_catalog','native_receipts','negative_catalog','source_proof','test_successor','methods','reproduction','terminal_jobs']:walk(read(check(j[k])))
 source=read(H/'source-catalog-s.json');S=R/source['source_root'];assert len(source['source_hashes'])==470
 for n,h in source['source_hashes'].items():assert sha(S/n)==h
 methods=read(H/'method-inputs-s.json')
 for n,d in methods.items():
  p=R/n;assert sha(p)==d['sha256']and p.stat().st_size==d['bytes'];seen[n]=d['sha256']
 n=read(H/'native-receipts-s.json')
 for p,d in n['files'].items():
  pp=R/p if(R/p).exists()else H/p;assert sha(pp)==d['sha256']and pp.stat().st_size==d['bytes'];seen[str(pp.relative_to(R))]=d['sha256']
 original=H/'review_callers_j.py';text=original.read_text(encoding='utf-8')
 old="dest=H/f'caller-review-{a.suffix}.json'";new="dest=ROOT_OUTPUT/f'caller-review-{a.suffix}.json'";assert text.count(old)==1
 modified=text.replace(old,new);(O/'root-caller-verifier.py.txt').write_text(modified,encoding='utf-8')
 groups=[]
 for i,ref in enumerate(n['caller_reviews']):
  report=read(R/ref['path']);tag=report['tag'];suffix=f'{i:02d}'
  previous=sys.argv;sys.argv=[str(original),'--tag',tag,'--suffix',suffix]
  stream=io.StringIO()
  try:
   with contextlib.redirect_stdout(stream):exec(compile(modified,str(original),'exec'),{'__name__':'__main__','__file__':str(original),'ROOT_OUTPUT':O})
  finally:sys.argv=previous
  (O/f'caller-{i:02d}.log').write_text(stream.getvalue(),encoding='utf-8')
  got=read(O/f'caller-review-{suffix}.json');assert got==report
  differences=[dict(id=q['id'],native=q['native_cycles'],instruction=q['instruction_cycles'])for q in got['calls']if q['native_cycles']!=q['instruction_cycles']]
  groups.append(dict(tag=tag,calls=len(got['calls']),report_sha256=sha(O/f'caller-review-{suffix}.json'),all_original_report_fields_literal=True,native_vs_instruction_cycle_differences=differences))
  print('ROOT_CALLERS',tag,len(got['calls']),flush=True)
 assert sum(g['calls']for g in groups)==180
 out=O/'review.json';out.write_text(json.dumps(dict(status='PASS_ROOT_FROZEN_ARM_PACKET_AND_180_FULL_COMPILED_CALLER_REEXECUTIONS',packet_sha256=sha(packet),script_sha256=sha(__file__),source_files=470,artifacts=16,raw_receipt_files=len(seen),groups=groups,verifier_change='Only destination path redirected outside immutable specialist phase. All assertions/oracles/source byte logic unmodified.',source_payment='Lift gated by cost8 but free; throw spends8 or Starfree, refuses insufficient stock before held-slot/projectile mutation. Explicit32 source witnesses and32 instrumented repetitions remain component-scoped.',limits=j['limits'],main_changed=False,installed=False,goal_complete=False),indent=2)+'\n',encoding='utf-8');print('REVIEW',sha(out),flush=True)
if __name__=='__main__':main()
