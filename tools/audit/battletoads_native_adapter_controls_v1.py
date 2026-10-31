"""Real copied RAM3 boundary CPU controls; no cold/menu/gameplay claim."""
from pathlib import Path
import importlib.util,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import battletoads_current_loader_controls_v1 as L
H=L.H;address=L.address
from verify_native_relocation import NesMPU
O=R/'build/battletoads-native-adapter-v6';J=O/'joint'
spec=importlib.util.spec_from_file_location('bt_original',R/'build/battletoads-native-assets-v1/extract.py')
N=importlib.util.module_from_spec(spec);spec.loader.exec_module(N)
def get(m,n,i=0):
    at=address(m.bundle,n)+i
    return m.ram[3][at&8191]if 0xa000<=at<0xc000 else m[at]
def put(m,n,v,i=0):
    at=address(m.bundle,n)+i
    if 0xa000<=at<0xc000:m.ram[3][at&8191]=v
    else:m[at]=v
def direct(m,name,a=0x55,x=0,y=91,p=0x71):
    m[0x5115]=3;H.put(m,CurrentBank=3)
    c=NesMPU(memory=m,pc=address(m.bundle,name));c.a=a;c.x=x;c.y=y;c.p=p;c.sp=224;c.stPushWord(0x5aff)
    c,low=H.finish(m,c);assert c.sp==224
    return c,low
def row(m,index,**kw):return L.call(m,'BtServiceVeneers',slot=index,**kw)
def seed(b,player=0,variant=0):
    m=L.make(b,CurrentPlayer=player,FmGroups=variant<<5,TimerControl=0,Player_State=0)
    L.call(m,'BtLoad');row(m,15)
    return m
def health(b):
    m=seed(b);count=0
    for slot,hp,timer,p in itertools.product(range(2),range(256),[0,0xc0],[0x30,0xff]):
        n=N.Bus(0);n.put('Level_ID',1);n.put('Objects_Life',hp,slot);n.put('Objects_death_timer',timer,slot)
        n.put('Object_RamSlotID_tmp',slot);n.put('tmp_var_21',slot);n.put('update_ui_flag',13)
        r=n.invoke('loc_0_E056',X=slot,Y=90,P=p)
        put(m,'BtSrc_Level_ID',1);put(m,'BtSrc_Objects_Life',hp,slot);put(m,'BtSrc_Objects_death_timer',timer,slot)
        put(m,'BtSrc_update_ui_flag',13)
        direct(m,'BtApplyDamage18',x=slot,p=p)
        for field in['Objects_Life','Objects_death_timer','Objects_Z_speed','Objects_Z_spd_sub','Obj_anims_timer']:
            assert n.get(field,slot)==get(m,'BtSrc_'+field,slot),('true original HP profile18',slot,hp,timer,p,field,n.get(field,slot),get(m,'BtSrc_'+field,slot))
        assert n.get('update_ui_flag')==get(m,'BtSrc_update_ui_flag')
        count+=1
    food=0
    for slot,hp in itertools.product(range(2),range(48)):
        n=N.Bus(0);n.put('Objects_Linker_ID',slot,4);n.put('Object_RamSlotID_tmp',4);n.put('Objects_X_speed',248,4)
        n.put('Objects_Life',hp,slot);n.put('update_ui_flag',13)
        c=NesMPU(memory=n,pc=N.LABELS['muha_add_life']);c.x=4;c.sp=224
        for _ in range(100):
            if c.pc==N.LABELS['loc_0_CFC6']:break
            c.step()
        else:raise AssertionError('original food boundary')
        put(m,'BtSrc_Objects_Life',hp,slot);put(m,'BtSrc_update_ui_flag',13)
        direct(m,'BtFoodHeal',x=slot)
        assert get(m,'BtSrc_Objects_Life',slot)==n.get('Objects_Life',slot)
        assert get(m,'BtSrc_update_ui_flag')==n.get('update_ui_flag');food+=1
    return dict(original_damage_profile18_pairs=count,original_food_plus8_cap2F_pairs=food,
        scope='Actual original bank0 E056 and muha_add_life CPU consumers; health fields and original zero-vs-underflow death exact. Wrapper contact timing/native defeat remains separate.')
def movement(b):
    rows=[]
    for player,variant in itertools.product(range(2),range(2)):
        m=seed(b,player,variant);H.put(m,DisableScreenFlag=0,NmiDisable=0,Mirror_PPUMASK=30)
        for frame in range(150):
            keys=1 if frame<40 else 0 if frame<50 else 129 if frame<66 else 1 if frame<95 else 2 if frame<125 else 0
            H.put(m,SavedJoypadBits=keys)
            beforebytes=[bytes(x)for x in m.ram[:3]];before=bytes(list.__getitem__(m,slice(3,11)))
            c,low=row(m,0,p=0x71)
            assert(c.a,c.x,c.y,c.sp)==(85,7,91,224)
            assert bytes(list.__getitem__(m,slice(3,11)))==before
            assert[bytes(x)for x in m.ram[:3]]==beforebytes
            assert H.get(m,'Player_X_Position')==((get(m,'BtSrc_Objects_Xpos_L',player)-8)&255)
            native=(H.get(m,'Player_Y_HighPos')-1)*256+H.get(m,'Player_Y_Position')+32
            source=(get(m,'BtSrc_Objects_Ypos_H',player)*256+get(m,'BtSrc_Objects_Ypos_L',player)-get(m,'BtSrc_Objects_Zpos_H',player)*256-get(m,'BtSrc_Objects_Zpos_L',player))&65535
            assert native&65535==source
            rows.append([player,variant,frame,keys,H.get(m,'Player_X_Position'),H.get(m,'Player_Y_Position'),H.get(m,'Player_Y_Speed'),get(m,'BtSrc_player1_obj_wanted_frame',player),low])
            # Explicit flat test support, not installed geometry or native route:
            # a future actual PlayerBGCollision pass is authoritative in Main.
            if H.get(m,'Player_Y_Speed')<128 and H.get(m,'Player_Y_Position')>=160:
                H.put(m,Player_Y_Position=160,Player_Y_HighPos=1,Player_Y_Speed=0,Player_State=0)
        assert any(r[5]<140 for r in rows if r[0]==player and r[1]==variant),'actual source jump'
    return dict(actual_source_row_ticks=len(rows),AXYP_SP_borrowed_R0_R7_foreign_RAM_preserved=True,rows=rows,
        scope='Actual own ROMrow→copied donor integrator/native projection, with explicit flat-support fixture between calls. Not real terrain/fullMain/native gameplay.')
def palettes_render(b):
    rows=[]
    for player,variant,face in itertools.product(range(2),range(2),[0,64]):
        m=seed(b,player,variant);put(m,'BtSrc_Objects_Flags',face,player)
        H.put(m,VRAM_Buffer1_Offset=0,CurrentOAMOffset=0,Player_Rel_XPos=120,Player_Rel_YPos=160,
            ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,Player_SprAttrib=0)
        row(m,26)
        packet=bytes(m[address(b,'VRAM_Buffer1'):address(b,'VRAM_Buffer1')+13])
        shades=bytes([15,10,26]if variant==0 else[15,23,39])
        assert packet==bytes([63,17,3])+shades+bytes([63,21,3,24,40,32,0]),('exact source roles/queue',player,variant,face,list(packet))
        row(m,1);assert m.chr_latches[0]==915
        m[0x5116]=0xa2;H.put(m,CurrentBankC=0xa2)
        row(m,2)
        count=H.get(m,'CurrentOAMOffset');assert count==32,(count,player,variant,face)
        assert m.rawtags[2]==0xa2 and H.get(m,'CurrentBankC')==0xa2
        assert H.get(m,'SmPosePtr')+256*m[address(b,'SmPosePtr')+1]==address(b,'QwEmpty34')
        oam=bytes(m[0x200:0x200+count]);assert all(oam[i]<240 for i in range(0,count,4))
        rows.append(dict(player=player,variant=variant,face=face,packet=list(packet),OAM=list(oam),physical=915))
    return dict(cases=len(rows),actual_kernel_original_source_8_parts=True,source_two_role_queue_universal_untouched=True,rows=rows,
        scope='Native kernel on actually loaded cache/source descriptor, current CHR915. Full native post-shot/actor consumer and live P1 retirement not yet qualified.')
def main():
    out=O/'boundary-controls.json';assert not out.exists();q=dict(passed=False,native=False,checks={})
    try:
        b=H.C.qualified(J/'candidate.nes')
        for name,fn in[('source_health',health),('source_movement',movement),('source_palette_native_kernel',palettes_render)]:
            q['checks'][name]=fn(b);print(name,'PASS',flush=True)
        q['passed']=True
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
    q['bindings']={str(p.resolve()):L.sha(p)for p in[Path(__file__),Path(L.__file__),Path(N.__file__),O/'source-stage.json',J/'candidate.nes',J/'candidate.dbg',J/'bt/api.s',J/'bt/cache.bin',J/'bt/cookie.bin']}
    out.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(passed=q['passed'],checks=list(q['checks']),error=q.get('error'))));assert q['passed'],q.get('error')
if __name__=='__main__':main()
