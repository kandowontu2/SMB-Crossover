"""Prove existing Select-before-confirm ordering and bind a distinct observer."""
from pathlib import Path
import sys,json,copy,argparse
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import audit_bub_menu_frontend_1102_v1 as F
import prepare_bub_menu_qualification_1102_v2 as N
M=F.M;O=N.O;W=O/'ordered-input-v3';PIN='90a7108003343ad9f5f9719f860f44f09d1e1932194d5eac1c89bc473e932dd8'
sha=F.sha

def expected(bob):
    name=[36]*16;name[6:9]=[11,24 if bob else 30,11]
    return name,[44,35,48]if bob else[42,38,48]

def queued(m,bob):
    commands=F.commands(m);name,pal=expected(bob)
    assert [p['bytes']for p in commands if p['address']==0x2328][-1]==name
    assert [p['bytes']for p in commands if p['address']==0x3f11][-1]==pal
    assert M.get(m,'SelectedCharacter')==39 and M.get(m,'FmGroups')&128==bob*128 and M.get(m,'CrossoverMenuState')==2
    return dict(name=name,palette=pal,OAM=list(m[0x200:0x210]))

def prove():
    W.mkdir(exist_ok=True);rom=O/'candidate.nes';assert sha(rom)==PIN
    b=F.scoped_load(rom);seed=M.fresh(b);cases=[];deferred=[]
    source=R/'tools/reference/menu_input_1101_v3.inc';text=source.read_text()
    clause='lda #$20\n sta CrossoverMenuPressed\n jsr CrossoverMenuInput::CheckDirection\n pla\n sta CrossoverMenuPressed'
    assert clause in text
    # Bind the actual current107B worker, including its native masked-Select
    # call. Its literal target is the unchanged public CheckDirection A85C.
    raw=b['raw'];worker=raw[16+66*8192+0x10c0:16+66*8192+0x10c0+107]
    assert bytes.fromhex('a9208d0873205ca8688d0873')in worker
    for bob in[0,1]:
        for keys in[48,160,176]:
            m=M.fork(seed);M.put(m,CrossoverMenuIndex=32,FmGroups=bob*128)
            F.invoke(m,'MenuResolveCharacter');F.invoke(m,'QueueSelection')
            M.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=keys,SavedJoypad2Bits=0)
            trace=[]
            def watch(c):
                if c.pc in[0xa85c,0xad39,0xaa14,0xa7e3,0xad5d,0xa7fc]and c.memory.rawtags[1]==194:
                    trace.append(dict(PC=c.pc,pressed=M.get(c.memory,'CrossoverMenuPressed'),groups=M.get(c.memory,'FmGroups'),A=c.a,X=c.x,P=c.p))
            F.invoke(m,'CrossoverMenuInput',watch=watch);ui=queued(m,1-bob)
            first=next(x for x in trace if x['PC']==0xad39);confirm=next(x for x in trace if x['PC']==0xad5d)
            assert first['pressed']==32 and first['groups']==bob*128
            assert confirm['pressed']==keys and confirm['groups']==(1-bob)*128
            cases.append(dict(initial_Bob=bob,input=keys,result_Bob=1-bob,actual_ordered_trace=trace,queued_UI=ui,confirmation_blocked=True))
    for bob in[0,1]:
        for continue_mode in[0,128]:
            for keys in[32,160]:
                m=M.fork(seed);M.put(m,CrossoverMenuIndex=32,FmGroups=bob*128,CrossoverContinue=continue_mode,CrossoverMenuState=1,
                    DisableScreenFlag=1,Mirror_PPUMASK=0,CrossoverMenuButtons=0,SavedJoypad1Bits=keys,SavedJoypad2Bits=0)
                F.invoke(m,'CrossoverMenuInput')
                assert M.get(m,'CrossoverMenuState')==2 and M.get(m,'CrossoverContinue')==continue_mode+1 and M.get(m,'FmGroups')==bob*128
                M.put(m,VRAM_Buffer1_Offset=0,SavedJoypad1Bits=0)
                F.invoke(m,'CrossoverMenuInput');ui=queued(m,1-bob)
                assert M.get(m,'CrossoverContinue')==continue_mode
                M.put(m,VRAM_Buffer1_Offset=0);F.invoke(m,'CrossoverMenuInput')
                assert M.get(m,'FmGroups')==(1-bob)*128 and not F.commands(m),'Deferred Select must execute exactly once'
                deferred.append(dict(initial_Bob=bob,continue_mode=continue_mode,state1_input=keys,result_Bob=1-bob,queued_UI=ui,exactly_one_deferred_toggle=True))
    negative=O/'native-menu2/capture';terminal=json.loads((negative/'binding.json').read_text());assert terminal['exit_code']==1
    log=(negative/'candidate-controller.log').read_text(errors='replace');assert 'Actual name new-blocked-select+a byte8 actual30 expected24'in log
    observations=(negative/'observations.csv').read_text();assert '2020,new-blocked-start,2,32,39,128,'in observations
    q=dict(passed=True,ROM_SHA256=PIN,ROM_changed=False,observer_correction_only=True,native_pass=False,
        actual_existing_policy='MnMenuEdges intentionally consumes masked Select through native CheckDirection, then restores full input and performs confirm. Simultaneous Select+confirm selects the next alternate before a launch or blocked confirmation.',
        CPU_ordered_cases=cases,deferred_state1_cases=deferred,negative_scope='Native-menu2 reached actual Bob UI, then observer expected Bob after Select+A. Ordered original input instead selects Bub; queued source name/palette/OAM agree. This is an incorrect observer expectation, not evidence of stale UI or an actor-source defect.',
        bindings={p.relative_to(R).as_posix():sha(p)for p in[Path(__file__),rom,source,negative/'binding.json',negative/'candidate-controller.log',negative/'observations.csv',O/'metadata-repair.json']})
    receipt=W/'CPU-ordered-input.json';receipt.write_text(json.dumps(q,indent=2)+'\n');return receipt

def revised(original):
    q=original()
    for mode in['browse-blocked','browse-admitted']:
        bob=1
        for s in q[mode]['steps']:
            if s['tag']=='new-blocked-select+a':bob=0
            elif s['tag']=='new-blocked-select+start':bob=1
            if s['tag'].startswith('new-blocked-'):
                s['variant']=s['bob']=bob;s['name']=expected(bob)[0]
        q[mode]['scope']+=' Existing simultaneous Select+confirm applies Select first; source RGB/name/CHR/DMA checks remain exact.'
    # For each desired post-Select launch identity, start on its predecessor.
    # This keeps the original real policy rather than changing ROM priority.
    for mode in['bob-start','bt-start','cf-start']:
        route=q[mode]['steps'];assert route[-2]['keys']==['select'];del route[-2]
    route=q['bub-start']['steps'];pre=copy.deepcopy(route[-2]);pre.update(keys=['select'],variant=1,bob=1,name=expected(1)[0],tag='Bob-before-simultaneous-Select-to-Bub');route.insert(-1,pre)
    return q

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--prepare',choices=N.MODES,default='browse-blocked');a=ap.parse_args()
    receipt=prove();original_plans=N.plans;original_prepare=N.prepare;original_output=N.O
    N.plans=lambda:revised(original_plans);N.O=W
    def prepare(output,rom,controller,refs,**kw):
        refs={p for p in refs if p.name!='candidate.json'}|{receipt,Path(__file__),O/'metadata-repair.json'}
        destination=O/('native-menu3'if a.prepare=='browse-blocked'else'native-ordered-'+a.prepare)
        kw['scope']='Ordered-input observer successor; unchanged90a710 ROM. '+kw['scope']
        return original_prepare(destination,rom,controller,refs,**kw)
    N.prepare=prepare;sys.argv=[str(Path(N.__file__)),'--prepare',a.prepare,'--rom',str(O/'candidate.nes'),'--sha256',PIN]
    try:N.main()
    finally:N.plans=original_plans;N.prepare=original_prepare;N.O=original_output
    print(json.dumps(dict(passed=True,ROM_changed=False,ordered_input_cases=6,deferred_state1_cases=8,prepared=a.prepare)))
if __name__=='__main__':main()
