"""Natural shared Main C93 marker ingress and authentic busy-interval cuts."""
from pathlib import Path
import itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_fx_world_marker_controls_v3 as B
import ff_fx_world_marker_main_v1 as W
from ff_wram_host_isr_v4 import clone
K=B.K;H,M,T=K.H,K.M,K.T;V=W.V;address=K.address
O=K.O;P=K.P
scene=W.scene

def full_main(old,new):
    rows=[]
    for variant,off,skip in itertools.product(range(4),[0,1],[0,1]):
        memories=[scene(b,variant,off,skip)for b in[old,new]]
        for tick in range(4):
            results=[]
            for m in memories:
                H.put(m,SavedJoypadBits=0,A_B_Buttons=0,Left_Right_Buttons=0,
                    NmiDisable=255,VRAM_Buffer1_Offset=0)
                entries=[];tagged=set()
                gate=address(m.bundle,'FwNativeFlashProbe')
                store=address(m.bundle,'FfMuxWorldDraw::Tag')+5 if'FfMuxWorldDraw'in m.bundle['syms']else-1
                def observer(mem,c,i):
                    if c.pc==gate and mem.rawtags[1]==(((K.location(mem.bundle,'FwNativeFlashProbe')-16)//8192)|128):entries.append([mem.rawtags[1],mem.rawtags[2],c.y])
                    if c.pc==store and mem.rawtags[2]==221:tagged.add(len(mem.writes))
                m.writes.clear();m.ram_writes.clear()
                c,low=M.invoke_main(m,observer)
                exclude=set(range(0x100,0x200))
                app=bytes((m[a]&239 if 512<=a<768 and a%4==2 else m[a])for a in range(0x8000)if a not in exclude)
                ordered=[(a,v&239 if 512<=a<768 and a%4==2 else v)for i,(a,v)in enumerate(m.writes)if a not in exclude and i not in tagged]
                results.append(dict(reg=(c.a,c.x,c.y,c.p,c.sp),state=app,ordered=ordered,
                    CPU=c.processorCycles,low=low,entries=entries,tagged=len(tagged)))
            a,z=results
            assert a['reg']==z['reg'] and a['state']==z['state']
            assert a['ordered']==z['ordered']
            assert a['entries']==z['entries']
            assert all(rawA==132 and rawC==221 and 1<=y<=6 for rawA,rawC,y in z['entries'])
            if not skip:assert z['entries'],(variant,off,skip,tick)
            rows.append(dict(variant=variant,outlines_off=off,skip=skip,tick=tick,
                native_probe_entries=z['entries'],tagged_parts=z['tagged'],
                extra_CPU=z['CPU']-a['CPU'],minimum_SP=z['low']))
    return dict(pairs=len(rows),rows=rows,actual_Main_source_and_native_DrawAll_hooks=True,
        all_genuine_FF_probe_ingress_C93=True,all_original_outputs_and_ordered_application_writes_except_metadata_exact=True,
        extra_CPU=[min(r['extra_CPU']for r in rows),max(r['extra_CPU']for r in rows)])



def actual_vectors(new):
    m=W.scene(new,0,1,0);samples=[];seen=set()
    begin=address(new,'FfMuxWorldDraw');end=address(new,'FfMuxWorldDrawEnd')
    def observe(mem,c,i):
        tag=mem.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else -1
        if tag==0xdd and begin<=c.pc<end and c.pc not in seen:
            assert H.get(mem,'NmiDisable')==255
            seen.add(c.pc);samples.append((i,clone(mem,c)))
    M.invoke_main(m,observe);assert samples
    rows=[]
    for step,(state,cpu)in samples:
        for kind in['NMI','IRQ']:
            n,c=clone(state,cpu);assert H.get(n,'NmiDisable')==255
            if kind=='IRQ'and c.p&c.INTERRUPT:continue
            r=V.interrupt(n,c,kind);H.finish(n,c)
            assert c.sp==224 and n.rawtags[1]==H.get(n,'CurrentBank')and n.rawtags[2]==H.get(n,'CurrentBankC')
            rows.append(dict(actual_Main_step=step,**r))
    normal=[]
    for selected in[0,2,9,22,32]:
        n=T.copy(m);H.put(n,SelectedCharacter=selected)
        assert H.get(n,'NmiDisable')==0
        c=H.start(n,'FwCheck');normal.append(dict(selected=selected,**V.interrupt(n,c,'NMI')))
    return dict(actual_busy_instruction_states=len(samples),busy_lag_NMI_IRQ_cases=len(rows),rows=rows,
        real_normal_NMI_after_completed_frame=normal,no_fabricated_normal_NMI_inside_active_DrawAll=True)

def main():
    out=O/'main-and-isr-controls-v3.json';assert not out.exists()
    proof=dict(passed=False,native=False,admitted=False,metadata_only=True,scheduler=False,checks={})
    try:
        old=H.C.qualified(P/'candidate.nes');new=H.C.qualified(H.O/'candidate.nes')
        proof['checks']['actual_Main']=full_main(old,new);print('actual shared Main PASS',flush=True)
        proof['checks']['actual_vectors']=actual_vectors(new);print('actual busy vectors PASS',flush=True)
        proof['passed']=True
    except Exception as e:proof.update(error=repr(e),traceback=traceback.format_exc())
    proof['bindings']={str(f.resolve()):K.sha(f)for f in[Path(__file__),Path(B.__file__),Path(W.__file__),Path(K.__file__),Path(M.__file__),Path(V.__file__),
        P.parent/'source-closure.json',O/'source-closure.json',O/'marker-controls-v2.json',P/'candidate.nes',P/'candidate.dbg',H.O/'candidate.nes',H.O/'candidate.dbg']}
    out=out if proof['passed']else O/'main-and-isr-negative-v3.json'
    out.write_text(json.dumps(proof,indent=2)+'\n',newline='\n');print(json.dumps(dict(passed=proof['passed'],path=str(out),error=proof.get('error'))),flush=True);assert proof['passed']

if __name__=='__main__':main()
