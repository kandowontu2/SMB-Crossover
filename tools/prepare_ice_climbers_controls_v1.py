"""Finite actual-compiled leaf controls for new Popo/Nana, no native emulator.

Direct native leaves and real shared renderer/damage/publisher are executed.
Typed CPU arenas are not physical acquisition, a whole level, or NMI timing.
"""
from pathlib import Path
import argparse,hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from check_tmnt_render_oa import Memory,address,location
from link_pit_rygar_sophia_audit_cpu import scoped_load,Arena
from samus_hud_icon_controls_v1 import execute,pixel
import prepare_ice_climbers_assets_v1 as source
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def qnew(b,v=0,mode=1):
    q=Arena(b,20);q.put(IcVariant=v,CrossoverBehaviorVersion=mode,Player_State=0,TimerControl=0,DisableScreenFlag=0)
    q.invoke('IcEnsure');return q
def movement(q,buttons):
    q.put(SavedJoypadBits=buttons,A_B_Buttons=buttons&192)
    return q.invoke('IcMovement')[0]
def original_call(prg,m,pc,x=0,y=0):
    from verify_native_relocation import NesMPU
    m[0xc000:]=prg;c=NesMPU(memory=m,pc=pc);c.x=x;c.y=y;c.sp=253;c.stPushWord(0x5aff)
    for _ in range(3000):
        if c.pc==0x5b00:break
        c.step()
    assert c.pc==0x5b00 and c.sp==253
    return c
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--rom',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    proof=dict(passed=False,source_only=True,native_run=False,ROM_sha256=sha(a.rom),scope=__doc__)
    try:
        b=scoped_load(a.rom)
        for n,v in [('IcVariant',0x5fec),('IcReady',0x5f80),('IcPower',0x5f84),('IcPrevious',0x5c00)]:assert address(b,n)==v
        assert (location(b,'IcMovement')-16)//8192==62 and (location(b,'IcArtStart')-16)//8192==70
        assert address(b,'IcGlobalInit')>=0xa2b7 and address(b,'IcArtStart')>=0xc380
        raw=b['raw'];cb=16+128*8192
        assert raw[cb+712*1024:cb+716*1024]==(R/'chr/characters/ice-climbers.chr').read_bytes()
        # Real original complete renderer masks vs the actual linked records/CHR.
        prg=source.original();art=[]
        for variant,pose,face in itertools.product([0,1],range(15),[1,2]):
            i=variant*30+pose*2+(face==2)
            lo=raw[location(b,'IcPoseLo')+i];hi=raw[location(b,'IcPoseHi')+i];ptr=lo+256*hi
            at=16+70*8192+ptr%8192;rec=raw[at:at+raw[at]+1]
            page=712+raw[location(b,'IcPosePage')+i];actual={}
            for j in range(1,len(rec),4):
                tile,attr,dy,dx=rec[j:j+4];dx=dx-256 if dx&128 else dx;dy=dy-256 if dy&128 else dy
                for y in range(16):
                    for x in range(8):
                        v=pixel(raw,page,tile,attr,x,y)
                        if v:actual[x+dx,y+dy-8]=v
            expected,parts,cycles=source.render(prg,variant,pose,face)
            assert actual==expected,(variant,pose,face)
            q=qnew(b,variant);q.put(PlayerFacingDir=face);q.invoke('IcSetPose',x=pose);assert q.get('SmPosePtr')+256*q.get('SmPosePtr',1)==ptr
            q.invoke('IcDraw');assert q.get('SmChrBank')==page%256
            q.put(R0=lo,R1=hi,R3=0,R4=100,R5=0,R6=100,R7=1,CurrentOAMOffset=0)
            q.invoke('MetaspriteRenderLoop');assert q.get('CurrentOAMOffset')==rec[0]
            art.append(dict(variant=variant,pose=pose,face=face,physical_page=page,parts=rec[0]//4,opaque_pixels=len(actual)))
        proof['art']=art
        motion=[]
        for variant,mode,face in itertools.product([0,1],[0,1],[1,2]):
            q=qnew(b,variant,mode);start=q.get('Player_X_Position')+256*q.get('Player_PageLoc')
            for _ in range(24):movement(q,face)
            end=q.get('Player_X_Position')+256*q.get('Player_PageLoc');assert abs(end-start)==27,(face,end-start)
            paths=[]
            for held in [False,True]:
                q=qnew(b,variant,mode)
                for _ in range(24):movement(q,face)
                y0=q.get('Player_Y_Position');ys=[];xs=[]
                for tick in range(70):
                    buttons=face|(128 if tick==0 or held else 0)
                    movement(q,buttons);ys.append(q.get('Player_Y_Position'));xs.append(q.get('Player_X_Position')+256*q.get('Player_PageLoc'))
                    if tick>10 and q.get('Player_Y_Position')>=y0:break
                assert y0-min(ys)>=64,(variant,mode,face,ys)
                paths.append(ys)
            assert paths[0]==paths[1],'Fixed native jump arc cannot be A-release shortened'
            q=qnew(b,variant,mode)
            movement(q,face|128);assert q.get('IcMoveDir')==face
            movement(q,3-face);assert q.get('IcMoveDir')==face,'Established native air direction cannot reverse'
            c,_=q.invoke('IcStompPolicy');assert bool(c.p&1)==(mode==0)
            motion.append(dict(variant=variant,mode=mode,face=face,walk24_delta=end-start,jump_rise=y0-min(paths[0]),arc_updates=len(paths[0]),fixed_release_arc=True))
        proof['movement']=motion
        upgrades=[]
        for variant,mode in itertools.product([0,1],[0,1]):
            q=qnew(b,variant,mode)
            for food,want in [(0,1),(1,2),(0,2),(1,2)]:
                c,_=q.invoke('IcPickup',a=food);assert c.p&1 and q.get('IcPower')==want and q.get('PlayerStatus')==want
            old=q.get('IcPower');c,_=q.invoke('IcPickup',a=2);assert not c.p&1 and q.get('IcPower')==old
            q.put(NumberofLives=5);q.invoke('IcEnsure');assert q.get('IcPower')==2
            q.put(IcLife=255,NumberofLives=0);q.invoke('IcEnsure');assert q.get('IcPower')==2
            q.put(IcLife=2,NumberofLives=1);q.invoke('IcEnsure');assert q.get('IcPower')==0
            q.invoke('IcFullPower');q.invoke('IcInjuryStart');assert q.get('IcPower')==1 and q.get('IcHurt')==90
            q.invoke('IcInjuryStart');assert q.get('IcPower')==1,'Natural protection must prevent repeat loss'
            for _ in range(90):movement(q,0)
            assert q.get('IcHurt')==0
            q.invoke('IcInjuryStart');assert q.get('IcPower')==0
            upgrades.append(dict(variant=variant,mode=mode,food_consumers=4,real_lives_writer_scope='Controlled complete Ensure consumer states, not native earned1Up',protection_ticks=90))
        proof['upgrades']=upgrades
        # Actual20-update swing, source strike age9, facing and generic damage.
        combat=[]
        for variant,mode,face,power in itertools.product([0,1],[0,1],[1,2],[0,2]):
            q=qnew(b,variant,mode);q.put(IcPower=power,PlayerFacingDir=face)
            px=q.get('Player_X_Position');tx=px+(20 if face==1 else-12)
            for n,v in [('Enemy_Flag',1),('Enemy_ID',6),('Enemy_State',0),('Enemy_X_Position',tx&255),('Enemy_PageLoc',q.get('Player_PageLoc')+(tx//256)),('Enemy_Y_Position',q.get('Player_Y_Position')+4),('Enemy_Y_HighPos',1),('MmEnemyHealthLo',244),('MmEnemyHealthHi',1),('EnemyOffscrBitsMasked',0)]:q.set(n,v,0)
            hits=[];last=500
            for tick in range(1,22):
                movement(q,64);q.invoke('IcWeapons');hp=q.get('MmEnemyHealthLo')+256*q.get('MmEnemyHealthHi')
                if hp!=last:hits.append([tick,last,hp]);last=hp
            assert hits and hits[0][0]==9,(variant,mode,face,power,hits)
            assert hits[0][1]-hits[0][2]==(200 if power==2 else 100),hits
            assert q.get('MmBulletType')==0 and q.get('IcMoveDir')==0
            combat.append(dict(variant=variant,mode=mode,face=face,power=power,hits=hits))
        proof['combat']=combat
        # Actual hardware IRQ across every reachable new drawing gate boundary.
        irq=[]
        for caller in ['IcMovement','IcDraw','IcPalette']:
            q=qnew(b);q.put(SavedJoypadBits=129,IcPaletteAck=255)
            q.m.page(1,62);q.set('CurrentBank',190);image=list(q.m);banks=q.m.banks[:]
            def fresh():
                m=Memory(b);list.__setitem__(m,slice(None),image);m.banks=banks[:];return m
            m=fresh();c,trace=execute(b,m,caller,record=True)
            # New source entries, direct C-publication stores, and full-call joins.
            keys=sorted(set(k for k in trace if k[1]==62 and address(b,caller)<=k[0]<address(b,caller)+40))
            def state(m,c):return([c.a,c.x,c.y,c.p&207,c.sp],bytes(m[:256]+m[512:2048]+m[0x5c00:0x6000]+m[0x6000:0x8000]),m.banks,[m[address(b,n)+i]for n,i in [('NextBank_SMC',1),('SafecallA_SMC',1),('SafereturnA_SMC',1),('FarcallJmpTarget_SMC',1),('FarcallJmpTarget_SMC',2)]])
            want=state(m,c)
            for k in keys:
                mm=fresh();cc,_=execute(b,mm,caller,inject=k);assert state(mm,cc)==want,(caller,k)
            irq.append(dict(caller=caller,boundaries=len(keys)))
        proof['IRQ']=irq
        proof.update(passed=True,limitations=['Direct assembled source components only; live menu/dispatch or whole1-1 not asserted by this tool.','Food and health tests exercise native consumer with typed CPU input; no native earned pickup claim.','Original jump0428 is explicit approved SMB64px terrain adaptation; original03A8 remains authenticated.','Native rendering deadlines/8sprite crowding/audio and actual controller route require ROOT native qualification.'])
    except Exception as e:
        proof.update(error=str(e),traceback=traceback.format_exc())
    proof['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),a.rom,a.rom.with_suffix('.dbg'),R/'tools/prepare_ice_climbers_assets_v1.py',*sorted((R/'src').glob('ice_climbers*')),*sorted((R/'chr/characters').glob('ice-climbers*'))]}
    a.output.write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(passed=proof['passed'],output=str(a.output),error=proof.get('error'))));assert proof['passed']
if __name__=='__main__':main()
