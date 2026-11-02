"""Native profile/clamp consistency and genuine source-lean jump envelope."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import check_hogan_current_bounded_v1 as M
from check_tmnt_render_oa import address,location
from check_excitebike_cold_1101_v1 import bundle
from check_excitebike_host_1101_v1 import fixture,tick,wx
from prepare_excitebike_dispatch_1101_v1 import O,sha,save
from prepare_excitebike_host_1101_v1 import BASE,PIN


def main():
    b=bundle();at=location(b,'BlockBufferAdderData');profile=b['raw'][at+3]
    at=location(b,'BlockBuffer_X_Adder')+profile;xs=list(b['raw'][at:at+7])
    at=location(b,'BlockBuffer_Y_Adder')+profile;ys=list(b['raw'][at:at+7])
    assert xs==[8,2,13,1,1,14,14]and ys==[8,32,32,12,24,12,24]
    seed=M.fresh(b);walls=0;maximum=0
    for boundary in [16,240,256,272,496,512,528,752]:
      for penetration in range(4):
        for side in [1,2]:
            x=boundary-14+penetration if side==1 else boundary-2-penetration
            expected=boundary-15 if side==1 else boundary-1
            m=M.fork(seed);M.put(m,SelectedCharacter=37,Player_X_Position=x&255,Player_PageLoc=x>>8,
                Player_X_Speed=16 if side==1 else 240,R0=side)
            z=M.invoke(m,'SamusStopAtWallBanked',a=37)
            actual=wx(m);distance=abs(actual-x);maximum=max(maximum,distance)
            assert actual==expected and distance<=4 and z['P']&1,(boundary,penetration,side,x,actual,expected)
            # Published side samples and clamped body are exactly one pixel
            # outside the contacted tile on both sides and at page seams.
            assert actual+14==boundary-1 if side==1 else actual+1==boundary
            walls+=1
    m,digest=fixture()
    for f in range(180):tick(m,f,1)
    jumps=[]
    for hold in [0,24,28,36,44,52]:
        n=M.fork(m);minimum=176;crashes=set();grounded=None
        for f in range(180):
            pad=1|(128 if f==0 else 0)|(8 if f<hold else 0)
            tick(n,180+f,pad);minimum=min(minimum,M.get(n,'Player_Y_Position'));crashes.add(n.ram[2][0x98])
            if f>3 and M.get(n,'Player_State')==0 and grounded is None:grounded=f
        assert M.get(n,'Player_Y_Position')==176 and M.get(n,'Player_State')==0,(hold,'landing')
        jumps.append(dict(backlean_updates=hold,rise=176-minimum,first_landing_update=grounded,
                          crash_states=sorted(crashes),final_speed=n.ram[2][0x90]+256*n.ram[2][0x94]))
    controls=[]
    for throttle in [1,65]:
      for prelean in [0,4,8]:
        n,_=fixture()
        for f in range(180):tick(n,f,throttle|(8 if f>=180-prelean else 0))
        initial=dict(speed=n.ram[2][0x90]+256*n.ram[2][0x94],angle=n.ram[2][0xac],lean=n.ram[2][0x5c]&3,heat=n.ram[2][0x3e0])
        minimum=176;crashes=set()
        for f in range(150):
            tick(n,180+f,throttle|(128 if f<8 else 0)|(8 if f<36 else 0))
            minimum=min(minimum,M.get(n,'Player_Y_Position'));crashes.add(n.ram[2][0x98])
        assert M.get(n,'Player_Y_Position')==176 and M.get(n,'Player_State')==0
        controls.append(dict(throttle=throttle,prelean_updates=prelean,launch_input=initial,
                             rise=176-minimum,crash_states=sorted(crashes)))
    q=dict(passed=True,base_ROM_SHA256=PIN,native_terrain_profile=3,X_adders=xs,Y_adders=ys,
           exact_native_wall_cases=walls,max_separation_pixels=maximum,source_lean_jump_envelope=jumps,
           intended_turbo_prelean_controls=controls,
           deliberate_adaptation='Native32px terrain rectangle with matching native1/14 side clamp and2/13 feet. Original Excitebike contact rectangle is not claimed.',
           helpers_added=[],native=False,installed=False,
           scope='Current native clamp consumer instructions at left/right/page seams and original actor/host flat-floor jump progression. No physical level traversal claim.',
           bindings={p.relative_to(R).as_posix():sha(p)for p in [Path(__file__),BASE,O/'host-assembly.json',O/'scene-assembly.json']})
    save('terrain-CPU.json',q);print(json.dumps(q))

if __name__=='__main__':main()
