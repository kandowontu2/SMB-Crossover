"""Bounded zero-output checks for Jay's existing-native pickup platform."""

import argparse
from collections import Counter, deque
import json
import inspect
import contextlib
import io

import compose_jay_pickup_helper_1113 as P

B=P.B
Current=B.Current
N,W=Current.N,Current.W


def call(m,pc,observe=None,*,a=83,x=71,y=109,p=0x31):
    m.raw_page(1,3);m.raw_page(2,2);N.put(m,CurrentBank=3,CurrentBankC=2)
    c=N.NesMPU(memory=m,pc=pc)
    c.a,c.x,c.y,c.p,c.sp=a,x,y,p,224
    c.stPushWord(0x5aff)
    B.Gun.C.Vector.finish(m,c,(0x5b00,224),observe)
    assert(c.a,c.x,c.y,c.p&0xef)==(a,x,y,(p|32)&0xef)
    return c


def finite(raw,info):
    bundle=dict(W.Symbols.bundle(),raw=raw)
    fields=info['fields'];counts=Counter()
    for index,left in enumerate((688,880,384)):
        for relative in(255,256,270,287,288):
            for occupied in range(64):
                m=B.Gun.C.Common.blank(bundle)
                B.Gun.C.Common.scene(m,16);m[0x730b]=32
                data=info['new']['images']['HELPERS']
                m.ram[3][P.ORIGIN-0xa000:P.ORIGIN-0xa000+len(data)]=data
                for slot in range(6):
                    m[fields['EnemyFlag']+slot]=(occupied>>slot)&1
                    m[fields['EnemyID']+slot]=6
                camera=left-relative
                N.put(m,AreaType=1,WorldNumber=0,LevelNumber=0,TimerControl=0,
                      ScreenLeft_PageLoc=camera>>8,ScreenLeft_X_Pos=camera&255,ObjectOffset=2)
                m.ram[2][0x3d]=7^(1<<index)
                scratch=bytes(m[3:11]);before=[Current.actor(m,s)for s in range(6)]
                entered=[]
                def observe(m,c):
                    if m.rawtags[1]==130 and c.pc==0xa74f:entered.append(c.x)
                call(m,P.ORIGIN,observe)
                admitted=256<=relative<=287 and occupied!=63
                assert len(entered)==int(admitted),(index,relative,occupied,entered)
                assert bytes(m[3:11])==scratch and N.get(m,'ObjectOffset')==2
                for s in range(6):
                    if(occupied>>s)&1:assert Current.actor(m,s)==before[s]
                if admitted:
                    s,=entered
                    assert s==max(i for i in range(6)if not(occupied>>i)&1)
                    a=Current.actor(m,s)
                    assert(a['flag'],a['id'],a['x'],a['y'])==(1,37,left,192)
                    assert N.get(m,'Enemy_Y_HighPos',s)==1 and N.get(m,'Enemy_BoundBoxCtrl',s)==5
                    assert N.get(m,'Enemy_X_Speed',s)==(169,161,169)[index]
                    assert m.ram[2][0x3d]==7
                    second=[Current.actor(m,s)for s in range(6)]
                    call(m,P.ORIGIN,observe)
                    assert len(entered)==1 and second==[Current.actor(m,s)for s in range(6)]
                    counts['constructor_and_no_repeat']+=1
                else:
                    assert m.ram[2][0x3d]==7^(1<<index)
                    counts['declined_without_seen']+=1
    return dict(counts)


def fixture(raw,info,left=384,relative=287,occupied=0):
    bundle=dict(W.Symbols.bundle(),raw=raw)
    m=B.Gun.C.Common.blank(bundle);B.Gun.C.Common.scene(m,16);m[0x730b]=32
    body=info['new']['images']['HELPERS']
    m.ram[3][P.ORIGIN-0xa000:P.ORIGIN-0xa000+len(body)]=body
    for slot in range(6):m[info['fields']['EnemyFlag']+slot]=(occupied>>slot)&1
    camera=left-relative
    N.put(m,AreaType=1,WorldNumber=0,LevelNumber=0,TimerControl=0,
          ScreenLeft_PageLoc=camera>>8,ScreenLeft_X_Pos=camera&255,ObjectOffset=2)
    m.ram[2][0x3d]=3
    return m


def guards(raw,info):
    counts=Counter()
    for name,values in dict(AreaType=(0,2,3,255),WorldNumber=(1,7,255),LevelNumber=(1,3,255),
                            TimerControl=(1,255),ScreenLeft_PageLoc=(3,4,255)).items():
        for value in values:
            m=fixture(raw,info);N.put(m,**{name:value})
            before=[Current.actor(m,s)for s in range(6)]
            call(m,P.ORIGIN)
            assert before==[Current.actor(m,s)for s in range(6)]and m.ram[2][0x3d]==3
            counts['scene_declined']+=1
    for slot in range(6):
        m=fixture(raw,info,occupied=63);call(m,P.ORIGIN)
        assert m.ram[2][0x3d]==3
        m[info['fields']['EnemyFlag']+slot]=0
        call(m,P.ORIGIN)
        assert m.ram[2][0x3d]==7 and N.get(m,'Enemy_ID',slot)==37
        counts['full_then_free_retry']+=1
    m=fixture(raw,info);m.ram[2][0x3d]=0
    call(m,P.ORIGIN)
    assert m.ram[2][0x3d]==4
    slot=next(s for s in range(6)if N.get(m,'Enemy_Flag',s)and N.get(m,'Enemy_ID',s)==37)
    m[info['fields']['EnemyFlag']+slot]=0
    call(m,P.ORIGIN)
    assert m.ram[2][0x3d]==4 and not any(N.get(m,'Enemy_Flag',s)for s in range(6))
    counts['one_bit_consumed_after_retirement']=1
    for seen in range(8):
        m=fixture(raw,info);m.ram[2][0x3d]=seen;m.ram[2][0xd7]=3
        m.raw_page(1,3);N.put(m,CurrentBank=3)
        c=N.NesMPU(memory=m,pc=info['new']['symbols']['ResetHelpers']);c.sp=224
        c.stPushWord(0x5aff);B.Gun.C.Vector.finish(m,c,(0x5b00,224))
        assert(m.ram[2][0x3d],m.ram[2][0xd7])==(0,0)
        counts['reset_seen_and_drop']+=1
    # Existing two records produce identical native actors, including their
    # complete per-slot constructor effects, when the new record is consumed.
    for index,left in enumerate((688,880)):
        for rel in(255,256,270,287,288):
            a=fixture(raw,info,left,rel);b=Current.C.L.clone(a)
            a.ram[2][0x3d]=b.ram[2][0x3d]=6 if index==0 else 5
            old=info['old']['images']['HELPERS']
            a.ram[3][P.ORIGIN-0xa000:P.ORIGIN-0xa000+len(old)]=old
            call(a,P.ORIGIN);call(b,P.ORIGIN)
            assert a.ram[0]==b.ram[0]and a.ram[1]==b.ram[1]and a.ram[2]==b.ram[2]
            counts['existing_record_exact_pair']+=1
    seed=fixture(raw,info)
    for p in range(256):
        m=Current.C.L.clone(seed);scratch=bytes(m[3:11])
        call(m,P.ORIGIN,a=(p*3)&255,x=(p*7)&255,y=255-p,p=p)
        assert bytes(m[3:11])==scratch and N.get(m,'ObjectOffset')==2
        counts['AXYP_all_status_values']=counts.get('AXYP_all_status_values',0)+1
    return dict(counts)


def vectors(raw,info):
    _,seed=P.Head.cold(raw,P.COOKIE,P.PIN)
    cuts=set();counts=Counter();floor=224
    for camera,seen,occupied,area in((97,3,0,1),(97,3,63,1),(96,3,0,1),(128,3,0,1),
                                    (0,0,0,1),(97,7,0,1),(97,3,0,0),(401,6,0,1)):
        m=Current.C.L.clone(seed)
        N.put(m,ScreenLeft_PageLoc=camera>>8,ScreenLeft_X_Pos=camera&255,AreaType=area,
              WorldNumber=0,LevelNumber=0,TimerControl=0,DisableScreenFlag=1,NmiDisable=255)
        m.ram[2][0x3d]=seen
        for slot in range(6):m[info['fields']['EnemyFlag']+slot]=(occupied>>slot)&1
        def observe(m,c):
            nonlocal floor
            tag=m.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else -1
            used=(tag==3 and P.ORIGIN<=c.pc<0xbe17)or 0x15a<=c.pc<0x17b or(tag==130 and 0xa74f<=c.pc<0xa756)
            key=tag,c.pc
            if not used or key in cuts:return
            cuts.add(key)
            for kind in('FF',)if c.p&4 else('FF','IRQ'):
                _,branch=B.Gun.C.Vector.clone(m,c)
                floor=min(floor,B.Gun.C.ColdVector.interrupt(branch,kind));counts[kind]+=1
        call(m,P.ORIGIN,observe)
    return dict(instruction_cuts=len(cuts),interrupts=dict(counts),minimum_SP=floor,
                exact_CPU_stack_RAM_mapper_restoration=True)


def cold(raw,info):
    import check_steve_shatterhand_companion_transport_1111 as Cold
    import check_steve_shatterhand_upgrade_transport_1111 as Upgrade
    cuts=set();floors=[]
    original=B.Gun.C.ColdVector.interrupt
    source=inspect.getsource(original);needle='assert floor >= 0x7b'
    assert source.count(needle)==1
    scope=dict(original.__globals__)
    exec(compile(source.replace(needle,'assert floor >= 0x7a'),'<shared descriptor baseline SP7a>','exec'),scope)
    results={}
    for image,cookie,label in((P.inverse(raw),P.Head.NEW_COOKIE,'head_parent'),(raw,P.COOKIE,'helper')):
        wrapper=Cold.compact_cold(cookie,extended=True,upgrade=Upgrade.descriptor(371))
        at=B.Gun.C.offset(65,B.Gun.T.COLD)
        assert image[at:at+B.Gun.T.COLD_SIZE]==wrapper['images']['COLD65'].ljust(B.Gun.T.COLD_SIZE,b'\xea')
        bundle=dict(W.Symbols.bundle(),raw=image)
        target=wrapper['symbols']['JaySceneOrRetire']
        def fresh(variant):
            m=B.Gun.C.Common.blank(bundle);B.Gun.C.Common.scene(m,16);m[0x730b]=variant<<5
            return m
        def load(m,interrupts=False):
            c=B.Gun.C.ColdVector.entry(m);m[0x16c],m[0x16d]=target&255,target>>8
            def observe(m,c):
                if not interrupts or m.rawtags[2]!=2 or not 0xd000<=c.pc<0xd101:return
                key=c.pc,c.p&1
                if key in cuts:return
                cuts.add(key)
                _,branch=B.Gun.C.Vector.clone(m,c);floors.append(scope['interrupt'](branch,'FF'))
            B.Gun.C.Vector.finish(m,c,(0x5b00,224),observe)
            assert(c.a,c.x,c.y,c.p&0xef,c.sp)==(83,71,109,0x21,224)
        cuts.clear();floors.clear();rows={}
        for variant in(1,2):
            m=fresh(variant);load(m,variant==1)
            assert B.Gun.C.Common.headers(m)==(cookie,)*2 and m.ppu_reads==32800
            expected=info['new'if label=='helper'else'old']['images']['HELPERS']
            assert bytes(m.ram[3][P.ORIGIN-0xa000:P.ORIGIN-0xa000+247])==expected
            load(m);assert m.ppu_reads==32800
            rows[variant]=dict(cold_reads=32800,warm_reads=0)
        fault_count=0
        if label=='helper':
            for fault in((3,0x1d20),(3,0x1e02),(3,0x1837)):
                m=fresh(1);m.corrupt_at=fault;load(m)
                assert not any(h[0]for h in B.Gun.C.Common.headers(m));fault_count+=1
        assert min(floors)==0x7a
        results[label]=dict(variants=rows,NMI_cuts=len(cuts),minimum_SP=min(floors),readback_faults=fault_count)
    return results


def foreign(raw):
    before=P.inverse(raw)
    bundles=[dict(W.Symbols.bundle(),raw=image)for image in(before,raw)]
    result={};pads=[0]*6+[64]*12+[1]*19+[129]*9+[2]*15+[0]*10+[64]*9
    for variant,name in((0,'MIKE JONES'),(2,'STEVE HERMANN')):
        row=dict(name=name,slot=15,cycle=variant,raw=16)
        a,b=[Current.C.cold(bundle,row)[1]for bundle in bundles]
        def compare():
            old,new=B.Gun.C.Vector.app(a),B.Gun.C.Vector.app(b)
            assert old[:3]+old[4:]==new[:3]+new[4:]
            assert a.ram[2][:0x1000]==b.ram[2][:0x1000]and a.ram[0]==b.ram[0]and a.ram[1]==b.ram[1]
            assert a.vram==b.vram and a.chr_latches==b.chr_latches
        compare()
        for pad in pads:
            a.controller_pad=b.controller_pad=pad
            Current.Frames.frame(a);Current.Frames.frame(b);compare()
        if not variant:assert a.ram==b.ram
        result[name]=dict(paired_updates=len(pads),exact_native_and_live_private=True)
    return result


def parity(raw):
    import replay_jay_pickup_helper_1113 as Replay
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    script=Replay.controller(raw)
    prefix=script.split('local function pause(n)',1)[0]
    lua=LuaRuntime();current=[None]
    def read(at,kind):return current[0][at]if kind==0 else current[0].ram[at//8192][at%8192]
    emu=lua.table();emu['read']=read;emu['memType']=lua.table_from(dict(nesDebug=0,nesWorkRam=1))
    lua.globals()['emu']=emu;lua.globals()['os']['getenv']=lambda name:P.PIN
    lua.execute(prefix+'\nfunction jayBegin()game=true;opening=60 end\nfunction jayDrive()drive();return pad end')
    lua.globals().jayBegin();compared=[]
    def check(m,epoch,pad):
        current[0]=m;actual=lua.globals().jayDrive()
        assert actual==pad,(epoch,pad,actual,Current.state(m));compared.append(pad)
    with contextlib.redirect_stdout(io.StringIO()):result=route(raw,pad_observer=check)
    assert result['passed']
    return dict(script_SHA256=P.digest(script.encode()),compared_inputs=len(compared),actual_CPU_route=result)


def stage(raw,info):
    """Repeat original stage controls using the exact changed helper symbols."""
    Motion=B.Gun.T.Motion
    bundle=dict(W.Symbols.bundle(),raw=raw)
    m=B.Gun.C.menu(bundle,1)
    for tick in range(220):
        if tuple(N.get(m,n)for n in Motion.STATES)==(1,3,8):break
        m.controller_pad=0;Current.Frames.frame(m)
    else:raise AssertionError('Helper candidate Jay ingress')
    assert B.Gun.C.Common.headers(m)==(P.COOKIE,)*2
    helper=info['new'];body=helper['images']['HELPERS']
    assert bytes(m.ram[3][0x1d20:0x1d20+len(body)])==body
    work,fields=Motion.assemble_handoff(bundle,bytes(m.ram[3][0x88d:0x8c0]),origin=0xb800,
        control_tail=True,native_sync=True,native_helpers=(helper['symbols']['StepHelpers'],helper['symbols']['ResetHelpers']),pit_boundary=True)
    work.update(tile=B.Gun.C.Jay.build()['symbols']['JayHostTile'],status=0xc0f3)
    early=Motion.assisted_route(m,fields,work)
    assert early['lives']==2 and early['terminal']==(995,176,883),early
    assert [v['pipe']for v in early['carry']]==[3,4]
    late=Motion.late_route(m,fields,middle_hold=2)
    assert late['lives']==2 and late['scene'][3]==1 and len(late['gap_landings'])==3,late
    for entrance in range(550):
        if tuple(N.get(m,n)for n in Motion.STATES)==(1,3,8)and N.get(m,'LevelNumber')==1:
            if N.get(m,'Player_State')==0 and N.get(m,'Player_Y_Position')==176:break
        m.controller_pad=0;Current.Frames.frame(m)
    else:raise AssertionError(('Helper candidate 1-2 ingress',Current.state(m)))
    assert m.ram[2][0xbf]==3 and m.ram[2][0x20]==0 and m.ram[2][0xbe]==63
    assert m.ram[2][0x3d]==0 and m.ram[2][0xd7]==0
    assert not any(N.get(m,'Enemy_Flag',s)and N.get(m,'Enemy_ID',s)==37 and Current.actor(m,s)['x']==384 for s in range(6))
    return dict(controller_only=True,early=early,late=late,entrance_wait=entrance,terminal=Current.state(m),
                helper_seen_and_drop_reset=True)


def route(raw,limit=1400,detail=False,pad_observer=None):
    _,m=P.Head.cold(raw,P.COOKIE,P.PIN)
    phase,at='approach',0
    heads,births,platforms,boards,departures=[],[],[],[],[]
    recent=deque(maxlen=16);trace=[];pending=None;collected=None
    collector=W.address(m.bundle,'HandlePowerUpCollision')
    head=W.address(m.bundle,'PlayerHeadCollision')
    native_tag=lambda pc:m.rawtags[(pc-0x8000)//8192]
    def observe(m,c):
        nonlocal pending,collected
        if m.rawtags[1]==130 and c.pc==0xa74f and N.get(m,'Enemy_ID',c.x)==37:
            a=Current.actor(m,c.x)
            if a['x']==384 and not platforms:
                s=Current.state(m)
                platforms.append(dict(actor=a,player=s,relative=384-s['camera'],epoch=epoch))
        if pending and(c.pc,c.sp)==pending['return']:
            collected=dict(before=pending['before'],item=pending['item'],after=Current.state(m),epoch=epoch,
                           erased=N.get(m,'Enemy_Flag',pending['item']['slot'])==0)
            pending=None
        if c.pc==head and native_tag(head)==254:heads.append(dict(epoch=epoch,tile=c.a,player=Current.state(m)))
        if c.pc==collector and native_tag(collector)==254:
            pending=dict(before=Current.state(m),item=Current.actor(m,c.x),
                         return_=(0,0))
            pending['return']=(m[0x101+c.sp]+256*m[0x102+c.sp]+1,c.sp+2)
    for epoch in range(limit):
        s=Current.state(m);x=s['x'];y=s['Player_Y_Position'];ground=s['Player_State']==0
        actors=[Current.actor(m,i)for i in range(6)if N.get(m,'Enemy_Flag',i)]
        item=next((a for a in actors if a['id']==46),None)
        platform=next((a for a in actors if a['id']==37 and a['x']==384),None)
        if platform and not platforms:platforms.append(dict(actor=platform,player=s,relative=384-s['camera'],epoch=epoch))
        if item and not births:births.append(dict(actor=item,player=s,epoch=epoch))
        contact=N.get(m,'PlatformCollisionFlag',platform['slot'])if platform else 255
        boarded=platform and contact==platform['slot'] and y+32==platform['y'] and ground
        if boarded and not boards:boards.append(dict(actor=platform,player=s,epoch=epoch))
        if collected and epoch-collected['epoch']>=8:
            assert heads and heads[0]['tile']==193 and births and platforms and boards and departures
            assert 256<=platforms[0]['relative']<=287 and platforms[0]['actor']['y']==192
            assert collected['erased'] and(collected['item']['state'],collected['item']['private'],collected['item']['owner'])==(128,129,16)
            assert(collected['before']['JnHealth'],collected['before']['JnMaxHearts'])==(6,3)
            assert(collected['after']['JnHealth'],collected['after']['JnMaxHearts'],collected['after']['Square2SoundQueue'])==(8,4,32)
            assert(s['JnHealth'],s['JnMaxHearts'],s['NumberofLives'])==(8,4,2)
            return dict(passed=True,controller_only=True,heads=heads,births=births,platform_birth=platforms,
                        boards=boards,departures=departures,collected=collected,final=s,trace=trace if detail else [])
        assert s['NumberofLives']==2 and s['GameEngineSubroutine']!=11,(epoch,phase,s)
        near=any(a['id']<21 and not a['state']&32 and 0<a['x']-x<100 and abs(a['y']-y)<30 for a in actors)
        shot=64 if near and epoch%12<2 else 0
        def change(p):
            nonlocal phase,at
            phase,at=p,epoch
        if phase=='approach'and x>=332 and ground:change('park')
        if phase=='park'and epoch-at>=8:change('reveal')
        if item and phase in('approach','park','reveal'):change('lift-approach')
        if phase=='approach':pad=1+shot
        elif phase=='park':pad=shot
        elif phase=='reveal':pad=(128 if epoch-at<18 else 0)+shot
        elif phase=='lift-approach':
            pad=(1 if x<408 else 0)+shot
            if x>=408 and ground:change('lift-wait');pad=shot
        elif phase=='lift-wait':
            pad=shot
            if boarded:change('lift-ride')
            elif platform and ground and platform['y']>=176:change('lift-board');pad|=128
        elif phase=='lift-board':
            pad=(128 if epoch-at<18 else 0)+shot
            if boarded:change('lift-ride');pad=shot
            elif ground and epoch-at>20:change('lift-wait')
        elif phase=='lift-ride':
            pad=shot
            if boarded and platform['y']<=168:
                change('lift-face');pad=2+shot
        elif phase=='lift-face':
            pad=shot
            if boarded and s['donor_flags']&2 and not s['donor_control']&0x38:
                change('collect-jump');pad=130+shot
                departures.append(dict(epoch=epoch,actor=platform,player=s))
        elif phase=='collect-jump':
            pad=(2 if item and x>item['x']else 0)+shot
            if epoch-at<18:pad|=128
        else:pad=0
        if pad_observer:pad_observer(m,epoch,pad)
        row=dict(epoch=epoch,phase=phase,pad=pad,contact=contact,platform=platform,**s)
        recent.append(row)
        if detail:trace.append(row)
        if epoch%128==0:print(json.dumps(dict(event='jay_helper_route',**row)),flush=True)
        m.controller_pad=pad
        Current.Frames.frame(m,observe)
    return dict(passed=False,phase=phase,recent=list(recent),heads=heads,births=births,platforms=platforms,boards=boards,departures=departures)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--part',choices=('finite','guards','vectors','cold','foreign','parity','stage','route'),default='finite')
    p.add_argument('--detail',action='store_true')
    args=p.parse_args()
    image,info=P.proposal(P.frozen_head())
    assert P.inverse(image)==P.frozen_head()
    result={'finite':lambda:finite(image,info),'guards':lambda:guards(image,info),
            'vectors':lambda:vectors(image,info),'cold':lambda:cold(image,info),
            'foreign':lambda:foreign(image),'parity':lambda:parity(image),
            'stage':lambda:stage(image,info),
            'route':lambda:route(image,detail=args.detail)}[args.part]()
    print(json.dumps(dict(ROM_SHA256=P.PIN,output_files=0,part=args.part,result=result)),flush=True)
    if args.part=='route':assert result['passed']
