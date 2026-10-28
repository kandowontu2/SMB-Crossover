"""Prepare one exact-candidate BillHard seven-case gallery; never launch Mesen.

Reuses the actual qualified 3b seven-case controller/observer. The initial
mushroom form is explicitly staged; later gun/Rapid grants are physical.
"""
from pathlib import Path
import argparse, ast, csv, hashlib, inspect, json, re, sys

import final_bill_lance_hard_gallery_prepare_v1 as old
import final_bill_lance_hard_gallery_prepare_v2 as advanced
import final_bill_lance_hard_gallery_prepare_v3 as chronology
from final_bill_lance_hard_gallery_source_v2 import BillArena
from final_bill_lance_hard_gallery_source_v1 import plans, OWNER_NAMES, EXTRA_OWNERS
from final_item_abilities_current731_prepare_v1 import protocol
from final_inventory_compact_capture_v1 import adapt_script, collect_full_ppu
from final_bill_lance_hard_gallery_run_v2 import collect as original_collect
from check_tmnt_render_oa import address, location
from link_pit_rygar_sophia_audit_cpu import scoped_load

R = Path(__file__).resolve().parents[2]
B = R/'build'
ROM = B/'bill_inert_pool.nes'
EXPECTED = '44204c9b573a82dd4838df1821afeaad8ffab8b264ebb234f31a8e156434ff5a'
BASE = B/'zelda2_easy_glove.nes'
BASE_SHA = '32694243361bb1366f6fd64c054ea2451f86b2517fc020d9c2b5d66bbf07bfa0'
OUT = B/'current-44204-bill-hard-earned-v1'
PARENT = R/'docs/qa/checkpoints/2026-10-26/bill-lance-hard-native-final-v2/final-component-proof.json'
PARENT_SHA = 'd490c5deb0369228764eb8f86b579d413d7141538334725735cf690ea2a52973'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p, value):p.write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8', newline='\n')


def metadata(b):
    """Only genuine current compiled addresses, opcodes, tables and full records."""
    raw=b['raw'];value=lambda n,i=0:raw[location(b,n)+i]
    def record(ptr,bank):
        off=16+bank*8192+ptr%8192;n=raw[off]
        assert n%4==0 and n<=252
        return dict(address=ptr,bank=bank,bytes=list(raw[off:off+n+1]))
    effects={}
    for i in range(7):
        ptr=value('RgBILLWeaponsRightLo',i)+256*value('RgBILLWeaponsRightHi',i)
        effects[f'19:{ptr}']=record(ptr,19)
    for i in range(address(b,'AvArtRightHi')-address(b,'AvArtRightLo')):
        bank=value('AvArtBanks',i)&127
        for side in ['Right','Left']:
            ptr=value('AvArt'+side+'Lo',i)+256*value('AvArt'+side+'Hi',i)
            effects[f'{bank}:{ptr}']=record(ptr,bank)
    mechanics=(R/'tools/audit/final_bill_lance_hard_gallery_native_v3.lua').read_text()
    names=set(re.findall(r"hook\('([^']+)'",mechanics))|{'RosterWeapons::SpawnBill','RemainingWeapons::Spawn','NonMaskableInterrupt','IrqScrollSplit','RosterOamReady'}
    names-={'finish'};hooks={}
    for name in sorted(names):
        off=location(b,name)
        hooks[name]=dict(address=address(b,name),physical_bank=(off-16)//8192,bytes=list(raw[off:off+3]))
    # The only setup execution boundary is after the real NmiDisable=$FF store.
    off=location(b,'GameLoop');disable=address(b,'NmiDisable')
    assert raw[off:off+5]==bytes([0xa9,255,0x8d,disable&255,disable>>8])
    hooks['GameLoop'].update(address=address(b,'GameLoop')+5,bytes=list(raw[off+5:off+8]),source_delta=5)
    for key,name,opcode in [('finish','GameLoop',0x60),('NmiReturn','NonMaskableInterrupt',0x40)]:
        delta=int(b['syms'][name]['size'],0)-1;off=location(b,name)+delta
        assert raw[off]==opcode
        hooks[key]=dict(address=address(b,name)+delta,physical_bank=(off-16)//8192,bytes=[opcode])
    # Current E125 is a genuine resident-code clone. Admit it only after byte proof.
    for name in ['NonMaskableInterrupt','NmiReturn']:
        h=hooks[name];h['physical_banks']=[127]
        size=int(b['syms']['NonMaskableInterrupt']['size'],0) if name=='NonMaskableInterrupt' else 1
        pc=h['address'];normal=16+127*8192+pc%8192;clone=16+125*8192+pc%8192
        assert raw[normal:normal+size]==raw[clone:clone+size]
        h['physical_banks'].append(125)
    irqpos=location(b,'IrqScrollSplit')
    irq=[address(b,'IrqScrollSplit')+i for i in range(int(b['syms']['IrqScrollSplit']['size'],0)-2)if raw[irqpos+i:irqpos+i+3]==b'\x8d\x05\x20']
    assert irq==[address(b,'IrqScrollSplit')+0x17]
    recipe=plans()
    for q,grants in zip(recipe,[[],[4],[5],[2],[3],[4,1],[6]]):
        q['incremental_grants']=grants
        q['damage_type']=q['shot_type']+27 if q['shot_type']>=32 else [11,12,13][q['shot_type']-1]
        q['sfx']=address(b,'AV_SFX_BILLLASER'if q['shot_type']==42 else'AV_SFX_BILLFLARE')if q['shot_type']>=42 else 0
        i=48+q['expected_selected'];ptr=value('InvNameLo',i)+256*value('InvNameHi',i)
        segment=b['segs'][b['syms']['InvNameLo']['seg']]
        off=int(segment['ooffs'],0)+ptr-int(segment['start'],0)
        q['hud_name']=list(raw[off:off+7])
        q['terrain_behavior']='bypass-plain-ground'if q['shot_type']in[42,43]else'impact-plain-ground'
    scalars='RgBillCadence RgBillBurst RgBillBurstDelay RgPreviousButtons RgWeaponButtons SavedJoypadBits SavedJoypad1Bits A_B_Buttons PreviousA_B_Buttons InvPrevious InvFresh GuestBodyNow GuestBodyPrev GuestHurtTicks GuestHurtKind GuestInvulTicks GuestFlickerPhase GuestLegacyHurt InjuryTimer PlayerChangeSizeFlag GuestPowerupActive GuestPowerupAge TimerControl GamePauseStatus GamePauseTimer CheatInvincible MmDeathFlag CrouchingFlag RgCrouch InvRefill InvRefillTick InvRefillRemain AvRefillItem InvDropAmount'.split()
    arrays='RgShotType RgShotX RgShotPage RgShotY RgShotYHigh RgShotDir RgShotAge RgShotFracX RgShotFracY RgShotVXLo RgShotVXHi RgShotVYLo RgShotVYHi RgShotHits RgShotImpact RgShotHitsNow XgShotAim'.split()
    drops='InvDropKind InvDropX InvDropPage InvDropY InvDropVY InvDropVYMid InvDropVYHi InvDropFraction InvDropFractionHi InvDropAge InvDropAgeHi AvDropItem'.split()
    dma=protocol(b);dma['banks']=[127,125]
    assert all(raw[16+v*8192+dma['window_start']%8192:16+v*8192+dma['window_start']%8192+8]==bytes(dma['window_bytes'])for v in dma['banks'])
    cfg=dict(family='bill',character=3,slot=3,variant=0,hard=True,mode_value=1,cases=recipe,ram={},hooks=hooks,
        irq_scroll_stores=irq,dma_protocol=dma,clear_scalars=scalars,shot_arrays=arrays,drop_arrays=drops,
        clear_ranges=[dict(name=n,bytes=address(b,end)-address(b,n))for n,end in [('AvRamStart','AvRamEnd'),('SpecialRamStart','SpecialRamEnd')]],
        effect_records=effects,single_masks=[value('InvSingleLo',48+i)for i in range(7)],auto_equip=[value('InvAutoEquip',48+i)for i in range(7)],
        powerup_sfx=address(b,'Sfx_PowerUpGrab'),fireball_sfx=address(b,'Sfx_Fireball'),machine_first_deltas=[7,7,6,7,6],
        art={n:dict(address=address(b,n),bank=(location(b,n)-16)//8192)for n in ['MTileTopLeft','MTileTopRight','MTileBotLeft','MTileBotRight','MTileAttribute']},
        smc_fields=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2])
    advanced.B=b
    probe,_=chronology.compose(cfg)
    used=set(re.findall(r"'([A-Za-z_][A-Za-z_0-9]*)'",probe))|set(arrays+scalars+drops+['Sprite_Data','AvRamStart','SpecialRamStart','NmiSkipped','NmiDisable'])
    cfg['ram']={n:address(b,n)for n in sorted(used)if n in b['syms']and address(b,n)<0x8000}
    for name,at in cfg['ram'].items():
        # Filter the quote scan's ROM owner names, keeping only actual RAM symbols.
        if 0x8000<=at:continue
        assert 0<=at<0x8000
    return cfg


def adapt(cfg):
    script,guards=chronology.compose(cfg);changes=[]
    def change(before,after,label):
        nonlocal script
        assert script.count(before)==1,(label,script.count(before));script=script.replace(before,after,1)
        changes.append(dict(change=label,before=before,after=after))
    # The body of every old native mechanic and its predicates remains literal.
    old_guard="assert(writeBoundary,'Fixture writes only at native GameLoop entry');"
    change(old_guard,old_guard+"assert(r('NmiDisable')==255 and emu.getState()['cpu.pc']==C.hooks.GameLoop.address,'Setup only after genuine main NMI exclusion');",'Guarded setup at GameLoop+5')
    change("if bank(h.address)~=h.physical_bank then return end", "local actual=bank(h.address);local permitted=actual==h.physical_bank;for _,v in ipairs(h.physical_banks or{})do permitted=permitted or actual==v end;if not permitted then return end",'Genuine current E127/E125 NMI aliases')
    change("if bank(pc)~=dmaProtocol.bank then return end", "local permitted=false;for _,v in ipairs(dmaProtocol.banks)do permitted=permitted or bank(pc)==v end;if not permitted then return end",'Same real postDMA hook in resident clones')
    helper="""local function hardwareOamMatches(source,hardware)
 if #source~=256 or #hardware~=256 then return false end
 for i=1,256 do local want=source:byte(i);if(i-1)%4==2 then want=want&0xe3 end;if hardware:byte(i)~=want then return false end end
 return true
end
"""
    change('local dmaProtocol=assert(C.dma_protocol)',helper+'local dmaProtocol=assert(C.dma_protocol)','Qualified physical attribute E3 semantics')
    change("if q.source:byte(i)~=q.hardware:byte(i)then", "local expected=q.source:byte(i);if(i-1)%4==2 then expected=expected&0xe3 end;if expected~=q.hardware:byte(i)then",'Report only actual physical differences; raw source retained')
    for before,after,label in [
        ("assert(q.hardware==q.source,'All256 physical OAM bytes equal the actual DMA source')","assert(hardwareOamMatches(q.source,q.hardware),'All256 physical OAM bytes follow actual E3 hardware semantics')",'All256 physical completion'),
        ("assert(hardware==dmaCompleted.source,'startFrame hardware retains last completed DMA')","assert(hardwareOamMatches(dmaCompleted.source,hardware),'startFrame hardware retains last completed DMA with E3 attributes')",'All256 uncontested startFrame'),
        ("assert(bytes(0,emu.memType.nesSpriteRam)==dma,'Committed native publication reaches OAM DMA')","assert(hardwareOamMatches(dma,bytes(0,emu.memType.nesSpriteRam)),'Committed native publication reaches OAM DMA with E3 attributes')",'Original publication check')]:
        change(before,after,label)
    direct=set(re.findall(r"\b[wr]\('([A-Za-z_][A-Za-z_0-9]*)'",script))
    assert not direct-set(cfg['ram']),direct-set(cfg['ram'])
    assert all(cfg['ram'][n]<0x8000 for n in direct)
    assert "w('InvSelected'"not in script and "w('CrossoverBehaviorVersion'"not in script
    # Typed source configuration asserts before registration; no emulated writes.
    preflight="local C0=FINAL_ITEM_PROGRESSIVE;assert(C0.character==3 and C0.variant==0 and C0.mode_value==1 and #C0.cases==7,'Exact BillHard plan');for i,q in ipairs(C0.cases)do assert(type(q)=='table'and type(q.tasks)=='table'and #q.tasks==4 and type(q.incremental_grants)=='table','Typed seven-case configuration')end;for _,v in pairs(C0.ram)do assert(type(v)=='number'and v%1==0,'Compiled numeric RAM/address configuration')end\n"
    first,body=script.split('\n',1);script=first+'\n'+preflight+body
    script,inserted=adapt_script(script)
    # Close the one container at the existing original stop, after its PPU callback.
    assert script.count('f:close();emu.stop(0)')==1
    script=script.replace('f:close();emu.stop(0)','f:close();FINAL_COMPACT_CAPTURE.close();emu.stop(0)',1)
    return script,guards,changes


def source_controls(b):
    for name in EXTRA_OWNERS:
        if name in b['syms']and name not in OWNER_NAMES:OWNER_NAMES.append(name)
    value=lambda n,i:b['raw'][location(b,n)+i]
    tables={n:[value(n,48+i)for i in range(7)]for n in ['InvSelectable','InvAutoEquip','InvSingleLo','InvAvailability','InvCosts','InvAmmoIndex']}
    assert tables==dict(InvSelectable=[0]*7,InvAutoEquip=[0,0,1,1,1,1,0],InvSingleLo=[0,0,56,52,44,28,0],InvAvailability=[0,255,255,255,255,255,1],InvCosts=[0]*7,InvAmmoIndex=[255]*7)
    emissions=[];cadence=[]
    for plan in plans():
        for face in [1,2]:
            q=BillArena(b);q.put(PlayerFacingDir=face,Player_MovingDir=face)
            for item in plan['grant_sequence']:q.grant(item)
            assert q.get('InvOwnedLo',3)==plan['expected_owned']and q.get('InvSelected',3)==plan['expected_selected']
            q.buttons(0);q.buttons(64)
            active=[i for i in range(10)if q.get('RgShotType',i)]
            assert len(active)==plan['expected_initial_emissions']
            assert all(q.get('RgShotType',i)==plan['shot_type']and q.get('RgShotDir',i)==face for i in active)
            owners={v['owner']for v in q.calls[-1]['entries']}
            assert ('BillAdvancedBirth'if plan['shot_type']>=42 else'BillSourceProjection')in owners
            for tick in range(1,401):
                q.buttons(0)
                if not any(q.get('RgShotType',i)for i in range(10)):break
            else:raise AssertionError(('Natural expiry',plan['name'],face))
            emissions.append(dict(case=plan['name'],face=face,type=plan['shot_type'],emissions=len(active),natural_empty_update=tick))
    for rapid in [0,1,2]:
        q=BillArena(b)
        for item in [4]+([1]if rapid else[])+([6]if rapid==2 else[]):q.grant(item)
        births=[]
        for tick in range(80):
            _,trace=q.buttons(64)
            if any(address(b,'RgShotType')<=v['address']<address(b,'RgShotType')+10 and v['value']==2 for v in trace):births.append(tick)
        assert births[:6]==[0,7,14,20,27,33]
        cadence.append(dict(rapid=rapid,birth_updates=births))
    terrain=old.terrain_controls(b)
    return dict(passed=True,source_only=True,native_run=False,ROM_sha256=EXPECTED,tables=tables,
        current_complete_ProcFireball_Bubble_emission_cleanup_cases=emissions,current_cadence=cadence,
        current_complete_terrain_cases=terrain['rows'],scope='Fresh candidate compiled gateways and genuine C19 graphics entry. No actual native pickup, IRQ/PPU or new whole GameLoop campaign inferred. Existing candidate CPU/IRQ receipts separately bound.')


def collect(out):
    """Literal original typed collector, only container/E3 readers adapted."""
    cfg=json.loads((out.parent/'config.json').read_text());text=inspect.getsource(original_collect)
    begin=text.index('    try:\n        c=json.loads((out/\'ppu-capture-native-result.json\').read_text())')
    end=text.index("    except Exception as e:errors.append('Full PPU: '+str(e))",begin)
    text=text[:begin]+"    try:\n        parts['actual_full_PPU']=collect_full_ppu(out)\n"+text[end:]
    text=text.replace("q['source']==q['hardware']", "physical(q['source'])==q['hardware']")
    text=text.replace("q['hardware']==last['source']", "q['hardware']==physical(last['source'])")
    begin=text.index("    caps=[p for p in out.glob('*.argb')")
    end=text.index("    if(out/'first-failure.json').exists()",begin)
    text=text[:begin]+"    caps=parts.get('actual_full_PPU',{}).get('container',{}).get('named_capture_index',[])\n    if not caps:errors.append('Missing actual case captures')\n    parts['case_captures']=caps\n"+text[end:]
    ns=dict(json=json,csv=csv,copy=__import__('copy'),sha=sha,collect_full_ppu=collect_full_ppu,
        physical=lambda a:[v&0xe3 if i%4==2 else v for i,v in enumerate(a)])
    exec(compile(text,str(Path(__file__))+'::literal-collector','exec'),ns)
    result=ns['collect'](out,cfg);put(out/'component-review.json',result)
    return result


def binding_controls(b,cfg):
    base=scoped_load(BASE);prior_cfg=metadata(base)
    assert prior_cfg==cfg,'Every hooked owner/table/art/RAM binding is exact versus current326; no moved helper alias'
    differences=[i for i,(a,z)in enumerate(zip(base['raw'],b['raw']))if a!=z]
    assert len(differences)==31 and {(i-16)//8192 for i in differences}=={6}
    return dict(passed=True,candidate_sha256=EXPECTED,parent_sha256=BASE_SHA,changed_bytes=31,changed_banks=[6],
        actual_fresh_candidate_metadata_equals_current326_parent=True,
        all_hooks=[dict(name=n,**h)for n,h in cfg['hooks'].items()],
        genuine_helper_moves_receipt=str(B/'bill_inert_pool_verify_build.json'),
        six_genuine_private_moves_not_used_as_fake_aliases=True,
        original_mechanics_sha256=sha(R/'tools/audit/final_bill_lance_hard_gallery_native_v3.lua'),
        first_preparation_failure_retained=str(OUT/'preparation-negatives.json'),
        Lua_VM_available=False,Lua_VM_executed=False,
        limitation='No installed Lua VM found; startup and negative runtime controls were not rerun. Generated code reuses the qualified literal startup-static module; current compiled CPU source campaigns and all actual metadata are freshly checked. Native execution remains unrun/ROOT-owned.')


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--collect',type=Path);a=ap.parse_args()
    if a.collect:
        result=collect(a.collect);print(json.dumps(dict(passed=result['passed'],errors=result['errors'])));return
    assert sha(ROM)==EXPECTED and sha(BASE)==BASE_SHA and sha(PARENT)==PARENT_SHA
    if(OUT/'prepared-not-run.json').exists():
        assert not(native_launch:=OUT/'native/launch.json').exists(),native_launch
        # This local unsubmitted draft had one host collector path error only.
        draft=OUT/'prepared-not-run.json';old_ready=json.loads(draft.read_text())
        assert sha(draft)=='17fba0bd7adfceef2b9dc394ed2a35f9af1fb38f5f9574f31eb42db14ca924df'
        put(OUT/'unsubmitted-draft-receipt.json',dict(sha256=sha(draft),bytes=draft.stat().st_size,native_run=False,
            issue='Offline collector looked for config.json in native output rather than its prepared parent. No launch or collector run occurred. Corrected before submission; original draft hash retained.'))
    OUT.mkdir(exist_ok=True);native=OUT/'native';native.mkdir(exist_ok=True)
    b=scoped_load(ROM);cfg=metadata(b);bindings_proof=binding_controls(b,cfg);advanced.B=b;script,guards,changes=adapt(cfg)
    source=source_controls(b);put(OUT/'source-controls.json',source)
    put(OUT/'config.json',cfg);(OUT/'run.lua').write_text(script,encoding='utf-8',newline='\n')
    (OUT/'inherited-guards.lua').write_text(guards,encoding='utf-8',newline='\n');put(OUT/'observer-adaptations.json',changes)
    put(OUT/'metadata-controls.json',bindings_proof)
    command=['python','-B',str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(native),'--emulator','C:/Mesen2/Mesen.exe',str(OUT/'run.lua'),str(ROM),'--timeout','1800',
        '--option=--doNotSaveSettings','--option=--nes.removeSpriteLimit=false','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
    put(OUT/'command.json',dict(argv=command,maximum_launches=1,retries=0,ROOT_only=True))
    # The isolated driver provides OUTPUT and L before the fixture; bind its real configuration too.
    deps={ROM,ROM.with_suffix('.dbg'),ROM.with_suffix('.lbl'),BASE,PARENT,Path(__file__).resolve(),
        B/'bill_inert_pool_handoff.json',B/'bill_inert_pool_cpu.json',B/'bill_inert_pool_final.json',B/'bill_inert_pool_ordinary.json',B/'bill_inert_pool_verify_build.json',
        R/'docs/qa/bill-inert-pool-independent-review-2026-10-28.json',R/'tools/run_mesen.py',R/'tools/audit/run_mesen_isolated.py',R/'tools/audit/capture_budget.py',
        R/'tools/audit/final_item_matrix_progressive.lua',R/'tools/audit/final_item_abilities_static_return_v1.lua',R/'tools/audit/final_item_abilities_dma731_v1.lua',
        R/'tools/audit/final_item_abilities_pit731_ppu_v1.lua',R/'tools/audit/final_item_abilities_failure.lua',R/'tools/audit/final_inventory_compact_capture_v1.lua',
        R/'tools/audit/current_roster_compact_11_v1.lua',R/'tests/current-inventory-powerups.lua',
        Path('C:/Mesen2/Mesen.exe'),Path('C:/Mesen2/MesenCore.dll'),Path('C:/Mesen2/settings.json')}
    deps.update(R/'tools/audit'/('final_bill_lance_hard_gallery_native_v'+str(i)+'.lua')for i in [1,2,3])
    deps.update(Path(m.__file__).resolve()for m in list(sys.modules.values())if getattr(m,'__file__',None)and Path(m.__file__).resolve().is_relative_to(R/'tools')and Path(m.__file__).suffix=='.py')
    deps.update(p for p in OUT.iterdir()if p.is_file()and p.name!='prepared-not-run.json')
    ready=dict(prepared=True,native_run=False,native_granted=False,ROM=str(ROM),ROM_sha256=EXPECTED,profile='bill-hard',cases=7,stages=28,command=command,
        maximum_launches=1,maximum_owned_workers=1,retries=0,ROOT_only_native=True,wall_frame_cap=12000,host_seconds=1800,
        parent=dict(receipt=str(PARENT),sha256=PARENT_SHA,actual_native_ROM='3b112e1d79ba7348f2f7a4c426f4675845a5781017ab74690feb235121a66287',current_native_pass_transferred=False),
        candidate_route_FALSE_retained='Candidate whole-route v2 ZeroDeath FALSE1811; source review does not exonerate it. Unmodified326 adaptive baseline passed; causal analysis remains separate.',
        acquisition='Initial PlayerStatus1 and mushroom InvOwnedLo[3]=1 are explicit inherited B-use seeds after30 settle updates. All later exclusive guns/Rapid are actual staged-mature actor pickups/autoequip. No natural reveal/rise, mushroom acquisition or Select cycling claim.',
        exact_scope='Normal/Machine/Spread/Laser42/Flare43/Rapid1/Rapid2; right free/left real enemy/right terrain/left fresh-B or Machine cadence; source art/SFX, natural cleanup, carried mutually-exclusive ownership and passive speed. All guns cost0/InvSelectable0; no energy or Select requirement invented.',
        source_controls=str(OUT/'source-controls.json'),source_complete_gateway_cases=14,source_terrain_cases=14,source_cadence_cases=3,
        hardware='Original NMI bank/publication windows/A/SP/5SMC, IRQ31, CHR write-latch, stack/APU preserved; genuine current E127/E125 clones proven; E008 actual256 unmasked source/data/destination plus physical attribute E3 normalization; Addr0/render-off throughout and strict pre-render274 deadline.',
        observer_changes=str(OUT/'observer-adaptations.json'),Lua_VM_preflight_executed=False,
        startup='Typed numeric plan/RAM assertions generated before callback registration; unchanged qualified static-return module; all host callbacks startup-only. No new runtime callback registration.',
        storage=dict(maximum_bytes=2_000_000_000,maximum_files=64,one_container_cap_bytes=1_500_000_000,container_records=25000,PNG_during_native=0,maximum_offline_selected_PNGs=8,no_source_runtime_copies=True),
        collector=['python','-B',str(Path(__file__).resolve()),'--collect',str(native)],
        owned_files=[str(Path(__file__).resolve())],bindings=[dict(path=str(p.resolve()),sha256=sha(p),bytes=p.stat().st_size)for p in sorted(deps)])
    put(OUT/'prepared-not-run.json',ready)
    print(json.dumps(dict(prepared=True,native_run=False,ready=str(OUT/'prepared-not-run.json'),sha256=sha(OUT/'prepared-not-run.json'),bindings=len(deps),command=str(OUT/'command.json'))))


if __name__=='__main__':main()
