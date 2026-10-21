"""Read actual movement/button consumers during the retained 1-2 failure."""
from pathlib import Path
import csv, hashlib, importlib.util, json, subprocess, sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-megaman-jump-observe-cm'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    H.mkdir(exist_ok=False)
    dep = V / 'agent49g-samus-crouch-fix-proposal-b/image.py'
    spec = importlib.util.spec_from_file_location('jump_cm_image', dep)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    rom = R / 'build/smb-crossover-mmc3.nes'
    im = m.Image(rom)
    assert sha(rom) == '8c79f8f0e8f0c0a0d987d8d828aa2bcd377df89a5c4f4b4cf6c54984a3a947be'
    parent = R / 'build/roster-through-2-2/root49cl-megaman-live-1-v0-mmc3'
    replay = parent / 'inputs.csv'
    hooks = {name: im.hook(label, scope) for name, label, scope in [
        ('Movement', 'MegaManMovement', None), ('CheckJump', 'CheckJump', 'MegaManMovement'),
        ('Jump', 'Jump', 'MegaManMovement'), ('JumpReady', 'JumpReady', 'MegaManMovement'),
        ('CheckSlide', 'CheckSlide', 'MegaManMovement')]}
    fields = ['Player_State', 'Player_X_Position', 'Player_PageLoc', 'Player_Y_Position', 'A_B_Buttons',
              'PreviousA_B_Buttons', 'SavedJoypadBits', 'MmSliding', 'MmJumpReleased', 'MmFrictionYActive',
              'MmVY', 'Player_Y_Speed', 'TimerControl', 'GameEngineSubroutine']
    assert all(n in im.ram for n in fields)
    cfg = dict(hooks=hooks, fields=fields, ROM=im.metadata(), ram=im.ram)
    (H / 'binding.json').write_text(json.dumps(cfg, indent=2) + '\n')
    policy = H / 'policy.lua'
    policy.write_text('local c=' + m.lua(cfg) + '\n' + '''
local frame,poll,sel,mode=0,0,0,0
local regs={}
emu.addMemoryCallback(function(_,v)sel=v&7;mode=(v>>6)&1 end,emu.callbackType.write,0x8000)
emu.addMemoryCallback(function(_,v)if sel>=6 then regs[sel]=v&63 end end,emu.callbackType.write,0x8001)
local function bank(pc)
 if pc>=0xe000 then return 63 end
 if pc>=0xc000 then return mode==0 and 62 or(regs[6]or-1)end
 if pc>=0xa000 then return regs[7]or-1 end
 return mode==0 and(regs[6]or-1)or62
end
local f=assert(io.open(ROSTER_CONFIG.out..'jump-consumers.csv','w'))
f:write('frame,poll,hook,cycle,'..table.concat(c.fields,',')..',qVY\\n')
for name,h in pairs(c.hooks)do
 emu.addMemoryCallback(function()
  if frame<6920 or frame>7040 or bank(h.address)~=h.physical_bank then return end
  for i,v in ipairs(h.bytes)do assert(emu.read(h.address+i-1,emu.memType.nesDebug)==v,'Actual movement hook bytes')end
  local row={frame,poll,name,emu.getState()['cpu.cycleCount']}
  for _,n in ipairs(c.fields)do row[#row+1]=emu.read(c.ram[n],emu.memType.nesDebug)end
  row[#row+1]=emu.read(c.ram.MmVY,emu.memType.nesDebug)+256*emu.read(c.ram.MmVY+1,emu.memType.nesDebug)+65536*emu.read(c.ram.MmVY+2,emu.memType.nesDebug)
  f:write(table.concat(row,',')..'\\n');f:flush()
 end,emu.callbackType.exec,h.address)
end
emu.addEventCallback(function()poll=poll+1 end,emu.eventType.inputPolled)
emu.addEventCallback(function()frame=frame+1 end,emu.eventType.endFrame)
return function(c)return{}end
''')
    # Compile the Lua source without executing any emulator operations.
    sys.path.insert(0, str(V / 'agent47-samus-controller-batch-h-preparation/parser/runtime'))
    from lupa.lua54 import LuaRuntime
    LuaRuntime().execute('assert(load(...))', policy.read_text())
    tag = 'root49cm-megaman-observe'
    log_path = H / 'host.log'
    with log_path.open('wb') as log:
        rc = subprocess.run([sys.executable, str(R / 'tools/playthroughs/roster_run.py'), '--character', '1',
            '--mapper', 'mmc3', '--rom', str(rom), '--tag', tag, '--replay', str(replay), '--policy', str(policy),
            '--frames', '36000', '--timeout', '240', '--workspace-cap-gb', '50'], cwd=R,
            stdout=log, stderr=subprocess.STDOUT).returncode
    folder = R / 'build/roster-through-2-2' / (tag + '-1-v0-mmc3')
    result = json.loads((folder / 'result.json').read_text()) if (folder / 'result.json').exists() else None
    trace = list(csv.DictReader((folder / 'trace.csv').open())) if (folder / 'trace.csv').exists() else []
    expected = list(csv.DictReader((parent / 'trace.csv').open()))
    exact = trace == expected
    observations = list(csv.DictReader((folder / 'jump-consumers.csv').open())) if (folder / 'jump-consumers.csv').exists() else []
    report = dict(status='PASS_PASSIVE_CM_IDENTICAL_NATIVE_NEGATIVE' if exact and observations else 'RETAINED_CM_OBSERVER_NEGATIVE',
                  exit=rc, script_sha256=sha(__file__), binding_sha256=sha(H / 'binding.json'), policy_sha256=sha(policy),
                  replay_sha256=sha(replay), result=result, all_trace_fields_exact_parent=exact,
                  observations=len(observations), output=folder.relative_to(R).as_posix(),
                  qualification='Read-only physical-bank/eight-byte guarded movement/button observations. Identical failed route is a preserved native negative, not a playthrough clear.',
                  accepted_release=False, goal_complete=False)
    (H / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'], sha(H / 'report.json'), 'rows', len(observations), flush=True)


if __name__ == '__main__':
    main()
