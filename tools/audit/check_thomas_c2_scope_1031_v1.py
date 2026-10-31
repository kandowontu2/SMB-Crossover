"""Narrow selected-C2 primitive/store and real lab-vector scratch proofs."""
from pathlib import Path
import argparse,copy,hashlib,itertools,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).resolve().parent))
import check_thomas_c2_component_1031_v4 as K
import thomas_original_cpu_1031_v1 as T
from verify_native_relocation import NesMPU
from private_build_outputs_v1 import validate
P=R/'build/thomas-c2-eight-melee-v1';O=R/'build/thomas-c2-scope-controls-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
dump=lambda p,v:Path(p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')

class Bus(K.C2Bus):
    def __init__(self):super().__init__();self.events=[]
    def __setitem__(self,a,v):
        native=self.instruction_map.get(self.pc)
        super().__setitem__(a,v)
        if native is None or not isinstance(a,int):return
        if a<8:
            self.events.append([a,self.working[a],native])
            if native in [0xa842,0xa915,0xa923]:
                for event in reversed(self.events[:-1]):
                    if event[0]==a-1:event[1]=self.working[a-1];break
        elif 0xc000<=a<0xc800:self.events.append([a-0xc000,v&255,native])
        elif a<0x800 and not 0x100<=a<0x200:
            raise AssertionError(('Worker escaped declared R0..7',hex(native),hex(a)))

def main():
    global P,O
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,default=P);ap.add_argument('--output',type=Path,default=O);a=ap.parse_args();P=a.source.resolve();O=a.output.resolve();assert not O.exists();O.mkdir(parents=True)
    s=T.labels(P/'component.lbl');image=(P/'component.bin').read_bytes();inverse={}
    for prefix in ['Th_','ThHealth_','ThGeom_','ThCold_','ThController_','ThTimers_','ThFrameReset_']:
        inverse.update({v:int(n[len(prefix):],16)for n,v in s.items()if n.startswith(prefix)})
    inverse.update({v:int(n[7:],16)for n,v in s.items()if n.startswith('ThData_')})
    def candidate(ram=None,syms=s,img=image):
        b=Bus();list.__setitem__(b,slice(0x6000,0x8000),img)
        list.__setitem__(b,slice(0,2048),[(i*73+41)&255 for i in range(2048)])
        b.instruction_map=dict(inverse);b.pointer_inverse=dict(inverse);b.commit_pc=syms['ThomasC2Return']+4
        if ram is not None:b.c2[:2048]=ram;b.logical[:]=ram[:16]
        return NesMPU(memory=b,pc=0x6000)
    def execute(c,pc,a=0,x=0,y=0,p=0x30,sp=0xe0,cut=None,kind='nmi',collect=False):
        c.a,c.x,c.y,c.p,c.sp=a,x,y,p,sp;c.stPushWord(0x5ffe);c.pc=pc;c.memory.writes=[];c.memory.events=[]
        n=0;low=c.sp;pcs=[];fired=False
        while c.pc!=0x5fff:
            if cut==n:
                if kind=='nmi':c.nmi();fired=True
                else:
                    allowed=not(c.p&4);c.irq();fired=allowed
            if collect:pcs.append(c.pc)
            if c.pc==s['ThomasC2Borrow']:c.memory.working[:]=c.memory.logical
            c.memory.pc=c.pc;c.step();n+=1;low=min(low,c.sp);assert n<50000,(hex(pc),hex(c.pc))
        return(c.a,c.x,c.y,c.p,c.sp),low,pcs,fired
    def oldrun(c,pc,a,x,y,p):
        c.a,c.x,c.y,c.p,c.sp=a,x,y,p,0xe0;c.stPushWord(0x5ffe);c.pc=pc;c.memory.writes=[];events=[]
        n=0
        while c.pc!=0x5fff:
            at=c.pc;count=len(c.memory.writes);c.step();n+=1;assert n<15000,(hex(pc),hex(c.pc))
            events.extend([address,v,at]for address,v in c.memory.writes[count:]if address<0x800 and not 256<=address<512)
        return(c.a,c.x,c.y,c.p,c.sp),events
    def app(c):
        b=bytearray(c.memory.c2[:2048]);b[:16]=c.memory.logical
        return bytes(b[:256]+b[512:])
    corpus=(R/'build/thomas-original-controls-v4/native-input-states.bin').read_bytes();states=[corpus[i:i+2048]for i in range(0,len(corpus),2048)]
    entries=[('ThomasInput',0xa482,0),('ThomasMove',0xa696,0),('ThomasAnimate',0xa826,0),('ThomasSelectPose',0xa8eb,0),
        ('ThomasBodyBox',0xc0b6,0),('ThomasBodyBox',0xc0b6,4),('ThomasAttackBox',0xc65b,6),('ThomasOverlap',0xc0f3,0),('ThomasNativeDamage',0xc462,6)]
    pairs=0;deltas=[]
    for ram,(entry,oldpc,x),p in itertools.product(states,entries,K.FLAGS):
        r=T.machine();list.__setitem__(r.memory,slice(0,2048),ram)
        # A genuine selected-player source API; enemy serviceX0..5 is not admitted.
        r.memory[0x0a]=0
        if entry=='ThomasNativeDamage':r.memory[0x37a]=2
        c=candidate(bytes(r.memory[:2048]));host=bytes(c.memory[:2048]);c.memory.c2[0x801]=1
        execute(c,s['ThomasC2Borrow']);old,events=oldrun(r,oldpc,0x59,x,0x83,p)
        actual,_,_,_=execute(c,s[entry],0x59,x,0x83,p)
        assert actual==old,(entry,p,'AXYP',actual,old)
        assert c.memory.events==events,(entry,p,'ordered writes',c.memory.events[:10],events[:10])
        # The scoped-return commits byte-provenance state and restores only R0..7.
        execute(c,s['ThomasC2Return'])
        assert app(c)==bytes(r.memory[:256]+r.memory[512:2048]),(entry,p,'projection')
        assert bytes(c.memory[:256])==host[:256]and bytes(c.memory[512:2048])==host[512:]
        pairs+=1
    # Real vector/RTI execution uses precisely the declared eight-byte host ISR
    # contract. A host-owned09 increment MUST survive the owner transaction.
    asm=''' .setcpu "6502"
 .import ThBusy,ThomasC2AcceptedFrame
 .export ThLabISR
 .segment "ISR"
ThLabISR:
 pha
 txa
 pha
 tya
 pha
 ldx #0
@Save:
 lda $00,x
 pha
 inx
 cpx #8
 bne @Save
 ldx #7
 lda #$e1
@Clobber:
 sta $00,x
 dex
 bpl @Clobber
 inc $09
 lda ThBusy
 beq @Restore
 lda #$a5
 ldx #1
 ldy #$7f
 jsr ThomasC2AcceptedFrame
@Restore:
 ldx #7
@Pop:
 pla
 sta $00,x
 dex
 bpl @Pop
 pla
 tay
 pla
 tax
 pla
 rti
'''
    (O/'lab-isr.s').write_text(asm,encoding='utf-8')
    (O/'lab-imports.s').write_text(f'.export ThBusy,ThomasC2AcceptedFrame\nThBusy=${s["ThBusy"]:04X}\nThomasC2AcceptedFrame=${s["ThomasC2AcceptedFrame"]:04X}\n',encoding='utf-8')
    (O/'lab-isr.cfg').write_text('MEMORY { ISR:start=$5e00,size=$100,file=%O; }\nSEGMENTS { ISR:load=ISR,type=ro; }\n',encoding='utf-8')
    cc=R/'tools/Windows/cc65/bin';commands=[]
    def compile(cmd):
        g=validate(cmd,O,cwd=O);p=subprocess.run([str(v)for v in cmd],cwd=O,capture_output=True,text=True);commands.append(dict(command=[str(v)for v in cmd],guard=g,returncode=p.returncode,stderr=p.stderr));assert p.returncode==0,p.stderr
    for n in ['lab-isr','lab-imports']:compile([cc/'ca65.exe',O/f'{n}.s','-o',O/f'{n}.o'])
    compile([cc/'ld65.exe','-C',O/'lab-isr.cfg',O/'lab-isr.o',O/'lab-imports.o','-o',O/'lab-isr.bin'])
    isr=(O/'lab-isr.bin').read_bytes();dump(O/'lab-build.json',commands)
    def install(c):
        list.__setitem__(c.memory,slice(0x5e00,0x5e00+len(isr)),isr)
        list.__setitem__(c.memory,slice(0xfffa,0xfffc),[0,0x5e]);list.__setitem__(c.memory,slice(0xfffe,0x10000),[0,0x5e])
    def snapshot(c):return bytes(c.memory.c2),bytes(c.memory[:256]+c.memory[512:2048])
    vcases=0;minsp=255;witness=[]
    for kind,operation in itertools.product(['nmi','irq'],['cold','frame']):
        seed=candidate();install(seed)
        if operation=='frame':execute(seed,s['ThomasC2ColdInit'],0,1,0xf9)
        pc=s['ThomasC2ColdInit'if operation=='cold'else'ThomasC2AcceptedFrame'];args=(0,1,0xf9)if operation=='cold'else(0x48,1,0xfa)
        base=copy.deepcopy(seed);regs,_,pcs,_=execute(base,pc,*args,sp=0xa9,collect=True)
        first={}
        for index,at in enumerate(pcs):first.setdefault(at,index)
        candidates=sorted(first.values());cuts=candidates[::max(1,len(candidates)//32)][:32]
        cuts=sorted(set(cuts+[0,len(pcs)-2]))
        for cut in cuts:
            c=copy.deepcopy(seed);actual,sp,_,fired=execute(c,pc,*args,sp=0xa9,cut=cut,kind=kind);minsp=min(minsp,sp)
            assert fired,'RealIRQ should be enabled inthiscase'
            assert actual==regs and bytes(c.memory.c2)==bytes(base.memory.c2),('actualvector changed owner',operation,kind,cut)
            for a in list(range(256))+list(range(512,2048)):
                expected=(base.memory[a]+int(a==9))&255
                assert c.memory[a]==expected,('host scope',operation,kind,cut,hex(a),c.memory[a],expected)
            assert bytes(c.memory[0x155:0x186])==bytes(seed.memory[0x155:0x186]),'Labvector touched all33SMC guard'
            if len(witness)<8:witness.append(dict(operation=operation,kind=kind,cut=cut,sourcePC=f'{pcs[cut]:04X}',minimumSP=sp,host09_increment_survives=True))
            vcases+=1
    result=dict(result='PASS',primitive_allflag_pairs=pairs,compared='Exactoriginal AXYP/SP, everyordered sourceapplicationstore including truepointer-byteprovenance, projected2KBstate excludingdeadstack',
        selected_player_damage_X6_only=True,borrowed_physical_scratch='00..07only;08..0FdirectC2state',
        actual_lab_NMI_IRQ_cases=vcases,realvector_stack_RTI=True,host09_increment_survives=True,reentrant_busy_worker_inert=True,all33SMC_guard_exact=True,minimumSP=minsp,witness=witness,
        cpu_model='verify_native_relocation.NesMPU binary2A03 ADC/SBC with Dflagpreserved',
        vector_scope='Compiledlab ISR preciselypreservesdeclaredR0..7, incrementshost09 and attempts busyreentry. NotcurrenthostNMI/mapper/NMI-audio qualification.',
        future_terrain_base=json.loads((P/'source-stage.json').read_text())['future_terrain_base'],
        bindings={str(p):sha(p)for p in [Path(__file__),Path(K.__file__),Path(T.__file__),R/'tools/audit/private_build_outputs_v1.py',R/'tools/audit/verify_native_relocation.py',P/'source-stage.json',P/'component.bin',P/'component.lbl',O/'lab-isr.s',O/'lab-isr.bin',O/'lab-build.json']})
    dump(O/'controls.json',result);print(json.dumps(dict(result='PASS',pairs=pairs,labvectors=vcases,controls_sha256=sha(O/'controls.json'))))

if __name__=='__main__':main()
