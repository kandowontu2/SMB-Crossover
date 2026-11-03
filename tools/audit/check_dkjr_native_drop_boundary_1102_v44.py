"""Measure exact current native drop-hook side effects for typed owner40.

This is a proposed private specialization boundary, no native hook changes.
"""
import itertools,json
from pathlib import Path
import check_dkjr_native_lifecycle_1102_v31 as F
import measure_dkjr_admission_1102_v11 as A
import check_hogan_current_bounded_v1 as N
R=A.R;O=A.O;W=A.W


def main():
    b,seed,L,q=F.fixture();cases=0;footprints=set();minimum=255
    destination=W.address(b,'InvDropEnemy')
    # All native drop eligibility controls for owner40: Easy/Hard, slot,
    # full/empty drop slots, random outcomes. Variant bytes are irrelevant
    # because each live source predicate rejects40 before its variant read.
    for mode,slot,occupied,random,flags in itertools.product([0,1],range(6),[0,1],[0,1,255],[0x30,0xf1]):
        m=N.fork(seed);N.put(m,CrossoverBehaviorVersion=mode,SelectedCharacter=40)
        for i in range(4):m[W.address(b,'InvDropKind')+i]=occupied
        for i in range(3):m[W.address(b,'PseudoRandomBitReg')+i]=random
        m[destination]=0xa5;before=list.__getitem__(m,slice(0,32768));state=[bytes(v)for v in m.ram];maps=list(m.rawtags)
        z=N.invoke(m,'InventoryDropHook',a=85,x=slot,y=91,p=flags);minimum=min(minimum,z['minimum_SP'])
        after=list.__getitem__(m,slice(0,32768))
        changes=[(i,old,new)for i,(old,new)in enumerate(zip(before,after))if old!=new and not 0x100<=i<0x200 and not 0x2000<=i<0x5c00]
        footprints.update(i for i,_,_ in changes)
        assert changes==[(destination,0xa5,slot)],(mode,slot,occupied,random,flags,changes)
        assert[z[k]for k in ['A','X','Y']]==[85,slot,91]and z['P']&0x7d==flags&0x7d and state==[bytes(v)for v in m.ram]and maps==m.rawtags,(mode,slot,flags,z,[i for i,v in enumerate(state)if v!=bytes(m.ram[i])],maps,m.rawtags)
        cases+=1
    at=W.location(b,'ShellOrBlockDefeat');pc=W.address(b,'ShellOrBlockDefeat')
    assert b['raw'][at:at+3]==bytes([32,W.address(b,'InventoryDropHook')&255,W.address(b,'InventoryDropHook')>>8])
    sources=['src/inventory_drops.s','src/inventory_legacy_leaf.s','src/darkwing_core.s','src/darkwing_pickups.s','src/remaining_weapons.s']
    out=dict(passed=True,ROM_written=False,shared_mutation=False,native_owner_admitted=False,historical_v65_model_only=True,
        actual_current_drop_hook_cases=cases,sole_observable_nonstack_write=dict(name='InvDropEnemy',address=destination,value='incomingX0..5'),minimum_direct_hook_SP=minimum,
        hook_flag_scope='Standalone outer farcall may publish NZ from restoredA. Native ShellOrBlockDefeat immediately loads EnemyID and CMPs PiranhaPlant, overwriting NZC before any use; exact whole-service AXYP differential still required.',
        proposed_private_service=dict(owner=40,prelude='STX InvDropEnemy',genuine_native_target=pc+3,physical_PRG=(at-16)//8192,source_owner='Native ShellOrBlockDefeat immediately after its InventoryDropHook call',source_next8=b['raw'][at+3:at+11].hex()),
        source_path='Owner40 cannot be classic/MM/Bass/Darkwing/Samus/Link/Sophia/Ryu/Simon; the exact native eligibility chain always rejects before probability/cap/spawn, retaining only InvDropEnemy. The standalone native hook must remain unchanged for all foreign owners.',
        scope='Exact current native hook footprint in legal isolated CPU states, plus bound native continuation preimage. A private adapter may specialize this source-proven rejection to avoid the nested generic drop call chain; it still requires full Main/IRQ/ABI qualification before use.',
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in [Path(__file__),Path(F.__file__),A.BASE]+[R/n for n in sources]})
    (O/'native-drop-boundary-v44.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k]for k in ['passed','actual_current_drop_hook_cases','minimum_direct_hook_SP','proposed_private_service']}))


if __name__=='__main__':main()
