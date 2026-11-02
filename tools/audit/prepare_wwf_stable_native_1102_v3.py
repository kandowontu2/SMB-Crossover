"""Repair incomplete observer symbols and count genuine native platform carrying."""
import json,re
from pathlib import Path
import propose_wwf_generic_helper_1102_v1 as P
from prepare_selected_native_packet_v1 import prepare,sha
O=P.R/'build/wwf-helper-stable-1102-v2'

def main():
    old=O/'candidate.nes';rom=O/'candidate2.nes'
    assert not rom.exists();rom.write_bytes(old.read_bytes())
    rom.with_suffix('.dbg').write_bytes(old.with_suffix('.dbg').read_bytes())
    source=P.R/'build/hogan-gap-probe-1102-v4/native/controller.lua';text=source.read_text()
    b=P.scoped_load(P.BASE)
    names=set(re.findall(r"\br\('([^']+)'",text))|set(re.findall(r'\bL\.(\w+)',text))
    names.update(['HpActorOwner','HpRecord','PositionPlayerOnHPlat'])
    labels={n:P.address(b,n) for n in names}
    rom.with_suffix('.lbl').write_text(''.join(f'al {pc:06X} .{n}\n' for n,pc in sorted(labels.items())))
    text='\n'.join(f'L[{json.dumps(n)}]={pc}' for n,pc in labels.items())+'\n'+text
    insert="""
local helperCarries=0
emu.addMemoryCallback(function()
 local pc=emu.getState()['cpu.pc'];local addr=emu.convertAddress(pc)
 if not addr or addr.memType~=emu.memType.nesPrgRom or addr.address~=HELPER_CARRY_PHYSICAL then return end
 local slot=emu.getState()['cpu.x'];local owner=emu.read(L.HpActorOwner+slot,emu.memType.nesDebug)
 if owner>0 and owner<=3 and emu.read(L.HpRecord+owner-1,emu.memType.nesDebug)==34 then helperCarries=helperCarries+1 end
end,emu.callbackType.exec,L.PositionPlayerOnHPlat)
""".replace('HELPER_CARRY_PHYSICAL',str(P.location(b,'PositionPlayerOnHPlat')-16))
    text=insert+text if False else text.replace('local frame,age,phase,step=',insert+'\nlocal frame,age,phase,step=',1)
    marker=" local passed=reason=='active-1-2' and initialLives==r('NumberofLives')"
    assert text.count(marker)==1
    text=text.replace(marker,marker+"\n local hf=assert(io.open(OUTPUT..'helper-contact.json','w'));hf:write(string.format('{\"native_carry_calls\":%d,\"passed_gap\":%s,\"center_x\":1400,\"initial_left_x\":1376,\"initial_y\":208}',helperCarries,tostring(maxX>1424)));hf:close()")
    prepare(O/'native-hogan2',rom,text,[Path(__file__),source,O/'proposal.json',O/'caller-load-CPU.json'],expected=sha(rom),timeout=240,allow_interactive=True,
        scope='Same helper ROM, repaired complete controller symbols; actual native carrying counted using physical PRG-qualified PositionPlayerOnHPlat and owned record34. Controller-only full1-1/no-life-loss assertions retained.')

if __name__=='__main__':main()
