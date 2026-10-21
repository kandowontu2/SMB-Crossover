"""Unchanged native water/graphics/foreign special tests on private filter J."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';J=V/'root49-water-filter-native-hd'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not J.exists();J.mkdir()
 assert sha(V/'root49-water-enemy-filter-gy/build-review-ha.json')=='6eedbf9da2b36e9c77fae68200d63b4308c611af1511becb0bf6a197900144d6'
 tests=['megaman-water-performance','bass-water-performance','water-corner-differential','water-motion-differential','water-expansion-differential','water-left-source','water-oam-differential','bass-special-weapons','megaman-special-armor-202'];deps=[R/'tests'/f'{n}.lua'for n in tests]+[R/'tests/water-shield-performance.lua',R/'tests/water-corner-reference.json',R/'tests/menu-bootstrap.lua',R/'tools/run_mesen.py',R/'tools/audit/run_mesen_isolated.py']
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 used=workspace_bytes(R);assert used+200000000<100000000000
 (J/'preparation.json').write_text(json.dumps(dict(script_sha256=sha(__file__),candidate_build_review_sha256=sha(V/'root49-water-enemy-filter-gy/build-review-ha.json'),dependencies={str(p.relative_to(R)):sha(p)for p in deps},workspace_before=used,global_cap=100000000000,phase_cap=200000000,reserve=50000000,scope='PrivateJ: I plus exact50B batch offscreen reject; unchanged authored mechanics/geometry/OAM/native performance and foreign weapons fixtures. Setup/grants mean no ordinary acquisition. Original Bass Arm cost oracle remains wrong and is not promoted to source accuracy; no new Arm implementation is present here.'),indent=2)+'\n',encoding='utf-8')
 groups=[]
 for name in tests:
  for mapper in ['mmc3','mmc5']:
   assert workspace_bytes(J)+16000000+50000000<200000000
   rom=V/'root49-water-enemy-filter-gy/source/build'/f'smb-crossover-{mapper}.nes';out=J/(mapper+'-'+name)
   args=[sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(out),str(R/'tests'/f'{name}.lua'),str(rom),'--timeout','180']
   (J/(mapper+'-'+name+'-command.json')).write_text(json.dumps(args,indent=2)+'\n',encoding='utf-8')
   with(J/(mapper+'-'+name+'-host.log')).open('wb')as f:q=subprocess.run(args,cwd=R,stdout=f,stderr=subprocess.STDOUT)
   groups.append(dict(fixture=name,mapper=mapper,exit=q.returncode,ROM_sha256=sha(rom),files={str(p.relative_to(J)):dict(bytes=p.stat().st_size,sha256=sha(p))for p in out.rglob('*')if p.is_file()}))
   (J/'partial.json').write_text(json.dumps(groups,indent=2)+'\n',encoding='utf-8');print(name,mapper,q.returncode,flush=True)
 out=J/'review.json';out.write_text(json.dumps(dict(status='PASS_PRIVATE_J_18_UNCHANGED_NATIVE_WATER_AND_FOREIGN_GROUPS'if all(g['exit']==0 for g in groups)else'RETAINED_PRIVATE_J_NATIVE_FAILURES',preparation_sha256=sha(J/'preparation.json'),groups=groups,analysis_pending=True,goal_complete=False),indent=2)+'\n',encoding='utf-8');print('NATIVE',sha(out),flush=True)
if __name__=='__main__':main()
