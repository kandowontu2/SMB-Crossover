"""Observe real Giant contact defeat and block shattering using controller input only."""
import argparse
from pathlib import Path

import prepare_mega_giant_f33_native_1110 as G
from prepare_selected_native_packet_v1 import prepare, sha


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--expected-sha', required=True)
    p.add_argument('--proof', type=Path, required=True)
    a = p.parse_args()
    assert sha(a.rom) == a.expected_sha
    source = G.controller(a.expected_sha)
    bundle = G.Q.C.bundle(G.BASE.read_bytes())
    names = ('Block_State', 'Block_Metatile', 'InjuryTimer')
    definitions = '\n'.join(f'C.ram.{n}={G.Q.C.address(bundle,n)}' for n in names)
    at = source.index('\n-- Actual Select')
    source = source[:at] + '\n' + definitions + source[at:]
    source = source.replace('local frame, updates, draws, lag',
                            'local combat={defeats={},injury_calls=0,shatters={},head_hits={},original_materials={}}\n'
                            'local frame, updates, draws, lag', 1)
    source = source.replace('terminal=state(),body=body,flag=flag,',
                            'terminal=state(),combat=combat,body=body,flag=flag,', 1)
    at = source.index('hook(C.main,')
    source = source[:at] + '''hook(0xb174,emu.memType.nesPrgRom,90*8192+(0xb174&8191),function()
 combat.original_materials[#combat.original_materials+1]={metatile=ram(6),player=state()}
end)
hook(0x9af5,emu.memType.nesPrgRom,126*8192+(0x9af5&8191),function()
 local slot=emu.getState()['cpu.x']
 combat.defeats[#combat.defeats+1]={slot=slot,id=r('Enemy_ID',slot),
   x=pos('Enemy_X_Position','Enemy_PageLoc',slot),enemy_state=r('Enemy_State',slot),player=state()}
end)
hook(0x976c,emu.memType.nesPrgRom,126*8192+(0x976c&8191),function()
 combat.injury_calls=combat.injury_calls+1
end)
hook(0x9ef5,emu.memType.nesPrgRom,126*8192+(0x9ef5&8191),function()
 combat.head_hits[#combat.head_hits+1]={metatile=emu.getState()['cpu.a'],player=state()}
end)
for slot=0,1 do
 emu.addMemoryCallback(function(_,value)
  if active() and value==0x12 then
   combat.shatters[#combat.shatters+1]={slot=slot,player=state()}
  end
 end,emu.callbackType.write,C.ram.Block_State+slot)
end
''' + source[at:]
    start = source.index('local function choose()')
    end = source.index('\nemu.addEventCallback(function()\n frame=frame+1', start)
    source = source[:start] + '''local function choose()
 input={right=true}
 if x()>=400 then
  local goomba=false
  for _,v in ipairs(combat.defeats) do if v.id==6 then goomba=true end end
  local ok=goomba and combat.injury_calls==0 and r('InjuryTimer')==0 and #combat.shatters>0
  return finish(ok,'first Goomba ground contact and native block shatter')
 end
end
''' + source[end:]
    prepare(a.output, a.rom, source,
            {Path(__file__), Path(G.__file__), G.SOURCE, G.PROOF, G.ROUTE,a.proof},
            expected=a.expected_sha, timeout=120, allow_interactive=True,
            rom_symbols=(G.BASE.with_suffix('.lbl'), G.BASE.with_suffix('.dbg')),
            scope='Walk into first Goomba without A or cheats; native defeat entry, '
                  'injury calls and block shatter writes observed. No gameplay state writes.')


if __name__ == '__main__':
    main()
