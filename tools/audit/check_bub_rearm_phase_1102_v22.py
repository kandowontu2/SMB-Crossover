"""Actual camera-phase leftwall stop and earliest real facing-ready shot."""
import json
from pathlib import Path
import measure_bub_landing_1102_v21 as L

N,Q,P,R,address=L.N,L.Q,L.P,L.R,L.address;O=L.O

def main():
    _,b,q,route=L.bundle();cases=[];native=N.NesMPU;core=P.P.labels(L.B/'component.lbl')
    for identity,clock in[(i,c)for i in[0,1]for c in[147,148]]:
        m=Q.fresh(b,route,identity);L.E.main_fields(m);actor=0x42 if identity else 0x2e;oy=8 if identity else 0
        N.put(m,Player_X_Position=668&255,Player_PageLoc=668>>8,ScreenLeft_X_Pos=589&255,ScreenLeft_PageLoc=589>>8,ScreenRight_X_Pos=844&255,ScreenRight_PageLoc=844>>8,Player_Pos_ForScroll=79)
        for left,right,top in[(608,640,160),(736,768,144)]:
            for wx in range(left,right,16):
                name='Block_Buffer_2'if(wx//256)&1 else'Block_Buffer_1'
                for wy in range(top,208,16):m[address(b,name)+((wy-32)//16)*16+(wx%256)//16]=0x54
        m.ram[2][actor+8]=18;m.ram[2][0x1f]=clock
        phase='rewind';steps=0;launch=None;events=[];samples=[];epoch=-1;ys=[]
        class Trace(native):
            def step(self):
                if self.pc==core['BbOriginal_D36B']and self.memory.rawtags[1]==3:
                    events.append(dict(epoch=epoch+1,support=m.ram[2][actor+9],x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc')))
                return native.step(self)
        N.NesMPU=Trace
        try:
            for epoch in range(350):
                x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc')
                if phase=='rewind':
                    keys=2
                    if x<=645:phase='face';steps=0;keys=1
                elif phase=='face':
                    keys=1
                    if steps>=1 and m.ram[2][actor+8]==0 and m.ram[2][0x102+oy]&64:
                        phase='grow';steps=0;keys|=64;launch=dict(epoch=epoch+1,x=x,source_facing=m.ram[2][0x102+oy],cooldown=m.ram[2][actor+8])
                elif phase=='grow':
                    keys=1|(64 if steps<4 else 0)
                    for slot in range(15):
                        gap=m.ram[2][0x18b+8*slot]-m.ram[2][0x103+oy]
                        if m.ram[2][0x88+4*slot]==2 and 0<=gap<=16:phase='cross';steps=0;keys=129;break
                else:keys=129
                N.put(m,FrameCounter=epoch&255,SavedJoypadBits=keys,SavedJoypad1Bits=keys,VRAM_Buffer1_Offset=0);N.invoke(m,'GameCoreRoutine',x=0,y=0);steps+=1
                x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc');y=N.get(m,'Player_Y_Position');ys.append(y)
                if epoch%24==0:samples.append(dict(epoch=epoch+1,x=x,y=y,phase=phase))
                assert not m.ram[2][actor+3]&128 and N.get(m,'NumberofLives')==2
                if x>=776 and y==176 and N.get(m,'Player_State')==0:break
        finally:N.NesMPU=native
        assert launch and launch['x']==646 and any(z['support']for z in events)and x>=776 and y==176,(identity,clock,launch,x,y,events,samples)
        cases.append(dict(identity=identity,initial_source_clock=clock,actual_camera=589,nominal_target=644,accepted_source_wall_stop=645,launch=launch,final_x=x,final_y=y,minimum_y=min(ys),source_jump_events=events,epochs=epoch+1,lives=2))
    evidence=O/'native-landing-bub-full11/capture/full11.json';negative=json.loads(evidence.read_text());assert negative['why']=='Bounded source shot rearm'and negative['current_x']==645
    out=dict(passed=True,ROM_written=False,native=False,ROM_sha256=P.sha(b['raw']),cases=cases,
        scope='Current landing candidate actualMain with priorpipe608..640 and64pxpipe736..768/camera589. Bothidentities/bothclockparities: sourceclampsat645, oneactualRightupdate earnsattr40 beforefreshB at646; originalgap16ride supportsfarX776/Y176/lives2. Controllerphase correction only; do notchange physics or native assertions.',
        bindings={str(p.relative_to(R)):P.sha(p.read_bytes())for p in[Path(__file__),evidence,O/'combined-landing.nes',O/'landing-v21-layout.json']})
    (O/'rearm-phase-v22-CPU.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))

if __name__=='__main__':main()
