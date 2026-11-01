"""Native equipment controls/rendering with a declared earned-stock fixture.

Cold menu and all movement/activation use controller input. Only six source
inventory bytes are initialized after gameplay starts; no ROM/code/terrain,
native position, clock, enemy, SMC or mapper writes are made by this fixture.
"""
from pathlib import Path
import argparse,json,sys
import prepare_karnov_opening_native_1101_v1 as P


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--option',type=int,choices=[0,3,7],required=True);a=ap.parse_args()
    prepare=P.prepare;once=P.once
    def equipment(output,rom,t,refs,**kw):
        t='local equipmentOption='+str(a.option)+'''
local fixtureAt,activatedAt,firedAt,returnedAt=nil,nil,nil,nil
local optionStock=nil
local equipmentBase,equipmentPeak,flightUp,flightDown=nil,nil,nil,nil
local equipmentDone=false
local function kwrite(off,v)emu.write(2*8192+off,v,emu.memType.nesWorkRam)end
'''+t
        t=once(t,'source_weapons=weaponTicks,','source_weapons=weaponTicks,equipment_option=equipmentOption,fixture_update=fixtureAt,activated_update=activatedAt,option_stock=optionStock,boomerang_fired=firedAt,boomerang_returned=returnedAt,equipment_base=equipmentBase,equipment_peak=equipmentPeak,flight_up=flightUp,flight_down=flightDown,')
        lo=t.index(' if updates<=40 then');hi=t.index(' if updates%20==0',lo)
        t=t[:lo]+'''
 if updates==20 then
  -- Deliberate earned-equipment fixture. Collection has a separate test.
  for off,v in pairs({[0x65]=2,[0x8e]=255,[0x8f]=137,[0xbd]=1,[0xbe]=1,[0xbf]=1})do kwrite(off,v)end
  fixtureAt=updates;equipmentBase=y;equipmentPeak=y
 end
 if not fixtureAt then pad={};return end
 local n=updates-fixtureAt
 local presses=equipmentOption==0 and 1 or equipmentOption==3 and 2 or 3
 if n<presses*8 then pad=n%8<4 and{select=true}or{};return end
 n=n-presses*8
 if n<4 then pad={down=true,b=true};return end
 if not activatedAt then
  assert(kr(0x8e)==equipmentOption,'Fresh Select chose the requested source option')
  assert(equipmentOption~=0 or kr(0x65)&128~=0,'Original boots activation')
  assert(equipmentOption~=3 or kr(0x65)&15==8,'Original boomerang activation')
  assert(equipmentOption~=7 or kr(0x62)&31==15 or equipmentOption==7 and kr(0x62)&31==16,'Original wings activation')
  optionStock=kr(equipmentOption==0 and 0xbd or equipmentOption==3 and 0xbe or 0xbf)
  assert(optionStock==0,'Original stock consumed once');activatedAt=updates
 end
 local use=updates-activatedAt
 if equipmentOption==0 then
  equipmentPeak=math.min(equipmentPeak,y);pad=use>=4 and use<26 and{a=true}or{}
  if use>85 then equipmentDone=equipmentBase-equipmentPeak==88 and r('Player_State')==0 end
 elseif equipmentOption==3 then
  pad=use%24<4 and{b=true}or{}
  if kr(0x6e)&128~=0 and not firedAt then firedAt=updates end
  if firedAt and kr(0x65)&15==2 then returnedAt=updates;equipmentDone=true end
 else
  if use<4 then pad={}
  elseif use<24 then pad={up=true}
  elseif use<28 then flightUp=y;pad={}
  elseif use<48 then pad={down=true}
  else flightDown=y;pad={};equipmentDone=flightUp<equipmentBase and flightDown>flightUp end
 end
'''+t[hi:]
        lo=t.index('if updates>=240 and maxX>=220');hi=t.index(';return end',lo)+len(';return end')
        t=t[:lo]+"if equipmentDone and shown.game and shown.game.visible and not lastMain then finish(vectors>100 and sourceTicks>50,'Original equipment activation, stock, controls and displayed body; declared stock fixture');return end"+t[hi:]
        t=once(t,"if updates>=650 and not lastMain then finish(false,'650 Main route bound');return end","if updates>=260 and not lastMain then finish(false,'260 Main equipment bound');return end")
        t=once(t,"if updates>=35 and shown.game and not shown.game.shot", "if activatedAt and updates>=activatedAt+15 and shown.game and not shown.game.shot")
        kw['scope']='Cold controller Select/Start with original portrait/lives/body CHR, palette, DMA and ISR checks. Six declared source inventory bytes create earned stock at Main20; subsequent Select/Down+B/use controls are real controller input. Tests boots88px jump, boomerang flight/return or wingsUp/Down. No claim that the fixture collected gear or qualified expiry/full-stage/audio.'
        result=prepare(output,rom,t,[*refs,Path(__file__)],**kw)
        path=output/'ready.json';q=json.loads(path.read_text());q['emulated_writes']=True
        q['fixture_source_offsets']=[0x65,0x8e,0x8f,0xbd,0xbe,0xbf]
        path.write_text(json.dumps(q,indent=2)+'\n')
        return result
    P.prepare=equipment
    sys.argv=[sys.argv[0],'--output',str(a.output)];P.main()


if __name__=='__main__':main()
