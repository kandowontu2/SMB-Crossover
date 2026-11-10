"""Narrow actual-bus tests of Sonic metadata world/effect/render changes."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import check_sonic_native_host_services_1110 as S
import sonic_sms_native_effects_1110 as B

E,C,O,N=S.E,S.C,S.O,S.N
R=E.R


class EffectsBus(S.ServiceBus):
    effect=None
    def __getitem__(self,at):
        if self.active and isinstance(at,int)and 0xc800<=at<0xd900:
            lo,hi=self.effect['metadata_half_open']
            assert lo<=at<hi,('Retired source world read',hex(at))
        return O.ControllerBus.__getitem__(self,at)
    def __setitem__(self,at,value):
        if self.active and isinstance(at,int):
            e=self.effect
            native=self.allowed_native
            own=0xc000<=at<B.CONTEXT+len(B.FIELDS)or 0xc200<=at<0xc2b8 or 0xc300<=at<0xc31a
            bounds=self.bounds_base
            assert own or at in native or 0x17b<=at<=0x1e0 or 0x200<=at<0x300 or bounds<=at<bounds+4 or at in self.program['packet']['core']['SMC_operands'],('Unowned metadata write',hex(at))
            self.writes.append((at,value&255))
        O.ControllerBus.__setitem__(self,at,value)


def clone(seed,p):
    m=S.clone(seed);m.__class__=EffectsBus;m.effect=p;m.active=False;m.program=p['service'];return m


def install(bundle,p,program):
    m=O.blank(bundle);C.cold(m,43,program['new']);E.owned(m,p['packet'])
    m.raw_page(1,3);m.raw_page(2,2);N.put(m,CurrentBank=3,CurrentBankC=2)
    m.__class__=EffectsBus;m.effect=p;m.program=p['service'];m.active=False;m.writes=[]
    names=(*B.Host.HOST,'R2','R3','R4','R5','R6','R7','PlayerSize','Player_Rel_XPos','Player_Rel_YPos',
        'CurrentOAMOffset','ObjectMetasprite','X5ChrMode','CurrentCHRBank','X5WideChrActive','ReloadCHRBank','GuestBodyNoStomp','Player_Pos_ForScroll')
    m.allowed_native={S.host(m,n)for n in names};m.bounds_base=S.host(m,'BoundingBox_UL_Corner')
    return m


def invoke(m,pc,*,y=109,watch=True):
    c=O.NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=85,73,y,0x31,224;c.stPushWord(S.STOP-1)
    m.active=watch;m.writes=[];low=c.sp
    try:
        for _ in range(22000):
            if c.pc==S.STOP:break
            assert m[c.pc],('Metadata BRK',hex(c.pc),m.rawtags)
            low=min(low,c.sp);c.step()
        else:raise AssertionError(('Metadata bound',hex(c.pc)))
    finally:m.active=False
    assert c.sp==224
    return c,low


def pointer(x,y):return 0x300+(x//256&1)*208+((y-32)//16)*16+(x//16&15)


def projection(m,oldx):
    y=(S.word(m,0xc074)+m[0xc042]-32)&65535
    expected=dict(Player_X_Position=m[0xc071],Player_PageLoc=m[0xc072],Player_Y_Position=y&255,
        Player_Y_HighPos=((y>>8)+1)&255,Player_X_Scroll=(m[0xc071]-oldx)&255,
        Player_Y_Speed=255 if m[m.effect['context']['HeadPending']]else m[0xc061])
    assert all(S.native(m,k)==v for k,v in expected.items()),('Effect projection',expected,{k:S.native(m,k)for k in expected})


def episodes(seed,p):
    cases=[];minimum=224;cycles=[]
    for rolling in(False,True):
        m=clone(seed,p);S.scene(m);invoke(m,p['service']['symbols']['SonicHostFresh'])
        heights=set()
        for tick in range(200):
            pad=0 if tick<24 else 1 if tick<80 else(5 if rolling else 129)if tick<100 else(129 if rolling else 1)if tick<140 else 1
            S.set_native(m,FrameCounter=tick,SavedJoypadBits=pad)
            oldx=S.native(m,'Player_X_Position')+256*S.native(m,'Player_PageLoc');S.floor_domain(m,oldx)
            ref=clone(m,p)
            if not ref[p['service']['fields']['Ready']]:invoke(ref,p['service']['symbols']['SonicHostConstruct'])
            # Restore only the frozen selector/frame bodies in the control;
            # it executes the original qualified world-independent frame.
            f=p['service']['packet']['frame'];q=f['selector']
            for block in(f,q):
                lo,hi=block['code_half_open'];ref.ram[3][lo-0xa000:hi-0xa000]=block['image']
            ref[0xc0a8]=pad;ref[0xc092]=(ref[0xc092]+1)&255
            wanted,_=invoke(ref,f['symbols']['SonicNativeOrdinaryFrame']);assert wanted.p&1
            c,low=invoke(m,p['service']['symbols']['SonicServices']);assert c.p&1 and not m[B.Host.Payload.Frame.STATUS]
            assert S.private(m)==S.private(ref),('World derivative changed in-plane original motor/contacts',rolling,tick)
            projection(m,oldx&255);minimum=min(minimum,low);cycles.append(c.processorCycles)
            heights.add(m[0xc042])
        if rolling:assert heights=={24,32}
        cases.append(dict(rolling=rolling,frames=200,source_x=S.word(m,0xc071),source_y=S.word(m,0xc074),
            native_y=S.native(m,'Player_Y_Position'),height=m[0xc042],heights_seen=sorted(heights)))
    return dict(episodes=cases,full180_state_and4SMC_equal_frozen_frame=True,cycles=[min(cycles),max(cycles)],minimum_SP=minimum)


def getters(seed,p):
    counts=Counter();meta=p['metadata']['symbols']
    for kind,row,dy in(('head',10,4),('side',14,8),('feet',35,32)):
        for grounded in(False,True):
            for tile in(0,0x54,0x10,0x11,0x23,0xc2,0xc3,0x24,0x25,0x6c,0x1f):
                m=clone(seed,p);S.scene(m);m[0xc030]=128 if grounded else 0
                S.set_native(m,PlayerSize=0)
                # Big native head0/side3/feet0->1 each addresses worldcol2.
                m[pointer(40,176+dy)]=tile
                c,_=invoke(m,p['service']['symbols']['SonicServices']+3*row,y=3 if kind=='side'else 0)
                allowed=tile in(0x23,0xc2,0xc3)or kind=='side'and tile in(0x24,0x25,0x6c,0x1f)or kind=='feet'and grounded
                expected=tile if allowed else 0
                assert c.a==expected and bool(c.p&2)==(expected==0),(kind,grounded,tile,c.a,c.p)
                assert c.x==0
                counts[kind]+=1
    # The cached actual source ceiling contact supplies the native block
    # column/row and a confirmed-contact phase, without moving the actor.
    for page in(0,1):
        m=clone(seed,p);S.scene(m,32+page*256);ctx=p['context']
        for name,value in dict(HeadPending=1,HeadTile=0x61,HeadRow=128,HeadPhase=15,HeadColumn=2,HeadPage=page).items():m[ctx[name]]=value
        c,_=invoke(m,meta['MetaHead'],y=7)
        assert(c.a,c.x,c.y)==(0x61,0,7)and not c.p&2
        assert S.native(m,'R2')==128 and S.native(m,'R4')==15
        assert S.native(m,'R6')==(2 if page==0 else 210)and S.native(m,'R7')==3
        assert m[ctx['HeadPending']]==0
        counts['cached_genuine_ceiling_ABI']+=1
    return dict(counts)


def bounds_and_head_contact(seed,p):
    counts=Counter()
    for height in(24,32):
        m=clone(seed,p);S.scene(m);m[0xc042]=height;m[0xc074]=208-height
        S.set_native(m,Player_Rel_XPos=80,GuestBodyNoStomp=255)
        c,_=invoke(m,p['metadata']['symbols']['MetaBounds'])
        a=S.host(m,'BoundingBox_UL_Corner')
        assert tuple(m[a:a+4])==(80,208-height,103,207)and c.p&1
        c,_=invoke(m,p['metadata']['symbols']['MetaBody'])
        assert not c.p&1 and S.native(m,'GuestBodyNoStomp')==0
        counts['source24px_bounds_and_native_stomp_policy']+=1
    m=clone(seed,p);S.scene(m,64,176);invoke(m,p['service']['symbols']['SonicHostFresh'])
    invoke(m,p['service']['symbols']['SonicServices'])
    S.set_native(m,FrameCounter=1,SavedJoypadBits=0)
    invoke(m,p['service']['symbols']['SonicServices'])
    m[pointer(76,160)]=0x61
    S.set_native(m,FrameCounter=2,SavedJoypadBits=129)
    c,_=invoke(m,p['service']['symbols']['SonicServices'])
    assert c.p&1 and m[p['context']['HeadPending']]==1 and S.native(m,'Player_Y_Speed')==255
    actor=S.private(m);native_y=S.native(m,'Player_Y_Position')
    c,_=invoke(m,p['metadata']['symbols']['MetaHead'],y=0)
    assert c.a==0x61 and not c.p&2
    N.invoke(m,'PlayerHeadCollision')
    assert S.private(m)==actor and S.native(m,'Player_Y_Position')==native_y
    counts['actual_source_ceiling_to_native_PlayerHeadCollision']+=1
    return dict(counts)


def world_edges(seed,p):
    m=clone(seed,p);S.scene(m,64,176);invoke(m,p['service']['symbols']['SonicHostFresh'])
    S.set_native(m,NumberofLives=2)
    # Native buffer is genuinely empty throughout the committed interval.
    for at in range(0x300,0x4a0):m[at]=0
    high=set();points=[]
    for tick in range(200):
        S.set_native(m,FrameCounter=tick,SavedJoypadBits=0)
        c,_=invoke(m,p['service']['symbols']['SonicServices']);assert c.p&1 and not m[B.Host.Payload.Frame.STATUS]
        projection(m,64);high.add(S.native(m,'Player_Y_HighPos'))
        if S.native(m,'Player_Y_HighPos')>=6:
            points.append(dict(frame=tick,source_y=S.word(m,0xc074),native_high=S.native(m,'Player_Y_HighPos')));break
    assert points and len(high)>3,('Pit held at viewport boundary',high,S.word(m,0xc074))
    # Actual native pit threshold is reached; its real suffix owns death.
    S.set_native(m,DeathMusicLoaded=0,GameTimerExpiredFlag=0,CloudTypeOverride=0,EventMusicBuffer=0,EventMusicQueue=0)
    N.invoke(m,'PlayerHole')
    assert S.native(m,'DeathMusicLoaded')==1 and S.native(m,'ScrollLock')==1
    death_frame=None
    death_updates=0
    for tick in range(155,555):
        # Native GameLoop advances its clock in death as well as gameplay.
        S.set_native(m,FrameCounter=tick&255,SavedJoypadBits=0)
        # AudioUpdate is NMI-owned; use its actual full interrupt so C-window
        # restoration and publication match the real host lifetime.
        E.Alias.regular_nmi(m)
        if tick==155:
            assert S.native(m,'EventMusicQueue')==0,('Native death audio queue not consumed',S.native(m,'EventMusicQueue'),S.native(m,'EventMusicBuffer'))
        if S.native(m,'GameEngineSubroutine')==6:death_frame=tick;break
        engine=S.native(m,'GameEngineSubroutine')
        if engine==11:
            # The real PlayerDeath router will select this own row after
            # public admission. Do not repeat PlayerHole and requeue music.
            invoke(m,p['service']['symbols']['SonicServices']+3*8,watch=False)
            death_updates+=1
        elif engine==8:
            invoke(m,p['service']['symbols']['SonicServices'])
            N.invoke(m,'PlayerHole')
        else:raise AssertionError(('Unexpected native death engine',engine))
    assert death_frame is not None and death_updates==150,(death_frame,death_updates)
    music_end=S.native(m,'EventMusicBuffer')
    N.invoke(m,'PlayerLoseLife')
    assert S.native(m,'NumberofLives')==1
    return dict(pit_crossed_native_high_planes=sorted(high),native_pit_death_threshold=points,
        actual_native_PlayerHole_sets_death_music_and_scroll_lock=True,
        actual_native_death_update_completion_frame=death_frame,actual_native_pit_death_updates=death_updates,
        death_music_queue_consumed=True,death_music_buffer_at_end=music_end,actual_PlayerLoseLife_decrements2_to1=True,
        limitation='Typed source spawn/empty-room inputs and direct real native suffix/audio/life calls; actual full stage and respawn driver remain required. No music state is cleared after death begins.')


def render(seed,p):
    counts=Counter()
    for facing in(1,2):
        for rotation in(0,16,224):
            m=clone(seed,p);S.scene(m)
            S.set_native(m,PlayerFacingDir=facing,Player_Rel_XPos=80,Player_Rel_YPos=176,Player_SprAttrib=32,
                CurrentOAMOffset=0,GuestOamRotationActive=int(bool(rotation)),RgOamRotation=rotation)
            invoke(m,p['metadata']['symbols']['MetaGraphics'])
            assert S.native(m,'X5ChrMode')==0x85 and S.native(m,'CurrentCHRBank')==16
            assert S.native(m,'Player_Pos_ForScroll')==80
            invoke(m,p['metadata']['symbols']['MetaDraw'])
            assert S.native(m,'CurrentOAMOffset')==16
            for i,tile in enumerate((0,2,32,34)if facing==1 else(2,0,34,32)):
                at=0x200+((rotation+4*i)&255)
                assert tuple(m[at:at+4])==(176+(16 if i>=2 else 0),tile,32|(64 if facing==2 else 0),84+(8 if i&1 else 0))
            counts['direct_owned_OAM_no_pointer_export']+=1
            private=tuple(bytes(b)for b in m.ram)
            E.Alias.regular_nmi(m)
            assert m.chr_latches[0]==224,('Native prototype art publication',m.chr_latches,S.native(m,'X5ChrMode'))
            assert tuple(bytes(b)for b in m.ram)==private
            counts['actual_regular_NMI_page224_publication_private_unchanged']+=1
    return dict(counts,limitations='Temporary genuine-SMS16px standing canvas, fixed pose and incumbent palette; original24px full source animation/audio remain unfinished.')


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    assert args.output.resolve().is_relative_to(R/'build')and not args.output.exists()
    old=C.ROM.read_bytes();current=E.FF.proposal(old)[0];bundle=C.Current.W.bundle(current);p=B.build(bundle)
    with patch.object(E.Payload,'build',return_value=p['packet']):image,program,_,_,_=E.proposal(old,current)
    seed=install(C.Current.W.bundle(image),p,program)
    result=dict(passed=True,source_only=True,outputs_written=0,ROM_written=False,parent_SHA256=E.PIN,
        in_memory_SHA256=E.digest(image),source_SHA256=sha256(Path(__file__).read_bytes()).hexdigest(),
        metadata_code=p['metadata_half_open'],remaining_metadata=p['remaining_metadata_bytes'],private_code=p['service']['code_half_open'],remaining_private=p['remaining_private_bytes'],
        ordinary=episodes(seed,p),native_getters=getters(seed,p),bounds_head=bounds_and_head_contact(seed,p),world_edges=world_edges(seed,p),render=render(seed,p),
        no_public_raw43_admission=True,qualified_dispatch_and_full_native_stage_pending=True)
    print(json.dumps(result,sort_keys=True),flush=True);assert not args.output.exists()


if __name__=='__main__':main()
