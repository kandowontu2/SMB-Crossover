"""Exercise the legacy-only brick expectations in explicitly selected Easy mode."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-samus-head-axis-easy-bu'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not H.exists();H.mkdir();groups=[]
 for rev,folder in [('F',R/'build/checkpoints/roster-audit-v49-freeze-render-fast-f'),('G',V/'root49-samus-head-axis-g2/source/build')]:
  for name in ['samus-zero-wall-contact','samus-head-bricks']:
   fixture=R/f'tests/{name}.lua'
   for mp in ['mmc3','mmc5']:
    out=H/f'{rev}-{mp}-{name}';out.mkdir();wrapper=H/f'{rev}-{mp}-{name}.lua'
    wrapper.write_text('TEST_DIR='+json.dumps((R/'tests').as_posix()+'/')+'\ndofile(TEST_DIR.."menu-bootstrap.lua")\nlocal modeFrame=0\nemu.addEventCallback(function()modeFrame=modeFrame+1;if modeFrame==61 then emu.write(L.CrossoverBehaviorVersion,0,emu.memType.nesDebug)end end,emu.eventType.endFrame)\ndofile('+json.dumps(fixture.as_posix())+')\n')
    rom=folder/f'smb-crossover-{mp}.nes'
    q=subprocess.run([sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(out),str(wrapper),str(rom),'--timeout','180'],cwd=R,capture_output=True,text=True)
    log=H/f'{rev}-{mp}-{name}-host.log';log.write_text(q.stdout+q.stderr)
    groups.append(dict(revision=rev,mapper=mp,fixture=name,fixture_sha256=sha(fixture),wrapper_sha256=sha(wrapper),ROM_sha256=sha(rom),exit=q.returncode,log_sha256=sha(log),files={str(p.relative_to(H)):sha(p)for p in out.rglob('*')if p.is_file()}))
    (H/'partial.json').write_text(json.dumps(groups,indent=2)+'\n');print(rev,mp,name,q.returncode,flush=True)
 (H/'review.json').write_text(json.dumps(dict(script_sha256=sha(__file__),groups=groups,scope='Authored Easy0 fixture. Original legacy suit/brick expectations require Easy; default generic menu-bootstrap chooses Hard1. No original fixture rewritten; no ordinary route/source-perfect or full-suite claim.',main_changed=False),indent=2)+'\n')
 print('EASY_HEAD_REVIEW',sha(H/'review.json'),flush=True)
if __name__=='__main__':main()
