"""Verify Getsu Fuma's natural mushroom, hidden extra life and Star in Easy 1-1."""

import argparse
import json
from unittest.mock import patch

import compose_dkjr_head_bridge_current_1123 as Nightly
import run_simon_ryu_stock_1123 as Stock


ROUTES = ('mushroom', 'life', 'star')
MOVEMENT = 0xA078
OWNER_PAGE = 991
CHR_START = 16 + 128 * 8192
ROUTE = Stock.OPENING.parent / 'getsu_fuma_host_1110.lua'


def bindings(raw, route):
    parent = Nightly.inverse(raw) if Stock.H(raw) == Nightly.CANDIDATE else raw
    assert Stock.H(parent) == Nightly.PIN
    cfg = Stock.bindings(parent, 'simon', route)
    bundle = dict(Stock.W.Symbols.bundle(), raw=raw)
    menu = Stock.W.UI.seed(bundle, 5)
    for _ in range(4):
        Stock.W.UI.key(menu, 32)
    assert Stock.W.UI.menu_name(menu)[0] == 'GETSU FUMA'
    assert Stock.N.get(menu, 'SelectedCharacter') == 5
    assert Stock.N.get(menu, 'Cv3Variant') == 4
    Stock.W.UI.key(menu, 16)
    assert Stock.N.get(menu, 'SelectedCharacter') == 42
    for name, hook in cfg['hooks'].items():
        if name == 'Movement':
            continue
        offset = 16 + hook['offset']
        expected = bytes.fromhex(hook['hex'])
        assert raw[offset:offset+len(expected)] == parent[offset:offset+len(expected)] == expected
    within = MOVEMENT & 8191
    offset = CHR_START + OWNER_PAGE * 1024 + within
    movement = raw[offset:offset+12]
    assert movement == parent[offset:offset+12] and movement.startswith(bytes.fromhex('ad0260c92a'))
    cfg['hooks']['Movement'] = dict(pc=MOVEMENT, tag=3, offset=3 * 8192 + within, hex=movement.hex())
    return dict(cfg, sha=Stock.H(raw), form='getsu', char=42, variant=4, name='GETSU FUMA')


def opening():
    source = ROUTE.read_text(encoding='utf-8')
    drive = source[source.index('local function choose()'):source.index('\nemu.addEventCallback(function() emu.setInput')]
    drive = Stock.once(drive, 'local function choose()\n local x,y=playerX()',
                       'local function travel(c)\n active=c;updates=c.update\n local x,y=playerX()')
    drive = Stock.once(drive, ' input={right=true,a=updates<jumpUntil,b=firstAttack~=nil and updates<firstAttack.player.updates+4}',
                       ' return{right=true,a=updates<jumpUntil,b=firstAttack~=nil and updates<firstAttack.player.updates+4}')
    return r'''
local active,updates
local jumpUntil=0
local firstAttack,swordHit
local launched={}
local routePipes={{448,176,404},{608,160,563},{736,144,679},{912,144,855}}
local routePits={{1104,1136},{1376,1424},{2448,2480}}
local function r(n)return active.r(n)end
local function playerX()return active.x end
local function state()return {updates=updates}end
local function actor(i)
 local e={flag=active.r('Enemy_Flag',i),id=active.r('Enemy_ID',i),state=active.r('Enemy_State',i),
  x=active.r('Enemy_X_Position',i)+256*active.r('Enemy_PageLoc',i),y=active.r('Enemy_Y_Position',i),slot=i}
 if firstAttack and i==firstAttack.target.slot and e.state&32~=0 then swordHit=true end
 return e
end
local function solid(x,y)
 local t=active.block(x,y)
 return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3
end
''' + drive + r'''
local jumpAt=-200
return function(c)
 if c.status>0 or c.x<312 then return travel(c)end
 active=c;updates=c.update
 for i=0,5 do
  local item=actor(i)
  if item.flag==1 and item.id==46 and c.r('PowerUpType',i)==0 then
   local gap=item.x-c.x
   if math.abs(gap)<20 and item.y<c.y-16 and c.grounded and updates-jumpAt>45 then jumpAt=updates end
   return{right=gap>3,left=gap< -3,a=updates-jumpAt<23}
  end
 end
 if updates-jumpAt<23 then return{a=true}end
 local gap=330-c.x
 if math.abs(gap)>2 then return{right=gap>0,left=gap<0}end
 if c.grounded and updates-jumpAt>45 then jumpAt=updates end
 return{a=updates-jumpAt<23}
end
'''


def controller(raw, route):
    cfg = bindings(raw, route)
    policy = opening()
    with patch.object(Stock, 'bindings', return_value=cfg), \
         patch.object(Stock, 'opening_policy', return_value=policy):
        text = Stock.controller(raw, 'getsu', route).decode()
    text = Stock.once(text, 'r(C.variant_field)&C.variant_mask==0\n  and',
                      'r(C.variant_field)&C.variant_mask==C.variant\n  and')
    text = Stock.once(text, "assert(r(C.variant_field)&C.variant_mask==0,'Original identity in menu')",
                      "if r(C.variant_field)&C.variant_mask~=C.variant then return pulse('select') end")
    text = Stock.once(text, "assert(identity(),'Requested character, alternate and difficulty in menu')",
                      "assert(r('SelectedCharacter')==5 and r('CrossoverBehaviorVersion')==C.mode_value,"
                      "'Getsu portrait and difficulty before native Start admission')")
    if route == 'star':
        # The camera follows the Koopa jump and leaves X1621 as the floor's
        # left limit. Approach the brick's right edge from inside that limit.
        text = Stock.once(text, '  if c.x<target-72 then return base(c)end',
                          '  if kind==2 and (c.x<1646 or not c.grounded or c.y<160) then return base(c)end\n'
                          '  if c.x<target-72 then return base(c)end')
        text = Stock.once(text, '  local aim=target-5', '  local aim=kind==2 and target+7 or target-5')
    Stock.LuaRuntime().compile(text)
    return text.encode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--route', choices=ROUTES, required=True)
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    raw = Stock.ROM.read_bytes()
    program = controller(raw, args.route)
    print('GETSU STOCK SOURCE '+json.dumps(dict(ROM_SHA256=Stock.H(raw), route=args.route,
          controller_SHA256=Stock.H(program))), flush=True)
    if not args.run:
        return 0
    guard = Stock.check(Stock.ROM)
    rom, script = Stock.OUT/'candidate.nes', Stock.OUT/'controller.lua'
    assert guard['ROM_sha256'] == Stock.H(raw) and not guard['matching_patch_files']
    assert set(Stock.OUT.iterdir()) == {rom, script} and rom.read_bytes() == raw
    with Stock.preserve_script(script, rom, raw) as stage:
        stage(program)
        result = Stock.run(script, Stock.ROM, Stock.OUT/'capture', Stock.H(raw), 190)
    assert result['script_SHA256'] == Stock.H(program) and result['outputs_written'] == 0 and not result['images']
    assert Stock.ROM.read_bytes() == raw and Stock.check(Stock.ROM) == guard
    print('GETSU STOCK NATIVE '+json.dumps(result, separators=(',', ':')), flush=True)
    return int(not result['passed'])


if __name__ == '__main__':
    raise SystemExit(main())
