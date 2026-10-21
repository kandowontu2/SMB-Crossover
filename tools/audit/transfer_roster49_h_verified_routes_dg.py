"""Fresh complete H/MMC3 replays of four frozen, root-reviewed G routes."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';J=V/'root49-h-roster-transfer-dg'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not J.exists();J.mkdir()
 cp=R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json';assert sha(cp)=='8de2e8a7799087b1889433123f50352684de3f164148e8d9f8ad0dcb655f387c';h=json.loads(cp.read_text());rom=cp.parent/'smb-crossover-mmc3.nes';assert sha(rom)=='df226ab7be27a0f0b9231c1a66ac16200ba487ee041be10308dd6757343a8d6f'
 assert sha(V/'root49-samus-audio-adoption-dd/review.json')=='6317c78ac227f4a2c22103090a261e1eb1fc3ff24f6e2bcd749e421445e008e8'
 assert sha(V/'root49-current-route-review-cm.json')=='ed8e80955df544744f0b1cc704e2db34faceb22b4bc3b40e495e52b58718cfe9';assert sha(V/'root49-megaman-g-full-review-df.json')=='676f12af4a21437cfbfccc22c18db38b00265babe58ee0ab0d0cec7561d4c656'
 hand=V/'specialist-mario-luigi-scrooge-current-g-a/milestone-handoff-j.json';assert sha(hand)=='dbe7c1fba625f744d11accbbbcef22d39440fa8010ff7977b508428f08569ca7';ml=json.loads(hand.read_text())
 cases=[]
 for char,name in[(0,'mario'),(8,'luigi')]:
  receipt=json.loads((R/ml['accepted'][str(char)+'/Easy/mmc3']['receipt']).read_text());cases.append(dict(char=char,name=name,source=receipt['proof']))
 cases+=[dict(char=4,name='link',source='build/roster-through-2-2/lsr-current-g-link-a-4-v0-mmc3'),dict(char=1,name='megaman',source='build/roster-through-2-2/agent49-currentg-mm-fixed-v-1-v0-mmc3')]
 for q in cases:
  source=R/q['source'];m=json.loads((source/'manifest.json').read_text());assert m['rom_sha256']=='151f3f6e8aa8753fce088c3f2ba6815df7290c1ec3b959018ca4717ae8f491cc'and m['verified_through_2_2']
  q.update(source_manifest_sha256=sha(source/'manifest.json'),input_sha256=sha(source/'inputs.csv'),policy_sha256=sha(source/'policy.lua'),original_result=m['result'])
  body=(source/'policy.lua').read_text();assert not any(t in body for t in['emu.write(','emu.setState(','emu.loadSavestate'])
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 total=workspace_bytes(R);assert total+400000000<80000000000
 pre=dict(script_sha256=sha(__file__),checkpoint_H_sha256=sha(cp),ROM_H_sha256=sha(rom),cases=cases,phase_cap=400000000,reserve=100000000,global_cap=80000000000,workspace_before=total,scope='Four independent cold complete fixed H/MMC3 replays of frozen root-admitted G streams. Existing passive G observer bytes/address guards reused only where actual H compiled bytes remain identical; any unexpected hook assertion fails. No prefix/adaptive tail/state grants, and no automatic cross-revision or mapper inference.')
 (J/'preparation.json').write_text(json.dumps(pre,indent=2)+'\n');results=[]
 names=['inputs.csv','trace.csv','events.csv','render.csv','oam.csv','chr.csv','scroll-writes.csv','audio-events.csv','stomp-events.csv']
 for q in cases:
  before=workspace_bytes(R);owned=sum(p.stat().st_size for p in J.rglob('*')if p.is_file())
  for d in(R/'build/roster-through-2-2').glob('root49-h-*-dg-*'):owned+=sum(p.stat().st_size for p in d.rglob('*')if p.is_file())
  assert owned+180000000<400000000 and before+80000000<80000000000
  source=R/q['source'];tag='root49-h-'+q['name']+'-dg';out=R/'build/roster-through-2-2'/(tag+'-'+str(q['char'])+'-v0-mmc3')
  args=[sys.executable,str(R/'tools/playthroughs/roster_run.py'),'--character',str(q['char']),'--mapper','mmc3','--rom',str(rom),'--tag',tag,'--policy',str(source/'policy.lua'),'--replay',str(source/'inputs.csv'),'--frames','50000','--timeout','900','--workspace-cap-gb','80']
  (J/(q['name']+'-command.json')).write_text(json.dumps(args,indent=2)+'\n')
  with(J/(q['name']+'-native.log')).open('wb')as f:proc=subprocess.run(args,cwd=R,stdout=f,stderr=subprocess.STDOUT)
  m=json.loads((out/'manifest.json').read_text());comparison={n:dict(literal=(out/n).read_bytes()==(source/n).read_bytes(),sha256=sha(out/n),G_sha256=sha(source/n))for n in names if(out/n).exists()}
  extra={}
  for n in ['ordinary-telemetry.csv','ordinary-native-events.jsonl','mm-source-state.csv','movement-input.csv','mm-fresh-ground-entry.csv','natural-pickups.csv','mm-injury-owner.csv','link-native.csv','final-ram.csv']:
   if(source/n).exists()and(out/n).exists():extra[n]=dict(literal=(source/n).read_bytes()==(out/n).read_bytes(),sha256=sha(out/n),G_sha256=sha(source/n))
  result=dict(character=q['name'],selected=q['char'],exit=proc.returncode,manifest=str((out/'manifest.json').relative_to(R)),manifest_sha256=sha(out/'manifest.json'),actual_ROM=m['rom_sha256'],result=m.get('result'),verified=m['verified_through_2_2'],full_frame_audit=m['full_frame_audit'],canonical=comparison,extra=extra,all_literal=all(z['literal']for z in list(comparison.values())+list(extra.values())))
  results.append(result);(J/'partial.json').write_text(json.dumps(results,indent=2)+'\n');print(q['name'],proc.returncode,m.get('result',{}).get('frames'),result['all_literal'],flush=True)
 out=J/'review.json';out.write_text(json.dumps(dict(status='PASS_FOUR_ACTUAL_H_MMC3_COMPLETE_FIXED_TRANSFERS'if all(q['exit']==0 and q['verified']and q['all_literal']for q in results)else'RETAINED_H_TRANSFER_NEGATIVES',preparation_sha256=sha(J/'preparation.json'),results=results,source_revision='G',executed_revision='H',source_and_runtime_limits='Actual replays, no source-perfect/arsenal/fullmedia inference; all original proof limitations remain.',goal_complete=False),indent=2)+'\n');print('TRANSFER_REVIEW',sha(out),flush=True)
if __name__=='__main__':main()
