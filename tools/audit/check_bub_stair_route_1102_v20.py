"""Original directional43px jumps over legal native16px stairs; no ROM edits."""
import json
from pathlib import Path
import check_bubble_native_event_1102_v9 as E

N,Q,P,R,address=E.N,E.Q,E.P,E.R,E.address
O=R/'build/bub-menu-candidate-1102-v2'
CURRENT=R/'build/menu-family-root-candidate-1102-v1/mr-gimmick-family.nes'
PIN='22d09909bf952ef007d1582589dc869073262784bf38b92d2c7b206ce3c45b19'

def main():
    _,b,layout,route=E.bundle();b['raw']=CURRENT.read_bytes();assert P.sha(b['raw'])==PIN
    native=N.NesMPU;rows=[];core=P.P.labels(E.O/'component.lbl')
    # Explicit legal metatile arena matches the positive first native foot
    # probe (world2144 top192). Higher columns test the same16px staircase.
    geometry=[(2144,2160,192),(2160,2176,176),(2176,2192,160),(2192,2224,144)]
    for identity,use_jump in[(i,j)for i in[0,1]for j in[False,True]]:
        m=Q.fresh(b,route,identity);E.main_fields(m);actor=0x42 if identity else 0x2e;oy=8 if identity else 0
        N.put(m,Player_X_Position=2100&255,Player_PageLoc=2100>>8,ScreenLeft_X_Pos=2021&255,ScreenLeft_PageLoc=2021>>8,
            ScreenRight_X_Pos=2276&255,ScreenRight_PageLoc=2276>>8,Player_Pos_ForScroll=79)
        for left,right,top in geometry:
            for wx in range(left,right,16):
                name='Block_Buffer_2'if(wx//256)&1 else'Block_Buffer_1'
                for wy in range(top,208,16):m[address(b,name)+((wy-32)//16)*16+(wx%256)//16]=0x54
        def solid(wx,wy):
            if not 32<=wy<240:return False
            name='Block_Buffer_2'if(wx//256)&1 else'Block_Buffer_1'
            return bool(m[address(b,name)+((wy-32)//16)*16+(wx%256)//16])
        events=[];mismatch=[];xs=[];ys=[];pulse=0;epoch=-1;samples=[]
        class Trace(native):
            def step(self):
                if self.pc==core['BbOriginal_D36B']and self.memory.rawtags[1]==3:
                    events.append(dict(epoch=epoch+1,x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),y=N.get(m,'Player_Y_Position'),source_input=m.ram[2][actor+1]))
                if self.pc==layout['labels']['BbNativeDraw']and self.memory.rawtags[1]==3:
                    x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc')
                    expected=(x-N.get(m,'ScreenLeft_X_Pos')-256*N.get(m,'ScreenLeft_PageLoc')+16)&255
                    cached=m.ram[2][0x103+oy]
                    if cached!=expected and len(mismatch)<6:
                        mismatch.append(dict(epoch=epoch+1,native_x=x,source_x=cached,expected_source_x=expected,delta=((cached-expected+128)&255)-128,native_y=N.get(m,'Player_Y_Position')))
                if self.pc==layout['labels']['BbNativePair']and self.memory.rawtags[1]==3 and mismatch and'source_after_actual_draw'not in mismatch[-1]:
                    after=m.ram[2][0x103+oy];assert after==mismatch[-1]['expected_source_x']
                    mismatch[-1]['source_after_actual_draw']=after
                return native.step(self)
        N.NesMPU=Trace
        try:
            for epoch in range(180 if use_jump else 70):
                x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc');y=N.get(m,'Player_Y_Position');ground=N.get(m,'Player_State')==0
                need=not solid(x+12,y+32)or solid(x+20,y+31)
                pulse=pulse+1 if ground and need and m.ram[2][actor+3]==0 else 0
                keys=1|(128 if use_jump and 0<pulse<=3 else 0)
                N.put(m,FrameCounter=epoch&255,SavedJoypadBits=keys,SavedJoypad1Bits=keys,VRAM_Buffer1_Offset=0)
                N.invoke(m,'GameCoreRoutine',x=0,y=0)
                x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc');y=N.get(m,'Player_Y_Position');xs.append(x);ys.append(y)
                if epoch%16==0:samples.append(dict(epoch=epoch+1,x=x,y=y,keys=keys,pulse=pulse,native=N.get(m,'Player_State'),source=list(m.ram[2][actor:actor+10])))
                expected=(x-N.get(m,'ScreenLeft_X_Pos')-256*N.get(m,'ScreenLeft_PageLoc')+16)&255
                cached=m.ram[2][0x103+oy]
                assert cached==expected
                assert not m.ram[2][actor+3]&128 and N.get(m,'NumberofLives')==2
                if use_jump and x>=2224:break
        finally:N.NesMPU=native
        if use_jump:
            assert x==2165 and y==128 and len(events)==2,(identity,x,y,events,samples[-12:])
            assert N.get(m,'Player_State')==0 and m.ram[2][actor+3]==3
            assert solid(x+14,y+32)and not solid(x+1,y+32)
        else:assert max(xs)<2144 and mismatch,(identity,x,y,mismatch)
        rows.append(dict(identity=identity,step_jump_controller=use_jump,epochs=epoch+1,maximum_x=max(xs),final_y=ys[-1],minimum_y=min(ys),source_jump_events=events,
            actual_collision_cache_examples=mismatch,lives=N.get(m,'NumberofLives'),samples=samples,
            final_native_state=N.get(m,'Player_State'),final_native_Y_speed=N.get(m,'Player_Y_Speed'),final_source_selector=m.ram[2][actor+3],
            left_foot_native_solid=solid(x+1,y+32),right_foot_native_solid=solid(x+14,y+32)))
    out=dict(passed=True,diagnostic_only=True,stair_traversal_passed=False,source_native_support_disagreement_reproduced=True,ROM_sha256=PIN,ROM_written=False,native_emulator=False,source_physics_changed=False,geometry=geometry,cases=rows,
        original_landing_contract='OriginalD3AE falllanding clears actor+3 then unwinds its2nestedreturnbytes. OriginalD41C..D422 directly loads actor+3, AND80, storesactor+3,RTS: retaininjury80 while clearingunsupported3 after originalD3C1 support accepts. Neither resetsjumpheight/timer or grantsnewability. A proposed native actualsupportadapter must prove its own realgroundpredicate and original-entry ABI, not call the unwindingD3AE as a normal leaf.',
        scope='Actual currentGameCore legal metatile staircase, bothidentities. Right-only reproduces firststepstall. Existing bodybottom/sidefoot controller earns2genuine43pxjumps but reproduces nativeState0/rightfoot-supported X2165/Y128 with sourceunsupported3, stopping furtherwalking. This is a negative integration fixture, not traversalpass. BeforeactualDraw sourcecache can precede native sideclamp; actual HuDraw resynchronizes cache and rendered body. No nativefullstage/parser or fixclaim.',
        bindings={str(p.relative_to(R)):P.sha(p.read_bytes())for p in[Path(__file__),CURRENT,O/'native-event-bub-full11-wide/capture/full11.json']})
    (O/'stair-route-v20-CPU.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))

if __name__=='__main__':main()
