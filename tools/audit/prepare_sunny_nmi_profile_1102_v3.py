"""Attribute Sunny's reproduced late enable to actual NMI function entries."""
from pathlib import Path
import audit_current_menu_indicators_1102_v1 as A
from check_tmnt_render_oa import address,location
from prepare_selected_native_packet_v1 import R,prepare,sha
from observe_chip_committed_write import lua
O=R/'build/sunny-nmi-profile-1102-v3'
ROM=R/'build/menu-family-root-candidate-1102-v1/mr-gimmick-family.nes'

def main():
    O.mkdir(exist_ok=True);source=R/'build/sunny-deadline-1102-v2/native/controller.lua';text=source.read_text();b=A.bundle();b['raw']=ROM.read_bytes()
    hooks={}
    for name in ['SamusFreezeUpdateScreen','UpdateScreen','BankSwitchCHR','OAMandReadJoypad','PostDmaMaskEnable']:
        at=location(b,name);hooks['Profile'+name]=dict(pc=address(b,name),banks=[(at-16)//8192],bytes=list(b['raw'][at:at+3]))
    extra='\nfor n,h in pairs('+lua(hooks)+')do CURRENT_KIRBY_META_EARNED.hooks[n]=h end\n'
    for n in ['VRAM_Buffer_AddrCtrl','VRAM_Buffer1_Offset','Mirror_PPUMASK','DisableScreenFlag']:
        extra+='CURRENT_KIRBY_META_EARNED.ram['+lua(n)+']='+str(address(b,n))+'\n'
    first,rest=text.split('\n',1);text=first+extra+rest
    anchor="emu.addMemoryCallback(function(_,v)\n if entered and nmi and v&24~=0 then"
    assert text.count(anchor)==1
    profile='''local timing=nil
hook('NmiEntry',function(s)
 timing={start=s['cpu.cycleCount'],line=s['ppu.scanline'],dot=s['ppu.cycle'],buffer=r('VRAM_Buffer1_Offset'),addressControl=r('VRAM_Buffer_AddrCtrl'),screenOff=r('DisableScreenFlag'),events={}}
end)
for _,name in ipairs({'SamusFreezeUpdateScreen','UpdateScreen','BankSwitchCHR','OAMandReadJoypad','PostDmaMaskEnable'})do
 hook('Profile'..name,function(s)
  if timing and nmi and #timing.events<12 then table.insert(timing.events,{name=name,elapsed=s['cpu.cycleCount']-timing.start,line=s['ppu.scanline'],dot=s['ppu.cycle']})end
 end)
end
'''
    text=text.replace(anchor,profile+anchor)
    text=text.replace("   local f=assert(io.open(OUTPUT..'late-enable.json','w'))","   q.profile=timing;q.elapsed=s['cpu.cycleCount']-timing.start\n   local f=assert(io.open(OUTPUT..'late-enable.json','w'))")
    deps=[R/'tools/playthroughs'/n for n in ['sunny_11_v3.lua','sunny_11_v1.lua','mario_luigi_scrooge_policy.lua','mario_luigi_scrooge_nav.lua']]
    prepare(O/'native',ROM,text,[Path(__file__),source,*deps],expected=sha(ROM),timeout=180,scope='Sunny same controller first late NMI enable with bounded in-memory function-entry timings, emitted once on failure. No ROM/state change; assertion retained.',allow_interactive=True)
if __name__=='__main__':main()
