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


def collision_controller(route, image, text):
    bundle = dict(route.W.Symbols.bundle(), raw=image)
    names = ('LargePlatformCollision', 'CheckPlayerVertical', 'PlayerCollisionCore',
             'ProcLPlatCollisions', 'ChkForTopCollision', 'SetCollisionFlag',
             'PlatformSideCollisions', 'ExLPC', 'PositionPlayerOnVPlat')
    sites = {}
    for name in names:
        at = route.W.location(bundle, name)
        sites[name] = dict(pc=route.W.address(bundle, name), address=at - 16,
                           bytes=list(image[at:at + 8]), private=False)
    fields = ('BoundingBox_UL_XPos', 'Player_Y_Speed', 'Player_OffscreenBits',
              'Enemy_OffscreenBits', 'R0')
    ram = {name: route.W.address(bundle, name) for name in fields}
    witness = "local TRACE=" + route.P.Base.lua(dict(sites=sites, ram=ram)) + r'''
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
'''
    text = route.P.G.First.once(text, 'local function naturalStockTick()\n',
                                witness + '\nlocal function naturalStockTick()\n')
    route.P.Base.LuaRuntime().compile(text)
    return text


def controller(installed, image, overlay, mode, later=False):
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
    if mode == 'collision':
        return collision_controller(Route, image, text)
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--cadence', dest='mode', action='store_const', const='cadence')
    modes.add_argument('--stage', dest='mode', action='store_const', const='stage')
    modes.add_argument('--collision', dest='mode', action='store_const', const='collision')
    parser.set_defaults(mode='pickup')
    parser.add_argument('--later', action='store_true', help='Test the later cap departure window')
    parser.add_argument('--carry-first', action='store_true', help='Test lift support before the terrain fallback')
    args = parser.parse_args()
    if args.later and args.mode not in ('pickup', 'collision'):
        parser.error('--later applies only to the pickup and collision routes')
    downloads = check(Timing.ROM)
    installed = Timing.ROM.read_bytes()
    assert Compose.H(installed) == downloads['ROM_sha256'] == Compose.PARENT
    assert not downloads['matching_patch_files']
    work = Timing.SHARED
    rom, controls = work / 'candidate.nes', work / 'controller.lua'
    assert set(work.iterdir()) == {rom, controls} and rom.read_bytes() == installed
    require_free_workspace(Timing.R, Timing.ROM, allow_interactive=True)

    if args.carry_first:
        import compose_prince_lift_carry_1123 as Carry

        image, overlay = Carry.compose(installed)
    else:
        image, overlay = Compose.compose(installed)
    pin = Compose.H(image)
    program = controller(installed, image, overlay, args.mode, later=args.later).encode()
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
            stock.pop('head_queries', None)
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
