"""Retry the progressing Rogue route with the same finite frame/controller bound."""
from pathlib import Path
import argparse
import json
import os
import sys

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/audit'))
import rogue_current_native_v1 as original

O=R/'build/rogue-current-menu-v5'
P=O/'native/route'
D=O/'native/route-retry-v1'


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--prepare-only',action='store_true')
    a=ap.parse_args();sha=original.sha
    if not(D/'ready.json').exists():
        assert not D.exists()
        timed=json.loads((P/'host-timeout.json').read_text());old=json.loads((P/'binding.json').read_text())
        assert not timed['passed']and timed['status']=='HOST_TIMEOUT_PARTIAL_NATIVE_ROUTE_RETAINED'
        assert timed['last_complete_observation']['frame']=='5707'
        assert timed['last_complete_observation']['engine']=='5'
        assert timed['last_complete_observation']['x']=='3265'
        assert old['ROM_sha256']==sha(O/'candidate.nes')==timed['ROM_sha256']
        for p,h in old['inputs'].items():assert sha(p)==h,p
        config=json.loads((P/'config.json').read_text());assert config['limit']==7000
        source=(P/'controller.lua').read_text()
        assert source.count(P.as_posix()+'/')==2
        controller=source.replace(P.as_posix()+'/',D.as_posix()+'/')
        assert controller.replace(D.as_posix()+'/',P.as_posix()+'/')==source
        D.mkdir(parents=True)
        (D/'controller.lua').write_text(controller,newline='\n')
        config.update(out=D.as_posix()+'/',prefix=D.as_posix()+'/')
        (D/'config.json').write_text(json.dumps(config,indent=2)+'\n')
        (D/'driver-source.py').write_bytes(Path(__file__).read_bytes())
        inputs=dict(old['inputs'])
        for p in [P/'controller.lua',P/'config.json',P/'host-timeout.json',P/'binding.json',
                  D/'controller.lua',D/'config.json',D/'driver-source.py',O/'controls.json']:
            inputs[str(p)]=sha(p)
        ready=dict(prepared=True,native_run=False,ROM_sha256=old['ROM_sha256'],host_timeout_seconds=300,
            frame_bound=7000,controller_and_policy_unchanged_except_output_paths=True,inputs=inputs,
            justification='First run advanced normally to actual victory walk,5707frames/x3265;180-second host timeout prevented completion. Same finite gameplay bound retained.')
        (D/'ready.json').write_text(json.dumps(ready,indent=2)+'\n')
    ready=json.loads((D/'ready.json').read_text())
    for p,h in ready['inputs'].items():assert sha(p)==h,p
    assert sha(O/'candidate.nes')==ready['ROM_sha256']
    if a.prepare_only:
        print(json.dumps(dict(prepared=True,output=str(D),ROM_sha256=ready['ROM_sha256'])))
        return
    assert not(D/'capture-budget.json').exists(),'Preserve previous run; no implicit restart'
    os.environ['SMB_RUN_OUTPUT']=str(D)
    result=original.run(D/'controller.lua',O/'candidate.nes',timeout=300,emulator_options=[
        '--doNotSaveSettings','--nes.removeSpriteLimit=false','--nes.ramPowerOnState=AllZeros',
        '--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
    for p,h in ready['inputs'].items():assert sha(p)==h,p
    assert sha(O/'candidate.nes')==ready['ROM_sha256']
    (D/'binding.json').write_text(json.dumps(dict(ROM_sha256=ready['ROM_sha256'],exit_code=result,
        no_native_RAM_writes=True,normal_sprite_limit=True,ready_sha256=sha(D/'ready.json'),
        inputs=ready['inputs']),indent=2)+'\n')
    print(json.dumps(dict(exit_code=result,ROM_sha256=ready['ROM_sha256'])))
    raise SystemExit(result)


if __name__=='__main__':main()
