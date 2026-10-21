"""Independently rehash the frozen private E source/build/native handoff."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
D=V/'agent49-gq-bill-union-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rec=lambda p:dict(path=Path(p).relative_to(R).as_posix(),bytes=Path(p).stat().st_size,sha256=sha(p))


def resolve(s):
 p=Path(s)
 return p if p.is_absolute()else R/p


def main():
 out=V/'root49-bill-e-review-im.json';assert not out.exists()
 report=dict(status='RUNNING',script_sha256=sha(__file__),scope='Independent identity/integrity review of frozen evidence; does not promote private E to shared main or assert full source geometry/full-route/recording completion.')
 try:
  frozen=D/'freeze-final-e.json'
  assert sha(frozen)=='26906e2583fa23d16eb9669571cdb479f3678b58109a5aa5f7f49d6e9e9b0079'
  f=json.loads(frozen.read_text());assert not f['main_modified']and not f['live_owned_processes']
  checked={}
  def walk(x):
   if isinstance(x,dict):
    if 'sha256'in x and ('path'in x or 'script'in x):
     path=resolve(x.get('archive',x.get('path',x.get('script'))))
     assert path.is_file(),str(path)
     assert sha(path)==x['sha256'],str(path)
     checked[path.relative_to(R).as_posix()]=x['sha256']
    for value in x.values():walk(value)
   elif isinstance(x,list):
    for value in x:walk(value)
  walk(f)
  catalog=json.loads((D/'source-catalog-e.json').read_text());assert len(catalog)==447
  for n,h in catalog.items():assert sha(D/'source-e'/n)==h,n
  overlay=f['overlay']['changes'];assert len(overlay)==21
  for n,values in overlay.items():assert sha(D/'overlay-e'/n)==values['E'],n
  native=json.loads((D/'native-receipt-catalog-final-e.json').read_text());assert len(native)==1024
  native_bytes=0
  for n,h in native.items():
   p=resolve(n);assert sha(p)==h,n;native_bytes+=p.stat().st_size
  reproduction=json.loads((D/'reproduction-e.json').read_text());walk(reproduction)
  groups=[]
  for n,group in reproduction['native_groups'].items():
   p=resolve(n)/'result.json';assert sha(p)==group['result_sha256'],n
   actual=json.loads(p.read_text());assert actual['cases']==group['cases'],n
   assert not actual.get('failures',0),n
   groups.append(dict(path=n,mapper=group['mapper'],cases=actual['cases'],result_sha256=sha(p)))
  artifacts=[]
  for name,build in f['builds'].items():
   artifacts.extend(dict(name=name,kind=k,**a)for k,a in build.items()if isinstance(a,dict)and'path'in a)
  report.update(status='PASS_FROZEN_PRIVATE_E_IDENTITY_INTEGRITY_REVIEW',freeze=rec(frozen),sources=447,overlay_files=21,build_artifacts=artifacts,referenced_records=len(checked),native_files=1024,native_bytes=native_bytes,native_catalog=rec(D/'native-receipt-catalog-final-e.json'),native_groups=groups,declared_cost=f['cost'],qualifications=f['qualifications'],main_changed=False,accepted_release=False,goal_complete=False)
 except Exception as exc:report.update(status='FAIL_RETAINED',error=str(exc));raise
 finally:out.write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(dict(status=report['status'],sources=report['sources'],native_files=report['native_files'],native_groups=len(report['native_groups']))))


if __name__=='__main__':main()
