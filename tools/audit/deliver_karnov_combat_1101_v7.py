"""Freeze the tested combat WIP and replace the user's sole nightly, no backup."""
from pathlib import Path
import hashlib,json,shutil,zipfile
from deliver_karnov_menu_health_1101_v3 import pack,validate
from build_storage_guard_v1 import preflight
from check_karnov_combat_integrated_1101_v7 import EXPECTED

R=Path(__file__).resolve().parents[2];J=R/'build/karnov-host-resource-base-1101-v1'
O=R/'build/karnov-combat-native-1101-v7'
D=R/'docs/qa/checkpoints/2026-11-01/karnov-combat-nightly-v7'
PREVIOUS='0162287ebf5b8fcb8a84dcf108a0d0930c4dc9d6e68928c4804bd774712e1a6c'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def receipt(p):
    q=json.loads(p.read_text());validate(q)
    assert q['passed']and q['ROM_sha256']==EXPECTED,p
    return q


def main():
    preflight(private_root=O,reserved_bytes=4000000,reserved_files=12,fresh=True)
    assert not D.exists()and not(O/'binding.json').exists()
    assert sha(J/'candidate.nes')==EXPECTED
    stage=receipt(J/'terrain-assembly.json');assert stage['combat']and stage['pickups']
    suite=receipt(J/'menu-health-suite.json')
    for n,h in suite['receipts'].items():assert sha(J/n)==h;receipt(J/n)
    main=receipt(O/'combat-Main-controls.json');assert main['no_executable_overlay']and main['Main']['reserve_above_SMC']>=12
    loader=receipt(O/'loader-final.json');assert loader['no_executable_overlay']and loader['cold_Main']['reserve_above_SMC']>=12
    grant=receipt(O/'carrier-successor.json');assert grant['carrier_granted']and grant['unchanged_other_owner_bytes']
    natives={};native_files={};native_scopes={}
    for name in ['combat-crouch','block-row','final-menu']:
        child=O/name;ready=json.loads((child/'ready.json').read_text());validate(ready)
        binding=json.loads((child/'capture/binding.json').read_text());q=receipt(child/'capture/result.json')
        assert binding['exit_code']==0 and binding['ready_sha256']==sha(child/'ready.json')and binding['ROM_sha256']==EXPECTED
        files=[p for p in child.rglob('*')if p.is_file()]
        assert len(files)<=64 and sum(p.suffix=='.png'for p in files)<=4 and sum(p.stat().st_size for p in files)<128000000
        native_files.update({name+'/'+p.relative_to(child).as_posix():p for p in files})
        natives[name]=q;native_scopes[name]=ready['scope']
    combat=natives['combat-crouch'];blocks=natives['block-row'];menu=natives['final-menu']
    assert combat['goomba_kills']>=1 and combat['native_enemy_damage']>=1 and combat['kill_sfx']
    assert combat['source_weapon']==1 and combat['source_health']==0 and combat['maximum_projectiles']==2
    assert all(combat[n]for n in ['rising_seen','mature_seen','source_owner_seen','erased_seen'])
    assert blocks['combat_block_effects']>=3 and blocks['brick_animation']and blocks['pickup_prepares']>=1
    assert len(menu['transitions'])==124 and not menu['anomalies']and menu['heading_errors']==menu['visible_mask_writes']==0
    prior=R/'docs/qa/checkpoints/2026-11-01/karnov-pickup-nightly-v4/source.zip'
    with zipfile.ZipFile(prior)as z:manifest=json.loads(z.read('files.json'))
    sources={n:Path(v['original'])for n,v in manifest.items()if not n.endswith('.json')}
    for p in J.iterdir():
        if p.suffix in ['.s','.inc','.cfg']or p.name in ['terrain-assembly.json','main-build.json','link.json','menu-health-suite.json',*suite['receipts']]:sources['host/'+p.name]=p
    for n in ['terrain-main-build.json','terrain-kernel-build.json','terrain-first-link.json','terrain-images-build.json','terrain-final-link.json','ingress-union-build.json']:
        sources['host/'+n]=J/n
    tools=['build_karnov_gameplay_host_1101_v1.py','build_karnov_combat_component_1101_v2.py',
           'prepare_karnov_combat_stack_1101_v3.py','prepare_karnov_combat_host_1101_v7.py','prepare_karnov_loader_funding_1101_v6.py',
           'check_karnov_combat_main_1101_v6.py','check_karnov_combat_integrated_1101_v7.py','check_karnov_loader_integrated_1101_v7.py',
           'check_karnov_carrier_successor_1101_v7.py','check_karnov_scene_1101_v1.py',
           'prepare_karnov_combat_native_1101_v7.py','prepare_karnov_combat_native_1101_v8.py',
           'prepare_karnov_block_shots_native_1101_v8.py','deliver_karnov_combat_1101_v7.py']
    for n in tools:sources['tools/audit/'+n]=R/'tools/audit'/n
    for n in ['karnov_combat_1101_v2.inc','karnov_combat_carrier_loader_1101_v3.inc','karnov_loader_funding_1101_v6.md']:
        sources['tools/reference/'+n]=R/'tools/reference'/n
    for n in ['combat-Main-controls.json','loader-final.json','carrier-successor.json']:
        sources['verification/'+n]=O/n
    components=[
        ('carrier-grant','karnov-carrier-final-1101-v6/source-and-proof.zip','9b122337170d23d8d34539b18d915af6499fc8c63aba8d8c06265fed46a547c2',True),
        ('loader-funding','karnov-loader-funding-1101-v6/source-proof.zip','ad5d8f3a1ba170b4f4edce36f12186c59231381611500f861e3b9c655980c5eb',True),
        ('combat-stack-component','karnov-combat-main-1101-v6/source-proof.zip','8d8b45a0abf3820d9992ab8f583d0e63ae1298661f4ce220ec0739396417e4cd',True),
        ('metal-storm-terrain-v5','metal-storm-terrain-host-1101-v5/source-proof.zip','43084a98280258338fa387ce106c3d249cdb87a47c3a31c1b7287d4eeefbb80e',False),
        ('metal-storm-objects-v6','metal-storm-objects-host-1101-v6/source-proof.zip','dcb7cc103fcd48949efb7b0dd1413edce1633ee1ebc1fbfd132afa5e927f6442',False),
        ('karnov-options-v7','karnov-options-component-1101-v7/source-proof.zip','cedec68dfc324fb65ab6a81bd76a2963fc22c2dd0915a10ef3d610a0aff7b7bd',False)]
    for _,name,h,_ in components:assert sha(R/'build'/name)==h
    nightly=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes');assert sha(nightly)==PREVIOUS
    D.mkdir();source=pack(D/'source.zip',sources);native=pack(D/'native-results.zip',native_files);parts={}
    for name,origin,h,integrated in components:
        dest=D/(name+'.zip');shutil.copyfile(R/'build'/origin,dest);assert sha(dest)==h
        parts[name]=dict(path=dest.relative_to(R).as_posix(),sha256=h,integrated=integrated)
    verification=dict(ROM_sha256=EXPECTED,actual_Main_ISR_cuts=sum(len(x['interrupts'])for x in main['Main']['cases']),
        minimum_combat_Main_ISR_SP=main['Main']['minimum_Main_ISR_SP'],cold_Main_ISR_cuts=loader['cold_Main']['unmasked_ISR_cases'],
        minimum_cold_Main_ISR_SP=loader['cold_Main']['minimum_ISR_SP'],both_carrier_readback_failures_rejected=True,
        both_complete_cache_headers_checked=True,source_CPU_suite=list(suite['receipts']),
        native_goomba_kills=combat['goomba_kills'],native_enemy_hit_sound=True,native_earned_double_shot=True,
        native_projectile_block_effects=blocks['combat_block_effects'],native_brick_debris=True,native_question_block_powerup=True,
        native_menu_transitions=124,sampled_roster_anomalies=0,heading_errors=0,visible_mask_writes=0,
        native_scopes=native_scopes)
    result=dict(passed=True,installed=True,backup_created=False,complete=False,user_requested_WIP=True,
        destination=str(nightly),output_sha256=EXPECTED,replaced_sha256=PREVIOUS,selectable_identities=86,
        total_menu_identities=90,selection='Rygar -> Select -> Karnov -> A/Start',
        checkpoint=D.relative_to(R).as_posix(),source=source,native=native,verification=verification,components=parts,
        changes=['Karnov original fireballs now hit native enemies and activate/break eligible blocks with native score, SFX and animations.',
                 'Projectile contact aligns with the visible lower8px of every original8x16 fireball/boomerang tile pair.',
                 'A17-byte private saved-frame transfer preserves the actual Main interrupt reserve through nested native effects.',
                 'The real forced-blank ten-row loader copies and verifies combat before publishing both cache cookies.'],
        pending=['Original equipment activation/Select/HUD/icons and original Karnov audio remain unintegrated.',
                 'Full1-1/shortcut/every-powerup controller qualification is unfinished; crouch-fire is needed for low enemies.',
                 'Metal Storm, Shinobi and Excitebike remain unselectable; Metal Storm actor/terrain/projectile and Karnov option source components are preserved.'],
        storage=preflight(fresh=True))
    # Keep this final mutation after every qualification and compact checkpoint.
    assert sha(J/'candidate.nes')==EXPECTED and sha(nightly)==PREVIOUS
    shutil.copyfile(J/'candidate.nes',nightly);assert sha(nightly)==EXPECTED
    (D/'handoff.json').write_text(json.dumps(result,indent=2)+'\n')
    (D/'README.md').write_text('''# Karnov projectile combat WIP

The exact0ffb1d79 candidate replaces the single Downloads nightly, without a
backup. Reopen the ROM and start fresh. Rygar -> Select -> Karnov -> A/Start.

Actual controller input crouch-fires the first Goomba, with native score and
hit sound, then collects a block-emerged mushroom and fires double shots.
A second route shoots the lone coin box, advances past that used block, then
breaks a brick with debris and shoots the mushroom question block. Its item
emerges normally. The124-transition menu sweep also passes on this exact ROM.

Collision now follows the visible bottom8px of the original8x16 projectile
tiles; standing flames naturally pass above low enemies. HoldDown+B to aim
lower. Native damage/HP, score positions, brick debris and block items retain
their existing owners. The real ten-row loader copies/readbacks all1280bytes
before paired cache validity. Actual Main and cold-loader IRQ/NMI tests retain
at least12bytes above native SMC storage. See handoff.json for precise scope.

Equipment activation, its UI/icons and original audio are not integrated.
Full levels/shortcut/all-powerup testing remains unfinished. This remains an
86-selectable WIP, not a completed Karnov implementation or new roster count.

The obsolete block-route diagnostic stopped behind the first used coin box;
the final route advances to the brick row. Earlier ground-fire diagnostics
identified the blank-half hitbox. Historical diagnostics do not qualify this
delivery. Frozen native templates have conservative legacy scope strings;
their hash-bound ready scopes and explicit counters define these tests.

Packets contain source/recipes/receipts and12 screenshots, no ROM, fulldebug,
object, video or per-frame dump. Separate component packets are explicitly
marked as integrated or pending in handoff.json.
''')
    (O/'binding.json').write_text(json.dumps(result,indent=2)+'\n')
    p=R/'docs/qa/continuation-current.json';state=json.loads(p.read_text())
    state['installed_nightly']=result;state['storage']=result['storage']
    state['current_priority']='Delivered86-selectable0ffb1d79 WIP with actual Karnov enemy/block combat, visible-tile hitbox alignment and preserved Main ISR reserve. Next allocate/integrate original equipment activation and HUD/audio, then full-stage qualification and remaining original-source roster.'
    k=state['Karnov_current'];k.update(installed=True,installed_nightly_sha256=EXPECTED,current_WIP_checkpoint=result['checkpoint'],
        current_combat=dict(ROM_sha256=EXPECTED,checkpoint=result['checkpoint'],services=stage['implemented_services'],
                            resident_bytes=stage['resident_bytes'],kernel_bytes=stage['kernel_bytes'],verification=verification),
        next=result['pending'],carrier_granted=parts['carrier-grant'],options_component=parts['karnov-options-v7'])
    state['latest_component_progress']=parts
    p.write_text(json.dumps(state,indent=2)+'\n')
    readme=R/'README.md';text=readme.read_text(encoding='utf-8')
    old='**Karnov** is selectable:';lo=text.index(old);hi=text.index('\n\n',lo)
    text=text[:lo]+'''**Karnov** is selectable: highlight Rygar, press Select, then A or Start. Original movement, fireballs, health, injury/death and stomp rebound are integrated. Shots now damage enemies, break eligible bricks with debris and trigger question blocks. Hold Down+B to hit low enemies. Real controller checks cover a Goomba defeat with score/SFX, shooting bricks and a mushroom block, then collecting an emerged mushroom and firing the earned double shot. Equipment activation/HUD, original audio and full-stage testing remain unfinished. See the [current WIP verification](docs/qa/checkpoints/2026-11-01/karnov-combat-nightly-v7/README.md).'''+text[hi:]
    text=text.replace('See the [current WIP verification](docs/qa/checkpoints/2026-11-01/karnov-pickup-nightly-v4/README.md).','See the [current WIP verification](docs/qa/checkpoints/2026-11-01/karnov-combat-nightly-v7/README.md).')
    readme.write_text(text,encoding='utf-8')
    print(json.dumps(dict(passed=True,installed=str(nightly),sha256=EXPECTED,source=source,native=native,storage=result['storage'])))


if __name__=='__main__':main()
