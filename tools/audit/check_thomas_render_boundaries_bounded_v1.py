"""Compare legacy inventory results across every real menu identity and form."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import check_hogan_current_bounded_v1 as C
P=R/'build/thomas-platform-ground';J=R/'build/thomas-native-render';O=J/'boundaries'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists();O.mkdir()
    old,new=[C.scoped_load(p/'candidate.nes')for p in [P,J]]
    stage=json.loads((J/'source-stage.json').read_text())
    for p,h in stage['bindings'].items():assert sha(p)==h,p
    a=16+85*8192+0x133a;z=16+85*8192+0x1900
    outside={i for i in stage['native_changed_offsets']if not a<=i<z}
    inv=C.location(old,'InventorySupported')
    # The three exact farcall operands, one Arthur-source helper pointer and
    # the existing Gimmick head-table low byte rebound by the actual linker.
    assert outside=={inv+32,inv+37,inv+42,C.location(old,'HuExtendedArthur')+1,0xf868d},outside
    assert old['raw'][0xf868d]==C.address(old,'ThGmHeadWithinOwn')&255
    assert new['raw'][0xf868d]==C.address(new,'ThGmHeadWithinOwn')&255
    rows=cases=declined=0
    counts=[7,2,2,2,2,4,2,2,2,3,3,2,2,2,3,1,4,4,4,2,2,4,1,2,4,1,2,1,6,2,4,2]
    for slot,count in enumerate(counts):
        memories=[C.fresh(b)for b in [old,new]]
        for m in memories:
            C.put(m,CrossoverMenuIndex=slot);C.invoke(m,'MenuResolveCharacter');C.invoke(m,'QueueSelection')
        for variant in range(count):
            if variant:
                for m in memories:
                    C.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0)
                    C.invoke(m,'CrossoverMenuInput')
            thomas=slot==10 and C.get(memories[1],'FmAlts')&68==64
            for status in [0,1,2]:
                for flags in [0x30,0x31,0x71,0xf1]:
                    answers=[]
                    for m in memories:
                        C.put(m,PlayerStatus=status)
                        answers.append(C.invoke(m,'InventorySupported',a=85,x=7,y=91,p=flags))
                    if thomas:
                        assert answers[1]['P']&1==0 and answers[1]['A']==answers[1]['X']==10
                        assert answers[1]['Y']==91
                        assert answers[1]['P']&0x4c==flags&0x4c
                        declined+=1
                    else:
                        assert all(answers[0][n]==answers[1][n]for n in ['A','X','Y','P']),(slot,variant,status,flags,answers)
                    cases+=1
            rows+=1
    assert rows==86 and declined==12
    result=dict(passed=True,source_CPU=True,native=False,menu_identities=rows,inventory_cases=cases,
                Thomas_declines=declined,other_identity_registers_flags_exact=True,
                native_outside_resident_changed_offsets=sorted(outside),candidate=sha(J/'candidate.nes'),
                scope='Actual resolved menu identities, all three native power states and four incoming flag combinations. Inventory predicate only, not all powerup gameplay.',
                bindings={str(p):sha(p)for p in [Path(__file__),Path(C.__file__),J/'source-stage.json',P/'candidate.nes',P/'candidate.dbg',J/'candidate.nes',J/'candidate.dbg']})
    (O/'controls.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items()if k!='bindings'}))


if __name__=='__main__':main()
