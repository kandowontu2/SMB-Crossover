"""Root review of frozen D Bass without altering the specialist's frozen files."""
from pathlib import Path
import collections,csv,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'agent49-megaman-bass-current-d-a';O=V/'root49-bass-d-root-review-ce'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not O.exists();O.mkdir()
 freeze=H/'bass-freeze-cg.json';handoff=H/'handoff-ch.json'
 assert sha(freeze)=='a3344559f20727899b69bcad9efa2cabb5eb2d2b2cdf012db44a03a72e2657b9'
 assert sha(handoff)=='0173e475114e6b423923d12b5da59d82f9ce307e7a04f3b0d02bca7ec74ef312'
 f=json.loads(freeze.read_text());h=json.loads(handoff.read_text())
 counts={}
 for kind,files in [('ordinary',f['proofs']['ordinary']),('fixed',f['proofs']['fixed']),('closure',f['canonical_controller_closure']['files']),('receipts',f['local_receipts_and_reproduction'])]:
  for n,q in files.items():
   p=R/n if kind in ['ordinary','fixed','closure']else H/n
   if not p.exists():p=R/n
   assert sha(p)==q['sha256'],(kind,n)
  counts[kind]=len(files)
 for q in h['receipts'].values():assert sha(R/q['path'])==q['sha256']
 cp=R/f['checkpoint'];d=json.loads(cp.read_text());assert sha(cp)==f['checkpoint_sha256']
 source=Path(d['source_directory'])
 for n,v in d['source_hashes'].items():assert sha(source/n)==v,n
 for b in d['builds']:
  for q in b['artifacts'].values():assert sha(R/q['frozen_path'])==q['sha256']
 original=H/'review_fixed_bass.py';text=original.read_text()
 anchor="out=H/f'fixed-review-{a.suffix}.json';assert not out.exists()";assert text.count(anchor)==1
 redirected=O/'review-fixed-redirected.py'
 # Keep the exact reviewer and its true __file__ root; change only destination.
 body=text.replace(anchor,'out=ROOT_REPORT;assert not out.exists()')
 redirected.write_text('ROOT_REPORT='+repr(str(O/'fixed-review.json'))+'\n'+"__file__="+repr(str(original))+'\n'+body.replace('out=ROOT_REPORT;', 'out=Path(ROOT_REPORT);'))
 fixed=R/h['latest_native']['independent_fixed'];ordinary=R/h['latest_native']['source']
 q=subprocess.run([sys.executable,str(redirected),'--fixed',str(fixed.relative_to(R)),'--source',str(ordinary.relative_to(R)),'--suffix','root-cd'],cwd=R,capture_output=True,text=True)
 (O/'host.log').write_text(q.stdout+q.stderr);assert q.returncode==0,q.stdout+q.stderr
 review=json.loads((O/'fixed-review.json').read_text());assert review['result']['frames']==30281
 rows=lambda p:list(csv.DictReader(p.open(newline='')))
 trace=rows(fixed/'trace.csv');assert len(trace[0])==21
 controls=[z for z in trace if(z['world'],z['level'],z['mode'],z['task'],z['engine'])==('1','2','1','3','8')]
 assert len(controls)==25 and int(controls[0]['x'])==40 and int(controls[-1]['x'])>40
 render=rows(fixed/'render.csv');oam=rows(fixed/'oam.csv');assert len(render)==29782 and len(oam)==20943
 for z in oam:
  raw=bytes.fromhex(z['oamHex']);assert len(raw)==256
  edges=collections.Counter();visible=hud=0
  for i in range(0,256,4):
   y=raw[i]+1
   if y<240:
    visible+=1;hud+=y<32;first,last=max(32,y),min(240,y+16)
    if first<last:edges[first]+=1;edges[last]-=1
  n=maximum=0
  for y in range(32,240):n+=edges[y];maximum=max(maximum,n)
  assert(visible,hud,maximum)==tuple(int(z[k])for k in ['visible','hudSprites','maxSprites'])
 out=V/'root49-bass-d-full-review-cd.json';assert not out.exists()
 out.write_text(json.dumps(dict(status='PASS_ROOT_FROZEN_D_BASS_EASY_MMC3_FULL_PROOF',script_sha256=sha(__file__),freeze_sha256=sha(freeze),handoff_sha256=sha(handoff),rehashed=counts,D_source_files=len(d['source_hashes']),independently_executed_reviewer_sha256=sha(original),redirected_reviewer_sha256=sha(redirected),independent_review_sha256=sha(O/'fixed-review.json'),actual_DMA_decodes=len(oam),whole_trace_fields=21,controlled_next_stage_rows=len(controls),support_qualification=h['native_support'],limits=f['limits'],current_G_admitted=False,arsenal_complete=False,final_media_complete=False,goal_complete=False),indent=2)+'\n')
 print('ROOT_BASS_D',sha(out),flush=True)
if __name__=='__main__':main()
