"""Actual original FF27/8BCF vs composed native actor, aggregate receipts."""
from pathlib import Path
import hashlib,itertools,json,random,sys,traceback
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/audit'),str(ROOT/'tools')]
import metal_storm_cpu_1101_v2 as M
import prepare_metal_storm_objects_host_1101_v6 as P
from verify_native_relocation import NesMPU
OUT=P.OUT
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

class Mem(bytearray):
    def __init__(self):super().__init__(65536);self.writes=[]
    def __setitem__(self,k,v):
        if isinstance(k,int):self.writes.append(k)
        super().__setitem__(k,v)

def main():
    q=dict(passed=False,source_CPU=True,native=False,installed=False,admitted=False)
    try:
        stage=json.loads((OUT/'assembly.json').read_text())
        for p,h in stage['bindings'].items():assert sha(p)==h,p
        lab=stage['labels'];f=stage['source_fields'];binary=(OUT/'objects.bin').read_bytes()
        v5=json.loads((P.V5/'CPU-controls.json').read_text());assert v5['passed']
        rng=random.Random(0x110106);digest=hashlib.sha256();minsp=224;maxcycles=0;excluded={}
        compare=[i for i in range(2048)if not(0x180<=i<0x200 or 0x300<=i<0x480)and i not in[0x6e,0x6f,0x7fe,0x7ff]]
        def original(initial=None):
            c=M.machine();m=c.memory;m.regs[6:8]=[0,1];m.map()
            if initial is not None:m[:2048]=initial
            return m
        def native(initial=None):
            m=Mem();m[0xa000:0xa000+len(binary)]=binary;m[:256]=bytes((i*29+13)&255 for i in range(256))
            if initial is not None:m[0xc000:0xc800]=initial
            # These are controlled terrain inputs, not a copied native ROM.
            # Exact native helper/all256attributes were proved by frozenv5.
            m[f['BlockBufferAddr']:f['BlockBufferAddr']+4]=bytes([0,0xd0,3,3]);m[f['MTileAttribute']+0x61]=1
            return m
        def run(m,pc,a=85,x=7,y=91,p=0x71,ports=(),stop=None,limit=50000):
            nonlocal minsp,maxcycles
            c=NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=a,x,y,p,224;c.stPushWord(0x5ffe);start=c.processorCycles;order=[]
            for _ in range(limit):
                if c.pc==0x5fff:break
                minsp=min(minsp,c.sp)
                if c.pc==stop:c.pc=(c.stPopWord()+1)&65535;continue
                if c.pc in ports:
                    excluded[f'{c.pc:04X}']=excluded.get(f'{c.pc:04X}',0)+1;c.pc=(c.stPopWord()+1)&65535;continue
                if c.pc in[0xdcd8,lab['MsObj_DCD8']]:order.append(c.x)
                assert m[c.pc]!=0,('BRK',hex(c.pc));c.step()
            else:raise AssertionError(('bound',hex(c.pc)))
            assert c.sp==224;maxcycles=max(maxcycles,c.processorCycles-start)
            return(c.a,c.x,c.y,c.p&0xcf,c.sp),order
        def terrain(om,nm,shape):
            for row,col in itertools.product(range(15),range(20)):
                solid=(row>=13 if shape=='floor'else row==4 if shape=='ceiling'else col==6 if shape=='wall'else False)
                om[0x300+row*20+col]=0xf8 if solid and row>=2 else 0
                if row>=2:
                    page=col//16;off=0x300+page*208+(row-2)*16+(col&15)
                    nm[off]=0x61 if solid else 0
            for row,col in itertools.product(range(2,15),range(20,32)):
                solid=(row>=13 if shape=='floor'else row==4 if shape=='ceiling'else col%20==6 if shape=='wall'else False)
                nm[0x300+(col//16)*208+(row-2)*16+(col&15)]=0x61 if solid else 0
        # Genuine bank routine's state/AXYP retained, native mapper writes
        # redirected into two private log bytes. No emulated host remapping.
        bankpairs=0
        for bank,p in itertools.product(range(16),[0x30,0x71]):
            om=original();nm=native();om[0x3a]=nm[0xc03a]=bank
            ar,_=run(om,0xd783,a=bank,p=p);nr,_=run(nm,lab['MsObj_D783'],a=bank,p=p)
            assert ar==nr and all(om[i]==nm[0xc000+i]for i in[0x3a,0x58,0x5d,0x5e])
            assert nm[0xc818]==7 and nm[0xc819]==bank*2+1;bankpairs+=1
        q['original_bank_state_pairs']=bankpairs
        controlpairs=0;om=original();nm=native()
        for one,two,saved in itertools.product([0,1,0x7f,0x80,0xff],[0,1,0x7f,0x80,0xff],[0,0x80,0xff]):
            for field,v in[(0x119,one),(0x11a,two),(0x11f,saved)]:om[field]=v;nm[0xc000+field]=v
            ar,_=run(om,0xfc5e,stop=0xfc8e);nr,_=run(nm,lab['MsObj_FC5E'])
            assert ar==nr and all(om[i]==nm[0xc000+i]for i in[0x119,0x11a,0x11f])
            assert om[0x119]^0x80==om[0x11a]and not((om[0x119]|om[0x11a])&0x7f);controlpairs+=1
        q['original_reset_control_pairs']=controlpairs
        def original_mask(m,p=0x71):
            oldregs=m.regs[6:8];oldptr=(m[0x26],m[0x27]);m.regs[6:8]=[12,13];m.map()
            table=m[0x800e]+256*m[0x800f];meta=m[table]+256*m[table+1];m[0x26]=meta&255;m[0x27]=meta>>8
            run(m,0xf2ea,x=0,p=p,stop=0xf2f8)
            m[0x26],m[0x27]=oldptr;m.regs[6:8]=oldregs;m.map()
        maskpairs=0
        for state,p in itertools.product(range(8),[0x30,0x71]):
            om[0x4e0]=state;nm[0xc4e0]=state;original_mask(om,p)
            r,_=run(nm,lab['MsNativeAnimationMask'],p=p)
            assert nm[0xc5a0]==om[0x5a0]and r[:4]==(85,7,91,p&0xcf)
            maskpairs+=1
        q['original_renderer_mask_pairs']=maskpairs
        # Whole genuine FF27; object order, signed movement, normal/upgraded
        # contacts, window retirement and frame animation execute directly.
        objectpairs=responses=retired=clockwraps=0
        for shape,typ,world,yy,motion in itertools.product(['air','floor','ceiling','wall'],[0x80,0x81],[8,80,95,255,319,320,400,-16],[31,64,100,207,239,260],[(12,0),(-12,0),(0,12),(0,-12)]):
            initial=bytearray(2048);initial[0x732]=255;initial[0x733]=7;initial[0x43f]=128;initial[0x53]=objectpairs&255
            initial[0x482]=world&255;initial[0x49a]=(world>>8)&255;initial[0x4b2]=yy&255;initial[0x4ca]=(yy>>8)&255
            initial[0x512]=128;initial[0x52a]=typ;initial[0x602]=0x0a
            initial[0x55a]=motion[0]&255;initial[0x572]=motion[1]&255;initial[0x542]=128 if motion[1]>0 else 64 if motion[0]<0 else 0
            initial[0x4e2]=128 if typ==0x81 else 0;initial[0x58a]=128;initial[0x5a2]=3
            om=original(initial);nm=native(initial);terrain(om,nm,shape);z=bytes(nm[:256])
            ar,ao=run(om,0xdcae);nr,no=run(nm,lab['MsObj_DCAE'])
            assert ar==nr,('objectAXYP',shape,typ,world,yy,motion,ar,nr)
            assert ao==no==list(range(23,0,-1)),('objectorder',ao,no)
            diffs=[(hex(i),om[i],nm[0xc000+i])for i in compare if om[i]!=nm[0xc000+i]]
            assert not diffs,('objectstate',shape,typ,world,yy,motion,diffs[:12])
            assert all(nm[i]==z[i]for i in range(256)if i not in[3,4])
            if om[0x61a]&128:responses+=1
            if not om[0x512]:retired+=1
            assert om[0x53]==(initial[0x53]+1)&255
            clockwraps+=not om[0x53]
            digest.update(bytes(om[i]for i in compare));objectpairs+=1
        assert responses and retired
        q.update(original_FF27_pairs=objectpairs,projectile_terrain_responses=responses,original_window_retirements=retired,source_clock_wraps=clockwraps,object_order_23_to_1=True)
        # Preflight rejects unsupported source objects atomically before actor.
        guardcases=rejects=0
        for slot,active,typ,flags,gravity in itertools.product(range(1,24),[0,128],[0,0x80,0x81,0x82],[0x0a,0x40],[0,128]):
            nm=native(bytes(2048));nm[0xc510+slot]=active;nm[0xc528+slot]=typ;nm[0xc600+slot]=flags;nm[0xc6a8+slot]=gravity
            before=bytes(nm[0xc000:0xc81a]);r,_=run(nm,lab['MsNativeObjectsReady'])
            want=not active or(slot<4 and typ in[0x80,0x81]and flags==0x0a and not gravity)
            assert bool(r[3]&1)==want and r[:3]==(85,7,91)
            assert bytes(nm[0xc000:0xc81a])==before
            guardcases+=1;rejects+=not want
        q['object_preflight_cases']=guardcases;q['object_preflight_rejections']=rejects
        # Composed constructor -> real actor -> real FF27 +8BCF -> native delta.
        # Unported scene/map/audio APIs are EXPLICIT effect-free test boundaries
        # in BOTH engines. Their game behavior/native admission is not claimed.
        oldports={0x8874,0x9ed7,0xff18,0xff39};newports={0x5000,0x5006,0x5009,0x5018}
        frames=duplicates=paused=constructed=0;gravityset=set();shotseen=set();clockwrap=False
        for axis in['walk','jump','reverse','shoot-right','shoot-up','shoot-down']:
            nm=native(bytes([0x5a])*2048)
            for n,v in dict(Player_X_Position=72,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1,SelectedCharacter=35,OperMode=1,GameEngineSubroutine=8,GamePauseStatus=0).items():nm[f[n]]=v
            nm[0xc732]=255;nm[0xc733]=7;nm[3],nm[4]=0xa5,0x5a
            setup=original();terrain(setup,nm,'floor')
            r,_=run(nm,lab['MsNativeConstruct']);assert r[3]&1;constructed+=1
            om=original(bytes(nm[0xc000:0xc800]));terrain(om,nm,'floor')
            for tick in range(96):
                pad=(1 if tick<48 else 2)if axis=='walk'else (0x81 if tick%48<20 else 1)if axis=='jump'else (0x88 if tick in[4,5]else 0x84 if tick in[48,49]else 0)if axis=='reverse'else 0x40 if axis=='shoot-right'else 0x48 if axis=='shoot-up'else 0x44
                nm[f['SavedJoypadBits']]=pad;nm[f['FrameCounter']]=(tick+200)&255
                clock=om[0x53];before=bytes(nm[0xc000:0xc800]);nativebefore=(nm[f['Player_PageLoc']]*256+nm[f['Player_X_Position']],nm[f['Player_Y_HighPos']]*256+nm[f['Player_Y_Position']])
                ar,_=run(om,0xad8c,ports=oldports);original_mask(om);nr,_=run(nm,lab['MsHostStep'],ports=newports)
                assert nr[:4]==(85,7,91,0x41),('step ABI',axis,tick,nr)
                om[0x31]=int(f'{pad:08b}'[::-1],2)
                diffs=[(hex(i),om[i],nm[0xc000+i])for i in compare if om[i]!=nm[0xc000+i]]
                assert not diffs,('composedstate',axis,tick,diffs[:12])
                assert om[0x53]==(clock+1)&255;clockwrap|=om[0x53]==0
                assert nm[3]==0xa5 and nm[4]==0x5a
                deltax=nm[0xc803]+256*nm[0xc804];deltay=nm[0xc805]+256*nm[0xc806]
                run(nm,lab['MsNativeApplyDelta'])
                assert(nm[f['Player_PageLoc']]*256+nm[f['Player_X_Position']],nm[f['Player_Y_HighPos']]*256+nm[f['Player_Y_Position']])==((nativebefore[0]+deltax)&65535,(nativebefore[1]+deltay)&65535)
                sourcebefore=bytes(nm[0xc000:0xc800]);run(nm,lab['MsHostStep'],ports=newports);run(nm,lab['MsNativeApplyDelta']);assert bytes(nm[0xc000:0xc800])==sourcebefore;duplicates+=1
                nm[f['GamePauseStatus']]=1;nm[f['FrameCounter']]=(tick+201)&255;run(nm,lab['MsHostStep'],ports=newports);assert bytes(nm[0xc000:0xc800])==sourcebefore;nm[f['GamePauseStatus']]=0;paused+=1
                frames+=1;gravityset.add(om[0x734]);digest.update(bytes(om[i]for i in compare))
                for slot in[2,3]:
                    if om[0x510+slot]:shotseen.add(slot)
        assert gravityset=={0,128}and shotseen=={2,3},(gravityset,shotseen,frames,excluded)
        q.update(composed_constructors=constructed,composed_actor_frames=frames,duplicate_epoch_cases=duplicates,paused_cases=paused,gravity_directions=sorted(gravityset),source_shot_slots=sorted(shotseen),excluded_scene_audio_calls=excluded)
        atomic=0
        for slot,typ,flags,g in[(1,0x82,0x0a,0),(2,0x80,0x40,0),(3,0x80,0x0a,128),(4,0x80,0x0a,0),(23,0x80,0x0a,0)]:
            nm[0xc510+slot]=128;nm[0xc528+slot]=typ;nm[0xc600+slot]=flags;nm[0xc6a8+slot]=g
            before=bytes(nm[0xc000:0xc81a]);r,_=run(nm,lab['MsHostStep'],ports=newports)
            assert r[:4]==(85,7,91,0x40)and bytes(nm[0xc000:0xc81a])==before
            nm[0xc510+slot]=0;atomic+=1
        q['composed_unsupported_object_atomic_rejections']=atomic
        nm[0xc717]=128;before=bytes(nm[0xc000:0xc81a]);r,_=run(nm,lab['MsHostStep'],ports=newports)
        assert r[:4]==(85,7,91,0x40)and bytes(nm[0xc000:0xc81a])==before;nm[0xc717]=0
        q['unsupported_GravityFire_rejected_before_spawn']=True
        actual=M.boot();opening={}
        for tick in range(526):
            def observe(c):
                if c.pc==0xad8c and not opening:opening.update(frame=tick,control119=c.memory[0x119],control11A=c.memory[0x11a],saved11F=c.memory[0x11f],animation5A0=c.memory[0x5a0])
            M.frame(actual,16 if tick in[120,121,300,301,480,481]else 0,trace=observe)
        assert opening and(opening['control119'],opening['control11A'])==(0,128)
        q['actual_donor_first_actor']=opening
        q.update(passed=True,kernel_bytes=len(binary),remaining_before_cookie=8160-len(binary),minimum_standalone_SP=minsp,max_standalone_cycles=maxcycles,aggregate_sha256=digest.hexdigest(),native_ROM_read=False,donor_RAM_snapshot_constructor=False,scope='Original FF27 order/clock/negative projectile motion/contact/retirement and8BCF empty platform pass composed with ctor/terrain/actor. Source enemy/meta/GravityFire, scene/audio effects, Main/ISR/SMC/native display/lifecycle not admitted.')
        q['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),Path(P.__file__),Path(M.__file__),M.ROM,P.REF,P.V5/'CPU-controls.json',OUT/'assembly.json',OUT/'objects.bin',OUT/'objects.dbg']}
    except Exception:
        q['error']=traceback.format_exc();raise
    finally:
        (OUT/'CPU-controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['error','bindings','excluded_scene_audio_calls']}))
if __name__=='__main__':main()
