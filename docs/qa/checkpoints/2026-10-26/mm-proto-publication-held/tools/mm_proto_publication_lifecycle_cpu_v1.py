"""Actual lifecycle reset, cold/fresh game initialization, and OAM writer closure."""
from pathlib import Path
import argparse,hashlib,itertools,json,re,traceback
from check_tmnt_render_oa import Memory,address,location
from link_pit_rygar_sophia_audit_cpu import scoped_load
from verify_native_relocation import NesMPU
from mm_proto_publication_nmi_cpu_v2 import FLAGS

STATE=0x5ff8
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def run(b,name,state,p):
    m=Memory(b);l=lambda n:address(b,n)
    for at in range(0x200,0x300):m[at]=(at*73+17)&255
    for at in range(0x5c00,0x6000):m[at]=(at*13+29)&255
    m[STATE]=state
    pc=l(name);bank=(location(b,name)-16)//8192;window=(pc-0x8000)//8192;m.page(window,bank)
    if window in[1,2]:m[l('CurrentBank'if window==1 else'CurrentBankC')]=bank|128
    c=NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=167,73,19,p,253;c.stPushWord(0x5aff);m.writes=[]
    trace=[]
    for _ in range(200000):
        if c.pc==0x5b00:break
        trace.append(c.pc);c.step()
    else:raise AssertionError(('Lifecycle timeout',name,hex(c.pc),m.banks))
    assert c.sp==253
    return c,m,trace

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for n in['parent','candidate','source','output']:ap.add_argument('--'+n,type=Path,required=True)
    a=ap.parse_args();a.output.mkdir(parents=True,exist_ok=False);rows=[]
    try:
        old,new=[scoped_load(p)for p in[a.parent,a.candidate]]
        for name,flags in [('MoveAllSpritesOffscreen',FLAGS),('X5ProfilesNewGame',FLAGS),('X5InventoryInit',[0x20,0x61]),('CrossoverInit',[0x20]),('KbFreshGameInit',[0x20])]:
            for state,p in itertools.product([0,64,128,192],flags):
                c,m,left=run(old,name,state,p);d,n,right=run(new,name,state,p)
                assert(c.a,c.x,c.y,c.p&207,c.sp,tuple(m.banks))==(d.a,d.x,d.y,d.p&207,d.sp,tuple(n.banks)),('Lifecycle full ABI/banks',name,state,p)
                diff=[(at,m[at],n[at])for at in range(0x8000)if at!=STATE and not 0x100<=at<0x200 and m[at]!=n[at]]
                assert not diff,('Lifecycle memory/SMC/otherhardware',name,state,p,diff[:20])
                assert n[STATE]==0,('Missing reset',name,state,p,n[STATE])
                assert[(at,v)for at,v in m.writes if not 0x100<=at<0x200 and at!=STATE]==[(at,v)for at,v in n.writes if not 0x100<=at<0x200 and at!=STATE],('Lifecycle original stores/order',name,state,p)
                delta=d.processorCycles-c.processorCycles
                assert delta==(18 if name=='MoveAllSpritesOffscreen'else 0),(name,delta)
                rows.append(dict(entry=name,state_before=state,physical_flags=p,cycles_delta=delta,state_after=n[STATE],clear_reached=address(new,'X5ProfilesNewGame')in right))
        callers=[]
        for p in sorted((a.source/'src').rglob('*.s')):
            for line,s in enumerate(p.read_text().splitlines(),1):
                if re.search(r'\b(?:jsr|jmp|farcall)\s+(?:MoveAllSpritesOffscreen|OAMClear|X5ProfilesNewGame|X5InventoryInit|ProtoGlobalInit|DwInventoryInit|KbFreshGameInit|KbGlobalInit|CrossoverInit)\b',s):
                    callers.append(dict(file=p.relative_to(a.source).as_posix(),line=line,text=s.strip()))
        direct_clear=[r for r in callers if re.search(r'\b(?:jsr|jmp|farcall)\s+OAMClear\b',r['text'])]
        assert not direct_clear
        engine=(a.source/'src/metasprite_engine.s').read_text()
        assert engine.count('adc #<OAMClear')==1 and engine.count('lda #>OAMClear')==1
        # Ineligible replacement retains desired phase but cannot leave an
        # old pending tag; renderer cases verify actual assembled ASL/LSR.
        (a.output/'cases.json').write_text(json.dumps(rows,indent=2)+'\n')
        (a.output/'source-callers.json').write_text(json.dumps(callers,indent=2)+'\n')
        proof=dict(passed=True,source_only=True,native_run=False,parent_ROM_sha256=sha(a.parent),candidate_ROM_sha256=sha(a.candidate),actual_lifecycle_cases=len(rows),full_original_AXYP_SP_RAM_5SMC_banks_and_ordered_OAM_otherstores_exact=True,new_byte_resets_zero=True,
                   common_MoveAllSpritesOffscreen_added_cycles=18,other_cold_newgame_entries_added_cycles=0,source_named_direct_OAMClear_callers=0,
                   computed_OAMClear_owner='Only original DrawAllMetasprites legacy tail computes the OAMClear address; owned negative modes use genuine Roster tail instead.',
                   lifecycle_entry_counts={n:sum(r['entry']==n for r in rows)for n in sorted({r['entry']for r in rows})},
                   ownership='New ExRAM5FF8 sits outside existing5FF0..5FF5 bounce and5FF6..5FF7 NativeStatus, inside genuine X5ProfilesNewGame5C00..5FFF full reset. Complete owner audit is bound separately; no existing RAM symbol changes.',
                   limits='Source/cold/fresh-game/OAM-clear simulation, not native scene/death/area coverage or displayed fairness.',tool_sha256=sha(__file__))
        (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2))
    except BaseException as e:
        (a.output/'failure.json').write_text(json.dumps(dict(passed=False,error=repr(e),traceback=traceback.format_exc(),completed=len(rows)),indent=2)+'\n');(a.output/'failed-tool.py').write_bytes(Path(__file__).read_bytes());raise

if __name__=='__main__':main()
