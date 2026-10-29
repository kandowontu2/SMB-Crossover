"""Actual compiled DK leaf controls, including original-ROM barrel animation differential."""
from pathlib import Path
import hashlib
import itertools
import json
import sys
from py65.devices.mpu6502 import MPU

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/donkey-kong-component-v1'
sys.path[:0]=[str(ROOT/'tools/audit')]
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_tmnt_render_oa import address
from prepare_original_dk_assets_v1 import decode


def bind(p):
    p=Path(p).resolve();b=p.read_bytes()
    return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())


def new(b):
    q=Arena(b,28)
    q.put(NumberofLives=2,AreaAddrsLOffset=5,WorldNumber=0,Player_X_Position=120,
          Player_PageLoc=1,Player_Y_Position=144,PlayerFacingDir=1,
          VRAM_Buffer1_Offset=0,GuestPowerupActive=0,StarInvincibleTimer=0)
    q.invoke('DkConstruct')
    return q


def original(memory,pc):
    c=MPU(memory=memory,pc=pc);c.sp=253;c.stPushWord(0x5aff)
    for _ in range(10000):
        if c.pc==0x5b00:
            assert c.sp==253
            return c
        c.step()
    raise AssertionError(hex(c.pc))


def raster(record,patterns,width=48,height=32):
    pixels=bytearray(width*height)
    for k in range(1,1+record[0],4):
        tile,attr,yy,xx=record[k:k+4]
        xx=xx if xx<128 else xx-256
        yy=(yy if yy<128 else yy-256)+1
        for half in range(2):
            vals=decode(patterns[(tile+half)*16:(tile+half+1)*16])
            for y in range(8):
                for x in range(8):
                    v=vals[y*8+x]
                    if not v:continue
                    dx=7-x if attr&64 else x
                    dy=15-(half*8+y) if attr&128 else half*8+y
                    at=(yy+dy)*width+xx+16+dx
                    assert 0<=at<len(pixels),(tile,attr,xx,yy,dx,dy)
                    pixels[at]=v
    return pixels


def main():
    proof=OUT/'controls.json'
    assert not proof.exists(),'Keep completed controls immutable'
    b=scoped_load(OUT/'candidate.nes')
    build=json.loads((OUT/'build-proof.json').read_text())
    assert bind(OUT/'candidate.nes')['sha256']==build['candidate']
    results={}
    # Gates must leave foreign overlays and registers alone, including every
    # old identity and not-yet-admitted new raw number.
    gated=['DkConstruct','DkEnterScene','DkEnsure','DkGrant','DkFullPower',
           'DkMovement','DkBounds','DkSpawnBarrel','DkBarrelStep','DkGraphics',
           'DkPortrait','DkColors','DkDraw']
    for char,name in itertools.product(range(28),gated):
        q=Arena(b,char)
        q.m[0x5c00:0x5c80]=bytes((19*i+char)&255 for i in range(128))
        before=bytes(q.m[0x5c00:0x5c80])
        c,_=q.invoke(name,a=0x19,x=5,y=17)
        assert bytes(q.m[0x5c00:0x5c80])==before,(char,name)
        assert [c.a,c.x,c.y,c.p,c.sp]==[0x19,5,17,0x30,253],(char,name,c.a,c.x,c.y,c.p,c.sp)
    results['foreign_gates']=28*len(gated)
    # Whole original source payload matched by the previous asm6 rebuild.
    source=Path('C:/NES/Donkey Kong (World) (Rev 1).nes')
    raw=source.read_bytes();assert bind(source)['sha256']=='226c6f698f60b0a07157bd031004820789469884615fef7bdd862c3157e89d27'
    n=0
    for direction,frame,counter in itertools.product([1,2],range(4),range(6)):
        memory=[0]*65536
        memory[0x8000:0xc000]=raw[16:16400]
        memory[0xc000:]=raw[16:16400]
        memory[0x5d]=0;memory[0x68]=int(direction==2)
        memory[0x72]=0x80+4*frame;memory[0x40d]=counter
        q=new(b);at=address(b,'DkShots')
        q.m[at:at+12]=[1,frame,counter,120,120,1,128,direction,0,0,0,0]
        q.set('DkQuery',1)
        for tick in range(24):
            original(memory,0xdbee)
            q.invoke('DkBarrelStep',x=0)
            assert q.m[at+1]==(memory[0x72]-0x80)//4,(direction,frame,counter,tick)
            assert q.m[at+2]==memory[0x40d]
            n+=1
    results['original_DBEE_animation_CPU_comparisons']=n
    # Persistent actual earned grants and real life/scene transitions. The
    # explicit activation constructor is required; no magic-byte assumption.
    q=new(b)
    for kind,tier in [(0,1),(0,2),(0,2),(1,2)]:
        c,_=q.invoke('DkGrant',a=kind,x=5)
        assert c.p&1 and c.x==5 and q.get('DkTier')==tier
    q.set('AreaPointer',0xc2);q.invoke('DkEnsure');assert q.get('DkTier')==2
    q.set('AreaAddrsLOffset',6);q.invoke('DkEnsure');assert q.get('DkTier')==2
    q.set('NumberofLives',3);q.invoke('DkEnsure');assert q.get('DkTier')==2
    q.set('NumberofLives',2);q.invoke('DkEnsure');assert q.get('DkTier')==0
    q.set('DkTier',2);q.invoke('DkConstruct');assert q.get('DkTier')==0
    results['earned_grants_and_lifecycle']=True
    # Exactly one event per attack, finite pool at each tier, no overwrite.
    for tier in range(3):
        q=new(b);q.set('DkTier',tier)
        for shot in range(tier+1):
            q.put(DkSpawn=1,DkAttack=1)
            c,_=q.invoke('DkSpawnBarrel')
            assert c.p&1 and c.x==12*shot and q.get('DkSpawn')==0
        old=bytes(q.m[address(b,'DkShots'):address(b,'DkShots')+36])
        q.put(DkSpawn=1,DkAttack=1)
        c,_=q.invoke('DkSpawnBarrel')
        assert not c.p&1 and q.get('DkSpawn')==1
        assert bytes(q.m[address(b,'DkShots'):address(b,'DkShots')+36])==old
        q=new(b);q.put(DkTier=tier,SavedJoypadBits=0x44)
        q.invoke('DkClock');assert q.get('DkAttack')==(2 if tier==2 else 1)
        events=[]
        for tick in range(1,25):
            q.invoke('DkClock')
            if q.get('DkSpawn'):
                events.append(tick);q.invoke('DkSpawnBarrel')
        assert events==[16] and q.get('DkAttack')==0,(tier,events)
        q.invoke('DkClock');assert q.get('DkAttack')==0 # held B cannot retrigger.
        q.set('SavedJoypadBits',0);q.invoke('DkClock')
        q.set('SavedJoypadBits',0x40);q.invoke('DkClock');assert q.get('DkAttack')==1
    results['actual_throw_publication_and_pool']=True
    # Render the actual emitted descriptor, not a parallel pose generator.
    assets=json.loads((ROOT/'build/dk-source-assets-v1/handoff.json').read_text())
    patterns=(ROOT/'build/dk-playable-assets-v3/dk.chr').read_bytes()
    n=0
    for pose,face in itertools.product(range(9),[1,2]):
        q=new(b);q.put(PlayerFacingDir=face,DkMirror=0)
        c,_=q.invoke('DkSetPose',x=pose,y=19)
        assert c.x==pose and c.y==19
        at=address(b,'DkRenderBuffer');record=q.m[at:at+q.m[at]+1]
        page=q.get('DkRenderPage')-(820&255)
        pixels=raster(record,patterns[page*1024:(page+1)*1024])
        src=assets['frames'][pose]
        if face==1:
            assert hashlib.sha256(pixels).hexdigest()==src['source_pixel_SHA256']
        else:
            mirrored=bytes(pixels[y*48+47-x] for y in range(32) for x in range(48))
            assert hashlib.sha256(mirrored).hexdigest()==src['source_pixel_SHA256']
        n+=1
    results['actual_emitted_original_body_rasters_both_facings']=n
    # Full atomic packet or no packet, preserving arbitrary existing queue
    # prefixes, following canary, offset and pending acknowledgement.
    for offset in range(84):
        q=new(b);base=address(b,'VRAM_Buffer1')
        q.m[base:base+85]=[(i*13+3)&255 for i in range(85)]
        q.set('VRAM_Buffer1_Offset',offset);q.set('DkPaletteAck',255)
        before=bytes(q.m[base:base+85])
        q.invoke('DkQueuePalette')
        after=bytes(q.m[base:base+85])
        if offset<=71:
            assert after[:offset]==before[:offset] and after[offset+13:]==before[offset+13:]
            assert after[offset:offset+13]==bytes.fromhex('3f11033036063f150306270200')
            assert q.get('VRAM_Buffer1_Offset')==offset+12 and q.get('DkPaletteAck')==0
        else:
            assert after==before and q.get('VRAM_Buffer1_Offset')==offset and q.get('DkPaletteAck')==255
    results['palette_atomic_boundaries']=84
    report=dict(passed=True,source_CPU_only=True,native_run=False,checks=results,
        candidate=bind(OUT/'candidate.nes'),
        limits='Isolated actual compiled leaves and original animation differential only. No shared admission, wholeMain, interrupts, real combat/terrain, PPU, audio or1-1 qualification.',
        bindings=[bind(p)for p in[Path(__file__),source,OUT/'candidate.nes',OUT/'candidate.dbg',
            OUT/'candidate.lbl',OUT/'build-proof.json',ROOT/'src/donkey_kong_core.s',
            ROOT/'src/donkey_kong_render.s',ROOT/'src/donkey_kong_state.inc']])
    proof.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__=='__main__':
    main()
