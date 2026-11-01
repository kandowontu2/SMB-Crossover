"""Freeze qualified original equipment and replace the sole Downloads nightly."""
from pathlib import Path
import hashlib,json,re,shutil,zipfile
from deliver_karnov_menu_health_1101_v3 import pack,validate
from build_storage_guard_v1 import preflight

R=Path(__file__).resolve().parents[2];J=R/'build/karnov-host-resource-base-1101-v1'
O=R/'build/karnov-options-native-1101-v8'
D=R/'docs/qa/checkpoints/2026-11-01/karnov-options-nightly-v8'
EXPECTED='1c073196b51b6aaaaac90d1bea925b68807fcaa3055665cf6dd0cc8f7858fe33'
PREVIOUS='0ffb1d79c4fbc52bb337a4726f8e61f984f30e4795fd2555b204322140c0a717'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def receipt(p):
    q=json.loads(p.read_text());validate(q)
    assert q['passed']and q['ROM_sha256']==EXPECTED,p
    return q


def source_pack(path,updates):
    previous=R/'docs/qa/checkpoints/2026-11-01/karnov-combat-nightly-v7/source.zip'
    assert sha(previous)=='d4160bbdda88160a74f735975a9899a69c4d2c3bd82d4c6467f39ab545379ca5'
    with zipfile.ZipFile(previous)as z:
        manifest=json.loads(z.read('files.json'))
        data={n:z.read(n)for n in manifest}
    for name,p in updates.items():
        data[name]=p.read_bytes();manifest[name]=dict(original=str(p.resolve()),sha256=sha(p),bytes=p.stat().st_size)
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for n,v in sorted(data.items()):
            assert hashlib.sha256(v).hexdigest()==manifest[n]['sha256']and len(v)==manifest[n]['bytes']
            z.writestr(n,v)
        z.writestr('files.json',json.dumps(manifest,indent=2)+'\n')
    assert path.stat().st_size<2000000
    return dict(path=path.relative_to(R).as_posix(),sha256=sha(path),bytes=path.stat().st_size,members=len(data)+1,
                inherited_source_packet=previous.relative_to(R).as_posix(),inherited_sha256=sha(previous))


def main():
    preflight(private_root=O,reserved_bytes=4000000,reserved_files=12,fresh=True)
    assert not D.exists()and not(O/'binding.json').exists()
    assert sha(J/'candidate.nes')==EXPECTED
    stage=receipt(J/'terrain-assembly.json');assert stage['options']and stage['combat']and stage['pickups']
    suite=receipt(J/'menu-health-suite.json')
    for n,h in suite['receipts'].items():assert sha(J/n)==h;receipt(J/n)
    cpu=receipt(O/'options-integrated.json')
    assert cpu['no_executable_overlay']and cpu['owners']['unchanged_other_owners']
    assert cpu['equipment_Main']['minimum_Main_ISR_SP']>=135 and cpu['combat_Main']['minimum_Main_ISR_SP']>=135
    assert cpu['loader']['cold_Main']['reserve_above_SMC']>=12
    natives={};native_files={};native_scopes={}
    names=['boots','boomerang','wings','combat-crouch','block-row','final-menu']
    for name in names:
        child=O/name;ready=json.loads((child/'ready.json').read_text());validate(ready)
        binding=json.loads((child/'capture/binding.json').read_text());q=receipt(child/'capture/result.json')
        assert binding['exit_code']==0 and binding['ready_sha256']==sha(child/'ready.json')and binding['ROM_sha256']==EXPECTED
        assert ready['emulated_writes']==(name in ['boots','boomerang','wings'])
        files=[p for p in child.rglob('*')if p.is_file()]
        assert len(files)<=64 and sum(p.suffix=='.png'for p in files)<=4 and sum(p.stat().st_size for p in files)<128000000
        native_files.update({name+'/'+p.relative_to(child).as_posix():p for p in files})
        natives[name]=q;native_scopes[name]=ready['scope']
    assert natives['boots']['equipment_base']-natives['boots']['equipment_peak']==88
    assert natives['boomerang']['boomerang_returned']>natives['boomerang']['boomerang_fired']
    assert natives['wings']['flight_up']<natives['wings']['equipment_base']and natives['wings']['flight_down']>natives['wings']['flight_up']
    assert all(natives[n]['option_stock']==0 for n in names[:3])
    combat=natives['combat-crouch'];blocks=natives['block-row'];menu=natives['final-menu']
    assert combat['goomba_kills']>=1 and combat['kill_sfx']and combat['maximum_projectiles']==2 and combat['source_weapon']==1
    assert blocks['combat_block_effects']>=3 and blocks['brick_animation']and blocks['pickup_prepares']>=1
    assert len(menu['transitions'])==124 and not menu['anomalies']and menu['heading_errors']==menu['visible_mask_writes']==0
    updates={}
    for p in J.iterdir():
        if p.suffix in ['.s','.inc','.cfg']or p.name in ['terrain-assembly.json','main-build.json','link.json','menu-health-suite.json',*suite['receipts']]:updates['host/'+p.name]=p
    for n in ['terrain-main-build.json','terrain-kernel-build.json','terrain-first-link.json','terrain-images-build.json','terrain-final-link.json','ingress-union-build.json']:
        updates['host/'+n]=J/n
    tools=['build_karnov_gameplay_host_1101_v1.py','prepare_karnov_options_1101_v7.py','prepare_karnov_options_host_1101_v8.py',
           'build_karnov_options_host_component_1101_v8.py','check_karnov_options_host_component_1101_v8.py',
           'check_karnov_options_integrated_1101_v8.py','check_karnov_loader_funding_1101_v6.py',
           'check_karnov_scene_1101_v1.py','check_karnov_menu_health_suite_1101_v3.py',
           'prepare_karnov_options_native_1101_v8.py','deliver_karnov_options_1101_v8.py']
    for n in tools:updates['tools/audit/'+n]=R/'tools/audit'/n
    updates['tools/reference/karnov_options_1101_v7.inc']=R/'tools/reference/karnov_options_1101_v7.inc'
    updates['verification/options-integrated.json']=O/'options-integrated.json'
    components=[('equipment-carrier-grant','karnov-carrier-extension-1101-v7/source-and-proof.zip','b61c283362a2e593de24c38c91088d1b497100fd921d03d1915fabc879556846',True),
                ('bomb-ladder-component','karnov-equipment-component-1101-v8/source-proof.zip','4e4bad3d63ab5487c88c160ea5c0378a1378fa8709123f6c720a7e5433d01b29',False)]
    for _,name,h,_ in components:assert sha(R/'build'/name)==h
    nightly=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes');assert sha(nightly)==PREVIOUS
    D.mkdir();source=source_pack(D/'source.zip',updates);native=pack(D/'native-results.zip',native_files);parts={}
    for name,origin,h,integrated in components:
        dest=D/(name+'.zip');shutil.copyfile(R/'build'/origin,dest);assert sha(dest)==h
        parts[name]=dict(path=dest.relative_to(R).as_posix(),sha256=h,integrated=integrated)
    verification=dict(ROM_sha256=EXPECTED,equipment_Main_minimum_ISR_SP=cpu['equipment_Main']['minimum_Main_ISR_SP'],
        combat_Main_minimum_ISR_SP=cpu['combat_Main']['minimum_Main_ISR_SP'],cold_Main_minimum_ISR_SP=cpu['loader']['cold_Main']['minimum_ISR_SP'],
        cold_Main_ISR_cuts=cpu['loader']['cold_Main']['unmasked_ISR_cases'],equipment_Main_cases=3,
        combat_Main_ISR_cuts=sum(len(r['interrupts'])for r in cpu['combat_Main']['cases']),
        four_new_carrier_fault_rows_rejected=[8,9,10,11],all32_cookie_bytes_independently_rejected=True,
        actual_loader_rows=12,source_CPU_suite=list(suite['receipts']),native_equipment_stock_fixture=True,
        native_controller_combat_and_pickups=True,native_menu_transitions=124,heading_errors=0,visible_mask_writes=0,native_scopes=native_scopes)
    result=dict(passed=True,installed=True,backup_created=False,complete=False,user_requested_WIP=True,
        destination=str(nightly),output_sha256=EXPECTED,replaced_sha256=PREVIOUS,selectable_identities=86,total_menu_identities=90,
        selection='Rygar -> Select -> Karnov -> A/Start',checkpoint=D.relative_to(R).as_posix(),source=source,native=native,verification=verification,components=parts,
        controls='Select cycles earned Boots/Boomerang/Wings/NONE. Down+fresh B activates the highlighted option. A jumps; B fires. Up/Down move during flight.',
        changes=['Original Karnov Boots, Boomerang and Wings activation, stock consumption, motion and timers are integrated.',
                 'Full source button edges reach the equipment controller; source effects advance once per accepted game update.',
                 'New life selects NONE and clears equipment; same-life area changes preserve cursor/stock.',
                 'Twelve cold-loader rows copy and verify both equipment pages before either complete cache cookie is published.'],
        pending=['Equipment HUD/icons and original Karnov audio remain unfinished. Six other original equipment options are not enabled.',
                 'Equipment native tests use declared inventory fixtures; actual earned equipment progression/full1-1/shortcut/all-powerup tests remain unfinished.',
                 'Metal Storm, Shinobi and Excitebike remain unselectable; remaining new source characters and campaigns remain required.'],storage=preflight(fresh=True))
    text='''# Karnov original equipment WIP

The exact1c073196 candidate replaces the single Downloads nightly without a
backup. Reopen the ROM and start fresh. Rygar -> Select -> Karnov -> A/Start.

Select cycles earned Boots, Boomerang, Wings, then NONE. Down+freshB activates
the chosen equipment. A jumps; B fires. HoldUp/Down to move during flight.
Original source stock consumption,88px boots jump, boomerang return/base-shot
restoration and original timer leaves are retained. New life selects NONE;
same-life area transfers preserve selected equipment and stock.

Three native Mesen checks use six declared source inventory bytes to create
earned stock, then use real controller controls. They verify activation,
stock, displayed original body, boots jump, boomerang return and Up/Down flight.
They do not claim controller-earned equipment. CPU Main tests additionally
verify expiry and real IRQ/NMI resumption. The original curled flight pose
includes the wings in its body raster; no new wing artwork was invented.

Separate controller-only runs still defeat a Goomba with score/hitSFX, collect
an emerged mushroom and fire double shots, break a brick with debris, and
shoot a mushroom question block. All90 menu identities/124 transitions pass
the same sampled heading/gray-portrait/PPUMASK checks on this exact ROM.

The actual12-row loader verifies code before both complete16-byte cache
headers. Faults in either combat or equipment page deny both cache headers.
Native Main/cold-loader stack checks preserve at least12bytes above SMC.

Equipment HUD/icons, six other equipment types, original audio and full-stage
qualification remain unfinished. This is86 selectable WIP identities, not
a finished Karnov implementation or complete roster. Source/native packets
contain no ROM, full debugger/object tree, videos or per-frame captures.
'''
    (D/'README.md').write_text(text,encoding='utf-8')
    readme=(R/'README.md').read_text(encoding='utf-8')
    paragraph='**Karnov** is selectable: highlight Rygar, press Select, then A or Start. Original movement, fireballs, health, injury/death and stomp rebound are integrated. Shots damage enemies, break eligible bricks with debris and trigger question blocks. Select cycles earned Boots, Boomerang, Wings and NONE; Down+B activates the chosen equipment. Boots give the original higher jump, boomerangs return to the base shots, and wings use Up/Down flight controls. Equipment HUD/icons, other equipment, original audio and full-stage testing remain unfinished. See the [current WIP verification](docs/qa/checkpoints/2026-11-01/karnov-options-nightly-v8/README.md).'
    readme,n=re.subn(r'(?m)^\*\*Karnov\*\*.*$',lambda _:paragraph,readme);assert n==1
    latest='The latest delivered nightly is `1c073196` (November 1), with **86 selectable identities**. Karnov now has original Boots/Boomerang/Wings controls, stock, motion and timers alongside the preceding combat/pickup/health fixes. Native equipment checks use declared inventory fixtures; separate controller-only runs verify enemy defeat, brick/question-block effects and earned mushroom/double shots. The 124-transition menu sweep and source health/terrain/scene checks pass on this exact ROM. Equipment HUD/icons, other equipment/audio, full stages, shortcuts, all powerups and steady 60 Hz remain unfinished. See the [verification](docs/qa/checkpoints/2026-11-01/karnov-options-nightly-v8/README.md) and [delivery receipt](docs/qa/checkpoints/2026-11-01/karnov-options-nightly-v8/handoff.json).'
    readme,n=re.subn(r'(?m)^The latest delivered nightly is .*$',lambda _:latest,readme);assert n==1
    readme=readme.replace('docs/qa/checkpoints/2026-11-01/karnov-combat-nightly-v7/README.md','docs/qa/checkpoints/2026-11-01/karnov-options-nightly-v8/README.md')
    assert sha(J/'candidate.nes')==EXPECTED and sha(nightly)==PREVIOUS
    shutil.copyfile(J/'candidate.nes',nightly);assert sha(nightly)==EXPECTED
    (D/'handoff.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    (O/'binding.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    continuation=R/'docs/qa/continuation-current.json';q=json.loads(continuation.read_text())
    q.update(goal_status='ACTIVE_INCOMPLETE',previous_goal_turn_classification='progress',installed_nightly=result,
             current_priority='Delivered86-selectable1c073196 WIP with original Karnov Boots/Boomerang/Wings controls/timers. Next equipmentHUD/audio and other original equipment, then full-stage/shortcut/all-powerup qualification and remaining original-source roster.',
             completion='Not complete.86 selectable/90 menu identities; remaining characters, campaigns and full1-1/shortcuts/every-upgrade are required.',
             storage=result['storage'],Mesen='All root-owned SMB native queues for this delivery are terminal. Other projects may run concurrently; root owns the SMB queue.')
    continuation.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
    (R/'README.md').write_text(readme,encoding='utf-8')
    print(json.dumps(dict(passed=True,installed=True,backup_created=False,ROM_sha256=EXPECTED,checkpoint=str(D),source_bytes=source['bytes'],native_bytes=native['bytes'])))


if __name__=='__main__':main()
