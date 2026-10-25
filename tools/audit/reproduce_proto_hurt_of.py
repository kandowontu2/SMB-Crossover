"""Passive native reproduction of a legacy low-byte restore in Proto's bank."""
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--route', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    out = a.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    source = a.route.resolve()
    run = (source / 'run.lua').read_text()
    old = 'out=' + json.dumps(source.as_posix() + '/')
    assert run.count(old) == 1 and run.count('replay=nil') == 1
    run = run.replace(old, 'out=' + json.dumps(out.as_posix() + '/'))
    run = run.replace('replay=nil', 'replay=' + json.dumps((source / 'inputs.csv').as_posix()))
    run = run.replace('capture=12,', 'capture=0,')
    debug = a.rom.with_suffix('.dbg')
    text = debug.read_text() if debug.exists() else gzip.decompress(a.rom.with_suffix('.dbg.gz').read_bytes()).decode()
    symbols = {}
    for line in text.splitlines():
        if not line.startswith('sym\t'): continue
        q = dict(s.split('=', 1) for s in line.split('\t', 1)[1].split(',') if '=' in s)
        if 'val' in q: symbols[q['name'].strip('"')] = int(q['val'], 0)
    aliases = ''.join('L.' + n + '=' + str(symbols[n]) + '\n'
                      for n in ['MegaManHurtEnd', 'MegaManHurtReturned'])
    observer = out / 'observer.lua'
    observer.write_text(aliases + 'local output=' + json.dumps(out.as_posix() + '/') + r'''
local frame,inEnd,restores=0,false,0
local f=assert(io.open(output..'restore-writes.csv','w'))
f:write('frame,pc,bank,value,mode,inHurtEnd\n')
local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
local function bank(a)return emu.convertAddress(a).address//8192 end
emu.addMemoryCallback(function()
 if bank(0xa000)==10 then inEnd=true end
end,emu.callbackType.exec,L.MegaManHurtEnd)
emu.addMemoryCallback(function()
 if bank(0xa000)==10 then inEnd=false end
end,emu.callbackType.exec,L.MegaManHurtReturned)
emu.addMemoryCallback(function(_,value)
 if frame<1100 or frame>1350 then return end
 local state=emu.getState()
 f:write(table.concat({frame,state['cpu.pc'],bank(0xa000),value,r('X5ChrMode'),inEnd and 1 or 0},',')..'\n')
 if inEnd and value==64 and r('X5ChrMode')&128~=0 then
  assert(r('SelectedCharacter')==1 and r('ProtoVariant')==1)
  restores=restores+1
 end
end,emu.callbackType.write,L.PlayerChrBank)
emu.addEventCallback(function()
 frame=frame+1
 if frame==1300 then
  f:close();assert(restores>0,'Original Proto path reproduces invalid legacy restore')
  local p=assert(io.open(output..'observed.json','w'))
  p:write(string.format('{"reproduced":true,"invalid_legacy_restores":%d,"frames":%d,"read_only":true}',restores,frame));p:close()
  emu.stop(0)
 end
end,emu.eventType.endFrame)
''')
    at = run.index('dofile(')
    run = run[:at] + 'dofile(' + json.dumps(observer.as_posix()) + ')\n' + run[at:]
    script = out / 'run.lua'; script.write_text(run)
    result = subprocess.run([sys.executable, str(ROOT / 'tools/audit/run_mesen_isolated.py'),
        '--output', str(out), str(script), str(a.rom.resolve()), '--timeout', '60',
        '--option=--nes.ramPowerOnState=AllZeros', '--option=--nes.randomizeCpuPpuAlignment=false',
        '--option=--nes.randomizeMapperPowerOnState=false'], capture_output=True, text=True, cwd=ROOT)
    (out / 'host.log').write_text(result.stdout + result.stderr)
    assert result.returncode == 0, (result.stdout + result.stderr)[-2000:]
    observed = json.loads((out / 'observed.json').read_text())
    q = dict(reproduced=True, known_bug_present=True, accepted=False,
             ROM_sha256=hashlib.sha256(a.rom.read_bytes()).hexdigest(), observed=observed,
             controller_source_sha256=hashlib.sha256((source / 'inputs.csv').read_bytes()).hexdigest(),
             scope='Read-only native exact controller prefix. Old MegaManHurtEnd writes logical64 while Proto explicit-page high bits remain1, producing physical320 instead of the retained hurt-body page267. Negative reproduction; no repaired-build claim.')
    (out / 'proof.json').write_text(json.dumps(q, indent=2) + '\n')
    print(json.dumps(q, indent=2))


if __name__ == '__main__': main()
