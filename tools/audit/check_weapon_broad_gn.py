"""Run the broad Bass fixture with only source-correct Arm expectations."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];O=R/'build/verification/weapons-broad-gn'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists();O.mkdir()
    old=R/'tests/bass-special-weapons.lua';text=old.read_text()
    changes={"assert(r('InvAmmo',145)==104,'Super Arm charges eight units at pickup, not throw')":"assert(r('InvAmmo',145)==112,'Super Arm lift is free; eight units are paid at throw')", "'Second B throws the held brick without a second charge'":"'Second B throws the held brick and pays eight units'"}
    for a,b in changes.items():assert text.count(a)==1;text=text.replace(a,b)
    source=O/'bass-special-weapons.lua';source.write_text(text)
    frozen=R/'build/verification/agent49-super-arm-h-a/test-overlay-s/tests/bass-special-weapons.lua'
    assert source.read_text()==frozen.read_text(),'Use the independently source-backed successor verbatim'
    wrapper=O/'component.lua';wrapper.write_text('dofile([=['+(R/'tests/menu-bootstrap.lua').as_posix()+']=])\ndofile([=['+source.as_posix()+']=])\n')
    cases=[]
    for mapper in ('mmc3','mmc5'):
        rom=R/f'build/verification/weapons-current-gf/source/build/smb-crossover-{mapper}.nes'
        with(O/(mapper+'-host.log')).open('wb')as f:z=subprocess.run([sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(O/mapper),str(wrapper),str(rom),'--timeout','120'],cwd=R,stdout=f,stderr=subprocess.STDOUT)
        cases.append(dict(mapper=mapper,exit=z.returncode,ROM_sha256=sha(rom)));print(mapper,z.returncode,flush=True)
    (O/'summary.json').write_text(json.dumps(dict(passed=all(z['exit']==0 for z in cases),cases=cases,original_fixture_sha256=sha(old),successor_fixture_sha256=sha(source),only_changes=changes,goal_complete=False),indent=2)+'\n')
    assert all(z['exit']==0 for z in cases)


if __name__=='__main__':main()
