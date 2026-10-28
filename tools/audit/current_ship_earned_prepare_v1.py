"""Prepare four bounded earned ship profiles on frozen5a. Never launches Mesen."""
from pathlib import Path
import argparse, hashlib, json, re, sys
from current_ship_earned_cpu_v1 import EXPECTED, ROM, plans, ACTOR, ENV, PICKUP, campaign
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location
from current_roster_compact_11_v1 import lua, navigation

ROOT=Path(__file__).resolve().parents[2]
FIXTURE=ROOT/'tools/audit/current_ship_earned_v1.lua'
NAMES=['vic','octopus','twinbee','pentarou']
FORBIDDEN='PlayerStatus PlayerSize NumberofLives VvAlive VvInitialized VvVariant VvPrevious VvHeld VvFresh VvMeter VvSpeed VvGun VvMissile VvOptions VvShield VvAutoFire VvHurt VvLife VvNeedEntry VvObjX VvObjY VvObjAnim VvObjSub PnActive PnType PnX PnY PnGun PnSkin PnBellFlags PnRedRemaining PnRedSelected PnRedReady PnAux PnBombCapturePending PnBombPaletteReady PnMissing InvOwnedLo InvOwnedHi InvAmmo InvSelected InvHudActive InvHudDirty GuestPowerupActive GuestPowerupTarget Player_X_Position Player_Y_Position Player_PageLoc Player_State InjuryTimer GuestHurtTicks MmDeathFlag CheatInvincible'.split()
FINAL='VvMeter VvSpeed VvGun VvMissile VvOptions VvShield PnAux PnSkin PnBellFlags PnRedRemaining NumberofLives'.split()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
bind=lambda p:dict(path=str(Path(p).resolve()),bytes=Path(p).stat().st_size,sha256=sha(p))
put=lambda p,z:Path(p).write_text(json.dumps(z,indent=2)+'\n',newline='\n')

def preflight(b,text,variant,source_paths=None):
    assert sha(ROM)==EXPECTED
    parent=ROOT/'tools/audit/current_rygar_powerups_v1.lua';old=parent.read_text()
    start='-- All callback registration is startup-static.';stop="hook('DmaComplete',function()\n if not entered"
    expected=old[old.index(start):old.index('emu.addEventCallback(function()\n if not entered')]
    actual=text[text.index(start):text.index(stop)]
    assert actual==expected and len(actual.encode())==4058
    assert text.count('emu.write(')==2 and not any(s in text for s in ['removeMemoryCallback','loadSavestate','setState','emu.reset'])
    assert not re.search(r'\b(?:and|or)\d',text),'Lua lexical boundary'
    allowed=set(ACTOR+ENV+PICKUP);assert not allowed&set(FORBIDDEN)
    direct=set(re.findall(r'C\.ram\.([A-Za-z_][A-Za-z_0-9]*)',text))
    names=set(re.findall(r"'([A-Za-z_][A-Za-z_0-9]*)'",text))|allowed|set(FORBIDDEN)|set(FINAL)|direct
    ram={n:address(b,n)for n in names if n in b['syms']}
    needed=set(re.findall(r"[rw]\('([A-Za-z_][A-Za-z_0-9]*)'",text))|allowed|set(FINAL)
    needed|=direct|{'CurrentBank','CurrentBankC','Sprite0HitDetectFlag','Square1SoundQueue','Square2SoundQueue','NoiseSoundQueue'}
    assert not needed-set(ram),sorted(needed-set(ram))
    for n in needed:
        at=ram[n];assert at<0x2000 or 0x5c00<=at<0x8000,('Genuine RAM field',n,hex(at))
    for t in plans(variant):
        if 'field'in t:assert t['field']in ram
    assert b['raw'][location(b,'InvItemCount')+18]==0
    assert b['raw'][location(b,'BoundBoxCtrlData')+12:location(b,'BoundBoxCtrlData')+16]==bytes([2,9,14,21]),'Actual mature pickup box3; fixed flower placement must intersect native point/core'
    for n in ['InvSelectable','InvInitialAmmo','InvMaxAmmo']:
        assert b['raw'][location(b,n)+288:location(b,n)+304]==bytes(16)
    def hook(n,delta=0,size=3,owner=None):
        pos=location(b,n)+delta;pc=address(b,n)+delta;k=(pos-16)//8192;bs=list(b['raw'][pos:pos+size]);banks=[k]
        if k==127:
            owner=owner or n;at=location(b,owner);startpc=address(b,owner);length=int(b['syms'][owner]['size'],0)
            assert length>0 and k==(at-16)//8192 and startpc<=pc<startpc+length
            clone=16+125*8192+(startpc&8191)
            assert b['raw'][clone:clone+length]==b['raw'][at:at+length],('Actual whole copied owner',owner)
            off=(pos-16)%8192;assert b['raw'][16+125*8192+off:16+125*8192+off+size]==bytes(bs);banks=[125,127]
        return dict(pc=pc,banks=banks,bytes=bs,source_symbol=n,source_delta=delta)
    actualOwners=dict(VvTake='VvTake',PnTakeKind='PnTakeKind',BuyVic='VvBuyUpgrade',BuyParodius='PnNativeGear',VicWeapons='VvWeapons',ParodiusWeapons='PnWeapons',VicBody='VvBody',ParodiusBody='PnBody',Defeat='ShellOrBlockDefeat',RedFire='Pb9a86',BombDamage='PnBombWorldDamage',BigDecrement='Pn81fa')
    hooks={key:hook(n)for key,n in actualOwners.items()}
    hooks.update(PhysicalPickup=hook('VvPickupDispatch'),NmiEntry=hook('NonMaskableInterrupt'),IrqEntry=hook('IrqScrollSplit'))
    assert b['raw'][location(b,'GameLoop'):location(b,'GameLoop')+5]==bytes([169,255,141,address(b,'NmiDisable')&255,address(b,'NmiDisable')>>8])
    hooks['GameLoopOwned']=hook('GameLoop',5)
    for key,n,op in [('GameLoopFinish','GameLoop',96),('NmiReturn','NonMaskableInterrupt',64),('IrqReturn','IrqScrollSplit',64)]:
        delta=int(b['syms'][n]['size'],0)-1;assert b['raw'][location(b,n)+delta]==op;hooks[key]=hook(n,delta,1)
    post=location(b,'PostDmaMaskEnable');mirror=address(b,'Mirror_PPUMASK');load=bytes([165,mirror])if mirror<256 else bytes([173,mirror&255,mirror>>8])
    assert b['raw'][post-3:post]==b'\x8d\x14\x40' and b['raw'][post:post+len(load)+3]==load+b'\x8d\x01\x20'
    hooks['DmaComplete']=hook('PostDmaMaskEnable',len(load),owner='OAMandReadJoypad')
    for n in re.findall(r"hook\('([A-Za-z_][A-Za-z_0-9]*)'",text):assert n in hooks,n
    nav=navigation(b['raw'],lambda n:location(b,n),17)
    assert b['raw'][location(b,'X5MenuCharacters')+17]==18
    source=[]
    for i,mode in enumerate(['easy','hard']):
        p=source_paths[i] if source_paths else ROOT/f'build/current-5a-{NAMES[variant]}-{mode}-earned-source-v5.json';z=json.loads(p.read_text())
        assert z['passed']and not z['native_run']and not z['Lua_executed']and z['ROM_sha256']==EXPECTED
        assert z['tool_sha256']==sha(ROOT/'tools/audit/current_ship_earned_cpu_v1.py')
        assert z['mode']==int(mode=='hard')and z['variant']==variant
        assert [c['actual_prepared_type_owner_item']for c in z['actual_VvPrepareDispatch_controls']]==[[1,255,252]]*2
        assert [q['name']for q in z['cases']]==[q['name']for q in plans(variant)]
        source.append(p)
    cfg=dict(ROM_sha256=EXPECTED,character=18,variant=variant,mode=1,ram=ram,hooks=hooks,
        setup_allowed={n:True for n in sorted(allowed)},forbidden={n:True for n in FORBIDDEN},final_fields=FINAL,
        owner_hooks=list(actualOwners),plan=plans(variant),navigation=nav,update_cap=5000,
        dma_store_return=address(b,'PostDmaMaskEnable'),
        smc=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2],
        metatiles={n:dict(bank=(location(b,n)-16)//8192,offset=(location(b,n)-16)%8192)for n in ['MTileTopLeft','MTileTopRight','MTileBotLeft','MTileBotRight','MTileAttribute']},
        scope='Actual source-prepared mature ship capsules (ordinary reward requests0/1 both map to type1) to each native bar purchase/cap refusal; actual shots/defeats/options/shield debit. Parodius adds !? reset, roulette, first Gold500, Blue bomb, three Red charges, full Big duration/restoration/protected contact, White1UP. Typed complete mature pickup/default Goomba/empty map only; no reveal/rise/natural drops/RNG/emergence/star/common1UP/damage-death/reacquire/terrain firing/campaign/allposes/allpixels/audio-fidelity or general FPS claim. Easy source only; this command is Hard1.')
    controls=dict(passed=True,native_run=False,Lua_VM_executed=False,ROM_sha256=EXPECTED,variant=variant,
        source_campaigns=[bind(p)for p in source],source_GameLoops=sum(json.loads(p.read_text())['GameLoop_calls']for p in source),
        guard_bytes=len(actual.encode()),guard_sha256=hashlib.sha256(actual.encode()).hexdigest(),
        strict_guard_literal=True,all_literal_and_dynamic_RAM_names_compiled=True,
        no_equipment_or_resource_or_player_position_seeds=True,
        allowed_setup_names=sorted(allowed),forbidden_setup_names=FORBIDDEN,
        genuine_cloned_NMI_and_DMA_owner_bytes_verified=True,
        mature_pickup_compiled_box=[2,9,14,21],actual_collection_hook='VvPickupDispatch before erase; full GameLoop campaigns record real slot5 PowerUpObject/mature state/type1; actual producer maps both0/1 requests to1',
        Big_timer='Actual $04FF /1279 native low-byte decrements before complete exit animation; not1536',
        native_input_polled_not_source_mirror=True,
        source_model_limit='Actual assembled GameLoop + VRAM queue consumer; initialized CPU arena and direct joypad per GameLoop are not a native poll/PPU/palette/IRQ or screenshot result. Native cold position is inherited, not set to CPU initial80/120. CPU arena uses genuine empty source enemy list; native inherits the legal started level parser.')
    return cfg,controls,source,parent

def main():
    global ROM,EXPECTED
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--variant',type=int,choices=range(4),required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--rom',type=Path,default=ROM);p.add_argument('--expected-sha256',default=EXPECTED);a=p.parse_args()
    out=a.output.resolve();assert not out.exists()and out.is_relative_to(ROOT/'build')
    original=EXPECTED;ROM=a.rom.resolve();EXPECTED=a.expected_sha256;assert sha(ROM)==EXPECTED
    b=scoped_load(ROM);text=FIXTURE.read_text();fresh_source=None
    if EXPECTED!=original:
        # Run genuine target instructions; do not retag the immutable5a result.
        out.mkdir();fresh_source=[]
        for mode in [0,1]:
            z=campaign(b,a.variant,mode);z.update(ROM_sha256=EXPECTED,native_run=False,Lua_executed=False,tool_sha256=sha(ROOT/'tools/audit/current_ship_earned_cpu_v1.py'),scope='Fresh same compiled campaign on explicit new target; no old5a native/source PASS transfer.')
            f=out/('source-hard.json' if mode else 'source-easy.json');put(f,z);fresh_source.append(f)
    cfg,controls,source,parent=preflight(b,text,a.variant,fresh_source)
    out.mkdir(exist_ok=True);put(out/'config.json',cfg);put(out/'source-controls.json',controls)
    (out/'run.lua').write_text('CURRENT_SHIP_EARNED='+lua(cfg)+'\ndofile([=['+FIXTURE.as_posix()+']=])\n',newline='\n')
    argv=[sys.executable,'-B',str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(out/'native'),'--emulator','C:/Mesen2/Mesen.exe',str(out/'run.lua'),str(ROM),'--timeout','1200','--option=--doNotSaveSettings','--option=--nes.removeSpriteLimit=false','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
    put(out/'command.json',dict(PREPARED_DO_NOT_RUN=True,ROOT_owns_native_lease=True,argv=argv))
    paths=[ROM,ROM.with_suffix('.dbg'),ROM.with_suffix('.lbl'),Path(__file__),FIXTURE,parent,*source]
    paths += [ROOT/'tools/audit'/n for n in ['current_ship_earned_cpu_v1.py','link_pit_rygar_sophia_audit_cpu.py','check_tmnt_render_oa.py','verify_native_relocation.py','current_roster_compact_11_v1.py','final_inventory_compact_capture_v1.py','run_mesen_isolated.py','capture_budget.py']]+[ROOT/'tools/run_mesen.py']
    # Canonical source may advance independently. Actual compiled ROM/DBG/LBL
    # and target-specific CPU controls are inputs; no mutable src/ tree binding.
    paths += [out/n for n in ['config.json','run.lua','source-controls.json','command.json']]
    put(out/'prepared-not-run.json',dict(status='PREPARED_DO_NOT_RUN',native_run=False,passed=False,goal_complete=False,
        ROM_sha256=EXPECTED,character=18,variant=a.variant,numeric_mode=1,cases=len(cfg['plan']),
        source_controls_passed=True,Lua_VM_executed=False,strict_hardware_guard_literal_bytes=4058,
        caps=dict(actual_updates=5000,wall_frames=8000,host_seconds=1200,bytes=2000000000,files=64,PNGs=8),
        resources='No tested meter/equipment/options/shield/bell charge/owned skin/ammo/lives/player position/health seeds. Only complete typed mature pickup actors or fresh default-health NPC targets and logical/visible empty scene are staged at native GameLoop+5. Native movement, input edge, resource grant/debit, projectile lifetime and cleanup remain real.',
        source_modes=['Easy0','Hard1'],native_prepared_modes=['Hard1'],scope=cfg['scope'],
        limitations='This is not a native PASS or Lua-VM execution. Screenshots require ROOT whole-image review and do not establish allpixel/everypose visibility. CPU modeled source bounds are not a 60Hz, queue timing or real input-poll guarantee.',
        bindings=[bind(q)for q in dict.fromkeys(paths)]))
    ready=out/'prepared-not-run.json';z=json.loads(ready.read_text())
    assert all(sha(q['path'])==q['sha256']for q in z['bindings'])
    print(json.dumps(dict(prepared=True,native_run=False,variant=a.variant,ready=str(ready),sha256=sha(ready),bindings=len(z['bindings']),cases=len(cfg['plan']),command=str(out/'command.json'))))

if __name__=='__main__':main()
