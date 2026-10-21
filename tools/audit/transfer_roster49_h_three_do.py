"""Actual H fixed replays of independently reviewed F Bill/Lance/Sophia routes."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';J=V/'root49-h-three-transfer-do'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not J.exists();J.mkdir()
 cp=R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json';assert sha(cp)=='8de2e8a7799087b1889433123f50352684de3f164148e8d9f8ad0dcb655f387c';rom=cp.parent/'smb-crossover-mmc3.nes'
 refs={'root49-lance-f-full-review-ca.json':'82a5739180507824f70ce918e5df7111100b1c3dfeeb0f09eab3c0387faadaad','root49-sophia-f-full-review-ba.json':'60d0999d8e19088b915984abdc9550e708bbd12b18cd8ef4569f3904f0864031'}
 for n,h in refs.items():assert sha(V/n)==h
 cases=[(3,0,'bill','specialist-f-bill-fixed-v-3-v0-mmc3'),(3,1,'lance','specialist-f-lance-fixed-aj-3-v1-mmc3'),(11,0,'sophia','lsr-sophia-f-l-11-v0-mmc3')]
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 total=workspace_bytes(R);assert total+400000000<80000000000
 prep=dict(script_sha256=sha(__file__),checkpoint_H_sha256=sha(cp),ROM_H_sha256=sha(rom),source_F_root_reviews=refs,cases=cases,workspace_before=total,phase_cap=400000000,reserve=100000000,global_cap=80000000000,scope='Three actual H full fixed native replays of root-reviewed F controller streams. Source F proofs retain F identity. Existing passive source hook guards must match actual H bytes; no metadata retag, no assumed pass or all-arsenal/media/source-perfect inference.')
 (J/'preparation.json').write_text(json.dumps(prep,indent=2)+'\n');results=[]
 names=['inputs.csv','trace.csv','events.csv','render.csv','oam.csv','chr.csv','scroll-writes.csv','audio-events.csv','stomp-events.csv']
 for ident,variant,name,src in cases:
  source=R/'build/roster-through-2-2'/src;m=json.loads((source/'manifest.json').read_text());assert m['verified_through_2_2']and m['rom_sha256']=='ae0f981a8846238185d2d69549accf69f68b779832cafa7dd35bc431b00b09ca'
  owned=sum(p.stat().st_size for p in J.rglob('*')if p.is_file())
  for d in(R/'build/roster-through-2-2').glob('root49-h-*-do-*'):owned+=sum(p.stat().st_size for p in d.rglob('*')if p.is_file())
  assert owned+180000000<400000000 and workspace_bytes(R)+80000000<80000000000
  tag='root49-h-'+name+'-do';out=R/'build/roster-through-2-2'/(tag+'-'+str(ident)+'-v'+str(variant)+'-mmc3')
  args=[sys.executable,str(R/'tools/playthroughs/roster_run.py'),'--character',str(ident),'--variant',str(variant),'--mapper','mmc3','--rom',str(rom),'--tag',tag,'--policy',str(source/'policy.lua'),'--replay',str(source/'inputs.csv'),'--frames','50000','--timeout','900','--workspace-cap-gb','80']
  (J/(name+'-command.json')).write_text(json.dumps(args,indent=2)+'\n')
  with(J/(name+'-native.log')).open('wb')as f:q=subprocess.run(args,cwd=R,stdout=f,stderr=subprocess.STDOUT)
  a=json.loads((out/'manifest.json').read_text());same={n:dict(literal=(source/n).read_bytes()==(out/n).read_bytes(),H_sha256=sha(out/n),F_sha256=sha(source/n))for n in names if(out/n).exists()}
  extra={}
  for n in['bill-native-events.jsonl','bill-telemetry.csv','sophia-native.csv','ordinary-native-events.jsonl','final-ram.csv']:
   if(source/n).exists()and(out/n).exists():extra[n]=dict(literal=(source/n).read_bytes()==(out/n).read_bytes(),H_sha256=sha(out/n),F_sha256=sha(source/n))
  z=dict(character=name,identity=ident,variant=variant,source=str(source.relative_to(R)),source_manifest_sha256=sha(source/'manifest.json'),manifest=str((out/'manifest.json').relative_to(R)),manifest_sha256=sha(out/'manifest.json'),exit=q.returncode,result=a.get('result'),verified=a['verified_through_2_2'],actual_ROM=a['rom_sha256'],streams=same,extra=extra,all_literal=len(same)==9 and all(v['literal']for v in list(same.values())+list(extra.values())))
  results.append(z);(J/'partial.json').write_text(json.dumps(results,indent=2)+'\n');print(name,q.returncode,z['verified'],z['all_literal'],flush=True)
 (J/'review.json').write_text(json.dumps(dict(status='PASS_THREE_ACTUAL_H_FIXED_TRANSFERS'if all(z['exit']==0 and z['verified']and z['all_literal']for z in results)else'RETAINED_TRANSFER_NEGATIVES',results=results,goal_complete=False),indent=2)+'\n');print('REVIEW',sha(J/'review.json'),flush=True)
if __name__=='__main__':main()
