"""Current H authored full Water Shield performance/corner checks, both mappers."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';J=V/'root49-h-water-ei'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not J.exists();J.mkdir()
 cp=R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json';assert sha(cp)=='8de2e8a7799087b1889433123f50352684de3f164148e8d9f8ad0dcb655f387c'
 tests=['megaman-water-performance','bass-water-performance','water-corner-differential'];deps=[R/'tests'/f'{n}.lua'for n in tests]+[R/'tests/water-shield-performance.lua',R/'tests/water-corner-reference.json',R/'tests/menu-bootstrap.lua',R/'tools/run_mesen.py',R/'tools/audit/run_mesen_isolated.py']
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 used=workspace_bytes(R);assert used+200000000<80000000000
 (J/'preparation.json').write_text(json.dumps(dict(script_sha256=sha(__file__),checkpoint_H_sha256=sha(cp),dependencies={str(p.relative_to(R)):sha(p)for p in deps},workspace_before=used,global_cap=80000000000,phase_cap=200000000,reserve=50000000,scope='Existing authored fixtures with emulated setup writes/explicit inventory grants. Eight-bubble orbit and expansion on empty native floor, real OAM DMA and instruction-cycle measurements; separate exact terrain corner output reference. Not ordinary acquisition, populated-level FPS or final media/source-perfect claims.'),indent=2)+'\n')
 groups=[]
 for name in tests:
  for mapper in['mmc3','mmc5']:
   rom=cp.parent/f'smb-crossover-{mapper}.nes';out=J/(mapper+'-'+name)
   args=[sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(out),str(R/'tests'/f'{name}.lua'),str(rom),'--timeout','180']
   (J/(mapper+'-'+name+'-command.json')).write_text(json.dumps(args,indent=2)+'\n')
   with(J/(mapper+'-'+name+'-host.log')).open('wb')as f:q=subprocess.run(args,cwd=R,stdout=f,stderr=subprocess.STDOUT)
   z=dict(fixture=name,mapper=mapper,exit=q.returncode,ROM_sha256=sha(rom),files={str(p.relative_to(J)):dict(bytes=p.stat().st_size,sha256=sha(p))for p in out.rglob('*')if p.is_file()})
   groups.append(z);(J/'partial.json').write_text(json.dumps(groups,indent=2)+'\n');print(name,mapper,q.returncode,flush=True)
 out=J/'review.json';out.write_text(json.dumps(dict(status='PASS_CURRENT_H_EXISTING_WATER_PERFORMANCE_AND_CORNERS'if all(g['exit']==0 for g in groups)else'RETAINED_CURRENT_H_WATER_FIXTURE_FAILURES',preparation_sha256=sha(J/'preparation.json'),groups=groups,analysis_pending=True,goal_complete=False),indent=2)+'\n');print('REVIEW',sha(out),flush=True)
if __name__=='__main__':main()
