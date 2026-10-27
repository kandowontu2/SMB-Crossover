"""Prepare finite current6be Rygar mature-tier/disk profiles; never launch Mesen."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import Arena, scoped_load
from check_tmnt_render_oa import address, location
from verify_native_relocation import NesMPU
from observe_chip_committed_write import lua

EXPECTED = '6be48337ffee66a22b22de9ce134d5db323649fb4de620c43bad4ca98b80f193'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
put = lambda p,z: p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')
PLAN = [dict(name='cold-disk-right',kind='disk',tier=0,face=1,hit=False,limit=90),
        dict(name='cold-hit-left',kind='disk',tier=0,face=2,hit=True,limit=90),
        dict(name='mushroom-transform',kind='collect',tier=0,face=1,pickup=0,limit=120),
        dict(name='tier1-disk-left',kind='disk',tier=1,face=2,hit=False,limit=90),
        dict(name='tier1-hit-right',kind='disk',tier=1,face=1,hit=True,limit=90),
        dict(name='flower-transform',kind='collect',tier=1,face=1,pickup=1,limit=120),
        dict(name='tier2-disk-right',kind='disk',tier=2,face=1,hit=False,limit=90),
        dict(name='tier2-hit-left',kind='disk',tier=2,face=2,hit=True,limit=90)]
ALLOWED = '''Block_Buffer_1 MmSolidTerrain MmBrickHealth Enemy_Flag Enemy_CollisionBits InvDropKind Player_X_Speed Player_Y_Speed Player_X_MoveForce Player_Y_MoveForce ScrollThirtyTwo AreaParserTaskNum MmVX MmVY MmXFraction MmYFraction ScrollLock ScreenLeft_X_Pos ScreenLeft_PageLoc ScreenRight_X_Pos ScreenRight_PageLoc Player_X_Position Player_PageLoc MmOldX Player_Y_Position Player_Y_HighPos Player_State PlayerFacingDir Player_MovingDir Player_CollisionBits Enemy_ID Enemy_State Enemy_BoundBoxCtrl Enemy_X_Position Enemy_PageLoc Enemy_Y_Position Enemy_Y_HighPos Enemy_X_Speed Enemy_Y_Speed Enemy_SprAttrib PowerUpType InvPickupOwner InvPickup Enemy_Y_MoveForce Enemy_MovingDir EnemyOffscrBitsMasked MmEnemyHealthLo MmEnemyHealthHi MmEnemyFlash RgEnemyStun'''.split()


def setup(q, task):
    assert q.get('XgDiskReach') == 0
    assert all(q.get('RgShotType', i) == 0 for i in range(10))
    for n in ['Block_Buffer_1', 'MmSolidTerrain', 'MmBrickHealth']:
        q.array(n, [0]*416)
    for page in (0, 1):
        for row in (11, 12):
            for col in range(16):
                q.set('Block_Buffer_1',0x54,page*208+row*16+col)
    for i in range(6):
        q.set('Enemy_Flag',0,i);q.set('Enemy_CollisionBits',0,i)
    for i in range(4):
        q.set('InvDropKind',0,i)
    q.put(Player_X_Position=112,Player_PageLoc=0,Player_Y_Position=176,
          Player_Y_HighPos=1,Player_State=0,PlayerFacingDir=task['face'],
          Player_MovingDir=task['face'],Player_CollisionBits=255,MmOldX=112,
          ScreenLeft_PageLoc=0,ScreenLeft_X_Pos=0,ScreenRight_PageLoc=0,
          ScreenRight_X_Pos=255,ScrollLock=1,ScrollThirtyTwo=0,AreaParserTaskNum=0,
          Player_X_Speed=0,Player_Y_Speed=0,Player_X_MoveForce=0,Player_Y_MoveForce=0)
    for n, size in [('MmVX',3),('MmVY',3),('MmXFraction',2),('MmYFraction',2)]:
        q.array(n,[0]*size)
    if task['kind'] == 'collect':
        for n,v in [('Enemy_Flag',1),('Enemy_ID',0x2e),('Enemy_State',128),
                    ('Enemy_BoundBoxCtrl',3),('Enemy_X_Position',112),
                    ('Enemy_PageLoc',0),('Enemy_Y_Position',184),('Enemy_Y_HighPos',1),
                    ('Enemy_X_Speed',0),('Enemy_Y_Speed',0),('Enemy_SprAttrib',0),
                    ('PowerUpType',task['pickup']),('InvPickupOwner',7),('InvPickup',0xfc)]:
            q.set(n,v,5)
    elif task['hit']:
        x = 160 if task['face'] == 1 else 88
        for col in range(x//16,(x+16)//16+1):
            q.set('Block_Buffer_1',0x54,160+col)
        for n,v in dict(Enemy_Flag=1,Enemy_ID=6,Enemy_State=0,Enemy_X_Position=x,
                        Enemy_PageLoc=0,Enemy_Y_Position=168,Enemy_Y_HighPos=1,
                        Enemy_X_Speed=0,Enemy_Y_Speed=0,Enemy_Y_MoveForce=0,
                        Enemy_MovingDir=1,Enemy_BoundBoxCtrl=9,EnemyOffscrBitsMasked=0,
                        Enemy_CollisionBits=0,MmEnemyHealthLo=0,MmEnemyHealthHi=0,
                        MmEnemyFlash=0,RgEnemyStun=0).items():
            q.set(n,v,0)


def campaign(b, mode, plan):
    q = Arena(b,7)
    q.put(PlayerStatus=0,CrossoverBehaviorVersion=mode,OperMode_Task=3,AreaType=1)
    q.array('GameTimerDisplay',[3,9,9])
    raw = lambda n,i=0: b['raw'][location(b,n)+i]
    assert raw('InvItemCount',7) == 0
    for n in ['InvSelectable','InvInitialAmmo','InvMaxAmmo']:
        assert all(raw(n,112+i) == 0 for i in range(16))
    c,_ = q.invoke('InventorySupported');assert c.p&1 == 0
    source_rows, trace, case, age = [], None, None, 0
    names = ['GameLoop','HpProcessFireballsBridge','ProcFireball_Bubble','RlWeaponsDispatch',
             'LmWeaponsGate','JnWeaponsDispatch','M3WeaponsDispatch','VvWeaponsDispatch',
             'TnWeaponsDispatch','CdWeaponsDispatch','KbWeaponsDispatch','ExpandedWeapons',
             'ExpandedWeapons::CatchDisk',
             'MegaManWeapons::DamageEnemy','MarioSourcePowerupCollision',
             'GuestBeginPowerup','GuestPowerupUpdate']
    owners = {(address(b,n),(location(b,n)-16)//8192):n for n in names}
    owners[(address(b,'ExpandedWeapons::Many')-6,
            (location(b,'ExpandedWeapons::Many')-16)//8192)]='RygarActiveDiskRefusal'
    original = NesMPU.step

    def step(cpu):
        bank = q.m.banks[(cpu.pc-0x8000)//8192] if cpu.pc >= 0x8000 else -1
        n = owners.get((cpu.pc,bank))
        if n:
            if n not in trace['owners']:trace['owners'].append(n)
            if n == 'RygarActiveDiskRefusal':
                assert q.get('RgCount') == 1 and q.get('RgWeaponButtons')&64
                trace['refusals'] += 1
                trace['refusal_PC_bank']=[cpu.pc,bank]
            elif n == 'ExpandedWeapons::CatchDisk':
                assert q.get('XgDiskReach') == 16 and q.get('XgDiskReturning') == 1
                trace['catch_age'] = age;trace['catch_shot_age'] = q.get('RgShotAge',q.get('RgSlot'))
            elif n == 'MegaManWeapons::DamageEnemy':
                assert cpu.x == 0 and q.get('MmBulletType') == 29
                trace['contacts'].append(dict(age=age,PC=cpu.pc,bank=bank,
                    proxy=q.get('MmBulletType'),disk=[q.get('MmBulletX'),q.get('MmBulletY')],
                    target=[q.get('Enemy_X_Position'),q.get('Enemy_Y_Position')]))
            elif n == 'MarioSourcePowerupCollision':
                assert cpu.x == 5;trace['collections'] += 1
            elif n == 'GuestPowerupUpdate' and q.get('GuestPowerupActive'):
                trace['growth_calls'] += 1
        original(cpu)

    NesMPU.step = step
    try:
        for case in plan:
            assert q.get('PlayerStatus') == case['tier']
            setup(q,case)
            trace = dict(name=case['name'],tier=case['tier'],face=case['face'],owners=[],
                         sequences=[],anchors=[],refusals=0,contacts=[],collections=0,
                         growth_calls=0,hp_writes=[],spawn_writes=0)
            for age in range(case['limit']+1):
                b_button = case['kind']=='disk' and (6<=age<9 or age>=11 and q.get('RgCooldown')==0 and any(q.get('RgShotType',s) for s in range(10)) and trace['refusals']==0)
                q.put(SavedJoypadBits=64 if b_button else 0)
                _, writes = q.invoke('GameLoop')
                assert q.get('Player_X_Position') == 112 and q.get('Player_Y_Position') == 176
                assert q.get('Player_State') == 0 and q.get('MmDeathFlag') == q.get('InjuryTimer') == q.get('GuestHurtTicks') == 0
                for w in writes:
                    if address(b,'RgShotType') <= w['address'] < address(b,'RgShotType')+10 and w['value'] == 2:trace['spawn_writes'] += 1
                    if w['address'] in [address(b,'MmEnemyHealthLo'),address(b,'MmEnemyHealthHi')]:trace['hp_writes'].append(dict(age=age,**w))
                if case['kind'] == 'collect':
                    if trace['growth_calls'] and q.get('GuestPowerupActive') == 0:
                        assert trace['collections'] == 1 and trace['growth_calls'] == 60
                        assert q.get('PlayerStatus') == case['tier']+1 and q.get('TimerControl') == 0
                        break
                else:
                    assert q.get('PlayerStatus') == case['tier'] and q.get('GameEngineSubroutine') == 8
                    active = [s for s in range(10) if q.get('RgShotType',s)]
                    assert len(active) <= 1
                    if active:
                        slot=active[0];assert q.get('RgShotType',slot) == 2
                        if q.get('RgShotAge',slot) >= 3:
                            reach=q.get('XgDiskReach');trace['sequences'].append(reach)
                            expected=112+8+(reach if case['face']==1 else 2-reach)
                            assert q.get('RgShotX',slot)+256*q.get('RgShotPage',slot) == expected
                            assert q.get('RgShotY',slot) == 184
                            trace['anchors'].append([expected,184])
            trace['full_GameLoop_calls'] = age+1
            if case['kind'] == 'disk':
                assert trace['sequences'] == case['sequence']
                assert trace['catch_shot_age'] == len(case['sequence'])+3
                assert trace['spawn_writes'] == trace['refusals'] == 1, (case['name'],trace['spawn_writes'],trace['refusals'],trace['owners'])
                assert q.get('XgDiskReach') == 0 and q.get('XgDiskReturning') == 1
                assert q.get('RgShootPose') == 0 and all(q.get('RgShotType',s)==0 for s in range(10))
                if case['hit']:
                    assert len(trace['contacts']) == 1 and len(trace['hp_writes']) >= 4
                else:assert not trace['contacts'] and not trace['hp_writes']
            source_rows.append(trace)
    finally:
        NesMPU.step = original
    return dict(passed=True,mode=mode,complete_caller=True,no_inventory_IDs=True,
                no_tier_fuel_disk_or_projectile_writes_after_cold_initial_state=True,
                actual_cpu_setup='Same complete logical map/position/actor setup; real nametable art/PPU/timing remains native work.',
                cases=source_rows,GameLoop_calls=sum(r['full_GameLoop_calls'] for r in source_rows))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,default=ROOT/'build/samus_fixed_hud_current4a.nes')
    p.add_argument('--expected-sha256',default=EXPECTED)
    p.add_argument('--mode',choices=['easy','hard'],required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.rom=a.rom.resolve();a.output=a.output.resolve()
    assert not a.output.exists() and sha(a.rom)==a.expected_sha256==EXPECTED
    b=scoped_load(a.rom);fixture=ROOT/'tools/audit/current_rygar_powerups_v1.lua';text=fixture.read_text()
    baseline=ROOT/'tools/audit/current_pit_powerups_v3.lua';old=baseline.read_text()
    begin='-- All callback registration is startup-static.';end="emu.addEventCallback(function()\n if not entered"
    assert text[text.index(begin):text.index(end)] == old[old.index(begin):old.index(end)]
    assert text.count('emu.write(')==2 and 'removeMemoryCallback' not in text and 'dofile(' not in text
    plan=json.loads(json.dumps(PLAN))
    many=location(b,'ExpandedWeapons::Many');count=address(b,'RgCount');ret=address(b,'ExpandedWeapons::Return');clear=address(b,'ExpandedWeapons::ClearMeleeMap')
    assert b['raw'][many-11:many]==bytes([0xad,count&255,count>>8,0xf0,3,0x4c,ret&255,ret>>8,0x20,clear&255,clear>>8]),'Real Rygar early active-disk refusal, not generic PoolFull'
    for task in plan:
        if task['kind']=='disk':
            reach=b['raw'][location(b,'ExpandedWeapons::DiskReach')+task['tier']]
            assert reach==[40,64,88][task['tier']]
            task.update(reach=reach,sequence=list(range(24,reach+1,4))+list(range(reach-4,19,-4)),outward_count=(reach-24)//4+1)
    source=campaign(b,int(a.mode=='hard'),plan)
    def hook(n,delta=0,size=3):
        pos=location(b,n)+delta;pc=address(b,n)+delta;k=(pos-16)//8192;bs=list(b['raw'][pos:pos+size]);banks=[k]
        if k==127:
            off=(pos-16)%8192;assert b['raw'][16+125*8192+off:16+125*8192+off+size]==bytes(bs);banks=[125,127]
        return dict(pc=pc,banks=banks,bytes=bs,source_symbol=n,source_delta=delta)
    hooks={key:hook(n) for key,n in dict(PhysicalPickup='MarioSourcePowerupCollision',GuestBeginPowerup='GuestBeginPowerup',GuestPowerupUpdate='GuestPowerupUpdate',CatchDisk='ExpandedWeapons::CatchDisk',DamageEnemy='MegaManWeapons::DamageEnemy',NmiEntry='NonMaskableInterrupt',IrqEntry='IrqScrollSplit').items()}
    hooks['DiskPoolRefusal']=hook('ExpandedWeapons::Many',-6)
    assert b['raw'][location(b,'GameLoop'):location(b,'GameLoop')+5]==bytes([0xa9,255,0x8d,address(b,'NmiDisable')&255,address(b,'NmiDisable')>>8])
    hooks['GameLoopOwned']=hook('GameLoop',5)
    for key,n,op in [('GameLoopFinish','GameLoop',0x60),('NmiReturn','NonMaskableInterrupt',0x40),('IrqReturn','IrqScrollSplit',0x40)]:
        delta=int(b['syms'][n]['size'],0)-1;assert b['raw'][location(b,n)+delta]==op;hooks[key]=hook(n,delta,1)
    post=location(b,'PostDmaMaskEnable');mirror=address(b,'Mirror_PPUMASK');load=bytes([0xa5,mirror]) if mirror<256 else bytes([0xad,mirror&255,mirror>>8])
    assert b['raw'][post-3:post]==b'\x8d\x14\x40' and b['raw'][post:post+len(load)+3]==load+b'\x8d\x01\x20'
    hooks['DmaComplete']=hook('PostDmaMaskEnable',len(load))
    names=set(re.findall(r"'([A-Za-z_][A-Za-z_0-9]*)'",text))|set(ALLOWED)|set('CurrentBank CurrentBankC Sprite0HitDetectFlag MmEnemyHealthLo MmEnemyHealthHi RgShotType Square1SoundQueue'.split())
    ram={n:address(b,n) for n in names if n in b['syms']}
    for n in re.findall(r"[rw]\('([A-Za-z_][A-Za-z_0-9]*)'",text)+ALLOWED:assert n in ram,n
    assert not set(ALLOWED)&set('PlayerStatus PlayerSize XgDiskReach XgDiskReturning RgShotType RgShootPose RgAttack InvOwnedLo InvOwnedHi InvSelected InvAmmo InjuryTimer GuestHurtTicks MmDeathFlag CheatInvincible'.split())
    cfg=dict(ROM_sha256=EXPECTED,character=7,slot=7,mode=int(a.mode=='hard'),ram=ram,hooks=hooks,setup_allowed={n:True for n in ALLOWED},plan=plan,dma_store_return=address(b,'PostDmaMaskEnable'),smc=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2],metatiles={n:dict(bank=(location(b,n)-16)//8192,offset=(location(b,n)-16)%8192) for n in ['MTileTopLeft','MTileTopRight','MTileBotLeft','MTileBotRight','MTileAttribute']})
    a.output.mkdir(parents=True);put(a.output/'config.json',cfg)
    (a.output/'run.lua').write_text('CURRENT_RYGAR_POWERUPS='+lua(cfg)+'\ndofile([=['+fixture.as_posix()+']=])\n',newline='\n')
    put(a.output/'source-controls.json',source)
    argv=[sys.executable,'-B',str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(a.output/'native'),str(a.output/'run.lua'),str(a.rom),'--timeout','1200','--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
    put(a.output/'command.json',dict(PREPARED_DO_NOT_RUN=True,ROOT_owns_native_lease=True,argv=argv))
    paths=[a.rom,a.rom.with_suffix('.dbg'),a.rom.with_suffix('.lbl'),fixture,Path(__file__),baseline]
    paths += [ROOT/'tools/audit'/n for n in ['link_pit_rygar_sophia_audit_cpu.py','check_tmnt_render_oa.py','verify_native_relocation.py','observe_chip_committed_write.py','run_mesen_isolated.py','capture_budget.py']]+[ROOT/'tools/run_mesen.py']
    paths += [ROOT/'src'/n for n in ['inventory.s','game.s','object.s','expanded.s','expanded_weapons.s','guest_powerups.s','mario_source.s','roster.s','megaman_weapons.s']]
    paths += [a.output/n for n in ['config.json','run.lua','source-controls.json','command.json']]
    put(a.output/'prepared-not-run.json',dict(status='PREPARED_DO_NOT_RUN',native_run=False,passed=False,goal_complete=False,ROM_sha256=EXPECTED,character=7,actual_numeric_mode=cfg['mode'],plan=plan,source_controls_passed=True,hardware_guard_literal_from_current_Pit=True,caps=dict(updates=3000,wall_frames=8000,host_seconds=1200,bytes=2000000000,files=64,PNGs=8),setup='Private GameLoop+5 complete logical+visible scene/mature actors/raised default-health NPC only; no tested tier, inventory, reach, return, projectiles or outcomes seeded.',limits='No native/Lua-VM/PPU-art/cadence/audio proof from source CPU. Mature pickup, not reveal/rise/RNG. Source has no Rygar inventory IDs; star/1up/air/crouch/terrain-blocked disk/damage/reacquire/campaign remain untested.',bindings=[dict(path=str(q.resolve()),bytes=q.stat().st_size,sha256=sha(q)) for q in paths]))
    print(json.dumps(dict(status='PREPARED_DO_NOT_RUN',output=str(a.output),sha256=sha(a.output/'prepared-not-run.json'),bindings=len(paths),source_GameLoop_calls=source['GameLoop_calls'],native_run=False)))


if __name__=='__main__':
    main()
