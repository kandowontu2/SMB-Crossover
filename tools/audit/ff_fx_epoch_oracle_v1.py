"""Read-only family oracle over actual completed DrawAll/normal-NMI records.

No scheduler code, palette packet or owner state is installed. Model outputs
are Python lists; the source cartridge and emulated source OAM stay unchanged.
Renderer state fixtures are explicit, not controller-earned weapon evidence.
"""
from pathlib import Path
import collections,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_upper_fx_windows_controls_1030_v2 as U
import ff_joint_native_flash_controls_1030_v3 as F
import ff_fx_palette_lifecycle_controls_v5 as L
from check_tmnt_render_oa import address,location
H,M,T,V=L.H,L.M,L.T,L.V
P=R/'build/ff-fx-world-marker-proposal-v2';H.O=P/'joint'
O=R/'build/ff-fx-epoch-oracle-v1'

def pixels(b,m,tile):
    w=U.window(tile);page=m.chr_latches[w];at=1048592+page*1024+(tile&0x3e)*16
    data=b['raw'][at:at+32];assert len(data)==32
    return collections.Counter(((data[half*16+y]>>bit)&1)|(((data[half*16+y+8]>>bit)&1)<<1)
        for half,y,bit in itertools.product(range(2),range(8),range(8)))

def family_vectors(b):
    def get(n,k):p=location(b,n);return list(b['raw'][p:p+k])
    red=get('FfPaletteRed',16)
    return {1:red[5:8],2:get('FfPaletteIce',4)[1:],3:get('FfPaletteBolt',4)[1:],4:red[9:12],5:red[13:16]}

def base(b,area):
    m=F.seed(b);H.put(m,AreaType=area,SmFreezePalettePending=0,SmFreezeLastBlue=0,NmiDisable=255)
    # Genuine native area palette publication, before the source FF body force.
    H.invoke(m,'GetAreaPalette');L.Q.consume(m,0)
    return m

def frame(seed,variant,pose,off,face,kind,entries):
    m=T.copy(seed);b=m.bundle
    H.put(m,FfVariant=variant,PlayerOutlinesOff=off,PlayerFacingDir=face,FfPose=pose,
        FrameCounter=0,GuestPowerupActive=0,StarInvincibleTimer=0,SmFreezeRenderState=0,NmiDisable=255,
        VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0)
    m[address(b,'VRAM_Buffer1')]=0
    H.invoke(m,'FwEnsure');H.put(m,FfPose=pose,FfPower=0)
    for i in range(36):m[address(b,'FfProjectile')+i]=0
    for slot,entry in entries:U.set_projectile(m,slot,entry,face)
    if variant==1 and entries:m[address(b,'FfProjectile')]=4 # true White source kind, same Ice-art family.
    for i in range(24):m[address(b,'ObjectMetasprite')+i]=0
    for i in range(6):m[address(b,'Enemy_Flag')+i]=0
    meta={'mushroom':'POWERUP_MUSHROOM','koopa':'KOOPA_WALKING_1','flower':'POWERUP_FIREFLOWER'}[kind]
    slot=0 if kind=='koopa'else 5
    m[address(b,'ObjectMetasprite')+slot+1]=address(b,'METASPRITE_'+meta)
    for name,value in[('Enemy_Flag',1),('Enemy_ID',0 if kind=='koopa'else address(b,'PowerUpObject')),
        ('Enemy_State',0 if kind=='koopa'else 128),('Enemy_X_Position',192),('Enemy_PageLoc',0),
        ('Enemy_Y_Position',160),('Enemy_Y_HighPos',1),('Enemy_SprAttrib',0)]:m[address(b,name)+slot]=value
    H.put(m,PowerUpType=2 if kind=='flower'else 0)
    H.invoke(m,'FwHostGraphics');H.invoke(m,'FwForceColors')
    pending=[];objects=[];entrypc=address(b,'FfMuxWorldDraw')
    def observe(mem,c,i):
        for p in pending[:]:
            if c.pc==p['return_PC']and c.sp==p['SP']+2:
                pending.remove(p);p['end']=H.get(mem,'CurrentOAMOffset');objects.append(p)
        if c.pc==entrypc and mem.rawtags[2]==221:
            pending.append(dict(start=H.get(mem,'CurrentOAMOffset'),rotation=H.get(mem,'RgOamRotation'),
                SP=c.sp,return_PC=mem[0x101+c.sp]+256*mem[0x102+c.sp]+1))
    cpu,low=F.invoke_drawall(m,observe);assert not pending
    H.put(m,NmiDisable=0);c=H.start(m,'FwCheck');V.interrupt(m,c,'NMI')
    return m,objects,cpu.processorCycles

def model(m,objects,vectors):
    b=m.bundle;original=list(m[512:768]);used=H.get(m,'RgOamUsed');rotation=H.get(m,'RgOamRotation')
    start=H.get(m,'RgOamPlayerStart');ptr=H.get(m,'SmPosePtr')+256*m[address(b,'SmPosePtr')+1]
    header=m[ptr];end=start+header
    assert 0<=start<=end<=220 and end<=used<=252
    native=list(m.vram[0x3f15:0x3f18]);vectors={0:native,**vectors};records=[];present=set()
    for logical in range(0,used,4):
        at=(logical+rotation)&255;data=original[at:at+4];y,tile,attr,x=data;pal=attr&3
        family=None;body0=False
        if logical<end:
            window=U.window(tile)
            if window in[5,6,7]:
                slot=(window-5)*12;typ=m[address(b,'FfProjectile')+slot]
                assert 1<=typ<=4;family={1:1,2:3,3:2,4:2}[typ]
            else:
                assert window==0 and pal in[0,2,3],('unrecognized FF own record',logical,data,window)
                body0=pal==0;family=None if body0 else 4 if pal==2 else 5
        elif attr&16:family=0
        elif y<240:assert pal!=1,('visible nativeP1 escaped complete-object marker',logical,data)
        if family is not None and y<240:present.add(family)
        records.append(dict(logical=logical,at=at,data=data,family=family,body0=body0))
    choices=sorted(present)or[0];color_pixels=0;body_count=sum(r['body0']for r in records)
    for chosen in choices:
        result=original[:]
        for r in records:
            at=r['at'];data=r['data'];f=r['family'];result[at+2]&=239
            if f is not None:
                if f!=chosen:result[at]=248
                elif f!=0:result[at+2]=(result[at+2]&252)|1
            if r['body0']:assert result[at:at+4]==data
            if data[0]>=240 or result[at]>=240:continue
            want=vectors[f]if f is not None else list(m.vram[0x3f11+4*(data[2]&3):0x3f14+4*(data[2]&3)])
            got=vectors[chosen]if result[at+2]&3==1 else list(m.vram[0x3f11+4*(result[at+2]&3):0x3f14+4*(result[at+2]&3)])
            counts=pixels(b,m,data[1])
            assert all(got[i-1]==want[i-1]for i in counts if i),('source color approximation',f,chosen,data,want,got)
            color_pixels+=sum(n for i,n in counts.items()if i)
        for obj in objects:
            part_offsets=[(j+obj['rotation'])&255 for j in range(obj['start'],obj['end'],4)]
            marked=any(original[a+2]&16 for a in part_offsets)
            if marked:
                assert all(original[a+2]&16 for a in part_offsets)
                assert all(result[a]==(original[a]if chosen==0 else 248)for a in part_offsets)
        # Same source-priority order; hiding groups never increases line load.
        before=max((sum(d[0]<=y<d[0]+16 for d in[original[i:i+4]for i in range(0,256,4)]if d[0]<240)for y in range(240)),default=0)
        after=max((sum(d[0]<=y<d[0]+16 for d in[result[i:i+4]for i in range(0,256,4)]if d[0]<240)for y in range(240)),default=0)
        assert after<=before
    assert list(m[512:768])==original,'Read-only oracle wrote emulated OAM'
    # Exercise fair next-present search independently of frame duration.
    cursor=0;hist=collections.Counter()
    for _ in range(3*len(choices)):
        chosen=next((x for x in[(cursor+j)%6 for j in range(6)]if x in choices),0)
        hist[chosen]+=1;cursor=(chosen+1)%6
    assert set(hist.values())=={3}
    return dict(source_records=len(records),body0_records=body_count,families=choices,admitted_color_pixels=color_pixels,
        original_max_scanline_sprites=before,world_objects=len(objects),fair_model_histogram=dict(hist))

def main():
    O.mkdir(exist_ok=False);p=dict(passed=False,native=False,admitted=False,read_only_model=True,source_scheduler_installed=False,rows=[])
    try:
        b=H.C.qualified(P/'joint/candidate.nes');vectors=family_vectors(b)
        audit=json.loads((R/'build/ff-fx-sword-role-audit-v1/controls.json').read_text())
        sword={v:next(r['pose']for r in audit['rows']if r['character']==name and r['sword_parts'])for v,name in[(0,'Fighter'),(3,'Thief')]}
        scenarios=[(0,1,[]),(0,sword[0],[]),(3,1,[]),(3,sword[3],[]),(1,1,[]),(1,1,[(0,149)]),
            (2,1,[(0,144)]),(2,1,[(0,144),(12,154)]),(2,1,[(0,144),(12,149)]),(2,1,[(0,144),(12,145),(24,154)])]
        bases={a:base(b,a)for a in range(4)}
        for area,face,off,world,(variant,pose,entries)in itertools.product(range(4),[1,2],[0,1],['mushroom','koopa','flower'],scenarios):
            m,objects,CPU=frame(bases[area],variant,pose,off,face,world,entries)
            p['rows'].append(dict(area=area,face=face,outlines_off=off,world=world,variant=variant,pose=pose,entries=entries,
                DrawAll_source_CPU=CPU,**model(m,objects,vectors)))
        p.update(passed=True,cases=len(p['rows']),source_vectors=vectors,limits=[
            'Renderer state fixtures are explicit; these are not controller-earned actions or natural Main/campaign proof.',
            'Pure Python epoch outputs only. Actual scheduler/gates/heartbeat/queue/cookie implementation is still absent.',
            'Color equality covers admitted source pixels; visibility is time multiplexed. Existing8/line and64OAM losses remain visible.'])
    except Exception as e:p.update(error=repr(e),traceback=traceback.format_exc())
    files=[Path(__file__),Path(U.__file__),Path(F.__file__),Path(L.__file__),P/'handoff.json',P/'joint/candidate.nes',P/'joint/candidate.dbg',R/'build/ff-fx-sword-role-audit-v1/controls.json']
    p['bindings']={str(f.resolve()):L.sha(f)for f in files}
    out=O/('controls.json'if p['passed']else'negative-controls.json');out.write_text(json.dumps(p,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(passed=p['passed'],cases=len(p['rows']),error=p.get('error'),path=str(out))),flush=True);assert p['passed']

if __name__=='__main__':main()
