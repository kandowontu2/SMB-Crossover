"""Compare hardware cadence while a natural Goomba is on screen in Easy 1-1."""

import argparse
import json

import run_sparse_sprite_scan_native_1123 as Trial


Current, Previous, Timing = Trial.Current, Trial.Previous, Trial.Timing


def controller(reference, row, digest):
    script = Current.controller(reference, row)

    def replace(old, new):
        nonlocal script
        assert script.count(old) == 1, old
        script = script.replace(old, new, 1)

    replace(Timing.PIN, digest)
    replace('local started,done,menuDone=false,false,false',
            'local started,done,menuDone=false,false,false\nlocal goombaMin=512;local drawReturns=0')
    replace('local function empty()', '''local function visibleGoomba()
 local camera=r(0x71f)+256*r(0x71d)
 for i=0,5 do
  if r(0x10+i)==1 and r(0x17+i)==6 then
   local world=r(0x76+i)+256*r(0x5d+i)
   if world>=camera and world<camera+256 then return world end
  end
 end
end
local function empty()''')
    replace(" for i=0,5 do assert(r(0x10+i)==0,'Enemy entered empty profile')end\n", '')
    replace('and active()and ticks<64', 'and active()and ticks<48')
    replace("if observe and settled>=4 and not started then\n  started=true;beginFrame=frame;beginSkipped=r(0x13a);phases[1]={name='idle48',before=state()}\n end",
            '''local goomba=visibleGoomba()
 if observe and settled>=4 and not started and goomba and goomba-x()>=88 then
  started=true;beginFrame=frame;beginSkipped=r(0x13a);phases[1]={name='first Goomba visible',before=state(),goomba=goomba}
  pad=0
 end''')
    replace('if settled<4 then settled=settled+1;return end',
            '''if settled<4 then settled=settled+1;return end
  if not started then return end
  local goomba=visibleGoomba()
  assert(goomba and goomba-x()>=24,'The authored Goomba stays visible and out of contact')
  goombaMin=math.min(goombaMin,goomba-x())''')
    replace("if ticks==48 then phases[1].after=state();phases[2]={name='Right16',before=state()};pad=1 end",
            'if ticks==48 then phases[1].after=state();phases[1].closestGoomba=goombaMin end')
    replace('  if ticks==64 then phases[2].after=state();pad=0 end\n', '')
    replace("scope='64 actual Main completions in an inclusive physical-frame interval, four settled updates, naturally zero enemies, idle48 then Right16. Literal4016/4017 reads and inclusive Main cycles (interrupts/DMA included). Boundary frames can be partial. No cadence acceptance assumed.'",
            "scope='48 completed game updates after the first natural Goomba is visible. The player waits outside contact. Controller-only Easy 1-1. Boundary video frames can be partial.'")
    replace('phases=phases,terminal=state(),', 'phases=phases,terminal=state(),draw_returns=drawReturns,')
    replace("if ticks>=64 then assert(ticks==64 and phases[2].after.x>phases[2].before.x,'Right moves through the empty opening');finish(true,'Natural roster empty64-Main profile');return end",
            "if ticks>=48 then assert(ticks==48 and drawReturns>0,'The ordinary sprite renderer ran');finish(true,'Natural first Goomba cadence');return end")
    replace('press(16);menuDone=true', 'press(16);menuDone=true;pad=1')
    replace("frame=frame+1;assert(frame<=2000,'Physical bound')", "frame=frame+1;assert(frame<=3200,'Physical bound')")
    script += '''
emu.addMemoryCallback(guarded(function()
 local p=emu.convertAddress(0xa1c6)
 if live and live.observe and started and p and p.memType==emu.memType.nesPrgRom and p.address==4*8192+0x1c6 then
  drawReturns=drawReturns+1
 end
end),emu.callbackType.exec,0xa1c6)
'''
    Previous.LuaRuntime().compile(script)
    return script


def run(names, compose=Trial.Sparse.compose):
    downloads = Previous.check(Timing.ROM)
    parent = Timing.ROM.read_bytes()
    candidate = compose(parent)
    reference = Current.reference(parent)
    roster = Previous.roster(parent)
    work = Timing.SHARED
    rom, controls = work / 'candidate.nes', work / 'controller.lua'
    assert set(work.iterdir()) == {rom, controls} and rom.read_bytes() == parent
    Previous.require_free_workspace(Timing.R, Timing.ROM, allow_interactive=True)
    original = controls.read_bytes()
    try:
        for label, image, path in (('installed', parent, Timing.ROM), ('trial', candidate, rom)):
            digest = Timing.H(image)
            if path == rom:
                rom.write_bytes(candidate)
            assert Previous.check(path)['ROM_sha256'] == digest
            for name in names:
                controls.write_bytes(controller(reference, roster[name], digest).encode())
                proof = Previous.run(controls, path, work / 'capture', digest, 80)
                assert proof['outputs_written'] == 0 and not proof['images']
                data = proof['receipt']
                fields = ('passed', 'reason', 'character', 'phases', 'terminal', 'draw_returns',
                          'measured_Main', 'inclusive_video_frames', 'Main_return_histogram',
                          'native_lag_NMI', 'inclusive_Main_costs', 'no_controller_read_frames')
                summary = {key: data[key] for key in fields if key in data}
                summary.update(version=label, ROM=digest, receipt_SHA256=proof['receipt_SHA256'])
                print('OCCUPIED SPRITES ' + json.dumps(summary, separators=(',', ':')), flush=True)
                assert proof['passed'], (label, name, data['reason'])
    finally:
        rom.write_bytes(parent)
        controls.write_bytes(original)
        assert set(work.iterdir()) == {rom, controls} and rom.read_bytes() == Timing.ROM.read_bytes() == parent
        assert Previous.check(Timing.ROM) == downloads


if __name__ == '__main__':
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument('characters', nargs='+', choices=Trial.TARGETS)
    run(args.parse_args().characters)
