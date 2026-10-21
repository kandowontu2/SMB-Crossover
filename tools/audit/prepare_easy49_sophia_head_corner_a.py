"""Bind a read-only native head/corner observation to frozen current C."""
from pathlib import Path
import hashlib
import importlib.util
import json

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
D = V / 'root49-sophia-current-c-route-a'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = D / 'head-corner-binding-a.json'
    assert not out.exists()
    spec = importlib.util.spec_from_file_location('image49', V / 'agent49k-samus-water-up-direction-component-a/image.py')
    image = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(image)
    rom = V / 'root49-combined-working-c/source/build/smb-crossover-mmc3.nes'
    im = image.Image(rom)
    assert sha(rom) == 'a4765d19bb90d476f78e14240f4d3b2bf8ee0fa0eda7f8425a9aaea407921005'
    hooks = []
    for name, scope in [('SophiaSourceHeadProbe', None), ('Separate', 'SophiaSourceHeadProbe'),
                        ('ReturnTile', 'SophiaSourceHeadProbe'), ('Empty', 'SophiaSourceHeadProbe'),
                        ('SophiaSourceAfterTerrain', None)]:
        h = im.hook(name, scope)
        h['event'] = name
        hooks.append(h)
    fields = 'Player_PageLoc Player_X_Position Player_Y_Position MmXFraction MmYFraction MmVX MmVY RyWallOldPage RyWallOldX RyWallOldXFine RyWallOldXFrac RyWallOldY RyWallOldYFine RyWallOldYFrac RyWallSupported Player_State Player_X_Speed Player_Y_Speed RgTempX RgTempPage RgTempY RgTemp2 SmHeadX SmHeadPage SmCeilingHit SmTempY SmClearance R2 R3 R4 R6 R7 XgRise'.split()
    # Enumerate the source Q8.16 fields rather than relying on integer speeds.
    columns = []
    for n in fields:
        columns.extend([(n, im.ram[n] + j) for j in range(3)] if n in ('MmVX', 'MmVY') else
                       [(n, im.ram[n] + j) for j in range(2)] if n in ('MmXFraction', 'MmYFraction') else [(n, im.ram[n])])
    names = [f'{n}+{j}' if names_so_far else n for n, names_so_far, j in []]  # no hidden symbol inference
    names = []
    counts = {}
    for n, a in columns:
        j = counts.get(n, 0)
        names.append(n if j == 0 else f'{n}+{j}')
        counts[n] = j + 1
    policy = '''dofile(IDENTITY)
local H=HOOKS
local ADDRS=ADDRS_VALUE
local f=0
local out=assert(io.open(ROSTER_CONFIG.out..'head-corner-a.csv','w'))
out:write(HEADER)
local function r(a)return emu.read(a,emu.memType.nesDebug)end
local function emit(event,h)
 local st=emu.getState();local v={f,event,h and h.address or -1,h and h.physical_bank or -1,st['cpu.a'],st['cpu.x'],st['cpu.y'],st['cpu.ps'],st['cpu.sp']}
 for _,a in ipairs(ADDRS)do v[#v+1]=r(a)end
 out:write(table.concat(v,',')..'\\n');out:flush()
end
for _,h in ipairs(H)do
 emu.addMemoryCallback(function()
  if f<900 or f>1120 then return end
  local a=emu.convertAddress(h.address)
  if not a or a.memType~=emu.memType.nesPrgRom or a.address//8192~=h.physical_bank then return end
  for i,b in ipairs(h.bytes)do assert(r(h.address+i-1)==b,'Frozen current C head observer eight bytes')end
  emit(h.event,h)
 end,emu.callbackType.exec,h.address)
end
emu.addEventCallback(function()f=f+1;if f>=900 and f<=1120 then emit('endFrame')end end,emu.eventType.endFrame)
return function()return{}end
'''
    policy = policy.replace('IDENTITY', json.dumps((D / 'identity.lua').as_posix())).replace('HOOKS', image.lua(hooks)).replace('ADDRS_VALUE', image.lua([a for n, a in columns]))
    policy = policy.replace('HEADER', json.dumps(','.join(['frame', 'event', 'pc', 'bank', 'A', 'X', 'Y', 'P', 'SP'] + names) + '\n'))
    (D / 'head-corner-policy-a.lua').write_text(policy)
    parent = R / 'build/roster-through-2-2/root49-sophia-current-c-a-11-v0-mmc3'
    record = dict(status='PREPARED_NATIVE_READ_ONLY_HEAD_CORNER_OBSERVER', script_sha256=sha(__file__),
                  ROM=im.metadata(), hooks=hooks, columns=dict(zip(names, [a for n, a in columns])),
                  input_parent=parent.relative_to(R).as_posix(), input_sha256=sha(parent / 'inputs.csv'),
                  policy_sha256=sha(D / 'head-corner-policy-a.lua'), emulated_writes=False,
                  phase_cap_bytes=1000000000, final_reserve_bytes=100000000, global_cap_bytes=70000000000)
    out.write_text(json.dumps(record, indent=2) + '\n')
    print('Prepared actual frozen-C native Sophia head/corner observer.')


if __name__ == '__main__':
    main()
