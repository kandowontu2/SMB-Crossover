"""Retain Sunny's first real rendering-deadline negative with exact timing."""
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha
O=R/'build/sunny-deadline-1102-v2'
ROM=R/'build/menu-family-root-candidate-1102-v1/mr-gimmick-family.nes'

def main():
    O.mkdir(exist_ok=True);source=R/'build/sunny-current-full11-1102-v1/native/controller.lua';text=source.read_text()
    anchor="  if not safe then late=late+1 end;assert(safe,'Actual NMI render enable deadline')"
    assert text.count(anchor)==1
    replacement='''  if not safe then
   late=late+1
   local q={ROM_sha256=C.ROM_sha256,frame=wall,updates=updates,line=line,dot=dot,pc=s['cpu.pc'],sp=s['cpu.sp'],mask=v,x=world(),y=r('Player_Y_Position'),status=r('PlayerStatus'),size=r('PlayerSize'),engine=r('GameEngineSubroutine'),bankA=bank(0xa000),bankC=bank(0xc000),nmi=nmis,irq=irqCount}
   local f=assert(io.open(OUTPUT..'late-enable.json','w'));f:write(json(q));f:close()
   local p=assert(io.open(OUTPUT..'late-enable.png','wb'));p:write(emu.takeScreenshot());p:close()
  end
  assert(safe,'Actual NMI render enable deadline')'''
    text=text.replace(anchor,replacement)
    deps=[R/'tools/playthroughs'/n for n in ['sunny_11_v3.lua','sunny_11_v1.lua','mario_luigi_scrooge_policy.lua','mario_luigi_scrooge_nav.lua']]
    prepare(O/'native',ROM,text,[Path(__file__),source,*deps],expected=sha(ROM),timeout=180,scope='Same Sunny natural input discovery; first late NMI render enable saves exact timing/PC/native state and one PNG before keeping failing assertion. No ROM/game-state change.',allow_interactive=True)
if __name__=='__main__':main()
