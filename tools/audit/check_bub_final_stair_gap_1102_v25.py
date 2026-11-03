"""Source-normal43px jumps over the final authored stair/pit, actual Main only."""
import hashlib,json,re
from pathlib import Path
import measure_bub_landing_1102_v21 as L

N,Q,P,R,address=L.N,L.Q,L.P,L.R,L.address;O=L.O


def main():
    _,b,layout,route=L.bundle();core=P.P.labels(L.B/'component.lbl')
    text=(R/'src/level_tiles.s').read_text()
    block=text.split('L_GroundArea6:\n',1)[1].split('L_GroundArea7:',1)[0]
    stream=bytes(int(v,16)for line in block.splitlines()if'.byte'in line for v in re.findall(r'\$([0-9a-fA-F]{2})',line))
    assert len(stream)==101 and hashlib.sha256(stream).hexdigest()=='162fc0bf0e2e7bd2ecda0ac1bf3551ee5f45a3f116fa6343badda72005c0b4ec'
    assert b['raw'].count(stream)==1
    assert bytes.fromhex('4fb387639c01b763c862d961ea60')in stream
    # Actual page9 sequence: staircase4F/B3 emits rowsA,9,8,7;
    # column87/63 extends the row7 plateau, 9C/01 clears two columns;
    # B7/63,C8/62,D9/61,EA/60 emit the descending far bank.
    geometry=[(2368,2384,192),(2384,2400,176),(2400,2416,160),(2416,2448,144),
              (2480,2496,144),(2496,2512,160),(2512,2528,176),(2528,2544,192)]
    native=N.NesMPU;cases=[]
    for identity,probe in[(i,p)for i in[0,1]for p in[12,4]]:
        m=Q.fresh(b,route,identity);L.E.main_fields(m);actor=0x42 if identity else 0x2e
        N.put(m,Player_X_Position=2330&255,Player_PageLoc=2330>>8,
            ScreenLeft_X_Pos=2251&255,ScreenLeft_PageLoc=2251>>8,
            ScreenRight_X_Pos=2506&255,ScreenRight_PageLoc=2506>>8,Player_Pos_ForScroll=79)
        for left,right,top in geometry:
            for wx in range(left,right,16):
                name='Block_Buffer_2'if(wx//256)&1 else'Block_Buffer_1'
                for wy in range(top,208,16):m[address(b,name)+((wy-32)//16)*16+(wx%256)//16]=0x61
        for wx in range(2448,2480,16):
            name='Block_Buffer_2'if(wx//256)&1 else'Block_Buffer_1'
            for wy in range(32,240,16):m[address(b,name)+((wy-32)//16)*16+(wx%256)//16]=0
        def solid(wx,wy):
            if not 32<=wy<240:return False
            name='Block_Buffer_2'if(wx//256)&1 else'Block_Buffer_1'
            return bool(m[address(b,name)+((wy-32)//16)*16+(wx%256)//16])
        epoch=-1;events=[];samples=[];minimum=176;takeoff=None;crossing=None;pulse=0
        class Trace(native):
            def step(self):
                if self.pc==core['BbOriginal_D36B']and self.memory.rawtags[1]==3:
                    events.append(dict(epoch=epoch+1,x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),
                        y=N.get(m,'Player_Y_Position'),native_state=N.get(m,'Player_State'),
                        prior_support=m.ram[2][actor+9],source_keys=m.ram[2][actor+1]))
                return native.step(self)
        N.NesMPU=Trace
        try:
            for epoch in range(650):
                x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc');y=N.get(m,'Player_Y_Position')
                grounded=N.get(m,'Player_State')==0
                need=solid(x+20,y+31)or not solid(x+probe,y+32)
                pulse=pulse+1 if grounded and need and m.ram[2][actor+3]in[0,3]else 0
                keys=1|(128 if 0<pulse<=3 else 0)
                if 2432<=x<2448 and keys&128 and takeoff is None:
                    takeoff=dict(epoch=epoch+1,x=x,y=y,left_support=solid(x+1,y+32),right_support=solid(x+14,y+32))
                N.put(m,FrameCounter=epoch&255,SavedJoypadBits=keys,SavedJoypad1Bits=keys,VRAM_Buffer1_Offset=0)
                N.invoke(m,'GameCoreRoutine',x=0,y=0)
                x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc');y=N.get(m,'Player_Y_Position');minimum=min(minimum,y)
                if epoch%32==0:samples.append(dict(epoch=epoch+1,x=x,y=y,native_state=N.get(m,'Player_State'),source=m.ram[2][actor+3],keys=keys))
                if m.ram[2][actor+3]&128 or N.get(m,'NumberofLives')!=2 or N.get(m,'GameEngineSubroutine')==11:break
                # The early takeoff control is a traversal negative. Stop it
                # below the original ground before unrelated death/audio
                # continuation, which this isolated arena does not initialize.
                if 2448<=x<2480 and y>192:break
                if x>=2488 and N.get(m,'Player_State')==0:
                    crossing=dict(epoch=epoch+1,x=x,y=y);break
        finally:N.NesMPU=native
        cases.append(dict(identity=identity,foot_probe_dx=probe,takeoff=takeoff,crossing=crossing,
            original_D36B_events=events,final_x=x,final_y=y,minimum_y=minimum,
            source_injury=bool(m.ram[2][actor+3]&128),lives=N.get(m,'NumberofLives'),samples=samples))
    qualified=[c for c in cases if c['foot_probe_dx']==4]
    assert all(c['crossing']and c['takeoff']and c['takeoff']['left_support']and not c['source_injury']and c['lives']==2 for c in qualified),cases
    out=dict(passed=True,ROM_written=False,native=False,ROM_sha256=P.sha(b['raw']),geometry=geometry,pit=[2448,2480],
        cases=cases,scope='Source-backed legal native metatile arena from exact current1-1 objectstream. ActualGameCore and original freshA/D36B, no B/support marker/physics changes after initialization. Both identities ordinary stair climb plus late supported43pxjump clear32pxpit. Native parser/controller fullstage remains pending.',
        bindings={str(p.relative_to(R)):P.sha(p.read_bytes())for p in[Path(__file__),R/'src/level_tiles.s',O/'combined-landing.nes',O/'landing-v21-layout.json']})
    (O/'final-stair-gap-v25-CPU.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(passed=True,cases=[{k:c[k]for k in['identity','foot_probe_dx','takeoff','crossing','final_x','final_y','lives']}for c in cases])))


if __name__=='__main__':main()
