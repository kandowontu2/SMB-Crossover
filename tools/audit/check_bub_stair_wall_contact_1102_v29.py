"""Reproduce the measured camera-aligned donor wall latch before any route fix."""
import json
from pathlib import Path
import measure_bub_landing_1102_v21 as L

N,Q,P,R,address=L.N,L.Q,L.P,L.R,L.address;O=L.O


def main():
    _,b,layout,route=L.bundle();core=P.P.labels(L.B/'component.lbl');native=N.NesMPU
    evidence=O/'native-landing-bub-stair-diagnostic/capture/full11.json';diag=json.loads(evidence.read_text())['actual_stair_diagnostic']
    assert diag['jumps'][1]['x']==2369 and diag['jumps'][1]['camera']==2288 and diag['jumps'][1]['source_clock']==77
    assert all(j['actual_latched_direction']==1 for j in diag['jumps'])
    cases=[]
    for identity,retreat in[(i,r)for i in[0,1]for r in[False,True]]:
        m=Q.fresh(b,route,identity);L.E.main_fields(m);actor=0x42 if identity else 0x2e;oy=8 if identity else 0
        N.put(m,Player_X_Position=2369&255,Player_PageLoc=2369>>8,Player_Y_Position=160,
            ScreenLeft_X_Pos=2288&255,ScreenLeft_PageLoc=2288>>8,
            ScreenRight_X_Pos=2543&255,ScreenRight_PageLoc=2543>>8,
            Player_Pos_ForScroll=81,PlayerSize=1,PlayerStatus=1,Player_State=0,Player_Y_Speed=0)
        # Actual captured rows, including tile IDs97 and84, rather than an
        # approximate source arena or a different screen-grid alignment.
        for col in diag['terrain']['columns']:
            for row in col['rows']:
                wx,wy=col['x'],row['y'];name='Block_Buffer_2'if(wx//256)&1 else'Block_Buffer_1'
                m[address(b,name)+((wy-32)//16)*16+(wx%256)//16]=row['tile']
        m.ram[2][actor:actor+20]=diag['jumps'][1]['actor'];m.ram[2][actor+3]=0
        m.ram[2][0x1f]=77;m.ram[2][0x301]=1;m.ram[2][0x102+oy]=67
        epoch=-1;zeroes=[];jumps=[];samples=[];minimum=160;phase='retreat'if retreat else'jump';takeoff=None
        class Trace(native):
            def step(self):
                if self.memory.rawtags[1]==3:
                    if self.pc==core['BbOriginal_D4BB']:
                        zeroes.append(dict(epoch=epoch+1,pc=self.pc,A=self.a,old_latch=m.ram[2][actor+5],
                            x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),y=N.get(m,'Player_Y_Position'),
                            source_y=m.ram[2][0x100+oy],source_x=m.ram[2][0x103+oy],source_probe=list(m.ram[2][0x21:0x25]),
                            native_tile=list(m.ram[2][0x3d0:0x3d5]),selector=m.ram[2][actor+3]))
                    if self.pc==core['BbOriginal_D36B']:
                        jumps.append(dict(epoch=epoch+1,x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),
                            y=N.get(m,'Player_Y_Position'),native_state=N.get(m,'Player_State'),held=m.ram[2][actor+1],support=m.ram[2][actor+9]))
                return native.step(self)
        N.NesMPU=Trace
        try:
            for epoch in range(105):
                x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc')
                if phase=='retreat'and x>2363:keys=2
                else:
                    if phase!='air':
                        phase='air';takeoff=dict(epoch=epoch+1,x=x,y=N.get(m,'Player_Y_Position'));keys=129
                    else:keys=1
                N.put(m,FrameCounter=epoch&255,SavedJoypadBits=keys,SavedJoypad1Bits=keys,VRAM_Buffer1_Offset=0)
                N.invoke(m,'GameCoreRoutine',x=0,y=0)
                x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc');y=N.get(m,'Player_Y_Position');minimum=min(minimum,y)
                if epoch%12==0:samples.append(dict(epoch=epoch+1,x=x,y=y,latch=m.ram[2][actor+5],source=m.ram[2][actor+3],native=N.get(m,'Player_State')))
                assert not m.ram[2][actor+3]&128 and N.get(m,'NumberofLives')==2
                if retreat and x>=2384 and y==144 and N.get(m,'Player_State')==0:break
        finally:N.NesMPU=native
        cases.append(dict(identity=identity,retreat_before_freshA=retreat,actual_camera=2288,initial_clock=77,
            takeoff=takeoff,original_jump_entries=jumps,original_wall_direction_clear=zeroes[:6],
            final_x=x,final_y=y,final_native_state=N.get(m,'Player_State'),minimum_y=minimum,lives=2,samples=samples))
    immediate=[c for c in cases if not c['retreat_before_freshA']];back=[c for c in cases if c['retreat_before_freshA']]
    assert all(c['final_x']<2384 and c['original_wall_direction_clear']for c in immediate),cases
    assert all(c['final_x']>=2384 and c['final_y']==144 and c['final_native_state']==0 for c in back),cases
    out=dict(passed=True,native=False,ROM_written=False,ROM_sha256=P.sha(b['raw']),cases=cases,
        first_source_contact='Exact originalD4BE right-side probe reaches solid native step, D4EB/EF/F1 follows originalD4B9/D4BB and clears actor+5 direction latch. Later Right input does not restore that airborne latch; D36B only latches at takeoff. No donor or terrain defect inferred.',
        scope='Actual captured tiles97/84, PlayerSize1/Status1, camera2288/sourceclock77 and standing160 are initialized once. ActualGameCore then accepts only source controls. Immediate freshRight+A at2369 repeatsvertical117..160. Genuine supported6pxLeft retreat then freshRight+A at2363 clears this16pxstep and lands2385/Y144/nativeState0. This is one measured wall/step, not whole staircase/fullstage. Native route correction pending.',
        bindings={str(p.relative_to(R)):P.sha(p.read_bytes())for p in[Path(__file__),evidence,O/'combined-landing.nes',O/'landing-v21-layout.json']})
    (O/'stair-wall-contact-v29-CPU.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(passed=True,cases=[{k:c[k]for k in['identity','retreat_before_freshA','takeoff','final_x','final_y','minimum_y','original_wall_direction_clear']}for c in cases])))


if __name__=='__main__':main()
