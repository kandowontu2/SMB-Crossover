"""Source-funded Mini/Karnov independent Up/Down+Select native helpers."""

import argparse
from collections import Counter
from hashlib import sha256
from itertools import product
import json
import inspect
from pathlib import Path
import subprocess
import tempfile

import check_manual_vertical_platform_1110 as P


R,N = P.R,P.N
OUT = R/'build/manual-dual-platform-1110'
BASE = R/'build/getsu-current-native-1110/candidate.nes'
PIN = '095c164a574479401f284c1669264034404b83cb2e1d6cdc4a1f5ef37dcafe79'
SOURCE = R/'tools/reference/manual_dual_platform_1110.s'
KARNOV_SOURCE = R/'tools/reference/karnov_manual_dual_platform_1110.s'
MINI_SOURCE = R/'tools/reference/mini_manual_dual_platform_1110.inc'
CODE=P.L.CODE


def funding(raw,out):
    source=P.PROTOMAN.read_text()
    body=source[:source.index('.assert ProtoMm3::_nmi_audio_processing')]
    assert body.endswith('.endscope\n.popseg\n\n')
    assert body.count('.align $100')==1
    body=body.replace('.align $100','.align $100,$ff')
    with tempfile.TemporaryDirectory(dir=out) as tmp:
        work=Path(tmp)
        path=work/'funding.s'
        symbols=P.L.M.bundle(raw)
        defs=''.join(f'{name}=${P.L.M.address(symbols,name):04x}\n' for name in
            ('MmAudioEngine','GuestNativeStoreSTA00Y','GuestNativeStatusSTA','GuestNativeStoreSTA05','GuestNativeStoreSTA01'))
        path.write_text('.setcpu "6502"\nMAPPER_MMC5=1\nMm3AudioRam=$6980\n'+defs+body,encoding='utf-8')
        linked,_=P.link(work,path,(('PROTO_MM3_AUDIO',0xa000,8192),))
    assert len(linked)==0x1fdd
    bank=bytearray(raw[P.at(64,0xa000):P.at(64,0xa000)+8192])
    bank[0x1378:0x1400]=bytes([255])*136
    assert bytes(bank)==linked+bytes([255])*35,[(hex(0xa000+i),a,b) for i,(a,b) in enumerate(zip(bank,linked)) if a!=b][:12]
    assert linked[-4:]==bytes.fromhex('16bf1c17')
    assert source.count('pm3_music_jump music_staff_roll_noise_main')==1
    assert source.count('pm3_music_end\n\n.endscope\n.popseg')==1
    return dict(exact_entire_bank_reproduction=True,segment='PROTO_MM3_AUDIO',
                segment_start=0xa000,segment_bytes=len(linked),
                replacement_extent=[0xbfdd,0xc000],bytes=35,
                existing_manual_gap=[0xb378,0xb400],
                terminal_command=dict(pc=0xbfda,bytes='16bf1c17',jump_target=0xbf1c,
                    source='pm3_music_jump music_staff_roll_noise_main; pm3_music_end'),
                source_SHA256=sha256(P.PROTOMAN.read_bytes()).hexdigest())


def build(raw, out):
    assert sha256(raw).hexdigest()==PIN
    patches=[]
    with tempfile.TemporaryDirectory(dir=out) as tmp:
        work=Path(tmp)
        worker,wl=P.link(work,SOURCE,(('MANUAL',0xb378,136),('MANUAL_TAIL',0xbfdd,35)))
        main=wl['ManualPlatformEnd']-0xb378
        tail=wl['ManualPlatformTailEnd']-0xbfdd
        assert main==135 and tail==34 and len(worker)==main+tail
        assert raw[P.at(64,0xbfdd):P.at(64,0xbfdd)+35]==bytes([255])*35
        for pc,code in ((0xb378,worker[:main]),(0xbfdd,worker[main:])):
            patches.append(P.L.patch(raw,P.at(64,pc),code,'Shared native manual-axis constructor'))
        exports='\n.export MiniHeadEvent,MiniTempPixel\n'
        old,ol=P.compile_source(work,P.mini_source(P.MINI.read_text())+exports,P.L.CONFIG)
        mini,ml=P.compile_source(work,mini_source()+exports,P.L.CONFIG)
        assert old==raw[CODE:CODE+5120] and len(mini)==5120
        moved_private=('MiniManualInput','MiniPlatformFloor','MiniHeadEvent','MiniTempPixel')
        assert {k:v for k,v in ol.items() if k not in moved_private}=={
            k:ml[k] for k in ol if k not in moved_private}
        patches.append(P.L.patch(raw,CODE,mini,'Same five Mini pages; all public entries pinned'))
        digest=sha256(mini+raw[CODE+5120:CODE+7168]).digest()[:13]
        assert raw[P.L.COOKIE:P.L.COOKIE+16]==bytes([167,41,1])+sha256(raw[CODE:CODE+7168]).digest()[:13]
        patches.append(P.L.patch(raw,P.L.COOKIE+3,digest,'Authentic complete Mini payload digest'))
        kr,kl=P.link(work,KARNOV_SOURCE,(('OPTIONS',0xb378,136),('RESET',0xddf7,9)))
        count=kl['KrManualOptionsEnd']-0xb378
        assert count==130 and kr[count:]==raw[P.KR_OPTIONS+0x7f7:P.KR_OPTIONS+0x7fe]
        patches.append(P.L.patch(raw,P.at(11,0xb378),kr[:count],'Karnov independent pending-axis bits; existing reset retained'))
        assert raw[P.KR_CODE+0x1fcb:P.KR_CODE+0x1fce]==bytes.fromhex('a9788d')
        labels=wl|ml|kl|{'KrManualIngress':0xbfcb,'BeforeMiniHeadEvent':ol['MiniHeadEvent'],'BeforeMiniTempPixel':ol['MiniTempPixel']}
    return P.install(raw,patches),patches,labels,mini


def owned(bus, kind=None):
    return [(s,row) for s,row in enumerate(P.actors(bus))
            if row[:3] in ((1,0x25,0x41),(1,0x28,0x42))
            and (kind is None or row[1]==kind)]


def offset(owner, horizontal, facing=1):
    center=4 if owner==41 else 8
    return (center-48 if facing==2 else center+16) if horizontal else center-16


def ctor(seed,owner):
    counts=Counter()
    for horizontal,facing,mask,mode in product((False,True),(1,2),range(64),('pool','replace','other-axis','foreign-sidecar')):
        m=P.slim_fork(seed)
        marker=0x42 if horizontal else 0x41
        actor=0x28 if horizontal else 0x25
        px=(1,10,255,256,521,731)[mask%6]
        N.put(m,Player_X_Position=px&255,Player_PageLoc=px>>8,Player_Y_Position=176,
              Player_Y_HighPos=1,PlayerFacingDir=facing,ObjectOffset=mask%6)
        for slot in range(6):
            P.set_slot(m,slot,Enemy_Flag=int(bool(mask&(1<<slot))),Enemy_ID=6,
                       Enemy_State=marker,FloateyNum_Control=0)
        want=min((s for s in range(6) if not mask&(1<<s)),default=None)
        prior=mask%6
        if mode!='pool':
            P.set_slot(m,prior,Enemy_Flag=1,Enemy_ID=actor,Enemy_State=marker)
            if mode=='replace': want=prior
            else:
                if mode=='other-axis':
                    P.set_slot(m,prior,Enemy_ID=0x25 if horizontal else 0x28,Enemy_State=0x41 if horizontal else 0x42)
                else: m[0x73ae+prior]=1
                want=min((s for s in range(6) if s!=prior and not mask&(1<<s)),default=None)
        before=P.actors(m)
        maps=tuple(m.rawtags)
        result=N.invoke(m,'ManualPlatform',x=marker,y=offset(owner,horizontal,facing)&255)
        after=P.actors(m)
        assert tuple(m.rawtags)==maps and N.get(m,'ObjectOffset')==prior
        if want is None:
            assert result['A']==result['X']==128 and before==after
        else:
            left=max(0,px+offset(owner,horizontal,facing))
            assert result['A']==result['X']==want+1
            assert after[want][:8]==(1,actor,marker,left&255,left>>8,208,1,5),(owner,horizontal,facing,mask,mode,after[want])
            assert all(a==b for s,(a,b) in enumerate(zip(before,after)) if s!=want)
            assert m[0x73ae+want]==0
        counts[mode]+=1
    return dict(counts)


def controls(seed,owner,labels):
    m=P.slim_fork(seed)
    births=[]
    original=N.NesMPU
    class Trace(original):
        def step(self):
            if self.pc==labels['ManualPlatformCreated'] and self.memory.rawtags[1]==0xc0:
                row=P.fields(self.memory,P.SLOT_FIELDS,self.x)
                p=P.fields(self.memory,P.PLAYER_FIELDS)
                facing=N.get(self.memory,'PlayerFacingDir')
                horizontal=row[1]==0x28
                assert row[:3]==(1,0x28 if horizontal else 0x25,0x42 if horizontal else 0x41)
                assert row[7]==5 and P.world(row,3,4)==max(0,P.world(p)+offset(owner,horizontal,facing))
                assert row[5]==p[2]+32
                births.append(dict(slot=self.x,actor=row[1],left=P.world(row,3,4),top=row[5],player_x=P.world(p)))
            return original.step(self)
    N.NesMPU=Trace
    try:
        if owner==34:
            m.ram[2][0x8f]=0x89
            m.ram[2][0x8e]=255
        for held in (0,0x20,0,8,0,4,0,0x2c):
            P.frame(m,held)
            assert not births
        option=m.ram[2][0x8e] if owner==34 else None
        for held in (0,8,0x28)+(0x28,)*60:
            P.frame(m,held)
        assert len(births)==1 and len(owned(m,0x25))==1
        if owner==34: assert m.ram[2][0x8e]==option
        vertical=births[0]['slot']
        P.frame(m,0)
        P.frame(m,0x20)
        option=m.ram[2][0x8e] if owner==34 else None
        for _ in range(12): P.frame(m,0x24)
        assert len(births)==2 and len(owned(m))==2
        if owner==34: assert m.ram[2][0x8e]==option
        horizontal=births[1]['slot']
        assert horizontal!=vertical
        before=P.fields(m,P.SLOT_FIELDS,vertical)
        # Replacing horizontal does not erase or restart the vertical actor.
        P.frame(m,0)
        P.frame(m,4)
        P.frame(m,0x24)
        assert len(births)==3 and births[-1]['slot']==horizontal
        after=P.fields(m,P.SLOT_FIELDS,vertical)
        assert after[:5]==before[:5] and abs(after[5]-before[5])<=4,(owner,vertical,before,after,births)
        # The opposite completion order also replaces only the vertical kind.
        P.frame(m,0);P.frame(m,0x20);P.frame(m,0x28)
        assert len(births)==4 and births[-1]['slot']==vertical and len(owned(m))==2
        # Two queued kinds are retained independently under real slot pressure.
        q=P.slim_fork(seed)
        for slot in range(6):
            P.set_slot(q,slot,Enemy_Flag=1,Enemy_ID=0x23,Enemy_State=0,
                       Enemy_X_Position=220,Enemy_PageLoc=0,Enemy_Y_Position=160,Enemy_Y_HighPos=1)
        P.frame(q,0x28);P.frame(q,0);P.frame(q,0x24)
        assert not owned(q)
        pending=(q.ram[2][0x30e],q.ram[2][0x30f]) if owner==41 else (q.ram[2][0x866],)
        assert pending==((128,128) if owner==41 else (192,)),(owner,pending)
        N.invoke(q,'EraseEnemyObject',x=2)
        P.frame(q,0)
        assert len(owned(q))==1
        N.invoke(q,'EraseEnemyObject',x=3)
        P.frame(q,0)
        assert len(owned(q))==2 and len(owned(q,0x25))==len(owned(q,0x28))==1
        # Pending state is cold/life/scene-owned, existing area teardown owns slots.
        N.put(q,AreaPointer=0x26,LevelNumber=1,OperMode_Task=0,GameEngineSubroutine=0,
              FamilyMainCommit=1,DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255)
        N.invoke(q,'InitializeArea');N.invoke(q,'InitScreen')
        assert not owned(q)
        assert (q.ram[2][0x30e],q.ram[2][0x30f])==(0,0) if owner==41 else q.ram[2][0x866]==0
    finally: N.NesMPU=original
    return dict(births=births,independent_queues=True,invalid_chord_rejected=True,area_reset=True)


def motion(seed,owner,axis):
    m=P.slim_fork(seed)
    P.frame(m,axis)
    kind=0x25 if axis==0x28 else 0x28
    [(slot,birth)]=owned(m,kind)
    board=None
    for age in range(64):
        # The horizontal platform is one width in front, reached by walking.
        P.frame(m,0 if kind==0x25 else 1)
        support=m.ram[2][0x30d] if owner==41 else N.get(m,'PlatformCollisionFlag',slot)+1
        if support==slot+1 if owner==41 else support<129:
            board=age;break
    assert board is not None,(owner,axis,P.actors(m),P.fields(m,P.PLAYER_FIELDS))
    samples=[]
    for _ in range(60):
        P.frame(m,0)
        row=P.fields(m,P.SLOT_FIELDS,slot)
        p=P.fields(m,P.PLAYER_FIELDS)
        support=m.ram[2][0x30d] if owner==41 else N.get(m,'PlatformCollisionFlag',slot)+1
        native=N.get(m,'PlatformCollisionFlag',slot)
        samples.append((P.world(row,3,4),row[5],P.world(p),p[2],support,native))
    column=1 if kind==0x25 else 0
    assert max(r[column] for r in samples)-min(r[column] for r in samples)>=4,(owner,axis,samples)
    carried=[r for r in samples if abs(r[1]-r[3]-32)<=1 and (r[4]==slot+1 if owner==41 else r[4]<129)]
    assert len(carried)>=4,(owner,axis,samples)
    if kind==0x28:
        assert max(r[2] for r in carried)-min(r[2] for r in carried)>=4,(owner,axis,carried)
        assert sum(r[5]<128 for r in samples)>=40,(owner,axis,samples)
        assert all(r[1]-r[3]==32 for r in samples if r[5]<128),(owner,axis,samples)
    return dict(slot=slot,boarding_updates=board,carry_samples=len(carried),
                native_carry_samples=sum(r[5]<128 for r in samples),
                native_Y_range=[min(r[3] for r in samples),max(r[3] for r in samples)],
                platform_X_range=[min(r[0] for r in samples),max(r[0] for r in samples)],
                platform_Y_range=[min(r[1] for r in samples),max(r[1] for r in samples)],
                player_X_range=[min(r[2] for r in carried),max(r[2] for r in carried)])


def private_call(m,pc,*,a=85,x=0,y=91,p=0x31):
    N.put(m,CurrentBank=3)
    m[0x5115]=3
    c=N.NesMPU(memory=m,pc=pc)
    c.a,c.x,c.y,c.p,c.sp=a,x,y,p,224
    c.stPushWord(0x5aff)
    P.run(c,lambda q:q.pc==0x5b00)
    assert c.sp==224
    return c


def head_packet(seeds,labels):
    count=0
    for same,pattern in product((True,False),range(32)):
        worlds=[P.slim_fork(seed) for seed in seeds]
        for m in worlds:
            packet=bytes(((pattern*79+j*43)&255) for j in range(7))
            m[0xc2e0:0xc2e7]=packet
            m[0xc264:0xc268]=packet[:4] if same else bytes(v^128 for v in packet[:4])
            m[0xc25d:0xc264]=bytes([0x77])*7
            m[0xc268]=254
        a=private_call(worlds[0],labels['BeforeMiniHeadEvent'])
        b=private_call(worlds[1],labels['MiniHeadEvent'])
        assert worlds[0].ram[2][:0x1fe3]==worlds[1].ram[2][:0x1fe3]
        assert worlds[0].ram[2][0x1ff0:]==worlds[1].ram[2][0x1ff0:]
        assert a.x==b.x==0 and a.y==b.y
        count+=1
    for value in range(0,65536,31):
        worlds=[P.slim_fork(seed) for seed in seeds]
        for m in worlds: m[0xc270:0xc272]=value.to_bytes(2,'little')
        a=private_call(worlds[0],labels['BeforeMiniTempPixel'])
        b=private_call(worlds[1],labels['MiniTempPixel'])
        assert worlds[0].ram[2][:0x1fe3]==worlds[1].ram[2][:0x1fe3]
        assert worlds[0].ram[2][0x1ff0:]==worlds[1].ram[2][0x1ff0:]
        assert (a.a,a.x,a.y,a.p)==(b.a,b.x,b.y,b.p)
    return dict(head_packets=count,projection_states=len(range(0,65536,31)),
        matched_packet_unchanged=True,caller_flags_liveness='Only caller MiniHeadEvent→yfinished loads MiniTemp/MiniNegative then MiniFinish compares before any carry use; A/NZ/V/C dead, X0/Y exact')


def vectors(bundle,labels,axis):
    # Retain the frozen real-vector checker; specialize only physical input,
    # typed constructor argument and ownership predicate for this axis.
    source=inspect.getsource(P.vectors).replace('def vectors(','def check(')
    source=source.replace('SavedJoypadBits=0x28, SavedJoypad1Bits=0x28',
                          f'SavedJoypadBits={axis}, SavedJoypad1Bits={axis}')
    source=source.replace("N.invoke(m,'ManualPlatform',y=0xf4 if owner==41 else 0xf8)",
        "N.invoke(m,'ManualPlatform',x="+str(0x41 if axis==0x28 else 0x42)+
        ",y="+("0xf4 if owner==41 else 0xf8" if axis==0x28 else "20 if owner==41 else 24")+")")
    env=dict(P.__dict__)
    env['owned']=lambda bus:owned(bus,0x25 if axis==0x28 else 0x28)
    source=source.replace('if not inside or key in seen:',
        "hot = owner == 41 and tag == 3 and (labels['MiniStep'] <= pc < labels['MiniWorldEnd'] or labels['MiniPlatformFloor'] <= pc < labels['MiniHostGraphics'])\n                if not (inside or hot) or key in seen:")
    exec(source,env)
    return env['check'](bundle,labels)


def mini_source():
    source=P.mini_source(P.MINI.read_text())
    spec=MINI_SOURCE.read_text()
    code,macros=spec.split('; Filled into the space recovered',1)
    source=macros[macros.index('.macro'):]+'\n'+P.replace_one(source,P.MINI_SOURCE.read_text(),code)
    old='''MiniHeadEvent:
    lda MiniScanX
    cmp MiniUpCacheX
    bne @new
    lda MiniScanX+1
    cmp MiniUpCacheX+1
    bne @new
    lda MiniScanY
    cmp MiniUpCacheY
    bne @new
    lda MiniScanY+1
    cmp MiniUpCacheY+1
    beq @done
@new:
    lda MiniScanX
    sta MiniUpCacheX
    sta MiniHeadX
    lda MiniScanX+1
    sta MiniUpCacheX+1
    sta MiniHeadX+1
    lda MiniScanY
    sta MiniUpCacheY
    sta MiniHeadY
    lda MiniScanY+1
    sta MiniUpCacheY+1
    sta MiniHeadY+1
    lda MiniQueryTile
    sta MiniHeadTile
    lda MiniQueryAddress
    sta MiniHeadAddress
    lda MiniQueryAddress+1
    sta MiniHeadAddress+1
    inc MiniHeadPending
@done:
    rts
'''
    new='''MiniHeadEvent:
    ldx #3
@compare:
    lda MiniScanX,x
    cmp MiniUpCacheX,x
    bne @new
    dex
    bpl @compare
    inx
    rts
@new:
    ldx #6
@copy:
    lda MiniScanX,x
    sta MiniHeadX,x
    cpx #4
    bcs @next
    sta MiniUpCacheX,x
@next:
    dex
    bpl @copy
    inx
    inc MiniHeadPending
    rts
    MiniManualDispatchBody
'''
    source=P.replace_one(source,old,new)
    pixel='''MiniToPixel:
    .repeat 4
      lsr a
      ror MiniCoord
    .endrepeat
    sta MiniCoord+1
    ldx #0
    rts
'''
    source=P.replace_one(source,pixel,'')
    source=P.replace_one(source,'    .export MiniHostInjury\nMiniHostInjury:',
                         '    .res $89d-(*-MiniStep),$ea\n    .export MiniHostInjury\nMiniHostInjury:')
    source=P.replace_one(source,'    .res $8c5-(*-MiniStep),$ea',pixel+'''MiniManualFar:
    lda #$c0
    jmp MiniFarCall
    .res $8c5-(*-MiniStep),$ea''')
    source=P.replace_one(source,'''MiniTempPixel:
    lda MiniTemp
    sta MiniCoord
    lda MiniTemp+1
    jmp MiniToPixel''','''MiniTempPixel:
    ldx #MiniTemp-MiniX
    jmp MiniHostPixelAxis''')
    source=P.replace_one(source,' jsr MiniManualInput\n sta MiniAssistState\n jsr MiniStep',
                         ' jsr MiniManualInput\n nop\n nop\n nop\n jsr MiniStep')
    source=P.replace_one(source,'''MiniPlatformFloor:
    lda MiniAssistState
    bne @collision
    ldx MiniLiftActor
    beq @miss
    lda MiniX+1
    and #$e0
    cmp #$20
    bne @miss
@collision:''','''MiniPlatformFloor:
    lda MiniAssistState
    ora MiniHorizontalState
    ora MiniLiftActor
    beq @miss''')
    source=P.replace_one(source,'''MiniManualFar:
    lda #$c0
    jmp MiniFarCall

; Mini's downward source sweep''', "; Mini's downward source sweep")
    source=P.replace_one(source,'MiniHostGraphics:\n',' .res 8,$ea\nMiniHostGraphics:\n')
    source=P.replace_one(source,'''    lda $1f,x
    and #$fe                 ; Authored $40 or manual $41, never native $00.
    cmp #$40
    bne @next
    lda $17,x                ; Existing native vertical lift type.
    cmp #$25
    bne @next''','''    lda $17,x
    cmp #$25
    beq @vertical
    cmp #$28
    bne @next
    lda $1f,x
    cmp #$42
    beq @flag
    bne @next
@vertical:
    lda $1f,x
    and #$fe
    cmp #$40
    bne @next
@flag:''')
    for axis,index in (('X',0),('Y',2)):
        old_copy=f'''    lda MiniCoord
    sta MiniScan{axis}
    lda MiniCoord+1
    sta MiniScan{axis}+1'''
        assert source.count(old_copy)==2
        source=source.replace(old_copy,f'    ldx #{index}\n    jsr MiniCopyToScan')
    land='''    tya
    .repeat 4
        asl a
    .endrepeat
    sta MiniTemp
    tya
    .repeat 4
        lsr a
    .endrepeat
    sta MiniTemp+1
    sec
    rts'''
    source=P.replace_one(source,'@land:\n'+land,'@land:\n    jmp MiniFloorLand')
    source=P.replace_one(source,'    .res $89d-(*-MiniStep),$ea', '''MiniCopyToScan:
    lda MiniCoord
    sta MiniScanX,x
    lda MiniCoord+1
    sta MiniScanX+1,x
    rts
MiniFloorLand:
'''+land+'\n    .res $89d-(*-MiniStep),$ea')
    source=P.replace_one(source,'''    sbc #8                   ; Mini source feet are source Y+8.
    tay''','''    sbc #8                   ; Mini source feet are source Y+8.
    ldy $17,x
    cpy #$28
    bne :+
    adc #0                   ; CMP equality supplied C=1: inclusive native H contact.
:
    tay''')
    return source


def fit():
    raw=BASE.read_bytes()
    assert sha256(raw).hexdigest()==PIN
    OUT.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=OUT) as work:
        work=Path(work)
        code,labels=P.link(work,SOURCE,(('MANUAL',0xb378,136),('MANUAL_TAIL',0xbfdd,35)))
        print('worker',len(code),labels,flush=True)
        kr,kl=P.link(work,KARNOV_SOURCE,(('OPTIONS',0xb378,136),('RESET',0xddf7,9)))
        print('karnov',len(kr),kl,flush=True)
        measurement=mini_source()
        mini,ml=P.compile_source(work,measurement,P.L.CONFIG)
        print('mini measurement',len(mini),{k:v for k,v in ml.items() if k in ('MiniManualInput','MiniManualDispatch','MiniWorldEnd','MiniNativeTile','MiniPlatformFloor','MiniHostEnd')},flush=True)
        _,old_labels=P.compile_source(work,P.mini_source(P.MINI.read_text()),P.L.CONFIG)
        moved={k:(v,ml[k]) for k,v in old_labels.items() if ml.get(k)!=v}
        print('moved',moved,flush=True)


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--fit',action='store_true')
    cli.add_argument('--cpu',action='store_true')
    cli.add_argument('--irq',action='store_true')
    args=cli.parse_args()
    if args.fit:
        fit();return
    assert args.cpu or args.irq
    OUT.mkdir(exist_ok=True)
    raw=BASE.read_bytes()
    candidate,patches,labels,kernel=build(raw,OUT)
    before,after=P.bundles(raw,candidate)
    print('exact memory image',sha256(candidate).hexdigest(),flush=True)
    if args.cpu:
        allocation=funding(raw,OUT)
        results={}
        for owner in (41,34):
            seed=P.scene(after,owner)
            results[owner]=dict(constructor=ctor(seed,owner),controls=controls(seed,owner,labels),
                                motion={axis:motion(seed,owner,axis) for axis in (0x28,0x24)})
            print('owner CPU',owner,results[owner],flush=True)
        regular={owner:P.regular_parity([P.scene(before,owner),P.scene(after,owner)],owner,raw,candidate)
                 for owner in (0,5,25,34,41)}
        head=head_packet([P.scene(before,41),P.scene(after,41)],labels)
        proof=dict(passed=True,source_CPU_only=True,ROM_written=False,Mesen_run=False,
                   parent_SHA256=PIN,expected_memory_only_SHA256=sha256(candidate).hexdigest(),
                   patches=patches,labels=labels,success_PC=labels['ManualPlatformCreated'],success_bank=64,
                   owner_CPU=results,no_chord=regular,source_funding=allocation,head_projection=head,
                   horizontal_alignment='Only manual ID28/state42 floor returns sourceY=top-7 (one inclusive contact pixel); native horizontal collision/motion owns carry and restores nativeY=top-32.6x7 bounds, terrain, vertical and original jump math unchanged.',
                   public_Mini_entries_pinned=True,
                   native_config=dict(width=32,markers={'vertical':[0x25,0x41],'horizontal':[0x28,0x42]},
                        Mini_pending=[0xc30e,0xc30f],Karnov_pending=0xc866,Karnov_queue_bits=[128,64],
                        centers={'41':4,'34':8},horizontal_offsets={'41':[20,-44],'34':[24,-40]}),
                   bindings={p.relative_to(R).as_posix():sha256(p.read_bytes()).hexdigest()
                    for p in (Path(__file__),SOURCE,MINI_SOURCE,KARNOV_SOURCE,BASE,P.PROTOMAN,P.SOURCE,
                              P.MINI,P.MINI.with_suffix('.bin'),Path(P.__file__))})
        (OUT/'proof.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
        (OUT/'kernel.bin').write_bytes(kernel)
        print('foreground PASS',regular,flush=True)
    if args.irq:
        proof=json.loads((OUT/'proof.json').read_text())
        assert proof['expected_memory_only_SHA256']==sha256(candidate).hexdigest()
        result={}
        for axis in (0x28,0x24):
            result[axis]=vectors(after,labels,axis)
            print('vectors',axis,result[axis],flush=True)
        receipt=dict(passed=True,parent_SHA256=PIN,expected_memory_only_SHA256=sha256(candidate).hexdigest(),
                     foreground_proof_SHA256=sha256((OUT/'proof.json').read_bytes()).hexdigest(),vectors=result)
        (OUT/'irq.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
        print('actual vectors PASS',result,flush=True)


if __name__=='__main__':
    main()
