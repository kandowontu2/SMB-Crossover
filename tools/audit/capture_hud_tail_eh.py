"""Capture real numeric calls during fixed ordinary controller prefixes."""
from pathlib import Path
import concurrent.futures
import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
O = V / 'hud-tail-native-er'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    global O
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate',type=Path,default=V/'hud-tail-dz/source')
    parser.add_argument('--tag',default='hud-tail-native-er')
    args=parser.parse_args()
    O=V/args.tag
    assert not O.exists()
    O.mkdir()
    spec = importlib.util.spec_from_file_location('hud_eh_image', V / 'agent49g-samus-crouch-fix-proposal-b/image.py')
    a = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(a)
    source = V / 'agent49-water-visible-j-a/caller_k.lua'
    observer = source.read_text().replace("assert(rd(h.address+i-1)==v,'Actual H Arm compiled entry8 '..name)", "assert(rd(h.address+i-1)==v,'Actual HUD compiled entry8 '..name)")
    observer = observer.replace('local isrs,isrSerial={},0', 'local isrs,isrSerial={},0\nlocal seenISR={}')
    old = "local ir={id=isrSerial,name=name,captured=#pending>0};isrs[#isrs+1]=ir"
    new = "local capture=#pending>0 or (#isrs>0 and isrs[#isrs].captured) or (frame>=550 and not seenISR[name]);if capture then seenISR[name]=true end;local ir={id=isrSerial,name=name,captured=capture};isrs[#isrs+1]=ir"
    assert observer.count(old) == 1
    observer = observer.replace(old, new)
    old = 'if #pending==0 then return end'
    assert observer.count(old) == 2
    observer = observer.replace(old, 'if #pending==0 and not(#isrs>0 and isrs[#isrs].captured)then return end')
    # Keep the balanced physical-bank-qualified ISR observer. The old Arm-only
    # name/window is not used: the public numeric routine is HudNumber.
    prefix = R / 'build/roster-through-2-2/search/rygar-mushroom-eb/best-inputs.csv'
    jobs = []
    for version in ('CW', 'DZ'):
        for mapper in ('mmc3', 'mmc5'):
            folder = O / f'{version}-{mapper}'
            native = folder / 'native'
            native.mkdir(parents=True)
            rom = (R / 'build/checkpoints/water-visible-cw/build' if version == 'CW' else args.candidate / 'build') / f'smb-crossover-{mapper}.nes'
            im = a.Image(rom)
            hooks = dict(HudNumber=im.hook('UpdateNumber'), NMI=im.hook('NonMaskableInterrupt'), NMIEnd=im.hook('NonMaskableInterrupt', delta='last'),
                         IRQ=im.hook('IrqScrollSplit'), IRQEnd=im.hook('IrqScrollSplit', delta='last'))
            config = dict(out=native.as_posix()+'/', character=7, observeSelected=0, hooks=hooks)
            driver = 'CFG='+a.lua(config)+'\n'+observer+'\n'+r'''
local f,poll=0,0
local fixed={}
for line in io.lines(__PREFIX__)do
 local p,n,mask=line:match('^(%d+),(%d+),(%d+)$')
 if p then fixed[tonumber(p)]={frame=tonumber(n),mask=tonumber(mask)}end
end
emu.addEventCallback(function()
 poll=poll+1;local q=assert(fixed[poll]);assert(q.frame==f,'HUD capture fixed input/frame synchronization')
 local b={};for n,bit in pairs({a=128,b=64,select=32,start=16,up=8,down=4,left=2,right=1})do b[n]=(q.mask&bit)~=0 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 f=f+1
 if f==5200 then
  assert(emu.read(L.SelectedCharacter,emu.memType.nesDebug)==7,'Ordinary menu selects Rygar')
  local out=assert(io.open(CFG.out..'endpoint.png','wb'));out:write(emu.takeScreenshot());out:close()
  print('PASS bounded ordinary-controller HUD capture at5200; no emulated state writes');emu.stop(0)
 end
end,emu.eventType.endFrame)
'''.replace('__PREFIX__', a.lua(prefix.as_posix()))
            fixture = folder / 'component.lua'
            fixture.write_text(driver)
            binding = dict(ROM=im.metadata(), config=config, input_sha256=sha(prefix), fixture_sha256=sha(fixture), observer_parent_sha256=sha(source),
                           scope='Fixed ordinary Rygar input prefix. No memory/ROM/register/state writes; bounded5200frame observation, not a full clear.')
            (folder / 'binding.json').write_text(json.dumps(binding, indent=2)+'\n')
            command = [sys.executable, str(R / 'tools/audit/run_mesen_isolated.py'), '--output', str(native), str(fixture), str(rom), '--timeout', '180',
                       '--option=--nes.ramPowerOnState=AllZeros', '--option=--nes.randomizeCpuPpuAlignment=false', '--option=--nes.randomizeMapperPowerOnState=false']
            jobs.append((version, mapper, folder, command))

    def run(job):
        version, mapper, folder, command = job
        with (folder/'host.log').open('wb') as log:
            result = subprocess.run(command, cwd=R, stdout=log, stderr=subprocess.STDOUT)
        print(version, mapper, result.returncode, flush=True)
        return dict(version=version, mapper=mapper, exit=result.returncode, log_sha256=sha(folder/'host.log'))

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(run, jobs))
    report = dict(passed=all(z['exit']==0 for z in results), groups=results, goal_complete=False)
    (O/'summary.json').write_text(json.dumps(report, indent=2)+'\n')
    assert report['passed']


if __name__ == '__main__':
    main()
