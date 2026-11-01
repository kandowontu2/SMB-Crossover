"""Aggregate original/native constructor and gravity-contact CPU controls.

No native menu, loader, renderer, cycle/PPU/audio or final Main stack admission.
"""
from pathlib import Path
import hashlib,itertools,json,random,sys,traceback
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/audit'),str(ROOT/'tools')]
import metal_storm_cpu_1101_v2 as M
import prepare_metal_storm_terrain_host_1101_v5 as P
from verify_native_relocation import NesMPU
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import Memory,address,location
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
        b=scoped_load(P.NATIVE);lab=stage['labels'];f=stage['source_fields']
        donor=M.machine();donor.memory.regs[6:8]=[0,1];donor.memory.map();original=bytes(donor.memory[0x8000:])
        kernel=(OUT/'terrain.bin').read_bytes();rng=random.Random(0x110105)
        attrs=b['raw'][location(b,'MTileAttribute'):location(b,'MTileAttribute')+256]
        native0=b['raw'][16+126*8192:16+127*8192];native3=b['raw'][16+127*8192:16+128*8192]
        events={};digest=hashlib.sha256();minsp=224;maxcycles=0
        def new(initial=None):
            m=Mem();m[0x8000:0xa000]=native0;m[0xe000:]=native3;m[0xa000:0xa000+len(kernel)]=kernel
            m[:256]=bytes((i*19+7)&255 for i in range(256))
            if initial is not None:m[0xc000:0xc800]=initial
            return m
        def run(m,pc,a=0x55,x=7,y=91,p=0x71,stop=None,callbacks=None,limit=25000):
            nonlocal minsp,maxcycles
            c=NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=a,x,y,p,224;c.stPushWord(0x5ffe);start=c.processorCycles
            for steps in range(limit):
                minsp=min(minsp,c.sp)
                if c.pc==0x5fff:break
                if c.pc==stop:c.pc=(c.stPopWord()+1)&65535;continue
                if callbacks and c.pc in callbacks:
                    callbacks[c.pc](m,c);c.pc=(c.stPopWord()+1)&65535;continue
                assert m[c.pc]!=0,('BRK',hex(c.pc));c.step()
            else:raise AssertionError(('bound',hex(c.pc)))
            assert c.sp==224;maxcycles=max(maxcycles,c.processorCycles-start)
            return(c.a,c.x,c.y,c.p&0xcf,c.sp)
        # All small original leaves are differential against original donor
        # instructions, not callback-effect replay or rewritten formulas.
        leafcases=0
        for pc,name in[(0xe2c4,'MsNativeFF33'),(0xe2e7,'MsNativeFF36'),(0xda71,'MsNativeFF3F'),(0x911b,'MsCtor_911B'),(0x9431,'MsCtor_9431'),(0x943c,'MsCtor_943C')]:
            for k in range(512):
                initial=bytes(rng.randrange(256)for _ in range(2048));a,x,y,p=0x55,7,k%24,0x30|(k&1)|((k&2)<<5)
                old=Mem();old[0x8000:]=original;old[:2048]=initial
                n=new(initial);r0=bytes(n[:256]);old.writes=[];n.writes=[]
                ar=run(old,pc,a,x,y,p);nr=run(n,lab[name],a,x,y,p)
                assert ar==nr,(name,ar,nr)
                assert all(old[i]==n[0xc000+i]for i in range(2048)if not 0x180<=i<0x200),name
                assert bytes(n[:256])==r0
                assert all(0xc000<=v<0xc800 or 0x100<=v<0x200 for v in n.writes),name
                digest.update(bytes(old[:2048]));leafcases+=1
        q['original_leaf_pairs']=leafcases
        # Actual emitted native BlockBufferCollision, independent from bridge.
        # Every metatile, both buffer parities, and every one of13native rows.
        helper=Memory(b);hm=new();helpercases=0
        for tile,page,row in itertools.product(range(256),[0,1],range(13)):
            sx=(tile*37+row*13)&255;sy=32+16*row+(tile&15)
            for m in[helper,hm]:
                m[0x300:0x4a0]=bytes(416)
                m[0x300+(0xd0 if page else 0)+row*16+(sx>>4)]=tile
            # Probe0's actual8/4adders are compensated, preserving a page borrow.
            world=page*256+sx-8
            helper[f['Player_X_Position']]=world&255;helper[f['Player_PageLoc']]=(world>>8)&255
            helper[f['Player_Y_Position']]=(sy-4)&255
            rr=run(helper,address(b,'BlockBufferCollision'),a=0,x=0,y=0,p=0x30)
            assert rr[0]==tile and helper[address(b,'R3')]==tile
            hm[0xc059]=sx;hm[0xc05a]=page;hm[0xc05b]=sy;hm[0xc732]=255;hm[0xc733]=1
            z=bytes(hm[:256]);app=bytes(hm[0x300:0x4a0]);hm.writes=[]
            nr=run(hm,lab['MsNativeTileQuery'],x=7)
            flags=0xe0 if attrs[tile]&3==1 else 0
            assert hm[0xc810]==flags and hm[0xc811]==tile
            assert nr[1]==7 and nr[2]==0 and hm[3]+256*hm[4]==0xc810
            assert bytes(hm[:3])==z[:3]and bytes(hm[5:256])==z[5:]
            assert bytes(hm[0x300:0x4a0])==app
            assert all(i in[3,4]or 0x100<=i<0x200 or 0xc810<=i<=0xc812 for i in hm.writes)
            helpercases+=1;digest.update(bytes([tile,page,row,flags]))
        q['actual_native_lookup_pairs']=helpercases
        negative=0
        for xx,yy in[(-1,100),(512,100),(255,31),(255,240),(255,255),(256,100)]:
            hm[0xc059]=xx&255;hm[0xc05a]=(xx>>8)&255;hm[0xc05b]=yy;hm[0xc732]=255;hm[0xc733]=0
            hm[0xc810]=0xe0;run(hm,lab['MsNativeTileQuery']);assert hm[0xc810]==0;negative+=1
        q['out_of_domain_rejections']=negative
        # Original pure constructor9371..93EC,17valid original spawn profiles.
        # These have nonzeroY; the separate native placement controls coverY0.
        profiles=[i for i in range(33)if original[0x8b4c-0x8000+2*i]];ctorpairs=0
        for profile in profiles:
            for p in[0x30,0x71]:
                initial=bytearray(rng.randrange(256)for _ in range(2048));initial[0x50]=0;initial[0x51]=profile;initial[0x43a]=0;initial[0x42e]=0
                old=Mem();old[0x8000:]=original;old[:2048]=initial;n=new(initial);z=bytes(n[:256])
                ar=run(old,0x9371,p=p,stop=0x93ed);nr=run(n,lab['MsCtor_9371'],p=p)
                assert ar==nr and all(old[i]==n[0xc000+i]for i in range(2048)if not 0x180<=i<0x200),('ctor',profile,ar,nr)
                assert bytes(n[:256])==z;ctorpairs+=1
        q['original_pure_constructor_pairs']=ctorpairs
        # Native initial placement: exact donor scan against matching columns.
        # Source map stride20 and native stride16 are intentionally different.
        placementcases=0
        for floorrow,depth in itertools.product(range(2,13),[1,2]):
            old=Mem();old[0x8000:]=original;old[0x480]=0x48;n=new();n[0xc480]=0x48;n[0xc732]=255;n[0xc733]=1
            n[0x300:0x4a0]=bytes(416)
            for yy in range(32+floorrow*16,min(240,32+(floorrow+depth)*16),16):
                addr=0x300+4+(yy//16)*20;assert 0x300<=addr<0x480;old[addr]=0xe0
                n[0x300+((yy-32)//16)*16+4]=0x61
            if floorrow==12:continue #Y224 is below original scan'sD0start.
            run(old,0x944a);r=run(n,lab['MsNativePlacement'])
            assert r[3]&1 and all(old[i]==n[0xc000+i]for i in[0x4b0,0x4c8,0x4e0,0x4f8,0x588]),('placement',floorrow,depth,old[0x4b0],n[0xc4b0])
            placementcases+=1
        n=new();n[0xc732]=255;n[0xc733]=1;n[0x300:0x4a0]=bytes([0x61])*416
        # HUD is empty, so an all-solid visible column still terminates.
        r=run(n,lab['MsNativePlacement']);assert r[3]&1
        n[0x300:0x4a0]=bytes(416);r=run(n,lab['MsNativePlacement']);assert not r[3]&1
        q['native_placement_pairs']=placementcases;q['bounded_empty_column_rejected']=True
        # Actual reset-equivalent algorithm, then real constructor leaves.
        # Private state begins poisoned. No donor snapshot or host RAM preload.
        nativectors=0
        for world,sy in itertools.product([8,40,255,256,511,1024],[32,80,144,176,208]):
            n=new(bytes([0x5a])*2048);n[0xc732]=0xff;n[0xc733]=7
            n[f['Player_X_Position']]=world&255;n[f['Player_PageLoc']]=world>>8;n[f['Player_Y_Position']]=sy;n[f['Player_Y_HighPos']]=1
            n[0x300:0x4a0]=bytes(416)
            for page in range(2):n[0x300+page*208+11*16:0x300+page*208+13*16]=bytes([0x61])*32
            n[3],n[4]=0xa5,0x5a;z=bytes(n[:256]);n.writes=[]
            r=run(n,lab['MsNativeConstruct']);assert r[:4]==(0x55,7,91,0x41)
            assert bytes(n[:256])==z and n[0xc800]==0xa7
            assert n[0xc480]+256*n[0xc498]==world-8 and n[0xc4b0]==sy and n[0xc4c8]==0
            assert n[0xc510]==128 and n[0xc734]==0 and n[0xc540]&0xc0==0 and n[0xc732]==255 and n[0xc733]==7
            assert n[0xc4e0]==7 and n[0xc4f8]==2 and n[0xc558]==0 and n[0xc570]==0
            assert all(i in[3,4]or 0x100<=i<0x200 or 0xc000<=i<0xc818 for i in n.writes)
            nativectors+=1
        q['native_constructor_cases']=nativectors
        for high in[0,2,255]:
            n[f['Player_Y_HighPos']]=high;before=bytes(n[0xc000:0xc800]);r=run(n,lab['MsNativeConstruct']);assert not r[3]&1 and bytes(n[0xc000:0xc800])==before and n[0xc800]==0
        q['constructor_bad_entry_rejections']=3
        # Original actor collision consumers plus the actual donor tile API,
        # against native bridge+unchanged actor on the same semantic terrain.
        # Both tests use original full-solidE0/air00, with donor20-column and
        # native16-column storage layouts. No callback tile-effect replay.
        contacts=0;contact_changes=0;gravities=set();sound_boundary=0
        def silent_boundary(m,c):
            nonlocal sound_boundary
            sound_boundary+=1 # external sound port deliberately unimplemented
        for shape,gravity,xx,yy,velocity in itertools.product(['floor','ceiling','wall','air'],[0,128],[64,68,72,92,96],[60,64,68,172,176,180],[-4,-1,1,4]):
            initial=bytearray(2048)
            initial[0x480]=xx;initial[0x4b0]=yy;initial[0x510]=128
            initial[0x558]=velocity&255;initial[0x570]=velocity&255
            initial[0x734]=gravity;initial[0x540]=gravity;initial[0x732]=255;initial[0x733]=0
            initial[0x4e0]=7;initial[0x4f8]=2;initial[0x730]=0x69
            old=Mem();old[0x8000:]=original;old[:2048]=initial;n=new(initial)
            for row,col in itertools.product(range(15),range(16)):
                solid=(row>=13 if shape=='floor'else row<=3 if shape=='ceiling'else col==6 if shape=='wall'else False)
                old[0x300+20*row+col]=0xe0 if solid else 0
                if row>=2:n[0x300+16*(row-2)+col]=0x61 if solid else 0
            # Donor terrain outside nativeHUD isair, not a fabricated ceiling.
            old[0x300:0x328]=bytes(40)
            for op,sourcepc in[('MsWalls',0xbb08),('MsSupport',0xb744)]:
                aold=Mem();aold[:]=old;anew=Mem();anew[:]=n;z=bytes(anew[:256])
                ar=run(aold,sourcepc,callbacks={0xff39:silent_boundary})
                nr=run(anew,lab[op],callbacks={stage['callbacks']['MsExternal_FF39']:silent_boundary})
                assert ar==nr,('consumerAXYP',shape,gravity,xx,yy,velocity,op,ar,nr)
                compare=[i for i in range(2048)if not(0x180<=i<0x200 or 0x300<=i<0x480)and i not in[0x6e,0x6f,0x7fe,0x7ff]]
                diffs=[(hex(i),aold[i],anew[0xc000+i])for i in compare if aold[i]!=anew[0xc000+i]]
                assert not diffs,('consumerstate',shape,gravity,xx,yy,velocity,op,diffs[:12])
                assert bytes(anew[:256])==z
                if any(aold[i]!=initial[i]for i in[0x480,0x498,0x4b0,0x4c8,0x5b8,0x618]):contact_changes+=1
                digest.update(bytes(aold[i]for i in compare));contacts+=1;gravities.add(gravity)
        assert contact_changes and gravities=={0,128}
        q['original_actor_native_terrain_pairs']=contacts;q['contact_response_cases']=contact_changes;q['gravity_directions']=sorted(gravities);q['excluded_sound_port_calls']=sound_boundary
        # Native/world displacement once, with source fractions never rewritten.
        delta=0
        for wx,wy,dx,dy in itertools.product([0,255,256,511],[0,255,256,511],[-257,-1,0,1,257],[-241,-1,0,1,241]):
            n[f['Player_X_Position']]=wx&255;n[f['Player_PageLoc']]=wx>>8;n[f['Player_Y_Position']]=wy&255;n[f['Player_Y_HighPos']]=wy>>8
            n[0xc802]=1;n[0xc801]=delta&255;n[0xc815]=0
            n[0xc803]=dx&255;n[0xc804]=(dx>>8)&255;n[0xc805]=dy&255;n[0xc806]=(dy>>8)&255
            before=bytes(n[0xc000:0xc800]);z=bytes(n[:256]);r=run(n,lab['MsNativeApplyDelta'])
            actual=(n[f['Player_X_Position']]+256*n[f['Player_PageLoc']],n[f['Player_Y_Position']]+256*n[f['Player_Y_HighPos']])
            assert actual==((wx+dx)&65535,(wy+dy)&65535)and r[:4]==(85,7,91,0x41)
            owned={f[k]for k in['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos']}
            assert bytes(n[0xc000:0xc800])==before and all(n[i]==z[i]for i in range(256)if i not in owned)
            snapshot=bytes(n);run(n,lab['MsNativeApplyDelta']);assert bytes(n[:0x100])==snapshot[:0x100]
            for field in['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos']:assert n[f[field]]==snapshot[f[field]]
            delta+=1
        q['once_only_world_delta_cases']=delta
        q.update(passed=True,ROM_sha256=sha(P.NATIVE),DBG_sha256=sha(P.NATIVE.with_suffix('.dbg')),kernel_bytes=len(kernel),remaining_before_cookie=8160-len(kernel),minimum_standalone_SP=minsp,max_standalone_cycles=maxcycles,aggregate_sha256=digest.hexdigest(),boundaries='Actual original actor support/wall consumers and donor FF1E/contact leaves vs compiled native bridge. Sound port is a declared excluded boundary. Whole source frame callbackFF27/Main/ISR/native PPU/renderer/menu not admitted.',no_native_RAM_or_ROM_snapshot=True)
        q['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),Path(P.__file__),Path(M.__file__),P.REF,P.NATIVE,P.NATIVE.with_suffix('.dbg'),OUT/'assembly.json',OUT/'terrain.bin',OUT/'terrain.dbg']}
    except Exception:
        q['error']=traceback.format_exc();raise
    finally:
        (OUT/'CPU-controls.json').write_text(json.dumps(q,indent=2)+'\n')
        print(json.dumps({k:v for k,v in q.items()if k not in['bindings','error']}))
if __name__=='__main__':main()
