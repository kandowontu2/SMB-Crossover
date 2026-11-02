"""Read-only first-write trace of Arthur's flower-approach wall displacement."""
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha
O=R/'build/arthur-natural-flower-1101-v6'

def main():
 ref=O/'native2/controller.lua';t=ref.read_text()
 t=t.replace('local jumps=0', '''local drift=assert(io.open(OUTPUT..'displacement.csv','w'))
drift:write('frame,old_x,new_x,y,pc,bank_a,bank_c,r0,r4,r5,speed,player_state,source_mode\\n')
local driftCount,lastWrite=0,nil
local jumps=0''',1)
 t=t.replace('row();trace:close();shot(', 'row();trace:close();drift:close();shot(',1)
 marker="emu.addMemoryCallback(function()\n if phase=='play' then mainCalls=mainCalls+1 end"
 hook='''emu.addMemoryCallback(function(_,value)
 if phase=='play' and seenItem and lastWrite and math.abs(value-lastWrite)>8 and driftCount<16 then
  local s=emu.getState();driftCount=driftCount+1
  drift:write(string.format('%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d\\n',frame,lastWrite,value,r('Player_Y_Position'),s['cpu.pc'] or 0,r('CurrentBank'),r('CurrentBankC'),r('R0'),r('R4'),r('R5'),r('Player_X_Speed'),r('Player_State'),r('ArMode')))
 end
 lastWrite=value
end,emu.callbackType.write,assert(L.Player_X_Position))
'''
 assert t.count(marker)==1;t=t.replace(marker,hook+marker)
 t=t.replace('if age>=1600 then','if age>=600 then')
 rom=R/'build/shinobi-bbox-candidate-1101-v30/candidate.nes'
 prepare(O/'diagnostic',rom,t,[Path(__file__),ref],expected=sha(rom),timeout=90,allow_interactive=True,scope='Read-only Xwrite diagnosis of genuine Arthur firstflower approach on v30. Atmost16displacement rows,4PNGs,600playframes; no emulated memory writes. Failed collection assertion retained; diagnosis doesnotqualify pickup.')

if __name__=='__main__':main()
