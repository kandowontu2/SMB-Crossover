"""Explicit current-ROM binding and bounded Star chase observations; no state writes."""
from hashlib import sha256
import argparse
import json

import compose_prince_entrance_current_1113 as Current
import replay_steve_all_pickups_guarded_1113 as Guarded
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT = Current.Entry.R/'build/metal-flower-native-1112'
OLD = '1d585c40b2155b529d959212c09fb5229935af383707b76ec57e30c04591fbd7'


def controller(raw, *, combat_chase=False):
    assert sha256(raw).hexdigest() == Current.PIN
    parent526 = Current.reverse(raw)
    parent62 = Current.Karnov.inverse_current(parent526)
    assert sha256(parent62).hexdigest() == Guarded.S.PIN
    text = Guarded.controller(parent62, clear_path=True)
    assert sha256(text.encode()).hexdigest() == OLD
    assert text.count(Guarded.S.PIN) == 1
    text = text.replace(Guarded.S.PIN, Current.PIN)
    if combat_chase:
        before = '''  local gap=actor.x-x()-8
  local direction=gap>4 and 1 or gap< -4 and 2 or 0
  if not natural.starJumpStart and read(0xbd)==176 and read(0x1e)==0 and read(0x5c92)==0 then
    natural.starJumpStart=projections
  end
  local jump=natural.starJumpStart and projections-natural.starJumpStart<9 and 128 or 0
  return direction|jump'''
        after = '''  local nearest,delta=nil,73
  for slot=0,5 do
    local flag,id=read(pickupFields.Enemy_Flag+slot),read(pickupFields.Enemy_ID+slot)
    local dx=read(pickupFields.Enemy_X_Position+slot)+256*read(pickupFields.Enemy_PageLoc+slot)-x()
    if flag>0 and flag<128 and id<12 and read(pickupFields.Enemy_State+slot)&32==0
      and read(guardFields.Enemy_Y_HighPos+slot)==1 and math.abs(dx)<math.abs(delta)
      and math.abs(read(pickupFields.Enemy_Y_Position+slot)-read(0xbd))<=24 then
      nearest,delta=slot,dx
    end
  end
  local gap=actor.x-x()-8
  local direction=gap>4 and 1 or gap< -4 and 2 or 0
  local jump=0
  if nearest~=nil then
    natural.defenseUpdates=natural.defenseUpdates+1
    local face=delta>=0 and 1 or 2
    direction=math.abs(delta)>32 and face or (projections%12==0 and face or 0)
    jump=projections%12<6 and 64 or 0
  end
  return direction|jump'''
        assert text.count(before)==1
        text=text.replace(before,after)
        text=text.replace("assert(age<180,'Native moving-item chase bound')",
                          "assert(age<600,'Native moving-item chase bound')")
    b = dict(Guarded.S.W.Symbols.bundle(), raw=raw)
    fields = {name:Guarded.S.W.address(b, name) for name in
        ('JnAttack', 'JnPressed', 'SavedJoypadBits')}
    pre = 'local starTrace={}\nlocal starFields={'+','.join(
        f'{name}={value}' for name,value in fields.items())+'}\n'
    text = pre+text
    before = '"path_combat":[%s]}'
    assert text.count(before) == 1
    text = text.replace(before, '"path_combat":[%s],"star_trace":[%s]}')
    before = 'natural.actorReport or "null",table.concat(natural.pathCombat,",")))'
    assert text.count(before) == 1
    text = text.replace(before,
        'natural.actorReport or "null",table.concat(natural.pathCombat,","),table.concat(starTrace,",")))')
    before = '  return direction|jump'
    assert text.count(before) == 1
    text = text.replace(before, r'''
  if #starTrace<96 then
    starTrace[#starTrace+1]=string.format(
      '{"projection":%d,"phase":"%s","x":%d,"y":%d,"native_state":%d,"source_move":%d,"attack":%d,"pressed":%d,"held":%d,"jump_start":%d,"pad":%d,"star_x":%d,"star_y":%d,"health":%d}',
      projections,phase,x(),read(0xbd),read(0x1e),read(0x5c92),
      read(starFields.JnAttack),read(starFields.JnPressed),read(starFields.SavedJoypadBits),
      natural.starJumpStart or -1,direction|jump,actor.x,actor.y,read(0x5f30))
  end
  return direction|jump''')
    assert not any(word in text for word in ('emu.write', 'emu.setState', 'io.open', 'takeScreenshot'))
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    LuaRuntime().compile(text)
    return text


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--metadata', action='store_true')
    p.add_argument('--combat-chase', action='store_true')
    args = p.parse_args()
    rom = Current.Karnov.Owner.NIGHTLY
    raw = rom.read_bytes()
    assert check(rom)['ROM_sha256'] == Current.PIN
    text = controller(raw, combat_chase=args.combat_chase)
    if args.metadata:
        print(json.dumps(dict(script_SHA256=sha256(text.encode()).hexdigest(),
            ROM_SHA256=Current.PIN, input_decisions_unchanged=not args.combat_chase,
            native_run=False, output_files=0)), flush=True)
    else:
        script = OUT/'controller.lua'
        script.write_text(text, encoding='utf-8', newline='\n')
        result = run(script, rom, OUT/'capture', Current.PIN, 180)
        receipt=result['receipt']
        compact={key:value for key,value in receipt.items() if key!='star_trace'}
        trace=receipt.get('star_trace',[])
        compact['star_trace_changes']=[row for index,row in enumerate(trace)
            if index==0 or index==len(trace)-1 or any(row[key]!=trace[index-1][key]
                for key in ('source_move','attack','health','jump_start'))]
        print(json.dumps(dict(passed=result['passed'], ROM_SHA256=Current.PIN,
            script_SHA256=result['script_SHA256'], receipt_SHA256=result['receipt_SHA256'],
            receipt=compact, outputs_written=result['outputs_written']),
            separators=(',', ':')), flush=True)
        assert check(rom)['ROM_sha256'] == Current.PIN
        if args.combat_chase:
            assert result['passed'], 'Ordinary combat chase must earn all four stock items'
