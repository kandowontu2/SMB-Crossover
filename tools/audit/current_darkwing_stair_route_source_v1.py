"""Finite Arrow-at-stair control after genuine recovery acquisition.

Source CPU typed scene, not an unlogged native Block_Buffer reconstruction.
The second scene preserves the actual earned inventory from the first scene.
"""
from pathlib import Path
import argparse,csv,hashlib,json
from current_darkwing_arrow_route_source_v1 import ROOT,ROM,EXPECTED,scene,world,block,Controller,arrow
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address

sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

class StairController(Controller):
    def buttons(self,q):
        t=block(q,world(q)+32,q.get('Player_Y_Position')-20)
        solid=t not in [0,0x23,0x26,0xc2,0xc3]
        if (self.phase=='route'and world(q)>450 and q.get('Player_State')==0
                and q.get('Player_X_Speed')==0 and solid
                and q.get('DwAdaptor')==2 and q.get('DwGas')>=3):
            self.origin=world(q);self.ground=q.get('Player_Y_Position');self.change(q,'acquire')
        return super().buttons(q)

def control(b):
    q=scene(b);c=Controller();rows=[]
    def tick(bits,stage):
        q.put(SavedJoypadBits=bits);q.invoke('GameLoop')
        rows.append(dict(stage=stage,x=world(q),y=q.get('Player_Y_Position'),state=q.get('Player_State'),gas=q.get('DwGas'),adaptor=q.get('DwAdaptor'),mode=q.get('DwMode'),arrow=arrow(q)))
        assert q.get('GameEngineSubroutine')==8 and q.get('DwHealth')==4
        ptr=address(b,'VRAM_Buffer1');q.put(NmiR0=ptr&255,NmiR1=ptr>>8,VRAM_Buffer_AddrCtrl=0);q.invoke('SamusFreezeUpdateScreen');q.put(VRAM_Buffer1=0,VRAM_Buffer1_Offset=0)
    for i in range(220):
        tick(c.buttons(q),'actual-earned-pipe')
        if world(q)>817:break
    assert q.get('DwAdaptor')==2 and q.get('DwGas')==7 and q.get('DwMode')==1
    earned=dict(adaptor=q.get('DwAdaptor'),gas=q.get('DwGas'),mode=q.get('DwMode'))
    # Disclosed scene boundary: map/position and movement only. No inventory,
    # resources, pickup, shot, input-consumer, health or outcome field is set.
    while any(q.get('RgShotType',i)for i in range(10)):tick(0,'native-shot-expiry')
    q.put(Player_X_Position=177,Player_PageLoc=8,MmOldX=177,Player_Y_Position=176,Player_State=0,
          MmVX=0,Player_X_Speed=0,Player_Y_Speed=0,ScreenLeft_X_Pos=66,ScreenLeft_PageLoc=8,ScreenRight_X_Pos=65,ScreenRight_PageLoc=9)
    for n in ['MmVX','MmVY','MmXFraction','MmYFraction']:
        for i in range(3 if n in ['MmVX','MmVY']else 2):q.set(n,0,i)
    for i in range(416):q.set('Block_Buffer_1',0,i)
    for row in [11,12]:
        for x in range(32):q.set('Block_Buffer_1',0x54,(x//16)*208+row*16+x%16)
    for x in [2240,2256]:
        for row in range(7,11):q.set('Block_Buffer_1',0x61,x//256%2*208+row*16+x%256//16)
    c=StairController();begin=len(rows)
    for i in range(220):
        tick(c.buttons(q),'earned-arrow-stair')
        if world(q)>2289:break
    actual=rows[begin:]
    assert max(r['x']for r in actual)>2289,(actual[-1],c.phase,c.transitions)
    assert any(r['arrow']is not None for r in actual)and any(r['state']==0 and r['y']<176 for r in actual)
    assert q.get('DwGas')==earned['gas']-3 and q.get('DwAdaptor')==earned['adaptor']
    return dict(passed=True,GameLoops=len(rows),earned_before_stair=earned,transitions=c.transitions,rows=rows)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists()and sha(ROM)==EXPECTED
    old=ROOT/'build/verification/compact-ab221e-darkwing-easy-v4';trace=list(csv.DictReader((old/'trace.csv').open(newline='')))
    stationary=[r for r in trace if r['x']=='2225'];rises=[r for i,r in enumerate(trace[1:],1)if r['x']=='2225'and trace[i-1]['state']=='0'and r['state']=='1'and int(r['vy'])>=128]
    assert len(stationary)>4000 and len(rises)>20 and min(int(r['y'])for r in stationary)==125
    files=[Path(__file__),ROM,ROM.with_suffix('.dbg'),ROM.with_suffix('.lbl'),ROOT/'tools/playthroughs/current_roster_darkwing_arrow_v2.lua',ROOT/'tools/playthroughs/current_roster_darkwing_gap_v3.lua',old/'trace.csv',old/'result.json',old/'mega_proto_body_palette_9ea-run.log',ROOT/'build/current-ab221e-darkwing-stairs-actual-v1.png']
    z=dict(passed=True,native_run=False,Lua_executed=False,ROM_sha256=EXPECTED,native_v4_negative=dict(frame=8000,x=2225,stationary_frames=len(stationary),consumed_jump_rises=len(rises),minimum_y=125,geometry='Actual selected RGB:32px valley, next four-cell/64px stair face. No captured native Block_Buffer/DwGas at stall.'),source=control(scoped_load(ROM)),scope=__doc__,limits='Model proves legal toolkit at authored solid stair after real earned recovery; not exact native scene/map, resource availability at frame8000, PPU/cadence or route-clear proof. All original guards/8000 bound remain.',bindings={str(p):sha(p)for p in files})
    a.output.write_text(json.dumps(z,indent=2)+'\n',newline='\n');print(json.dumps(dict(passed=True,path=str(a.output),sha256=sha(a.output),GameLoops=z['source']['GameLoops'],rises=len(rises))))

if __name__=='__main__':main()
