"""Play the Prince's real 1-1 lift route in the shared Mesen test slot."""

import argparse
import json

import compose_prince_oneup_lift_1123 as Compose
import run_sonic_current_empty_cadence_1122 as Timing
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run


def stage_controller(route, image, overlay, pickup):
    template = route.P.FIXTURE.read_bytes()
    assert Compose.H(template) == route.P.FIXTURE_SHA
    text = template.decode()
    once = route.P.G.First.once
    text = once(text, route.P.Base.PIN, Compose.H(image))
    text = once(text, "local cookie = 'a7260209e6eb04c8dbe70c3197b0cb4b'",
                "local cookie = '" + overlay['cookie'] + "'")
    for name in ('verifiedHooks', 'candidateStaticExtents'):
        prefix = f'local {name}='
        before = next(line for line in text.splitlines() if line.startswith(prefix))
        after = next(line for line in pickup.splitlines() if line.startswith(prefix))
        text = once(text, before, after)

    text = once(text, 'local newPacketVerified=nil', 'local newPacketVerified=nil\nlocal liftBirth')
    text = once(text, 'added_helpers=false,', 'added_helpers=liftBirth~=nil,lift_birth=liftBirth,')
    text = once(text, "assert(newPacketVerified,'Actual tier2 packet consumer readback required');",
                "assert(verifiedGrounded>=25 and not verifiedPendingMain,'Grounded 1-2 endpoint');"
                "assert(newPacketVerified and liftBirth,'Actual stream readback and lift admission');")
    bundle = dict(route.W.Symbols.bundle(), raw=image)
    pc = route.W.address(bundle, 'CheckpointEnemyID')
    offset = route.W.location(bundle, 'CheckpointEnemyID') - 16
    text += f'''
emu.addMemoryCallback(guarded(function()
 local mapped=emu.convertAddress({pc})
 if not mapped or mapped.memType~=emu.memType.nesPrgRom or mapped.address~={offset} then return end
 local i=emu.getState()['cpu.x']
 if i>=6 or read(0x17+i)~=37 or read(0x76+i)+256*read(0x5d+i)~=1008 then return end
 local s=state()
 assert(not liftBirth and s.world==0 and s.level==0 and s.engine==8,'Single stage lift')
 assert(read(0xbe+i)==192 and 1008-s.scroll>=256 and 1008-s.scroll<=287,'Lift admitted offscreen')
 liftBirth={{x=1008,y=192,slot=i,camera=s.scroll,frame=s.frame}}
end),emu.callbackType.exec,{pc})
'''
    route.P.Base.LuaRuntime().compile(text)
    return text


def collision_controller(route, image, overlay, text):
    bundle = dict(route.W.Symbols.bundle(), raw=image)
    names = ('LargePlatformCollision', 'CheckPlayerVertical', 'PlayerCollisionCore',
             'ProcLPlatCollisions', 'ChkForTopCollision', 'SetCollisionFlag',
             'PlatformSideCollisions', 'ExLPC', 'PositionPlayerOnVPlat')
    sites = {}
    for name in names:
        at = route.W.location(bundle, name)
        sites[name] = dict(pc=route.W.address(bundle, name), address=at - 16,
                           bytes=list(image[at:at + 8]), private=False)
    source_sites = {}
    for name in ('Import', 'Material', 'Support', 'Sweep'):
        if name not in overlay['raw1_labels']:
            continue
        pc = overlay['raw1_labels'][name]
        off = pc & 8191
        source_sites[name] = dict(pc=pc, address=8192 + off,
                                  bytes=list(overlay['decoded'][3][off:off + 8]), private=True)
    fields = ('BoundingBox_UL_XPos', 'Player_Y_Speed', 'Player_OffscreenBits',
              'Enemy_OffscreenBits', 'R0')
    ram = {name: route.W.address(bundle, name) for name in fields}
    witness = "local TRACE=" + route.P.Base.lua(dict(sites=sites, sources=source_sites, ram=ram)) + r'''
local platformTrace,currentCollision={},nil
stock.lift.native_trace=platformTrace
local function traceRow(cpu)
 local s=stockState();local i=cpu['cpu.x']
 if i>=6 or s.x<1002 or s.x>1035 or #platformTrace>=48 then return end
 local a=stockActor(i)
 if a.flag~=1 or a.id~=37 or a.x~=1008 then return end
 local p=TRACE.ram.BoundingBox_UL_XPos;local e=p+4*(i+1)
 local row={s.Prince_returns,s.x,s.y,s.foot,a.y,s.ground,read(TRACE.ram.Player_Y_Speed),
  read(TRACE.ram.Player_OffscreenBits),read(TRACE.ram.Enemy_OffscreenBits+i),
  {read(p),read(p+1),read(p+2),read(p+3)},
  {read(e),read(e+1),read(e+2),read(e+3)}, {}}
 platformTrace[#platformTrace+1]=row
 return row
end
stockHook(TRACE.sites.LargePlatformCollision,function(cpu)
 currentCollision=traceRow(cpu)
end)
for _,n in ipairs({'CheckPlayerVertical','PlayerCollisionCore','ProcLPlatCollisions',
                    'ChkForTopCollision','SetCollisionFlag','PlatformSideCollisions','ExLPC'})do
 stockHook(TRACE.sites[n],function(cpu)
  local row=currentCollision;if not row then return end
  row[12][#row[12]+1]={n,cpu['cpu.a'],cpu['cpu.x'],cpu['cpu.y'],cpu['cpu.ps'],read(TRACE.ram.R0)}
  if n=='ExLPC'then currentCollision=nil end
 end)
end
stockHook(TRACE.sites.PositionPlayerOnVPlat,function(cpu)
 local row=traceRow(cpu)
 if row then row[12]={{'PositionPlayerOnVPlat',cpu['cpu.a'],cpu['cpu.x'],cpu['cpu.y']}}end
end)
local sourceTrace={}
stock.lift.source_trace=sourceTrace
for n,h in pairs(TRACE.sources)do
 stockHook(h,function(cpu)
  if stock.phase~='lift-settle' or #sourceTrace>=120 then return end
  local s=stockState();local a=liftActor()
  if not a or s.x<1008 or s.x>1048 then return end
  if s.Prince_returns-stock.lift.boarded.Prince_returns>20 then return end
  local function sample(tag,regs)
   local q=stockState()
   sourceTrace[#sourceTrace+1]={n,tag,q.Prince_returns,q.x,q.y,q.foot,
     source(0x86)+256*source(0x87),q.action,q.pose,q.mode,q.ground,a.y,a.carry,
     regs['cpu.a'],regs['cpu.ps']}
  end
  sample('entry',cpu)
  stockReturn(cpu,function(_,regs)sample('return',regs)end)
 end)
end
'''
    text = route.P.G.First.once(text, 'local function naturalStockTick()\n',
                                witness + '\nlocal function naturalStockTick()\n')
    route.P.Base.LuaRuntime().compile(text)
    return text


def controller(installed, image, overlay, mode, later=False, centered=False, face_first=False,
               reach=False):
    if mode == 'cadence':
        import run_roster_empty_cadence_current_1123 as Cadence

        row = Cadence.Previous.roster(installed)['PRINCE PERSIA']
        text = Cadence.controller(Cadence.reference(installed), row)
        assert text.count(Timing.PIN) == 1
        return text.replace(Timing.PIN, Compose.H(image), 1)

    import replay_prince_oneup_lift_1123 as Route

    text = Route.controller(image, overlay)
    if mode == 'stage':
        return stage_controller(Route, image, overlay, text)
    if later:
        once = Route.P.G.First.once
        text = once(text, 'descending120-145', 'descending128-145')
        text = once(text, 'if a.y>=120 and a.y<=145', 'if a.y>=128 and a.y<=145')
        Route.P.Base.LuaRuntime().compile(text)
    if reach:
        once = Route.P.G.First.once
        text = once(text, "stockPhase('lift-jump',128)", "stockPhase('lift-jump',8)")
        text = once(text, 'pad=l.admission and 0 or 128', 'pad=l.reached_apex and 0 or 8')
        text = once(text, 'if s.action==3 and not l.admission then l.admission={state=s,actor=a}end',
                    '''if (s.action==28 or s.pose==78) and not l.admission then
   l.admission={state=s,actor=a}
  end
  if s.pose==78 then l.reached_apex=s end''')
        text = once(text, "then l.admission=nil;stockPhase('lift-settle',0)end",
                    "then l.admission=nil;l.reached_apex=nil;stockPhase('lift-settle',0)end")
        text = once(text, 'stock.prince_returns-stock.start.Prince_returns<1100',
                    'stock.prince_returns-stock.start.Prince_returns<1600')
        Route.P.Base.LuaRuntime().compile(text)
    if centered:
        once = Route.P.G.First.once
        text = once(text, "strategy='descending120-145'", "strategy='centered cap departure'")
        text = once(text, 'math.abs(s.foot-a.y)<=1', 'math.abs(s.foot-a.y)<=4')
        text = once(text, 'pad=s.x<1015 and 1 or s.x>1019 and 2 or 0',
                    'pad=s.x<995 and 1 or 0')
        text = once(text, 'pad=s.x<1014 and 1 or s.x>1019 and 2 or 0',
                    'pad=idle(s) and (s.x<1017 and 65 or s.x>1026 and 66 or 0) or 0')
        text = once(text, 's.x>=1014 and s.x<=1019 and a.y', 's.x>=1017 and s.x<=1026 and a.y')
        if face_first:
            text = once(text, 'pad=idle(s) and (s.x<1017 and 65 or s.x>1026 and 66 or 0) or 0',
                        '''pad=0
  if idle(s)and s.action==0 then
   if s.x<1015 then pad=s.facing==255 and 64 or 1
   elseif s.x>1030 then pad=s.facing==0 and 64 or 2 end
  end''')
            text = once(text, 's.x>=1017 and s.x<=1026 and a.y', 's.x>=1015 and s.x<=1030 and a.y')
        if overlay['lift']['width'] == 48:
            text = once(text, ' local s=stockState();liftObserve(s)', ''' local s=stockState();liftObserve(s)
 if stock.phase=='lift-flight' and stock.lift.current then
  stock.lift.boarded=s;stockPhase('lift-settle',0)
 end''')
        Route.P.Base.LuaRuntime().compile(text)
    if mode == 'collision':
        return collision_controller(Route, image, overlay, text)
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--cadence', dest='mode', action='store_const', const='cadence')
    modes.add_argument('--stage', dest='mode', action='store_const', const='stage')
    modes.add_argument('--collision', dest='mode', action='store_const', const='collision')
    parser.set_defaults(mode='pickup')
    parser.add_argument('--later', action='store_true', help='Test the later cap departure window')
    parser.add_argument('--centered', action='store_true', help='Release Right during the cap jump')
    parser.add_argument('--face-first', action='store_true', help='Turn before taking a careful step')
    parser.add_argument('--reach', action='store_true', help='Use the original Up reach from the lift')
    support = parser.add_mutually_exclusive_group()
    support.add_argument('--carry-first', action='store_true', help='Test carried support before the terrain fallback')
    support.add_argument('--swept', action='store_true', help='Test the swept landing variant')
    support.add_argument('--wide-lift', action='store_true', help='Test the native 48-pixel lift')
    support.add_argument('--hold-plane', action='store_true', help='Use the carried lift plane as foot history')
    args = parser.parse_args()
    if args.later and args.mode not in ('pickup', 'collision'):
        parser.error('--later applies only to the pickup and collision routes')
    if args.centered and (args.later or args.mode not in ('pickup', 'collision')):
        parser.error('--centered uses the regular departure window on pickup and collision routes')
    if args.face_first and not args.centered:
        parser.error('--face-first requires --centered')
    if args.reach and args.mode not in ('pickup', 'collision'):
        parser.error('--reach applies only to the pickup and collision routes')
    downloads = check(Timing.ROM)
    installed = Timing.ROM.read_bytes()
    assert Compose.H(installed) == downloads['ROM_sha256'] == Compose.PARENT
    assert not downloads['matching_patch_files']
    work = Timing.SHARED
    rom, controls = work / 'candidate.nes', work / 'controller.lua'
    assert set(work.iterdir()) == {rom, controls} and rom.read_bytes() == installed
    require_free_workspace(Timing.R, Timing.ROM, allow_interactive=True)

    if args.swept or args.wide_lift or args.hold_plane:
        import probe_prince_lift_swept_plane_1123 as Sweep

        planner = (Sweep.hold_plane_plan if args.hold_plane else
                   Sweep.wide_plan if args.wide_lift else Sweep.compact_plan)
        image, overlay = Compose.compose(installed, planner)
    elif args.carry_first:
        import compose_prince_lift_carry_1123 as Carry

        image, overlay = Carry.compose(installed)
    else:
        image, overlay = Compose.compose(installed)
    pin = Compose.H(image)
    program = controller(installed, image, overlay, args.mode, args.later, args.centered,
                         args.face_first, args.reach).encode()
    prior_controller = controls.read_bytes()
    try:
        rom.write_bytes(image)
        controls.write_bytes(program)
        guard = check(rom)
        assert guard['ROM_sha256'] == pin and not guard['matching_patch_files']
        limit = {'cadence': 90, 'pickup': 240, 'stage': 360, 'collision': 240}[args.mode]
        proof = run(controls, rom, work / 'capture', pin, limit, variant=3, long_no_capture=True)
        assert proof['outputs_written'] == 0 and not proof['images']
        receipt = proof['receipt']
        if args.mode != 'cadence':
            keep = ('passed', 'reason', 'phase', 'terminal', 'physical_frames', 'Main_entries',
                    'Main_returns', 'Main_pending', 'output_files', 'added_helpers', 'natural_stock',
                    'persistent_sword', 'grounded_1_2_completed_returns', 'lift_birth')
            receipt = {key: receipt[key] for key in keep if key in receipt}
            stock = receipt.get('natural_stock', {})
            stock.pop('samples', None)
            queries = stock.pop('head_queries', [])
            stock['head_query_trace'] = [
                {key: query[key] for key in ('predicted_world_x', 'predicted_y', 'native_speed',
                                             'raw_tile', 'queried_row', 'source_actor_y') if key in query}
                | dict(pose=query['before']['pose'], action=query['before']['action'])
                for query in queries]
            lift = stock.get('lift', {})
            samples = lift.pop('samples', [])
            if samples:
                lift['first_contact_sample'], lift['last_contact_sample'] = samples[0], samples[-1]
        summary = dict(ROM=pin, receipt=receipt, receipt_SHA256=proof['receipt_SHA256'],
                       script_SHA256=proof['script_SHA256'], outputs_written=proof['outputs_written'])
        print('PRINCE LIFT MESEN ' + json.dumps(summary, separators=(',', ':')), flush=True)
        return int(not proof['passed'])
    finally:
        rom.write_bytes(installed)
        controls.write_bytes(prior_controller)
        assert rom.read_bytes() == Timing.ROM.read_bytes() == installed
        assert check(Timing.ROM) == downloads and set(work.iterdir()) == {rom, controls}


if __name__ == '__main__':
    raise SystemExit(main())
