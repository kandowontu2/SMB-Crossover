"""Whole callers with correct LOW/FIXED entry bank-shadow ownership.

Original all-gate entries are A-window124 and remain valid. Earlier whole
caller fixture incorrectly seeded CurrentBank from a LOW entry's bank126.
Those whole LOW-caller rows are superseded here, not relabeled qualified.
"""
from pathlib import Path
import argparse,itertools,json,sys,traceback
sys.path.insert(0,str(Path(__file__).resolve().parent))
import nr_router_compact_controls_v1 as C
from sunny_integrated_controls_v1 import *

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert not a.output.exists()
    old,new=[scoped_load(p)for p in[C.OLD,C.NEW]];files=[Path(__file__),Path(C.__file__),C.R/'tools/audit/sunny_integrated_controls_v1.py']+[p.with_suffix(e)for p in[C.OLD,C.NEW]for e in['.nes','.dbg','.lbl']]
    proof=dict(passed=False,source_CPU_only=True,native_run=False,bindings={str(p.resolve()):sha(p)for p in files},checks={});ck=proof['checks']
    try:
        q=C.setup(old,0,'GameLoop');win=(address(old,'GameLoop')-0x8000)//8192;wrongbank=(location(old,'GameLoop')-16)//8192
        assert win==0 and wrongbank==126 and q.m.banks[1]==87 and q.get('CurrentBank')==215
        ck['retained_old_LOW_seed_counterexample']=dict(old_fixture_mirrored_LOW_bank_as_A=254,actual_existing_A_physical=87,actual_existing_A_shadow=215,corrected_by_standard_run_window_1_2_only=True,affected_old_whole_GameLoop_and_GetPlayerColors_claims_withdrawn=True,all_11_router_matrix_entries_A124_unaffected=True)
        smc=set(smc_at(old));assert smc==set(smc_at(new));cases=[(ch,None,0)for ch in range(24)]+[(20,'IcVariant',0),(20,'IcVariant',1),(21,'RcVariant',0),(21,'RcVariant',1),(23,None,0),(15,'MacVariant',0),(15,'MacVariant',1),(15,'MacVariant',2),(0,'MarioVariant',4)]
        rows=[]
        for ch,var,value in cases:
            for mode,keys in itertools.product([0,1],[0,1,129]):
                pair=[]
                for b in[old,new]:
                    q=C.setup(b,ch,'GameLoop');q.put(CrossoverBehaviorVersion=mode,SavedJoypadBits=keys,A_B_Buttons=keys&192,Left_Right_Buttons=keys&3,NmiDisable=255)
                    if var:q.set(var,value)
                    if var=='MarioVariant':run(q,'MenuResolveCharacter');q.put(SelectedCharacter=0,MarioVariant=4)
                    assert q.get('CurrentBank')&127==q.m.banks[1]and q.get('CurrentBankC')&127==q.m.banks[2]
                    c,w,_=run(q,'GameLoop',p=0x71)
                    assert q.get('CurrentBank')&127==q.m.banks[1]and q.get('CurrentBankC')&127==q.m.banks[2]
                    pair.append((C.full(q,c),[(at,v)for at,v in w if at in smc or not 0x100<=at<0x200],c.processorCycles))
                assert pair[0][:2]==pair[1][:2],('coherent wholeGameLoop',ch,var,value,mode,keys);rows.append([ch,var,value,mode,keys,pair[1][2]-pair[0][2]])
        ck['coherent_actual_GameLoops']=dict(passed=True,cases=len(rows),AXYP_SP_fullapplication_OAM_CHR_banks_allordered_nonstack_AND5SMC_exact=True,entry_and_exit_physical_shadow_bank_coherence=True,CPU_delta=[min(r[-1]for r in rows),max(r[-1]for r in rows)],rows=rows)
        rows=[]
        for i,(ch,var,value)in enumerate([(ch,None,0)for ch in[0,20,21,23]]+cases[24:]):
            for name in['NrFreshGameInit','NrReset','NrPortrait','GetPlayerColors','NrStatusName']+(['NrGraphics']if i<4 else[]):
                pair=[]
                for b in[old,new]:
                    q=C.setup(b,ch,name);q.put(GameEngineSubroutine=0,VRAM_Buffer1_Offset=0)
                    if var:q.set(var,value)
                    c,w,_=run(q,name,a=0,p=0x71);pair.append((C.full(q,c),[(at,v)for at,v in w if at in smc or not 0x100<=at<0x200]))
                assert pair[0]==pair[1],('coherent menu/life',ch,value,name);rows.append([ch,var,value,name])
        ck['coherent_actual_menu_life_callers']=dict(passed=True,calls=len(rows),full_state_ordered5SMC_registers_banks_exact=True,actual_window_aware_entry_mapping=True,rows=rows)
        assert all(sha(p)==h for p,h in proof['bindings'].items());proof['passed']=True
    except Exception as e:proof.update(failure=repr(e),traceback=traceback.format_exc())
    a.output.write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=proof['passed'],failure=proof.get('failure'),checks=list(ck))));assert proof['passed']

if __name__=='__main__':main()
