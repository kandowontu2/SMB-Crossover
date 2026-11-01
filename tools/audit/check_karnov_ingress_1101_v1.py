"""Check the real shared service transport and exact source-funded table swap.

Stops at the genuine child-jump seam; this does not qualify gameplay or a menu
entry. Arithmetic and ISR checks execute the original emitted host routines.
"""
from pathlib import Path
import hashlib,itertools,json,re,subprocess,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import battletoads_current_loader_controls_v1 as L
import ff_wram_host_controls_v7 as H
import ff_host_pickups_vectors_v2 as V
import check_hogan_current_bounded_v1 as C
from check_tmnt_render_oa import address,location
O=R/'build/karnov-host-resource-base-1101-v1';J=R/'build/doki-current-component-1101-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def endpoint(m,name,p,hook=None):
    c=H.start(m,name,a=0x59,x=0x5a,y=0xc7,p=p);smc=address(m.bundle,'FarcallJmpTarget_SMC');first=True;trace=[]
    for n in range(900):
        if c.pc==smc:
            if not first:return (c.a,c.x,c.y,c.p,c.sp,m.rawtags[1],m[smc+1]|m[smc+2]<<8),trace,c
            first=False
        if hook:hook(m,c,n)
        trace.append((c.pc,m.rawtags[1],m.rawtags[2]));assert m[c.pc]!=0,(name,hex(c.pc));c.step()
    raise AssertionError(('Shared route bound',name))

def exports(p):
    t=subprocess.run([str(R/'tools/Windows/cc65/bin/od65.exe'),'--dump-exports',str(p)],check=True,capture_output=True,text=True).stdout
    return set(re.findall(r'Name:\s*"([^"]+)"',t))

def main():
    q=dict(passed=False,source_CPU=True,native=False,installed=False,menu_admitted=False)
    paths=[Path(__file__),O/'terrain-assembly.json',J/'candidate.nes',J/'candidate.dbg',O/'candidate.nes',O/'candidate.dbg',O/'union.o',R/'build/hogan-thomas-current/union.o']
    try:
        stage=json.loads((O/'terrain-assembly.json').read_text());assert stage['passed'] and stage['ingress']
        for p,h in stage['bindings'].items():assert sha(p)==h,p
        old,new=bs=[H.C.qualified(p/'candidate.nes')for p in [J,O]]
        # Only the three genuine indexed-read operands change in the routine;
        # the two remaining product tables and all other instructions are exact.
        code=[];operands=[]
        for b in bs:
            code.append(b['raw'][location(b,'MarioWaterCoast'):location(b,'MarioWaterCoast::ProductLo')])
        oldhi=address(old,'MarioWaterCoast::ProductHi');newhi=address(new,'MarioWaterCoast::ProductHi')
        assert oldhi&255==newhi&255==0x8e and newhi==address(new,'KrMarioWaterProductHi')
        value=bytes((i*62344)>>16 for i in range(256))
        for b in bs:
            at=location(b,'MarioWaterCoast::ProductHi');assert b['raw'][at:at+256]==value
        fixed=bytearray(code[0])
        for i in range(len(fixed)-2):
            if fixed[i]in [0xbd,0x7d]and fixed[i+1:i+3]==oldhi.to_bytes(2,'little'):
                operands.append(i);fixed[i+1:i+3]=newhi.to_bytes(2,'little')
        assert len(operands)==3 and bytes(fixed)==code[1],('Exact three emitted table consumers',operands)
        for n in ['ProductLo','ProductMid']:
            a,z=[b['raw'][location(b,'MarioWaterCoast::'+n):location(b,'MarioWaterCoast::'+n)+256]for b in bs];assert a==z
        # Every byte index through each genuine LDA/ADC, including all incoming
        # flags. The same low address preserves indexed page crossing cycles.
        reads=0;math=0;digest=hashlib.sha256();mems=[L.make(b)for b in bs]
        for offset,x,f in itertools.product(operands,range(256),[0x30,0x71,0xfc]):
            results=[]
            for m,b in zip(mems,bs):
                m.raw_page(1,157);H.put(m,CurrentBank=157)
                from verify_native_relocation import NesMPU
                c=NesMPU(memory=m,pc=address(b,'MarioWaterCoast')+offset);c.x=x;c.a=(x*19+7)&255;c.p=f;c.step()
                results.append((c.a,c.x,c.y,c.p,c.processorCycles))
            assert results[0]==results[1],('Indexed read ABI/cycles',offset,x,f,results);reads+=1
        values=sorted({0,1,2,255,256,257,511,65534,65535,65536,65537,0xfffffe,0xffffff}|{i<<s for s in [0,8,16]for i in range(256)}|{(i*1299709)&0xffffff for i in range(256)})
        for value,f in itertools.product(values,[0x30,0x71]):
            results=[]
            for m in mems:
                at=address(m.bundle,'MmMul');m[at:at+3]=value.to_bytes(3,'little');m.writes.clear()
                c=H.start(m,'MarioWaterCoast',a=89,x=90,y=199,p=f);c,_=H.finish(m,c)
                result=(bytes(m[at:at+3]),c.a,c.x,c.y,c.p,c.sp,c.processorCycles)
                results.append(result);assert int.from_bytes(result[0],'little')==(value*62344)>>16
            assert results[0]==results[1],('Full 24-bit math/ABI/cycles',value,f,results);digest.update(results[0][0]);math+=1
        print('Exact water table/three consumers/indexed cycles/full math PASS',reads,math,flush=True)
        # Public endpoints must stay put. Enumerate real final imports rather
        # than treating old-looking words in arbitrary data as control edges.
        names=exports(paths[-1]);assert names==exports(O/'union.o')
        for name in names:
            assert address(old,name)==address(new,name)and location(old,name)==location(new,name),('Existing exported ingress moved',name)
        objs=[Path(p)for p in json.loads((O/'terrain-final-link.json').read_text())['command']if p.endswith('.o')]
        moved=set(stage['moved_source_symbols']);consumers={}
        for p in objs:
            t=subprocess.run([str(R/'tools/Windows/cc65/bin/od65.exe'),'--dump-imports',str(p)],check=True,capture_output=True,text=True).stdout
            found=set(re.findall(r'Name:\s*"([^"]+)"',t))&moved
            if found:consumers[str(p)]=sorted(found)
        assert not consumers,('Unexpected external moved-internal consumer',consumers)
        services=[]
        for row in range(36):
            matches=[n for n in names if address(old,n)==address(old,'HuEntryBase')+16*row]
            if row==0:matches.remove('HuEntryBase')
            assert len(matches)==1,(row,matches);services.append(matches[0])
        count=0;newroutes=0
        def compare(pair,name,p,raw):
            nonlocal count,newroutes
            results=[];writes=[]
            for m in pair:
                m.writes.clear();results.append(endpoint(m,name,p)[0])
                writes.append([(a,v)for a,v in m.writes if not(0x100<=a<0x200 or a in [0x5115,0x5116])])
            if raw!=34:assert results[0]==results[1]and writes[0]==writes[1],('Legacy destination/AXYP/SP/application writes',name,raw,p,results,writes)
            else:
                row=services.index(name);z=results[1]
                # FarCallCommon restores Safecall A via LDA at this seam; this
                # defines N/Z. All other flags and the real caller Y survive.
                assert z==(89,90,199,(p&0x7d),218,157,0xb400+3*row),(name,p,z)
                newroutes+=1
            count+=1
        pair=[L.make(b)for b in bs]
        for raw in range(256):
            for m in pair:H.put(m,SelectedCharacter=raw,FmAlts=0,RdVariant=0,S2Variant=0,FfVariant=0)
            for name,p in itertools.product(services,[0x30,0xff]):compare(pair,name,p,raw)
        print('All raw IDs/all 36 real endpoints PASS',count,flush=True)
        # Resolve all actual 90 menu identities through real Select code and
        # exercise the 85 admitted identities with their real alternate fields.
        counts=[7,2,2,2,2,4,2,2,2,3,3,2,2,2,3,1,4,4,4,2,2,4,1,2,8,1,2,1,6,2,4,2];identities=0
        for slot,total in enumerate(counts):
            pair=[C.fresh(b)for b in bs]
            for m in pair:C.put(m,CrossoverMenuIndex=slot);C.invoke(m,'MenuResolveCharacter');C.invoke(m,'QueueSelection')
            for variant in range(total):
                if variant:
                    for m in pair:C.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0);C.invoke(m,'CrossoverMenuInput')
                pending=[bool(C.invoke(m,'FmPending')['P']&1)for m in pair];assert pending[0]==pending[1]
                raw=H.get(pair[1],'SelectedCharacter');assert H.get(pair[0],'SelectedCharacter')==raw
                if pending[1]:continue
                identities+=1
                for name,p in itertools.product(services,[0x30,0x71,0xbe,0xff]):compare(pair,name,p,raw)
        assert identities==85
        print('All 85 actual menu identity endpoints PASS',count,flush=True)
        for raw,alt in [(0,0),(7,0),(10,64),(22,0),(25,0),(27,0),(32,0),(33,0),(34,1)]:
            pair=[L.make(b)for b in bs]
            for m in pair:H.put(m,SelectedCharacter=raw,FmAlts=alt)
            for name,f in itertools.product(services,range(64)):compare(pair,name,L.flags(f),raw)
        # Real IRQ/NMI cuts through both changed code regions. Results compare
        # to the same uninterrupted candidate; PPU/raster cadence is separate.
        previous=V.pending_store
        def pending(m,c,slot,op):
            if previous(m,c,slot,op):return True
            reg=0x5115 if slot==1 else 0x5116;v={0x8d:c.a,0x8e:c.x,0x8c:c.y}.get(m[c.pc])
            return v is not None and bytes(m[c.pc+1:c.pc+3])==reg.to_bytes(2,'little')and v==H.get(m,'CurrentBank'if slot==1 else'CurrentBankC')
        V.pending_store=pending;cuts=0;minimum=255
        for raw in [0,7,10,22,25,27,32,33,34]:
            seed=L.make(new);H.put(seed,SelectedCharacter=raw,FmAlts=64 if raw==10 else 0)
            ref=L.fork(seed);expected,trace,_=endpoint(ref,'HuMovement',0x70)
            for at in range(0,len(trace),max(1,len(trace)//12)):
                for kind in ['IRQ','NMI']:
                    m=L.fork(seed);events=[]
                    def hook(mem,c,i):
                        if i==at:events.append(V.interrupt(mem,c,kind))
                    actual,_,_=endpoint(m,'HuMovement',0x70,hook);assert actual==expected and len(events)==1
                    assert[bytes(z)for z in m.ram]==[bytes(z)for z in ref.ram]and bytes(m[3:11])==bytes(ref[3:11])
                    minimum=min(minimum,events[0]['minimum_SP']);cuts+=1
        for offset in operands:
            seed=L.make(new);at=address(new,'MmMul');seed[at:at+3]=bytes([255,128,1])
            ref=L.fork(seed);c=H.start(ref,'MarioWaterCoast',p=0x70);trace=[]
            H.finish(ref,c,lambda m,c,i:trace.append(c.pc));expected=V.cpu_state(c)
            for atcut in [i for i,pc in enumerate(trace)if pc==address(new,'MarioWaterCoast')+offset]:
                for kind in ['IRQ','NMI']:
                    m=L.fork(seed);events=[];c=H.start(m,'MarioWaterCoast',p=0x70)
                    def hook(mem,c,i):
                        if i==atcut:events.append(V.interrupt(mem,c,kind))
                    H.finish(m,c,hook);assert V.cpu_state(c)==expected and bytes(m[at:at+3])==bytes(ref[at:at+3])and bytes(m[3:11])==bytes(ref[3:11])
                    minimum=min(minimum,events[0]['minimum_SP']);cuts+=1
        q.update(passed=True,ROM_sha256=stage['ROM_sha256'],parent_sha256=sha(J/'candidate.nes'),water_table_bytes=256,original_table_address=hex(oldhi),relocated_table_address=hex(newhi),exact_indexed_consumers=operands,indexed_read_pairs=reads,full_math_pairs=math,math_trace_sha256=digest.hexdigest(),legacy_union_exports_unchanged=len(names),actual_final_objects=len(objs),moved_internal_external_imports=consumers,route_pairs=count,new_raw34_routes=newroutes,admitted_menu_identities=identities,real_ISR_cuts=cuts,minimum_SP=minimum,scope='Actual shared36-entry dispatch child seam, all256 raw IDs, all85 actual admitted menu identities and selected all-flags cohorts. Original24-bit water multiplication routine/table/ABI/cycles, and real forced-blank IRQ/NMI cuts. No actual new-character menu admission, full Main sequence, normal raster, combat, audio, native controller traversal or nightly update claim.')
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
    q['bindings']={str(p.resolve()):sha(p)for p in paths}
    (O/'ingress-CPU-controls.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','traceback']}));assert q['passed'],q.get('error')

if __name__=='__main__':main()
