"""Actual menu input/resolution, Start retention, and complete-owner retirement."""
from pathlib import Path
import itertools,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import prepare_metal_storm_menu_1101_v15 as P
import check_hogan_current_bounded_v1 as M
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
def main():
    s=json.loads((P.O/'menu-assembly.json').read_text())
    for p,h in s['bindings'].items():assert P.sha(p)==h,p
    old=scoped_load(P.P/'candidate.nes');new=dict(old,raw=(P.O/'candidate.nes').read_bytes())
    counts=[8,2,2,2,2,4,2,2,2,3,3,2,2,2,3,1,4,4,4,2,2,4,1,2,8,1,2,1,6,2,4,2]
    a=M.fresh(old);b=M.fresh(new);identities=starts=metalstarts=0
    omit=set(range(0x100,0x200))|set(range(0x2000,0x5c00))|set(range(address(old,'R0'),address(old,'R0')+8))|{address(old,n) for n in ['CurrentBank','CurrentBankC','safecall_a']}
    def state(m):return bytes(v for i,v in enumerate(m[:0x8000]) if i not in omit),[bytes(r) for r in m.ram]
    for slot,count in enumerate(counts):
        left=M.fork(a);right=M.fork(b)
        for m in [left,right]:M.put(m,CrossoverMenuIndex=slot);M.invoke(m,'MenuResolveCharacter');M.invoke(m,'QueueSelection');M.invoke(m,'DrawSelectionPreview')
        for variant in range(count):
            if variant:
                for m in [left,right]:M.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0);M.invoke(m,'CrossoverMenuInput')
            metal=slot==11 and variant==1
            if metal:assert M.get(right,'SelectedCharacter')==35 and M.get(right,'FmAlts')&2
            else:assert state(left)==state(right),(slot,variant,'selection')
            for button,flags in itertools.product([16,128],[0x30,0x31,0x71,0xf9]):
                x=M.fork(left);y=M.fork(right)
                for m in [x,y]:M.put(m,CrossoverMenuButtons=0,SavedJoypad1Bits=button,SavedJoypad2Bits=0,VRAM_Buffer1_Offset=0);M.invoke(m,'CrossoverMenuInput',p=flags)
                if metal:
                    assert M.get(y,'SelectedCharacter')==35 and M.get(y,'FmAlts')==2 and M.get(y,'CrossoverMenuState')==0
                    metalstarts+=1
                else:assert state(x)==state(y),(slot,variant,button,flags,'Start');starts+=1
            identities+=1
    cookie=(R/'build/metal-storm-native-integration-1101-v12/native-cookie.bin').read_bytes();retired=0
    for corrupt,button in itertools.product([-1,*range(32)],[1,2,4,8,32]):
        m=M.fork(b);M.put(m,CrossoverMenuIndex=11,FmAlts=2);M.invoke(m,'MenuResolveCharacter');M.invoke(m,'QueueSelection')
        for bank in [2,3]:m.ram[bank][0x1fe0:0x1ff0]=cookie
        if corrupt>=0:m.ram[2+corrupt//16][0x1fe0+corrupt%16]^=1
        before=[bytes(m.ram[k]) for k in [2,3]]
        M.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=button,SavedJoypad2Bits=0);M.invoke(m,'CrossoverMenuInput')
        changed=M.get(m,'SelectedCharacter')!=35
        for i,bank in enumerate([2,3]):
            expect=bytearray(before[i])
            if changed and corrupt<0:expect[0x1fe0]=0
            assert m.ram[bank]==expect,(corrupt,button,bank)
        retired+=1
    assert identities==91 and starts==720 and metalstarts==8
    q=dict(passed=True,ROM_sha256=s['ROM_sha256'],menu_identities=identities,old_Start_cases=starts,Metal_Start_cases=metalstarts,
           paired_header_exit_cases=retired,installed=False,native=False,scope='Actual CPU menu/Start paths. No native Main/IRQ/gameplay, health/combat/audio claim.')
    (P.O/'menu-CPU.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
if __name__=='__main__':main()
