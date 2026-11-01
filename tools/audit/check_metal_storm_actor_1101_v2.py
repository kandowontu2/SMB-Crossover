"""Differential actor checks using legal donor frames and recorded API leaves."""
from pathlib import Path
import hashlib,json,re,sys,traceback
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/audit'))
import metal_storm_cpu_1101_v2 as M
from verify_native_relocation import NesMPU
OUT=ROOT/'build/metal-storm-component-1101-v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

class Memory(bytearray):
    def __init__(self):super().__init__(65536);self.writes=[]
    def __setitem__(self,k,v):
        if isinstance(k,int):self.writes.append(k)
        super().__setitem__(k,v)

def labels():
    q={}
    for line in(OUT/'portable.dbg').read_text().splitlines():
        if line.startswith('sym\t'):
            d=dict(re.findall(r'(\w+)=("[^"\n]*"|[^,\n]+)',line))
            if 'val'in d:q[d['name'].strip('"')]=int(d['val'],0)
    return q

def main():
    result=dict(passed=False,source_CPU=True,native=False,installed=False)
    try:
        proof=json.loads((OUT/'assembly.json').read_text())
        for p,h in proof['bindings'].items():assert sha(p)==h,p
        lab=labels();portable=(OUT/'portable.bin').read_bytes();selected=(OUT/'donor-selected.bin').read_bytes()
        cb={int(k,16):v for k,v in proof['portable_callbacks'].items()}
        core_indices=[i for i in range(2048)if not(0x180<=i<0x200)and i not in [0x6e,0x6f,0x7fe,0x7ff]]
        actual=M.boot()
        for t in range(600):M.frame(actual,0x10 if t in [120,121,300,301,480,481]else 0)
        cases=0;updates=0;events_total={};gravity=set();jump=set();shots=set();maxsteps=0;maxcycles=0;digest=hashlib.sha256()
        def execute(initial,entry,events,port):
            nonlocal maxsteps,maxcycles
            memory=Memory();memory[0x8000:]=selected
            if port:
                memory[0x9000:0xc000]=portable;memory[0x6000:0x6800]=initial
                memory[:256]=bytes((i*43+29)&255 for i in range(256))
                ptr=initial[0x6e]+256*initial[0x6f]
                if ptr<2048:ptr+=0x6000
                memory[0],memory[1]=ptr&255,ptr>>8
            else:memory[:2048]=initial
            c=NesMPU(memory=memory,pc=lab['MsFrame']if port else 0xad8c)
            c.a,c.x,c.y,c.p=entry;c.sp=0xe0;c.stPushWord(0x5ffe)
            global_zp=bytes(memory[:256]);memory.writes=[];index=0;steps=0;start=c.processorCycles
            emap={v:k for k,v in cb.items()}if port else{a:a for a in cb}
            while c.pc!=0x5fff:
                if c.pc in emap:
                    assert index<len(events),(port,'extra API',hex(c.pc))
                    e=events[index];kind=emap[c.pc];assert kind==e['kind'],(port,index,hex(kind),hex(e['kind']))
                    assert(c.a,c.x,c.y,c.p&0xcf)==(*e['entry'][:3],e['entry'][3]&0xcf),(port,'API ABI',hex(kind),(c.a,c.x,c.y,c.p),e['entry'])
                    for a,v in e['writes']:
                        if a in [0x6e,0x6f]and port:continue
                        memory[(0x6000 if port else 0)+a]=v
                    if port:
                        ptr=e['pointer'];assert ptr<2048,('unclosed pointer',hex(ptr))
                        ptr+=0x6000;memory[0],memory[1]=ptr&255,ptr>>8
                    c.a,c.x,c.y,c.p=e['exit'];c.pc=(c.stPopWord()+1)&65535;index+=1;continue
                assert memory[c.pc]!=0,('BRK',port,hex(c.pc));c.step();steps+=1
                assert steps<20000,('unit bound',port,hex(c.pc))
            assert c.sp==0xe0 and index==len(events),(port,c.sp,index,len(events))
            if port:
                assert bytes(memory[:256])==global_zp,'borrowed ZP not restored'
                assert all(0x6000<=a<0x6800 or 0x100<=a<0x200 or a in [0,1]for a in memory.writes),('outside private state',[hex(a)for a in memory.writes if not(0x6000<=a<0x6800 or 0x100<=a<0x200 or a in [0,1])])
            maxsteps=max(maxsteps,steps);maxcycles=max(maxcycles,c.processorCycles-start)
            return memory,(c.a,c.x,c.y,c.p&0xcf,c.sp)
        def pair(initial,entry,events,final):
            nonlocal cases
            a,ar=execute(initial,entry,events,False);b,br=execute(initial,entry,events,True)
            assert ar==br,('endpoint ABI',ar,br)
            delta=[i for i in core_indices if a[i]!=b[0x6000+i]]
            assert not delta,('private RAM',[(hex(i),a[i],b[0x6000+i])for i in delta[:20]])
            delta=[i for i in core_indices if a[i]!=final[i]]
            assert not delta,('actual donor replay',[(hex(i),a[i],final[i])for i in delta[:20]])
            digest.update(bytes(a[i]for i in core_indices));cases+=1
        for tick in range(480):
            # Real controller edges, original floor/ceiling/map data, no injected actor fields.
            phase=tick%240
            pad=1 if phase<32 else 0x81 if phase<65 else 0 if phase<85 else 0x88 if phase<120 else 0x40 if phase<145 else 0x84 if phase<180 else 0x42 if phase<205 else 0
            state={}
            def observe(c):
                nonlocal updates
                if c.pc==0xad8c and not state:
                    state.update(initial=bytes(c.memory[:2048]),entry=(c.a,c.x,c.y,c.p),events=[],pending=None,returnpc=((c.memory[0x100+((c.sp+1)&255)]+256*c.memory[0x100+((c.sp+2)&255)])+1)&65535)
                if not state or state.get('done'):return
                pending=state['pending']
                if pending and c.pc==pending['returnpc']:
                    after=bytes(c.memory[:2048]);before=pending['before']
                    writes=[(i,after[i])for i in range(2048)if after[i]!=before[i]and not(0x180<=i<0x200)]
                    state['events'].append(dict(kind=pending['kind'],entry=pending['entry'],exit=(c.a,c.x,c.y,c.p),writes=writes,pointer=after[0x6e]+256*after[0x6f]))
                    events_total[f'{pending["kind"]:04X}']=events_total.get(f'{pending["kind"]:04X}',0)+1
                    state['pending']=None
                if c.pc==state['returnpc'] and state['pending']is None:
                    pair(state['initial'],state['entry'],state['events'],bytes(c.memory[:2048]));state['done']=True;updates+=1;return
                if c.pc in cb and state['pending']is None:
                    ret=((c.memory[0x100+((c.sp+1)&255)]+256*c.memory[0x100+((c.sp+2)&255)])+1)&65535
                    state['pending']=dict(kind=c.pc,entry=(c.a,c.x,c.y,c.p),before=bytes(c.memory[:2048]),returnpc=ret)
            M.frame(actual,pad,trace=observe)
            if state:assert state.get('done'),('unreturned actor',tick,state.get('pending'))
            gravity.add(actual.memory[0x734]);jump.add(actual.memory[0x5b8]);shots.add((actual.memory[0x512],actual.memory[0x513]))
        assert cases>=300 and gravity=={0,128}and max(jump)>=49,(cases,gravity,jump)
        result.update(passed=True,donor_sha256=M.EXPECTED,actor_pairs=cases,engine_executions=2*cases,actual_source_NMI_frames=480,actual_callbacks_replayed=events_total,gravity_directions=sorted(gravity),jump_clock_states=sorted(jump),projectile_activation_pairs=[list(x)for x in sorted(shots)],maximum_component_steps=maxsteps,maximum_component_cycles=maxcycles,portable_bytes=lab['MsEnd']-0x9000,host_globalZP_restored=True,only_private_state_and_stack_writes=True,trace_sha256=digest.hexdigest(),scope='Legal donor CPU reset/Start/NMI frames exercise walking, jump/release, both gravity reversals, ceiling/floor and shooting. For each actor entry, original external API effects are recorded from actual donor execution and replayed identically at explicit original/private callback boundaries; exact actor state and AXYP/SP agree. API bodies are not ported by this replay test. PPU is untimed: this is not Mesen/raster/acoustic/host-gameplay proof or playable admission.')
    except Exception as e:result.update(error=repr(e),traceback=traceback.format_exc())
    result['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),Path(M.__file__),M.ROM,ROOT/'tools/audit/verify_native_relocation.py',OUT/'assembly.json',OUT/'portable.bin',OUT/'portable.dbg',OUT/'donor-selected.bin']}
    (OUT/'CPU-controls.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='bindings'}));assert result['passed']

if __name__=='__main__':main()
