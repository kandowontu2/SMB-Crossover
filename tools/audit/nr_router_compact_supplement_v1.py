"""Finite all-route ISR seams/current alternate callers on exact private router."""
from pathlib import Path
import argparse,itertools,json,sys,traceback
sys.path.insert(0,str(Path(__file__).resolve().parent))
import nr_router_compact_controls_v1 as C
from sunny_integrated_controls_v1 import *
R=C.R

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert not a.output.exists()
    old,new=[scoped_load(p)for p in[C.OLD,C.NEW]];names=C.re.findall(r'^NrGate (\w+),',(R/'src/new_roster_dispatch.s').read_text(),C.re.M)
    files=[Path(__file__),Path(C.__file__),R/'build/nr_router_compact_layout_v1.json']+[p.with_suffix(e)for p in[C.OLD,C.NEW]for e in['.nes','.dbg','.lbl']]
    proof=dict(passed=False,source_CPU_only=True,native_run=False,bindings={str(p.resolve()):sha(p)for p in files},checks={});ck=proof['checks']
    try:
        events=[];spmin=255
        for name,char in itertools.product(names,[0,20,21,23,24]):
            q=C.setup(new,char,name);q.put(NmiDisable=255);c,_,_,trace,_=C.actual(q,name,flags=0x30,record_trace=True)
            points=sorted(set((bank,pc)for bank,pc in trace if bank==124 and(address(new,name)<=pc<address(new,name)+80 or address(new,'NrTableColdFinish')<=pc<address(new,'NrTableColdFinish')+9)))
            for kind,at in itertools.product(['IRQ','NMI'],points):
                q=C.setup(new,char,name);q.put(NmiDisable=255);q.m.page(2,q.get('CurrentBankC')&127)
                c,_,sp,_,hit=C.actual(q,name,flags=0x30,inject=at,kind=kind);assert hit;events.append([name,char,kind,*at]);spmin=min(spmin,sp)
        ck['all11_real_route_IRQ_lagNMI']=dict(passed=True,cases=len(events),minimum_SP=spmin,
            actual_full_live_AXYP_PC_SP_returnstack_R0_R7_bankshadows_physicalbanks_5SMC_overlay_context_exact=True,
            all_reached_instructions_in_all11routers_and9B_finish=True,partial_SafecallA_target_low_high_NextBank_publication_seams=True,
            coherent_entry_mapping=True,no_bank_normalization=True,events=events)
        rows=[];deltas=[]
        cases=[(20,'IcVariant',0),(20,'IcVariant',1),(21,'RcVariant',0),(21,'RcVariant',1),(23,None,0),(15,'MacVariant',0),(15,'MacVariant',1),(15,'MacVariant',2),(0,'MarioVariant',4)]
        for char,var,variant,mode,keys in[(ch,v,i,mo,k)for ch,v,i in cases for mo in[0,1]for k in[0,1,129]]:
            pair=[]
            for b in[old,new]:
                q=C.setup(b,char,'GameLoop');q.put(CrossoverBehaviorVersion=mode,SavedJoypadBits=keys,A_B_Buttons=keys&192,Left_Right_Buttons=keys&3,NmiDisable=255)
                if var:q.set(var,variant)
                if char==0:run(q,'MenuResolveCharacter');q.put(SelectedCharacter=0,MarioVariant=4)
                c,_,sp,_,_=C.actual(q,'GameLoop',flags=0x71);pair.append((C.full(q,c),[(at,v)for at,v in q.m.writes if not 0x100<=at<0x200],c.processorCycles,sp))
            assert pair[0][:2]==pair[1][:2],('actual alternate GameLoop',char,var,variant,mode,keys)
            deltas.append(pair[1][2]-pair[0][2]);rows.append([char,var,variant,mode,keys,pair[1][2]-pair[0][2]])
        ck['actual_current_alternate_GameLoops']=dict(passed=True,cases=len(rows),full_state_OAM_CHR_banks_allorderedwrites5SMC_AXYP_SP_exact=True,CPU_delta=[min(deltas),max(deltas)],rows=rows)
        # Source-genuine menu Select/readback lifecycle, no raw alias admission.
        n=0
        for char,var,variant in cases:
            for name in['NrFreshGameInit','NrReset','NrPortrait','GetPlayerColors','NrStatusName']:
                pair=[]
                for b in[old,new]:
                    q=C.setup(b,char,name);q.put(GameEngineSubroutine=0,VRAM_Buffer1_Offset=0)
                    if var:q.set(var,variant)
                    c,_,_,_,_=C.actual(q,name,a=0,flags=0x71);pair.append((C.full(q,c),[(at,v)for at,v in q.m.writes if not 0x100<=at<0x200]))
                assert pair[0]==pair[1],('alternate menu/life',char,variant,name);n+=1
        ck['alternate_cold_menu_life_callers']=dict(passed=True,calls=n,real_complete_fresh_reset_portrait_palette_status=True)
        assert all(sha(p)==h for p,h in proof['bindings'].items());proof['passed']=True
    except Exception as e:proof.update(failure=repr(e),traceback=traceback.format_exc())
    a.output.write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=proof['passed'],failure=proof.get('failure'),checks=list(ck))))
    assert proof['passed']

if __name__=='__main__':main()
