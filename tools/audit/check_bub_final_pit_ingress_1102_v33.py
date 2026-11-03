"""Current9cf source landing/reset and fresh-A at captured final plateau."""
import json
from pathlib import Path
import measure_bub_landing_1102_v21 as L

N,Q,P,R,address=L.N,L.Q,L.P,L.R,L.address;O=L.O
PIN='9cf99b438e6f5bc614dc4ccc433707a3796702b7f33a04318a428a1155397f15'


def main():
    _,b,layout,route=L.bundle();rom=O/'combined-current-landing.nes';b['raw']=rom.read_bytes();assert P.sha(b['raw'])==PIN
    core=P.P.labels(L.B/'component.lbl');native=N.NesMPU
    evidence=O/'native-landing-bub-full11-stepback/capture/full11.json'
    actual=json.loads(evidence.read_text());landing=actual['actual_stair_landings'][-1]
    assert (landing['x'],landing['y'],landing['camera'],landing['source_clock'],landing['source_selector'])==(2423,112,2344,1,0)
    captured=O/'native-landing-bub-stair-diagnostic/capture/full11.json'
    terrain=json.loads(captured.read_text())['actual_stair_diagnostic']['terrain']['columns']
    cases=[]
    for identity,selector in[(i,s)for i in[0,1]for s in[0,2,3]]:
        m=Q.fresh(b,route,identity);L.E.main_fields(m);actor=0x42 if identity else 0x2e
        x,y,camera=2444,112,2365;right=camera+255
        N.put(m,Player_X_Position=x&255,Player_PageLoc=x>>8,Player_Y_Position=y,
            ScreenLeft_X_Pos=camera&255,ScreenLeft_PageLoc=camera>>8,
            ScreenRight_X_Pos=right&255,ScreenRight_PageLoc=right>>8,
            Player_Pos_ForScroll=79,PlayerSize=1,PlayerStatus=1,Player_State=0,Player_Y_Speed=0)
        for col in terrain:
            for row in col['rows']:
                wx,wy=col['x'],row['y'];name='Block_Buffer_2'if(wx//256)&1 else'Block_Buffer_1'
                m[address(b,name)+((wy-32)//16)*16+(wx%256)//16]=row['tile']
        for left,right,top in[(2480,2496,144),(2496,2512,160),(2512,2528,176),(2528,2544,192)]:
            for wx in range(left,right,16):
                name='Block_Buffer_2'if(wx//256)&1 else'Block_Buffer_1'
                for wy in range(top,208,16):m[address(b,name)+((wy-32)//16)*16+(wx%256)//16]=97
        def solid(wx,wy):
            if not 32<=wy<240:return False
            name='Block_Buffer_2'if(wx//256)&1 else'Block_Buffer_1'
            return bool(m[address(b,name)+((wy-32)//16)*16+(wx%256)//16])
        m.ram[2][actor+3]=selector;m.ram[2][actor+9]=0;m.ram[2][0x301]=1;m.ram[2][0x1f]=22
        events=[];epoch=-1
        class Trace(native):
            def step(self):
                if self.memory.rawtags[1]==3 and self.pc in[core['BbOriginal_D41C'],core['BbOriginal_D36B']]:
                    wx=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc');wy=N.get(m,'Player_Y_Position')
                    event=dict(epoch=epoch+1,name='reset'if self.pc==core['BbOriginal_D41C']else'jump',
                        x=wx,y=wy,native_state=N.get(m,'Player_State'),native_DY=N.get(m,'Player_Y_Speed'),
                        source_selector=m.ram[2][actor+3],left=solid(wx+1,wy+32),right=solid(wx+14,wy+32),
                        held=m.ram[2][actor+1],bubble_support=m.ram[2][actor+9])
                    if event['name']=='jump':
                        assert event['native_state']==0 and(event['left']or event['right'])and event['held']&128 and not event['bubble_support'],event
                    events.append(event)
                return native.step(self)
        N.NesMPU=Trace;pulse=0;minimum=y
        try:
            for epoch in range(150):
                wx=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc');wy=N.get(m,'Player_Y_Position')
                supported=N.get(m,'Player_State')==0 and N.get(m,'Player_Y_Speed')==0 and(solid(wx+1,wy+32)or solid(wx+14,wy+32))
                healthy=m.ram[2][actor+3]in[0,2,3]
                need=solid(wx+20,wy+31)or not solid(wx+4,wy+32)
                pulse=pulse+1 if supported and healthy and need else 0
                keys=1|(128 if 0<pulse<=3 else 0)
                N.put(m,FrameCounter=epoch&255,SavedJoypadBits=keys,SavedJoypad1Bits=keys,VRAM_Buffer1_Offset=0)
                N.invoke(m,'GameCoreRoutine',x=0,y=0)
                wx=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc');wy=N.get(m,'Player_Y_Position');minimum=min(minimum,wy)
                assert not m.ram[2][actor+3]&128 and N.get(m,'NumberofLives')==2
                if wx>=2488 and N.get(m,'Player_State')==0:break
                if 2448<=wx<2480 and wy>192:break
        finally:N.NesMPU=native
        jumps=[z for z in events if z['name']=='jump']
        assert jumps and jumps[0]['epoch']==1 and jumps[0]['x']==2444 and jumps[0]['y']==112,(identity,selector,events)
        if selector in[2,3]:assert events[0]['name']=='reset' and events[0]['epoch']==1 and events[0]['source_selector']==selector
        assert wx>=2488 and N.get(m,'Player_State')==0 and len(jumps)<=2,(identity,selector,wx,wy,events)
        cases.append(dict(identity=identity,initial_source_selector=selector,initial_native_state=0,initial_DY=0,
            initial_actual_camera=camera,initial_x=x,initial_y=y,events=events,final_x=wx,final_y=wy,
            epochs=epoch+1,minimum_y=minimum,lives=2))
    out=dict(passed=True,native=False,ROM_written=False,ROM_sha256=PIN,cases=cases,
        actual_negative_scope='v31 CSV skips X2444..2446; its exact native/source phase there is unrecorded. These CPU fixtures prove legal ingress, not the missing actual predicate.',
        scope='Exact current9cf actual GameCore, declared nativeState0/DY0/real-foot at X2444/Y112 with captured plateau and source-authored farbank. Both identities/source selectors0,2,3 accept genuine freshA; healthy2/3 first run original D41C then original D36B. Actual physical jump entries require native0/real-foot/A/no bubble marker; final landing native0. No ROM/source/physics/clock edits. Native successor retains strict checks and records every edge decision.',
        bindings={str(p.relative_to(R)):P.sha(p.read_bytes())for p in[Path(__file__),rom,O/'combined-current-landing.json',evidence,captured,O/'landing-v21-CPU.json']})
    dst=O/'final-pit-ingress-v33-CPU.json';assert not dst.exists();dst.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(passed=True,cases=[{k:c[k]for k in['identity','initial_source_selector','final_x','final_y','epochs']}for c in cases])))


if __name__=='__main__':main()
