"""Retained real H video/audio for four complete base routes; arsenal remains open."""
from pathlib import Path
import datetime,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';J=V/'root49-h-base-captures-di'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not J.exists();J.mkdir()
 review=V/'root49-h-roster-transfer-dg/review.json';assert sha(review)=='e6b84b04f17a3a874faef982a983c5f1478f74ebb6ad6a5ddbca269d99499d96'
 j=json.loads(review.read_text());assert j['status']=='PASS_FOUR_ACTUAL_H_MMC3_COMPLETE_FIXED_TRANSFERS'
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 total=workspace_bytes(R);assert total+2500000000<80000000000
 prep=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),script_sha256=sha(__file__),source_review_sha256=sha(review),encoder_sha256=sha(R/'tools/playthroughs/encode_capture_delivery.py'),workspace_before=total,global_cap=80000000000,phase_cap=2500000000,reserve=500000000,authority='User retain lossless captures; raise cap. Existing global allocation80GB remains. No deletion.',scope='Four H/Easy/MMC3 ordinary complete base-route recordings, full native frame/audio observations and exact lossless RGB/PCM verification. Not every weapon/upgrade, enemy/item, route-variant or universal final-release certification.')
 (J/'preparation.json').write_text(json.dumps(prep,indent=2)+'\n');results=[]
 names=['inputs.csv','trace.csv','events.csv','render.csv','oam.csv','chr.csv','scroll-writes.csv','audio-events.csv','stomp-events.csv']
 for q in j['results']:
  source=(R/q['manifest']).parent;m=json.loads((source/'manifest.json').read_text());assert sha(source/'manifest.json')==q['manifest_sha256']
  owned=sum(p.stat().st_size for p in J.rglob('*')if p.is_file())
  for d in(R/'build/roster-through-2-2').glob('root49-h-video-di-*'):owned+=sum(p.stat().st_size for p in d.rglob('*')if p.is_file())
  assert owned+900000000<2500000000 and workspace_bytes(R)+900000000<80000000000
  tag='root49-h-video-di-'+q['character'];out=R/'build/roster-through-2-2'/(tag+'-'+str(q['selected'])+'-v0-mmc3')
  args=[sys.executable,str(R/'tools/playthroughs/roster_run.py'),'--character',str(q['selected']),'--mapper','mmc3','--rom',str(source/'smb-crossover-mmc3.nes'),'--tag',tag,'--policy',str(source/'policy.lua'),'--replay',str(source/'inputs.csv'),'--frames',str(q['result']['frames']+100),'--timeout','900','--workspace-cap-gb','80','--record-segments','--keep-avi']
  (J/(q['character']+'-command.json')).write_text(json.dumps(args,indent=2)+'\n')
  with(J/(q['character']+'-native.log')).open('wb')as f:p=subprocess.run(args,cwd=R,stdout=f,stderr=subprocess.STDOUT)
  a=json.loads((out/'manifest.json').read_text());same={n:dict(literal=(source/n).read_bytes()==(out/n).read_bytes(),sha256=sha(out/n))for n in names}
  z=dict(character=q['character'],exit=p.returncode,manifest=str((out/'manifest.json').relative_to(R)),manifest_sha256=sha(out/'manifest.json'),result=a.get('result'),verified=a['verified_through_2_2'],recording_verified=a.get('recording_verified'),streams=same,all_literal=all(v['literal']for v in same.values()),lossless=a.get('lossless_verification_sha256'),delivery=a.get('delivery_report_sha256'))
  results.append(z);(J/'partial.json').write_text(json.dumps(results,indent=2)+'\n');print(q['character'],p.returncode,z['verified'],z['recording_verified'],z['all_literal'],flush=True)
  if not(p.returncode==0 and z['verified']and z['recording_verified']and z['all_literal']):break
 (J/'review.json').write_text(json.dumps(dict(status='PASS_FOUR_H_BASE_ROUTE_CAPTURES'if len(results)==4 and all(z['recording_verified']and z['all_literal']for z in results)else'RETAINED_CAPTURE_NEGATIVE',preparation_sha256=sha(J/'preparation.json'),results=results,frame_by_frame_visual_review_complete=False,whole_arsenal_complete=False,goal_complete=False),indent=2)+'\n')
 print('CAPTURE_REVIEW',sha(J/'review.json'),flush=True)
if __name__=='__main__':main()
