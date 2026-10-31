"""Actual Select/name/Start consumers and preserved status-call ABI."""
from pathlib import Path
import itertools
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import bowser_current64_menu_controls_v1 as U
import smb3plus_kick_host_controls_1031_v1 as K
import prepare_functional_roster_visuals58_v1 as B
from check_tmnt_render_oa import address
from link_pit_rygar_sophia_audit_cpu import scoped_load
M=K.M;C,H=U.C,U.H
O=R/'build/smb3plus-menu-host-1031-v4';J=O/'joint'
P=R/'build/smb3plus-peach-float-host-1031-v4/joint'


def tiles(s):return bytes(ord(c)-55 if 'A'<=c<='Z' else ord(c)-48 if c.isdigit() else 36 for c in s)


def main():
    assert not (O/'menu-controls-v1.json').exists()
    stage=json.loads(B.read(O/'source-stage.json'));B.bound(stage)
    old,new=[scoped_load(p/'candidate.nes') for p in [P,J]]
    menus=[]
    for slot,count in enumerate(U.COUNTS):
        if slot==16:continue
        pair=[]
        for b in [old,new]:
            m=C.fresh(b,0);H.put(m,CrossoverMenuIndex=slot,FfVariant=0,FmAlts=0)
            C.invoke(m,'MenuResolveCharacter');C.invoke(m,'QueueSelection');pair.append(m)
        for variant in range(count):
            if variant:
                for m in pair:
                    H.put(m,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0,VRAM_Buffer1_Offset=0)
                    C.invoke(m,'CrossoverMenuInput')
            got=[]
            for m in pair:
                z=C.invoke(m,'FmPending');got.append([H.get(m,'SelectedCharacter'),z['AXYP_SP'][0],z['AXYP_SP'][3]&1,U.queue(m)])
            assert got[0]==got[1],('Foreign menu',slot,variant,got[0][:3],got[1][:3])
            menus.append(dict(slot=slot,variant=variant,selected=got[1][0],pending=got[1][2]))
    own=[];m=C.fresh(new,0)
    H.put(m,CrossoverMenuIndex=16,FfVariant=0,FmAlts=0,M3Variant=0)
    C.invoke(m,'MenuResolveCharacter');C.invoke(m,'QueueSelection')
    names=['   SMB3 MARIO   ','   SMB3 LUIGI   ','   SMB3 TOAD    ','   SMB3 PEACH   ']
    for variant in [0,1,2,3,0]:
        assert H.get(m,'SelectedCharacter')==17 and H.get(m,'M3Variant')==variant
        packet=U.queue(m);assert tiles(names[variant]) in packet,(variant,packet.hex())
        ready=C.invoke(m,'FmPending');assert not ready['AXYP_SP'][3]&1
        own.append(dict(variant=variant,name=names[variant],actual_queue=packet.hex()))
        H.put(m,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0,VRAM_Buffer1_Offset=0)
        C.invoke(m,'CrossoverMenuInput')
    abi=[]
    for variant,arg,bits in itertools.product(range(4),[0,1,128],range(64)):
        flags=0x30|(bits&15)|((bits&48)<<2)
        results=[]
        for b in [old,new]:
            q=M.T.make(b,17);q.put(M3Variant=variant)
            c,tr,path,info=M.T.invoke(q,'M3StatusNameDispatch',a=arg,x=53,y=99,p=flags)
            results.append((M.regs(c),q.m.banks[:],bytes(q.m[address(b,'VRAM_Buffer1')+11:address(b,'VRAM_Buffer1')+18])))
        assert results[0][:2]==results[1][:2],('Status ABI',variant,arg,flags,results)
        expected=tiles(stage['status_names'][variant]) if arg==0 else bytes(7)
        assert results[1][2]==expected,(variant,arg,results[1][2].hex(),expected.hex())
        if variant<2:assert results[0][2]==results[1][2]
        abi.append(dict(variant=variant,arg=arg,flags=flags,AXYP_SP=results[1][0]))
    starts=[]
    for variant in [2,3]:
        r=C.fresh(new,0);H.put(r,CrossoverMenuIndex=16,M3Variant=variant,FmAlts=0,FfVariant=0)
        C.invoke(r,'MenuResolveCharacter');C.invoke(r,'QueueSelection')
        H.put(r,CrossoverMenuButtons=0,SavedJoypad1Bits=16,SavedJoypad2Bits=0,VRAM_Buffer1_Offset=0)
        C.invoke(r,'CrossoverMenuInput')
        assert H.get(r,'SelectedCharacter')==17 and H.get(r,'M3Variant')==variant
        starts.append(dict(variant=variant,selected=H.get(r,'SelectedCharacter'),mode=H.get(r,'OperMode'),
            menu_state=H.get(r,'CrossoverMenuState')))
    d=dict(passed=True,CPU_only=True,native=False,candidate=stage['candidate'],
        foreign_menu_identities=len(menus),foreign=menus,actual_Select_cycle=own,
        status_ABI_cases=len(abi),status=abi,actual_Start_cases=starts,
        limits=stage['limits'],bindings={str(p):B.sha(p) for p in [Path(__file__),Path(U.__file__),
            O/'source-stage.json',J/'candidate.nes',J/'candidate.dbg',P/'candidate.nes',P/'candidate.dbg']})
    B.write(O/'menu-controls-v1.json',json.dumps(d,indent=2)+'\n')
    print(json.dumps(dict(passed=True,foreign=len(menus),status_ABI=len(abi),starts=starts,candidate=stage['candidate'])))


if __name__=='__main__':main()
