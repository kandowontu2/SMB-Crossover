"""Bounded read-only trace of the failing cold Shinobi native launch."""
from prepare_selected_native_packet_v1 import prepare,sha
from pathlib import Path
import prepare_shinobi_menu_1101_v13 as P
import prepare_shinobi_owning_graft_1101_v1 as S


def main():
 c=(P.O/'native-smoke/controller.lua').read_text()
 lab=S.labels(P.R/'build/shinobi-hurt-layout-1101-v5/component.lbl')
 observer='''local events,writes={},{}
local function sample(id)
 if #events>=120 then return end
 local function v(a)return emu.read(a,emu.memType.nesDebug)end
 table.insert(events,string.format('[%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d]',id,frame,r('Player_X_Position'),r('Player_Y_Position'),r('Player_Y_HighPos'),r('PlayerSize'),r('GameEngineSubroutine'),r('CurrentBank'),r('CurrentBankC'),v(0xc379),v(0xc38f),v(0xc413),v(0xc800),v(0xc31)))
end
emu.addMemoryCallback(function(_,value)
 if frame>=450 and #writes<80 and r('SelectedCharacter')==36 then
  local s=emu.getState()
  table.insert(writes,string.format('[%d,%d,%d,%d,%d,%d,%d,%d]',frame,s['cpu.pc'],value,r('CurrentBank'),r('CurrentBankC'),r('Player_X_Speed'),r('Player_X_Scroll'),r('SavedJoypadBits')))
 end
end,emu.callbackType.write,L['Player_X_Position'])
'''
 for i,n in enumerate(['ShHostConstruct','ShHostMovement','ShMoveDone','ShHostDraw'],1):
  observer+=f"emu.addMemoryCallback(function() if r('SelectedCharacter')==36 and r('CurrentBank')==3 and r('CurrentBankC')==2 then sample({i}) end end,emu.callbackType.exec,{lab[n]})\n"
 c=c.replace('local function shot',observer+'local function shot',1)
 c=c.replace('done=true;emu.stop',"local z=assert(io.open(OUTPUT..'trace.json','w'));z:write('{\"calls\":['..table.concat(events,',')..'],\"writes\":['..table.concat(writes,',')..']}');z:close();done=true;emu.stop")
 prepare(P.O/'native-trace',P.O/'candidate.nes',c,[Path(__file__)],expected=sha(P.O/'candidate.nes'),timeout=90,scope='Same failed native replay,120 compact read-only observations, three PNGs. No state writes.')


if __name__=='__main__':main()
