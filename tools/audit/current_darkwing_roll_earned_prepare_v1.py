"""Prepare one small Hard earned component profile. Never launch an emulator."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import sys

from current_darkwing_roll_earned_cpu_v1 import campaign, plans, ALLOWED, FORBIDDEN, EXPECTED
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location
from observe_chip_committed_write import lua
from current_roster_compact_11_v1 import navigation

ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')
GUARD_SHA='2b3aa5da62ebdd76723bc3ad87991e63695f15ac151213718f58b55f0211d70c'


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--identity',choices=['darkwing','roll'],required=True)
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();a.output=a.output.resolve()
    assert a.output.is_relative_to(ROOT/'build') and not a.output.exists()
    rom=ROOT/'build/mega_proto_body_palette_9ea.nes';assert sha(rom)==EXPECTED
    fixture=ROOT/'tools/audit/current_darkwing_roll_earned_v1.lua'
    guard=ROOT/'tools/audit/current_rygar_powerups_v1.lua'
    text=fixture.read_text();old=guard.read_text()
    begin='-- All callback registration is startup-static.';end='emu.addEventCallback(function()\n if not entered'
    block=text[text.index(begin):text.index(end)]
    assert block==old[old.index(begin):old.index(end)]
    assert len(block.encode())==4058 and hashlib.sha256(block.encode()).hexdigest()==GUARD_SHA
    assert text.count('emu.write(')==2 and 'removeMemoryCallback'not in text and 'dofile('not in text
    assert not set(ALLOWED)&set(FORBIDDEN)
    assert not re.search(r"w\('(DwHealth|DwGas|DwAdaptor|DwMode|RlHealth|RlEnergy|RlFoodKind|PlayerStatus|InvSelected|InvAmmo|GameTimerDisplay)'",text)
    plan=plans(a.identity);assert len(plan)==(14 if a.identity=='darkwing'else 16)
    assert sum(bool(t.get('image'))for t in plan)==8
    b=scoped_load(rom);raw=b['raw']
    if a.identity=='darkwing':
        for name,values in [('DwLaunch::Cost',[0,2,3,2]),('DwLaunch::Cap',[3,1,2,1])]:
            assert list(raw[location(b,name):location(b,name)+len(values)])==values
    source=campaign(b,a.identity)
    assert source['passed'] and source['GameLoop_calls']<=3000 and source['plan']==plan
    def hook(n,delta=0,size=3):
        p=location(b,n)+delta;k=(p-16)//8192;pc=address(b,n)+delta;bs=list(raw[p:p+size]);banks=[k]
        if k==127:
            clone=16+125*8192+(p-16)%8192
            assert raw[clone:clone+size]==bytes(bs);banks=[125,127]
        return dict(pc=pc,banks=banks,bytes=bs,source_symbol=n,source_delta=delta)
    mapping=dict(PhysicalPickup='MarioSourcePowerupCollision',DamageEnemy='MegaManWeapons::DamageEnemy',NmiEntry='NonMaskableInterrupt',IrqEntry='IrqScrollSplit')
    mapping.update(dict(CollectOwner='DwCollectPickup',GiveItem='DwGiveItem',Launch='DwLaunch',ShotInit='DwShotInit')if a.identity=='darkwing'else dict(CollectOwner='RlCollect',ChargeSpawn='RlWeapons::Spawn',ChargeReset='RlWeapons::ResetCharge',Refill='RlRefillDispatch',RefillEnergySave='RlRefillDispatch::EnergySave',RefillHealthSave='RlRefillDispatch::HealthSave'))
    hooks={k:hook(v)for k,v in mapping.items()}
    assert raw[location(b,'GameLoop'):location(b,'GameLoop')+5]==bytes([0xa9,255,0x8d,address(b,'NmiDisable')&255,address(b,'NmiDisable')>>8])
    hooks['GameLoopOwned']=hook('GameLoop',5)
    for key,n,op in [('GameLoopFinish','GameLoop',0x60),('NmiReturn','NonMaskableInterrupt',0x40),('IrqReturn','IrqScrollSplit',0x40)]:
        delta=int(b['syms'][n]['size'],0)-1;assert raw[location(b,n)+delta]==op;hooks[key]=hook(n,delta,1)
    mirror=address(b,'Mirror_PPUMASK');load=bytes([0xa5,mirror])if mirror<256 else bytes([0xad,mirror&255,mirror>>8])
    post=location(b,'PostDmaMaskEnable')
    assert raw[post-3:post]==b'\x8d\x14\x40'and raw[post:post+len(load)+3]==load+b'\x8d\x01\x20'
    hooks['DmaComplete']=hook('PostDmaMaskEnable',len(load))
    # Genuine fixed-bank clone proof covers whole owners, not bank waivers.
    clone_owners={}
    for n in ['NonMaskableInterrupt','OAMandReadJoypad']:
        start=location(b,n);size=int(b['syms'][n]['size'],0);assert(start-16)//8192==127
        clone=16+125*8192+(start-16)%8192;assert raw[start:start+size]==raw[clone:clone+size]
        clone_owners[n]=dict(bytes=size,banks=[125,127],sha256=hashlib.sha256(raw[start:start+size]).hexdigest())
    names=set(re.findall(r"'([A-Za-z_][A-Za-z_0-9]*)'",text))|set(ALLOWED)|set(FORBIDDEN)
    names|=set('DwHealth DwGas DwAdaptor DwMode RlHealth RlEnergy RlFoodKind RlChargeFired RlReady DarkwingVariant RlVariant CurrentBank CurrentBankC Sprite0HitDetectFlag Square1SoundQueue Square2SoundQueue NoiseSoundQueue'.split())
    ram={n:address(b,n)for n in names if n in b['syms']and(address(b,n)<0x2000 or 0x5c00<=address(b,n)<0x8000)}
    literal=set(re.findall(r"[rw]\('([A-Za-z_][A-Za-z_0-9]*)'",text))|set(re.findall(r'C\.ram\.([A-Za-z_][A-Za-z_0-9]*)',text))|set(ALLOWED)|set(FORBIDDEN)
    dynamic=set('DwHealth DwGas DwAdaptor DwMode RlHealth RlEnergy RlFoodKind RlChargeFired RlReady DarkwingVariant RlVariant RgShotType MmBulletType Square1SoundQueue Square2SoundQueue NoiseSoundQueue'.split())
    assert not(literal|dynamic)-ram.keys(),('Actual RAM name absent',sorted((literal|dynamic)-ram.keys()))
    character,slot,variant=(12,8,'DarkwingVariant')if a.identity=='darkwing'else(9,9,'RlVariant')
    assert raw[location(b,'X5MenuCharacters')+slot]==character
    cfg=dict(ROM_sha256=EXPECTED,identity=a.identity,character=character,mode=1,variant_ram=variant,ram=ram,hooks=hooks,
        setup_allowed={n:True for n in ALLOWED},forbidden=FORBIDDEN,plan=plan,hardware_guard_sha256=GUARD_SHA,
        dma_store_return=address(b,'PostDmaMaskEnable'),
        navigation=navigation(raw,lambda n:location(b,n),slot),
        smc=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2],
        metatiles={n:dict(bank=(location(b,n)-16)//8192,offset=(location(b,n)-16)%8192)for n in ['MTileTopLeft','MTileTopRight','MTileBotLeft','MTileBotRight','MTileAttribute']})
    a.output.mkdir(parents=True)
    put(a.output/'config.json',cfg);put(a.output/'source-controls.json',source)
    (a.output/'run.lua').write_text('CURRENT_DARKWING_ROLL_EARNED='+lua(cfg)+'\ndofile([=['+fixture.as_posix()+']=])\n',newline='\n')
    argv=[sys.executable,'-B',str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(a.output/'native'),'--emulator','C:/Mesen2/Mesen.exe',str(a.output/'run.lua'),str(rom),'--timeout','1200','--option=--doNotSaveSettings','--option=--nes.removeSpriteLimit=false','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
    put(a.output/'command.json',dict(PREPARED_DO_NOT_RUN=True,ROOT_owns_native_lease=True,argv=argv))
    tools=['current_darkwing_roll_earned_cpu_v1.py','current_rygar_powerups_prepare_v1.py','current_roster_compact_11_v1.py','link_pit_rygar_sophia_audit_cpu.py','check_tmnt_render_oa.py','verify_native_relocation.py','observe_chip_committed_write.py','run_mesen_isolated.py','capture_budget.py']
    sources=['darkwing.s','darkwing_core.s','darkwing_weapons.s','darkwing_pickups.s','darkwing_recovery.s','roll.s','roll_core.s','roll_weapons.s','roll_dispatch.s','roll_state.inc','roll_motion.inc','inventory.s','inventory_drops.s','roster.s','game.s','object.s','mario_source.s']
    files=[rom,rom.with_suffix('.dbg'),rom.with_suffix('.lbl'),fixture,Path(__file__),guard,ROOT/'tools/run_mesen.py']+[ROOT/'tools/audit'/n for n in tools]+[ROOT/'src'/n for n in sources]+[a.output/n for n in ['config.json','source-controls.json','run.lua','command.json']]
    files += [ROOT/'build'/n for n in ['mm_player_prg_owner_metasprite_engine.s','mm_player_prg_owner_megaman_weapons.s','proto_normal_palette_ack_9ea_source.s','mega_proto_body_palette_9ea_build.json']]
    assert all(p.is_file()for p in files)
    ready=dict(status='PREPARED_DO_NOT_RUN',native_run=False,passed=False,goal_complete=False,ROM_sha256=EXPECTED,identity=a.identity,character=character,actual_numeric_mode=1,plan=plan,
        source_CPU_passed=True,source_GameLoop_calls=source['GameLoop_calls'],literal_hardware_guard_bytes=4058,literal_hardware_guard_sha256=GUARD_SHA,whole_clone_owners=clone_owners,
        all_literal_dynamic_RAM_names_reconciled=True,Lua_VM_executed=False,
        caps=dict(updates=3000,wall_frames=8000,host_seconds=1200,bytes=2_000_000_000,files=64,PNGs=8),
        setup='Complete logical+visible scene/mature native actors/default-health NPCs at GameLoop+5. Roll capsules have complete declared type/health-vs-energy/position/velocity/age fields. Real source injury/debit creates deficits. No health/ammo/adaptor/owned/tier/selection/projectile/result writes.',
        limitations='Source CPU and static Lua preparation only, no Lua VM/native/render/audio/cadence claim. Mature collection, not reveal/rise/RNG. No star/1up/allfacings/fullpool/exhaust/cape/hang/campaign claim. All effects/wholeframes require actual native review.',
        bindings=[dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))for p in files])
    put(a.output/'prepared-not-run.json',ready)
    assert all(sha(Path(z['path']))==z['sha256']for z in ready['bindings'])
    print(json.dumps(dict(prepared=True,native_run=False,ready=str(a.output/'prepared-not-run.json'),sha256=sha(a.output/'prepared-not-run.json'),bindings=len(files),source_GameLoop_calls=source['GameLoop_calls'],cases=len(plan))))


if __name__=='__main__':main()
