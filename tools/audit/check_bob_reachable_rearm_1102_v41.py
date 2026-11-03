"""Actualcamera591 source-leftwall stop, fresh facing and earned64pxpipe ride."""
import json
from pathlib import Path
import measure_bub_landing_1102_v21 as L

N,Q,P,R,address=L.N,L.Q,L.P,L.R,L.address;O=L.O
PIN='9cf99b438e6f5bc614dc4ccc433707a3796702b7f33a04318a428a1155397f15'


def main():
    _,b,layout,route=L.bundle();rom=O/'combined-current-landing.nes';b['raw']=rom.read_bytes();assert P.sha(b['raw'])==PIN
    evidence=O/'native-current-landing-bob-full11-castle-stairs/capture/full11.json';actual=json.loads(evidence.read_text())
    assert actual['why']=='Bounded source shot rearm'and actual['current_x']==647 and actual['initial_lives']==actual['final_lives']==2
    assert all(v['x']==647 and v['support_probe']['camera']==591 for v in actual['source_shot_rearm'][-6:])
    core=P.P.labels(L.B/'component.lbl');native=N.NesMPU;cases=[]
    for clock,mode in[(c,f)for c in[147,148]for f in['face1','face2','direct-RightB']]:
        face_updates=2 if mode=='face2'else 1
        m=Q.fresh(b,route,1);L.E.main_fields(m);actor=0x42;oy=8;camera=591
        N.put(m,Player_X_Position=670&255,Player_PageLoc=670>>8,Player_Y_Position=176,
            ScreenLeft_X_Pos=camera&255,ScreenLeft_PageLoc=camera>>8,
            ScreenRight_X_Pos=846&255,ScreenRight_PageLoc=846>>8,Player_Pos_ForScroll=79,
            PlayerSize=1,PlayerStatus=1,Player_State=0,Player_Y_Speed=0)
        for left,right,top in[(608,640,160),(736,768,144)]:
            for wx in range(left,right,16):
                name='Block_Buffer_2'if(wx//256)&1 else'Block_Buffer_1'
                for wy in range(top,208,16):m[address(b,name)+((wy-32)//16)*16+(wx%256)//16]=84
        def solid(wx,wy):
            if not 32<=wy<240:return False
            name='Block_Buffer_2'if(wx//256)&1 else'Block_Buffer_1'
            return bool(m[address(b,name)+((wy-32)//16)*16+(wx%256)//16])
        m.ram[2][actor+8]=17;m.ram[2][0x1f]=clock
        phase='rewind';steps=0;epoch=-1;candidate=None;candidate_clock=None;confirmed=None;launch=None;events=[];minimum=176
        class Trace(native):
            def step(self):
                if self.memory.rawtags[1]==3 and self.pc==core['BbOriginal_D36B']:
                    events.append(dict(epoch=epoch+1,x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),support=m.ram[2][actor+9]))
                return native.step(self)
        N.NesMPU=Trace
        try:
            for epoch in range(360):
                x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc');y=N.get(m,'Player_Y_Position')
                if phase=='rewind':
                    assert y==176 and N.get(m,'Player_Y_Speed')==0 and solid(x+1,y+32)and solid(x+14,y+32)
                    wall=False
                    if 645<x<=647 and solid(x-8,y+31)and m.ram[2][0x301]&3==2:
                        now=m.ram[2][0x1f]
                        if candidate!=x:candidate=x;candidate_clock=now
                        elif(now-candidate_clock)&255>=1:
                            wall=True;confirmed=dict(epoch=epoch+1,x=x,camera=camera,source_clock=now,elapsed_source_clocks=(now-candidate_clock)&255,
                                source_left_probe_x=x-8,source_left_probe_y=y+31,real_feet=True,old_nominal_target=644)
                    else:candidate=None
                    keys=2
                    if x<=645 or wall:
                        steps=0;keys=1
                        if mode=='direct-RightB':
                            assert not m.ram[2][actor+8]and not m.ram[2][0x301]&64
                            phase='grow';keys=65;launch=dict(epoch=epoch+1,x=x,facing_before=m.ram[2][0x102+oy],cooldown=0)
                        else:phase='face'
                elif phase=='face':
                    keys=1
                    if steps>=face_updates and m.ram[2][actor+8]==0 and m.ram[2][0x102+oy]&64:
                        phase='grow';steps=0;keys|=64;launch=dict(epoch=epoch+1,x=x,facing=m.ram[2][0x102+oy],cooldown=0)
                elif phase=='grow':
                    keys=1|(64 if steps<4 else 0)
                    for i in range(15):
                        gap=m.ram[2][0x18b+8*i]-m.ram[2][0x103+oy]
                        if m.ram[2][0x88+4*i]==2 and 0<=gap<=16:phase='cross';steps=0;keys=129;break
                else:keys=129
                N.put(m,FrameCounter=epoch&255,SavedJoypadBits=keys,SavedJoypad1Bits=keys,VRAM_Buffer1_Offset=0)
                N.invoke(m,'GameCoreRoutine',x=0,y=0);steps+=1
                x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc');y=N.get(m,'Player_Y_Position');minimum=min(minimum,y)
                assert not m.ram[2][actor+3]&128 and N.get(m,'NumberofLives')==2
                if x>=776 and y==176 and N.get(m,'Player_State')==0:break
                if mode=='face2'and len(events)>=2 and epoch>150 and x<736 and y==176 and N.get(m,'Player_State')==0:break
        finally:N.NesMPU=native
        assert confirmed and confirmed['x']==647 and launch and launch['x']==(647 if mode=='direct-RightB'else 647+face_updates)
        assert any(e['support']for e in events),(clock,mode,events,minimum)
        crossed=x>=776 and y==176 and N.get(m,'Player_State')==0
        if mode=='face2':assert not crossed and 721<=x<=722 and y==176 and 131<=minimum<=133,(clock,mode,x,y,minimum)
        else:assert crossed and minimum==96,(clock,mode,confirmed,launch,x,y,events,minimum)
        cases.append(dict(identity=1,mode=mode,initial_actual_camera=camera,source_clock=clock,face_source_updates=0 if mode=='direct-RightB'else face_updates,confirmed_source_wall=confirmed,launch=launch,
            original_jump_entries=events,expected_traversal=mode!='face2',crossed=crossed,final_x=x,final_y=y,epochs=epoch+1,minimum_y=minimum,lives=2))
    out=dict(passed=True,native=False,ROM_written=False,ROM_sha256=PIN,cases=cases,
        scope='ActualBobnegativecamera591/nativeground176/sourcecooldown17 afternaturalpop. ExactsourceLeft walksuntil actual647wall; priorLeft/source8pxsideprobesolid/bothnativefeet/positive sourceclockwithunchangedX confirmit. Face1prelaunch648 crosses; face2prelaunch649 fails721 byoriginalairwallbranch, retainedasexpectednegative. DirectfreshRight+B at647: originalD530 setsrequest, thenPlayerStepRight/pose updates BEFORE BubbleSteppublication, givinggenuineRightbubble/80ride/64pipe→far776/lives2. Bothclockparities. Noextrareset/seededabilities/timer/physicschange; actualBobfullstage remainsrequired.',
        bindings={str(p.relative_to(R)):P.sha(p.read_bytes())for p in[Path(__file__),rom,evidence,O/'combined-current-landing.json']})
    # This producer is still unbound while measuring the one/two-update
    # facing seam; replace its own preliminary aggregate, never native data.
    dst=O/'bob-reachable-rearm-v41-CPU.json';dst.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(passed=True,cases=cases)))


if __name__=='__main__':main()
