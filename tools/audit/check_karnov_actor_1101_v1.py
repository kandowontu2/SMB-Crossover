"""Compare recovered Karnov instructions and private RAM relocation to donor."""
from pathlib import Path
import hashlib,json,re,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from verify_native_relocation import NesMPU
from recover_karnov_actor_1101_v1 import ROM,EXPECTED,LO,HI
O=R/'build/karnov-original-source-1101-v1';REF=R/'build/karnov-native-reference-1101-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


class Memory(bytearray):
    def __init__(self):super().__init__(65536);self.writes=[]
    def __setitem__(self,k,v):
        if isinstance(k,int):self.writes.append(k)
        super().__setitem__(k,v)


def main():
    result=dict(passed=False,source_CPU=True,native_original=True,native_port=False,installed=False)
    try:
        assembly=json.loads((O/'assembly.json').read_text());original=json.loads((REF/'capture/reference.json').read_text())
        for p,h in assembly['bindings'].items():assert sha(p)==h,p
        assert original['passed']and sha(ROM)==EXPECTED
        labels={}
        for line in(O/'portable.dbg').read_text().splitlines():
            if line.startswith('sym\t'):
                d=dict(re.findall(r'(\w+)=("[^"\n]*"|[^,\n]+)',line))
                if 'val'in d:labels[d['name'].strip('"')]=int(d['val'],0)
        fixed=(O/'original-fixed.bin').read_bytes();portable=(O/'portable.bin').read_bytes();initial=bytes(original['initial_fixture']);assert len(initial)==2048
        all_events={};normalizations=0;maximum_steps=0;digest=hashlib.sha256();count=0
        aset={'LDA','PLA','TXA','TYA','ADC','SBC','AND','ORA','EOR'};xset={'LDX','TAX','TSX','INX','DEX'};yset={'LDY','TAY','INY','DEY'}
        def make(is_port):
            m=Memory()
            if is_port:
                m[0x6000:0x6800]=initial;m[0x9000:0xb000]=portable;m[:256]=bytes((i*37+19)&255 for i in range(256))
            else:m[:2048]=initial;m[0xc000:]=fixed
            m.writes=[];return m
        def put(m,p,addr,value):m[(0x6000 if p else 0)+addr]=value
        def get(m,p,addr):return m[(0x6000 if p else 0)+addr]
        def execute(m,p,flags,ceiling):
            nonlocal maximum_steps
            c=NesMPU(memory=m,pc=labels['KrFrame']if p else LO);c.sp=224;c.p=flags;c.a=85;c.x=19;c.y=23;c.stPushWord(0x7ffe)
            events=[];last=[None,None,None];at_result=None;global_zp=bytes(m[:256])if p else None
            for steps in range(12000):
                if c.pc==0x7fff:break
                if p and c.pc==labels['KrFrameResult']:at_result=(c.a,c.x,c.y,c.p,last.copy(),m[0]+256*m[1])
                if c.pc in [0xc1c7,0xc81d,0xc3d8]:
                    kind=f'{c.pc:04X}';events.append((kind,c.a,c.x,c.y))
                    if c.pc==0xc3d8:c.a=1 if c.y<ceiling else 0;c.FlagsNZ(c.a)
                    all_events[kind]=all_events.get(kind,0)+1
                    c.pc=(c.stPopWord()+1)&65535;continue
                op,mode=c.disassemble[m[c.pc]]
                if op in aset or(op in ['ASL','LSR','ROL','ROR']and mode=='acc'):last[0]=c.pc
                if op in xset:last[1]=c.pc
                if op in yset:last[2]=c.pc
                assert m[c.pc]!=0,('BRK',p,hex(c.pc));c.step()
            else:raise AssertionError(('Leaf bound',p,hex(c.pc)))
            maximum_steps=max(maximum_steps,steps);assert c.sp==224
            if p:
                assert bytes(m[:256])==global_zp,'Borrowed dispatch pointer not restored'
                assert all(0x6000<=a<0x6800 or 0x100<=a<0x200 or 0<=a<2 for a in m.writes),('Foreign write',[hex(a)for a in m.writes if not(0x6000<=a<0x6800 or 0x100<=a<0x200 or 0<=a<2)])
                assert at_result and(c.a,c.x,c.y,c.p&0xcf)==(*at_result[:3],at_result[3]&0xcf)
                return c,events,at_result[4],at_result[5]
            return c,events,last,m[0x58]+256*m[0x59]
        def pair(mems,flags=0x31,ceiling=0):
            nonlocal count,normalizations
            values=[execute(m,p,flags,ceiling)for p,m in enumerate(mems)]
            (a,ea,la,pa),(b,eb,lb,pb)=values
            assert ea==eb,('Native external event divergence',ea,eb)
            assert(a.y,a.p&0xcf)==(b.y,b.p&0xcf),('Y/P divergence',a.y,b.y,a.p,b.p)
            for i,(x,y)in enumerate([(a.a,b.a),(a.x,b.x)]):
                if x!=y:
                    source=0xc83e if i==0 else 0xc83c
                    assert la[i]==source and lb[i]==labels['KrDispatch']+source-0xc831,('Unexplained register divergence',i,x,y,la,lb)
                    assert pb==labels[f'Kr_{pa:04X}']and x==(pa>>8 if i==0 else pa&255)and y==(pb>>8 if i==0 else pb&255)
                    normalizations+=1
            skip=set(range(0x100,0x200))|{0x58,0x59,0x7fe,0x7ff}
            delta=[i for i in range(2048)if i not in skip and mems[0][i]!=mems[1][0x6000+i]]
            assert not delta,('RAM divergence',[(hex(i),mems[0][i],mems[1][0x6000+i])for i in delta[:12]])
            digest.update(bytes(get(mems[0],0,i)for i in range(0x5e,0x8e)));digest.update(json.dumps(ea).encode());count+=1
        selectors=0
        for state in range(32):
            for face in [0,128]:
                for held in [0,1,2,3,16,32,64,128,129,130,33,34,48,80,160,240]:
                    for flags in [0x30,0x31,0x71,0xf1]:
                        mems=[make(p)for p in range(2)]
                        for p,m in enumerate(mems):
                            for addr,value in {0x62:state|face,0x63:128,0x64:144,0x66:16,0x67:4,0x1b:held,0x21:held&3,0x89:9,0x8a:0,0x8b:9,0x8c:0,0x8d:0,0x6b0:1,0x737:4}.items():put(m,p,addr,value)
                        pair(mems,flags,ceiling=80);selectors+=1
        traces=0;updates=0;source_peaks=[]
        # Coherent source-driven land sequences. Both engines receive exactly
        # the same declared flat-floor/ceiling boundary and source input edges.
        for boots in [0,128]:
            for weapon in [0,1,2,8]:
                for ceiling in [0,96]:
                    mems=[make(p)for p in range(2)];prev=0;peak=144
                    for p,m in enumerate(mems):
                        for addr,value in {0x62:0,0x63:128,0x64:144,0x65:boots|weapon,0x66:0,0x1b:0,0x21:0,0x89:0,0x8a:0,0x8b:2,0x8c:0,0x8d:0}.items():put(m,p,addr,value)
                    for tick in range(360):
                        held=128 if 20<=tick<65 else 1 if 90<=tick<115 else 32 if 160<=tick<180 else 2 if 200<=tick<220 else 64 if 245<=tick<285 else 129 if 310<=tick<330 else 0
                        for p,m in enumerate(mems):
                            y=get(m,p,0x64);state=get(m,p,0x62)
                            if y>=144 and(state&64 or state&31 in [0,1,2,3,4,5,6,7,23]):put(m,p,0x64,144)
                            for addr,value in {0x1b:held,0x21:(held&~prev)&3,0xe8:tick&255,0x8b:2 if get(m,p,0x64)>=144 else 0}.items():put(m,p,addr,value)
                        pair(mems,ceiling=ceiling);peak=min(peak,get(mems[0],0,0x64));prev=held;updates+=1
                    assert peak<124,('Source jump not exercised',boots,weapon,ceiling,peak);source_peaks.append(144-peak);traces+=1
        assert all(x in all_events for x in ['C1C7','C81D','C3D8']),all_events
        result.update(passed=True,donor_sha256=EXPECTED,private_actor_bytes=labels['KrActorEnd']-0x9000,selector_boundary_pairs=selectors,source_coherent_sequences=traces,source_sequence_updates=updates,total_engine_executions=2*count,source_jump_rises=source_peaks,external_event_calls=all_events,pointer_derived_register_normalizations=normalizations,max_instruction_steps=maximum_steps,trace_sha256=digest.hexdigest(),host_global_ZP_restored=True,only_declared_private_RAM_stack_pointer_writes=True,scope='All32 selector roots across two facings,16 input patterns/four incoming flags;16 coherent360-update land sequences with four weapon levels/boots/declared ceilings. Exact original/private RAM, events, flags/Y/SP; A/X differences accepted only with last-writer proof of relocated dispatch-pointer bytes. Three declared external sound/terrain/scene callbacks are isolated identically. This does not qualify native host terrain, graphics, original audio, lifecycle or admission.')
    except Exception as e:result.update(error=repr(e),traceback=traceback.format_exc())
    result['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),O/'assembly.json',O/'portable.bin',O/'portable.dbg',O/'original-fixed.bin',REF/'capture/reference.json',ROM]}
    (O/'CPU-controls.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in result.items()if k!='bindings'}));assert result['passed']


if __name__=='__main__':main()
