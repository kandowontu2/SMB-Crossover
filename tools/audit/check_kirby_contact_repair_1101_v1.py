"""CPU differential of a funded Kirby-only inhale/copied-shell repair."""
from pathlib import Path
import hashlib,itertools,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from check_kirby_inhale_shell_fix_1101_v1 import Proof,baseline
O=R/'build/kirby-inhale-shell-fix-1101-v1';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def families(old,new):
    count=0;digest=hashlib.sha256()
    for kind,x,flag,state,flags in itertools.product(range(256),[0,5,6],[0,1,128],[0,1,2,32],[0x31,0xf9]):
        results=[]
        for p in[old,new]:
            m=p.make();p.enemy(m,x,356,184,kind=kind);m[p.s['Enemy_Flag']+x]=flag;m[p.s['Enemy_State']+x]=state;m.writes=[]
            c,_=p.run(m,'KbFamilyForEnemy',x=x,y=19,p=flags);results.append((c.a,c.x,c.y,c.p&0xcf));assert all(0x100<=a<0x200 for a in m.writes)
        assert results[0]==results[1],(kind,x,flag,state,flags,results);digest.update(bytes(results[0]));count+=1
    return dict(passed=True,exact_AXY_real_flags_pairs=count,IDs=256,all_native_families_and_upper_zero_entries=True,digest=digest.hexdigest())

def inhale(old,new):
    count=changed=0
    for age,action,variant,B,facing,dx,dy,high in itertools.product([0,1,8],[0,1],[0,1],[0,64],[1,2],[-1,0,12,56,57],[-13,0,13],[0,1,2]):
        results=[]
        for p in[old,new]:
            m=p.make();p.enemy(m,0,0x150+dx*(1 if facing==1 else-1),184+dy,high)
            for n,v in dict(Player_X_Position=0x50,Player_PageLoc=1,KbAction=action,KbActionAge=age,KbVariant=variant,SavedJoypadBits=B,PlayerFacingDir=facing).items():m[p.s[n]]=v
            c,_=p.run(m,'KbBodyContact');results.append(bool(c.p&1))
        expected=action==1 and variant==0 and B==64 and 0<=dx<=56 and dy==0 and high==1
        assert results[1]==expected,(age,action,variant,B,facing,dx,dy,high,results)
        assert results[0]==(expected and age==0)
        changed+=results[0]!=results[1];count+=1
    # A genuine source KbWeapons update (with exact other-bank KbInputs)
    # opens the mouth before the subsequent native enemy-contact phase.
    # This proves source sequencing; it does not emulate native Main/ISR.
    sequences=[]
    for p in[old,new]:
        m=p.make();p.enemy(m,0,356,184)
        for n,v in dict(KbAction=0,KbActionAge=0,GameEngineSubroutine=8,TimerControl=0,KbInputFrame=0,KbPrevious=0,FrameCounter=1).items():m[p.s[n]]=v
        contacts=[];ages=[]
        for frame in range(1,10):
            m[p.s['FrameCounter']]=frame;p.run(m,'KbWeapons');ages.append(m[p.s['KbActionAge']]);c,_=p.run(m,'KbBodyContact');contacts.append(bool(c.p&1))
        assert ages==list(range(8,-1,-1)),ages
        assert m[p.s['KbMouth']]==0 and m[p.s['Enemy_X_Position']]==98
        sequences.append(dict(mode=p.mode,first_fresh_B_and_held9_contact_C=contacts,opening_ages=ages))
    assert sequences[0]['first_fresh_B_and_held9_contact_C']==[False]*8+[True]
    assert sequences[1]['first_fresh_B_and_held9_contact_C']==[True]*9
    # Family hazards, dying Goomba and controller aliases remain ordinary.
    denied=0
    for kind,flag,state in[(0x1b,1,0),(0x2d,1,0),(6,1,2),(6,128,0),(6,1,32),(0xff,1,0)]:
        for p in[old,new]:
            m=p.make();p.enemy(m,0,356,184,kind=kind);m[p.s['Enemy_Flag']]=flag;m[p.s['Enemy_State']]=state;c,_=p.run(m,'KbBodyContact');assert not(c.p&1);denied+=1
    return dict(passed=True,guard_matrix_cases=count,intended_opening_corrections=changed,hazard_dying_alias_denials=denied,real_source_update_sequences=sequences,ordinary_rear_released_B_Meta_preserved=True,native_Main=False)

def geometry(new):
    table=bytes.fromhex(new.box['bytes']);count=0;digest=hashlib.sha256()
    allowed={new.s[n]for n in['KbTemp','KbTemp2','KbTempX','KbTempPage','KbTempY']}
    for ctrl,world,ey in itertools.product(range(12),[0x100,0x1ff,0x2ff],[0,184,240]):
        left,top,right,bottom=table[ctrl*4:ctrl*4+4]
        xs=[world+left-8,world+left-7,world+left,world+right,world+right+8,world+right+9]
        ys=[ey+top-8,ey+top-7,ey+top,ey+bottom,ey+bottom+8,ey+bottom+9]
        for sx,sy in itertools.product(xs,ys):
            if not(0<=sy<256):continue
            m=new.make();new.enemy(m,0,world,ey);m[0x646]=ctrl
            for n,v in dict(KbSavedSlot=0,KbShotX=sx&255,KbShotPage=sx>>8,KbShotY=sy).items():m[new.s[n]]=v
            m.writes=[];c,_=new.run(m,'KbShellEnemyContact',x=0,y=2)
            expected=(sx+7>=world+left and sx-8<=world+right and sy+7>=ey+top and sy-8<=ey+bottom)
            assert bool(c.p&1)==expected,(ctrl,world,ey,sx,sy,expected,c.p&1)
            assert c.x==0 and all(a in allowed or 0x100<=a<0x200 for a in m.writes)
            count+=1;digest.update(bytes([ctrl,sx&255,sx>>8,sy,c.p&1]))
    rejects=0
    for high,ctrl in itertools.product([0,1,2,255],[0,9,11,12,20,255]):
        if high==1 and ctrl<12:continue
        m=new.make();new.enemy(m,0,356,184,high);m[0x646]=ctrl;m[new.s['KbSavedSlot']]=0;c,_=new.run(m,'KbShellEnemyContact');assert not(c.p&1);rejects+=1
    return dict(passed=True,actual_native_table_CPU=new.box['CPU'],native_box_rectangle_boundary_cases=count,hidden_page_invalid_box_denials=rejects,full_X_pages_and_Y_borrow_retained=True,new_ZP_or_persistent_RAM=False,digest=digest.hexdigest())

def shots(old,new):
    fields=['KbAction','KbActionAge','KbCooldown','Square1SoundQueue']+[n for n in old.s if n.startswith('KbShot')and'::'not in n]
    fields=list(dict.fromkeys(fields));pairs=0
    for kind,direction in itertools.product(range(1,15),[1,2]):
        outcomes=[]
        for p in[old,new]:
            m=p.make();m[p.s['KbCopy']]=kind;m[p.s['PlayerFacingDir']]=direction;p.run(m,'KbWeapons::CopyAttack');outcomes.append({n:bytes(m[p.s[n]:p.s[n]+(3 if n.startswith('KbShot')else 1)])for n in fields})
        for n in fields:
            if kind in[2,3]and n=='KbShotVXHi':
                assert outcomes[0][n][0]==(4 if direction==1 else 252);assert outcomes[1][n][0]==(3 if direction==1 else 253)
                assert outcomes[0][n][1:]==outcomes[1][n][1:]
            else:assert outcomes[0][n]==outcomes[1][n],(kind,direction,n,outcomes)
        pairs+=1
    actual_route=[]
    for kind,sy,high in itertools.product([2,3],[196,197,200],[0,1,2]):
        p=new;m=p.make();p.enemy(m,0,356,184,high)
        for n,v in dict(KbSavedSlot=0,KbShotType=3,KbShotKind=kind,KbShotX=100,KbShotPage=1,KbShotY=sy).items():m[p.s[n]]=v
        c,hits=p.run(m,'KbWeapons::EnemyContacts');assert bool(hits)==(high==1);assert m[p.s['ObjectOffset']]==3;actual_route.append(bool(hits))
    legacy=0
    for kind,typ,dx,dy in itertools.product([0,1,5,6,7,8,11,13],[1,2,3],[-13,0,12,13],[-13,0,12,13]):
        outcomes=[]
        for p in[old,new]:
            m=p.make();p.enemy(m,0,356+dx,184+dy)
            for n,v in dict(KbSavedSlot=0,KbShotType=typ,KbShotKind=kind,KbShotX=100,KbShotPage=1,KbShotY=184).items():m[p.s[n]]=v
            c,hits=p.run(m,'KbWeapons::EnemyContacts');outcomes.append((hits,bytes(m[0x5c00:0x5ca0]),m[p.s['ObjectOffset']]))
        assert outcomes[0]==outcomes[1],(kind,typ,dx,dy);legacy+=1
    return dict(passed=True,copy_launch_state_pairs=pairs,only_shell2_3_launch_velocity_changed=True,velocity_reference='Native KickedShellXSpdData $30/$d0 in4.4 is3px/update; no claim that SMB copied-shell powers occur in original Kirby.',actual_shot_to_native_defeat_boundaries=len(actual_route),unrelated_projectile_contact_exact_pairs=legacy,native_defeat_routine_stubbed=True)

def ground_motion(old,new):
    cases=[];digest=hashlib.sha256()
    def floor(c,m,p):c.p=(c.p&254)|int(m[p.s['KbTempY']]>=208)
    for kind,direction in itertools.product([2,3],[1,2]):
        pair=[]
        for p in[old,new]:
            m=p.make();p.enemy(m,0,416 if direction==1 else 296,184)
            for n,v in dict(KbCopy=kind,PlayerFacingDir=direction,ScreenLeft_PageLoc=1,ScreenLeft_X_Pos=0).items():m[p.s[n]]=v
            p.run(m,'KbWeapons::CopyAttack');trace=[];hit_at=None
            hooks={p.s['KbWeapons::SolidPoint']:lambda c,m:floor(c,m,p),p.s['KbWeapons::BlockProxy']:lambda c,m:None}
            for update in range(1,41):
                _,hits=p.run(m,'KbWeapons::Shots',hooks=hooks)
                trace.append((m[p.s['KbShotX']],m[p.s['KbShotPage']],m[p.s['KbShotY']],m[p.s['KbShotType']]))
                if hits:hit_at=update;break
                if not m[p.s['KbShotType']]:break
            if p.mode=='fixed':assert hit_at is not None,(kind,direction,trace)
            if p.mode=='baseline'and kind==2:assert hit_at is None,(direction,trace)
            pair.append(dict(mode=p.mode,defeat_boundary_update=hit_at,updates=len(trace),final_center=trace[-1][:3],max_Y=max(t[2]for t in trace)))
            for row in trace:digest.update(bytes(row))
        cases.append(dict(copy=kind,direction=direction,outcomes=pair))
    return dict(passed=True,source_Spawn_Shots_Move_floor_and_EnemyContacts=True,cases=cases,terrain_callback='Declared flat208px floor probe; BlockProxy no-block boundary. Exact native SMB terrain/defeat code is not executed.',trace_digest=digest.hexdigest())

def main():
    old,new=Proof(),Proof('fixed');asm=json.loads((O/'fixed-assembly.json').read_text());assert asm['source_funding_fits']
    r=dict(passed=True,source_CPU=True,native=False,actual_Main=False,production_modified=False,installed=False,baseline=baseline(old),family_funding=families(old,new),inhale=inhale(old,new),shell_geometry=geometry(new),copies=shots(old,new),ground_motion=ground_motion(old,new),budget={k:asm[k]for k in['old_weapons_bytes','fixed_weapons_bytes','net_growth','projected_full_abilities_bytes','capacity','helper_bytes']},CPU_executions=old.count+new.count,standalone_minimum_SP=min(old.low,new.low),
      limitations=['No native Main/ISR/controller-emulator claim. Root must relink actual owner and test native stack reserve.','Native enemy defeat/score/SFX callees are boundary callbacks. Native table is exact current ROM witness; geometry uses those offsets directly.','Only original12 native enemy box profiles are admitted for copied shells.','Opening mouth guard changes; eight-update capture delay remains. Enemy suction movement and unrelated abilities retain source behavior.'],
      bindings={str(p.resolve()):sha(p)for p in[Path(__file__),R/'tools/audit/verify_native_relocation.py',R/'tools/audit/check_karnov_actor_1101_v1.py',R/'tools/audit/check_kirby_inhale_shell_fix_1101_v1.py',R/'tools/audit/prepare_kirby_contact_repair_1101_v1.py',R/'tools/audit/assemble_kirby_contact_repair_1101_v1.py',R/'tools/reference/kirby_shell_contact_1101_v1.inc',O/'current-witness.json',O/'current-kirby-code.bin',O/'native-box-witness.json',O/'baseline.bin',O/'baseline.dbg',O/'fixed-source.s',O/'fixed.bin',O/'fixed.dbg',O/'fixed-assembly.json']})
    (O/'repair-CPU.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items()if k not in['bindings','limitations']}))
if __name__=='__main__':main()
