"""Current real1-1 parser and supported controls over the castle staircase."""
import json
from pathlib import Path
import measure_bub_landing_1102_v21 as L

N,Q,P,R,address=L.N,L.Q,L.P,L.R,L.address;O=L.O
PIN='9cf99b438e6f5bc614dc4ccc433707a3796702b7f33a04318a428a1155397f15'


def main():
    _,b,layout,route=L.bundle();rom=O/'combined-current-landing.nes';b['raw']=rom.read_bytes();assert P.sha(b['raw'])==PIN
    evidence=O/'native-current-landing-bub-full11-reachable-pit/capture/full11.json';actual=json.loads(evidence.read_text())
    assert actual['why']=='Source route stationary500Main without a completed crossing'and actual['current_x']==2961 and actual['initial_lives']==actual['final_lives']==2
    assert len(actual['clears'])==7 and actual['clears'][-1]['right_exclusive']==2480
    # Execute the current linked level constructor directly, solely to decode
    # authored cells. This is no controller or live-scene claim.
    parser=Q.fresh(b,route,0);N.put(parser,AreaPointer=0x25,WorldNumber=0,Hidden1UpFlag=1)
    N.invoke(parser,'GetAreaDataAddrs')
    for i in range(3):parser[address(b,'AreaObjectLength')+i]=255
    columns=[]
    for col in range(208):
        N.invoke(parser,'AreaParserCore');columns.append([parser[address(b,'MetatileBuffer')+r]for r in range(13)])
        N.invoke(parser,'IncrementColumnPos')
    geometry=[]
    for x in range(2896,3040,16):
        nonzero=[i for i,t in enumerate(columns[x//16])if t==97]
        assert nonzero,(x,columns[x//16]);geometry.append(dict(left=x,right=x+16,top=32+16*min(nonzero)))
    assert [r['top']for r in geometry]==[192,176,160,144,128,112,96,80,80],geometry
    native=N.NesMPU;core=P.P.labels(L.B/'component.lbl');cases=[]
    for identity,start in[(i,s)for i in[0,1]for s in['last-pipe','actual-stuck-step']]:
        m=Q.fresh(b,route,identity);L.E.main_fields(m);actor=0x42 if identity else 0x2e
        x,y,camera=(2865,144,2786)if start=='last-pipe'else(2961,96,2880);right=camera+255
        N.put(m,Player_X_Position=x&255,Player_PageLoc=x>>8,Player_Y_Position=y,
            ScreenLeft_X_Pos=camera&255,ScreenLeft_PageLoc=camera>>8,
            ScreenRight_X_Pos=right&255,ScreenRight_PageLoc=right>>8,
            Player_Pos_ForScroll=x-camera,PlayerSize=1,PlayerStatus=1,Player_State=0,Player_Y_Speed=0)
        for wx in range(2816,3328,16):
            name='Block_Buffer_2'if(wx//256)&1 else'Block_Buffer_1'
            for row,tile in enumerate(columns[wx//16]):m[address(b,name)+16*row+(wx%256)//16]=tile
        def solid(wx,wy):
            if not 32<=wy<240:return False
            name='Block_Buffer_2'if(wx//256)&1 else'Block_Buffer_1'
            return bool(m[address(b,name)+((wy-32)//16)*16+(wx%256)//16])
        m.ram[2][actor+3]=0;m.ram[2][0x301]=1
        epoch=-1;phase='walk';age=0;seen_air=False;target=None;start_y=y;jumps=[];retreats=[];landings=[];pulse=0
        class Trace(native):
            def step(self):
                if self.memory.rawtags[1]==3 and self.pc==core['BbOriginal_D36B']:
                    wx=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc');wy=N.get(m,'Player_Y_Position')
                    event=dict(epoch=epoch+1,x=wx,y=wy,native_state=N.get(m,'Player_State'),
                        left=solid(wx+1,wy+32),right=solid(wx+14,wy+32),held=m.ram[2][actor+1],marker=m.ram[2][actor+9])
                    assert event['native_state']==0 and(event['left']or event['right'])and event['held']&128 and not event['marker'],event
                    jumps.append(event)
                return native.step(self)
        N.NesMPU=Trace
        try:
            for epoch in range(650):
                wx=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc');wy=N.get(m,'Player_Y_Position');ground=N.get(m,'Player_State')==0
                if phase=='walk':
                    keys=1
                    if wx>=2944 and ground and solid(wx+20,wy+31)and m.ram[2][actor+3]in[0,3]:
                        target=wx-6;phase='back';age=0;keys=2;retreats.append(dict(epoch=epoch+1,x=wx,y=wy,target=target))
                    elif wx<2944:
                        need=solid(wx+20,wy+31)or not solid(wx+12,wy+32)
                        pulse=pulse+1 if ground and need and m.ram[2][actor+3]in[0,3]else 0
                        keys=1|(128 if 0<pulse<=3 else 0)
                elif phase=='back':
                    assert ground and(solid(wx+1,wy+32)or solid(wx+14,wy+32))and age<=20,(identity,start,epoch,wx,wy)
                    if wx>target:keys=2
                    else:
                        assert not m.ram[2][0x301]&128
                        phase='air';age=0;start_y=wy;seen_air=False;keys=129
                else:
                    keys=1|(128 if age<3 else 0)
                    if not ground or wy<start_y:seen_air=True
                    if seen_air and ground:
                        assert solid(wx+1,wy+32)or solid(wx+14,wy+32)
                        landings.append(dict(epoch=epoch+1,x=wx,y=wy,camera=N.get(m,'ScreenLeft_X_Pos')+256*N.get(m,'ScreenLeft_PageLoc')))
                        phase='walk';age=0;keys=1
                    assert age<=150
                N.put(m,FrameCounter=epoch&255,SavedJoypadBits=keys,SavedJoypad1Bits=keys,VRAM_Buffer1_Offset=0)
                N.invoke(m,'GameCoreRoutine',x=0,y=0);age+=1
                wx=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc');wy=N.get(m,'Player_Y_Position')
                assert not m.ram[2][actor+3]&128 and N.get(m,'NumberofLives')==2
                if wx>=3024 and wy==48 and N.get(m,'Player_State')==0:break
        finally:N.NesMPU=native
        assert wx>=3024 and wy==48 and N.get(m,'Player_State')==0,(identity,start,wx,wy,retreats,landings,jumps)
        cases.append(dict(identity=identity,start=start,seed_x=x,seed_y=y,seed_camera=camera,
            supported_retreats=retreats,actual_original_jumps=jumps,landings=landings,
            final_x=wx,final_y=wy,final_native_state=N.get(m,'Player_State'),epochs=epoch+1,lives=2))
    out=dict(passed=True,native=False,ROM_written=False,ROM_sha256=PIN,actual_parser_columns=208,castle_staircase=geometry,cases=cases,
        scope='Current GetAreaDataAddrs/AreaParserCore/IncrementColumnPos decodes authored1-1; no handcrafted endstairs. Bothidentities actualGameCore from real lastpipe support and actualstuck2961/Y96/camera2880 climb thefinalstairs. Existingmarchcontrols below2944, verified6pxreal-supportedLeft and freshRight+A above2944 then realair/landing. AllsourceD36Bnative0/realfoot/A/marker0; no source/physics/helper changes. CurrentMesencontroller fullstage stillrequired.',
        bindings={str(p.relative_to(R)):P.sha(p.read_bytes())for p in[Path(__file__),rom,evidence,R/'src/level_tiles.s',O/'combined-current-landing.json']})
    dst=O/'castle-stairs-v38-CPU.json';assert not dst.exists();dst.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(passed=True,geometry=geometry,cases=[{k:c[k]for k in['identity','start','final_x','final_y','epochs','supported_retreats']}for c in cases])))


if __name__=='__main__':main()
