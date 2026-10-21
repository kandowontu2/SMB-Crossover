"""Unchanged native water/graphics/foreign special tests on private filter J."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';J=V/'root49-combined-k-native-hk'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not J.exists();J.mkdir()
 assert sha(V/'root49-components-combined-k/build-review-hj.json')=='8178d16675961c3d801ef19f0cff208482a0273333748ecd6d61e951212fb7ea'
 tests=['megaman-water-performance','bass-water-performance','water-corner-differential','water-motion-differential','water-expansion-differential','water-left-source','water-oam-differential','bass-special-weapons','megaman-special-armor-202'];deps=[R/'tests'/f'{n}.lua'for n in tests]+[R/'build/verification/agent49-super-arm-h-a/fixture-r/bass-special-weapons.lua',R/'tests/water-shield-performance.lua',R/'tests/water-corner-reference.json',R/'tests/menu-bootstrap.lua',R/'tools/run_mesen.py',R/'tools/audit/run_mesen_isolated.py']
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 used=workspace_bytes(R);assert used+200000000<100000000000
 (J/'preparation.json').write_text(json.dumps(dict(script_sha256=sha(__file__),candidate_build_review_sha256=sha(V/'root49-components-combined-k/build-review-hj.json'),dependencies={str(p.relative_to(R)):sha(p)for p in deps},workspace_before=used,global_cap=100000000000,phase_cap=200000000,reserve=50000000,scope='PrivateK: reviewed audio/cache+J batch reject+Arm+Rush mechanics, bothmappers. Eight unchanged Water/armor fixtures plus frozen corrected Arm fixtureS: free funded lift,8-unit throw. All other original Bass assertions retained. Setup/grants mean no ordinary acquisition/fullroute/source/finalmovie claim. Land/Ryu/HUD are not yet included.'),indent=2)+'\n',encoding='utf-8')
 groups=[]
 for name in tests:
  for mapper in ['mmc3','mmc5']:
   assert workspace_bytes(J)+16000000+50000000<200000000
   rom=V/'root49-components-combined-k/source/build'/f'smb-crossover-{mapper}.nes';out=J/(mapper+'-'+name)
   fixture=R/'build/verification/agent49-super-arm-h-a/fixture-r/bass-special-weapons.lua'if name=='bass-special-weapons'else R/'tests'/f'{name}.lua'
   args=[sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(out),str(fixture),str(rom),'--timeout','180']
   (J/(mapper+'-'+name+'-command.json')).write_text(json.dumps(args,indent=2)+'\n',encoding='utf-8')
   with(J/(mapper+'-'+name+'-host.log')).open('wb')as f:q=subprocess.run(args,cwd=R,stdout=f,stderr=subprocess.STDOUT)
   groups.append(dict(fixture=name,mapper=mapper,exit=q.returncode,ROM_sha256=sha(rom),files={str(p.relative_to(J)):dict(bytes=p.stat().st_size,sha256=sha(p))for p in out.rglob('*')if p.is_file()}))
   (J/'partial.json').write_text(json.dumps(groups,indent=2)+'\n',encoding='utf-8');print(name,mapper,q.returncode,flush=True)
 out=J/'review.json';out.write_text(json.dumps(dict(status='PASS_PRIVATE_K_18_NATIVE_WATER_ARM_AND_FOREIGN_GROUPS'if all(g['exit']==0 for g in groups)else'RETAINED_PRIVATE_K_NATIVE_FAILURES',preparation_sha256=sha(J/'preparation.json'),groups=groups,analysis_pending=True,goal_complete=False),indent=2)+'\n',encoding='utf-8');print('NATIVE',sha(out),flush=True)
if __name__=='__main__':main()
