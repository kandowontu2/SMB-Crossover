"""Root frozen G Bass review, followed by a real full fixed H execution."""
from pathlib import Path
import csv,hashlib,json,subprocess,sys,zipfile
R=Path(__file__).resolve().parents[2];V=R/'build/verification';J=V/'root49-bass-g-review-h-transfer-fc';A=V/'agent49-megaman-bass-current-g-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
def main():
 assert not J.exists();J.mkdir()
 freeze=A/'bass-freeze-bu.json';assert sha(freeze)=='77d6a1508cc2b4cae99fc38b3b02eb3ab8e2c59bd90b7700e130a2c0d4e2960e';frozen=read(freeze);checked={}
 def pin(n,z):
  p=R/n;assert p.is_file()and sha(p)==z['sha256'],n
  if 'bytes'in z:assert p.stat().st_size==z['bytes'],n
  checked[str(p.relative_to(R))]=z['sha256']
 def walk(z):
  if isinstance(z,dict):
   if 'path'in z and 'sha256'in z and isinstance(z['path'],str):pin(z['path'],z)
   for k,v in z.items():
    if isinstance(v,dict)and 'sha256'in v and isinstance(k,str)and ('/'in k or '\\'in k)and 'path'not in v:pin(k,v)
    walk(v)
  elif isinstance(z,list):
   for x in z:walk(x)
 walk(frozen);walk(read(A/'megaman-freeze-aa.json'))
 cpG=R/frozen['checkpoint']['path'];g=read(cpG)
 with zipfile.ZipFile(R/frozen['source_archive']['path'])as z:
  for n,h in g['source_hashes'].items():assert hashlib.sha256(z.read(n)).hexdigest()==h
  for n,h in g['generated11'].items():assert hashlib.sha256(z.read('build/generated/'+n)).hexdigest()==h
 source=R/'build/roster-through-2-2/agent49-currentg-bass-finish-bq-9-v0-mmc3';fixed=R/'build/roster-through-2-2/agent49-currentg-bass-fixed-br-9-v0-mmc3'
 commands=[['review_fixed_bass_ai.py','--fixed',str(fixed.relative_to(R)),'--source',str(source.relative_to(R)),'--suffix','rootfc'],['review_bass_hardware_ar.py','--fixed',str(fixed.relative_to(R)),'--suffix','rootfc'],['audit_support_bt.py','--fixed',str(fixed.relative_to(R)),'--suffix','rootfc','--entries','152','--platforms','4','--springs','1']]
 for args in commands:
  with(J/(args[0]+'.log')).open('wb')as log:q=subprocess.run([sys.executable,str(A/args[0])]+args[1:],cwd=R,stdout=log,stderr=subprocess.STDOUT)
  assert q.returncode==0,args
 cp=R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json';assert sha(cp)=='8de2e8a7799087b1889433123f50352684de3f164148e8d9f8ad0dcb655f387c'
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 used=workspace_bytes(R);assert used+200000000<80000000000
 (J/'preparation.json').write_text(json.dumps(dict(script_sha256=sha(__file__),freeze_G_sha256=sha(freeze),root_G_rehashed_files=len(checked),G_source_archive469_rehashed=True,root_G_review_files={n:sha(A/n)for n in ['fixed-review-rootfc.json','bass-hardware-review-rootfc.json','bass-support-review-rootfc.json']},checkpoint_H_sha256=sha(cp),G_manifest_sha256=sha(fixed/'manifest.json'),workspace_before=used,phase_cap=200000000,reserve=100000000,global_cap=80000000000,scope='Actual root frozen G source/catalogue/support/spring/full DMA review, then separate actual H power-on whole fixed replay. Every original G source, rectangle, audio, tier and arsenal limitation retained.'),indent=2)+'\n')
 out=R/'build/roster-through-2-2/root49-h-bass-fc-9-v0-mmc3';args=[sys.executable,str(R/'tools/playthroughs/roster_run.py'),'--character','9','--mapper','mmc3','--rom',str(cp.parent/'smb-crossover-mmc3.nes'),'--tag','root49-h-bass-fc','--policy',str(fixed/'policy.lua'),'--replay',str(fixed/'inputs.csv'),'--frames','33000','--timeout','900','--workspace-cap-gb','80']
 (J/'H-command.json').write_text(json.dumps(args,indent=2)+'\n')
 with(J/'H-native.log').open('wb')as log:q=subprocess.run(args,cwd=R,stdout=log,stderr=subprocess.STDOUT)
 m=read(out/'manifest.json');names=['inputs.csv','trace.csv','events.csv','render.csv','oam.csv','chr.csv','scroll-writes.csv','audio-events.csv','stomp-events.csv','mm-injury-owner.csv','bass-movement-input.csv','natural-pickups.csv','bass-source-state.csv','bass-fresh-ground-entry.csv']
 streams={n:dict(literal=sha(out/n)==sha(fixed/n),H_sha256=sha(out/n),G_sha256=sha(fixed/n))for n in names if (out/n).exists()}
 good=q.returncode==0 and m['verified_through_2_2']and m['result']==frozen['result']and len(streams)==14 and all(z['literal']for z in streams.values());hardware=None
 if good:
  assert m['rom_sha256']=='df226ab7be27a0f0b9231c1a66ac16200ba487ee041be10308dd6757343a8d6f'and m['full_frame_audit']and m['controller_only']and not m['memory_or_register_writes']
  sys.path.insert(0,str(R/'tools/audit'));from review_roster49_h_transfers_dl import hardware as decode
  hardware=decode(out,m['result']['frames']);assert hardware['actual_DMA']==20585
  trace=list(csv.DictReader((out/'trace.csv').open()));tail=trace[-25:];assert all((z['world'],z['level'],z['engine'],z['mode'],z['task'])==('1','2','8','1','3')for z in tail)and tail[0]['x']=='40'and tail[-1]['x']=='66'
 catalogue={str(p.relative_to(R)):dict(bytes=p.stat().st_size,sha256=sha(p))for p in out.rglob('*')if p.is_file()};catalog=J/'H-root-catalog.json';catalog.write_text(json.dumps(catalogue,indent=2)+'\n')
 report=dict(status='PASS_ROOT_G_BASS_REVIEW_AND_ACTUAL_H_FULL_FIXED_BASE_ROUTE'if good else'RETAINED_H_BASS_TRANSFER_NEGATIVE',script_sha256=sha(__file__),preparation_sha256=sha(J/'preparation.json'),G_freeze_sha256=sha(freeze),G_rehashed_files=len(checked),exit=q.returncode,H_manifest=str((out/'manifest.json').relative_to(R)),H_manifest_sha256=sha(out/'manifest.json'),actual_ROM=m['rom_sha256'],verified=good,result=m.get('result'),streams=streams,hardware=hardware,H_catalog_sha256=sha(catalog),limitations=frozen['limitations']+['Actual H is separately executed; literal whole streams preserve the original scoped G support and source qualifications. No H/MMC5 or complete arsenal/media claim.'],goal_complete=False)
 (J/'review.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status=report['status'],sha256=sha(J/'review.json'),result=report['result'],hardware=hardware)),flush=True)
if __name__=='__main__':main()
