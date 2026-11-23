"""Qualify the compact Prince lift transport and the ordinary Up pickup route."""

import argparse
import inspect
import json
from unittest.mock import patch

from py65.devices.mpu6502 import MPU

import check_prince_oneup_lift_cold_1123 as Cold
import compose_prince_lift_reach_1123 as Reach
import replay_prince_oneup_lift_1123 as R
import replay_prince_oneup_up_1123 as Up
import run_prince_oneup_lift_native_1123 as Native


H = Reach.C.H
CORE_CHANGES = R.CHANGES + ((Reach.Projection.CODE - 0xA000, 32),
                            (Reach.GROUND_CHECK - 0xA000, len(Reach.NEW_GROUND)))


def verify_head_gate():
    entry, foot = Reach.NATIVE_HEAD, 0x9C01
    old, new = Reach.OLD_HEAD, Reach.native_gate()
    old_cpu, new_cpu = (MPU(memory=bytearray(65536)), MPU(memory=bytearray(65536)))
    for cpu, code in ((old_cpu, old), (new_cpu, new)):
        cpu.memory[entry:foot] = code

    def enters(cpu, effect, speed, nibble):
        cpu.pc, cpu.a, cpu.x, cpu.p = entry, 0x60, 0, 0x30
        cpu.memory[0x8E], cpu.memory[7] = speed, nibble
        for _ in range(6):
            if cpu.pc in (effect, foot):
                break
            cpu.step()
        assert cpu.pc in (effect, foot) and cpu.a == 0x60 and cpu.x == 0
        if cpu.pc == effect and nibble < 16:
            assert cpu.y == nibble and cpu.p & 1
        return cpu.pc == effect

    for speed in range(256):
        for nibble in range(16):
            old_pass = enters(old_cpu, entry + 10, speed, nibble)
            assert old_pass == enters(new_cpu, entry + 12, speed, nibble)
        for tag in range(0x82, 0x88):
            assert enters(new_cpu, entry + 12, speed, tag)
    return dict(ordinary_speed_and_probe_pairs=4096, tagged_lift_entries=1536)


def controller(parent, image, overlay, *, stage=False):
    assert Reach.C.inverse(image, overlay) == parent
    prior, _ = R.original(parent)
    before = R.P.Packet.extract(prior)[1]
    decoded, _, cookie, _ = Reach.C.extract(image)
    assert decoded == overlay['decoded'] and cookie.hex() == overlay['cookie']
    assert before[1] == decoded[1]
    at = Reach.PICKUP_STAGE - 0xC100
    state = before[2]
    assert state[at:at + len(Reach.OLD_PICKUP)] == Reach.OLD_PICKUP
    assert decoded[2] == state[:at] + Reach.NEW_PICKUP + state[at + len(Reach.OLD_PICKUP):]
    owned = {offset for start, width in CORE_CHANGES for offset in range(start, start + width)}
    assert all(i in owned for i, (a, b) in enumerate(zip(before[0], decoded[0], strict=True)) if a != b)
    assert 0 < len(decoded[3]) <= 1024

    def authenticate(rom, spec):
        assert rom == image and spec == overlay
        return parent, decoded, dict(lift=overlay['lift'])

    # The older observer pins the old collector signature. Generate the same
    # observer with the exact new entry bytes as both its check and Lua hook.
    once = R.P.G.First.once
    pinned = once(inspect.getsource(R.controller), Reach.OLD_PICKUP[:12].hex(),
                  Reach.NEW_PICKUP[:12].hex())
    scope = dict(R.controller.__globals__, authenticate=authenticate, CHANGES=CORE_CHANGES)
    exec(compile(pinned, __file__ + ':collector-rebind', 'exec'), scope)
    with patch.object(R, 'authenticate', authenticate), patch.object(R, 'controller', scope['controller']):
        text = Up.controller(image, overlay)
    extent = next(row for row in text.splitlines() if row.startswith('local candidateStaticExtents='))
    old_entry = R.P.Base.lua(list(Reach.OLD_PICKUP))[1:-1]
    new_entry = R.P.Base.lua(list(Reach.NEW_PICKUP))[1:-1]
    text = once(text, extent, once(extent, old_entry, new_entry))
    if stage:
        return Native.stage_controller(R, image, overlay, text)
    text = once(text, '''  pad=0
  if idle(s)and s.action==0 then
   if s.x<1015 then pad=s.facing==255 and 64 or 1
   elseif s.x>1030 then pad=s.facing==0 and 64 or 2 end
  end''', '''  pad=0
  if idle(s)and s.action==0 then
   if s.facing==255 then pad=s.x<1038 and 64 or 2
   elseif s.x<1025 then pad=1
   elseif s.x>1031 then pad=64 end
  end''')
    text = once(text, 'and s.x>=1015 and s.x<=1030 and a.y>=164',
                'and s.facing==0 and s.x>=1025 and s.x<=1031 and a.y>=164')
    text = once(text, '''   target=math.min(right,math.max(left,s.x))
   pad=s.x<left and 1 or s.x>right and 2 or 0''', '''   target=1040
   pad=floor(s) and s.x<target and 1 or 0
   if a and s.foot<176 and s.x<1019 and idle(s) and s.action==0 then
    target=1019
    pad=s.facing==0 and 1 or 64
   end''')
    text = once(text, '''   target=item.x-4
   if high then target=math.max(left,math.min(right,target))
   else target=math.max(left,math.min(1076,target))end
   pad=s.x<target-4 and 1 or s.x>target+4 and 2 or 0''', '''   if high then
    target=math.max(left,math.min(right,item.x-4))
    pad=s.x<target-4 and 1 or s.x>target+4 and 2 or 0
   else
    -- Wait on the bank below the falling item. Brake before the pit.
    target=1040
    pad=floor(s) and s.x<target and 1 or 0
   end''')
    text = once(text, '   p.samples[#p.samples+1]={state=s,actor=item,lift=a,high=high,target=target,pad=pad,', '''
   local enemies={}
   for i=0,5 do
    local enemy=stockActor(i)
    if enemy.flag==1 and enemy.id<=6 and enemy.state&32==0 then
     enemies[#enemies+1]={enemy.x,enemy.y,enemy.id}
    end
   end
   p.samples[#p.samples+1]={state=s,actor=item,lift=a,high=high,target=target,pad=pad,enemies=enemies,''')
    text = once(text, ' if stock.born and a.state>=128 then stock.mature=', '''
 if a.flag==1 and a.id==46 and a.state<128 then
  local observed=stockState()
  stockReturn(cpu,function()
   local after=stockActor(i)
   assert(after.flag==1 and after.id==46 and stockState().lives==observed.lives,
    'An emerging pickup must stay on screen without credit')
   stock.immature_contacts=(stock.immature_contacts or 0)+1
  end)
  return
 end
 if stock.born and a.state>=128 then stock.mature=''')
    text = once(text, "assert(ox>0 and oy>0,'Actual positive native body/item overlap')",
                "assert(ox>=0 and oy>=0,'Actual inclusive native body/item contact')")
    text = once(text, "assert(stock.lift.head.speed>=128 and stock.lift.admission,"
                "'Actual rising native hidden hit from original Up reach')", '''
 local flag=read(7)
 stock.lift.head.ascent_tag=flag
 stock.lift.head.source_action=stock.lift.head.state.action
 local a=liftActor()
 assert(flag>=128 and stock.lift.admission and a and a.carry==a.slot
  and read(LIFT.ram.Enemy_Y_Speed+a.slot)>=128 and stock.lift.head.source_action==28,
  'Only a native ascending lift and the original Up reach can authorize the hidden hit')''')
    R.P.Base.LuaRuntime().compile(text)
    return text


def native(parent, image, text, *, stage=False):
    timing = Native.Timing
    downloads = Native.check(timing.ROM)
    assert H(parent) == downloads['ROM_sha256'] == Reach.C.PARENT
    assert not downloads['matching_patch_files']
    work = timing.SHARED
    rom, controls = work / 'candidate.nes', work / 'controller.lua'
    assert set(work.iterdir()) == {rom, controls} and rom.read_bytes() == parent
    Native.require_free_workspace(timing.R, timing.ROM, allow_interactive=True)
    script = controls.read_bytes()
    try:
        rom.write_bytes(image)
        controls.write_bytes(text.encode())
        guard = Native.check(rom)
        assert guard['ROM_sha256'] == H(image) and not guard['matching_patch_files']
        out = Native.run(controls, rom, work / 'capture', H(image), 360 if stage else 240,
                         variant=3, long_no_capture=True)
        assert out['outputs_written'] == 0 and not out['images']
        return out
    finally:
        rom.write_bytes(parent)
        controls.write_bytes(script)
        assert rom.read_bytes() == timing.ROM.read_bytes() == parent
        assert Native.check(timing.ROM) == downloads and set(work.iterdir()) == {rom, controls}


def deliver(parent, image, text, expected_receipt):
    timing = Native.Timing
    nightly = timing.ROM
    downloads = Native.check(nightly)
    assert H(parent) == downloads['ROM_sha256'] == Reach.C.PARENT
    assert not downloads['matching_patch_files']
    work = timing.SHARED
    rom, controls = work / 'candidate.nes', work / 'controller.lua'
    assert set(work.iterdir()) == {rom, controls} and rom.read_bytes() == parent
    Native.require_free_workspace(timing.R, nightly, allow_interactive=True)
    previous_script = controls.read_bytes()
    delivered = False
    try:
        controls.write_bytes(text.encode())
        nightly.write_bytes(image)
        guard = Native.check(nightly)
        assert guard['ROM_sha256'] == H(image) and not guard['matching_patch_files']
        proof = Native.run(controls, nightly, work / 'capture', H(image), 240,
                           variant=3, long_no_capture=True)
        assert proof['passed'] and proof['receipt_SHA256'] == expected_receipt, proof['receipt']
        assert proof['outputs_written'] == 0 and not proof['images']
        assert nightly.read_bytes() == image and Native.check(nightly) == guard
        rom.write_bytes(image)
        delivered = True
        return dict(path=str(nightly), ROM_SHA256=H(image), receipt_SHA256=proof['receipt_SHA256'],
                    script_SHA256=proof['script_SHA256'])
    finally:
        if not delivered:
            nightly.write_bytes(parent)
            rom.write_bytes(parent)
            assert Native.check(nightly) == downloads
        controls.write_bytes(previous_script)
        assert set(work.iterdir()) == {rom, controls}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('test', choices=('cold', 'pickup', 'stage', 'stage-and-deliver'))
    parser.add_argument('--verified-pickup', help='Passing same-image native pickup receipt SHA-256')
    args = parser.parse_args()
    if (args.test == 'stage-and-deliver') != bool(args.verified_pickup):
        parser.error('stage-and-deliver requires exactly one verified pickup receipt')
    parent = Native.Timing.ROM.read_bytes()
    image, overlay = Reach.compose(parent)
    if args.test == 'cold':
        result = Cold.verify(parent, image, overlay)
        assert Reach.recover_parent(image) == parent
        result['head_gate'] = verify_head_gate()
        passed = True
    else:
        stage = args.test in ('stage', 'stage-and-deliver')
        proof = native(parent, image, controller(parent, image, overlay, stage=stage), stage=stage)
        result = {key: proof[key] for key in ('receipt_SHA256', 'script_SHA256', 'outputs_written')}
        receipt = proof['receipt']
        passed = proof['passed']
        for name in ('reason', 'phase', 'terminal', 'Main_returns', 'persistent_sword',
                     'grounded_1_2_completed_returns', 'lift_birth'):
            if name in receipt:
                result[name] = receipt[name]
        stock = receipt.get('natural_stock', {})
        lift = stock.get('lift', {})
        for name in ('birth', 'admission', 'head', 'contacts', 'moving_contacts', 'reached_apex'):
            if name in lift:
                result['lift_' + name] = lift[name]
        for name in ('born', 'mature', 'collector', 'erase', 'popup', 'credit', 'finished', 'immature_contacts'):
            if name in stock:
                result['stock_' + name] = stock[name]
        if not passed:
            queries = stock.get('head_queries', [])
            if 'head' not in lift:
                result['head_queries'] = queries[-3:] if isinstance(queries, list) else queries
            pursuit = stock.get('item_pursuit', {})
            result['pursuit'] = [
                dict(x=s['state']['x'], y=s['state']['y'], action=s['state']['action'],
                     hp=s['state']['hp'], item=[s['actor']['x'], s['actor']['y'], s['actor']['state']],
                     input=s['pad'], aim=s['target'], enemies=s['enemies'])
                for s in pursuit.get('samples', [])]
    print('PRINCE REACH ' + json.dumps(dict(test=args.test, candidate=H(image),
          passed=passed, result=result), separators=(',', ':')), flush=True)
    if passed and args.test == 'stage-and-deliver':
        verified = deliver(parent, image, controller(parent, image, overlay), args.verified_pickup)
        print('PRINCE NIGHTLY ' + json.dumps(verified, separators=(',', ':')), flush=True)
    return int(not passed)


if __name__ == '__main__':
    raise SystemExit(main())
