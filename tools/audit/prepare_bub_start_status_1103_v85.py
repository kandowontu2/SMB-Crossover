"""Observe the actual native writes that give unupgraded Bub status1."""
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare
O=R/'build/bub-head-start-status-1103-v85'
PIN='cc7b9bddfd39c62fadb5c1afc34bc82361432eab5a8a8e5b5a18bde184813a4e'

def main():
    O.mkdir(exist_ok=True)
    source=R/'build/bub-head-item-diagnostic-1103-v84/bub-item/controller.lua'
    text=source.read_text();needle='local upgrade_attempts=0';assert text.count(needle)==1
    observer='''
local status_writes={}
emu.addMemoryCallback(function(_,value)
 if r('SelectedCharacter')~=39 then return end
 local s=emu.getState();local pc=s['cpu.pc'];local at=emu.convertAddress(pc)
 local key=tostring(pc)..':'..tostring(at and at.address)..':'..tostring(value)
 local row=status_writes[key]
 if row then row.count=row.count+1 else
  local nearby={}for i=-3,4 do nearby[#nearby+1]=ram((pc+i)&65535)end
  status_writes[key]={pc=pc,physical=at and at.address or -1,memory=at and at.memType or -1,value=value,phase=phase,count=1,nearby=nearby}
 end
 local f=assert(io.open(OUTPUT..'status-writes.json','w'));f:write(BUB_OBSERVER.json(status_writes)..'\\n');f:close()
end,emu.callbackType.write,L.PlayerStatus)
'''
    text=text.replace(needle,observer+'\n'+needle)
    rom=R/'build/bub-head-root-candidate-1103-v81/bub-source-head.nes'
    prepare(O/'bub-status',rom,text,[Path(__file__),source],expected=PIN,timeout=90,allow_interactive=True,scope='Private diagnostic only: one deduplicated aggregate observer of actual PlayerStatus write PCs/physical banks/values during real cold menu/gameplay. Same actual first-block diagnostic and no writes or installed change. Identifies native start tier/sourceflags mismatch before choosing a repair.')

if __name__=='__main__':main()
