"""Compare delivered foreign simultaneous Select/confirm against actual d0b."""
import copy,json
import audit_current_menu_indicators_1102_v1 as A
import audit_bub_menu_frontend_1102_v1 as F
from inventory_playable_menu_1101_v3 import menu_name
from prepare_selected_native_packet_v1 import sha

R=A.R;O=R/'build/bub-menu-candidate-1102-v2'
CURRENT=R/'build/menu-family-root-candidate-1102-v1/mr-gimmick-family.nes'
PIN='22d09909bf952ef007d1582589dc869073262784bf38b92d2c7b206ce3c45b19';M=F.M

def main():
    old=A.bundle();new=copy.copy(old);new['raw']=CURRENT.read_bytes();assert sha(CURRENT)==PIN
    comparisons=0;profiles=0;examples=[];own=[]
    for slot,count in enumerate(F.COUNTS):
        if slot==25:continue
        pair=[M.fresh(b)for b in[old,new]]
        for m in pair:
            M.put(m,CrossoverMenuIndex=slot);m[0x5ffe]=0
            F.invoke(m,'MenuResolveCharacter');F.invoke(m,'QueueSelection')
        for cycle in range(count):
            for keys in[16,128,48,160,176]:
                results=[]
                for seed in pair:
                    m=M.fork(seed);M.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=keys,SavedJoypad2Bits=0)
                    z=F.invoke(m,'CrossoverMenuInput')
                    results.append((m,z))
                a,za=results[0];b,zb=results[1]
                names=['CrossoverMenuState','CrossoverMenuIndex','SelectedCharacter','FmAlts','FmGroups','MarioVariant']
                assert[M.get(a,n)for n in names]==[M.get(b,n)for n in names],(slot,cycle,keys,names)
                assert bytes(a[0x5fe0:0x5ff0])==bytes(b[0x5fe0:0x5ff0]),(slot,cycle,keys,'variant byte domain')
                assert all(za[k]==zb[k]for k in['A','X','Y','P']),(slot,cycle,keys,'actual AXYP',za,zb)
                comparisons+=1
                if slot==29 and cycle==0 and keys==48:
                    assert M.get(b,'CrossoverMenuState')==2 and M.get(b,'SelectedCharacter')==0
                    examples.append(dict(slot=slot,initial='EXCITEBIKE',keys='Select+Start',result='locked Prince selected; confirmation remains menu',raw=0))
            for m in pair:
                M.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0)
                F.invoke(m,'CrossoverMenuInput')
            profiles+=1
    m=M.fresh(new);M.put(m,CrossoverMenuIndex=25);m[0x5ffe]=0
    F.invoke(m,'MenuResolveCharacter');F.invoke(m,'QueueSelection')
    for state in range(3):
        name,cells=menu_name(m);assert name==['MR GIMMICK','BUB','BOB'][state]
        for keys in[48,160,176]:
            n=M.fork(m);M.put(n,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=keys,SavedJoypad2Bits=0)
            F.invoke(n,'CrossoverMenuInput')
            next_state=(state+1)%3
            assert M.get(n,'CrossoverMenuState')==0 and M.get(n,'SelectedCharacter')==[26,39,39][next_state]
            assert bool(M.get(n,'FmGroups')&128)==(next_state==2)
            own.append(dict(initial=name,keys=keys,next_family_state=next_state,raw=M.get(n,'SelectedCharacter'),Bob=bool(M.get(n,'FmGroups')&128)))
        M.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0);F.invoke(m,'CrossoverMenuInput')
    q=dict(passed=True,ROM_changed=False,ROM_sha256=PIN,foreign_profiles=profiles,foreign_actual_input_differentials=comparisons,
        foreign_control_and_AXYP_exact=True,family_simultaneous_cases=own,retained_oracle_negative=examples,
        policy='Actual MnMenuEdges consumes maskedSelect first, then restoresconfirminput; result must be compared to next selectedprofile. Old v18 per-current-name expectation was incorrect for ExSelectStart selectinglockedPrince.',
        bindings={str(p.relative_to(R)):sha(p)for p in[Path(__file__),CURRENT,A.ROM,R/'tools/reference/menu_input_1101_v3.inc']})
    (O/'menu-family-simultaneous-v19.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))

from pathlib import Path
if __name__=='__main__':main()
