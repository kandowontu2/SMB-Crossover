"""Compare actual FF draw transport to source records and native OAM semantics."""
from pathlib import Path
import argparse,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_host_pickups_controls_v2 as T
import ff_host_pickups_vectors_v2 as ISR
from check_tmnt_render_oa import address
C=T.C;put=T.put;get=T.get;setv=T.setv;run=T.run
P=R/'build/final-fantasy-host-render-v8'
O=R/'build/final-fantasy-host-render-controls-v6'


def setup(b,variant=0,tier=0,shadows=1,face=1,rotation=0,offset=0):
    m=T.setup(b,variant,tier)
    put(m,Player_X_Position=112,Player_PageLoc=1,Player_Y_Position=176,Player_Y_HighPos=1,
        ScreenLeft_X_Pos=16,ScreenLeft_PageLoc=1,PlayerFacingDir=face,Player_X_Speed=0,
        Player_State=0,FfAction=0,PlayerOutlinesOff=shadows,CurrentOAMOffset=offset,
        RgOamRotation=rotation,GuestOamRotationActive=1,RgDrawFirst=0)
    for i in range(256):m[512+i]=(0xf8 if i%4==0 else (i*13+7)&255)
    run(m,'FfHostGraphics')
    put(m,RgDrawRemaining=220-get(m,'FfRenderBuffer'))
    m.writes.clear();return m


def records(m,entry,chunk,window,face):
    put(m,FfSlot=face)
    c,_,_=run(m,'FfRenderChunk',a=entry,x=chunk,y=window)
    if not c.p&1:return None
    n=get(m,'FfRenderBuffer')
    a=[get(m,'FfRenderBuffer',i)for i in range(1,n+1)]
    off=get(m,'FfRenderYOffset')+256*get(m,'FfRenderYOffset',1)
    if off&32768:off-=65536
    return [a[i:i+4]for i in range(0,n,4)],off,get(m,'FfRenderPage')


def model(oam,parts,origin,offset,rotation,cursor,limit=204):
    sx=lambda v:v-256 if v&128 else v
    parts=[p for p in parts if 0<=origin[0]+sx(p[3])<=255 and 31<=origin[1]+sx(p[2])-256<=239]
    limit=max(0,limit-offset)//4
    n=min(len(parts),limit)
    if not n:return offset,0,[]
    start=cursor%len(parts)if n<len(parts)else 0
    first=min(n,len(parts)-start)
    selected=list(reversed(parts[start:start+first]))
    if first<n:selected+=list(reversed(parts[:n-first]))
    for i,p in enumerate(selected):
        at=(offset+rotation+i*4)&255
        oam[at:at+4]=[origin[1]+sx(p[2])-256,p[0],p[1]&0xf3,origin[0]+sx(p[3])]
    return offset+4*n,1+int(first<n),selected


def native_count(b,trace):
    return sum(pc==address(b,'MetaspriteRenderLoop')and bank==132 for pc,bank in trace)


def chunk_models(b):
    cases=0;calls=0
    # Original effect records include signed193/97/1/95 Y bands, six-chunk
    # Bolt and physical pages on both sides of the768-page boundary.
    for entry,face,origin,rotation,offset,cursor in itertools.product(
            range(144,158),[1,2],[(96,381),(248,288),(-8,495)],
            [0,68],[0,128,200,204],[0,11]):
        ref=setup(b);chunk=0
        while True:
            source=records(ref,entry,chunk,1,face)
            if source is None:break
            parts,yoff,page=source
            m=setup(b,rotation=rotation,offset=offset)
            records(m,entry,chunk,1,face)
            put(m,FfTargetW=0,R4=origin[0]&255,R5=(origin[0]>>8)&255,
                R6=(origin[1]+yoff)&255,R7=((origin[1]+yoff)>>8)&255)
            setv(m,'FfProjectile',cursor,3)
            expected=list(m[512:768])
            end,native,selected=model(expected,parts,(origin[0],origin[1]+yoff),offset,rotation,cursor)
            c,tr,_=run(m,'FfHostRenderChunk')
            assert list(m[512:768])==expected,('genuine source/native OAM',entry,chunk,face,origin,rotation,offset,cursor)
            assert get(m,'CurrentOAMOffset')==end
            assert native_count(b,tr)==native
            assert not any(0x2000<=a<=0x3fff for a,v in m.writes),('active PPU store',entry,chunk)
            if selected:
                physical=756+page
                assert get(m,'CurrentCHRBank',1)==physical&255
                assert get(m,'X5ChrMode',1)==128+(physical>>8)
            cases+=1;calls+=native;chunk+=1
    return dict(source_chunk_cases=cases,actual_native_draw_calls=calls,all64OAM_records_exact=True,
                real_window_physical_upper_pages=True,signed_world_clip_and_HUD=True)


def full_draw(b):
    rows=[];costs={}
    patterns=[[],[(0,1,1)],[(0,2,2)],[(0,1,0),(12,2,2),(24,1,2)],
              [(0,3,3),(12,1,1),(24,4,1)]]
    for variant,tier,shadows,face,pattern in itertools.product(range(4),range(3),[0,1],[1,2],patterns):
        m=setup(b,variant,tier,shadows,face,rotation=68)
        for slot,kind,frame in pattern:
            for i,value in [(0,kind),(1,frame),(2,1),(3,7),(4,128),(5,1),(7,125),(8,face)]:
                setv(m,'FfProjectile',value,slot+i)
        ref=setup(b,variant,tier,shadows,face,rotation=68)
        for slot,kind,frame in pattern:
            for i,value in [(0,kind),(1,frame),(2,1),(3,7),(4,128),(5,1),(7,125),(8,face)]:
                setv(ref,'FfProjectile',value,slot+i)
        expected=list(m[512:768]);offset=0;calls=0
        limit=220-get(m,'FfRenderBuffer')
        pose=get(m,'FfPose');power=get(m,'FfPower')
        entry=[0,36,72,108][variant]+(18 if power>=2 else 0)+pose-1
        chunk=1
        while True:
            source=records(ref,entry,chunk,0,face)
            if source is None:break
            parts,yoff,page=source
            offset,native,_=model(expected,parts,(96,432+yoff),offset,68,0,limit=limit)
            calls+=native;chunk+=1
        # Initial native RgDrawFirst0 advances to1, so slots12,24,0.
        cursor_after={}
        for slot in [12,24,0]:
            c,_,_=run(ref,'FfProjectileEntry',x=slot)
            if not c.p&1:continue
            effect=c.a;chunks=[]
            for chunk in range(8):
                source=records(ref,effect,chunk,slot//12+1,face)
                if source is None:break
                chunks.append(source)
            start=1%len(chunks)
            cursor_after[slot]=[(start+1)%len(chunks),8]
            for i in range(len(chunks)):
                parts,yoff,page=chunks[(start+i)%len(chunks)]
                offset,native,_=model(expected,parts,(112,381+yoff),offset,68,8,limit=limit)
                calls+=native
        before=(get(m,'FfPower'),get(m,'FfEarned'),get(m,'FfHealCharges'),get(m,'CurrentBankC'))
        world=[get(m,n,i)for n in ['CurrentCHRBank','X5ChrMode']for i in range(4,12)]
        c,tr,_=run(m,'FfHostDrawShots')
        assert list(m[512:768])==expected,('full source loop OAM',variant,tier,shadows,face,pattern)
        assert get(m,'CurrentOAMOffset')==offset and offset<=limit
        assert native_count(b,tr)==calls
        assert (get(m,'FfPower'),get(m,'FfEarned'),get(m,'FfHealCharges'),get(m,'CurrentBankC'))==before
        assert [get(m,n,i)for n in ['CurrentCHRBank','X5ChrMode']for i in range(4,12)]==world
        for slot,pair in cursor_after.items():
            assert [get(m,'FfProjectile',slot+i)for i in [2,3]]==pair
        # Genuine body0, all source roles and signed body origin are restored.
        body=setup(b,variant,tier,shadows,face)
        count=get(body,'FfRenderBuffer')
        assert bytes(m[address(b,'FfRenderBuffer'):address(b,'FfRenderBuffer')+count+1])==bytes(body[address(b,'FfRenderBuffer'):address(b,'FfRenderBuffer')+count+1])
        physical=756+get(body,'FfRenderPage')
        assert get(m,'CurrentCHRBank')==physical&255 and get(m,'X5ChrMode')==128+(physical>>8)
        costs.setdefault(str(pattern),[]).append(c.processorCycles)
        rows.append([variant,tier,shadows,face,len(pattern)])
    return dict(full_source_draw_cases=len(rows),four_classes_all_tiers_faces_options=True,
                acquired_gear_unchanged=True,all_native_world_windows_untouched=True,
                measured_callback_CPU={k:dict(min=min(v),max=max(v),mean=sum(v)/len(v))for k,v in costs.items()})


def guards(b):
    for owner in list(range(34))+[255]:
        if owner==22:continue
        m=setup(b);put(m,SelectedCharacter=owner);before=T.V.state(m)
        run(m,'FfHostDrawShots');assert T.V.state(m)==before,owner
    return dict(foreign_owner_cases=34,no_foreign_application_stores=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--packet',type=Path,default=P);p.add_argument('--out',type=Path,default=O)
    args=p.parse_args();P=args.packet.resolve();O=args.out.resolve();assert not O.exists();O.mkdir()
    h=json.loads((P/'build-proof.json').read_text())
    for path,d in h['bindings'].items():assert C.sha(path)==d,path
    b=C.bundle(P);checks={};failures={}
    for name,fn in dict(source_native_chunks=chunk_models,full_draw=full_draw,foreign_guards=guards).items():
        try:checks[name]=fn(b);print(json.dumps(dict(group=name,passed=True,checks=checks[name])),flush=True)
        except Exception as e:failures[name]=dict(error=repr(e),traceback=traceback.format_exc());print(json.dumps(dict(group=name,passed=False,error=repr(e))),flush=True)
    bindings={**h['bindings'],str((P/'build-proof.json').resolve()):C.sha(P/'build-proof.json')}
    for path in [Path(__file__).resolve(),Path(T.__file__).resolve(),Path(ISR.__file__).resolve()]:bindings[str(path)]=C.sha(path)
    report=dict(passed=not failures,image_sha256=C.sha(P/'ram3.bin'),checks=checks,failures=failures,
                native=False,full_Main=False,bindings=bindings)
    (O/'controls.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(passed=not failures,groups=len(checks),failed=list(failures))))
    if failures:raise SystemExit(1)
