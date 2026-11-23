"""Measure or replay the exact Prince epoch candidate with ordinary Mesen input."""

import argparse
import json

import compose_prince_epoch_current_1123 as E
import run_prince_lift_reach_1123 as Route
import run_roster_empty_cadence_current_1123 as Cadence


Native, Reach = Route.Native, E.Reach
Timing = Native.Timing
CADENCE_ROWS = {'cadence': 'PRINCE PERSIA', 'mini': 'MINI MARIO', 'dk': 'DONKEY KONG JR',
                'sonic': 'SONIC', 'super': 'SUPER SONIC'}


def controllers(parent, candidate, tests):
    anchor = Reach.recover_parent(parent)
    assert E.H(parent) == E.PARENT and Reach.C.extract(parent) == Reach.C.extract(candidate)
    for pc in (0x82D9, 0x82BE, 0x82D0):
        at = 16 + 126 * 8192 + (pc & 8191)
        assert candidate[at:at + 16] == parent[at:at + 16] == anchor[at:at + 16]
    programs = {}
    if any(name in CADENCE_ROWS for name in tests):
        roster = Cadence.Previous.roster(parent)
        reference = Cadence.reference(anchor)
        for name in tests:
            if name in CADENCE_ROWS:
                source = Cadence.controller(reference, roster[CADENCE_ROWS[name]])
                assert source.count(Timing.PIN) == 1
                programs[name] = source.replace(Timing.PIN, E.H(candidate), 1)
    if any(name in tests for name in ('pickup', 'stage')):
        known, overlay = Reach.compose(anchor)
        assert known == parent
        for name in tests:
            if name in ('pickup', 'stage'):
                old = Route.controller(anchor, parent, overlay, stage=name == 'stage')
                assert E.PARENT in old
                text = old.replace(E.PARENT, E.H(candidate))
                if name == 'stage':
                    text = Route.R.P.G.First.once(text,
                        "    if age>=12 and support(s) and s.action~=4 and s.action~=3 then", '''    local finalFloor=x>=3040 and floor(s) and (solid(x+2,208) or solid(x+13,208))
    if age>=12 and (support(s) or finalFloor) and s.action~=4 and s.action~=3 then''')
                    text = Route.R.P.G.First.once(text, "local function tick()\n", '''local function authoredFlower()
  for slot=0,5 do
    local x=read(0x76+slot)+256*read(0x5d+slot)
    if x==1248 and read(0x10+slot)~=0 and read(0x17+slot)==0x2e and read(0x34+slot)==1 then
      return slot
    end
  end
end

local flowerRetried=false
local function tick()
''')
                    text = Route.R.P.G.First.once(text,
                        "    if read(0x15)~=0 and read(0x1c)==0x2e and read(0x39)==1 then flowerSeen=true end", '''    local slot=authoredFlower()
    if slot then flowerSeen=true end''')
                    text = Route.R.P.G.First.once(text,
                        "        if read(0x24)&128==0 then pad=0;return end\n      assert(flowerSeen and read(0x39)==1,'Mature native flower in slot5')", '''        if not slot or read(0x1f+slot)&128==0 then pad=0;return end
      late.flower.slot=slot''')
                    text = Route.R.P.G.First.once(text,
                        "        assert(late.flower.spawned and read(0x15)==0,'Authored flower erased before sword inventory')",
                        "        assert(late.flower.spawned and read(0x10+late.flower.slot)==0,'Authored flower erased before sword inventory')")
                    text = Route.R.P.G.First.once(text,
                        "      switch('flower-retreat',0);return\n      end\n    end", '''      if s.y<=114 then
        late.flower.boarded=s
        switch('flower-walk',s.x>1252 and 2 or 1)
      else
        switch('flower-retreat',0)
      end
      return
      end
    end''')
                    text = Route.R.P.G.First.once(text,
                        "    assert(s.lives==2 and s.hp>0,'Alive reaching flower')", '''
    local recent=late.flower_recent or {}
    late.flower_recent=recent
    if #recent==16 then table.remove(recent,1)end
    local actors={}
    for j=0,5 do
      local flag=read(0x10+j)
      if flag~=0 then
        actors[#actors+1]={slot=j,id=read(0x17+j),kind=read(0x34+j),flag=flag,state=read(0x1f+j),
          x=read(0x76+j)+256*read(0x5d+j),y=read(0xbe+j)}
      end
    end
    recent[#recent+1]={phase=progress,age=age,x=s.x,y=s.y,hp=s.hp,action=s.action,
      pad=pad,actors=actors}
    assert(s.lives==2 and s.hp>0,'Alive reaching flower')''')
                    text = Route.R.P.G.First.once(text,
                        "    elseif progress=='flower-up' then\n      if age>=80 then pad=0 end", '''    elseif progress=='flower-aim-left' then
      if s.facing==0 then pad=0 end
      if age>4 and s.facing==0 and idle(s) and floor(s)then switch('flower-aim-step',66)end
    elseif progress=='flower-aim-step' and s.action~=0 and s.action~=1 and s.action~=10 then
      switch('flower-aim-settle',0)
    elseif progress=='flower-aim-settle' and idle(s) and floor(s)then
      switch('flower-aim-right',1)
    elseif progress=='flower-aim-right' then
      if s.facing==255 then pad=0 end
      if age>4 and s.facing==255 and idle(s) and floor(s)then switch('flower-up',8)end
    elseif progress=='flower-up' then
      if age>=80 then pad=0 end
      if age>=110 and not flowerSeen then
        if flowerRetried then finish(false,'Two ordinary Up attempts missed the Fire Flower');return end
        if idle(s) and floor(s) then
          flowerRetried=true
          switch('flower-aim-left',2)
          return
        end
      end''')
                    text += '''
emu.addMemoryCallback(guarded(function()
 if progress~='flower-up' then return end
 local cpu=emu.getState()
 local s=state()
 local tile=cpu['cpu.a']
 local head=late.flower_head or {}
 local nil_tile=late.flower_empty_head or {}
 late.flower_head=head
 late.flower_empty_head=nil_tile
 local rows=tile~=0 and head or nil_tile
 if #rows>=24 or (tile==0 and s.y>=165) then return end
 rows[#rows+1]={x=s.x,y=s.y,pose=s.pose,action=s.action,tile=tile,y_speed=read(0x8e),
   row=read(5),nibble=read(7),column=read(9)+256*read(10)}
end),emu.callbackType.exec,0x9bc5)
'''
                Route.R.P.Base.LuaRuntime().compile(text)
                programs[name] = text
    return {name: programs[name] for name in tests}


def run(parent, candidate, programs, *, install=False):
    downloads = Native.check(Timing.ROM)
    assert downloads['ROM_sha256'] == E.H(parent) == E.PARENT
    assert not downloads['matching_patch_files']
    work = Timing.SHARED
    rom, controls = work / 'candidate.nes', work / 'controller.lua'
    assert set(work.iterdir()) == {rom, controls} and rom.read_bytes() == parent
    Native.require_free_workspace(Timing.R, Timing.ROM, allow_interactive=True)
    source = controls.read_bytes()
    finished = False
    wrote_nightly = False
    results = {}

    def check_trial(path, name):
        guard = Native.check(path)
        assert guard['ROM_sha256'] == E.H(candidate) and not guard['matching_patch_files']
        controls.write_bytes(programs[name].encode())
        proof = Native.run(controls, path, work / 'capture', E.H(candidate),
                           {'pickup': 220, 'stage': 320}.get(name, 90),
                           variant=3, long_no_capture=True)
        assert proof['outputs_written'] == 0 and not proof['images']
        r = proof['receipt']
        report = {k: r[k] for k in ('passed', 'reason', 'phase', 'terminal', 'inclusive_video_frames',
                    'measured_Main', 'native_lag_NMI', 'Main_return_histogram',
                    'grounded_1_2_completed_returns', 'persistent_sword') if k in r}
        if name == 'stage':
            trace = r.get('later_route', {})
            for key in ('flower_head', 'flower_empty_head'):
                report[key] = trace.get(key, [])
            if not r['passed']:
                report['last_flower_sample'] = (trace.get('flower_recent') or [None])[-1]
            report['flower_transitions'] = [(event['phase'], event['state']['x'], event['state']['commit'])
                for event in r.get('events', []) if event['phase'].startswith('flower-')]
        report.update(test=name, ROM=E.H(candidate), receipt_SHA256=proof['receipt_SHA256'],
                      script_SHA256=proof['script_SHA256'], launched_from_downloads=path == Timing.ROM)
        assert Native.check(path) == guard
        print('PRINCE EPOCH MESEN ' + json.dumps(report, separators=(',', ':')), flush=True)
        assert proof['passed'], (name, r['reason'], report['receipt_SHA256'])
        return proof['receipt_SHA256'], report

    try:
        rom.write_bytes(candidate)
        for name in programs:
            results[name] = check_trial(rom, name)
        if install:
            assert set(programs) == {'cadence', 'pickup', 'stage'}
            assert results['cadence'][1]['inclusive_video_frames'] < 168
            assert Native.check(Timing.ROM) == downloads
            wrote_nightly = True
            Timing.ROM.write_bytes(candidate)
            receipt, report = check_trial(Timing.ROM, 'cadence')
            assert receipt == results['cadence'][0] and report['inclusive_video_frames'] < 168
            assert Timing.ROM.read_bytes() == candidate
            assert not Native.check(Timing.ROM)['matching_patch_files']
            finished = True
    finally:
        if not finished:
            rom.write_bytes(parent)
            if wrote_nightly:
                Timing.ROM.write_bytes(parent)
            assert Native.check(Timing.ROM) == downloads
        controls.write_bytes(source)
        assert set(work.iterdir()) == {rom, controls}
        assert rom.read_bytes() == Timing.ROM.read_bytes() == (candidate if finished else parent)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('tests', nargs='+', choices=tuple(CADENCE_ROWS) + ('pickup', 'stage'))
    p.add_argument('--install', action='store_true')
    p.add_argument('--side', action='store_true')
    p.add_argument('--baseline', action='store_true')
    args = p.parse_args()
    parent = Timing.ROM.read_bytes()
    if args.baseline:
        assert not args.side and not args.install
        image = parent
    elif args.side:
        import compose_prince_side_current_1123 as Side
        image, _ = Side.compose(parent)
        assert Side.inverse(image) == parent
    else:
        image, _ = E.compose(parent)
        assert E.inverse(image) == parent
    run(parent, image, controllers(parent, image, args.tests), install=args.install)


if __name__ == '__main__':
    main()
