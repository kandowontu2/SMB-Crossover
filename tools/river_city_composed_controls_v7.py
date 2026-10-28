"""Actual composed RCR caller, pixels, HUD queue and ISR controls; no native claim."""
from pathlib import Path
import hashlib,itertools,json,sys
R=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from river_city_pipe_contact_controls_v2 import fixture,position,pipe,step,state
from sunny_integrated_controls_v1 import seed,run,registers,app,cleanwrites,smc_at
from prepare_river_city_controls import address
from prepare_river_city_assets import POSES,decode
from prepare_river_city_reference import NATIVE,native_pixels
from verify_native_relocation import NesMPU
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    rom=R/'build/river-city-shared-v7.nes';assert sha(rom)=='a759278ddb162eee92a94a0aadd3346d44f2632de0a78661047d5d8cea5d6aba'
    target=R/'build/river-city-composed-controls-v7.json';assert not target.exists()
    proof_path=R/'build/river-city-shared-v7-overlay/build-proof.json';build=json.loads(proof_path.read_text())
    for z in build['bindings']:assert sha(z['path'])==z['sha256'],z['path']
    b=scoped_load(rom);old=scoped_load(R/'build/river-city-native-v2.nes');parent=scoped_load(R/'build/roster-union-celeste-mac-v1.nes')
    rows=[];costs=[]
    for variant,mode,face,kind,bits in itertools.product((0,1),(0,1),(1,2),('open','side','ceiling','floor'),(0,1,2,4,128,129,64,65)):
        pairs=[]
        for bundle in(old,b):
            q=fixture(bundle,variant,mode);pipe(q,736)
            x,y,vy=(721,142,4)if kind=='side'else(448,174,-7)if kind=='ceiling'else(448,174,4)if kind=='floor'else(448,96,0)
            if kind=='ceiling':
                from river_city_pipe_contact_controls_v2 import tile
                for xx in range(400,512,16):tile(q,xx,160,0xc4)
            position(q,x,y,vy,face,state=1);q.put(RcHudDirty=0,SavedJoypadBits=bits,Left_Right_Buttons=bits&3,A_B_Buttons=bits&192,
              Player_Rel_XPos=96,Player_Rel_YPos=y,ScreenRight_PageLoc=x//256,ScreenRight_X_Pos=255)
            c,w,_=run(q,'GameLoop',p=0x71);pairs.append((registers(c),app(q),q.m.banks,c.processorCycles))
        assert pairs[0][:3]==pairs[1][:3],('whole RCR caller',variant,mode,face,kind,bits,pairs[0][0],pairs[1][0])
        costs.append(pairs[1][3]-pairs[0][3]);rows.append(dict(check='complete_RCR_GameLoop_exact_application_state',variant=variant,mode=mode,face=face,arena=kind,bits=bits,CPU_delta=costs[-1]))
    profiles=[(0,'MarioVariant',0),(0,'MarioVariant',1),(8,'MarioVariant',1),(1,'ProtoVariant',0),(1,'ProtoVariant',1),(2,None,0),
      (3,'BillVariant',0),(3,'BillVariant',1),(4,'Z2Variant',0),(4,'Z2Variant',1),(5,'Cv3Variant',0),(5,'Cv3Variant',1),(5,'Cv3Variant',2),(5,'Cv3Variant',3),
      (6,None,0),(7,None,0),(9,'RlVariant',0),(9,'RlVariant',1),(10,None,0),(11,None,0),(12,'DarkwingVariant',0),(12,'DarkwingVariant',1),
      (13,'KbVariant',0),(13,'KbVariant',1),(14,'CdVariant',0),(14,'CdVariant',1),(15,'MacVariant',0),(15,'MacVariant',1),(15,'MacVariant',2),
      (16,None,0),(17,'M3Variant',0),(17,'M3Variant',1),(18,'VvVariant',0),(18,'VvVariant',1),(18,'VvVariant',2),(18,'VvVariant',3),
      (19,'TnVariant',0),(19,'TnVariant',1),(19,'TnVariant',2),(19,'TnVariant',3),(20,'IcVariant',0),(20,'IcVariant',1),(23,None,0)]
    for (char,key,variant),mode in itertools.product(profiles,(0,1)):
        pairs=[]
        for bundle in(parent,b):
            q=seed(bundle,char)
            if key:q.set(key,variant)
            q.put(CrossoverBehaviorVersion=mode,GameTimerDisplay=4,PlayerEntranceCtrl=2,SavedJoypadBits=1,Left_Right_Buttons=1)
            c,w,_=run(q,'GameLoop',p=0x71);pairs.append((registers(c),app(q),q.m.banks,cleanwrites(q,w),c.processorCycles))
        assert pairs[0]==pairs[1],('foreign wholecaller',char,key,variant,mode,pairs[0][0],pairs[1][0])
        rows.append(dict(check='foreign_GameLoop_full_state_writes_banks_CPU_exact',char=char,variant=variant,mode=mode))
    # Exact native-source opaque pixel classes, both faces/variants/outline modes.
    original=NATIVE.read_bytes();cb=16+1048576
    for variant,face,pose,outlines in itertools.product((0,1),(1,2),range(18),(0,1)):
        q=fixture(b,variant);q.put(PlayerFacingDir=face,PlayerOutlinesOff=1-outlines,OutlineSourceHi=204,OutlineTinyHi=204,CurrentOAMOffset=0)
        q.array('OutlineTinyHi',[204]*4);q.array('CurrentCHRBank',[99,100,101,102]);q.array('X5ChrMode',[129]*4)
        q.invoke('RcSetPose',x=pose);q.invoke('RcPublish');ptr=q.get('SmPosePtr')+256*q.get('SmPosePtr',1)
        q.put(R0=ptr&255,R1=ptr>>8,R3=0,R4=96,R5=0,R6=96,R7=1,GuestOamRotationActive=0)
        c,_=q.invoke('MetaspriteRenderLoop');assert c.p&1
        pixels={};count=q.get('CurrentOAMOffset')//4
        for part in range(count-1,-1,-1):
            tt,aa=q.get('Sprite_Tilenumber',part*4),q.get('Sprite_Attributes',part*4)
            xx,yy=q.get('Sprite_X_Position',part*4)-96,q.get('Sprite_Y_Position',part*4)-96
            window=tt//64;page=q.get('CurrentCHRBank',window)+256*(q.get('X5ChrMode',window)&3)
            at=cb+page*1024+(tt%64)*16;pattern=decode(b['raw'][at:at+32])
            for y in range(16):
                for x in range(8):
                    v=pattern[y][7-x if aa&64 else x]
                    if v:pixels[xx+x,yy+y]=1 if aa&3==3 else{1:3,2:2,3:4}[v]
        source,_,_=native_pixels(original,POSES[pose][1],variant,face)
        assert pixels=={p:v for p,v in source.items()if outlines or v!=1},(variant,face,pose,outlines)
        rows.append(dict(check='actual_render_original_pixel_classes',variant=variant,face=face,pose=pose,outlines=outlines,parts=count))
    # Exact real queue, not arbitrary tile replacement or another glyph lease.
    for variant,health,offset in itertools.product((0,1),range(65),(0,69,70,75,76,80,83)):
        q=fixture(b,variant);q.put(RcPalette=1,RcHudDirty=1,VRAM_Buffer1_Offset=offset);q.set('RcHealth',health,variant)
        at=address(b,'VRAM_Buffer1');q.m[at:at+88]=bytes([0xa5]*88);q.m[at+offset]=0
        q.invoke('RcUi');end=q.get('VRAM_Buffer1_Offset')
        if offset<76:
            assert bytes(q.m[at+offset:at+end+1])==bytes([0x20,0x23,4,0x11,0x19,health//10,health%10,0])
            assert q.get('RcHudDirty')==0
        else:assert end==offset and q.get('RcHudDirty')==1
        assert bytes(q.m[at+84:at+88])==bytes([0xa5]*4)
    # Every executed new wall-path instruction: actual NMI/IRQ return keeps
    # live AXYP/SP, R2..R7, both banks and all five farcall SMC operand bytes.
    q=fixture(b);pipe(q,736);position(q,724,146);q.set('RcTerrainOldY',142);saved=NesMPU.step;pcs=[]
    def record(c):
        if c.pc>=0x8000 and q.m.banks[(c.pc-0x8000)//8192]==81:pcs.append(c.pc)
        saved(c)
    NesMPU.step=record
    try:q.invoke('RcTerrainWallPrepass')
    finally:NesMPU.step=saved
    seams=[]
    for kind,targetPC in itertools.product(('NMI','IRQ'),sorted(set(pcs))):
        q=fixture(b);pipe(q,736);position(q,724,146);q.set('RcTerrainOldY',142);fired=[False]
        def context(c):return(c.a,c.x,c.y,c.p&0xcf,c.sp,c.pc,list(q.m.banks),q.get('CurrentBank'),q.get('CurrentBankC'),bytes(q.m[2:8]),bytes(q.m[z]for z in smc_at(b)))
        def irq(c):
            if not fired[0]and c.pc==targetPC and q.m.banks[1]==81:
                fired[0]=True;before=context(c)
                if kind=='NMI':c.nmi()
                else:c.stPushWord(c.pc);c.stPush(c.p&~c.BREAK|c.UNUSED);c.p|=c.INTERRUPT;c.pc=address(b,'IrqScrollSplit')
                for _ in range(20000):
                    saved(c)
                    if c.pc==before[5]and c.sp==before[4]:break
                else:raise AssertionError('actual RTI timeout')
                assert context(c)==before,(kind,targetPC,before,context(c))
            saved(c)
        NesMPU.step=irq
        try:q.invoke('RcTerrainWallPrepass')
        finally:NesMPU.step=saved
        assert fired[0];seams.append(dict(kind=kind,PC=targetPC))
    proof=dict(passed=True,native_run=False,ROM_sha256=sha(rom),source_build_bindings_verified=len(build['bindings']),rows=rows,
        full_RCR_GameLoop_CPU_delta=[min(costs),max(costs)],HUD_cases=2*65*7,actual_ISR_seams=seams,
        limits=['Finite real CPU arenas; native cold menu/lives/whole route still root-owned and separate.','No native FPS/audio/every-item claim.','Optional ink hue remains world palette3 area-owned, as in earlier component qualification.'],
        bindings=[dict(path=str(p),sha256=sha(p))for p in[Path(__file__),rom,rom.with_suffix('.dbg'),proof_path,R/'src/river_city_wall_prepass_v2.inc',R/'tools/river_city_pipe_contact_controls_v2.py']])
    target.write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=True,rows=len(rows),HUD=proof['HUD_cases'],ISR=len(seams),CPU=proof['full_RCR_GameLoop_CPU_delta'])))
if __name__=='__main__':main()
