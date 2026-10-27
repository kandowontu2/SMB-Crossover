"""Prepare two seven-case legal Hard gun galleries; never run an emulator."""
from pathlib import Path
import argparse, ast, json, re, sys
from final_bill_lance_hard_gallery_source_v1 import plans, D, ROOT, sha, put, OWNER_NAMES, EXTRA_OWNERS
PARENT=D/"root-render-audio-palette-hud-union-v2"
SHA="ce635f6e8793d096ba50adec9cdf1fc2dd41fd487e4acd4d0972af03af9ea111"
OLD_SHA="3b112e1d79ba7348f2f7a4c426f4675845a5781017ab74690feb235121a66287"
from final_bill_lance_hard_gallery_source_v2 import BillArena
from final_item_abilities_run import lua
from final_item_abilities_current731_prepare_v1 import protocol, dma_mocks, OLD_DMA
from final_item_abilities_static_prepare_v2 import core_tests, old_core
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location
from parodius_visibility_hud_static_startup_v1 import MOCK


def compose(cfg):
    base=(ROOT/'tools/audit/final_item_matrix_progressive.lua').read_text()
    prefix=base[:base.index('local function seed()')]
    assert prefix.count("assert(n~='PlayerStatus','Power tiers must be acquired');")==1
    prefix=prefix.replace("assert(n~='PlayerStatus','Power tiers must be acquired');",'')
    prefix=prefix.replace("if C.family=='scrooge'and r('DarkwingVariant')~=0 then return{select=true}end",
                          "if r('BillVariant')~=C.variant then return{select=true}end")
    assert OLD_DMA in prefix
    prefix=prefix.replace(OLD_DMA,(ROOT/'tools/audit/final_item_abilities_dma731_v1.lua').read_text()+'\n')
    core=(ROOT/'tools/audit/final_item_abilities_static_return_v1.lua').read_text()
    mechanics=(ROOT/'tools/audit/final_bill_lance_hard_gallery_native_v3.lua').read_text()
    addon=(ROOT/'tools/audit/final_bill_lance_combined_hud_v1.lua').read_text()
    guards=base[base.index('local saved=nil'):base.index('emu.addEventCallback(function()\n if not entered then emu.setInput')]
    tail=base[base.index('emu.addEventCallback(function()\n wall=wall+1'):]
    before="local f=assert(io.open(OUTPUT..'native-progressive.json','w'));f:write(json({passed=true,goal_complete=false,family=C.family,hard=C.hard,cases=records,updates=updates,nmis=nmis,minSP=minSP,apuWrites=apuWrites,irq_scroll_stores=irqStores,hardware_chr_checks=chrChecks,complete_dma_checks=dmaChecks,scope='Actual head-bump/reveal/native full rise; explicit post-rise collision placement; cold selection and source-owned transformation/use. No campaign claim'}));f:close();emu.stop(0)"
    after="cadence:close();local f=assert(io.open(OUTPUT..'native-bill-gallery.json','w'));f:write(json({passed=true,goal_complete=false,lane='B controlled legal use',acquisition=false,family=C.family,variant=C.variant,actual_variant_readback=r('BillVariant'),actual_mode_readback=r('CrossoverBehaviorVersion'),hard=true,cases=records,updates=updates,nmis=nmis,minSP=minSP,apuWrites=apuWrites,irq_scroll_stores=irqStores,hardware_chr_checks=chrChecks,complete_dma_checks=dmaChecks}));f:close();emu.stop(0)"
    assert tail.count(before)==1;tail=tail.replace(before,after).replace("wall<9000,'Bounded progressive fixture '","wall<12000,'Bounded seven-case Bill gallery '")
    captures=(ROOT/'tools/audit/final_item_abilities_pit731_ppu_v1.lua').read_text()
    inputs="emu.addEventCallback(function()if not entered then emu.setInput(menu(),0)else emu.setInput(billInput(),0)end end,emu.eventType.inputPolled)\n"
    return 'FINAL_ITEM_PROGRESSIVE='+lua(cfg)+'\n'+(ROOT/'tools/audit/final_item_abilities_failure.lua').read_text()+'\n'+prefix+core+'\n'+mechanics+'\n'+addon+'\n'+guards+inputs+captures+'\n'+tail+'\nFINAL_ITEM_ABILITIES_STATIC_INSTALL_RETURNS()\n',guards


def terrain_controls(b):
    rows=[]
    for plan in plans():
      for face in [1,2]:
        q=BillArena(b);q.put(PlayerFacingDir=face,Player_MovingDir=face)
        for item in plan['grant_sequence']:q.grant(item)
        col=10 if face==1 else 4
        q.set('Block_Buffer_1',0x54,9*16+col);q.set('MmSolidTerrain',1,9*16+col)
        observed=False;impacts=False
        for tick in range(45):
            c,t=q.buttons(64 if tick==0 else 0)
            impacts=impacts or any(q.get('RgShotImpact',i) for i in range(10))
            if plan['shot_type']in[42,43]:
                crossed=any(q.get('RgShotType',i)==plan['shot_type'] and
                    (q.get('RgShotX',i)>=176 if face==1 else q.get('RgShotX',i)<64)
                    for i in range(10))
                if crossed:assert not impacts;observed=True;break
            elif impacts:observed=True;break
        assert observed,(plan['name'],face)
        rows.append(dict(case=plan['name'],face=face,first_expected_contact_update=tick,
            expected='bypass-plain-ground'if plan['shot_type']in[42,43]else'impact-plain-ground',
            calls=q.calls,scope='Actual complete compiled emission/terrain path in an isolated arena, not native PPU.'))
    return dict(passed=True,source_only=True,native_run=False,cases=len(rows),rows=rows)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();assert not a.output.resolve().is_relative_to(ROOT)
    a.output.mkdir(parents=True,exist_ok=False)
    packet=D/'final-bill-lance-hard-gallery-source-v2'
    prior=json.loads((packet/'proof.json').read_text());assert prior['passed'] and prior['ROM_sha256']==OLD_SHA
    for q in json.loads((packet/'manifest.json').read_text())['bindings']:assert sha(q['path'])==q['sha256']
    assert sha(PARENT/'candidate.nes')==SHA
    b=scoped_load(PARENT/'candidate.nes')
    for n in EXTRA_OWNERS:
        if n in b['syms'] and n not in OWNER_NAMES:OWNER_NAMES.append(n)
    bindings={Path(q['path'])for q in json.loads((packet/'manifest.json').read_text())['bindings']}
    bindings.add(packet/'proof.json');bindings.add(packet/'manifest.json')
    sys.path.insert(0,str(D/'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1'))
    from lupa.lua54 import LuaRuntime
    return_controls=core_tests(LuaRuntime,old_core((ROOT/'tools/audit/final_item_abilities_native.lua').read_text()),
        (ROOT/'tools/audit/final_item_abilities_static_return_v1.lua').read_text())
    dma_controls=dma_mocks(LuaRuntime,(ROOT/'tools/audit/final_item_abilities_dma731_v1.lua').read_text(),dict(dma_protocol=protocol(b)))
    terrain=terrain_controls(b);put(a.output/'terrain-controls.json',terrain)
    def record(ptr,bank):
        off=16+bank*8192+ptr%8192;n=b['raw'][off]
        assert n%4==0 and n<=252
        return dict(address=ptr,bank=bank,bytes=list(b['raw'][off:off+n+1]))
    effects={}
    for i in range(7):
        ptr=b['raw'][location(b,'RgBILLWeaponsRightLo')+i]+256*b['raw'][location(b,'RgBILLWeaponsRightHi')+i]
        effects[f'19:{ptr}']=record(ptr,19)
    for i in range(address(b,'AvArtRightHi')-address(b,'AvArtRightLo')):
        bank=b['raw'][location(b,'AvArtBanks')+i]&127
        for side in ['Right','Left']:
            ptr=b['raw'][location(b,'AvArt'+side+'Lo')+i]+256*b['raw'][location(b,'AvArt'+side+'Hi')+i]
            effects[f'{bank}:{ptr}']=record(ptr,bank)
    mechanics=(ROOT/'tools/audit/final_bill_lance_hard_gallery_native_v3.lua').read_text()
    addon=(ROOT/'tools/audit/final_bill_lance_combined_hud_v1.lua').read_text()
    names=set(re.findall(r"hook\('([^']+)'",mechanics+'\n'+addon))|{'RosterWeapons::SpawnBill','RemainingWeapons::Spawn','NonMaskableInterrupt','IrqScrollSplit','RosterOamReady'}
    names-={'finish'};hooks={}
    for n in names:
        pos=location(b,n);hooks[n]=dict(address=address(b,n),physical_bank=(pos-16)//8192,bytes=list(b['raw'][pos:pos+3]))
    for n,owner in [('finish','GameLoop'),('NmiReturn','NonMaskableInterrupt')]:
        delta=int(b['syms'][owner]['size'],0)-1;pos=location(b,owner)+delta
        assert b['raw'][pos]in[0x60,0x40]
        hooks[n]=dict(address=address(b,owner)+delta,physical_bank=(pos-16)//8192,bytes=[b['raw'][pos]])
    irqpos=location(b,'IrqScrollSplit')
    irq=[address(b,'IrqScrollSplit')+i for i in range(int(b['syms']['IrqScrollSplit']['size'],0)-2)if b['raw'][irqpos+i:irqpos+i+3]==b'\x8d\x05\x20']
    recipe=plans();incremental=[[],[4],[5],[2],[3],[4,1],[6]]
    value=lambda n,i=0:b['raw'][location(b,n)+i]
    for q,grant in zip(recipe,incremental):
        q['incremental_grants']=grant;q['damage_type']=q['shot_type']+27 if q['shot_type']>=32 else [11,12,13][q['shot_type']-1]
        q['sfx']=address(b,'AV_SFX_BILLLASER'if q['shot_type']==42 else'AV_SFX_BILLFLARE')if q['shot_type']>=42 else 0
        i=48+q['expected_selected'];ptr=value('InvNameLo',i)+256*value('InvNameHi',i)
        group=b['segs'][b['syms']['InvNameLo']['seg']];off=int(group['ooffs'],0)+ptr-int(group['start'],0)
        q['hud_name']=list(b['raw'][off:off+7])
        q['terrain_behavior']='bypass-plain-ground'if q['shot_type']in[42,43]else'impact-plain-ground'
    clear_scalars=['RgBillCadence','RgBillBurst','RgBillBurstDelay','RgPreviousButtons','RgWeaponButtons','SavedJoypadBits','SavedJoypad1Bits','A_B_Buttons','PreviousA_B_Buttons','InvPrevious','InvFresh','GuestBodyNow','GuestBodyPrev','GuestHurtTicks','GuestHurtKind','GuestInvulTicks','GuestFlickerPhase','GuestLegacyHurt','InjuryTimer','PlayerChangeSizeFlag','GuestPowerupActive','GuestPowerupAge','TimerControl','GamePauseStatus','GamePauseTimer','CheatInvincible','MmDeathFlag','CrouchingFlag','RgCrouch','InvRefill','InvRefillTick','InvRefillRemain','AvRefillItem','InvDropAmount']
    arrays=['RgShotType','RgShotX','RgShotPage','RgShotY','RgShotYHigh','RgShotDir','RgShotAge','RgShotFracX','RgShotFracY','RgShotVXLo','RgShotVXHi','RgShotVYLo','RgShotVYHi','RgShotHits','RgShotImpact','RgShotHitsNow','XgShotAim']
    drops=['InvDropKind','InvDropX','InvDropPage','InvDropY','InvDropVY','InvDropVYMid','InvDropVYHi','InvDropFraction','InvDropFractionHi','InvDropAge','InvDropAgeHi','AvDropItem']
    profiles=[];controls=[]
    for variant in [0,1]:
        name=('bill'if variant==0 else'lance')+'-hard';out=a.output/'profiles'/name/'native';out.mkdir(parents=True)
        cfg=dict(ROM_sha256=SHA,family='bill',character=3,slot=3,variant=variant,hard=True,mode_value=1,cases=recipe,ram={},hooks=hooks,
            irq_scroll_stores=irq,dma_protocol=protocol(b),clear_scalars=clear_scalars,shot_arrays=arrays,drop_arrays=drops,
            clear_ranges=[dict(name=n,bytes=address(b,end)-address(b,n))for n,end in [('AvRamStart','AvRamEnd'),('SpecialRamStart','SpecialRamEnd')]],
            effect_records=effects,single_masks=[value('InvSingleLo',48+i)for i in range(7)],auto_equip=[value('InvAutoEquip',48+i)for i in range(7)],
            powerup_sfx=address(b,'Sfx_PowerUpGrab'),fireball_sfx=address(b,'Sfx_Fireball'),machine_first_deltas=[7,7,6,7,6],
            art={n:dict(address=address(b,n),bank=(location(b,n)-16)//8192)for n in ['MTileTopLeft','MTileTopRight','MTileBotLeft','MTileBotRight','MTileAttribute']},
            smc_fields=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2])
        pos=location(b,'RemainingDraw::Draw');at=address(b,'RemainingDraw::Draw')
        cfg['advanced_after_pointer']=dict(pc=at+6,bank=(pos-16)//8192,bytes=list(b['raw'][pos:pos+12]))
        cfg['advanced_art_indices']=list(b['raw'][location(b,'BillAdvancedDrawArt::Arts'):location(b,'BillAdvancedDrawArt::Arts')+9])
        cfg['advanced_records']={}
        for art in cfg['advanced_art_indices']:
            ptr=value('AvArtRightLo',art)+256*value('AvArtRightHi',art);bn=value('AvArtBanks',art)&127
            cfg['advanced_records'][str(art)]=record(ptr,bn)
        cfg['hud_records']={}
        for item in [2,3,4,5]:
            art=value('RemainingDraw::PickupArts',8+item);ptr=value('AvArtRightLo',art)+256*value('AvArtRightHi',art);bn=value('AvArtBanks',art)&127
            cfg['hud_records'][str(item)]=record(ptr,bn)

        probe,_=compose(cfg);used=set(re.findall(r"'([A-Za-z_][A-Za-z_0-9]*)'",probe))|set(arrays+clear_scalars+drops+['Sprite_Data','AvRamStart','SpecialRamStart','NmiSkipped','NmiDisable'])
        cfg['ram']={n:address(b,n)for n in used if n in b['syms']};script,guards=compose(cfg)
        direct=set(re.findall(r"\b[wr]\('([A-Za-z_][A-Za-z_0-9]*)'",script));assert not direct-set(cfg['ram']),direct-set(cfg['ram'])
        assert "w('InvSelected'"not in script and "w('CrossoverBehaviorVersion'"not in script
        put(out/'config.json',cfg);(out/'run.lua').write_text(script,encoding='utf-8');(out/'inherited-NMI-stack-APU-guards.lua').write_text(guards,encoding='utf-8')
        rt=LuaRuntime(unpack_returned_tuples=True)
        rt.execute(MOCK+'\nL={};OUTPUT="mock/";emu.memType.nesPrgRom=6;emu.write=function()error("Unexpected startup mutation")end;emu.getScreenBuffer=function()local t={};for i=1,256*240 do t[i]=0xff000000 end;return t end')
        rt.execute(script);count=rt.eval('#callbacks')
        assert rt.eval('callbacks[#callbacks].lo==0 and callbacks[#callbacks].hi==65535') and rt.eval('#events[emu.eventType.endFrame]')==2
        rt.execute('emu.addMemoryCallback=function()error("Runtime registration forbidden")end;emu.removeMemoryCallback=function()error("Runtime removal forbidden")end')
        for frame in [1,2,3]:rt.execute(f"state['ppu.frameCount']={frame};runevents(emu.eventType.startFrame);runevents(emu.eventType.endFrame)")
        assert rt.eval('#callbacks')==count
        controls.append(dict(profile=name,startup_static_callbacks=count,dispatcher_last=True,no_startup_game_writes=True,runtime_API_registration_forbidden=True,original_guard_sha256=sha(out/'inherited-NMI-stack-APU-guards.lua')))
        profiles.append(dict(profile=name,variant=variant,mode_value=1,cases=7,output=str(out),script_sha256=sha(out/'run.lua'),maximum_launches=1))
    put(a.output/'plans.json',recipe)
    put(a.output/'static-controls.json',dict(passed=True,native_run=False,profiles=controls,return_controls=return_controls,DMA_controls=dma_controls,terrain_CPU_cases=terrain['cases']))
    runtime=D/'mmc3-flag-fix-v23/script-budget-probe-v2/emulator';settings=json.loads((runtime/'settings.json').read_bytes().decode('utf-8-sig'))
    for k,v in dict(RemoveSpriteLimit=False,AdaptiveSpriteLimit=False,RandomizeCpuPpuAlignment=False,RandomizeMapperPowerOnState=False,PpuExtraScanlinesBeforeNmi=0,PpuExtraScanlinesAfterNmi=0,DisableSprites=False,DisableBackground=False).items():assert settings['Nes'][k]==v
    assert settings['Emulation']['RunAheadFrames']==0 and settings['Emulation']['EmulationSpeed']==100
    env=dict(emulator=str(runtime/'Mesen.exe'),emulator_sha256=sha(runtime/'Mesen.exe'),core=str(runtime/'MesenCore.dll'),core_sha256=sha(runtime/'MesenCore.dll'),worker_settings=str(runtime/'settings.json'),worker_settings_sha256=sha(runtime/'settings.json'),user_settings='C:/Mesen2/settings.json',user_settings_sha256=sha('C:/Mesen2/settings.json'),Nes=settings['Nes'],Emulation=settings['Emulation'],actual_command_overrides=['--doNotSaveSettings','--nes.removeSpriteLimit=false','--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
    put(a.output/'environment.json',env)
    (a.output/'PLAN.txt').write_text('''PREPARE ONLY: two finite Hard profiles, Bill and Lance; seven legal carried
weapon cases each. No native launch/grant from this packet. Numeric Hard1
and alternate are selected with real cold menu input/readback. Seven cases:
Normal, Machine, Spread, Laser, Flare, Machine+Rapid1, Machine+Rapid2.
Only the first mushroom form/bit is an explicit B-use seed; all later
gun/passive grants use complete already-mature physical actors walked into
with actual Right input. Real InventoryCollect/Grant must replace exclusive
guns/auto-equip and preserve passives. No InvSelected/mode/outcome/RNG writes.
This is not a natural question block/rise/random-item acquisition claim.
Four finite components per case: right free emission, left actual Goomba
contact, right source-specific terrain query, left second-B batch (or held
Machine fractional cadence). Complete world/player/pool/drop state is set
only at GameLoop-entry boundaries. Inventory carries across all seven cases;
incremental physical grants are[],[4],[5],[2],[3],[4,1],[6], so no duplicate
Rapid1 or impossible all-guns-owned setup. No ammo depletion test: these
guns have free ammunition. Rapid upgrades alter projectile speed, not the
110ms machine cadence. All effects must reach bound compiled render records,
request native source SFX, contact/query, and expire naturally. Laser/Flare
must pass plain ground (source profiles69/70); other guns must impact it. Selected
HUD name and blank robot-only icon/ammo/meter cells are read from real PPU.
Historical source-only exact3b controls:170grants,3eligibility,28both-facing emissions,
28natural cleanup,6cadence;14new complete terrain controls. Original wrong
generic-C88 CPU fixture failure retained; actual graphics gateway establishes
requiredC19, without stubbing bounds/collisions. This is not a ROM bug.
Original immutable NMI/shadow/5SMC/SP/IRQ31/CHR/APU guards, startup-static
return dispatcher, full256DMA source/hardware/actual2004 writes and strict
pre-render274 enable deadline remain. Full actual PPU/index and compact Main
entry/finish cadence are retained. One12000-wall-frame bound/1800sec per
profile, one worker/no retry; stop firstFALSE. Later source/native grant must
name exact profile and readiness. No source/default/settings/Git edits.
''',encoding='utf-8')
    roots=[Path(__file__),ROOT/'tools/audit/final_bill_lance_combined_run_v1.py'];seen=set()
    while roots:
        f=roots.pop()
        if f in seen:continue
        seen.add(f);bindings.add(f)
        for node in ast.walk(ast.parse(f.read_text(encoding='utf-8-sig'))):
            mods=[node.module]if isinstance(node,ast.ImportFrom)else[q.name for q in node.names]if isinstance(node,ast.Import)else[]
            for n in mods:
                if n:
                    dep=ROOT/'tools/audit'/(n.split('.')[0]+'.py')
                    if dep.is_file():roots.append(dep)
    for n in ['final_bill_lance_hard_gallery_native_v1.lua','final_bill_lance_hard_gallery_native_v3.lua','final_bill_lance_combined_hud_v1.lua','final_item_matrix_progressive.lua','final_item_abilities_native.lua','final_item_abilities_static_return_v1.lua','final_item_abilities_dma731_v1.lua','final_item_abilities_pit731_ppu_v1.lua','final_item_abilities_failure.lua']:bindings.add(ROOT/'tools/audit'/n)
    bindings.update(PARENT/'source'/n for n in json.loads((PARENT/'source-manifest.json').read_text()))
    bindings.update([PARENT/'candidate.nes',PARENT/'candidate.dbg',PARENT/'candidate.lbl',PARENT/'candidate.map',PARENT/'proof.json',Path(sys.executable),Path(sys.modules[LuaRuntime.__module__].__file__),Path(env['emulator']),Path(env['core']),Path(env['worker_settings']),Path(env['user_settings'])])
    bindings.update(f for f in a.output.rglob('*')if f.is_file())
    put(a.output/'manifest.json',dict(bindings=[dict(path=str(f.resolve()),sha256=sha(f),bytes=f.stat().st_size)for f in sorted(bindings)]))
    commands={q['profile']:'python -B tools/audit/final_bill_lance_combined_run_v1.py --ready "'+a.output.as_posix()+'" --profile '+q['profile']+' --native-grant'for q in profiles}
    proof=dict(prepared=True,native_run=False,native_granted=False,ROM_sha256=SHA,profiles=profiles,cases_per_identity=7,mode_value=1,maximum_owned_workers=1,automatic_next_profile=False,retries=False,source_plan_sha256=sha(packet/'proof.json'),historical_source_plan_ROM_sha256=OLD_SHA,fresh_source_terrain_ROM_sha256=SHA,observer_version=3,unchanged_original_native_v3=True,extra_readonly_HUD_observer=True,manifest_sha256=sha(a.output/'manifest.json'),bindings=len(bindings),environment=env,commands=commands,ROM=str(PARENT/'candidate.nes'))
    put(a.output/'proof.json',proof)
    print(json.dumps(dict(passed=True,prepared_only=True,proof_sha256=sha(a.output/'proof.json'),bindings=len(bindings),commands=commands)))


if __name__=='__main__':main()
