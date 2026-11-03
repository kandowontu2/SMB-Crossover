"""Measure shoe-powered, source-controlled bubble alignment through actual Main."""
import hashlib,json
from pathlib import Path
import profile_bub_current_bridge_1103_v69 as C
from prepare_selected_native_packet_v1 import R,sha

O=R/'build/bub-powered-trajectory-1103-v92'
ROM=R/'build/combined-owner-auth-root-1103-v116/combined-auth-private.nes'
PIN='80d3ae95894f5ddb430c3e753dd95f3fc2eca6a87d8e1afdb4b8ce8376ec795a'
N,Q,address=C.N,C.Q,C.address


def earn_shoes(b,route,identity):
    m=Q.Q.fresh(b,route,identity);Q.L.E.main_fields(m)
    actor=0x42 if identity else 0x2e
    N.put(m,NmiDisable=255,TimerControl=0,Player_Rel_XPos=64,Player_Rel_YPos=176)
    N.invoke(m,'HuFullBox',a=83,x=0,y=0,p=0x21)
    N.put(m,ObjectOffset=5)
    for field,value in dict(Enemy_Flag=1,Enemy_ID=46,Enemy_State=128,PowerUpType=0,
        Enemy_X_Position=64,Enemy_PageLoc=0,Enemy_Y_Position=191,Enemy_Y_HighPos=1,
        Enemy_BoundBoxCtrl=9,Enemy_MovingDir=1).items():m[address(b,field)+5]=value
    N.invoke(m,'PowerUpObjHandler',a=83,x=5,y=0,p=0x21)
    assert m.ram[2][actor+2]==1 and N.get(m,'GuestPowerupActive')==1
    for _ in range(60):
        N.put(m,VRAM_Buffer1_Offset=0)
        N.invoke(m,'PlayerChangeSize',a=83,x=0,y=0,p=0x21)
    assert N.get(m,'GameEngineSubroutine')==8 and N.get(m,'PlayerStatus')==1
    assert N.get(m,'GuestPowerupActive')==0 and m.ram[2][actor+2]==1
    return m


def sample(m,identity):
    actor=0x42 if identity else 0x2e;oy=8 if identity else 0;s=m.ram[2]
    bubbles=[dict(slot=i,kind=s[0x88+4*i],x=s[0x18b+8*i],y=s[0x188+8*i],
        gap=s[0x18b+8*i]-s[0x103+oy],dy=s[0x188+8*i]-s[0x100+oy])
        for i in range(15)if s[0x88+4*i]in[1,2]]
    return dict(x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),
        y=N.get(m,'Player_Y_Position'),sx=s[0x103+oy],sy=s[0x100+oy],selector=s[actor+3],
        timer=s[actor+4],latch=s[actor+5],support=s[actor+9],clock=s[0x1f],
        native_state=N.get(m,'Player_State'),bubbles=bubbles)


def main():
    O.mkdir(exist_ok=True);assert sha(ROM)==PIN
    b,route,q,_,_,_=C.bundle();b=dict(b,raw=ROM.read_bytes())
    rows=[];native=N.NesMPU
    for identity in[0,1]:
        m=earn_shoes(b,route,identity);actor=0x42 if identity else 0x2e
        phase='grow';chosen=None;events=[];trace=[];epoch=-1
        class Trace(native):
            def step(self):
                if self.pc==q['labels']['BbOriginal_D36B']and self.memory.rawtags[1]==3:
                    events.append(dict(update=epoch,held=self.memory.ram[2][actor+1],**sample(self.memory,identity)))
                return native.step(self)
        N.NesMPU=Trace
        try:
            for epoch in range(180):
                s=sample(m,identity);active=s['bubbles'];bubble=None
                if chosen is not None:bubble=next((v for v in active if v['slot']==chosen),None)
                if bubble is None and active:
                    bubble=active[0];chosen=bubble['slot']
                if epoch<4:keys=65
                elif phase=='grow':
                    keys=1 if bubble and bubble['gap']>20 else 0
                    if bubble and bubble['kind']==2 and 10<=bubble['gap']<=28:
                        phase='align';keys=128
                elif phase=='align':
                    if s['support']&127 and s['selector']in[2,3]:phase='forward';keys=129
                    elif bubble and bubble['dy']>=10:keys=128|(1 if bubble['gap']>4 else 2 if bubble['gap']<0 else 0)
                    else:keys=128
                else:keys=129
                N.put(m,FrameCounter=epoch,SavedJoypadBits=keys,SavedJoypad1Bits=keys,VRAM_Buffer1_Offset=0)
                N.invoke(m,'GameCoreRoutine',x=0,y=0)
                after=sample(m,identity);trace.append(dict(update=epoch,phase=phase,keys=keys,**after))
                assert m.ram[2][actor+2]==1 and N.get(m,'NumberofLives')==2
        finally:N.NesMPU=native
        row=dict(identity=identity,events=events,minimum_native_y=min(v['y']for v in trace),
            maximum_world_x=max(v['x']for v in trace),trace=trace)
        rows.append(row)
        print(json.dumps(dict(identity=identity,events=events,minimum_native_y=row['minimum_native_y'],
            samples=[v for v in trace if v['update']%10==0])),flush=True)
    passed=all(any(e['support']&127 for e in row['events'])for row in rows)
    result=dict(passed=passed,CPU_only=True,ROM_written=False,ROM_SHA256=PIN,cases=rows,
        scope='Legitimate explicitly placed native mushroom collected through PowerUpObjHandler and complete60-update transformation. Empty legal flat native floor; subsequent state is changed only by ordinary controller input through complete GameCore. This measures source support timing, not natural earned flower or terrain traversal.',
        bindings={str(p.relative_to(R)):sha(p)for p in[Path(__file__),ROM,R/'build/bub-upgrades-root-1102-v47/component.s']})
    (O/'powered-bubble-CPU.json').write_text(json.dumps(result,indent=2)+'\n')
    assert passed,'Adaptive source support not yet earned'


if __name__=='__main__':main()
