"""Compare real existing menu Start flows and the private pending helper."""
from pathlib import Path
import itertools,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import prepare_metal_storm_menu_pending_1101_v14 as P
import check_hogan_current_bounded_v1 as M
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
def main():
    s=json.loads((P.O/'menu-assembly.json').read_text())
    for p,h in s['bindings'].items():assert P.sha(p)==h,p
    old=scoped_load(P.P/'candidate.nes');new=dict(old,raw=(P.O/'candidate.nes').read_bytes(),syms=dict(old['syms']))
    new['syms']['Ms14PlayablePending']=dict(old['syms']['FmStartFlags'],val=hex(s['helper_PC']))
    counts=[8,2,2,2,2,4,2,2,2,3,3,2,2,2,3,1,4,4,4,2,2,4,1,2,8,1,2,1,6,2,4,2]
    a=M.fresh(old);b=M.fresh(new);identities=starts=0
    omit=set(range(0x100,0x200))|set(range(0x2000,0x5c00))|set(range(address(old,'R0'),address(old,'R0')+8))|{address(old,n) for n in ['CurrentBank','CurrentBankC','safecall_a']}
    def state(m):return bytes(v for i,v in enumerate(m[:0x8000]) if i not in omit),[bytes(r) for r in m.ram]
    for slot,count in enumerate(counts):
        left=M.fork(a);right=M.fork(b)
        for m in [left,right]:M.put(m,CrossoverMenuIndex=slot);M.invoke(m,'MenuResolveCharacter');M.invoke(m,'QueueSelection')
        for variant in range(count):
            if variant:
                for m in [left,right]:M.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0);M.invoke(m,'CrossoverMenuInput')
            assert state(left)==state(right),(slot,variant,'selection')
            l=M.fork(left);r=M.fork(right)
            x=M.invoke(l,'FmPending');y=M.invoke(r,'Ms14PlayablePending')
            assert (x['A'],x['X'],x['Y'])==(y['A'],y['X'],y['Y'])
            expected=0 if slot==11 and variant==1 else x['P']&1
            assert y['P']&1==expected,(slot,variant,x,y)
            for button,flags in itertools.product([16,128],[0x30,0x31,0x71,0xf9]):
                x=M.fork(left);y=M.fork(right)
                for m in [x,y]:M.put(m,CrossoverMenuButtons=0,SavedJoypad1Bits=button,SavedJoypad2Bits=0,VRAM_Buffer1_Offset=0);M.invoke(m,'CrossoverMenuInput',p=flags)
                assert state(x)==state(y),(slot,variant,button,flags,'Start')
                starts+=1
            identities+=1
    assert identities==91 and starts==728
    q=dict(passed=True,ROM_sha256=s['ROM_sha256'],menu_identities=identities,unchanged_existing_Start_cases=starts,
           helper_only_new_admission='Slot11 alternate1, Metal Storm; all other pending carry results and A/X/Y preserved.',
           helper_wired=False,installed=False,scope='Private helper is tested but deliberately not connected to resolver/Start until retirement and identity handling are complete.')
    (P.O/'menu-CPU.json').write_text(json.dumps(q,indent=2)+'\n')
    d=R/'docs/qa/checkpoints/2026-11-01/metal-storm-menu-v14';d.mkdir(exist_ok=True)
    (d/'receipt.json').write_text(json.dumps(q,indent=2)+'\n')
    (d/'assembly.json').write_text(json.dumps(s,indent=2)+'\n')
    path=R/'docs/qa/continuation-current.json';c=json.loads(path.read_text())
    c['previous_goal_turn_classification']='progress'
    c['metal_storm_menu_followup']=dict(checkpoint=str(d.relative_to(R)),candidate=str(P.O/'candidate.nes'),
        helper_PC=s['helper_PC'],helper_bank=s['helper_bank'],helper_wired=False,
        next='Cold FmPending must keep atlas dispatch. The new13B helper may be used only by playable resolver/Start after mapping slot11/FmAlts2 to raw35 and retiring complete Metal headers on exit. KrStartFlags still only preserves Karnov; Metal needs its own retained bit. Existing Metal scene reset consumed prior work/copy slack, so do not reuse the old63-byte allocation plan.')
    path.write_text(json.dumps(c,indent=2)+'\n')
    print(json.dumps(q))
if __name__=='__main__':main()

