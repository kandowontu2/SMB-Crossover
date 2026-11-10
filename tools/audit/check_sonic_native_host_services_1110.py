"""Actual native-bus Sonic service ctor/epoch/frame/projection, RAM only."""
import argparse
from collections import Counter
import copy
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import check_sonic_eighth_cold_owner_1110 as E
import sonic_sms_native_host_services_1110 as B

R,N,O,C=E.R,E.N,E.O,E.C
STOP=0x5b00


class ServiceBus(O.ControllerBus):
    active=False
    program=None
    def __getitem__(self,at):
        if self.active and isinstance(at,int)and 0xc800<=at<0xd900:
            raise AssertionError(('Retired source fixture read',hex(at)))
        return super().__getitem__(at)
    def __setitem__(self,at,value):
        if self.active and isinstance(at,int):
            p=self.program;host={int(self.bundle['syms'][n]['val'],0)for n in B.HOST}
            own=0xc000<=at<B.CONTEXT+len(B.FIELDS)or 0xc200<=at<0xc2b8 or 0xc300<=at<0xc31a
            assert own or 0x17b<=at<=0x1e0 or at in p['packet']['core']['SMC_operands']or at in host,('Unowned service write',hex(at),value)
            self.writes.append((at,value&255))
        super().__setitem__(at,value)


def invoke(m,pc,*,watch=True,limit=20000):
    c=O.NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=85,73,109,0x21,224
    c.stPushWord(STOP-1);minimum=c.sp;m.writes=[];m.active=watch
    try:
        for _ in range(limit):
            if c.pc==STOP:break
            assert m[c.pc],('Service BRK',hex(c.pc),m.rawtags)
            minimum=min(minimum,c.sp);c.step()
        else:raise AssertionError(('Service bound',hex(c.pc)))
    finally:m.active=False
    assert c.sp==224
    return c,minimum


def word(m,at):return m[at]|m[at+1]<<8
def host(m,name):return E.Alias.address(m.bundle,name)
def native(m,name):return m[host(m,name)]
def set_native(m,**fields):
    for name,value in fields.items():m[host(m,name)]=value
def private(m):return bytes(m.ram[2][:0xb4]),bytes(m.ram[3][at-0xa000]for at in m.program['packet']['core']['SMC_operands'])


def install(bundle,program,packet):
    m=O.blank(bundle);C.cold(m,43,C.B.build()['new']);E.owned(m,packet)
    m.raw_page(1,3);m.raw_page(2,2);N.put(m,CurrentBank=3,CurrentBankC=2)
    m.__class__=ServiceBus;m.program=program;m.active=False;m.writes=[]
    return m


def floor_domain(m,x):
    h=m.program['packet']['frame']['selector']['point']['host'];left=max(0,(x-128)//16);end=left+24
    values={'ColumnSets':255,'AreaParserTaskNum':0,'CurrentPageLoc':end//16,'CurrentColumnPos':end&15,
        'BlockBufferColumnPos':end&31,'ScreenLeftPage':left//16,'ScreenLeftX':(left&15)*16}
    for name,value in values.items():m[h[name]]=value
    for at in range(0x300,0x4a0):m[at]=255
    for col in range(left,end):
        for row in range(13):m[0x300+(col//16&1)*208+row*16+(col&15)]=0x54 if row==11 else 0


def scene(m,x=32,y=176,epoch=0):
    set_native(m,GameEngineSubroutine=8,GamePauseStatus=0,TimerControl=0,AreaType=1,FrameCounter=epoch,
        Player_X_Position=x&255,Player_PageLoc=x>>8,Player_Y_Position=y,Player_Y_HighPos=1,SavedJoypadBits=0)
    floor_domain(m,x)


def projection(m,before_x):
    expect=dict(Player_X_Position=m[0xc071],Player_PageLoc=m[0xc072],Player_Y_Position=m[0xc074],
        Player_Y_HighPos=(m[0xc075]+1)&255,Player_X_Scroll=(m[0xc071]-before_x)&255,
        Player_X_MoveForce=m[0xc070],Player_Y_MoveForce=m[0xc060],Player_Y_Speed=m[0xc061],
        Player_X_Speed=((m[0xc021]<<4)|(m[0xc020]>>4))&255,
        PlayerFacingDir=2 if m[0xc030]&2 else 1,
        Player_State=0 if m[0xc030]&128 else(1 if m[0xc062]&128 else 2))
    assert all(native(m,k)==v for k,v in expect.items()),('Projection',expect,{k:native(m,k)for k in expect})


def constructors(seed,p):
    cases=0;minimum=224
    for x in(0,1,15,31,32,255,256,511,4095,65510):
        for y in(32,96,176,231):
            m=E.S.slim_fork(seed);m.__class__=ServiceBus;m.program=p;m.active=False;m.writes=[];scene(m,x,y)
            for at,value in((0xc047,17),(0xc048,19),(0xc058,23),(0xc0aa,27),(0xc0ab,31),(0xc092,91),(0xc0a0,37),(0xc0a2,41)):
                m[at]=value
            invoke(m,p['symbols']['SonicHostFresh']);c,low=invoke(m,p['symbols']['SonicHostConstruct'])
            minimum=min(minimum,low)
            assert word(m,0xc071)==x and word(m,0xc074)==y+8
            assert bytes(m.ram[2][0x301:0x307])==bytes(m.ram[2][0x70:0x76])
            assert all(m[at]==0 for at in(0xc047,0xc048,0xc058,0xc0aa,0xc0ab,*B.Payload.Frame.MAPPED_ZERO))
            assert(m[0xc092],m[0xc0a0],m[0xc0a2])==(91,37,41)
            assert m[p['fields']['Ready']]==1 and m[p['fields']['HaveEpoch']]==0
            assert all(native(m,k)==v for k,v in dict(Player_X_Position=x&255,Player_PageLoc=x>>8,Player_Y_Position=y,Player_Y_HighPos=1).items())
            cases+=1
    return dict(cases=cases,minimum_SP=minimum,source26byte_constructor_and_pixel_seed=True,
        original_caller_look_jump_bored_reset=True,private_tick_previous_animation_subframe_preserved=True,
        scope='Native adaptation seeds host pixel X and Y+8 after genuine type0 constructor; first source normal-body update subtracts8. No claim of native warm transition admission.')


def episodes(seed,p):
    rows=[];minimum=224;cycles=[];duplicates=0;counts=Counter()
    for rolling in(False,True):
        m=E.S.slim_fork(seed);m.__class__=ServiceBus;m.program=p;m.active=False;m.writes=[];scene(m)
        invoke(m,p['symbols']['SonicHostFresh'])
        ground=0;jumps=0;heights=set()
        for tick in range(260):
            if tick<24:pad=0
            elif tick<80:pad=1
            elif tick<100:pad=5 if rolling else 129
            elif tick<140:pad=129 if rolling else 1
            elif tick<200:pad=1
            else:pad=0
            set_native(m,FrameCounter=tick&255,SavedJoypadBits=pad)
            x=native(m,'Player_X_Position')+256*native(m,'Player_PageLoc');floor_domain(m,x)
            # Reference uses the same frozen frame entry on a cloned actual
            # native bus, without executing any bridge/projection code.
            reference=E.S.slim_fork(m);reference.__class__=ServiceBus;reference.program=p;reference.active=False;reference.writes=[]
            if not reference[p['fields']['Ready']]:invoke(reference,p['symbols']['SonicHostConstruct'])
            reference[0xc0a8]=pad;reference[0xc092]=(reference[0xc092]+1)&255
            expected,low=invoke(reference,p['packet']['frame']['symbols']['SonicNativeOrdinaryFrame'])
            assert expected.p&1,('Reference ordinary frame unavailable',rolling,tick)
            old_headers=O.headers(m);mailbox=bytes(m.ram[2][0x1fd0:0x1fd3]);zp=bytes(m[:256])
            c,low=invoke(m,p['symbols']['SonicServices'])
            assert c.p&1 and m[B.Payload.Frame.STATUS]==0,(rolling,tick,m[B.Payload.Frame.STATUS])
            assert private(m)==private(reference),('Bridge changed genuine frame state/SMC',rolling,tick)
            projection(m,x&255)
            declared={host(m,n)for n in B.HOST}
            assert all(m[a]==zp[a]for a in range(256)if a not in declared),'Host ZP scratch borrowed'
            assert O.headers(m)==old_headers and bytes(m.ram[2][0x1fd0:0x1fd3])==mailbox
            snapshot=private(m),bytes(m.ram[2][B.CONTEXT-0xc000:B.CONTEXT-0xc000+len(B.FIELDS)]),tuple(native(m,n)for n in B.HOST)
            again,_=invoke(m,p['symbols']['SonicServices'])
            assert again.p&1 and snapshot==(private(m),bytes(m.ram[2][B.CONTEXT-0xc000:B.CONTEXT-0xc000+len(B.FIELDS)]),tuple(native(m,n)for n in B.HOST))
            duplicates+=1;minimum=min(minimum,low);cycles.append(c.processorCycles)
            ground+=bool(m[0xc030]&128);jumps+=m[0xc05e]==1;heights.add(m[0xc042]);counts['accepted_original_frames']+=1
        assert ground>40 and jumps>=1 and word(m,0xc071)>300
        if rolling:assert heights=={24,32}
        rows.append(dict(rolling=rolling,frames=260,grounded=ground,jump_events=jumps,heights=sorted(heights),
            final_x=word(m,0xc071),final_y=word(m,0xc074),private_tick=m[0xc092]))
    return dict(episodes=rows,duplicate_calls_unchanged=duplicates,actual_native_epoch_wrap255_to0=True,
        full180_state_fourSMC_matches_frozen_frame=True,cycles=[min(cycles),max(cycles)],minimum_SP=minimum,
        terrain='Explicit native-buffer floor and consistent parser interval fixtures on actual mapped native bus, not a full native stage route')


def epochs(seed,p):
    m=E.S.slim_fork(seed);m.__class__=ServiceBus;m.program=p;m.active=False;m.writes=[];scene(m)
    invoke(m,p['symbols']['SonicHostFresh']);invoke(m,p['symbols']['SonicServices'])
    count=0
    for fields in(dict(GameEngineSubroutine=7),dict(GamePauseStatus=1),dict(TimerControl=255)):
        old=private(m);set_native(m,**fields);invoke(m,p['symbols']['SonicServices'])
        assert private(m)==old and m[p['fields']['HaveEpoch']]==0
        set_native(m,GameEngineSubroutine=8,GamePauseStatus=0,TimerControl=0)
        oldtick=m[0xc092];invoke(m,p['symbols']['SonicServices'])
        assert m[0xc092]==(oldtick+1)&255
        count+=1
    # Same frame byte after an arbitrarily long native nonordinary interval
    # must not suppress the first resumed source update.
    return dict(frozen_or_nonordinary_alias_resume_cases=count)


def corrections_and_failures(seed,p):
    m=E.S.slim_fork(seed);m.__class__=ServiceBus;m.program=p;m.active=False;m.writes=[];scene(m)
    invoke(m,p['symbols']['SonicHostFresh']);invoke(m,p['symbols']['SonicServices'])
    corrections=0
    for x in(31,32,255,256,511,512):
        for y in(96,176):
            q=E.S.slim_fork(m);q.__class__=ServiceBus;q.program=p;q.active=False;q.writes=[]
            set_native(q,FrameCounter=1,Player_X_Position=x&255,Player_PageLoc=x>>8,Player_Y_Position=y,SavedJoypadBits=0)
            floor_domain(q,x)
            r=E.S.slim_fork(q);r.__class__=ServiceBus;r.program=p;r.active=False;r.writes=[]
            if x!=(r[p['fields']['CacheX']]|r[p['fields']['CachePage']]<<8):
                r[0xc070],r[0xc071],r[0xc072]=0,x&255,x>>8
            if y!=r[p['fields']['CacheY']]or r[p['fields']['CacheYHigh']]!=1:
                r[0xc073],r[0xc074],r[0xc075]=0,y,0
            r[0xc0a8]=0;r[0xc092]=(r[0xc092]+1)&255
            expected,_=invoke(r,p['packet']['frame']['symbols']['SonicNativeOrdinaryFrame']);assert expected.p&1
            actual,_=invoke(q,p['symbols']['SonicServices']);assert actual.p&1
            assert private(q)==private(r),('External native relocation',x,y)
            projection(q,x&255);corrections+=1
    failures=0
    for kind in('parser','unsupported','below','foreign_plane','water'):
        q=E.S.slim_fork(m);q.__class__=ServiceBus;q.program=p;q.active=False;q.writes=[]
        set_native(q,FrameCounter=1,SavedJoypadBits=129)
        if kind=='parser':q[p['packet']['frame']['selector']['point']['host']['ColumnSets']]=0
        elif kind=='unsupported':q[0x300+11*16+2]=0x67
        elif kind=='below':set_native(q,Player_Y_Position=240)
        elif kind=='foreign_plane':set_native(q,Player_Y_HighPos=2)
        elif kind=='water':set_native(q,AreaType=0)
        old=private(q);coords=tuple(native(q,n)for n in('Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos'))
        c,_=invoke(q,p['symbols']['SonicServices'])
        assert c.p&1 and q[B.Payload.Frame.STATUS],('Missing explicit unavailability',kind)
        assert private(q)==old,('Unavailable donor-state mutation',kind)
        assert coords==tuple(native(q,n)for n in('Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos'))
        failures+=1
    return dict(external_native_position_resync_cases=corrections,explicit_unavailable_no_actor_position_or_donor_state_write_cases=failures,
        scope='Native external relocation deliberately imports changed integer position and zeros that axis fraction; ordinary uncorrected frames retain full source fractions. Unavailable safehold is not native pit/top/water gameplay policy.')


def powerups(seed,p):
    m=E.S.slim_fork(seed);m.__class__=ServiceBus;m.program=p;m.active=False;m.writes=[];scene(m)
    invoke(m,p['symbols']['SonicHostFresh']);invoke(m,p['symbols']['SonicServices'])
    set_native(m,PlayerStatus=0,GuestLegacyHurt=0)
    counts=Counter();cost=[];minimum=224
    for target in(1,2):
        N.invoke(m,'GuestBeginPowerup')
        assert native(m,'GuestPowerupActive')==1 and native(m,'GuestPowerupAge')==0
        assert native(m,'GameEngineSubroutine')==9 and native(m,'TimerControl')==255
        source=private(m);headers=O.headers(m)
        for update in range(1,61):
            c,low=invoke(m,p['symbols']['SonicServices']+33*3,watch=False)
            minimum=min(minimum,low);cost.append(c.processorCycles)
            assert private(m)==source and O.headers(m)==headers
            assert m[p['fields']['HaveEpoch']]==0
            assert native(m,'GuestPowerupAge')==update
            if update<60:
                assert native(m,'GuestPowerupActive')==1 and native(m,'GameEngineSubroutine')==9 and native(m,'TimerControl')==255
                assert native(m,'PlayerStatus')==target-1
            else:
                assert native(m,'GuestPowerupActive')==0 and native(m,'GameEngineSubroutine')==8 and native(m,'TimerControl')==0
                assert native(m,'PlayerStatus')==target
            counts['actual_native_progression_updates']+=1
        counts['native_begin_to_exact60_finish']+=1
    return dict(counts=dict(counts),cycles=[min(cost),max(cost)],minimum_SP=minimum,
        source_actor_clock_and_header_unchanged_during_freeze=True,
        scope='Actual GuestBeginPowerup and actual GuestPowerupUpdate through dedicated row33/farcall, both temporary native tiers. This does not prove physical earned collection, source shoes/rings, own palette/draw or full gameplay admission.')


def clone(m,c=None):
    q=list.__new__(type(m));list.extend(q,list.__iter__(m))
    for k,v in vars(m).items():
        setattr(q,k,v if k in('bundle','program')else []if k in('writes','ram_writes','ppu_log','blocked')else copy.deepcopy(v))
    q.active=False
    if c is None:return q
    d=copy.copy(c);d.memory=q;return q,d


def cold_and_rows(image,p,packet,program):
    trial=C.Current.W.bundle(image);seeds={}
    for owner in range(37,43):
        m=O.blank(trial);C.cold(m,owner,program['new']);seeds[owner]=(m,m)
    counts,result=E.eighth(trial,program,packet,seeds)
    m=install(trial,p,packet);scene(m)
    for row in p['explicit_unimplemented_rows']:
        before=tuple(bytes(v)for v in m.ram)
        c,_=invoke(m,p['symbols']['SonicServices']+row*3)
        assert not c.p&1 and(c.a,c.x,c.y)==(85,73,109)and tuple(bytes(v)for v in m.ram)==before
    return dict(counts=dict(counts),cold=result,all38_jump_targets_within_dedicated_envelope=True,
        explicit_unimplemented_rows_reject_without_state_write=len(p['explicit_unimplemented_rows']))


def vectors(seed,p):
    import check_ff_head_lifetime_irq_1110 as ISR
    # B is a stack annotation, not a physical6502 status latch. py65 RTI
    # synthesizes it; compare every real status bit across the interrupt.
    with patch.object(ISR,'regs',side_effect=lambda c:(c.pc,c.a,c.x,c.y,c.p&0xef,c.sp)):
        return vector_matrix(seed,p,ISR)


def vector_matrix(seed,p,ISR):
    ISR.PATHS.clear();ISR.DEEPEST=None
    class StackCPU(O.NesMPU):
        lowest=224
        def step(self):
            type(self).lowest=min(type(self).lowest,self.sp)
            assert self.sp>=0x7b,('Native service/vector stack budget',self.sp,hex(self.pc))
            return super().step()
    counts=Counter();minimum=224;private_end=p['code_half_open'][1]
    def live(m,c):
        return(ISR.regs(c),bytes(m[3:11]),bytes(m[0x15a:0x17b]),bytes(m[0x101+c.sp:0x200]),
            tuple(bytes(b)for b in m.ram),tuple(m.rawtags))
    def trace(m,name,pc):
        nonlocal minimum
        m.active=False;set_native(m,DisableScreenFlag=0,NmiDisable=255)
        c=StackCPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=85,73,109,0x21,224;c.stPushWord(STOP-1)
        points=set()
        for _ in range(30000):
            if c.pc==STOP:break
            tag=m.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else None
            used=tag==3 and 0xa000<=c.pc<private_end or 0x15a<=c.pc<0x17b
            key=tag,c.pc,c.sp,c.p&4
            if used and key not in points:
                points.add(key)
                for kind in('NMI','IRQ'):
                    q,d=clone(m,c);before=live(q,d)
                    # Existing real-handler observer checks genuine negative
                    # NMI branch, audio, actual IRQ PPU writes and RTI. Here
                    # rendering is enabled, so the lag handler reaches CLI.
                    with patch.object(ISR,'clone',side_effect=clone):result=ISR.isr(q,d,kind,(STOP,224))
                    after=live(q,d)
                    assert result=='returned'and after[:-1]==before[:-1],(name,kind,hex(c.pc),'Live foreground state')
                    if after[-1]!=before[-1]:
                        ins=bytes(q[d.pc:d.pc+3])
                        assert ins in(bytes.fromhex('8d1551'),bytes.fromhex('8d1651'),bytes.fromhex('8e1651'))
                        window=1 if ins[1]==0x15 else 2
                        assert after[-1][window]==q[0x145 if window==1 else O.CURRENT]
                        assert all(a==b for j,(a,b)in enumerate(zip(before[-1],after[-1]))if j!=window)
                        # The actual pending mapper-store opcode repairs
                        # this legal shadow/register interruption window.
                        ref,r=clone(m,c);d.step();r.step()
                        assert live(q,d)==live(ref,r),('Pending mapper write did not converge',name,kind,hex(c.pc))
                    minimum=min(minimum,d.sp);counts[name,kind]+=1
            assert m[c.pc],('Vector foreground BRK',name,hex(c.pc));c.step()
        else:raise AssertionError(('Vector foreground bound',name,hex(c.pc)))
        assert c.sp==224
        print('Sonic active service vector cuts',name,len(points),flush=True)
    first=clone(seed);scene(first);invoke(first,p['symbols']['SonicHostFresh']);trace(first,'fresh',p['symbols']['SonicServices'])
    for kind,pad in(('jump',129),('roll',5)):
        m=clone(seed);scene(m);invoke(m,p['symbols']['SonicHostFresh'])
        for tick in range(80):
            x=native(m,'Player_X_Position')+256*native(m,'Player_PageLoc');floor_domain(m,x)
            set_native(m,FrameCounter=tick,SavedJoypadBits=1);invoke(m,p['symbols']['SonicServices'])
        floor_domain(m,native(m,'Player_X_Position')+256*native(m,'Player_PageLoc'))
        set_native(m,FrameCounter=80,SavedJoypadBits=pad);trace(m,kind,p['symbols']['SonicServices'])
    m=clone(first);set_native(m,PlayerStatus=0,GuestLegacyHurt=0);N.invoke(m,'GuestBeginPowerup')
    trace(m,'powerup33',p['symbols']['SonicServices']+33*3)
    assert ISR.DEEPEST is not None
    state,cpu,outer,stop=ISR.DEEPEST
    m,c=clone(state,cpu);before=live(m,c)
    assert not c.p&4 and ISR.isr(m,c,'IRQ')=='returned'and live(m,c)==before
    minimum=min(minimum,c.sp)
    # Resume the real lag suffix after its nested scanline IRQ and verify
    # the original foreground entry/stack/private state, then finish frame.
    ref,r=clone(state,cpu)
    ISR.finish(m,c,(outer[0],outer[5]));ISR.finish(ref,r,(outer[0],outer[5]))
    assert live(m,c)==live(ref,r)
    ISR.finish(m,c,stop);ISR.finish(ref,r,stop);assert live(m,c)==live(ref,r)
    return dict(actual_cuts={f'{name}/{kind}':v for(name,kind),v in sorted(counts.items())},
        actual_handler_paths=dict(ISR.PATHS),nested_IRQ_in_actual_render_enabled_CLI_lag_NMI=True,
        deepest_nested_parent_SP=cpu.sp,minimum_foreground_return_SP=minimum,minimum_actual_foreground_ISR_nested_SP=StackCPU.lowest,
        scope='Fresh/walking-jump/rolling and row33 on actual mapped native bus. One reached privatePC/SP/I or realSMC-transport cut per scenario; genuine lag NMI with screen enabled and actual unmasked scanlineIRQ. Full registers/live stack/R0..7/SMC/all privateRAM/maps restored; deepest reached realCLI lag handler receives nestedIRQ and full suffix/foreground resumes. No full native stage or published regular-NMI/render claim.')


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--vectors',action='store_true');args=ap.parse_args()
    assert args.output.resolve().is_relative_to(R/'build')and not args.output.exists()
    # Downloads may advance independently. Preserve this component's a5 pin
    # by exact source reconstruction from retained c10, never silently repin.
    current=E.FF.proposal(C.ROM.read_bytes())[0];assert E.digest(current)==E.PIN
    bundle=C.Current.W.bundle(current);p=B.build(bundle);packet=B.packet_with_services(p)
    with patch.object(E.Payload,'build',return_value=packet):image,program,_,_,_=E.proposal(C.ROM.read_bytes(),current)
    seed=install(C.Current.W.bundle(image),p,packet)
    if args.vectors:
        result=dict(passed=True,source_only=True,outputs_written=0,ROM_written=False,source_SHA256=sha256(Path(__file__).read_bytes()).hexdigest(),
            current_parent_SHA256=E.PIN,in_memory_SHA256=E.digest(image),vectors=vectors(seed,p))
        print(json.dumps(result,sort_keys=True),flush=True);assert not args.output.exists();return
    result=dict(passed=True,source_only=True,outputs_written=0,ROM_written=False,
        current_parent_SHA256=E.PIN,in_memory_SHA256=E.digest(image),source_SHA256=sha256(Path(__file__).read_bytes()).hexdigest(),
        service_bytes=len(p['image']),service_SHA256=p['image_SHA256'],code=p['code_half_open'],context=p['context_half_open'],
        remaining_before_header=p['remaining_before_header'],constructor=constructors(seed,p),epochs=epochs(seed,p),
        correction_failure=corrections_and_failures(seed,p),powerups=powerups(seed,p),cold=cold_and_rows(image,p,packet,program),
        ordinary_native_bus=episodes(seed,p),unimplemented_rows=p['explicit_unimplemented_rows'],
        no_public_raw43_admission=True,no_native_stage_or_Mesen_or_runtime_RAM_lease=True)
    print(json.dumps(result,sort_keys=True),flush=True);assert not args.output.exists()


if __name__=='__main__':main()
