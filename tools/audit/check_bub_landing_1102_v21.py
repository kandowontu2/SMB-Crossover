"""Original landing reset plus actual Main staircase/air regressions in memory."""
import json
from pathlib import Path
import measure_bub_landing_1102_v21 as L
import check_bubble_bobble_component_1101_v2 as D

E=L.E;N,Q,P,R,address=L.N,L.Q,L.P,L.R,L.address
O=L.O;B=E.O

def main():
    old,new,layout,route=L.bundle();core=P.P.labels(B/'component.lbl');native=N.NesMPU;original=[]
    for identity in[0,1]:
        actor=0x42 if identity else 0x2e
        for selector in[0,1,2,3,128,130,131,255]:
            p=D.pair();D.put(p,actor+3,selector)
            donor=D.run(p,0xd41c,x=actor,y=9,a=0x55,flags=0x71,tag='native_landing_original_reset')
            assert donor.memory[actor+3]==selector&128
            original.append(dict(identity=identity,prior=selector,after=donor.memory[actor+3],A=donor.a,X=donor.x,Y=donor.y,P=donor.p))
    geometry=[(2144,2160,192),(2160,2176,176),(2176,2192,160),(2192,2224,144)]
    stairs=[];reconciliations=[];epoch=-1;current_identity=0
    class Trace(native):
        def step(self):
            if self.pc==core['BbOriginal_D41C']and self.memory.rawtags[1]==3:
                actor=0x42 if current_identity else 0x2e
                if self.memory.ram[2][actor+3]in[2,3]and N.get(self.memory,'Player_State')==0:
                    reconciliations.append(dict(identity=current_identity,epoch=epoch+1,source_selector=self.memory.ram[2][actor+3],native_state=N.get(self.memory,'Player_State'),native_Y_speed=N.get(self.memory,'Player_Y_Speed')))
            return native.step(self)
    N.NesMPU=Trace
    try:
        for identity in[0,1]:
            current_identity=identity;actor=0x42 if identity else 0x2e;m=Q.fresh(new,route,identity);E.main_fields(m)
            N.put(m,Player_X_Position=2100&255,Player_PageLoc=2100>>8,ScreenLeft_X_Pos=2021&255,ScreenLeft_PageLoc=2021>>8,ScreenRight_X_Pos=2276&255,ScreenRight_PageLoc=2276>>8,Player_Pos_ForScroll=79)
            for left,right,top in geometry:
                for wx in range(left,right,16):
                    name='Block_Buffer_2'if(wx//256)&1 else'Block_Buffer_1'
                    for wy in range(top,208,16):m[address(new,name)+((wy-32)//16)*16+(wx%256)//16]=0x54
            def solid(wx,wy):
                if not 32<=wy<240:return False
                name='Block_Buffer_2'if(wx//256)&1 else'Block_Buffer_1'
                return bool(m[address(new,name)+((wy-32)//16)*16+(wx%256)//16])
            samples=[];pulse=0;maxx=2100;minimum=176
            for epoch in range(350):
                x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc');y=N.get(m,'Player_Y_Position')
                ground=N.get(m,'Player_State')==0;need=not solid(x+12,y+32)or solid(x+20,y+31)
                pulse=pulse+1 if ground and need and m.ram[2][actor+3]in[0,3]else 0
                keys=1|(128 if 0<pulse<=3 else 0)
                N.put(m,FrameCounter=epoch&255,SavedJoypadBits=keys,SavedJoypad1Bits=keys,VRAM_Buffer1_Offset=0)
                N.invoke(m,'GameCoreRoutine',x=0,y=0)
                x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc');y=N.get(m,'Player_Y_Position');maxx=max(maxx,x);minimum=min(minimum,y)
                if epoch%24==0:samples.append(dict(epoch=epoch+1,x=x,y=y,native=N.get(m,'Player_State'),source=m.ram[2][actor+3],keys=keys))
                assert not m.ram[2][actor+3]&128 and N.get(m,'NumberofLives')==2
                if x>=2232:break
            assert maxx>=2232,(identity,x,y,samples)
            stairs.append(dict(identity=identity,epochs=epoch+1,max_x=maxx,minimum_y=minimum,final_x=x,final_y=y,lives=2,samples=samples))
    finally:N.NesMPU=native
    # Original airborne motion and zero-input ground remain exactly native
    # coordinate-identical; only genuine native-floor selector reconciliation
    # and the disclosed dead C3EF byte may differ inside private state.
    motion=[]
    for identity in[0,1]:
        for direction,jump in[(0,False),(1,False),(2,False),(1,True),(2,True)]:
            pair=[Q.fresh(b,route,identity)for b in[old,new]]
            for m in pair:E.main_fields(m);N.put(m,Player_X_Position=96)
            for epoch in range(90):
                keys=direction|(128 if jump and epoch==1 else 0)
                for m in pair:
                    N.put(m,FrameCounter=epoch&255,SavedJoypadBits=keys,SavedJoypad1Bits=keys,VRAM_Buffer1_Offset=0)
                    N.invoke(m,'GameCoreRoutine',x=0,y=0)
                a,b=pair;fields=['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','NumberofLives']
                assert[N.get(a,n)for n in fields]==[N.get(b,n)for n in fields],(identity,direction,jump,epoch)
            motion.append(dict(identity=identity,direction=direction,jump=jump,Main_epochs=90,coordinates_exact=True))
    # Healthy air, ascent and injury fail the landing guard. The entered
    # NativeUpdate is required to have one accepted fresh source epoch.
    guards=[]
    for identity in[0,1]:
        actor=0x42 if identity else 0x2e
        for selector,state,speed in[(0,0,0),(1,0,0),(2,1,0),(3,1,0),(2,0,1),(3,0,255),(128,0,0),(130,0,0),(131,0,0)]:
            m=Q.fresh(new,route,identity);E.main_fields(m);m.ram[2][actor+3]=selector;N.put(m,Player_State=state,Player_Y_Speed=speed)
            m[0x5115]=3;m[0x5116]=2;N.put(m,CurrentBank=3,CurrentBankC=2)
            # Test the exact18B predicate up to its sourcePlayerStep successor.
            c=N.NesMPU(memory=m,pc=layout['labels']['BbNativeLanding']);c.x=actor;c.y=8 if identity else 0;c.sp=224;c.a=85;c.p=0x31
            for _ in range(30):
                if c.pc==layout['labels']['BbNativeLandingDone']:break
                c.step()
            else:raise AssertionError('Landing predicate bound')
            assert m.ram[2][actor+3]==selector,(identity,selector,state,speed)
            guards.append(dict(identity=identity,selector=selector,native_state=state,velocity=speed,rejected=True))
    assert reconciliations and all(z['native_state']==0 and z['native_Y_speed']==0 for z in reconciliations)
    out=dict(passed=True,ROM_written=False,native=False,base_ROM_sha256=L.PIN,original_reset_cases=original,stair_cases=stairs,
        reconciliations=reconciliations,original_motion_cases=motion,rejected_guard_cases=guards,
        source_physics_changed=False,scope='Private compiled proposal exactcurrentMain; bothidentities actualnativefoot-supported16pxstairs now traverse without changing43pxsourcejump. OriginalD41C reset differential coversinjurybit preservation; airborne/ascent/injury guardrejects; 900flatidle/walk/jumpMain coordinatecomparisons exact. Actualnativefullstage/cold/ISR successor stillrequired.',
        bindings={str(p.relative_to(R)):P.sha(p.read_bytes())for p in[Path(__file__),R/'tools/audit/measure_bub_landing_1102_v21.py',O/'landing-v21-layout.json',O/'landing-v21-image.bin',O/'landing-v21-helper.chr',O/'stair-route-v20-CPU.json']})
    (O/'landing-v21-CPU.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(passed=True,stairs=stairs,original_reset_cases=len(original),motion_cases=len(motion),guard_cases=len(guards))))

if __name__=='__main__':main()
