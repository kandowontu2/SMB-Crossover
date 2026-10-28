"""Bounded actual-CPU qualification of integrated Mac/Doc/Tyson leaves.

Explicit isolated CPU arenas, not earned/native gameplay, IRQ or PPU timing.
Reads a frozen linked ROM/DBG and frozen authored asset manifest; no builds,
game/source edits, emulator launches, source trees or screenshots are created.
"""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
from link_pit_rygar_sophia_audit_cpu import Arena, scoped_load
from check_tmnt_render_oa import address, location

ROOT = Path(__file__).resolve().parents[2]
DEFAULT = 'b5bedafa3ce640408e6e80e753ee6f5789ceb07195946acf5dd0b01bfa487c2e'
TOTAL = [(34,88),(42,96),(28,76)]
START = [(27,71),(33,78),(23,60)]
END = [(12,42),(14,44),(9,30)]
REACH = [18,20,24]
HEIGHT = [(10,38),(12,38),(12,42)]
COST = [1,1,2]
REST = [30,24,36]
NAMES = ['mac','doc','tyson']


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def seed(bundle, variant, face=1):
    q=Arena(bundle,15)
    q.put(MacVariant=variant,LmReady=0x4d,LmLife=3,NumberofLives=3,
          AreaPointer=0x25,AreaType=1,AreaAddrsLOffset=5,LmArea=0x25,
          WorldNumber=0,LmWorld=0,GameEngineSubroutine=8,TimerControl=0,
          LmHealth=96,LmHearts=20,LmStars=3,LmPalette=1,
          Player_X_Position=120,Player_PageLoc=1,Player_Y_Position=160,
          Player_Y_HighPos=1,PlayerFacingDir=face,Player_CollisionBits=3,
          Player_State=0,PlayerSize=0,PlayerStatus=1,OperMode=1,
          ScreenRight_PageLoc=1,ScreenRight_X_Pos=255)
    return q


def read(bundle, name, n=1):
    at=location(bundle,name)
    return bundle['raw'][at:at+n]


def pointer(q):
    return q.get('SmPosePtr')+256*q.get('SmPosePtr',1)


def expected_frame(manifest,variant,pose,age,super_,walk,vy):
    v=min(variant,0) if variant>=3 else variant
    if pose==10:return 48+v
    if pose>=10:pose=0
    family=manifest['family_frames'][NAMES[v]]
    if pose>=8:
        key='duckpunch' if END[v][super_]<=age<START[v][super_] else 'duck'
    elif pose in (4,5):
        key=('uppercut' if super_ else 'punch') if END[v][super_]<=age<START[v][super_] else ('windup' if age>=START[v][super_] else 'idle')
    elif pose==7:key='hurt'
    elif pose==6:key='jump0' if vy&128 else 'jump1'
    elif pose==3:key='duck'
    elif pose==0:key='idle'
    else:key='walk0' if walk<14 else 'walk1' if walk<27 else 'walk2'
    return family[key]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--expected-sha256',default=DEFAULT)
    p.add_argument('--baseline',type=Path,default=ROOT/'build/roster-expansion-traversal-v1.nes')
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();assert not args.output.exists()
    assert sha(args.rom)==args.expected_sha256
    manifest_path=ROOT/'chr/characters/mac-roster-manifest.json'
    manifest=json.loads(manifest_path.read_text())
    inputs=[Path(__file__),args.rom,args.rom.with_suffix('.dbg'),args.rom.with_suffix('.lbl'),
            args.baseline,args.baseline.with_suffix('.dbg'),manifest_path,
            ROOT/'build/mac_roster_handoff.json',ROOT/'src/mac_roster.s',
            ROOT/'src/mac_roster_data.inc',ROOT/'chr/characters/mac-roster.chr',
            ROOT/'tools/audit/link_pit_rygar_sophia_audit_cpu.py',
            ROOT/'tools/audit/check_tmnt_render_oa.py',ROOT/'tools/audit/verify_native_relocation.py']
    before={str(q):sha(q) for q in inputs}
    proof=dict(passed=False,source_only=True,native_run=False,scope=__doc__,bindings=before,checks={})
    try:
        b=scoped_load(args.rom);old=scoped_load(args.baseline)
        assert read(b,'MacRosterNormalTotal',3)==bytes(x[0] for x in TOTAL)
        assert read(b,'MacRosterSuperTotal',3)==bytes(x[1] for x in TOTAL)
        for name,vals in [('MacRosterHeartCost',COST),('MacRosterPunchReach',REACH),('MacRosterRestPeriod',REST)]:
            assert list(read(b,name,3))==vals
        # The *integrated* CHR must be exactly the frozen delivered asset.
        asset=(ROOT/'chr/characters/mac-roster.chr').read_bytes()
        assert b['raw'][16+128*8192+668*1024:16+128*8192+708*1024]==asset
        proof['checks']['authentic_asset_CHR']=dict(bytes=len(asset),exact=True)
        admissions=0
        tyson_negative=None
        for variant,hearts,stars,super_,face in itertools.product(range(3),[0,1,2,20],[0,1,3],[0,1],[1,2]):
            q=seed(b,variant,face)
            q.put(LmHearts=hearts,LmStars=stars,LmFresh=64,SavedJoypadBits=64+(8 if super_ else 0),
                  LmHits=0xaa,LmBlockHit=0xbb,LmSuper=0x55)
            c,_=q.invoke('LmWeaponsGate')
            accepted=hearts>=COST[variant] and (not super_ or stars>0)
            assert q.get('LmAttack')==(TOTAL[variant][super_] if accepted else 0)
            assert q.get('LmHearts')==hearts-(COST[variant] if accepted else 0)
            assert q.get('LmStars')==stars-(1 if accepted and super_ else 0)
            assert c.sp==253
            if variant==2 and hearts==1 and super_ and stars==3:
                tyson_negative=dict(hearts=q.get('LmHearts'),stars=q.get('LmStars'),attack=q.get('LmAttack'))
            admissions+=1
        proof['checks']['real_weapon_admission']=dict(cases=admissions,Tyson_one_heart_super_rejected_no_star_debit=tyson_negative)
        blocked=0
        for variant,field in itertools.product(range(3),['TimerControl','MmDeathFlag','LmHurt','GameEngineSubroutine','LmFresh']):
            q=seed(b,variant);q.put(LmFresh=64,SavedJoypadBits=72)
            q.set(field,9 if field=='GameEngineSubroutine' else 0 if field=='LmFresh' else 1)
            q.invoke('LmWeaponsGate')
            assert [q.get(n) for n in ('LmAttack','LmHearts','LmStars')]==[0,20,3]
            blocked+=1
        proof['checks']['actual_rejected_attack_paths']=blocked
        # Literal remaining-age windows, through full real hit/block caller.
        windows=0
        for variant,super_,face,age,crouch in itertools.product(range(3),[0,1],[1,2],range(256),[0,4]):
            q=seed(b,variant,face)
            q.put(LmAttack=age,LmSuper=super_,RgCrouch=crouch,LmFresh=0)
            initial=[31,32,33,34,35]
            for name,value in zip(['LmRectX','LmRectPage','LmRectY','LmRectW','LmRectH'],initial):q.set(name,value)
            c,_=q.invoke('LmWeaponsGate')
            active=END[variant][super_]<=age<START[variant][super_]
            got=[q.get(n) for n in ['LmRectX','LmRectPage','LmRectY','LmRectW','LmRectH']]
            if active:
                world=376+(13 if face==1 else 2-REACH[variant])
                want=[world&255,world>>8,(140 if super_ else 165+(16 if crouch else 0)),REACH[variant],HEIGHT[variant][super_]]
                assert got==want,(variant,super_,face,age,crouch,got,want)
            else:assert got==initial,(variant,super_,face,age,crouch,got)
            assert q.get('LmHearts')==20 and q.get('LmStars')==3 and c.sp==253
            windows+=1
        proof['checks']['complete_weapon_windows_and_rectangles']=windows
        # Actual enemy-hit routine via full gate, page-crossing and strict
        # left/right reach boundaries; no substituted hit or resource result.
        contacts=0
        for variant,super_,face,xpos in itertools.product(range(3),[0,1],[1,2],[1,120,250]):
            world=256+xpos+(13 if face==1 else 2-REACH[variant])
            for delta in [-16,-15,-14,-1,0,REACH[variant]-1,REACH[variant],REACH[variant]+1]:
                q=seed(b,variant,face)
                q.put(Player_X_Position=xpos,LmHearts=5,LmAttack=END[variant][super_],LmSuper=super_)
                ex=(world+delta)&65535
                for name,value in [('Enemy_Flag',1),('Enemy_ID',6),('Enemy_State',0),
                    ('Enemy_X_Position',ex&255),('Enemy_PageLoc',ex>>8),
                    ('Enemy_Y_Position',140 if super_ else 165),('Enemy_Y_HighPos',1)]:q.set(name,value,3)
                c,_=q.invoke('LmWeaponsGate')
                # Native enemy width16 includes its x+15 pixel: touching the
                # rectangle's left pixel at delta-15 is a genuine overlap.
                # The v1 strict-> oracle negative remains unchanged.
                hit=-15<=delta<REACH[variant]
                assert bool(q.get('LmHits')&8)==hit,(variant,super_,face,xpos,delta,q.get('LmHits'))
                assert q.get('LmHearts')==5+int(hit) and c.sp==253
                contacts+=1
        proof['checks']['real_enemy_contact_reach_and_refund']=contacts
        # Execute real movement, not a synthetic DEC, for all attack ticks and
        # each variant's zero-heart crouch recovery. Intentional CPU setup only.
        timelines=[]
        for variant,super_ in itertools.product(range(3),[0,1]):
            q=seed(b,variant);q.put(LmFresh=64,SavedJoypadBits=64+8*super_)
            q.invoke('LmWeaponsGate')
            remaining=[]
            q.put(SavedJoypadBits=0)
            for tick in range(1,TOTAL[variant][super_]+1):
                q.invoke('LmMovementGate');q.invoke('LmWeaponsGate')
                assert q.get('LmAttack')==TOTAL[variant][super_]-tick
                remaining.append(q.get('LmAttack'))
            timelines.append(dict(variant=variant,super=super_,real_movement_ticks=len(remaining)))
        proof['checks']['real_attack_tick_timelines']=timelines
        rests=[]
        for variant in range(3):
            q=seed(b,variant);q.put(LmHearts=0,SavedJoypadBits=4)
            for tick in range(1,REST[variant]+1):
                q.invoke('LmMovementGate')
                assert q.get('LmHearts')==(20 if tick==REST[variant] else 0),(variant,tick,q.get('LmHearts'),q.get('LmRest'))
            assert q.get('LmRest')==0
            rests.append(dict(variant=variant,crouched_zero_heart_updates=REST[variant],restored_hearts=20))
        proof['checks']['actual_zero_heart_recovery']=rests
        # Real LmSetPose entry and actual C94 record identity for all poses,
        # active/windup/recovery thresholds, facing, walk phase, rising/falling.
        poses=0
        for variant,pose,face,super_,walk,vy in itertools.product(range(3),range(11),[1,2],[0,1],[0,14,27,39],[0,255]):
            for age in sorted({0,END[variant][super_]-1,END[variant][super_],START[variant][super_]-1,START[variant][super_],TOTAL[variant][super_]}):
                q=seed(b,variant,face);q.put(LmAttack=age,LmSuper=super_,LmWalk=walk,Player_Y_Speed=vy)
                c,_=q.invoke('LmSetPose',x=pose,y=0xa7)
                frame=expected_frame(manifest,variant,pose,age,super_,walk,vy)
                name=f'MacRosterFrame{frame}{"R" if face==1 else "L"}'
                assert pointer(q)==address(b,name),(variant,pose,age,frame,hex(pointer(q)),name)
                assert c.x==pose and c.y==0xa7 and c.sp==253
                assert q.get('SmChrBank')==manifest['frames'][frame]['page']&255
                assert q.m.banks[2]==94 and q.get('ObjectMetasprite')==address(b,'METASPRITE_SAMUS_BODY')
                header=b['raw'][location(b,name)]
                assert header==4*len(manifest['frames'][frame]['parts']) and header<=36
                poses+=1
        proof['checks']['real_SetPose_record_mapping']=poses
        portraits=[]
        for variant,face in itertools.product(range(3),[1,2]):
            q=seed(b,variant,face);c,_=q.invoke('LmPortraitGate')
            frame=48+variant
            assert pointer(q)==address(b,f'MacRosterFrame{frame}{"R" if face==1 else "L"}')
            assert q.get('SmChrBank')==manifest['frames'][frame]['page']&255
            assert q.m.banks[2]==94 and c.sp==253
            portraits.append(dict(variant=variant,face=face,frame=frame,parts=len(manifest['frames'][frame]['parts'])))
        proof['checks']['real_PortraitGate']=portraits
        # Foreign pure fallback: complete returned CPU and complete nonstack
        # application image. Consumed stack/SMC page is explicitly unclaimed.
        foreign=0
        for char in [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,16,17,18,19,20]:
            pair=[seed(x,0) for x in (old,b)]
            for q in pair:q.put(SelectedCharacter=char,TimerControl=1)
            result=[q.invoke('LmWeaponsGate',a=0x69,x=3,y=0x85)[0] for q in pair]
            assert [(c.a,c.x,c.y,c.p,c.sp) for c in result][0]==[(c.a,c.x,c.y,c.p,c.sp) for c in result][1],char
            for lo,hi in [(0,0x100),(0x200,0x8000)]:
                assert pair[0].m[lo:hi]==pair[1].m[lo:hi],('foreign RAM',char)
            assert pair[0].m.banks==pair[1].m.banks
            foreign+=1
        proof['checks']['foreign_full_weapon_fallback']=dict(cases=foreign,scope='Exact AXYP/SP/nonstackRAM/banks with TimerControl1; no live-shot or IRQ/NMI claim')
        assert all(sha(q)==digest for q,digest in before.items()),'Bound input changed'
        proof['passed']=True
        proof['limits']='Isolated CPU arenas with explicit state inputs, not earned pickups/native sprite capacity/flicker/palette-deadline/PPU/audio/IRQ/gameplay acceptance. Asset provenance/adaptation distinctions remain frozen in original handoff.'
    except Exception as error:
        proof['error']=repr(error)
        raise
    finally:
        args.output.write_text(json.dumps(proof,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(passed=proof['passed'],checks=proof['checks'],proof_sha256=sha(args.output))))


if __name__=='__main__':main()
