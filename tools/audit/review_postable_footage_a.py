"""Review current delivered footage without rewriting its retained packets."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];O=R/'build/verification/postable-footage-audit-b'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not O.exists();O.mkdir()
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 used=workspace_bytes(R);assert used+1000000000<100000000000
 commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
 roms={mapper:sha(R/'build'/f'smb-crossover-{mapper}.nes')for mapper in ['mmc3','mmc5']}
 source=R/'tools/playthroughs/roster_review.py';code=source.read_text(encoding='utf-8')
 code=code.replace('sheet.save(directory / f"review-contact-{offset // 48 + 1}.png")','sheet.save(ROOT_OUTPUT / directory.name / f"review-contact-{offset // 48 + 1}.png")')
 code=code.replace('(directory / "review.json").write_text','(ROOT_OUTPUT / directory.name / "review.json").write_text')
 assert code.count('ROOT_OUTPUT / directory.name')==2
 namespace={'__name__':'_postable_review','__file__':str(source),'ROOT_OUTPUT':O};exec(compile(code,str(source),'exec'),namespace)
 (O/'verifier-output-redirection.py.txt').write_text(code,encoding='utf-8')
 (O/'preparation.json').write_text(json.dumps(dict(commit=commit,ROMs=roms,review_tool_sha256=sha(source),script_sha256=sha(__file__),workspace_before=used,global_cap=100000000000,phase_cap=1000000000,reserve=250000000,scope='Existing current14 movie/controller packets; decode every frame and correlate telemetry, inspect flags separately. No altered gameplay/ROM/capture packet. User requires postable Easy/Hard upgrades and stomp comparison; these old Easy base movies alone do not establish that.'),indent=2)+'\n',encoding='utf-8')
 roster=[('Bass',9,0),('Bill',3,0),('Mario',0,0),('Mega Man',1,0),('Samus',2,0),('Link',4,0),('Simon',5,0),('Pit',6,0),('Rygar',7,0),('Luigi',8,0),('Ryu',10,0),('Sophia',11,0),('Scrooge',12,0),('Lance',3,1)]
 results=[]
 for name,character,variant in roster:
  packet=R/'build/roster-through-2-2'/f'claude-final-video-{character}-v{variant}-mmc3';m=json.loads((packet/'manifest.json').read_text())
  assert m['rom_sha256']==roms['mmc3']
  delivery=R/'Playthrough Videos'/(name+'.mp4');assert sha(delivery)==m['recording_metadata']['mp4_sha256']
  if(packet/'playthrough.mp4').exists():assert sha(delivery)==sha(packet/'playthrough.mp4')
  out=O/packet.name;out.mkdir()
  review=namespace['review'](packet)
  results.append(dict(name=name,packet=str(packet.relative_to(R)),manifest_sha256=sha(packet/'manifest.json'),delivery_sha256=sha(delivery),review=str((out/'review.json').relative_to(R)),review_sha256=sha(out/'review.json'),decoded=review['decoded_video_frames'],split_flags=len(review['split_timing_candidates']),motion_flags=len(review['motion_candidates']),pixel_flags=len(review['video_vertical_shift_candidates']),flash_flags=len(review['video_background_flash_candidates']),power_levels=sorted({int(z['power'])for z in namespace['rows'](packet/'trace.csv')if z.get('power') is not None})))
  (O/'partial.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8');print('CURRENT_REVIEW',name,results[-1]['decoded'],results[-1]['split_flags'],results[-1]['pixel_flags'],flush=True)
  assert workspace_bytes(O)+250000000<1000000000
 out=O/'index.json';out.write_text(json.dumps(dict(status='AUTOMATED_FULLFRAME_REVIEW_COMPLETE_VISUAL_FLAGS_REQUIRE_MANUAL_INSPECTION',commit=commit,ROMs=roms,movies=results,total_decoded=sum(z['decoded']for z in results),goal_complete=False),indent=2)+'\n',encoding='utf-8');print('FOOTAGE_INDEX',sha(out),flush=True)
if __name__=='__main__':main()
