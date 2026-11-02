"""Extend the verified four-pipe Thomas controller through the remainder of 1-1."""
from pathlib import Path
import propose_wwf_generic_helper_1102_v1 as P
from prepare_selected_native_packet_v1 import R,prepare,sha
O=R/'build/thomas-full11-1102-v1'
def main():
    source=R/'build/thomas-platform-native/controller.lua';text=source.read_text()
    rom=R/'build/wwf-helper-stable-1102-v2/candidate2.nes'
    text=text.replace('5471f6333b02f786ccb6009b20ed49568772385692ceedef9062b4fb3f8e0262',sha(rom))
    old="   if visible('game')and platformVisible()then finish(counters.defeat>0 and counters.source==counters.movement and counters.vectors>100,'Native moving-platform pipe crossings and source melee defeat');return end"
    assert text.count(old)==1;text=text.replace(old,"   routeState='full-stage';return")
    marker=' local lift,pipeTop=targets[target][1],targets[target][2]';assert text.count(marker)==1
    block=P.address(P.scoped_load(P.BASE),'Block_Buffer_1')
    insertion=f"""
 if routeState=='full-stage' then
  local function solid(xx,yy)
   if yy<32 or yy>=240 then return false end
   local tile=peek({block}+((xx//256)%2)*208+((yy-32)//16)*16+(xx%256)//16)
   return tile~=0 and tile~=0x23 and tile~=0x26 and tile~=0xc2
  end
  pad={{right=true}}
  if r('Player_State')==0 then
   if not solid(x+12,216) or solid(x+20,py+12) then pad.up=updates%8<3 end
   for i=0,5 do
    local dx=r('Enemy_PageLoc',i)*256+r('Enemy_X_Position',i)-x
    if r('Enemy_Flag',i)>0 and r('Enemy_Flag',i)<128 and r('Enemy_ID',i)<21 and r('Enemy_State',i)&32==0 and dx>0 and dx<38 and math.abs(r('Enemy_Y_Position',i)-py)<40 then pad={{down=true,b=updates%24<6}};break end
   end
  end
  if updates%10==0 then csv:write(table.concat({{frame,updates,x,py,camera,routeState,target,r('SavedJoypadBits'),counters.defeat,-1,-1}},',')..'\\n');csv:flush()end
  return
 end
"""
    text=text.replace(marker,insertion+marker)
    marker="  if r('GameEngineSubroutine')==11 or r('NumberofLives')~=initialLives then"
    assert marker in text
    text=text.replace(marker,"  if r('LevelNumber')==1 and r('WorldNumber')==0 and r('GameEngineSubroutine')==8 then finish(r('NumberofLives')==initialLives,'Full1-1 active1-2');return end\n"+marker)
    text=text.replace('updates>=4500','updates>=12000').replace('4500 Main route bound','12000 Main route bound').replace('frame>=10000','frame>=24000').replace('10000 physical frame bound','24000 physical frame bound')
    O.mkdir(exist_ok=True)
    prepare(O/'native',rom,text,[Path(__file__),source],expected=sha(rom),timeout=240,allow_interactive=True,
        scope='Current ROM controller-only Thomas full1-1 attempt, extending original native4pipe/CHR/ABI checks; original Upjump and crouchB. FourPNG maximum; existing helpers only, no writes.')
if __name__=='__main__':main()
