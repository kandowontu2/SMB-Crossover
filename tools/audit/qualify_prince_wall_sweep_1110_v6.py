"""Zero-file semantic and native-vector checks for the funded Prince derivative."""
import argparse
from collections import Counter
import json
import inspect
from itertools import product
from unittest.mock import patch
from py65.devices.mpu6502 import MPU
import check_prince_wall_sweep_1110_v6 as V

Q,C,N,I=V.Q,V.C,V.N,V.I


def flat(seed):
    m=bytearray(65536)
    m[:0x800]=bytes(seed[:0x800])
    m[0x8000:0xa000]=bytes(seed[0x8000:0xa000])
    m[0xa000:0xc000]=seed.ram[3]
    m[0xc000:0xe000]=seed.ram[2]
    m[0xe000:]=bytes(seed[0xe000:])
    return m


def call(m,pc,args=(83,71,109,0x61)):
    c=MPU(memory=m,pc=pc);c.a,c.x,c.y,c.p=args;c.sp=224;c.stPushWord(0x5aff)
    for _ in range(5000):
        if c.pc==0x5b00:break
        assert m[c.pc]!=0,('Unexpected BRK',hex(c.pc))
        c.step()
    else:raise AssertionError(('Call bound',hex(c.pc)))
    assert c.sp==224
    return c.a,c.x,c.y,c.p,c.sp


def points(old,new):
    a,b=flat(old),flat(new);count=0;Vdrift=0
    for tile in range(256):
        for m in (a,b):m[0x300:0x4a0]=bytes([tile])*0x1a0
        for x in (0,15,16,255,256,511,512,65535):
            for y in (0,31,32,47,48,223,224,239,240,255):
                for page in (0,1,255):
                    for m in (a,b):m[0xb369:0xb36d]=x.to_bytes(2,'little')+bytes((y,page))
                    args=(83,71,109,0x21|(tile&0xc0))
                    ar,br=call(a,0xb310,args),call(b,0xb310,args)
                    assert ar[:3]==br[:3] and ar[4:]==br[4:] and (ar[3]^br[3])&~0x40==0,(tile,x,y,page,ar,br)
                    assert a[0xb36d]==b[0xb36d] and a[3:11]==b[3:11]
                    Vdrift+=bool((ar[3]^br[3])&0x40);count+=1
    return dict(executed_pairs=count,all256_actual_native_metatiles=True,A_C_NZ_X_Y_SP_and_Raw_exact=True,
        V_flag_not_in_PointRead_contract_differences=Vdrift,
        note='WorldTile/Align and public native adder preserve caller P; PointRead specifies A/C and X/Y only.')


def admissions(old,new):
    a,b=flat(old),flat(new);marker=0x5a01
    # A/P-preserving substitute logs only whether the unchanged103B leaf is called.
    stub=bytes.fromhex('0848ee015a6828a0063860')
    for m in (a,b):
        m[0xd4d7:0xd4d7+len(stub)]=stub
        m[0x75]=40;m[0x5c]=0;m[0xbd]=176;m[0xa4]=1;m[0xc0a7:0xc0a9]=bytes((40,0))
    count=0;repairs=0
    for engine in (5,8,11):
        for dy in range(256):
            for residue in range(16):
                for p in (0x20,0x61):
                    for m in (a,b):m[15]=engine;m[0x8e]=dy;m[0xc084]=208+residue;m[marker]=0
                    ar,br=call(a,0xbd3e,(83,71,109,p)),call(b,0xbd3e,(83,71,109,p))
                    assert a[marker]==b[marker]==int(engine==8 and dy<128 and residue>max(4,dy)),(engine,dy,residue,a[marker],b[marker])
                    assert ar==br,(engine,dy,residue,p,ar,br)
                    repairs+=a[marker];count+=1
    return dict(executed_pairs=count,repair_calls=repairs,all_DY_and_residues=True,public_AXYP_SP_exact=True,
        frozen103_stub_only_for_predicate=True,new_SMC_threshold=False)


def exports(old,new):
    a,b=flat(old),flat(new);count=0
    fields=('Player_X_Position','Player_PageLoc','Player_X_Scroll','Player_X_Speed',
        'Player_Y_Position','Player_Y_HighPos','Player_State','Player_Pos_ForScroll')
    addresses=[I.address(old.bundle,n) for n in fields]
    def one(before,after):
        nonlocal count
        source=(after+8)&65535
        for m in (a,b):
            m[0x75]=before&255;m[0x5c]=before>>8
            m[0xc60f:0xc611]=source.to_bytes(2,'little')
            m[0xc611]=128;m[0xc08b]=128;m[0xc089:0xc08b]=bytes((77,0));m[0xc088]=3
        ar,br=call(a,0xc383),call(b,0xc383)
        assert ar==br and all(a[p]==b[p] for p in addresses),(before,after,ar,br)
        assert a[0xc078:0xc0a7]==b[0xc078:0xc0a7] and a[0xc606:0xc800]==b[0xc606:0xc800]
        assert int.from_bytes(b[0xc0a7:0xc0a9],'little')==before
        count+=1
    for before in range(256):
        for after in range(256):one(3*256+before,3*256+after)
    for page in (0,1,2,127,128,254,255):
        for lo in range(256):
            one(page*256+lo,((page+1)&255)*256+((lo+14)&255))
            one(page*256+lo,((page-1)&255)*256+((lo-14)&255))
    return dict(executed_full_export_pairs=count,full16_old_witness_exact=True,
        native_registers_geometry_actor_fields_exact=True,source_motor_not_replaced=True)


def cameras(old,new):
    a,b=flat(old),flat(new);count=0
    addresses=[I.address(old.bundle,n) for n in ('Player_X_Speed','PlayerFacingDir','Player_Y_Speed',
        'Player_X_Scroll','Player_Pos_ForScroll','Player_X_Position','Player_PageLoc')]
    for left,relative,scroll,stop,action,mode in product((0x197,0xfffa),
        (-3,0,112,119,120,121,122,125,128,239,255,256,264,319,512),(-5,0,1,4,5,10),
        ('none','lock','side','platform'),(0,7,13,24,42,49),(0,1,3,4,255)):
        x=(left+relative)&65535
        for m in (a,b):
            for n,v in dict(Player_X_Position=x&255,Player_PageLoc=x>>8,ScreenLeft_X_Pos=left&255,
                ScreenLeft_PageLoc=left>>8,Player_X_Scroll=scroll&255,Player_Pos_ForScroll=relative&255,
                ScrollLock=int(stop=='lock'),SideCollisionTimer=int(stop=='side'),
                Platform_X_Scroll=int(stop=='platform')).items():m[I.address(old.bundle,n)]=v
            m[0xc615]=255;m[0xc616]=action;m[0xc618]=mode
            m[0xc084:0xc088]=bytes((208,0,207,0))
            m[0xd4b1]=207;m[0xd4a3]=0
        ar,br=call(a,0xda98),call(b,0xda98)
        assert ar==br and all(a[p]==b[p] for p in addresses),(left,relative,scroll,stop,action,mode,ar,br)
        count+=1
    return dict(actual_NativeMotionExport_pairs=count,registers_and_native_camera_DY_exact=True,
        precondition='Exact HostExport invariant Player_Pos_ForScroll=(nativeX-ScreenLeft)&255',
        old67_new62_bytes=True,declared80B_reservation=[0xd622,0xd672])


def regressions(result):
    parent,trial,chunks,layout,program,packet,rows=result
    seed,cold=Q.actual_cold(trial,chunks,layout,program)
    source=inspect.getsource(Q.Foot.matrix)
    assert source.count('I.invoke(m,3,0xbd3e,')==1
    namespace=dict(Q.Foot.__dict__);exec(source.replace('I.invoke(m,3,0xbd3e,','I.invoke(m,3,0xd4d7,'),namespace)
    print('WALL_FROZEN103_FLOOR13 '+json.dumps(namespace['matrix'](seed),separators=(',',':')),flush=True)
    print('WALL_POSES '+json.dumps(Q.poses(parent,trial,seed),separators=(',',':')),flush=True)
    print('WALL_LIFECYCLE '+json.dumps(Q.landing_and_lifecycle(trial)[0],separators=(',',':')),flush=True)
    # Derivative of the frozen six-owner audit: exactly the42B source-dead
    # horizontal adapter is an intentional additional prefix-code difference.
    # Actor/geometry/constructor bytes outside this explicit span stay exact.
    text=inspect.getsource(Q.owner_regressions)
    needle="assert bytes(old.ram[2][:0x800])==bytes(new.ram[2][:0x800])"
    replacement="assert all(a==b or 0x386<=at<0x3b0 for at,(a,b) in enumerate(zip(old.ram[2][:0x800],new.ram[2][:0x800])))"
    assert text.count(needle)==1
    namespace=dict(Q.__dict__);exec(text.replace(needle,replacement),namespace)
    owners=namespace['owner_regressions'](parent,trial,chunks,layout,program,packet,rows)
    print('WALL_OWNERS '+json.dumps(owners,separators=(',',':')),flush=True)
    print('WALL_READBACK '+json.dumps(Q.append_readback_faults(trial,chunks,layout,program),separators=(',',':')),flush=True)


def wall_fixture(seed,old_x=897,new_x=911,wall=912,y=176,mode=1,action=13,dy=0,kind='wall'):
    m=Q.Sonic.slim_fork(seed);left=max(0,wall-128)
    def tile(x,v):
        if v>=208:return 0x54
        if wall%512<=x<wall%512+16 and v>=144:
            return dict(wall=0x14,coin=0xc2,hidden=0x5f,climb=0x24,spring=0x67,sidepipe=0x1c,
                temporary=0x23,empty=0).get(kind,0x14)
        return 0
    C.Seam.terrain(m,tile);C.Seam.layout(m,left,new_x)
    N.put(m,SelectedCharacter=38,GameEngineSubroutine=8,OperMode=1,FamilyMainCommit=1,
        GamePauseStatus=0,FrameCounter=33,Player_Y_Position=y,Player_Y_HighPos=1,
        Player_X_Speed=(80 if new_x>old_x else 176 if new_x<old_x else 0),Player_Y_Speed=dy,
        Player_State=0 if dy==0 else 2,PlayerFacingDir=1 if new_x>=old_x else 2,
        PlayerSize=0,CrouchingFlag=0,SwimmingFlag=0,DisableCollisionDet=0,NmiDisable=255,
        DisableScreenFlag=0,Mirror_PPUMASK=30)
    m.ram[2][0xa7:0xa9]=old_x.to_bytes(2,'little')
    m.ram[2][0xa9:0xad]=bytes((33,1,0xa7,0))
    m.ram[2][0x60f:0x611]=((new_x+8)&65535).to_bytes(2,'little')
    m.ram[2][0x611]=(y+32-80)&255;m.ram[2][0x8b]=m.ram[2][0x611]
    m.ram[2][0x84:0x88]=(y+32).to_bytes(2,'little')*2
    m.ram[2][0x88]=3;m.ram[2][0x89:0x8b]=bytes((77,0))
    m.ram[2][0x616]=action;m.ram[2][0x618]=mode;m.ram[2][0x615]=255 if new_x>=old_x else 0
    I.invoke(m,3,I.address(m.bundle,'GetPlayerOffscreenBits'))
    return m


def walls(seed):
    cases=[('right14',897,911,912,176,1,13,0,'wall',897),
        ('right32',897,929,912,176,1,13,0,'wall',897),
        ('left14',927,913,912,176,1,13,0,'wall',927),
        ('left32',927,895,912,176,1,13,0,'wall',927),
        ('page-right32',241,273,256,176,1,13,0,'wall',241),
        ('page-left32',271,239,256,176,1,13,0,'wall',271),
        ('stationary-right-boundary',897,897,912,176,0,0,0,'wall',897),
        ('away-left',897,883,912,176,1,13,0,'wall',883),
        ('above-wall',897,929,912,80,2,24,252,'wall',929),
        ('crouch-mode5',897,911,912,176,5,49,0,'wall',897),
        ('empty32',897,929,912,176,1,13,0,'empty',929)]
    result=[];held=[]
    for name,ox,nx,wx,y,mode,action,dy,kind,expected in cases:
        m=wall_fixture(seed,ox,nx,wx,y,mode,action,dy,kind)
        before=bytes(m.ram[2][0x606:0x800]);foot=bytes(m.ram[2][0x84:0x88]);saved=N.fork(m)
        out=I.invoke(m,3,I.address(m.bundle,'PlayerBGCollision'))
        x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc')
        assert x==expected,(name,x,expected,out)
        assert bytes(m.ram[2][0x606:0x800])==before and bytes(m.ram[2][0x84:0x88])==foot,name
        assert int.from_bytes(m.ram[2][0xa7:0xa9],'little')==ox,name
        result.append(dict(name=name,old=ox,attempt=nx,actual_native_x=x,source_actor_and_soles_unchanged=True,
            native_wall_timer=N.get(m,'SideCollisionTimer'),minimum_SP=out.get('minSP')))
        if name in ('right14','page-left32'):held.append((name,saved))
    return result,held


def negatives(seed):
    rows=[]
    def check(name,m,expected,exact=False):
        actor=bytes(m.ram[2][0x606:0x800]);foot=bytes(m.ram[2][0x84:0x88]);oldw=bytes(m.ram[2][0xa7:0xa9])
        before=tuple(map(bytes,m.ram));out=I.invoke(m,3,0xbd3e,(83,71,109,0x61))['regs']
        x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc')
        assert x==expected and out[:3]==[83,71,6] and out[4]==224 and out[3]&0xef==0x61,(name,x,expected,out)
        assert bytes(m.ram[2][0x606:0x800])==actor and bytes(m.ram[2][0x84:0x88])==foot
        assert bytes(m.ram[2][0xa7:0xa9])==oldw
        if exact:assert tuple(map(bytes,m.ram))==before,name
        rows.append(dict(name=name,native_x=x,actor_soles_and_full_old_witness_exact=True,whole_private_RAM_exact=exact))
    for kind in ('coin','hidden','climb','spring','sidepipe','temporary'):
        check('deferred-'+kind,wall_fixture(seed,kind=kind),911)
    for name,fields in (('pause',dict(GamePauseStatus=1)),('stale-frame',dict(FrameCounter=34)),
        ('scripted-engine',dict(GameEngineSubroutine=5))):
        m=wall_fixture(seed);N.put(m,**fields);check(name,m,911,True)
    m=wall_fixture(seed);m.ram[2][0xaa]=0;check('no-admitted-epoch',m,911,True)
    m=wall_fixture(seed);m.ram[2][0xaa]=0;m.ram[2][0xa7:0xa9]=bytes((255,255));check('retired-stale-witness',m,911,True)
    for oldx in (500,1216):check('old-origin-outside-current-view-'+str(oldx),wall_fixture(seed,oldx,911),911)
    check('old-leading-word-overflow',wall_fixture(seed,65535,40,128),40)
    m=wall_fixture(seed,40,65535,128);N.put(m,Player_OffscreenBits=0);check('new-leading-word-overflow',m,65535)
    m=wall_fixture(seed);N.put(m,Player_OffscreenBits=15);check('endpoint-offscreen',m,911,True)
    # An actual full collision followed by a repeated same-epoch source profile
    # must retain its genuine897 old witness and make no further private write.
    m=wall_fixture(seed);I.invoke(m,3,I.address(m.bundle,'PlayerBGCollision'))
    check('repeated-clipped-same-epoch',m,897,True)
    return rows


def hot_vectors(seed):
    import check_prince_climb_funded_irq_1109_v2 as Async
    watch=[(2,0xd53e,0xd672),(2,0xdfcc,0xdfe0),(3,0xb310,0xb369),(2,0xc386,0xc3b0)]
    rows=[]
    for name,m in walls(seed)[1]:
        Q.Sonic.O.clear_logs(m)
        rows.append(Async.stress('actual native BG '+name,m,
            lambda q:I.invoke(q,3,I.address(q.bundle,'PlayerBGCollision'))['regs'],watch))
    m=wall_fixture(seed)
    Q.Sonic.O.clear_logs(m)
    rows.append(Async.stress('actual full16 export low/high capture',m,
        lambda q:I.invoke(q,3,0xc383)['regs'],watch))
    return rows


def extension_faults(result):
    _,trial,chunks,layout,program,_,_=result;cases=[]
    for target in (0xdfcc,0xdfdf):
        m=Q.Sonic.O.blank(trial);bus=type(m);write=bus.__setitem__;native=N.NesMPU
        pc=-1;starts=0;injected=False
        class Trace(native):
            def step(self):
                nonlocal pc,starts
                if self.memory is m:
                    pc=self.pc
                    if pc==0xc000 and m.rawtags[2]==2:starts+=1
                return super().step()
        def writer(self,key,value):
            nonlocal injected
            if self is m and not injected and starts==2 and pc==0xc0c8 and key==target:
                injected=True;value^=1
            return write(self,key,value)
        with patch.object(bus,'__setitem__',writer),patch.object(N,'NesMPU',Trace),patch.object(Q.Sonic.O,'NesMPU',Trace):
            out=Q.Sonic.C.cold(m,38,program['new'],expect_success=False)
        assert injected and Q.Sonic.O.headers(m)==(bytes(16),)*2
        assert not Q.Sonic.C.invoke(m,Q.Sonic.O.AUTH)['P']&1
        retry=Q.Sonic.C.cold(m,38,program['new'])
        assert Q.Sonic.O.headers(m)==(bytes.fromhex(layout['Prince_cookie']),)*2
        assert bytes(m.ram[2][0x1fcc:0x1fe0])==chunks[1][-20:]
        cases.append(dict(target=target,injected=True,failed_closed=True,retry_succeeded=True,
            failure_CPU=out['CPU'],retry_CPU=retry['CPU']))
    return cases


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for flag in ('points','admission','export','camera','regressions','cold-vectors','walls','negative','hot-vectors','extension-faults'):p.add_argument('--'+flag,action='store_true')
    args=p.parse_args()
    _,old_bundle,_,_,_,_,_=Q.proposal();old,_=Q.P.Q.C.C.cold(old_bundle,38)
    new=Q.Sonic.slim_fork(old);V.apply(new)
    for flag,fn in (('points',points),('admission',admissions),('export',exports),('camera',cameras)):
        if getattr(args,flag):print('WALL_'+flag.upper()+' '+json.dumps(fn(old,new),separators=(',',':')),flush=True)
    if args.regressions:regressions(V.proposal())
    if args.cold_vectors:
        import check_prince_floor_vectors_1110 as Vectors
        _,trial,chunks,layout,_,_,_=V.proposal()
        print('WALL_COLD_VECTORS '+json.dumps(Vectors.cold_vectors(trial,chunks,layout),separators=(',',':')),flush=True)
    if args.walls:
        result=V.proposal();seed,_=Q.actual_cold(result[1],result[2],result[3],result[4])
        print('WALL_NATIVE_CASES '+json.dumps(walls(seed)[0],separators=(',',':')),flush=True)
    if args.negative or args.hot_vectors or args.extension_faults:
        result=V.proposal();seed,_=Q.actual_cold(result[1],result[2],result[3],result[4])
        if args.negative:print('WALL_NEGATIVES '+json.dumps(negatives(seed),separators=(',',':')),flush=True)
        if args.hot_vectors:print('WALL_HOT_VECTORS '+json.dumps(hot_vectors(seed),separators=(',',':')),flush=True)
        if args.extension_faults:print('WALL_EXTENSION_FAULTS '+json.dumps(extension_faults(result),separators=(',',':')),flush=True)


if __name__=='__main__':main()
