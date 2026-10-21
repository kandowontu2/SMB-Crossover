"""Independently rehash frozen G Scrooge, then execute the whole input tape on H."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';J=V/'root49-scrooge-g-review-h-transfer-ej';H=V/'specialist-mario-luigi-scrooge-current-g-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not J.exists();J.mkdir()
 pins={'milestone-freeze-scrooge-al.json':'b987931dcd55a683cd1006a409638a079c0fcfcb97a815e4bb38d0ab2b20353b','milestone-handoff-scrooge-al.json':'0372d9fc12a1d10cc0d5c6b44805edefbca8c7d8e9bbae9dccdfe89739c3f548','review-scrooge-al.py':'fff9cd6e55b6cf73033d4ad73117a48e21f681bb8225d21262a8f9313c64995a'}
 for n,h in pins.items():assert sha(H/n)==h
 args=[sys.executable,str(H/'review-scrooge-al.py'),'--catalogue','milestone-freeze-scrooge-al.json','--catalogue-sha256',pins['milestone-freeze-scrooge-al.json'],'--handoff','milestone-handoff-scrooge-al.json','--handoff-sha256',pins['milestone-handoff-scrooge-al.json']]
 q=subprocess.run(args,cwd=R,capture_output=True,text=True);(J/'G-root-review.log').write_text(q.stdout+q.stderr);assert q.returncode==0,q.stderr
 g=json.loads(q.stdout);assert g['catalogued_files']==1188 and g['actual_DMA_decoded']==20271 and g['result']['frames']==21742
 (J/'G-root-review.json').write_text(json.dumps(g,indent=2)+'\n')
 hand=json.loads((H/'milestone-handoff-scrooge-al.json').read_text());source=R/hand['proof'];m=json.loads((source/'manifest.json').read_text());assert m['verified_through_2_2']and m['rom_sha256']=='151f3f6e8aa8753fce088c3f2ba6815df7290c1ec3b959018ca4717ae8f491cc'
 cp=R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json';assert sha(cp)=='8de2e8a7799087b1889433123f50352684de3f164148e8d9f8ad0dcb655f387c'
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 used=workspace_bytes(R);assert used+200000000<80000000000
 (J/'preparation.json').write_text(json.dumps(dict(script_sha256=sha(__file__),G_pins=pins,G_root_review_sha256=sha(J/'G-root-review.json'),checkpoint_H_sha256=sha(cp),source_G_manifest_sha256=sha(source/'manifest.json'),source_G_inputs_sha256=sha(source/'inputs.csv'),workspace_before=used,phase_cap=200000000,reserve=100000000,global_cap=80000000000,scope='Root independent G catalogue/source/support/full-DMA review followed by actual cold H fullfixed replay. Original G corner/body-edge/spring/source/weapon/media limitations retained. Observer guards must match actual H bytes; no fictional G-to-H retag.'),indent=2)+'\n')
 out=R/'build/roster-through-2-2/root49-h-scrooge-ej-12-v0-mmc3'
 args=[sys.executable,str(R/'tools/playthroughs/roster_run.py'),'--character','12','--mapper','mmc3','--rom',str(cp.parent/'smb-crossover-mmc3.nes'),'--tag','root49-h-scrooge-ej','--policy',str(source/'policy.lua'),'--replay',str(source/'inputs.csv'),'--frames','25000','--timeout','900','--workspace-cap-gb','80']
 (J/'H-command.json').write_text(json.dumps(args,indent=2)+'\n')
 with(J/'H-native.log').open('wb')as f:q=subprocess.run(args,cwd=R,stdout=f,stderr=subprocess.STDOUT)
 a=json.loads((out/'manifest.json').read_text());streams={}
 for n in['inputs.csv','trace.csv','events.csv','render.csv','oam.csv','chr.csv','scroll-writes.csv','audio-events.csv','stomp-events.csv','ordinary-telemetry.csv','ordinary-native-events.jsonl']:
  if(out/n).exists():streams[n]=dict(literal=(out/n).read_bytes()==(source/n).read_bytes(),H_sha256=sha(out/n),G_sha256=sha(source/n))
 result=dict(status='PASS_G_ROOT_REVIEW_AND_ACTUAL_H_FIXED_SCROOGE_BASE_TRANSFER'if q.returncode==0 and a['verified_through_2_2']and len(streams)==11 and all(z['literal']for z in streams.values())else'RETAINED_H_TRANSFER_NEGATIVE',script_sha256=sha(__file__),preparation_sha256=sha(J/'preparation.json'),G_root_review_sha256=sha(J/'G-root-review.json'),exit=q.returncode,H_manifest=str((out/'manifest.json').relative_to(R)),H_manifest_sha256=sha(out/'manifest.json'),actual_ROM=a['rom_sha256'],verified=a['verified_through_2_2'],result=a.get('result'),streams=streams,root_H_hardware_decode_pending=True,source_limits=hand['limits'],goal_complete=False)
 (J/'review.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status=result['status'],sha256=sha(J/'review.json'),result=result['result'])),flush=True)
if __name__=='__main__':main()
