"""Observe the real fallback contacts and inspect their actual direct PPU window."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import math
import subprocess
import sys
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
OBSERVER = '''local f=assert(io.open(GRIP_OUTPUT..'contacts.csv','w'))
f:write('ppuFrame,cycle,x,y,climb,probeX,probeY,footTile,bodyTile,bodySolid\\n')
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function tile(x,y)
 if y<32 or y>=240 then return 0 end
 return r('Block_Buffer_1',(x//256)%2*208+((y-32)//16)*16+(x%256)//16)
end
emu.addMemoryCallback(function()
 if emu.convertAddress(L.Cv3GripWall).address//8192~=GRIP_BANK then return end
 local s=emu.getState();assert((s['cpu.ps']or s['cpu.p'])&1==0)
 local x=r('Player_X_Position')+256*r('Player_PageLoc');local y=r('Player_Y_Position')
 local probe=r('MmProbeX')+256*r('MmProbePage');local py=r('MmProbeY')
 local foot,body=tile(probe,py),tile(probe,y+20)
 local solid=(r('MTileAttribute',body)&3)==1 and 1 or 0
 f:write(table.concat({s['ppu.frameCount'],s['cpu.cycleCount'],x,y,r('Cv3Climb'),probe,py,foot,body,solid},',')..'\\n');f:flush()
end,emu.callbackType.exec,L.Cv3GripWall+8)
local stop=emu.stop
emu.stop=function(code)f:close();stop(code)end
'''


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('rom', 'route', 'capture', 'output'):
        p.add_argument('--' + name, type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    digest = sha(a.rom)
    capture = json.loads((a.capture / 'proof.json').read_text())
    source = json.loads((a.route / 'manifest.json').read_text())
    assert capture['passed'] and capture['ROM_sha256'] == source['ROM_sha256'] == digest
    assert capture['fixed_inputs_and_trace_exact'] and capture['actual_PPU_frame_ids_complete']
    assert source['exit'] == 0 and source['result']['cleared'] and source['result']['deaths'] == 0
    # This tool uses the bundled PIL runtime. Parse the linked debug aliases
    # directly rather than importing the py65-dependent CPU helper.
    symbols, segments = {}, {}
    for line in a.rom.with_suffix('.dbg').read_text().splitlines():
        if not line.startswith(('sym\t', 'seg\t')): continue
        row = dict(x.split('=', 1) for x in line[4:].split(',') if '=' in x)
        if line.startswith('seg\t'): segments[row['id']] = row
        elif 'val' in row: symbols[row['name'].strip('"')] = row
    fields = ('Cv3GripWall', 'Player_X_Position', 'Player_PageLoc', 'Player_Y_Position',
              'Cv3Climb', 'MmProbeX', 'MmProbePage', 'MmProbeY', 'Block_Buffer_1', 'MTileAttribute')
    aliases = ''.join('L[' + json.dumps(n) + ']=' + str(int(symbols[n]['val'], 0)) + '\n' for n in fields)
    helper = symbols['Cv3GripWall']; segment = segments[helper['seg']]
    offset = int(segment['ooffs'], 0) + int(helper['val'], 0) - int(segment['start'], 0)
    bank = (offset - 16) // 8192
    assert bank == 82 and a.rom.read_bytes()[offset + 8] == 0xae
    observer = a.output / 'observer.lua'
    observer.write_text(aliases + 'GRIP_BANK=' + str(bank) + '\nGRIP_OUTPUT=' + json.dumps(a.output.resolve().as_posix() + '/') + '\n' + OBSERVER)
    run = (a.route / 'run.lua').read_text()
    before = 'out=' + json.dumps(a.route.resolve().as_posix() + '/')
    assert run.count(before) == run.count('replay=nil') == run.count('capture=12,') == 1
    run = run.replace(before, 'out=' + json.dumps(a.output.resolve().as_posix() + '/'))
    run = run.replace('replay=nil', 'replay=' + json.dumps((a.route.resolve() / 'inputs.csv').as_posix())).replace('capture=12,', 'capture=0,')
    at = run.index('dofile(')
    script = a.output / 'run.lua'
    script.write_text(run[:at] + 'dofile(' + json.dumps(observer.resolve().as_posix()) + ')\n' + run[at:])
    command = [sys.executable, str(ROOT / 'tools/audit/run_mesen_isolated.py'), '--output', str(a.output),
        str(script), str(a.rom.resolve()), '--timeout', '150', '--option=--nes.ramPowerOnState=AllZeros',
        '--option=--nes.randomizeCpuPpuAlignment=false', '--option=--nes.randomizeMapperPowerOnState=false']
    with (a.output / 'host.log').open('w') as log:
        result = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
    assert result.returncode == 0
    for name in ('inputs.csv', 'trace.csv'):
        assert (a.output / name).read_bytes() == (a.route / name).read_bytes() == (a.capture / name).read_bytes()
    events = list(csv.DictReader((a.output / 'contacts.csv').open()))
    positive = [r for r in events if r['bodySolid'] == '1']
    assert positive
    first = positive[0]
    cluster = [first]
    for row in positive[1:]:
        if row['x'] != first['x'] or int(row['ppuFrame']) - int(cluster[-1]['ppuFrame']) > 5: break
        cluster.append(row)
    start, end = int(first['ppuFrame']) - 8, int(cluster[-1]['ppuFrame']) + 28
    assert 200 <= start < end < source['result']['frames']
    index = {int(r['frame']): r for r in csv.DictReader((a.capture / 'direct-frame-index.csv').open())}
    trace = {int(r['frame']): r for r in csv.DictReader((a.capture / 'trace.csv').open())}
    sheet = Image.new('RGB', (8 * 160, math.ceil((end - start + 1) / 8) * 258), (24, 28, 36))
    draw = ImageDraw.Draw(sheet)
    world_tile = int(first['probeX']) // 16 * 16
    for i, frame in enumerate(range(start, end + 1)):
        path = a.capture / 'frames' / (f'{frame:06d}.png')
        assert sha(path) == index[frame]['PNG_sha256'] and int(index[frame]['ppuFrame']) == frame
        x = world_tile - 32 - int(trace[frame]['camera'])
        with Image.open(path) as image:
            crop = image.convert('RGB').crop((x, 88, x + 80, 208)).resize((160, 240), Image.Resampling.NEAREST)
        cx, cy = i % 8 * 160, i // 8 * 258
        sheet.paste(crop, (cx, cy + 18))
        draw.text((cx + 4, cy + 2), str(frame), fill='white')
    target = a.output / 'every-contact-frame.png'
    sheet.save(target)
    q = dict(passed=True, accepted=False, ROM_sha256=digest, physical_contact_window=[start, end],
        every_physical_window_frame=end - start + 1, fallback_calls=len(events), positive_body_contacts=len(positive),
        first_contact_cluster=cluster, every_selected_PNG_hash_exact=True,
        exact_original_inputs_trace=True, observer_sha256=sha(observer), contact_log_sha256=sha(a.output / 'contacts.csv'),
        capture_proof_sha256=sha(a.capture / 'proof.json'), sheet_sha256=sha(target), driver_sha256=sha(Path(__file__)),
        scope='Read-only exact independent route replay logs actual mapped helper fallthrough after the foot probe fails. Live block-buffer/typed-body contact and actual PPU frame IDs select a complete contiguous direct-frame review window. The sheet contains every frame in that local window; it does not establish exhaustive human review of the whole route.')
    (a.output / 'proof.json').write_text(json.dumps(q, indent=2) + '\n')
    print(json.dumps({k: q[k] for k in ('physical_contact_window', 'every_physical_window_frame', 'fallback_calls', 'positive_body_contacts')}, indent=2))


if __name__ == '__main__': main()
