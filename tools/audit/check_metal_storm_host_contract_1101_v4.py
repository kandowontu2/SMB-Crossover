"""Original/source-rebased CPU and typed adapter evidence, no native admission."""
from pathlib import Path
import hashlib,itertools,json,sys,traceback,zipfile
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT/'tools/audit'),str(ROOT/'tools')]
import metal_storm_cpu_1101_v2 as M
from verify_native_relocation import NesMPU
OUT=ROOT/'build/metal-storm-host-contract-1101-v4'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

class Memory(bytearray):
    def __init__(self):super().__init__(65536);self.writes=[]
    def __setitem__(self,k,v):
        if isinstance(k,int):self.writes.append(k)
        super().__setitem__(k,v)

def main():
    q=dict(passed=False,source_CPU=True,native=False,installed=False,menu_admitted=False)
    try:
        stage=json.loads((OUT/'assembly.json').read_text())
        for p,h in stage['bindings'].items():assert sha(p)==h,p
        lab=stage['labels'];ports={v:int(n.rsplit('_',1)[1],16)for n,v in stage['callbacks'].items()};originalports={a:a for a in ports.values()}
        donor=M.machine();donor.memory.regs[6:8]=[0,1];donor.memory.map();selected=bytes(donor.memory[0x8000:])
        kernel=(OUT/'kernel.bin').read_bytes();cold=(OUT/'cold.bin').read_bytes();fields=stage['native_symbols'];core=[i for i in range(2048)if not(0x180<=i<0x200)and i not in[0x6e,0x6f,0x7fe,0x7ff]]
        digest=hashlib.sha256();cases=0;maxcycles=0;minimum=224;events_total={};first=None
        def memory(initial=None):
            m=Memory();m[0x8000:]=selected;m[0xa000:0xa000+len(kernel)]=kernel;m[0x8000:0x8000+len(cold)]=cold;m[:256]=bytes((i*43+29)&255 for i in range(256))
            if initial is not None:m[0xc000:0xc800]=initial
            return m
        def run(m,pc,entry=(85,7,91,0x71),events=(),kind='leaf'):
            nonlocal maxcycles,minimum
            c=NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p=entry;c.sp=224;c.stPushWord(0x5ffe);index=0;start=c.processorCycles;steps=0;emap=originalports if kind=='original'else ports
            while c.pc!=0x5fff:
                minimum=min(minimum,c.sp)
                if c.pc in emap:
                    assert index<len(events),('extra callback',kind,hex(c.pc))
                    e=events[index];assert emap[c.pc]==e['kind'],('callback order',kind,index)
                    assert(c.a,c.x,c.y,c.p&0xcf)==(*e['entry'][:3],e['entry'][3]&0xcf),('API AXYP',kind,hex(e['kind']),entry,(c.a,c.x,c.y,c.p),e['entry'])
                    for a,v in e['writes']:
                        if kind!='original'and a in[0x6e,0x6f]:continue
                        m[(0 if kind=='original'else 0xc000)+a]=v
                    if kind!='original':
                        pointer=e['pointer'];assert pointer<2048;pointer+=0xc000;m[3],m[4]=pointer&255,pointer>>8
                    c.a,c.x,c.y,c.p=e['exit'];c.pc=(c.stPopWord()+1)&65535;index+=1;continue
                assert m[c.pc]!=0,('BRK',kind,hex(c.pc));c.step();steps+=1;assert steps<25000,(kind,hex(c.pc))
            assert c.sp==224 and index==len(events),(kind,c.sp,index,len(events));maxcycles=max(maxcycles,c.processorCycles-start)
            return(c.a,c.x,c.y,c.p&0xcf,c.sp)
        def compare(initial,entry,events,final,pad,tick):
            nonlocal cases,first
            a=Memory();a[0x8000:]=selected;a[:2048]=initial
            ar=run(a,0xad8c,entry,events,'original')
            b=memory(initial);b[3],b[4]=0x93,0x21 # arbitrary caller pointer; every tile read must be preceded by real API lookup
            z0=bytes(b[:256]);b.writes=[];br=run(b,lab['MsFrame'],entry,events)
            assert ar==br and bytes(b[:256])==z0,('relocated actor AXYP or foreground restoration',ar,br)
            assert all(0xc000<=i<0xc800 or 0x100<=i<0x200 or i in[3,4]for i in b.writes),'Actor touched host globals/NMI scratch'
            assert all(a[i]==b[0xc000+i]==final[i]for i in core),'Original/rebased actor state differs'
            s=memory(initial)
            for n,v in dict(SelectedCharacter=35,SavedJoypadBits=pad,FrameCounter=tick&255,GamePauseStatus=0,OperMode=1,GameEngineSubroutine=8).items():s[fields[n]]=v
            s[0xc800]=167;s[0xc802]=0;s[3],s[4]=0xa5,0x5a;z0=bytes(s[:256]);s.writes=[]
            sr=run(s,lab['MsHostStep'],entry,events)
            assert sr[:3]==entry[:3]and sr[3]&1 and sr[3]&0xce==entry[3]&0xce
            assert all(a[i]==s[0xc000+i]for i in core if i!=0x31),'Typed step changed original physics'
            assert s[0xc031]==int(f'{pad:08b}'[::-1],2),'Post-actor original controller pipeline differs'
            assert bytes(s[:256])==z0 and all(0xc000<=i<0xc810 or 0x100<=i<0x200 or i in[3,4]for i in s.writes),'Step used foreign/NMI scratch'
            before=bytes(s[0xc000:0xc800]);run(s,lab['MsHostStep'],entry)
            assert bytes(s[0xc000:0xc800])==before and not any(s[0xc803:0xc807]),'Duplicate epoch replayed source or displacement'
            s[fields['FrameCounter']]=(tick+1)&255;s[fields['GamePauseStatus']]=1;run(s,lab['MsHostStep'],entry)
            assert bytes(s[0xc000:0xc800])==before and not any(s[0xc803:0xc807]),'Pause advanced source or displacement'
            digest.update(bytes(a[i]for i in core));cases+=1
            if first is None:first=initial
        actual=M.boot()
        for t in range(600):M.frame(actual,16 if t in[120,121,300,301,480,481]else 0)
        gravities=set();bounds=set()
        for tick in range(480):
            phase=tick%240;pad=1 if phase<32 else 0x81 if phase<65 else 0 if phase<85 else 0x88 if phase<120 else 0x40 if phase<145 else 0x84 if phase<180 else 0x42 if phase<205 else 0
            state={}
            def observe(c):
                if c.pc==0xad8c and not state:state.update(initial=bytes(c.memory[:2048]),entry=(c.a,c.x,c.y,c.p),events=[],pending=None,returnpc=((c.memory[0x100+((c.sp+1)&255)]+256*c.memory[0x100+((c.sp+2)&255)])+1)&65535)
                if not state or state.get('done'):return
                e=state['pending']
                if e and c.pc==e['returnpc']:
                    after=bytes(c.memory[:2048]);writes=[(i,after[i])for i in range(2048)if after[i]!=e['before'][i]and not(0x180<=i<0x200)]
                    state['events'].append(dict(kind=e['kind'],entry=e['entry'],exit=(c.a,c.x,c.y,c.p),writes=writes,pointer=after[0x6e]+256*after[0x6f]));events_total[f'{e["kind"]:04X}']=events_total.get(f'{e["kind"]:04X}',0)+1;state['pending']=None
                if c.pc==state['returnpc']and state['pending']is None:compare(state['initial'],state['entry'],state['events'],bytes(c.memory[:2048]),pad,tick);state['done']=True;return
                if c.pc in originalports and state['pending']is None:
                    ret=((c.memory[0x100+((c.sp+1)&255)]+256*c.memory[0x100+((c.sp+2)&255)])+1)&65535
                    state['pending']=dict(kind=c.pc,entry=(c.a,c.x,c.y,c.p),before=bytes(c.memory[:2048]),returnpc=ret)
            M.frame(actual,pad,trace=observe);assert not state or state.get('done');gravities.add(actual.memory[0x734]);bounds.add(actual.memory[0x732]+256*actual.memory[0x733])
        assert cases==480 and gravities=={0,128}
        # All8-bit input combinations, exact AXYP and no source edge invention.
        m=memory(first);inputcases=0
        for p in range(256):
            m[fields['SavedJoypadBits']]=p;entry=(85,7,91,0x71);r=run(m,lab['MsHostInput'],entry)
            assert r[:4]==(85,7,91,0x41)and m[0xc031]==int(f'{p:08b}'[::-1],2);inputcases+=1
        # Entire16-bit source Y domain: exact signed page*240 conversion.
        ycases=0
        for page,lo in itertools.product(range(256),range(256)):
            m[0xc4c8],m[0xc4b0]=page,lo;r=run(m,lab['MsHostReadY'])
            signed=page if page<128 else page-256;want=(signed*240+lo)&65535
            assert r[0]+256*r[1]==want and r[2]==91;ycases+=1
        # Cold menu remapping fragments: only slot11+bit2 becomes raw35.
        menucases=startcases=0
        for slot,alts,raw in itertools.product(range(32),[0,1,2,3,127,128,255],[0,11,34,35]):
            m[fields['CrossoverMenuIndex']]=slot;m[fields['FmAlts']]=alts;m[fields['SelectedCharacter']]=raw;r=run(m,lab['MsMenuResolveLeaf'])
            want=35 if slot==11 and alts&2 else raw
            assert m[fields['SelectedCharacter']]==want and r[0]==want;menucases+=1
            r=run(m,lab['MsMenuStartFlagsLeaf']);assert m[fields['FmAlts']]==(alts|2 if want==35 else alts);startcases+=1
        # Compact art decoder reproduces all original cells and native packet
        # order without fabricated wings/poses/tiles or world-bank replacement.
        with zipfile.ZipFile(ROOT/'docs/qa/checkpoints/2026-11-01/metal-storm-original-component-v3/source-proof.zip')as z:art=json.loads(z.read('proof/art.json'));body=z.read('assets/body.chr')
        meta=(OUT/'body-meta.bin').read_bytes();rendercases=0;maxpages=0
        for p in art['packets']:
            n=meta[p['state']*8+p['frame']];assert n!=255;count=meta[97+n];base=130+meta[64+n]*4;bits=(p['facing']>>6)+(p['gravity']>>6);order=(946 if count==6 else 970)+bits*count
            packet=[];pages=[]
            for j in range(count):
                i=meta[order+j];dx,dy,pattern,attr=meta[base+i*4:base+i*4+4]
                dx=24-dx if p['facing']else dx;dy=18-dy if p['gravity']else dy;attr^=p['facing']|p['gravity'];page=pattern//32
                if page not in pages:pages.append(page)
                tile=(pattern%32)*2+pages.index(page)*64;packet.append((dx,dy,pattern,attr,tile))
            # Existing native DrawMetasprite emits records in reverse order.
            emitted=[v[:4]for v in packet[::-1]];wanted=[(c['dx'],c['dy'],c['pattern_index'],c['attributes'])for c in p['cells']]
            assert emitted==wanted and all(v[4]%2==0 for v in packet)
            assert all(body[v[2]*32:v[2]*32+32]==body[(pages[v[4]//64]*32+(v[4]%64)//2)*32:][:32]for v in packet)
            maxpages=max(maxpages,len(pages));rendercases+=1
        assert rendercases==208 and maxpages==2
        q.update(passed=True,donor_sha256=M.EXPECTED,source_rebased_frames=cases,original_rebased_and_host_step_executions=3*cases,actual_donor_NMI_frames=480,source_callbacks_replayed=events_total,both_original_gravity_directions=True,source_right_bounds_observed=sorted(bounds),host_ZP_preserved=True,NMI_scratch_0_2_untouched=True,original_pointer_03_04_saved_restored=True,arbitrary_incoming_foreground_pointer=True,duplicate_epoch_no_update_cases=cases,paused_no_update_cases=cases,input_cases=inputcases,signed_240_page_Y_cases=ycases,cold_menu_remap_cases=menucases,cold_start_flag_cases=startcases,original_graphics_cell_order_cases=rendercases,maximum_body_CHR_windows=maxpages,maximum_component_cycles=maxcycles,minimum_standalone_SP=minimum,trace_sha256=digest.hexdigest(),scope='Legal donor frames compare original source actor, unchanged semantic core rebasedC000/A000/foreground03 and typed selected-owner step. External source API effects are recorded/replayed at explicit ports, NOT native terrain/scene/weapon/audio implementations. Graphics compact decoder matches original CPU-rendered cells/order/patterns, not a native PPU renderer. No source constructor, native cache authentication/loader, Main/ISR/SMC/raster/audio/complete weapons/upgrades or playable menu admission is claimed.')
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
    q['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),Path(M.__file__),M.ROM,OUT/'assembly.json',OUT/'kernel.bin',OUT/'kernel.dbg',OUT/'body-meta.bin',OUT/'cold.bin',ROOT/'tools/audit/verify_native_relocation.py']}
    (OUT/'CPU-controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['bindings']}));assert q['passed'],q.get('error')
if __name__=='__main__':main()
