"""Prepare one shared Star/1-Up pilot; actual CPU qualification, never Mesen.

Only Mario, Little Mac and Vic Viper are admitted initially. Additional identities
must be qualified after these native pilots; the linked37 metadata is not proof.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import sys

R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import Arena, scoped_load
from check_tmnt_render_oa import address, location
from verify_native_relocation import NesMPU
from current_roster_compact_11_v1 import BASE, navigation, lua

EXPECTED = 'ab221e81821dd10690ad3a1068d91c9efae6c7406230d9bd7fc4a729fdc433d2'
PILOTS = ('mario', 'mac', 'vic')
ALLOWED = '''Block_Buffer_1 MmSolidTerrain MmBrickHealth Enemy_Flag Enemy_CollisionBits
Player_X_Speed Player_Y_Speed Player_X_MoveForce Player_Y_MoveForce
ScrollThirtyTwo AreaParserTaskNum ScrollLock ScreenLeft_X_Pos ScreenLeft_PageLoc ScreenRight_X_Pos ScreenRight_PageLoc
Player_X_Position Player_PageLoc Player_Y_Position Player_Y_HighPos Player_State PlayerFacingDir Player_MovingDir Player_CollisionBits
Enemy_ID Enemy_State Enemy_BoundBoxCtrl Enemy_X_Position Enemy_PageLoc Enemy_Y_Position Enemy_Y_HighPos Enemy_X_Speed Enemy_Y_Speed Enemy_Y_MoveForce Enemy_MovingDir Enemy_SprAttrib EnemyOffscrBitsMasked
PowerUpType InvPickupOwner InvPickup'''.split()
BANS = '''StarInvincibleTimer NumberofLives PlayerStatus PlayerSize InvOwnedLo InvOwnedHi InvAmmo InvSelected LmHealth LmHearts LmStars VvShield VvGun VvMissile VvOptions VvSpeed VvMeter InjuryTimer GuestHurtTicks MmDeathFlag CheatInvincible PseudoRandomBitReg GuestPowerupActive GuestPowerupTarget AreaMusicQueue Square2SoundQueue FloateyNum_Control FloateyNum_Timer'''.split()
MOTION = ['Player_X_Speed', 'Player_Y_Speed', 'Player_X_MoveForce', 'Player_Y_MoveForce']
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
put = lambda p, v: p.write_text(json.dumps(v, indent=2)+'\n', newline='\n')


def resources(identity):
    a = [dict(name=n, index=0, count=c) for n, c in
         [('PlayerStatus',1),('PlayerSize',1),('InvOwnedLo',12),('InvOwnedHi',12),
          ('InvSelected',12),('InvAmmo',192)]]
    extra = {'mac':['LmHealth','LmHearts','LmStars'],
             'vic':['VvShield','VvGun','VvMissile','VvOptions','VvSpeed','VvMeter']}
    return a+[dict(name=n,index=0,count=1) for n in extra.get(identity, [])]


def hooks_for(b):
    def hook(n, delta=0, size=3):
        off=location(b,n)+delta;bank=(off-16)//8192
        bs=list(b['raw'][off:off+size]);banks=[bank]
        if bank==127:
            assert list(b['raw'][16+125*8192+(off-16)%8192:16+125*8192+(off-16)%8192+size])==bs
            banks=[125,127]
        return dict(pc=address(b,n)+delta,banks=banks,bytes=bs,source_symbol=n,source_delta=delta)
    h={k:hook(n)for k,n in dict(PhysicalPickup='MarioSourcePowerupCollision',AreaMusic='GetAreaMusic',NmiEntry='NonMaskableInterrupt',IrqEntry='IrqScrollSplit').items()}
    nd=address(b,'NmiDisable');off=location(b,'GameLoop')
    assert b['raw'][off:off+5]==bytes([169,255,141,nd&255,nd>>8]);h['GameLoopOwned']=hook('GameLoop',5)
    for k,n,opcode in [('GameLoopFinish','GameLoop',96),('NmiReturn','NonMaskableInterrupt',64),('IrqReturn','IrqScrollSplit',64)]:
        d=int(b['syms'][n]['size'],0)-1;assert b['raw'][location(b,n)+d]==opcode;h[k]=hook(n,d,1)
    # Bind the real star-only contact branch, not generic shell/weapon defeat.
    start=location(b,'PlayerEnemyCollision');star=address(b,'StarInvincibleTimer');dest=address(b,'ShellOrBlockDefeat')
    pattern=bytes([173,star&255,star>>8,240,6,76,dest&255,dest>>8])
    hits=[i for i in range(300)if b['raw'][start+i:start+i+len(pattern)]==pattern]
    assert len(hits)==1,('Exact Star contact source sequence',hits)
    h['StarContact']=hook('PlayerEnemyCollision',hits[0]+5)
    # Actual popup INC occurs after DEC48..42; the source predecrement compare is43.
    start=location(b,'FloateyNumbersCore');life=address(b,'NumberofLives')
    pattern=bytes([238,life&255,life>>8,169]);hits=[i for i in range(93)if b['raw'][start+i:start+i+4]==pattern]
    assert len(hits)==1;d=hits[0];h['LifeIncrement']=hook('FloateyNumbersCore',d)
    extra=b['raw'][start+d+4];assert b['raw'][start+d+5:start+d+8]==bytes([141,address(b,'Square2SoundQueue')&255,address(b,'Square2SoundQueue')>>8])
    start=location(b,'MarioSourcePowerupCollision');aq=address(b,'AreaMusicQueue')
    pattern=bytes([169,35,141,star&255,star>>8,169,64,141,aq&255,aq>>8])
    assert sum(b['raw'][start+i:start+i+10]==pattern for i in range(120))==1
    off=location(b,'PostDmaMaskEnable');mirror=address(b,'Mirror_PPUMASK')
    load=bytes([165,mirror])if mirror<256 else bytes([173,mirror&255,mirror>>8])
    assert b['raw'][off-3:off]==b'\x8d\x14\x40'and b['raw'][off:off+len(load)+3]==load+b'\x8d\x01\x20'
    h['DmaComplete']=hook('PostDmaMaskEnable',len(load))
    return h, extra


def actor(q,kind,slot,pickup,character):
    y=q.get('Player_Y_Position')-8;assert 24<=y<=200
    for n,v in dict(Enemy_Flag=1,Enemy_ID=kind,Enemy_State=128 if kind==46 else 0,
        Enemy_BoundBoxCtrl=3 if kind==46 else 9,Enemy_X_Position=q.get('Player_X_Position'),
        Enemy_PageLoc=q.get('Player_PageLoc'),Enemy_Y_Position=y,Enemy_Y_HighPos=1,
        Enemy_X_Speed=0,Enemy_Y_Speed=0,Enemy_Y_MoveForce=0,Enemy_MovingDir=1,
        Enemy_SprAttrib=0,EnemyOffscrBitsMasked=0,Enemy_CollisionBits=0).items():q.set(n,v,slot)
    if pickup is not None:
        for n,v in dict(PowerUpType=pickup,InvPickupOwner=character,InvPickup=252).items():q.set(n,v,slot)


def campaign(b,identity,mode,hooks):
    _,character,variant_name,variant=BASE[identity];q=Arena(b,character)
    q.put(CrossoverBehaviorVersion=mode,OperMode_Task=3,AreaType=1,PlayerStatus=0,
          Player_X_Position=112,Player_PageLoc=0,Player_Y_Position=176,Player_State=0,
          ScreenLeft_PageLoc=0,ScreenLeft_X_Pos=0,ScreenRight_PageLoc=0,ScreenRight_X_Pos=255,
          ScrollLock=1,Player_CollisionBits=255,Player_MovingDir=1)
    if variant_name:q.set(variant_name,variant)
    # Standalone source cold context only: native profile obtains this from menu.
    q.array('GameTimerDisplay',[3,9,9]);q.invoke('InventoryInit');q.invoke('CrossoverGraphicsBank')
    for n in ['Block_Buffer_1','MmSolidTerrain','MmBrickHealth']:q.array(n,[0]*416)
    for page in range(2):
        for row in [11,12]:
            for col in range(16):q.set('Block_Buffer_1',84,page*208+row*16+col)
    for i in range(6):q.set('Enemy_Flag',0,i);q.set('Enemy_CollisionBits',0,i)
    calls=0;phase='settle';hits={n:0 for n in ['PhysicalPickup','StarContact','LifeIncrement','AreaMusic']}
    trace=[];original=NesMPU.step
    lookup={(h['pc'],bank):name for name,h in hooks.items() for bank in h['banks']if name in hits}
    def step(c):
        bank=q.m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else -1
        name=lookup.get((c.pc,bank))
        if name and phase!='settle':
            if name=='AreaMusic':
                if phase=='expiry':assert q.get('StarInvincibleTimer')==4 and q.get('IntervalTimerControl')==0;hits[name]+=1
            else:
                if name=='PhysicalPickup':assert c.x==5 and q.get('PowerUpType',5)==(2 if phase=='star'else 3)
                elif name=='StarContact':assert phase=='contact'and c.x==0 and q.get('StarInvincibleTimer')>0
                elif name=='LifeIncrement':assert phase=='life'and c.x==5 and q.get('FloateyNum_Timer',5)==42 and q.get('NumberofLives')==lives
                hits[name]+=1
        original(c)
    def snapshot():return [q.get(p['name'],p['index']+i)for p in resources(identity)for i in range(p['count'])]
    def main():
        nonlocal calls
        q.set('SavedJoypadBits',0);calls+=1
        _,writes=q.invoke('GameLoop')
        if phase!='settle':
            assert snapshot()==initial,('No health/tier/inventory outcome changes',identity,phase,calls)
            assert q.get('InjuryTimer')==0 and q.get('MmDeathFlag')==0 and q.get('GameEngineSubroutine')==8
        return writes
    NesMPU.step=step
    try:
        for _ in range(30):main()
        initial=snapshot();lives=q.get('NumberofLives');assert q.get('StarInvincibleTimer')==0
        phase='star';actor(q,46,5,2,character);music=[]
        for age in range(20):
            writes=main();music += [w['value']for w in writes if w['address']==address(b,'AreaMusicQueue')]
            if q.get('StarInvincibleTimer')>0:break
        else:raise AssertionError(('Actual Star collection',identity))
        assert hits['PhysicalPickup']==1 and q.get('StarInvincibleTimer')==35 and music==[64]and q.get('Enemy_Flag',5)==0
        trace.append(dict(event='actual-Star-grant',call=calls,timer=35,music_requests=music))
        phase='contact';actor(q,6,0,None,character)
        for age in range(20):
            main()
            if q.get('Enemy_State',0)&32:break
        else:raise AssertionError(('Actual protected enemy contact',identity))
        assert hits['StarContact']==1;trace.append(dict(event='actual-star-contact-defeat',call=calls,enemy_state=q.get('Enemy_State',0)))
        phase='expiry';restore=[]
        for age in range(900):
            writes=main();restore += [w['value']for w in writes if w['address']==address(b,'AreaMusicQueue')]
            if q.get('StarInvincibleTimer')==0:break
        else:raise AssertionError(('Natural Star expiry',identity))
        assert hits['AreaMusic']==1 and restore==[1]
        trace.append(dict(event='natural-expiry-after-real-area-restore',call=calls,restore_requests=restore))
        phase='life';actor(q,46,5,3,character);life_sound=[];gain_at=None
        for age in range(70):
            writes=main();life_sound += [w['value']for w in writes if w['address']==address(b,'Square2SoundQueue')]
            assert q.get('NumberofLives')==lives+int(hits['LifeIncrement']>0)
            if hits['LifeIncrement']and gain_at is None:gain_at=calls
            if hits['LifeIncrement']and q.get('FloateyNum_Control',5)==0:break
        else:raise AssertionError(('Physical1-Up gain and popup cleanup',identity))
        assert hits['PhysicalPickup']==2 and hits['LifeIncrement']==1 and q.get('Enemy_Flag',5)==0
        trace.append(dict(event='physical1-Up-delayed-gain-and-cleanup',gain_call=gain_at,cleanup_call=calls,initial_lives=lives,final_lives=q.get('NumberofLives'),sound_requests=life_sound))
    finally:NesMPU.step=original
    return dict(passed=True,native_run=False,identity=identity,full_GameLoop_calls=calls,real_source_hooks=hits,events=trace,
                resource_fields=resources(identity),scope='Standalone real CPU cold source initialization, full collision/Main/popup/timer calls; logical typed mature actors, flat map and neutral input. No native menu/PPU/audio/interrupt claim; life baseline0 comes from zero-RAM source harness, never fixture life seeds. Native profile must use genuine cold-menu lives.')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--identity',choices=PILOTS,required=True)
    p.add_argument('--mode',choices=['easy','hard'],default='hard');p.add_argument('--output',type=Path,required=True)
    p.add_argument('--rom',type=Path,default=R/'build/mega_proto_body_palette_9ea.nes');a=p.parse_args()
    rom=a.rom.resolve();out=a.output.resolve();assert sha(rom)==EXPECTED
    assert out.is_relative_to(R/'build')and(not out.exists()or all(x.name.startswith('source-negative-')for x in out.iterdir())),'Never overwrite bound preparation'
    fixture=R/'tests/current-shared-star-life.lua';guard=R/'tools/audit/current_pit_powerups_v3.lua'
    text=fixture.read_text();old=guard.read_text();first='-- All callback registration is startup-static.';last='emu.addEventCallback(function()\n if not entered'
    assert text[text.index(first):text.index(last)]==old[old.index(first):old.index(last)]
    assert text.count('emu.write(')==2 and 'removeMemoryCallback'not in text and 'dofile('not in text
    assert not set(ALLOWED)&set(BANS)
    b=scoped_load(rom);hooks,extra=hooks_for(b);menu,character,variant_name,variant=BASE[a.identity]
    names=set(ALLOWED)|set(BANS)|set(MOTION)|{p['name']for p in resources(a.identity)}
    names|=set(re.findall(r"[rw]\('([A-Za-z_][A-Za-z_0-9]*)'",text))
    names|=set(re.findall(r'\bC\.ram\.([A-Za-z_][A-Za-z_0-9]*)',text))
    names|=set(re.findall(r"'([A-Za-z_][A-Za-z_0-9]*)'",text))&set(b['syms'])
    if variant_name:names.add(variant_name)
    ram={n:address(b,n)for n in names};assert all(isinstance(v,int)for v in ram.values()),'Every bare callback range and dynamic/literal RAM name must resolve'
    mode=int(a.mode=='hard');out.mkdir(exist_ok=True,parents=True)
    try:source=campaign(b,a.identity,mode,hooks)
    except Exception as e:
        put(out/('source-negative-'+str(len(list(out.glob('source-negative-*')))+1)+'.json'),dict(passed=False,native_run=False,error=repr(e),ROM_sha256=EXPECTED,fixture_sha256=sha(fixture),tool_sha256=sha(__file__)))
        raise
    scope='One Star2 and1-Up3 physical mature pickup; actual protected Goomba contact/defeat, natural Star expiry and native level-music request, delayed popup life gain/cleanup. Typed map/actor scenes only; no natural reveal/RNG/drop eligibility, original melody/fidelity, later vulnerability, death/life rollover, every-pixel or full-roster claim.'
    cfg=dict(ROM_sha256=EXPECTED,identity=a.identity,character=character,menu=menu,variant_name=variant_name,variant=variant,mode=mode,
        hooks=hooks,ram=ram,navigation=navigation(b['raw'],lambda n:location(b,n),menu),resources=resources(a.identity),motion=MOTION,
        setup_allowed={n:True for n in ALLOWED},resource_bans={n:True for n in BANS},star_music=64,extra_life_sfx=extra,scope=scope,
        dma_store_return=address(b,'PostDmaMaskEnable'),smc=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2],
        metatiles={n:dict(bank=(location(b,n)-16)//8192,offset=(location(b,n)-16)%8192)for n in ['MTileTopLeft','MTileTopRight','MTileBotLeft','MTileBotRight','MTileAttribute']})
    put(out/'config.json',cfg);put(out/'source-controls.json',dict(source,hardware_guard_literal_exact=True,all_bare_dynamic_literal_RAM_bound=True,all37_not_admitted=True))
    (out/'run.lua').write_text('CURRENT_SHARED_STAR_LIFE='+lua(cfg)+'\ndofile([=['+fixture.as_posix()+']=])\n',newline='\n')
    argv=[sys.executable,'-B',str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(out/'native'),str(out/'run.lua'),str(rom),'--timeout','1200','--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
    put(out/'command.json',dict(PREPARED_DO_NOT_RUN=True,ROOT_owns_native_lease=True,argv=argv))
    paths={rom,rom.with_suffix('.dbg'),rom.with_suffix('.lbl'),fixture,Path(__file__),guard,R/'build/mega_proto_body_palette_9ea_handoff.json'}
    paths|={R/'tools/audit'/n for n in ['run_mesen_isolated.py','capture_budget.py','current_roster_compact_11_v1.py']}
    paths|={R/'tools/run_mesen.py',Path('C:/Mesen2/Mesen.exe'),Path('C:/Mesen2/MesenCore.dll'),Path('C:/Mesen2/settings.json')}
    paths|={out/n for n in ['config.json','source-controls.json','run.lua','command.json']}
    # Bind the literal compiled common source and explicit sparse combined inputs;
    # no full source/runtime copy, and no assertion that live canonical is ab221e.
    paths|={R/'src'/n for n in ['collision.s','mario_source.s','game.s','common.s','reset.s','inventory.s','little_mac.s','vic_viper.s','parodius_adapter.s','tmnt_dispatch.s','tmnt_equipment.s','kirby.s','mike_jones.s','x5_mario3.s']if(R/'src'/n).is_file()}
    for module in list(sys.modules.values()):
        f=getattr(module,'__file__',None)
        if f and('py65'in f or str(R/'tools/audit')in f)and Path(f).is_file():paths.add(Path(f))
    put(out/'prepared-not-run.json',dict(status='PREPARED_DO_NOT_RUN',native_run=False,passed=False,goal_complete=False,ROM_sha256=EXPECTED,
        identity=a.identity,actual_numeric_mode=mode,source_calls=source['full_GameLoop_calls'],scope=scope,
        caps=dict(wall_frames=3500,updates=1800,host_seconds=1200,files=64,bytes=2000000000,PNGs=4,perframe_files=0),
        setup='Actual GameLoop+5/NmiDisableFF map/actor/motion scene writes only. No StarTimer/lives/health/ownership/tier/ammo/injury/kill/sound/music outcomes seeded. Ship native live object position retained. Genuine compiled19-node menu BFS/Select alternate and numeric mode readback.',
        limitations='Standalone source CPU pilots only. Actual Lua/menu/physical source and hardware assertions require separately authorized native runs. No other34 identities admitted until first native pilots are stable.',
        bindings=[dict(path=str(x.resolve()),bytes=x.stat().st_size,sha256=sha(x))for x in sorted(paths)]))
    print(json.dumps(dict(prepared=True,native_run=False,identity=a.identity,source_calls=source['full_GameLoop_calls'],ready=str(out/'prepared-not-run.json'),ready_sha256=sha(out/'prepared-not-run.json'))))


if __name__=='__main__':main()
