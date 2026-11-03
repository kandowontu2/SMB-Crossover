"""Additional actual plain-brick post-head audio minima; no question-block rerun.

Both source actors use the same declared small or genuinely collected mushroom
state. Persist only compact cut/profile aggregates, never memory fixtures.
"""
import argparse,json
from pathlib import Path
import check_bub_head_nested_phases_1102_v64 as P
import resume_bub_head_nested_1102_v65 as T
H,K,N,O,R,sha=P.H,P.K,P.N,P.O,P.R,P.sha


def seed(b,route,identity,powered):
    m,cell=H.P.H.H.H.arena(b,route,identity)
    actor=0x42 if identity else 0x2e
    assert m[H.address(b,'MTileAttribute')+0x51]&7==1
    m[cell]=0x51
    lifecycle=[]
    if powered:
        # A legal placed mushroom is collected by the actual owner24/native
        # collector. Its original item4/01 adaptation is not a seeded flag.
        N.put(m,TimerControl=0,Player_Rel_XPos=73,Player_Rel_YPos=176,ObjectOffset=5)
        N.invoke(m,'HuFullBox',a=83,x=0,y=0,p=0x21)
        for field,value in dict(Enemy_Flag=1,Enemy_ID=46,Enemy_State=128,PowerUpType=0,
            Enemy_X_Position=73,Enemy_PageLoc=1,Enemy_Y_Position=191,Enemy_Y_HighPos=1,
            Enemy_BoundBoxCtrl=9,Enemy_MovingDir=1).items():m[H.address(b,field)+5]=value
        N.invoke(m,'PowerUpObjHandler',a=83,x=5,y=0,p=0x21)
        assert m.ram[2][actor+2]==1 and N.get(m,'GuestPowerupActive')==1
        frozen=bytes(m.ram[2][:0x300])
        for _ in range(60):
            N.put(m,VRAM_Buffer1_Offset=0);N.invoke(m,'PlayerChangeSize',a=83,x=0,y=0,p=0x21)
            assert bytes(m.ram[2][:0x300])==frozen
        assert N.get(m,'GuestPowerupActive')==0 and N.get(m,'GameEngineSubroutine')==8
        assert N.get(m,'PlayerStatus')==1 and N.get(m,'PlayerSize')==0
        # Drain the actual native pickup sound via genuine FF NMI. This makes
        # the later plain-brick SFX independent of the previous mushroom SFX.
        for epoch in range(120):
            c=N.NesMPU(memory=m,pc=0x5b00);c.sp=224;c.p=0x21;c.nmi()
            for _ in range(30000):
                if(c.pc,c.sp)==(0x5b00,224):break
                assert m[c.pc]!=0;c.step()
            else:raise AssertionError('Setup native audio drain bound')
            if H.audio(m)==(0,0,0)and not any(P.sounds(m).values()):break
        else:raise AssertionError(('Pickup sound did not drain',H.audio(m),P.sounds(m)))
        lifecycle.append(dict(real_mushroom_collector=True,original_flags=m.ram[2][actor+2],
            native_size=N.get(m,'PlayerSize'),native_status=N.get(m,'PlayerStatus'),
            actual_transform_updates=60,actual_FF_audio_drain=epoch+1))
    # Source speed shoes may change the source update path/cadence. Locate
    # the actual first brick transaction, rather than assuming the small
    # question fixture's epoch16 is also a powered head-entry epoch.
    for epoch in range(40):
        N.put(m,FrameCounter=epoch,SavedJoypadBits=128 if epoch else 0,
            SavedJoypad1Bits=128 if epoch else 0,VRAM_Buffer1_Offset=0)
        before=N.fork(m)
        N.invoke(m,'GameCoreRoutine',x=0,y=0)
        if m[cell]!=0x51:
            m=before;break
    else:raise AssertionError(('No actual brick contact',identity,powered,N.get(m,'Player_Y_Position')))
    lifecycle.append(dict(actual_first_head_epoch=epoch))
    N.put(m,NmiDisable=255)
    assert N.get(m,'PlayerSize')==(0 if powered else 1)
    assert N.get(m,'PlayerStatus')==(1 if powered else 0)
    before=T.critical(m);m.writes=[];m.ram_writes=[];m.ppu_log=[];assert T.critical(m)==before
    return m,cell,lifecycle


def bindings():
    files=[Path(__file__),Path(P.__file__),Path(T.__file__),Path(K.__file__),
        O/'head-projection-v64-nested.json',O/'head-projection-v55.json',
        O/'head-projection-v55-image.bin',R/'src/bill_native_rare.s',
        R/'src/music_drivers/vanilla_sfx.s']
    return {str(f.relative_to(R)):sha(f)for f in files}


def measure():
    destination=O/'head-projection-v66-brick-profiles.json';assert not destination.exists()
    b,route,q,p,run=P.inputs();actual=N.NesMPU;rows=[]
    for powered in[False,True]:
        for identity in[0,1]:
            m,cell,life=seed(b,route,identity,powered);groups={};head_return=None;post=False;steps=0;head_calls=0
            head=H.address(b,'PlayerHeadCollision');fragment_writes=[]
            class Trace(actual):
                def step(self):
                    nonlocal head_return,post,steps,head_calls
                    if self.pc==head and self.memory.rawtags[3]==255:
                        head_calls+=1;sp=self.sp
                        head_return=(self.memory[0x100+sp+1]+256*self.memory[0x100+sp+2]+1,sp+2)
                    if head_return==(self.pc,self.sp):post=True
                    if post:
                        steps+=1;mm=self.memory;live=P.sounds(mm)
                        # Audio state is frozen between this ordinary block
                        # transaction and return. Distinct exact queue/buffer/
                        # clock profiles and foreground maps each retain their
                        # own deepest context; do not pick an empty-audio cut.
                        key=(mm.rawtags[1],mm.rawtags[2],tuple(live.items()))
                        cut=(self.pc,self.sp,mm.rawtags[1],mm.rawtags[2],int(bool(self.p&4)))
                        if key not in groups or self.sp<groups[key][0][1]:groups[key]=(cut,live)
                    return super().step()
            N.NesMPU=Trace
            try:out=run(m,p,q)
            finally:N.NesMPU=actual
            assert head_calls==1 and steps>0 and N.get(m,'Enemy_ID',5)!=46
            assert N.get(m,'NumberofLives')==2 and m.ram[2][0x3ef]==0
            assert m[cell]==0x23
            fields=['Block_State','Block_Metatile','Block_X_Position','Block_PageLoc',
                'Block_Y_Position','Block_Y_Speed','Block_X_Speed']
            blocks={n:[N.get(m,n,i)for i in range(2)]for n in fields}
            rows.append(dict(identity=identity,powered=powered,head_calls=head_calls,
                post_head_instructions=steps,foreground_minimum_SP=out['minimum_SP'],
                minima=[dict(foreground_cut=cut,live_sound=live)for cut,live in groups.values()],
                lifecycle=life,cell=m[cell],blocks=blocks,source_flags=m.ram[2][(0x42 if identity else 0x2e)+2],
                source_SHA256=__import__('hashlib').sha256(bytes(m.ram[2][:0x300])).hexdigest(),
                complete_private_SHA256=__import__('hashlib').sha256(bytes(m.ram[2][:1024])).hexdigest(),
                native=[N.get(m,n)for n in['Player_X_Position','Player_PageLoc','Player_Y_Position',
                    'Player_Y_HighPos','Player_State','Player_Y_Speed','PlayerSize','PlayerStatus','NumberofLives']]))
            print('Brick actual profiles',identity,powered,'poststeps',steps,'minima',len(groups),
                'wholemin',out['minimum_SP'],'blocks',blocks,'audio',P.sounds(m),flush=True)
    result=dict(passed=True,CPU_only=True,ROM_written=False,memory_ROM_SHA256=p['memory_ROM_SHA256'],
        nested_qualified=False,scenarios=rows,scope='Actual plain51 brick only: small/bump and real mushroom/60-update-powered shatter, both source actors. Every actual post-head instruction contributes to the deepest SP per exact native sound queue/buffer/clock profile and A/C maps. Additional FF/nested replay remains separate; existing Q cohort not repeated.',bindings=bindings())
    destination.write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--phase',choices=['measure'],required=True)
    args=parser.parse_args();measure()
