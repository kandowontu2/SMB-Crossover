"""Execute private FF point/response code and genuine native block writers.

RAM3 is explicitly preloaded. These are source CPU controls, not installed
hooks, a native emulator run, nor a claim of a complete FF Main integration.
"""
from pathlib import Path
import itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_host_combat_controls_v1 as C
from ff_host_combat_controls_v3 import direct
from check_tmnt_render_oa import address,location
from prepare_ff_current_component_v2 import qualified
O=R/'build/final-fantasy-host-terrain-controls-v2'
P=R/'build/final-fantasy-host-terrain-v3'
put=C.put;get=C.get;setv=C.setv;run=C.run;sha=C.sha


def empty(b):
    m=C.make(b)
    for i in range(address(b,'Block_Buffer_1'),address(b,'Block_Buffer_2')+208):m[i]=0
    put(m,Player_Y_HighPos=1,RgCrouch=0)
    m.writes.clear()
    return m


def cell(b,wx,y):
    base=address(b,'Block_Buffer_1')+(208 if (wx>>8)&1 else 0)+(wx&255)//16
    return base+(y//16)*16-32,base,(y//16)*16-32


def queries(b):
    m=empty(b);rows=[]
    for typ,px,page,y,high in itertools.product(['feet0','feet1','side3','side4','side5','side6'],[0,1,14,15,16,247,250,255],[0,1,255],[0,16,31,32,99,175,200,207,225,239,255],[0,1,2]):
        for i in range(address(b,'Block_Buffer_1'),address(b,'Block_Buffer_2')+208):m[i]=((i*17+31)%254)+1
        put(m,Player_X_Position=px,Player_PageLoc=page,Player_Y_Position=y,Player_Y_HighPos=high,Local_eb=0,R0=0x55,R1=0xa6,RgCrouch=0)
        if typ.startswith('feet'):
            iy=int(typ[-1]);name='FfHostFeet';want_y=iy+1;dx=1 if iy==0 else 14;dy=32
        else:
            iy=int(typ[-1]);name='FfHostSide';want_y=iy;dx=1 if iy<5 else 14;dy=8 if iy&1 else 30
            put(m,R0=2 if iy<5 else 1)
        before=[get(m,n)for n in ['R0','R1','Local_eb','Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos']]
        wx=(page*256+px+dx)&65535;valid=high==1 and 32<=y+dy<240
        at,base,row=cell(b,wx,y+dy);expected=m[at]if valid else 0
        c,tr,_=run(m,name,y=iy)
        assert c.a==expected and c.x==0 and c.y==want_y,(typ,px,page,y,high,c.a,expected,c.x,c.y)
        assert [get(m,n)for n in ['R0','R1','Local_eb','Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos']]==before
        if valid:
            assert [get(m,n)for n in ['R2','R3','R6','R7']]==[row,expected,base&255,base>>8]
        assert get(m,'R4')==((y if typ.startswith('feet')else px)&15)
        rows.append([typ,px,page,y,high,expected])
    return dict(cases=len(rows),actual_cell_tuple_and_world_page=True,caller_R0_R1_Localeb_and_player_unchanged=True,offscreen_wrap_rejected=True)


def boxes(b):
    m=empty(b);rows=[]
    for duck,dx,y,high in itertools.product([0,1],[-280,-16,-15,-14,-13,-1,0,1,120,241,242,254,255,256,300],[0,1,199,224,239,249,250,255],[0,1,2]):
        wx=512+dx
        put(m,Player_X_Position=wx&255,Player_PageLoc=wx>>8,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=2,Player_Y_Position=y,Player_Y_HighPos=high,RgCrouch=duck)
        # Execute the frozen source rectangle API, then independently convert
        # its half-open world rectangle to the native inclusive screen box.
        run(m,'FfCollisionBounds');l,t,r,bot=[get(m,n)for n in ['R0','R1','R2','R3']]
        hidden=high!=1 or y+t>255 or dx+r-1<0 or dx+l>255 or dx<-256 or dx>=256
        expected=[255]*4 if hidden else[max(0,dx+l),y+t,min(255,dx+r-1),min(255,y+bot-1)]
        c,_,_=run(m,'FfHostBox')
        actual=[get(m,'BoundingBox_UL_Corner'),get(m,'BoundingBox_UL_Corner',1),get(m,'BoundingBox_LR_Corner'),get(m,'BoundingBox_LR_Corner',1)]
        assert actual==expected,('source bbox',duck,dx,y,high,actual,expected)
        rows.append([duck,dx,y,high])
    return dict(cases=len(rows),genuine_source_bounds_executed=True,half_open_to_inclusive_exact=True,partial_screen_clip=True)


def head_and_wall(b):
    m=empty(b);heads=[];walls=[]
    solid=0xc1
    assert m[address(b,'MTileAttribute')+solid]&address(b,'MTILE_SOLID')
    for duck,wx,target_y,dy,site in itertools.product([0,1],[1,247,250,255,256,511,65530],[80,144,192],[-5,-3,-1],[8,1,14]):
        for i in range(address(b,'Block_Buffer_1'),address(b,'Block_Buffer_2')+208):m[i]=0
        top=17 if duck else 6
        previous=target_y+16-top
        current=previous+dy
        at,base,row=cell(b,(wx+site)&65535,current+top);m[at]=solid
        put(m,Player_X_Position=wx&255,Player_PageLoc=wx>>8,Player_Y_Position=current,Player_Y_HighPos=1,Player_Y_Speed=dy&255,RgCrouch=duck,FfTerrainPreviousY=previous,FfTerrainFlags=0,R0=0x55,R1=0xa6)
        c,_,_=run(m,'FfHostHead',y=0)
        assert c.a==solid and get(m,'FfTerrainFlags')==1 and get(m,'FfTerrainTargetY')==previous
        assert get(m,'R4')==4 and get(m,'Player_Y_Position')==previous
        assert get(m,'R0')==0x55 and get(m,'R1')==0xa6
        # The native effects have run by this boundary. The source response
        # stops upward motion at the actual cell lower edge, with no X shift.
        put(m,Player_State=2,MmVY=7,MmYFraction=9)
        run(m,'FfHostAfterTerrain')
        assert get(m,'Player_Y_Position')==previous and get(m,'Player_Y_Speed')==1
        assert [get(m,n)for n in ['Player_X_Position','Player_PageLoc']]==[wx&255,wx>>8]
        assert all(get(m,n,i)==0 for n,i in [('MmVY',0),('MmVY',1),('MmYFraction',0),('MmYFraction',1)])
        heads.append([duck,wx,target_y,dy,site])
    for side,blockwx in itertools.product([1,2],[0,16,240,256,272,496,512,65520]):
        wx=(blockwx-12 if side==1 else blockwx+14)&65535
        dx=14 if side==1 else 1
        point=(wx+dx)&65535
        at,base,row=cell(b,point,184)
        put(m,Player_X_Position=wx&255,Player_PageLoc=wx>>8,FfTerrainPage=point>>8,R6=base&255,R7=base>>8,R0=side,Player_CollisionBits=255,Player_X_Scroll=3,MmVX=1,Player_X_Speed=25)
        c,_,_=run(m,'FfHostWall')
        expected=(blockwx-15 if side==1 else blockwx+15)&65535
        actual=get(m,'Player_X_Position')+256*get(m,'Player_PageLoc')
        assert actual==expected and c.p&1,('actual cell wall',side,blockwx,actual,expected)
        assert get(m,'Player_CollisionBits')==255^side
        assert all(get(m,n,i)==0 for n,i in [('MmVX',0),('MmVX',1),('MmVX',2),('MmXFraction',0),('MmXFraction',1),('Player_X_Speed',0),('Player_X_Scroll',0)])
        walls.append([side,blockwx,actual])
    return dict(ceiling_crossings=len(heads),wall_world_page_cases=len(walls),player_never_moved_for_queries=True,exact_post_response=True)


def native_blocks(b):
    native=qualified(C.E.P/'candidate.nes');rows=[]
    physical=(location(native,'NativeRarePlayerHeadCollisionCore')-16)//8192
    for wx,slot,tier in itertools.product([120,247,250,255,256,511],[0,1],[0,2]):
        m=empty(b)
        # Exactly one mushroom/flower question block at the genuine head cell.
        py=151;top=6;point=(wx+8)&65535;at,base,row=cell(b,point,py+top);m[at]=0xc1
        put(m,Player_X_Position=wx&255,Player_PageLoc=wx>>8,Player_Y_Position=py,Player_Y_HighPos=1,Player_Y_Speed=253,PlayerStatus=tier,PlayerSize=0,RgCrouch=0,FfTerrainPreviousY=154,FfTerrainFlags=0,SprDataOffset_Ctrl=slot,BlockBounceTimer=0)
        c,_,_=run(m,'FfHostHead',y=0)
        assert c.a==0xc1 and get(m,'FfTerrainFlags')==1
        touched=(get(m,'R2'),get(m,'R6'),get(m,'R7'))
        c,tr=direct(m,'NativeRarePlayerHeadCollisionCore',a=0xc1,x=0,bank=physical|128,limit=150000)
        actual=[get(m,n,slot)for n in ['Block_X_Position','Block_PageLoc','Block_Y_Position']]
        expected=[point&240,point>>8,144]
        assert actual==expected,('genuine bumped block world origin',wx,slot,tier,actual,expected,touched)
        assert get(m,'Block_State',slot)==0x11 and get(m,'Square1SoundQueue')==address(b,'Sfx_Bump')
        assert get(m,'Player_X_Position')==wx&255 and get(m,'Player_PageLoc')==wx>>8
        spawned=[x for x in range(6)if get(m,'Enemy_Flag',x)and get(m,'Enemy_ID',x)==address(b,'PowerUpObject')]
        assert len(spawned)==1,('actual native powerup spawn',wx,slot,tier,spawned)
        x=spawned[0]
        assert get(m,'Enemy_State',x)==1,('emerging item',x,get(m,'Enemy_State',x))
        rows.append([wx,slot,tier,actual,x])
    return dict(cases=len(rows),genuine_original_native_head_writer=True,stable_block_world_origin=True,real_emerging_powerup=True,rows=rows)


if __name__=='__main__':
    assert not O.exists();O.mkdir()
    h=json.loads((P/'build-proof.json').read_text())
    for p,d in h['bindings'].items():assert sha(p)==d,p
    b=C.bundle(P);checks={};failures={}
    for name,fn in dict(queries=queries,boxes=boxes,head_and_wall=head_and_wall,native_blocks=native_blocks).items():
        try:checks[name]=fn(b);print(json.dumps(dict(group=name,passed=True,checks=checks[name]if name!='native_blocks'else{key:value for key,value in checks[name].items()if key!='rows'})),flush=True)
        except Exception as e:failures[name]=dict(error=repr(e),traceback=traceback.format_exc());print(json.dumps(dict(group=name,passed=False,error=repr(e))),flush=True)
    bindings={**h['bindings'],str((P/'build-proof.json').resolve()):sha(P/'build-proof.json'),str(Path(__file__).resolve()):sha(__file__)}
    report=dict(passed=not failures,status='OFFLINE_REAL_SOURCE_TERRAIN_CONTROLS',image_sha256=sha(P/'ram3.bin'),checks=checks,failures=failures,native=False,actual_hooks_installed=False,bindings=bindings)
    (O/'controls.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(passed=not failures,groups=len(checks),failed=list(failures))),flush=True)
    if failures:raise SystemExit(1)
