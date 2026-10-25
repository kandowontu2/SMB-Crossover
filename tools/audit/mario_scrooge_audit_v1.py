"""Bounded assembled audit of Mario-family and Scrooge-family components.

No emulator, actual PPU, acoustic fidelity, or campaign assertions. The private
proposal changes only SMB3 projectile admission and delegates Bowser damage to
the existing SMB1 boss routine. All source references remain untouched.
"""
from pathlib import Path
import argparse, difflib, hashlib, itertools, json, re, shutil, subprocess, sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools/audit'))
from check_tmnt_render_oa import load, Memory, address, location
from verify_native_relocation import NesMPU


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


class Arena:
    def __init__(self, b, char=17):
        self.b, self.m = b, Memory(b)
        self.put(SelectedCharacter=char, CrossoverBehaviorVersion=1,
                 OperMode=1, GameEngineSubroutine=8, Player_Y_HighPos=1,
                 Player_X_Position=96, Player_PageLoc=1, Player_Y_Position=160,
                 PlayerFacingDir=1, ScreenLeft_PageLoc=1, DisableScreenFlag=1)

    def get(self, n, i=0):
        return self.m[address(self.b,n)+i]

    def set(self,n,v,i=0):
        self.m[address(self.b,n)+i]=v

    def put(self, **values):
        for n,v in values.items(): self.set(n,v)

    def call(self,n,a=0,x=0,y=0):
        pc=address(self.b,n)
        window=(pc-0x8000)//8192
        bank=(location(self.b,n)-16)//8192
        self.m.page(window,bank)
        if window in (1,2):
            self.set('CurrentBank' if window==1 else 'CurrentBankC',bank|128)
        c=NesMPU(memory=self.m,pc=pc)
        c.a,c.x,c.y,c.p,c.sp=a,x,y,0x30,0xfd
        c.stPushWord(0x5aff)
        self.m.writes=[]
        trace=[]
        for _ in range(200000):
            if c.pc==0x5b00:
                assert c.sp==0xfd
                self.trace=trace
                return c
            if len(trace)<160: trace.append((c.pc,c.a,c.x,c.y,c.sp))
            c.step()
        raise AssertionError(('timeout',n,hex(c.pc),self.m.banks))


def shot_case(b, enemy, kind, variant=0, mode=1, hp=5):
    q=Arena(b)
    q.put(M3SavedSlot=0, M3Variant=variant, M3Form=6 if kind==2 else 2,
          CrossoverBehaviorVersion=mode, ObjectOffset=0, BowserHitPoints=hp,
          DuplicateObj_Offset=5)
    q.put(M3ShotKind=kind, M3ShotX=96, M3ShotPage=1, M3ShotY=168,
          M3ShotYHi=1, Enemy_Flag=1, Enemy_ID=enemy,
          Enemy_X_Position=96, Enemy_PageLoc=1, Enemy_Y_Position=160,
          Enemy_Y_HighPos=1, Enemy_Rel_XPos=96, Enemy_Rel_YPos=160)
    cpu=q.call('M3ShotEnemies')
    return q, dict(enemy=enemy, kind=kind, variant=variant, mode=mode,
                   isolated_cpu_cycles=cpu.processorCycles,
                   hp_before=hp, hp_after=q.get('BowserHitPoints'),
                   enemy_state=q.get('Enemy_State'), shot_after=q.get('M3ShotKind'),
                   enemy_id_after=q.get('Enemy_ID'),
                   trace=[dict(pc=f'{pc:04X}',a=a,x=x,y=y,sp=sp) for pc,a,x,y,sp in q.trace])


def original_weapon_cases():
    """Execute the pinned SMB3 common projectile handler with native attributes.

    Declared trap: Score_PopUp only, after successful damage has been decided.
    This is separate from the port's SMB1 Bowser HP adaptation.
    """
    auth=ROOT/'build/verification/smb3-mario-candidate-agent/auth-source'
    rom=Path('C:/NES/Super Mario Bros. 3 (USA) (Rev 1).nes').read_bytes()
    assert hashlib.sha256(rom).hexdigest()=='1ddc4b429490e298c05fa70389034107c0cb50f671c7c1baaa3f228224afc2e9'
    assert rom[16:]==(auth/'smb3.nes').read_bytes()[16:]
    sy={n:int(v,16) for n,v in re.findall(r'^(\w+)\s*=\s*\$([0-9A-Fa-f]+)',(auth/'smb3.fns').read_text(),re.M)}
    killed=int(re.search(r'^OBJSTATE_KILLED\s*=\s*(\d+)',(auth/'smb3.asm').read_text(),re.M).group(1))
    rows=[]
    for enemy,kind in itertools.product([0x18,0x70],[1,2]):
        m=[0]*65536
        for base,bank in [(0x8000,30),(0xa000,7),(0xc000,0),(0xe000,31)]:
            m[base:base+8192]=rom[16+bank*8192:16+(bank+1)*8192]
        attr=m[sy['Object_AttrFlags']+enemy]
        assert not attr&32,'Native object unexpectedly weapon-immune'
        if enemy==0x70: assert attr&64,'Buzzy must be fire-immune'
        for n,v in dict(Temp_Var1=attr,Temp_Var13=168,Temp_Var14=104,
                         Objects_SpriteY=160,Objects_SpriteX=96,
                         SlotIndexBackup=0,PlayerProj_ID=kind,PlayerProj_XVel=4,
                         Objects_HitCount=34 if enemy==0x18 else 0).items():
            m[sy[n]]=v
        c=NesMPU(memory=m,pc=sy['PlayerProj_HitObject'])
        c.x,c.y,c.sp,c.p=0,0,0xfd,0x30
        c.stPushWord(0x5aff)
        score=0
        for _ in range(20000):
            if c.pc==0x5b00: break
            if c.pc==sy['Score_PopUp']:
                score+=1; c.pc=(c.stPopWord()+1)&65535
                continue
            c.step()
        else: raise AssertionError(('original timeout',enemy,kind,hex(c.pc)))
        if enemy==0x18: assert m[sy['Objects_HitCount']]==33
        if enemy==0x70: assert (m[sy['Objects_State']]==killed)==(kind==2)
        rows.append(dict(enemy=enemy,kind=kind,native_attributes=attr,
                         hitcount_after=m[sy['Objects_HitCount']],
                         state_after=m[sy['Objects_State']],score_traps=score))
    return dict(original_ROM_sha256=hashlib.sha256(rom).hexdigest(),
                rebuilt_payload_exact=True,actual_original_cases=rows,
                symbols_sha256=sha(auth/'smb3.fns'),declared_traps=['Score_PopUp'])


def prepare(args):
    out=args.output.resolve()
    assert not out.is_relative_to(ROOT.resolve())
    out.mkdir(parents=True,exist_ok=False)
    stage=out/'source'; (stage/'src').mkdir(parents=True)
    for name in ('smb1base-mmc5-expanded.cfg','src/entrypoint.s','src/smb3_mario_combat.s'):
        shutil.copyfile(ROOT/name,stage/name)
    target=stage/'src/smb3_mario_combat.s'
    before=target.read_text()
    token=' lda Enemy_ID,y\n cmp #$15\n jcs Next\n cmp #Podoboo\n'
    assert before.count(token)==1
    after=before.replace(token,' jsr M3AuditProjectileAdmission\n nop\n nop\n jcs Next\n cmp #Podoboo\n')
    start=after.index('.proc M3ShotEnemies')
    head,tail=after[:start],after[start:]
    assert tail.count(' jsr M3DefeatEnemy\n')==1
    tail=tail.replace(' jsr M3DefeatEnemy\n',' jsr M3AuditProjectileDamage\n')
    after=head+tail
    target.write_text(after)
    helper='''; Private bounded proposal: source hammers pierce fire-only armor.
; Bowser receives the host's existing native boss damage rather than StnE.
.pushseg
.segment "M3_LOGIC"
.proc M3AuditProjectileAdmission
 lda Enemy_ID,y
 cmp #Bowser
 beq Allowed
 cmp #BuzzyBeetle
 bne Ordinary
 ldx M3SavedSlot
 lda M3ShotKind,x
 cmp #2
 bne BeetleFire
 lda #0 ; Only the following temporary ID filters see this value.
Allowed:clc
 rts
BeetleFire:lda #BuzzyBeetle
Ordinary:cmp #$15
 rts
.endproc
.proc M3AuditProjectileDamage
 lda Enemy_ID,x
 cmp #Bowser
 beq Boss
 jmp M3DefeatEnemy
Boss:stx R1
 jmp HandleEnemyFBallCol
.endproc
.popseg
'''
    (stage/'src/mario_scrooge_audit_combat.inc').write_text(helper)
    entry=stage/'src/entrypoint.s'
    entry_before=entry.read_text()
    entry_after=entry_before+'\n.include "mario_scrooge_audit_combat.inc"\n'
    entry.write_text(entry_after)
    patch=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),
                                      fromfile='a/src/smb3_mario_combat.s',tofile='b/src/smb3_mario_combat.s'))
    patch+=''.join(difflib.unified_diff(entry_before.splitlines(True),entry_after.splitlines(True),
                                       fromfile='a/src/entrypoint.s',tofile='b/src/entrypoint.s'))
    patch+=''.join(difflib.unified_diff([],helper.splitlines(True),
                                       fromfile='/dev/null',tofile='b/src/mario_scrooge_audit_combat.inc'))
    (out/'implementation.patch').write_text(patch)
    command=[sys.executable,str(ROOT/'tools/build_mmc5_expanded.py'),
             '--source-overlay',str(stage),'--output',str(out/'candidate.nes')]
    r=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
    (out/'prepare.log').write_text(r.stdout+r.stderr)
    assert r.returncode==0,(r.stdout+r.stderr)[-5000:]
    old,new=load(args.rom),load(out/'candidate.nes')
    old_labels={q[2]:q[1] for l in args.rom.with_suffix('.lbl').read_text().splitlines() if len(q:=l.split())==3}
    new_labels={q[2]:q[1] for l in (out/'candidate.lbl').read_text().splitlines() if len(q:=l.split())==3}
    assert all(new_labels[n]==v for n,v in old_labels.items()),'Existing exported PC/RAM moved'
    changes=[i for i,(a,b) in enumerate(zip(old['raw'],new['raw'])) if a!=b]
    assert len(old['raw'])==len(new['raw'])
    assert {(i-16)//8192 for i in changes}=={90}
    assert old['raw'][:16]==new['raw'][:16]
    assert old['raw'][16+1048576:]==new['raw'][16+1048576:]
    report=dict(prepared=True,accepted=False,baseline_sha256=sha(args.rom),
                candidate_sha256=sha(out/'candidate.nes'),changed_bytes=len(changes),
                changed_PRG_banks=sorted({(i-16)//8192 for i in changes}),
                existing_exported_PC_RAM_unchanged=True,CHR_unchanged=True,
                source_changes={'src/smb3_mario_combat.s':sha(target),
                                'appended_helper':sha(stage/'src/mario_scrooge_audit_combat.inc')},
                limits='Private only. Bowser uses native SMB1 HP, not SMB3 original35-hit balance. Hammer contact retains existing per-update behavior. Requires native rendering/audio/boss progression qualification.')
    (out/'prepare.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


def check(args):
    args.output.mkdir(parents=True,exist_ok=False)
    b=load(args.rom)
    rows=[]
    for enemy,kind,variant,mode in itertools.product([2,6,12,0x2d],[1,2],[0,1],[0,1]):
        q,row=shot_case(b,enemy,kind,variant,mode)
        row.pop('trace')
        if enemy==6: assert row['enemy_state']&32
        if enemy==12: assert row['enemy_state']==0
        if args.repaired:
            if enemy==2: assert bool(row['enemy_state']&32)==(kind==2)
            if enemy==0x2d:
                assert row['hp_after']==4 and row['enemy_state']==0
                assert row['shot_after']==(0 if kind==1 else 2)
        else:
            if enemy in (2,0x2d):
                assert row['enemy_state']==0 and row['hp_after']==5
        rows.append(row)
    failures=[]
    if not args.repaired:
        for enemy,kind in [(0x2d,1),(0x2d,2),(2,2)]:
            _,r=shot_case(b,enemy,kind)
            failures.append(r)
    checks=dict(projectile_matrix=len(rows))
    # Existing statue-damage repair must clear actual native queued suit state.
    count=0
    for form,variant,mode in itertools.product(range(1,7),[0,1],[0,1]):
        q=Arena(b)
        q.put(M3Form=form,M3Variant=variant,CrossoverBehaviorVersion=mode)
        for n in ['Player_Statue','Player_QueueSuit','Player_SuitLost','Player_FlashInv',
                  'Player_TailAttack','Player_TailCount','Player_FlyTime',
                  'Player_AllowAirJump','Player_WagCount']:
            q.set(n,0xc0)
        q.call('M3Injury')
        assert q.get('M3Form')==(0 if form==1 else 1)
        for n in ['Player_Statue','Player_QueueSuit','Player_SuitLost','Player_FlashInv',
                  'Player_TailAttack','Player_TailCount','Player_FlyTime',
                  'Player_AllowAirJump','Player_WagCount']:
            assert q.get(n)==0,n
        assert q.get('GuestInvulTicks')==113
        count+=1
    checks['statue_and_suit_loss']=count
    count=0
    for char,water,engine,state,vx,direction,force in itertools.product(
            [0,8,12],[0,1],[8,4],[0,1],[0,8,248],[0,1,2],[0x18,0x80,0x1a3]):
        q=Arena(b,char)
        q.put(SwimmingFlag=water,GameEngineSubroutine=engine,Player_State=state,
              Player_X_Speed=vx,Left_Right_Buttons=direction,
              FrictionAdderLow=force&255,FrictionAdderHigh=force>>8)
        q.call('LuigiNativeTraction')
        expect=force
        opposite=vx!=0 and not(direction&(1 if vx<128 else 2))
        if char==8 and water==0 and engine==8 and state==0 and opposite:
            expect=force-force//8
        assert q.get('FrictionAdderLow')+256*q.get('FrictionAdderHigh')==expect
        count+=1
    checks['Luigi_requested_ground_braking']=count
    # Dry jump fraction only, with native water and scripted-engine exclusions.
    count=0
    for water,engine,speed,frac in itertools.product([0,1],[8,4],[0xfb,0xfa],[0,0x33,0x80,0xff]):
        q=Arena(b,8)
        q.put(SwimmingFlag=water,GameEngineSubroutine=engine,
              Player_Y_Speed=speed,Player_Y_MoveForce=frac)
        q.call('LuigiNativeJump')
        expected=((speed<<8)|frac)-(0x33 if not water and engine==8 else 0)
        assert q.get('Player_Y_Speed')*256+q.get('Player_Y_MoveForce')==expected&65535
        count+=1
    checks['Luigi_requested_jump_fraction']=count
    count=0
    for mode,status,item in itertools.product([0,1],range(3),[0,1]):
        q=Arena(b,0)
        q.put(CrossoverBehaviorVersion=mode,PlayerStatus=status,PowerUpType=item)
        q.call('MarioSourceBeginPowerup')
        target=min(2,status+1) if mode==0 else max(status,item+1)
        changed=status<2 and target>status
        assert bool(q.get('GuestPowerupActive'))==changed
        if changed: assert q.get('GuestPowerupTarget')==target
        count+=1
    checks['Mario_easy_hard_power_tiers']=count
    count=0
    for kind,gas,prior,face,stance in itertools.product(range(4),[0,1,2,3,99],range(4),[1,2],[0,1,2]):
        q=Arena(b,12)
        q.put(DarkwingVariant=1,DwAdaptor=kind,DwMode=int(kind!=0),DwGas=gas,
              PlayerFacingDir=face,Player_State=int(stance==2),RgCrouch=int(stance==1))
        types=[1,3,5,7]
        for i in range(prior): q.set('RgShotType',types[kind],i)
        q.call('DwLaunch')
        allowed=gas>=[0,2,3,2][kind] and prior<[3,1,2,1][kind]
        assert q.get('DwGas')==gas-([0,2,3,2][kind] if allowed else 0)
        total=sum(bool(q.get('RgShotType',i)) for i in range(10))
        assert total==prior+int(allowed)
        if allowed:
            offset=17 if stance==0 else 28 if stance==1 else 20
            assert q.get('RgShotY',9)==160+offset
        count+=1
    checks['Darkwing_original_gas_cost_caps_stances']=count
    count=0
    for fresh,held,prior_rise,vy in itertools.product([0,128],[0,128],[0,1],[0,0xfb]):
        q=Arena(b,12)
        q.put(ScFresh=fresh,A_B_Buttons=held,XgRise=prior_rise,
              MmUnderwater=0,Player_State=1)
        q.set('MmVY',vy,2)
        q.call('ScroogePhysics')
        assert q.get('XgGravity')==0 and q.get('XgGravity',1)==0x33
        if fresh:
            assert [q.get('MmVY',i) for i in range(3)]==[0,0x12,0xfb]
            assert q.get('MmYFraction')==q.get('MmYFraction',1)==255
        elif prior_rise and vy==0xfb and not held:
            assert all(q.get('MmVY',i)==0 for i in range(3))
        count+=1
    checks['Scrooge_native_launch_release_gravity_adapter']=count
    source=original_weapon_cases()
    (args.output/'authenticated-original-projectiles.json').write_text(json.dumps(source,indent=2)+'\n')
    checks['actual_original_SMB3_projectile_handler']=4
    report=dict(passed=not failures,component_assertions_passed=True,accepted=False,ROM_sha256=sha(args.rom),
                driver_sha256=sha(Path(__file__)),
                implementation_source_sha256={n:sha((args.source_root/'src'/n) if (args.source_root/'src'/n).exists() else ROOT/'src'/n) for n in [
                    'mario_source.s','luigi_native.s','scrooge.s','darkwing_core.s',
                    'darkwing_weapons.s','darkwing_pickups.s','smb3_mario_combat.s',
                    'smb3_mario_core.s','smb3_mario_dispatch.s','smb3_mario_world.s']},
                repaired_projectile_expectations=args.repaired,checks=checks,
                known_failures=len(failures),
                scope='Assembled isolated CPU components. Existing Luigi/statue assertions pass; baseline projectile failures are recorded explicitly. No interrupt/PPU/audio/campaign/source-complete proof.')
    (args.output/'proof.json').write_text(json.dumps(report,indent=2)+'\n')
    (args.output/'projectile-cases.json').write_text(json.dumps(rows,indent=2)+'\n')
    (args.output/'baseline-defects.json').write_text(json.dumps(failures,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=['prepare','check'])
    p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--source-root',type=Path,default=ROOT)
    p.add_argument('--repaired',action='store_true')
    a=p.parse_args()
    (prepare if a.action=='prepare' else check)(a)
