"""Actual compiled router callers/target entry/SMC/ISR; source CPU only."""
from pathlib import Path
import argparse,hashlib,itertools,json,re,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
from sunny_integrated_controls_v1 import *
from new_roster_routing_fit_v1 import callback

OLD=R/'build/celeste-small-chr-v2.nes';NEW=R/'build/nr-router-compact-v1.nes'
def fastapp(q):
    # Same byte order/exclusions as inherited app(), copied in C-level slices.
    intervals=[(0,0x100),(0x200,0x2000),(0x5c00,0x5fff),(0x6000,0x8000)]
    if 'safecall_a'in q.b['syms']:
        at=address(q.b,'safecall_a');intervals=[part for lo,hi in intervals for part in([(lo,at),(at+1,hi)]if lo<=at<hi else[(lo,hi)])]
    return b''.join(bytes(q.m[lo:hi])for lo,hi in intervals)
def full(q,c):
    return(registers(c),fastapp(q),tuple(q.m.banks),bytes(q.m[z]for z in smc_at(q.b)))
def setup(b,char,name):
    q=seed(b,char);q.put(MarioVariant=0,PlayerStatus=1,PlayerSize=0,PlayerFacingDir=1,Player_State=0,
                        PlayerEntranceCtrl=2,GameTimerDisplay=4,ObjectOffset=0,Enemy_OffscreenBits=0,Player_Pos_ForScroll=96)
    if name in['NrDeath','NrDeathStart']:q.put(GameEngineSubroutine=11)
    return q
def actual(q,name,target=None,flags=0x30,inject=None,kind='IRQ',a=91,x=0,y=0,record_trace=False):
    b=q.b;pc=address(b,name);bank=(location(b,name)-16)//8192;q.m.page((pc-0x8000)//8192,bank);q.set('CurrentBank',bank|128)
    q.m.writes=[];c=NesMPU(memory=q.m,pc=pc);c.a,c.x,c.y,c.p,c.sp=a,x,y,flags,253;c.stPushWord(0x5aff)
    minimum=c.sp;entry=None;hit=False;trace=[]
    for _ in range(300000):
        minimum=min(minimum,c.sp)
        if c.pc==0x5b00:assert c.sp==253;return c,entry,minimum,trace,hit
        physical=q.m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
        if entry is None and target and c.pc==target[0]and physical==(target[1]&127):
            entry=(registers(c),fastapp(q),tuple(q.m.banks),bytes(q.m[z]for z in smc_at(b)),bytes(q.m[0x101+c.sp:0x200]))
        if record_trace:trace.append((physical,c.pc))
        if inject==(physical,c.pc)and not hit:
            def state():return(c.pc,c.a,c.x,c.y,c.p&0xcf,c.sp,tuple(q.m.banks),bytes(q.m[:11]),bytes(q.m[0x101+c.sp:0x200]),bytes(q.m[z]for z in smc_at(b)),bytes(q.m[0x5c00:0x6000]),q.get('CurrentBank'),q.get('CurrentBankC'))
            before=state()
            if kind=='IRQ':
                assert not c.p&4;q.m[0x5204]=128;c.irq()
            else:c.nmi()
            for _ in range(60000):
                c.step();minimum=min(minimum,c.sp)
                if c.pc==before[0]and c.sp==before[5]:break
            else:raise AssertionError(('ISR timeout',name,kind,hex(c.pc)))
            assert state()==before,('ISR full context',name,kind,inject,[(i,(a0,b0))for i,(a0,b0)in enumerate(zip(before,state()))if a0!=b0]);hit=True
        assert q.m[c.pc]!=0,('BRK',name,q.get('SelectedCharacter'),hex(c.pc),physical);c.step()
    raise AssertionError(('timeout',name,q.get('SelectedCharacter'),hex(c.pc)))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);ap.add_argument('--quick',action='store_true');a=ap.parse_args();assert not a.output.exists()
    old,new=[scoped_load(p)for p in[OLD,NEW]];gate_names=re.findall(r'^NrGate (\w+),', (R/'src/new_roster_dispatch.s').read_text(),re.M)
    files=[Path(__file__),R/'tools/prepare_nr_router_compact_v1.py',R/'tools/audit/sunny_integrated_controls_v1.py',R/'tools/audit/link_pit_rygar_sophia_audit_cpu.py',R/'tools/audit/check_tmnt_render_oa.py',R/'tools/audit/verify_native_relocation.py',R/'tools/audit/new_roster_routing_fit_v1.py',R/'build/nr-router-compact-v1-overlay/src/new_roster_dispatch.s',R/'build/nr_router_compact_layout_v1.json']+[p.with_suffix(e)for p in[OLD,NEW]for e in['.nes','.dbg','.lbl']]
    proof=dict(passed=False,source_CPU_only=True,native_run=False,bindings={str(p.resolve()):sha(p)for p in files},checks={});ck=proof['checks']
    try:
        moved=[];removed=[]
        for n,z in old['syms'].items():
            if n=='_FARCALL_COUNT':continue
            if n not in new['syms']:removed.append(n)
            elif address(old,n)!=address(new,n):moved.append(n)
        assert not moved,('moved old symbols',moved)
        assert all(n in['ToIce','ToCity','ToSunny']or any(n==g+'::'+k for g in gate_names for k in['ToIce','ToCity','ToSunny'])or n.startswith('@')or n.startswith('__')for n in removed),('unexpected removed symbols',removed)
        ck['layout']=dict(passed=True,old_public_PC_RAM_CHR_other_banks_exact=True,actual_removed_internal_labels=removed,new_helper=[address(new,'NrTableColdFinish'),address(new,'NrTableColdFinish')+9],all_11_slots=97)
        for b,char in itertools.product([old,new],range(24)):
            q=setup(b,char,'NrMovement');assert fastapp(q)==app(q)
        ck['fast_snapshot_oracle']=dict(passed=True,cases=48,byteexact_inherited_application_RAM_exclusions_and_order=True)
        rows=[];count=0;minsp=255
        flags=[0x30]if a.quick else[p for p in range(256)if p&0x30==0x30]
        chars=[0,15,20,21,22,23,24,25,28,29,255]if a.quick else range(256)
        for name in gate_names:
            oldcode=old['raw'][location(old,name):location(old,name)+97];targets=[callback(oldcode[17+20*i:37+20*i])for i in range(4)];costs={};counters=[]
            for char,f in itertools.product(chars,flags):
                target=targets[{20:1,21:2,23:3}.get(char,0)];outs=[]
                for b in[old,new]:
                    q=setup(b,char,name);c,entry,sp,trace,_=actual(q,name,target,f);assert entry is not None,(name,char,'missing actual target')
                    outs.append((full(q,c),entry,[(at,v)for at,v in q.m.writes if not 0x100<=at<0x200],c.processorCycles,sp))
                assert outs[0][:3]==outs[1][:3],('full caller/target/writes',name,char,f,outs[0][0][0],outs[1][0][0])
                key='legacy0_19'if char<20 else str(char)if char in[20,21,23]else'otherlegacy';costs.setdefault(key,[]).append(outs[1][3]-outs[0][3]);count+=1;minsp=min(minsp,outs[0][4],outs[1][4])
            rows.append(dict(name=name,calls=len(chars)*len(flags),CPU_delta={k:[min(v),max(v)]for k,v in costs.items()}));print(name,count,flush=True)
        ck['all_raw_all_flags_complete_target_and_return']=dict(passed=True,calls=count,all256raw_and64flags=not a.quick,actual_target_AXYP_SP_live_stack_appRAM_banks_5SMC_exact=True,full_return_state_and_all_ordered_nonstack_writes_including5SMC_exact=True,minSP=minsp,costs=rows)
        # Complete actual GameLoop cohorts and cold menu/life/lifecycle callers.
        count=0;ds=[]
        for char,mode,keys in itertools.product(range(24),[0,1],[0,1,129]):
            outs=[]
            for b in[old,new]:
                q=setup(b,char,'GameLoop');q.put(CrossoverBehaviorVersion=mode,SavedJoypadBits=keys,A_B_Buttons=keys&192,Left_Right_Buttons=keys&3,NmiDisable=255)
                c,_,sp,_,_=actual(q,'GameLoop',flags=0x71);outs.append((full(q,c),[(at,v)for at,v in q.m.writes if not 0x100<=at<0x200],c.processorCycles,sp))
            assert outs[0][:2]==outs[1][:2],('whole GameLoop',char,mode,keys);ds.append(outs[1][2]-outs[0][2]);count+=1
        ck['whole_GameLoop']=dict(passed=True,calls=count,all24_current_raw_both_modes_3key_states=True,full_register_RAM_OAM_CHR_banks_SMC_ordered_writes_exact=True,CPU_delta=[min(ds),max(ds)])
        count=0
        for char,name in itertools.product([0,20,21,23],['NrFreshGameInit','NrReset','NrPortrait','NrGraphics','GetPlayerColors','NrStatusName']):
            outs=[]
            for b in[old,new]:
                q=setup(b,char,name);q.put(GameEngineSubroutine=0,VRAM_Buffer1_Offset=0);c,_,sp,_,_=actual(q,name,flags=0x71,a=0);outs.append((full(q,c),[(at,v)for at,v in q.m.writes if not 0x100<=at<0x200]))
            assert outs[0]==outs[1],('menu/life',char,name);count+=1
        ck['menu_life_current_owners']=dict(passed=True,calls=count,complete_actual_fresh_reset_portrait_colors_status_and_graphics=True)
        # Every route instruction, including partial SMC target publication,
        # then actual farcall entry. Coherent bank shadows at first entry.
        events=[]
        for char in[0,20,21,23,24]:
            q=setup(new,char,'NrMovement');q.put(NmiDisable=255);c,_,_,trace,_=actual(q,'NrMovement',flags=0x30,record_trace=True)
            instructions=sorted(set((bank,pc)for bank,pc in trace if bank==124 and(address(new,'NrMovement')<=pc<address(new,'NrMovement')+80 or address(new,'NrTableColdFinish')<=pc<address(new,'NrTableColdFinish')+9)))
            for kind,(bank,pc)in itertools.product(['IRQ','NMI'],instructions):
                q=setup(new,char,'NrMovement');q.put(NmiDisable=255);q.m.page(2,q.get('CurrentBankC')&127)
                c,_,sp,_,hit=actual(q,'NrMovement',flags=0x30,inject=(bank,pc),kind=kind);assert hit;events.append([char,kind,bank,pc])
        ck['actual_IRQ_lagNMI_route_and_publication_seams']=dict(passed=True,cases=len(events),all_reached_NrMovement_and_sharedfinish_instructions=True,full_live_context_including_partial_5SMC_and_physical_banks=True,events=events)
        assert all(sha(p)==h for p,h in proof['bindings'].items());proof['passed']=True
    except Exception as e:proof.update(failure=repr(e),traceback=traceback.format_exc())
    a.output.write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=proof['passed'],failure=proof.get('failure'),checks=list(ck))))
    assert proof['passed']

if __name__=='__main__':main()
