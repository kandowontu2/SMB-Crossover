"""Bind private G native regressions to exact candidate artifacts and fixtures."""
from pathlib import Path
import hashlib, importlib.util, json, subprocess, sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
H=V/'root49-samus-head-axis-g-check-bs';G=V/'root49-samus-head-axis-g2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    assert not H.exists();H.mkdir()
    build=G/'build-review.json';assert sha(build)=='d5d027fbd9783851c830e0ff08d7fb1efcbf0aac7db0773336ff958ce69df753'
    helper=V/'agent49g-samus-crouch-fix-proposal-b/image.py'
    sp=importlib.util.spec_from_file_location('axis_checks',helper);im=importlib.util.module_from_spec(sp);sp.loader.exec_module(im)
    fixtures=['coral-side-jump','samus-head-displacement','samus-zero-wall-contact','samus-head-bricks','samus-powerups','samus-water']
    paths={n:(V/'root49-current-f-samus-coral-regression-br/coral-side-jump.lua'if n=='coral-side-jump'else R/f'tests/{n}.lua')for n in fixtures}
    dependencies={str(p.relative_to(R)):sha(p)for p in list(paths.values())+[R/'tests/menu-bootstrap.lua',R/'tests/guest-powerup-animation.lua',R/'tools/run_mesen.py',R/'tools/audit/run_mesen_isolated.py',helper]}
    sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
    size=workspace_bytes(R);assert size+120000000<80000000000
    pre=dict(script_sha256=sha(__file__),build_review_sha256=sha(build),dependencies=dependencies,
      workspace_before=size,global_cap_bytes=80000000000,phase_cap_bytes=120000000,reserve_bytes=20000000,
      scope='Explicit authored collision/component fixtures. Not an ordinary route, natural acquisition, full-arsenal or final-media proof.',main_changed=False)
    (H/'preparation.json').write_text(json.dumps(pre,indent=2)+'\n')
    groups=[]
    for name in fixtures:
        for mapper in ['mmc3','mmc5']:
            for n,h in dependencies.items():assert sha(R/n)==h,n
            image=im.Image(G/f'source/build/smb-crossover-{mapper}.nes')
            out=H/f'{mapper}-{name}';out.mkdir()
            fixture=paths[name]
            if name=='coral-side-jump':
                hooks=dict(BG=image.hook('PlayerBGCollision'),HeadDone=image.hook('Done',scope='SamusHeadProbe'))
                wrapper=H/f'{mapper}-coral.lua'
                wrapper.write_text('CORAL_HOOKS='+im.lua(hooks)+'\nTEST_DIR='+im.lua((R/'tests').as_posix()+'/')+'\ndofile(TEST_DIR.."menu-bootstrap.lua")\ndofile('+im.lua(fixture.as_posix())+')\n')
                fixture=wrapper
            q=subprocess.run([sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(out),str(fixture),str(image.path),'--timeout','180'],cwd=R,capture_output=True,text=True)
            log=H/f'{mapper}-{name}-host.log';log.write_text(q.stdout+q.stderr)
            groups.append(dict(mapper=mapper,fixture=name,exit=q.returncode,host_log_sha256=sha(log),files={str(p.relative_to(H)):dict(bytes=p.stat().st_size,sha256=sha(p))for p in out.rglob('*')if p.is_file()}))
            (H/'partial.json').write_text(json.dumps(groups,indent=2)+'\n')
            print(mapper,name,'exit',q.returncode,flush=True)
    out=H/'review.json'
    out.write_text(json.dumps(dict(status='PASS_PRIVATE_G_SAMUS_REGRESSIONS'if all(g['exit']==0 for g in groups)else'RETAINED_PRIVATE_G_REGRESSION_FAILURES',script_sha256=sha(__file__),preparation_sha256=sha(H/'preparation.json'),groups=groups,main_changed=False,goal_complete=False),indent=2)+'\n')
    print('REGRESSION_REVIEW',sha(out),flush=True)
if __name__=='__main__':main()
