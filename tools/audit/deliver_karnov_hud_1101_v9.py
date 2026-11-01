"""Freeze the tested equipment HUD and replace the sole Downloads nightly."""
from pathlib import Path
import hashlib,json,re,shutil,zipfile
from build_storage_guard_v1 import preflight
from deliver_karnov_menu_health_1101_v3 import pack,validate

R=Path(__file__).resolve().parents[2]
J=R/'build/karnov-host-resource-base-1101-v1'
O=R/'build/karnov-hud-native-1101-v9'
D=R/'docs/qa/checkpoints/2026-11-01/karnov-hud-nightly-v9'
PIN='99bf88c8d971f1305f965a21833703c7a11aafa6a24febd9f3bfb7c87ba4bbda'
OLD='1c073196b51b6aaaaac90d1bea925b68807fcaa3055665cf6dd0cc8f7858fe33'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def receipt(p):
    q=json.loads(p.read_text());validate(q)
    assert q['passed']and q['ROM_sha256']==PIN,p
    return q


def sources(path,updates):
    previous=R/'docs/qa/checkpoints/2026-11-01/karnov-options-nightly-v8/source.zip'
    assert sha(previous)=='dedeb87c123ce5b575bcf16f0eb84bd52bffd6a1808174cfd4f25fe5856514ea'
    with zipfile.ZipFile(previous)as z:
        manifest=json.loads(z.read('files.json'));data={n:z.read(n)for n in manifest}
    for n,p in updates.items():
        data[n]=p.read_bytes();manifest[n]=dict(original=str(p.resolve()),bytes=len(data[n]),sha256=sha(p))
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for n,v in sorted(data.items()):
            assert len(v)==manifest[n]['bytes']and hashlib.sha256(v).hexdigest()==manifest[n]['sha256']
            z.writestr(n,v)
        z.writestr('files.json',json.dumps(manifest,indent=2)+'\n')
    assert path.stat().st_size<2000000
    return dict(path=path.relative_to(R).as_posix(),sha256=sha(path),bytes=path.stat().st_size,members=len(data)+1,
                inherited_source_packet=previous.relative_to(R).as_posix(),inherited_sha256=sha(previous))


def main():
    preflight(private_root=O,reserved_bytes=5000000,reserved_files=12,fresh=True)
    assert not D.exists()and not(O/'binding.json').exists()and sha(J/'candidate.nes')==PIN
    stage=receipt(J/'terrain-assembly.json');assert stage['equipment_hud']and stage['options']and stage['combat']
    suite=receipt(J/'menu-health-suite.json')
    for n,h in suite['receipts'].items():assert sha(J/n)==h;receipt(J/n)
    hud=receipt(O/'hud-controls.json');cpu=receipt(O/'regression-controls.json')
    assert hud['no_executable_overlay']and hud['owners']['unchanged_other_owners']
    assert cpu['equipment_Main']['minimum_Main_ISR_SP']>=135 and cpu['combat_Main']['minimum_Main_ISR_SP']>=135
    assert cpu['loader']['cold_Main']['reserve_above_SMC']>=12 and hud['HUD_Main']['minimum_ISR_SP']>=135
    names=['boots-hud','boomerang-hud','wings-hud','combat-crouch','block-row','final-menu']
    native={};native_files={};scopes={}
    for n in names:
        child=O/n;ready=json.loads((child/'ready.json').read_text());validate(ready)
        binding=json.loads((child/'capture/binding.json').read_text());q=receipt(child/'capture/result.json')
        assert binding['exit_code']==0 and binding['ready_sha256']==sha(child/'ready.json')and binding['ROM_sha256']==PIN
        assert ready['emulated_writes']==(n in names[:3])
        files=[p for p in child.rglob('*')if p.is_file()]
        assert len(files)<=64 and sum(p.suffix=='.png'for p in files)<=4 and sum(p.stat().st_size for p in files)<128000000
        assert not any(p.suffix in ['.nes','.dbg','.o','.mp4','.avi']for p in files)
        native_files.update({n+'/'+p.relative_to(child).as_posix():p for p in files})
        native[n]=q;scopes[n]=ready['scope']
    for n in names[:3]:
        q=native[n];assert q['option_stock']==1 and min(q['HUD_checks'],q['HUD_font_maps'],q['world_font_maps'])>5
    assert native['boots-hud']['equipment_base']-native['boots-hud']['equipment_peak']==88
    assert native['boomerang-hud']['boomerang_returned']>native['boomerang-hud']['boomerang_fired']
    assert native['wings-hud']['flight_up']<native['wings-hud']['equipment_base']and native['wings-hud']['flight_down']>native['wings-hud']['flight_up']
    combat=native['combat-crouch'];blocks=native['block-row'];menu=native['final-menu']
    assert combat['goomba_kills']>=1 and combat['kill_sfx']and combat['maximum_projectiles']==2 and combat['source_weapon']==1
    assert blocks['combat_block_effects']>=3 and blocks['brick_animation']and blocks['pickup_prepares']>=1
    assert len(menu['transitions'])==124 and not menu['anomalies']and menu['heading_errors']==menu['visible_mask_writes']==0
    updates={}
    for p in J.iterdir():
        if p.suffix in ['.s','.inc','.cfg']or p.name in ['kr-hud-font.chr','terrain-assembly.json','main-build.json','link.json','menu-health-suite.json',*suite['receipts']]:updates['host/'+p.name]=p
    for n in ['terrain-main-build.json','terrain-kernel-build.json','terrain-first-link.json','terrain-images-build.json','terrain-final-link.json','ingress-union-build.json']:updates['host/'+n]=J/n
    tools=['build_karnov_gameplay_host_1101_v1.py','check_karnov_options_host_component_1101_v8.py',
           'prepare_karnov_hud_funding_1101_v9.py','check_karnov_hud_funding_1101_v9.py',
           'prepare_karnov_hud_host_1101_v9.py','check_karnov_hud_integrated_1101_v9.py','prepare_karnov_hud_native_1101_v9.py',
           'prepare_karnov_equipment_hud_1101_v9.py','check_karnov_equipment_hud_1101_v9.py','freeze_karnov_equipment_hud_1101_v9.py',
           'audit_karnov_hud_resource_1101_v9.py','finish_karnov_hud_resource_1101_v9.py','deliver_karnov_hud_1101_v9.py']
    for n in tools:updates['tools/audit/'+n]=R/'tools/audit'/n
    for n in ['karnov_equipment_hud_1101_v9.inc','karnov_equipment_hud_1101_v9.md']:updates['tools/reference/'+n]=R/'tools/reference'/n
    for n in ['hud-controls.json','regression-controls.json','hud-fixture-negative.json','regression-payload-negative.json']:updates['verification/'+n]=O/n
    # Failed controller route is diagnostic only: it never achieved a second
    # enemy contact. It is not included in the six positive native results.
    diagnostic=O/'encounter/capture/result.json'
    if diagnostic.exists():updates['diagnostics/unfinished-injury-route.json']=diagnostic
    component_inputs=[
      ('HUD-source','karnov-equipment-hud-1101-v9/source-proof.zip','10aa09065b7a999f75f3d5a8ff726d0c7031678bfd25519e68faed2a8baee34b',True),
      ('HUD-resource-grant','karnov-hud-resource-1101-v9/source-and-proof.zip','299abbd0477434f45334a25acfdd38d4ddc646c5966464aeac02806c8cec9b46',True),
      ('kirby-repair-component','kirby-inhale-shell-fix-1101-v1/source-proof.zip','9da690c7693403fb2088cc8e32ac27ba0890084c61a03d00d5d39f78a1d5709a',False),
      ('mario-tank-source','mario-tank-source-1101-v1/source-and-proof.zip','4ba9b8bcb8706e906749bde18619fd1dcdfff39cba259a0ed45bfc49bdeafac5',False),
      ('metal-storm-resources','metal-storm-resource-host-1101-v8/source-proof.zip','abe08a438e929bbeac93fcb319ed01cd9fdf64649a4a4d4f1828a8dd91d48710',False)]
    for _,n,h,_ in component_inputs:assert sha(R/'build'/n)==h
    nightly=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes');assert sha(nightly)==OLD
    D.mkdir();source=sources(D/'source.zip',updates);captured=pack(D/'native-results.zip',native_files);parts={}
    for n,origin,h,integrated in component_inputs:
        target=D/(n+'.zip');shutil.copyfile(R/'build'/origin,target);assert sha(target)==h
        parts[n]=dict(path=target.relative_to(R).as_posix(),sha256=h,integrated=integrated)
    verification=dict(ROM_sha256=PIN,HUD_Main_minimum_ISR_SP=hud['HUD_Main']['minimum_ISR_SP'],
        equipment_Main_minimum_ISR_SP=cpu['equipment_Main']['minimum_Main_ISR_SP'],combat_Main_minimum_ISR_SP=cpu['combat_Main']['minimum_Main_ISR_SP'],
        cold_Main_minimum_ISR_SP=cpu['loader']['cold_Main']['minimum_ISR_SP'],cold_Main_ISR_cuts=cpu['loader']['cold_Main']['unmasked_ISR_cases'],
        actual_loader_rows=12,all32_cookie_bytes_independently_rejected=True,source_CPU_suite=list(suite['receipts']),
        native_equipment_stock_fixture=True,native_controller_combat_and_pickups=True,native_menu_transitions=124,
        heading_errors=0,visible_mask_writes=0,native_scopes=scopes,
        HUD_font_physical=1023,HUD_cache='C87A..C87F',same_life_area_HUD_cancel=True,ROM_retirement_HUD_cancel=True)
    result=dict(passed=True,installed=True,backup_created=False,complete=False,user_requested_WIP=True,
        destination=str(nightly),output_sha256=PIN,replaced_sha256=OLD,selectable_identities=86,total_menu_identities=90,
        selection='Rygar -> Select -> Karnov -> A/Start',checkpoint=D.relative_to(R).as_posix(),source=source,native=captured,
        verification=verification,components=parts,
        controls='Select cycles earned Boots/Boomerang/Wings/NONE. Down+fresh B activates the highlighted option. A jumps; B fires. Up/Down move during flight.',
        changes=['Equipment HUD shows the original icon, full selected name and BCD stock with an alternating control hint.',
                 'Native HUD font publication preserves world font mapping and yields to busy native VRAM updates.',
                 'Same-life construction and ROM retirement cancel the derived HUD lease; other owners remain unchanged.'],
        pending=['Original Karnov audio and six other equipment types remain unfinished.',
                 'Equipment native tests use declared stock fixtures; controller-earned gear, full1-1/shortcut/every-powerup remain unfinished.',
                 'Kirby source repair is frozen but is not integrated in this nightly. Metal Storm, Shinobi and Excitebike remain unselectable.'],
        storage=preflight(fresh=True))
    text='''# Karnov equipment HUD WIP

The exact `99bf88c8` candidate replaces the single Downloads nightly without a
backup. Reopen the ROM and start fresh. Rygar → Select → Karnov → A/Start.

Select cycles earned Boots, Boomerang, Wings and NONE. Down+fresh B activates
the selected equipment. A jumps; B fires. Up/Down control flight. The HUD now
shows the full selected name, original icon, remaining stock and control hint.
Icon shapes are original; the two color planes are swapped for native HUD
contrast. No replacement wing artwork or equipment sprites were invented.

Three Mesen checks explicitly seed six original inventory bytes, then use real
controller input to verify activation, stock01, displayed name/icon, boots88px
jump, boomerang return and flight. They also check actual HUD/world CHR maps.
Separate controller-only runs defeat a Goomba with score/hit SFX, collect an
emerged mushroom, fire double shots, break bricks with debris and trigger a
question block. All90 menu identities/124 transitions pass sampled heading,
gray-portrait and rendering-mask checks. Each native run uses at most4PNGs.

Actual owning Main/IRQ/NMI checks cover equipment, combat, the HUD and cold
loader, with at least12bytes above stack-based code. The twelve-row loader
verifies both cache headers. Legal area transitions and retirement cancel the
HUD lease. Existing other-owner bytes remain exact outside documented imports.
Six source CPU suites cover health, rebound, life restart, terrain and scenes.

One additional controller route failed to reach a second enemy contact and is
preserved as a diagnostic, not a passing fatal-injury playthrough. Original
audio, six other equipment types, earned gear progression, full stages,
shortcuts, all powerups and constant60Hz remain unqualified or unfinished.
The source packets for Kirby's repair, Mario the Tank and Metal Storm are
preserved but are not admitted by this delivery. This remains86 selectable
work-in-progress identities, not a completed roster.
'''
    (D/'README.md').write_text(text,encoding='utf-8',newline='\n')
    readme=(R/'README.md').read_text(encoding='utf-8')
    paragraph='**Karnov** is selectable: highlight Rygar, press Select, then A or Start. Original movement, fireballs, health, injury/death and stomp rebound are integrated. Shots damage enemies, break eligible bricks with debris and trigger question blocks. Select cycles earned Boots, Boomerang, Wings and NONE; Down+B activates the chosen equipment. The equipment HUD shows its original icon, full name and remaining stock. Boots give the original higher jump, boomerangs return to the base shots, and wings use Up/Down flight controls. Other equipment, original audio and full-stage testing remain unfinished. See the [current WIP verification](docs/qa/checkpoints/2026-11-01/karnov-hud-nightly-v9/README.md).'
    readme,n=re.subn(r'(?m)^\*\*Karnov\*\*.*$',lambda _:paragraph,readme);assert n==1
    latest='The latest delivered nightly is `99bf88c8` (November 1), with **86 selectable identities**. Karnov now has an equipment HUD with original icons, full names, stock and controls, alongside original Boots/Boomerang/Wings behavior and preceding combat/pickup/health fixes. Three native equipment checks use declared inventory fixtures; separate controller-only runs verify enemy defeat, block effects and earned mushroom/double shots. The 124-transition menu sweep and owning Main/ISR/source lifecycle checks pass on this exact ROM. Other equipment/audio, full stages, shortcuts, every powerup and steady 60 Hz remain unfinished. See the [verification](docs/qa/checkpoints/2026-11-01/karnov-hud-nightly-v9/README.md) and [delivery receipt](docs/qa/checkpoints/2026-11-01/karnov-hud-nightly-v9/handoff.json).'
    readme,n=re.subn(r'(?m)^The latest delivered nightly is .*$',lambda _:latest,readme);assert n==1
    readme=readme.replace('docs/qa/checkpoints/2026-11-01/karnov-options-nightly-v8/README.md','docs/qa/checkpoints/2026-11-01/karnov-hud-nightly-v9/README.md')
    assert sha(J/'candidate.nes')==PIN and sha(nightly)==OLD
    shutil.copyfile(J/'candidate.nes',nightly);assert sha(nightly)==PIN
    (D/'handoff.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    (O/'binding.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    (R/'README.md').write_text(readme,encoding='utf-8',newline='\n')
    path=R/'docs/qa/continuation-current.json';q=json.loads(path.read_text())
    q.update(goal_status='ACTIVE_INCOMPLETE',previous_goal_turn_classification='progress',installed_nightly=result,
        current_priority='Delivered99bf88c8 equipmentHUD. Integrate Kirby inhale and shell repair next; continue Mario the Tank and Metal Storm, then full-stage/shortcut/every-upgrade and remaining original-source roster.',
        completion='Not complete:86 selectable/90 menu identities. Remaining characters, campaigns and all-character full1-1/shortcut/every-powerup verification remain required.',
        Mesen='Six positive root SMB runs terminal. Other-project sessions untouched.',storage=result['storage'],
        agents='Three authorized workers: isolated Kirby owning-link/Main proposal, Mario the Tank host adapters, Metal Storm world-safe palette/resource proposal. Root owns SMB Mesen queue.',
        active_source_components=dict(kirby_repair=parts['kirby-repair-component'],mario_tank=parts['mario-tank-source'],metal_storm_resources=parts['metal-storm-resources'],equipment_HUD=parts['HUD-source']))
    path.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,installed=True,backup_created=False,ROM_sha256=PIN,source_bytes=source['bytes'],native_bytes=captured['bytes'],build_bytes=result['storage']['build_bytes'],build_files=result['storage']['build_files'])))


if __name__=='__main__':main()
