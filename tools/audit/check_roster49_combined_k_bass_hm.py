"""Restore explicit external-fixture mode/menu bootstrap; retain HK negatives."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';J=V/'root49-combined-k-native-hk'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 out=J/'bass-bootstrap-successor-hm.json';assert not out.exists()
 fixture=V/'agent49-super-arm-h-a/fixture-r/bass-special-weapons.lua';assert sha(fixture)=='1cecc69c18a38f0243bd533c486c68c311dfea2b8c78507c7e3087d37f269118'
 bootstrap=R/'tests/menu-bootstrap.lua';wrapper=J/'bass-bootstrap-hm.lua';assert not wrapper.exists()
 wrapper.write_text('dofile('+json.dumps(bootstrap.as_posix())+')\ndofile('+json.dumps(fixture.as_posix())+')\n',encoding='utf-8')
 groups=[]
 for mapper in ['mmc3','mmc5']:
  rom=V/'root49-components-combined-k/source/build'/f'smb-crossover-{mapper}.nes';folder=J/f'{mapper}-bass-bootstrap-hm'
  args=[sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(folder),str(wrapper),str(rom),'--timeout','180']
  (J/f'{mapper}-bass-bootstrap-hm-command.json').write_text(json.dumps(args,indent=2)+'\n',encoding='utf-8')
  with(J/f'{mapper}-bass-bootstrap-hm-host.log').open('wb')as log:q=subprocess.run(args,cwd=R,stdout=log,stderr=subprocess.STDOUT)
  groups.append(dict(mapper=mapper,exit=q.returncode,ROM_sha256=sha(rom),files={str(p.relative_to(J)):dict(bytes=p.stat().st_size,sha256=sha(p))for p in folder.rglob('*')if p.is_file()}));print(mapper,q.returncode,flush=True)
 result=dict(status='PASS_PRIVATE_K_CORRECTED_ARM_FIXTURE_WITH_REQUIRED_EXPLICIT_BOOTSTRAP'if all(z['exit']==0 for z in groups)else'RETAINED_PRIVATE_K_BASS_SUCCESSOR_FAILURE',script_sha256=sha(__file__),fixture_sha256=sha(fixture),bootstrap_sha256=sha(bootstrap),wrapper_sha256=sha(wrapper),groups=groups,predecessor='Original HK external-fixture runs failed Metal Blade at age14. run_mesen.py autoloads menu-bootstrap only when script.parent==ROOT/tests, so moving the frozen corrected fixture outside tests removed its required setup. HK negatives remain raw. This wrapper restores the same existing bootstrap explicitly; no source/runtime/fixture assertions are changed.',limits=['Authored setup/grants and real controller attacks, not natural acquisition/fullroute or universal source fidelity.','Combined K still excludes LandV/Ryu/HUD, and exact mixed new-helper/IRQ/source audits remain separate.'],main_changed=False,installed=False,goal_complete=False)
 out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print('BASS_SUCCESSOR',sha(out),flush=True)
if __name__=='__main__':main()
