"""Qualify supported stepbacks over the complete captured staircase and pit."""
import json
from pathlib import Path
import measure_bub_landing_1102_v21 as L

N,Q,P,R,address=L.N,L.Q,L.P,L.R,L.address;O=L.O


def main():
    _,b,layout,route=L.bundle();native=N.NesMPU;core=P.P.labels(L.B/'component.lbl')
    evidence=O/'native-landing-bub-stair-diagnostic/capture/full11.json';q=json.loads(evidence.read_text())['actual_stair_diagnostic'];seed=q['jumps'][0]
    assert seed['x']==2348 and seed['y']==176 and seed['actual_latched_direction']==1
    far=[(2480,2496,144),(2496,2512,160),(2512,2528,176),(2528,2544,192)]
    cases=[]
    for identity,retreat_distance in[(i,d)for i in[0,1]for d in[6,7]]:
        m=Q.fresh(b,route,identity);L.E.main_fields(m);actor=0x42 if identity else 0x2e;oy=8 if identity else 0
        camera=seed['camera'];right=camera+255
        N.put(m,Player_X_Position=seed['x']&255,Player_PageLoc=seed['x']>>8,Player_Y_Position=seed['y'],
            ScreenLeft_X_Pos=camera&255,ScreenLeft_PageLoc=camera>>8,
            ScreenRight_X_Pos=right&255,ScreenRight_PageLoc=right>>8,
            Player_Pos_ForScroll=seed['x']-camera,PlayerSize=1,PlayerStatus=1,Player_State=0,Player_Y_Speed=0)
        for col in q['terrain']['columns']:
            for row in col['rows']:
                wx,wy=col['x'],row['y'];name='Block_Buffer_2'if(wx//256)&1 else'Block_Buffer_1'
                m[address(b,name)+((wy-32)//16)*16+(wx%256)//16]=row['tile']
        for left,right,top in far:
            for wx in range(left,right,16):
                name='Block_Buffer_2'if(wx//256)&1 else'Block_Buffer_1'
                for wy in range(top,208,16):m[address(b,name)+((wy-32)//16)*16+(wx%256)//16]=97
        def solid(wx,wy):
            if not 32<=wy<240:return False
            name='Block_Buffer_2'if(wx//256)&1 else'Block_Buffer_1'
            return bool(m[address(b,name)+((wy-32)//16)*16+(wx%256)//16])
        m.ram[2][actor:actor+20]=seed['actor'];m.ram[2][actor+3]=0
        m.ram[2][0x1f]=seed['source_clock'];m.ram[2][0x301]=129;m.ram[2][0x102+oy]=67
        epoch=-1;phase='walk';target=None;age=0;seen_air=False;start_y=None;pit_start=None;pulse=0
        jumps=[];moves=[];samples=[];landings=[];minimum=176
        class Trace(native):
            def step(self):
                if self.memory.rawtags[1]==3 and self.pc==core['BbOriginal_D36B']:
                    wx=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc');wy=N.get(m,'Player_Y_Position')
                    event=dict(epoch=epoch+1,phase=phase,x=wx,y=wy,camera=N.get(m,'ScreenLeft_X_Pos')+256*N.get(m,'ScreenLeft_PageLoc'),
                        native_state=N.get(m,'Player_State'),left=solid(wx+1,wy+32),right=solid(wx+14,wy+32),held=m.ram[2][actor+1],bubble_support=m.ram[2][actor+9])
                    assert event['native_state']==0 and(event['left']or event['right'])and event['held']&128 and not event['bubble_support'],event
                    jumps.append(event)
                return native.step(self)
        N.NesMPU=Trace
        try:
            for epoch in range(700):
                x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc');y=N.get(m,'Player_Y_Position');ground=N.get(m,'Player_State')==0
                if phase=='walk':
                    keys=1
                    if ground and solid(x+20,y+31):
                        target=x-retreat_distance;phase='back';age=0;keys=2;moves.append(dict(epoch=epoch+1,x=x,y=y,target=target))
                    elif ground and x>=2432 and not solid(x+4,y+32):
                        phase='pit';age=0;keys=129;pulse=1;pit_start=len(jumps)
                elif phase=='back':
                    assert ground and(solid(x+1,y+32)or solid(x+14,y+32)),('unsupported retreat',identity,x,y,phase)
                    assert age<20
                    if x>target:keys=2
                    else:
                        assert not m.ram[2][0x301]&128
                        phase='air';age=0;seen_air=False;start_y=y;keys=129
                elif phase=='air':
                    keys=1|(128 if age<3 else 0)
                    if not ground or y<start_y:seen_air=True
                    if seen_air and ground:
                        landings.append(dict(epoch=epoch+1,x=x,y=y,camera=N.get(m,'ScreenLeft_X_Pos')+256*N.get(m,'ScreenLeft_PageLoc')))
                        phase='walk';age=0;keys=1
                else:
                    need=solid(x+20,y+31)or not solid(x+4,y+32)
                    pulse=pulse+1 if ground and need and m.ram[2][actor+3]in[0,3]else 0
                    keys=1|(128 if 0<pulse<=3 else 0)
                N.put(m,FrameCounter=epoch&255,SavedJoypadBits=keys,SavedJoypad1Bits=keys,VRAM_Buffer1_Offset=0)
                N.invoke(m,'GameCoreRoutine',x=0,y=0);age+=1
                x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc');y=N.get(m,'Player_Y_Position');minimum=min(minimum,y)
                if epoch%32==0:samples.append(dict(epoch=epoch+1,x=x,y=y,phase=phase,camera=N.get(m,'ScreenLeft_X_Pos')+256*N.get(m,'ScreenLeft_PageLoc'),source=m.ram[2][actor+3]))
                assert not m.ram[2][actor+3]&128 and N.get(m,'NumberofLives')==2,(identity,x,y,phase)
                if phase=='pit'and x>=2488 and N.get(m,'Player_State')==0:break
                if 2448<=x<2480 and y>192:break
        finally:N.NesMPU=native
        assert x>=2488 and N.get(m,'Player_State')==0 and pit_start is not None,(identity,x,y,phase,moves,landings,jumps,samples)
        assert 1<=len(jumps)-pit_start<=2,(identity,jumps,pit_start)
        cases.append(dict(identity=identity,retreat_distance=retreat_distance,initial_actual_camera=seed['camera'],initial_clock=seed['source_clock'],
            initial_actual_PlayerSize=1,initial_actual_PlayerStatus=1,retreats=moves,supported_step_landings=landings,
            actual_original_jump_entries=jumps,final_pit_original_jumps=len(jumps)-pit_start,
            final_x=x,final_y=y,final_native_state=N.get(m,'Player_State'),epochs=epoch+1,minimum_y=minimum,lives=2,samples=samples))
    out=dict(passed=True,native=False,ROM_written=False,ROM_sha256=P.sha(b['raw']),cases=cases,
        scope='Exact actualcapturednearstairs/camera/playerform/sourceclock, originalsourceonly6or7pxLeftsupportedstepbacks thenfreshRight+A; normal4pxledgejump acrossactual32pit, farbanksourcecolumns. The7pxcase covers oneadditionalacceptedupdate ofretreat beforephysicalinputswitch. AlloriginalD36B entries validate nativeState0/realfoot/A/noBubbleMarker. Bothidentities completecapturedstairs/finalpit under actualMain, noB/teleport/statechange afterinitialfixture. Nativecontroller remains pending.',
        bindings={str(p.relative_to(R)):P.sha(p.read_bytes())for p in[Path(__file__),evidence,O/'combined-landing.nes',O/'stair-wall-contact-v29-CPU.json']})
    (O/'actual-stair-route-v30-CPU.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(passed=True,cases=[{k:c[k]for k in['identity','retreat_distance','retreats','supported_step_landings','final_pit_original_jumps','final_x','final_y','epochs','lives']}for c in cases])))


if __name__=='__main__':main()
