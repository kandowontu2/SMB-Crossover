"""Qualify the actual odd-X native-ground takeoff, without air-jump admission."""
import json,zipfile
from pathlib import Path
import measure_bub_landing_1102_v21 as L

N,Q,P,R,address=L.N,L.Q,L.P,L.R,L.address;O=L.O
PIN='9cf99b438e6f5bc614dc4ccc433707a3796702b7f33a04318a428a1155397f15'


def main():
    archive=O/'landing-current-supplement-v35.zip';assert P.sha(archive.read_bytes())=='41ca85f81278f25fe33349193e196134456abd1617006caa11826625805fb857'
    with zipfile.ZipFile(archive)as z:
        actual=json.loads(z.read('build/bub-menu-candidate-1102-v2/native-current-landing-bub-full11-final-pit/capture/full11.json'))
        terrain=json.loads(z.read('build/bub-menu-candidate-1102-v2/native-landing-bub-stair-diagnostic/capture/full11.json'))['actual_stair_diagnostic']['terrain']['columns']
    rows=actual['actual_final_edge_decisions'];row=next(r for r in rows if r['Main']==3861);seed=row['support']
    assert(seed['x'],seed['y'],seed['camera'],seed['source_clock'],seed['source_selector'],seed['native_state'],seed['native_Y_speed'])==(2443,112,2364,21,0,0,0)
    assert row['jump_ready']and not row['edge_missing']and seed['foot'][1]['solid']
    missed=[r for r in rows if r['Main']in[3862,3863]]
    assert len(missed)==2 and all(r['support']['x']==2445 and r['support']['native_state']==2 and r['edge_missing']and not r['jump_ready']for r in missed)
    assert all(r['support']['x']!=2444 for r in rows)
    _,b,layout,route=L.bundle();rom=O/'combined-current-landing.nes';b['raw']=rom.read_bytes();assert P.sha(b['raw'])==PIN
    core=P.P.labels(L.B/'component.lbl');native=N.NesMPU;cases=[]
    for identity in[0,1]:
        m=Q.fresh(b,route,identity);L.E.main_fields(m);actor=0x42 if identity else 0x2e
        x,y,camera=seed['x'],seed['y'],seed['camera'];right=camera+255
        N.put(m,Player_X_Position=x&255,Player_PageLoc=x>>8,Player_Y_Position=y,
            ScreenLeft_X_Pos=camera&255,ScreenLeft_PageLoc=camera>>8,
            ScreenRight_X_Pos=right&255,ScreenRight_PageLoc=right>>8,
            Player_Pos_ForScroll=x-camera,PlayerSize=1,PlayerStatus=1,Player_State=0,Player_Y_Speed=0)
        for col in terrain:
            for cell in col['rows']:
                wx,wy=col['x'],cell['y'];name='Block_Buffer_2'if(wx//256)&1 else'Block_Buffer_1'
                m[address(b,name)+((wy-32)//16)*16+(wx%256)//16]=cell['tile']
        for left,right,top in[(2480,2496,144),(2496,2512,160),(2512,2528,176),(2528,2544,192)]:
            for wx in range(left,right,16):
                name='Block_Buffer_2'if(wx//256)&1 else'Block_Buffer_1'
                for wy in range(top,208,16):m[address(b,name)+((wy-32)//16)*16+(wx%256)//16]=97
        def solid(wx,wy):
            if not 32<=wy<240:return False
            name='Block_Buffer_2'if(wx//256)&1 else'Block_Buffer_1'
            return bool(m[address(b,name)+((wy-32)//16)*16+(wx%256)//16])
        m.ram[2][actor+3]=seed['source_selector'];m.ram[2][actor+9]=0
        m.ram[2][0x301]=row['previous_source_held'];m.ram[2][0x1f]=seed['source_clock']
        assert solid(x+4,y+32)and not solid(x+5,y+32)and solid(x+1,y+32)
        epoch=-1;jumps=[];decisions=[];pulse=0;minimum=y
        class Trace(native):
            def step(self):
                if self.memory.rawtags[1]==3 and self.pc==core['BbOriginal_D36B']:
                    wx=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc');wy=N.get(m,'Player_Y_Position')
                    event=dict(epoch=epoch+1,x=wx,y=wy,native_state=N.get(m,'Player_State'),native_DY=N.get(m,'Player_Y_Speed'),
                        left=solid(wx+1,wy+32),right=solid(wx+14,wy+32),held=m.ram[2][actor+1],bubble_marker=m.ram[2][actor+9])
                    assert event['native_state']==0 and(event['left']or event['right'])and event['held']&128 and not event['bubble_marker'],event
                    jumps.append(event)
                return native.step(self)
        N.NesMPU=Trace
        try:
            for epoch in range(160):
                wx=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc');wy=N.get(m,'Player_Y_Position')
                supported=N.get(m,'Player_State')==0 and N.get(m,'Player_Y_Speed')==0 and(solid(wx+1,wy+32)or solid(wx+14,wy+32))
                need=solid(wx+20,wy+31)or not solid(wx+5,wy+32)
                pulse=pulse+1 if supported and m.ram[2][actor+3]in[0,2,3]and need else 0
                keys=1|(128 if 0<pulse<=3 else 0)
                if keys&128:decisions.append(dict(epoch=epoch+1,x=wx,y=wy,native_state=N.get(m,'Player_State'),keys=keys))
                N.put(m,FrameCounter=epoch&255,SavedJoypadBits=keys,SavedJoypad1Bits=keys,VRAM_Buffer1_Offset=0)
                N.invoke(m,'GameCoreRoutine',x=0,y=0)
                wx=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc');wy=N.get(m,'Player_Y_Position');minimum=min(minimum,wy)
                assert not m.ram[2][actor+3]&128 and N.get(m,'NumberofLives')==2
                if wx>=2488 and N.get(m,'Player_State')==0:break
                if 2448<=wx<2480 and wy>192:break
        finally:N.NesMPU=native
        assert 1<=len(jumps)<=2 and jumps[0]['x']==2443 and jumps[0]['epoch']==1,(identity,jumps)
        assert wx>=2488 and N.get(m,'Player_State')==0,(identity,wx,wy,jumps)
        cases.append(dict(identity=identity,seed=seed,actual_original_jumps=jumps,controller_A_requests=decisions,
            epochs=epoch+1,final_x=wx,final_y=wy,final_native_state=N.get(m,'Player_State'),minimum_y=minimum,lives=2))
    out=dict(passed=True,native=False,ROM_written=False,ROM_sha256=PIN,cases=cases,
        actual_cause='Actualv34 walks odd2px positions. At2443 native0/DY0/source0/leftfoottrue but4pxprobe stillsees97. Next2445 edgeisclear butnativeState2; native0 gate correctlyrejects it. No2444 exists. Source2 conjecture disproven; source remains0.',
        controller_change='Only final-pit horizontal lookahead4to5: actualreachable2443 has5pxprobe inpit whileleftfootremainsreal. Native0/DY0/Yhigh1/realfoot and physicalD36B guards staystrict. No newsource, physics, resources or helper.',
        scope='Bothidentity legal native arena initializedfrom actual2443/camera2364/sourceclock21 snapshot and capturedterrain plus sourcefarbank. ActualGameCore consumes genuineRight+A; atmost2originalD36B entries allnative0/realfoot/A/marker0 and supportedfarlanding. Actualcold/fullstage successor remainsrequired.',
        bindings={str(p.relative_to(R)):P.sha(p.read_bytes())for p in[Path(__file__),archive,rom,O/'combined-current-landing.json']})
    dst=O/'reachable-pit-takeoff-v36-CPU.json';assert not dst.exists();dst.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(passed=True,cases=[{k:c[k]for k in['identity','final_x','final_y','epochs','actual_original_jumps']}for c in cases])))


if __name__=='__main__':main()
