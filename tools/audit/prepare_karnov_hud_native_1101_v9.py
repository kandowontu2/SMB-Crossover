"""Observe original equipment icons/text under real native font publication."""
from pathlib import Path
import json
import prepare_karnov_options_native_1101_v8 as V
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address


def main():
    prepare=V.P.prepare;once=V.P.once
    def hud(output,rom,t,refs,**kw):
        b=scoped_load(rom)
        t=''.join(f'L["{n}"]={address(b,n)}\n'for n in ['InvHudActive','InvHudPhysical','X5HudChrUpper','X5WideChrActive'])+t
        t='local HUDChecks,HUDMaps,WorldMaps=0,0,0\n'+t
        t=once(t,'[0xbd]=1,[0xbe]=1,[0xbf]=1','[0xbd]=2,[0xbe]=2,[0xbf]=2')
        t=once(t,"assert(optionStock==0,'Original stock consumed once')","assert(optionStock==1,'Original stock consumed once')")
        t=once(t,'source_weapons=weaponTicks,','source_weapons=weaponTicks,HUD_checks=HUDChecks,HUD_font_maps=HUDMaps,world_font_maps=WorldMaps,')
        point='emu.addMemoryCallback(function()apu=apu+1 end,emu.callbackType.write,0x4000,0x4017)'
        t=once(t,point,point+'''
emu.addMemoryCallback(function(_,v)
 if active()then
  if upper+v==1023 then HUDMaps=HUDMaps+1 elseif upper+v==0 then WorldMaps=WorldMaps+1 end
 end
end,emu.callbackType.write,0x5128)
''')
        marker=" if active()and updates>15 then"
        t=once(t,marker,''' if active()and activatedAt and updates>=activatedAt+10 then
  local ppu=emu.memType.nesPpuDebug
  local function chr(c)return c==' 'and 36 or string.byte(c)-55 end
  local name=equipmentOption==0 and'BOOTS    'or equipmentOption==3 and'BOOMERANG'or'WINGS    '
  assert(r('InvHudActive')==233 and r('InvHudPhysical')==255 and r('X5HudChrUpper')==3 and r('X5WideChrActive')==1,'Exclusive wide HUD font lease')
  for i=1,9 do assert(emu.read(0x2022+i,ppu)==chr(name:sub(i,i)),'Equipment HUD name')end
  assert(emu.read(0x202d,ppu)==0 and emu.read(0x202e,ppu)==1,'Remaining original BCD stock01')
  local tile=equipmentOption==0 and 0x30 or equipmentOption==3 and 0x34 or 0x38
  for i,a in ipairs({0x2037,0x2038,0x2057,0x2058})do assert(emu.read(a,ppu)==tile+i-1,'Original equipment icon layout')end
  HUDChecks=HUDChecks+1
 end
'''+marker)
        t=once(t,"finish(vectors>100 and sourceTicks>50,'Original equipment activation, stock, controls and displayed body; declared stock fixture')",
                  "finish(vectors>100 and sourceTicks>50 and HUDChecks>5 and HUDMaps>5 and WorldMaps>5,'Original equipment controls, visible HUD name/stock/icon and wide/NMI/world font publication; declared stock fixture')")
        kw['scope']+=' Two earned-stock uses are explicitly initialized per equipment, leaving01 after activation so its original icon remains selected. Native PPU checks verify fullname/BCD/icon tiles, exact font lease and actual HUD/world publications.'
        result=prepare(output,rom,t,[*refs,Path(__file__)],**kw)
        path=output/'ready.json';q=json.loads(path.read_text());q['fixture_initial_stock']=2
        path.write_text(json.dumps(q,indent=2)+'\n');return result
    V.P.prepare=hud;V.main()


if __name__=='__main__':main()
