"""Execute projected Thomas C2 cold/accepted-frame source against original code."""
from pathlib import Path
import argparse,copy,hashlib,itertools,json,random,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).resolve().parent))
import thomas_original_cpu_1031_v1 as T
from verify_native_relocation import NesMPU
P=R/'build/thomas-c2-eight-component-v1';O=R/'build/thomas-c2-eight-controls-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
dump=lambda p,v:Path(p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
FLAGS=[0x30|(i&3)|(i&4)|(i&8)|((i&16)<<2)|((i&32)<<2)for i in range(64)]

class C2Bus(T.Bus):
    def __init__(self):
        super().__init__(T.donor());self.c2=bytearray(0x820);self.private_writes=[];self.pc=0;self.logical=bytearray(16);self.working=bytearray(16);self.instruction_map={};self.pointer_inverse={};self.commit_pc=-1
    def __getitem__(self,key):
        if isinstance(key,int)and 0xc000<=key<0xc820:return self.c2[key-0xc000]
        return super().__getitem__(key)
    def __setitem__(self,key,v):
        if isinstance(key,int)and 0xc000<=key<0xc820:
            index=key-0xc000;self.c2[index]=v&255
            if index<16:self.logical[index]=self.working[index] if self.pc==self.commit_pc else v&255
            self.writes.append((key,v&255));self.private_writes.append((self.pc,key,v&255));return
        if isinstance(key,int)and 0<=key<16 and self.pc in self.instruction_map:
            native=self.instruction_map[self.pc];self.working[key]=v&255
            if native in [0xa842,0xa915,0xa923]:
                low=key-1;pointer=self[low]|((v&255)<<8)
                assert pointer in self.pointer_inverse,('actual complete sourcepointer',hex(native),hex(pointer))
                self.working[low:low+2]=self.pointer_inverse[pointer].to_bytes(2,'little')
            elif native in [0x84fc,0x8505,0x850d]:
                assert key==1 and 0xc0<=v<=0xc8
                self.working[key]=v-0xc0
        super().__setitem__(key,v)

def main():
    global P,O
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,default=P);ap.add_argument('--output',type=Path,default=O);a=ap.parse_args();P=a.source.resolve();O=a.output.resolve();assert not O.exists();O.mkdir(parents=True)
    stage=json.loads((P/'source-stage.json').read_text(encoding='utf-8'))
    for p,h in stage['bindings'].items():assert sha(p)==h,p
    syms=T.labels(P/'component.lbl');image=(P/'component.bin').read_bytes()
    inverse={v:int(n[3:],16)for n,v in syms.items()if n.startswith('Th_')}
    for prefix in ['ThHealth_','ThGeom_','ThCold_','ThController_','ThTimers_','ThFrameReset_']:
        inverse.update({v:int(n[len(prefix):],16)for n,v in syms.items()if n.startswith(prefix)})
    inverse.update({v:int(n[7:],16)for n,v in syms.items()if n.startswith('ThData_')})
    def candidate(seed=0):
        b=C2Bus();b.instruction_map={v:k for v,k in inverse.items()if k>=0x8000};b.pointer_inverse=inverse;b.commit_pc=syms['ThomasC2Return']+4;list.__setitem__(b,slice(0x6000,0x8000),image)
        rng=random.Random(seed)
        list.__setitem__(b,slice(0,2048),[rng.randrange(256)for _ in range(2048)])
        b.c2[:0x800]=bytes(rng.randrange(256)for _ in range(2048))
        # Explicit owner-acquired idle transaction context, not seeded Thomas data.
        b.c2[0x800:]=bytes(32);b.logical[:]=b.c2[:16]
        return NesMPU(memory=b,pc=0x6000)
    def invoke(c,name,a=0,x=0,y=0,p=0x30,sp=0xe0):
        c.a,c.x,c.y,c.p,c.sp=a,x,y,p,sp;c.stPushWord(0x5ffe);c.pc=syms[name];c.memory.writes=[];c.memory.private_writes=[]
        count=0;low=c.sp;cycles=c.processorCycles
        while c.pc!=0x5fff:
            c.memory.pc=c.pc
            if c.pc==syms['ThomasC2Borrow']:c.memory.working[:]=c.memory.logical
            c.step();low=min(low,c.sp);count+=1;assert count<40000,(name,hex(c.pc))
        assert(c.a,c.x,c.y,c.p,c.sp)==(a,x,y,p,sp),(name,'callerAXYP',c.a,c.x,c.y,c.p,c.sp,a,x,y,p,sp)
        return c.processorCycles-cycles,low,count
    def projected(c,normalize=True):
        b=bytearray(c.memory.c2[:2048])
        b[:16]=c.memory.logical
        return bytes(b[:256]+b[512:])
    def reference(c):return bytes(c.memory[:256]+c.memory[512:2048])
    def original_hunk(c,start,stop,*,x=None,a=None):
        c.pc=start
        if x is not None:c.x=x
        if a is not None:c.a=a
        c.sp=0xe0;count=0
        while c.pc!=stop:
            if c.pc==0xacdf: # Native enemy actor update excluded from this actor boundary.
                c.pc=(c.stPopWord()+1)&65535;continue
            c.step();count+=1;assert count<20000,(hex(start),hex(c.pc))
    def native_cold(floor,player):
        c=T.machine();c.memory[0x55]=player;c.memory[0x5f]=floor
        T.run(c,0x84f0);T.run(c,0x8563);c.memory[0x52]=0;T.run(c,0xa8eb)
        return c
    def native_frame(c,pad):
        original_hunk(c,0x830d,0x8319)
        original_hunk(c,0x8321,0x8338)
        T.run(c,0x9002,a=pad,x=c.memory[0x55])
        c.memory[0x6a]=c.memory[0x14+c.memory[0x55]*2]
        original_hunk(c,0x87b5,0x87e0)
        T.run(c,0xa826)
        if c.memory[0x38f]:T.run(c,0xa8eb)
    def unchanged_host(c,before):
        after=bytes(c.memory[:2048]);assert after[:256]==before[:256]and after[512:]==before[512:],'HostRAM changed outside selected state'
        assert not c.memory.apu and not c.memory.ppuwrites,'Private source touched APU/PPU'
        assert all(a<0xc818 for pc,a,v in c.memory.private_writes),'Eight-byte context exceededC817'
    cold_pairs=0;cycles=[];minsp=255
    for floor,player,p in itertools.product(range(5),range(2),FLAGS):
        c=candidate(cold_pairs);before=bytes(c.memory[:2048]);r=native_cold(floor,player)
        q,sp,_=invoke(c,'ThomasC2ColdInit',floor,player,0xf9,p);cycles.append(q);minsp=min(minsp,sp)
        assert projected(c)==reference(r),('cold',floor,player,[(i,r.memory[i],c.memory.c2[i])for i in range(2048)if not 256<=i<512 and r.memory[i]!=c.memory.c2[i]][:15])
        assert c.memory.c2[0x800]==0xa7 and c.memory.c2[0x801]==0 and c.memory.c2[0x804]==0
        assert c.memory.c2[0x805]==r.memory[0x52]
        assert c.memory.private_writes[-1][1:]==(0xc800,0xa7),'Ready not last'
        unchanged_host(c,before);cold_pairs+=1
    # True original routines in this finite actor boundary; no native enemy,
    # terrain, deathscript, renderer or hardware NMI routine is intercepted as PASS.
    policies=[('walk-right',[1]*60+[0]*12),('reverse',[1]*30+[2]*45+[0]*12),
        ('jump',[8]*3+[0]*60),('crouch',[4]*30+[0]*12),
        ('punch',[0]*2+[64]*6+[0]*40),('kick',[0]*2+[128]*6+[0]*40),
        ('crouchpunch',[4]*2+[68]*6+[4]*40),('crouchkick',[4]*2+[132]*6+[4]*40),
        ('airpunch',[8]*3+[0]*7+[64]*4+[0]*50),('airkick',[8]*3+[0]*7+[128]*4+[0]*50)]
    frames=0;actions=set();trace=['floor,player,policy,index,pad,epoch,state,phase,xlo,xhi,y,hp,pose,cycles']
    for floor,player,(name,policy)in itertools.product([0,1],range(2),policies):
        c=candidate(0x1234+frames);before=bytes(c.memory[:2048]);r=native_cold(floor,player);invoke(c,'ThomasC2ColdInit',floor,player,0xf9)
        epoch=0xf9;pose=r.memory[0x52]
        for index,pad in enumerate(policy):
            epoch=(epoch+1)&255;native_frame(r,pad);q,sp,_=invoke(c,'ThomasC2AcceptedFrame',pad,1,epoch,FLAGS[index%64]);minsp=min(minsp,sp)
            assert projected(c)==reference(r),('frame',floor,player,name,index,[(i,r.memory[i],c.memory.c2[i])for i in range(2048)if not 256<=i<512 and r.memory[i]!=c.memory.c2[i]][:15])
            if r.memory[0x52]:pose=r.memory[0x52]
            assert c.memory.c2[0x805]==pose and not c.memory.c2[0x801]
            actions.add(r.memory[0x69]&0x3e);unchanged_host(c,before)
            trace.append(','.join(map(str,[floor,player,name,index,pad,epoch,r.memory[0x69],r.memory[0x68],r.memory[0xd4],r.memory[0xe5],r.memory[0xb6],r.memory[0x4a6],pose,q])))
            # Duplicate, unaccepted and busy calls preserve every C2 byte.
            for accept,ep,busy in [(1,epoch,0),(0,(epoch+1)&255,0),(1,(epoch+1)&255,1)]:
                c.memory.c2[0x801]=busy;snapshot=bytes(c.memory.c2)
                invoke(c,'ThomasC2AcceptedFrame',pad^255,accept,ep,FLAGS[index%64])
                assert bytes(c.memory.c2)==snapshot and not c.memory.private_writes,('nonaccepted mutates state',accept,ep,busy)
            c.memory.c2[0x801]=0;frames+=1
    assert {0,2,4,16,18,20,32,34,36}.issubset(actions),actions
    (O/'accepted-trace.csv').write_text('\n'.join(trace)+'\n',encoding='utf-8')
    result=dict(result='PASS',scope='Isolated C2 projected-source cold and accepted actor-boundary CPU controls; no current-host/native/IRQ qualification',
        cpu_model='verify_native_relocation.NesMPU: P.D preserved, ADC/SBC alwaysbinary',cold_original_source_pairs=cold_pairs,
        accepted_frame_pairs=frames,duplicate_unaccepted_busy_inert_checks=frames*3,actual_stances=sorted(actions),
        private_state_bytes=2048,private_transaction_bytes=24,borrowed_zp_bytes=8,all_hostZP_restored=True,caller_AXYP_SP_exact=True,
        full64_physical_flag_patterns='B/U canonical30hex; C/Z/I/D/V/N variedexhaustively',cold_cycles=[min(cycles),max(cycles)],minimumSP=minsp,
        pose_API='Original69/68/52 state and generated originalpose command projected exactly; lastnonzero body command latched locally',
        projection='DirectnativeRAM mapsC000+address, stackpage1excluded;16scratchbytes comparedthrough instruction-provenance observer. Only complete pointerwriters A842/A915/A923 rebindtheir truepair;clear-pointer highwriters84FC/8505/850D project C3..C8. Laterpartial/scalaroverwrites preserve eachbyteprovenance; no genericwordnormalization.',
        exclusions=['C2addresses labonly,nohostlease','Nativeworld/actor/contact/deathscript absent from acceptedboundary','No audio execution; actualnativeFB..FFqueue state retained','NoPPU/APU/mapper/NMI hardware writes or native emulator run'],
        future_terrain_base=stage['future_terrain_base'],
        bindings={str(p):sha(p)for p in [Path(__file__),Path(T.__file__),R/'tools/audit/verify_native_relocation.py',P/'source-stage.json',P/'component.bin',P/'component.lbl',O/'accepted-trace.csv']})
    dump(O/'controls.json',result)
    print(json.dumps(dict(result='PASS',cold_pairs=cold_pairs,accepted_frame_pairs=frames,controls_sha256=sha(O/'controls.json'))))

if __name__=='__main__':main()
