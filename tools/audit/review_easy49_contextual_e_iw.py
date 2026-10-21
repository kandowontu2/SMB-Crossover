"""Independently bind the complete contextual E packet before QA adoption."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[2];V=R/'build/verification';D=V/'agent49-e-sophia-union-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rec=lambda p:dict(path=Path(p).relative_to(R).as_posix(),bytes=Path(p).stat().st_size,sha256=sha(p))


def resolve(s):
 p=Path(s);return p if p.is_absolute()else R/p


def main():
 out=V/'root49-contextual-e-admission-review-iw.json';assert not out.exists()
 report=dict(status='RUNNING',script_sha256=sha(__file__),scope='Independent frozen identity/build/native receipt/status/ordinary check review for next shared QA checkpoint. Full roster/sourcefidelity/arsenal/routes/lag/final recordings remain incomplete.')
 try:
  frozen=D/'freeze-final-e.json';assert sha(frozen)=='eb873f8e18c7863a67ad342744a871c28b56d259668c3b1cf2eb0851015b9a1f'
  supplement=D/'freeze-supplement-e.json';assert sha(supplement)=='8557d0f28faf88c72a52d88bf12d5399de2b286ae643eee02dd12e073a6d3acf'
  f=json.loads(frozen.read_text());assert not f['main_installed']and not f['owned_live_handles']
  checked={}
  def walk(x):
   if isinstance(x,dict):
    if 'path'in x and'sha256'in x:
     p=resolve(x['path']);assert p.is_file()and sha(p)==x['sha256'],str(p);checked[str(p.relative_to(R))]=x['sha256']
    for y in x.values():walk(y)
   elif isinstance(x,list):
    for y in x:walk(y)
  walk(f);walk(json.loads(supplement.read_text()))
  cat=json.loads((D/'source-catalog-e.json').read_text());assert len(cat)==f['source_files']==449
  for n,h in cat.items():assert sha(D/'source-e'/n)==h,n
  for n,h in f['generated11'].items():assert sha(D/'source-e/build/generated'/n)==h,n
  assert sha(resolve(f['overlay']['zip']))==f['overlay']['zip_sha256']
  for n,values in f['overlay']['changes'].items():assert sha(resolve(f['overlay']['path'])/n)==values['union_E'],n
  statuses={}
  for n,entry in f['reports'].items():
   d=json.loads(resolve(entry['path']).read_text());status=d['status'];assert status=='PASS'or status.startswith('PASS_'),(n,status);statuses[n]=status
  native_files=0;native_groups=[]
  assert len(f['native'])==f['native_executions']==36
  for group in f['native']:
   assert group['exit']==0,group['path']
   for n,h in group['files'].items():assert sha(resolve(group['path'])/n)==h,(group['path'],n);native_files+=1
   p=resolve(group['path'])/'result.json'
   if p.exists():
    result=json.loads(p.read_text());assert not result.get('failures',0),str(p)
   native_groups.append(dict(path=group['path'],cases=group.get('cases'),files=len(group['files'])))
  assert native_files==644,native_files
  ordinary=[]
  assert len(f['ordinary_files'])==4
  for n,files in f['ordinary_files'].items():
   folder=resolve(n)
   for name,h in files.items():assert sha(folder/name)==h,(n,name)
   result=json.loads((folder/'result.json').read_text());assert result['frames']==1780 and result['deaths']==0 and not result['cleared'],result
   ordinary.append(dict(path=n,result=result,files=len(files),input=rec(folder/'inputs.csv')))
  builds=[]
  assert len(f['builds'])==4 and sum(len(x)for x in f['builds'].values())==16
  for n,b in f['builds'].items():
   for ext,a in b.items():assert sha(resolve(a['path']))==a['sha256'],(n,ext)
   builds.append(dict(name=n,artifacts=b))
  cp=R/'build/checkpoints/roster-audit-v49-link-ceiling-gq/manifest.json';old=json.loads(cp.read_text());assert len(old['source_hashes'])==442
  for n,h in old['source_hashes'].items():assert sha(R/n)==h,n
  for b in old['builds']:
   for a in b['artifacts'].values():assert sha(R/a['path'])==a['sha256']
  delta={n:dict(previous=old['source_hashes'].get(n),next=h,exists_now=(R/n).exists())for n,h in cat.items()if old['source_hashes'].get(n)!=h}
  for n,row in delta.items():
   if row['previous']is None and row['exists_now']:assert sha(R/n)==row['next'],('New-path local conflict',n)
  report.update(status='PASS_CONTEXTUAL_E_SCOPED_QA_ADMISSION_REVIEW',freeze=rec(frozen),supplement=rec(supplement),sources=449,source_catalog=rec(D/'source-catalog-e.json'),builds=builds,referenced_record_hashes_checked=len(checked),native_groups=native_groups,native_files=644,ordinary=ordinary,final_report_statuses=statuses,scope_counts=f['scope_counts'],costs=f['costs'],qualifications=f['qualifications'],predecessor=rec(cp),source_changes=delta,main_changed=False,accepted_release=False,goal_complete=False)
 except Exception as exc:report.update(status='FAIL_RETAINED',error=str(exc));raise
 finally:out.write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(dict(status=report['status'],source_changes=len(report['source_changes']),native_files=644,ordinary=4)))


if __name__=='__main__':main()
