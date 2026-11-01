"""Deliver only an exact owning-link/Main/native-qualified Kirby repair."""
from pathlib import Path
import argparse,hashlib,json,re,shutil,zipfile
from build_storage_guard_v1 import preflight
from deliver_karnov_menu_health_1101_v3 import pack,validate

R=Path(__file__).resolve().parents[2]
J=R/'build/kirby-owner-main-1101-v2';N=R/'build/kirby-owner-native-1101-v2'
D=R/'docs/qa/checkpoints/2026-11-01/kirby-owner-nightly-v2'
BASE='99bf88c8d971f1305f965a21833703c7a11aafa6a24febd9f3bfb7c87ba4bbda'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def checked(path,pin):
    q=json.loads(path.read_text());validate(q)
    assert q['passed']and q['ROM_sha256']==pin,path
    return q


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--expected',required=True);ap.add_argument('--native',type=Path,required=True);a=ap.parse_args()
    pin=a.expected;assert len(pin)==64 and sha(J/'candidate.nes')==pin
    preflight(private_root=N,reserved_bytes=3000000,reserved_files=10,fresh=True)
    assert not D.exists()and not(N/'binding.json').exists()
    owner=checked(J/'owner-link.json',pin);cpu=checked(J/'Main-CPU.json',pin)
    foreign=checked(J/'foreign-body-CPU.json',pin)
    closure=checked(J/'source-closure.json',pin)
    assert owner['base_ROM_sha256']==BASE and owner['source_owner_relinked']and cpu['source_CPU']
    assert cpu['interrupts']['passed']and cpu['interrupts']['minimum_ISR_SP']>=135
    child=a.native.resolve();assert child.is_relative_to(N)
    ready=json.loads((child/'ready.json').read_text());validate(ready)
    native=checked(child/'capture/result.json',pin);binding=json.loads((child/'capture/binding.json').read_text())
    assert ready['emulated_writes']and not ready['baseline_expected_failure']
    assert binding['exit_code']==0 and binding['ready_sha256']==sha(child/'ready.json')and binding['ROM_sha256']==pin
    assert native['actual_numeric_mode']==1 and len(native['cases'])==3 and native['screenshots']<=4
    assert native['disclosed_scene_actor_setup']and native['no_ability_or_health_seeds']
    for q in native['cases']:
        assert q['before']['hp']==q['ending']['hp']==6 and q['captures']==1 and q['injuries']==0 and q['defeats']
        if q['kind']=='copy':assert q['swallows']==1 and q['attacks']>0
    files=[p for p in child.rglob('*')if p.is_file()]
    assert len(files)<=64 and sum(p.suffix=='.png'for p in files)<=4 and sum(p.stat().st_size for p in files)<128000000
    assert not any(p.suffix in ['.nes','.dbg','.o','.mp4','.avi']for p in files)
    nightly=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes');assert sha(nightly)==BASE
    parent=R/'docs/qa/checkpoints/2026-11-01/karnov-hud-nightly-v9/handoff.json';old=json.loads(parent.read_text())
    assert old['passed']and old['output_sha256']==BASE
    previous=R/old['source']['path'];assert sha(previous)==old['source']['sha256']
    with zipfile.ZipFile(previous)as z:
        manifest=json.loads(z.read('files.json'));data={n:z.read(n)for n in manifest}
    updates={}
    for p in J.iterdir():
        if p.is_file()and p.suffix in ['.s','.inc','.cfg','.json','.py','.md']:updates['kirby-owner/'+p.name]=p
    for n in ['prepare_kirby_owner_main_1101_v2.py','prepare_kirby_body_ingress_1101_v2.py','check_kirby_owner_main_1101_v2.py','prepare_kirby_owner_native_1101_v2.py','prepare_kirby_native_diagnostic_1101_v3.py','deliver_kirby_owner_1101_v2.py']:
        updates['tools/audit/'+n]=R/'tools/audit'/n
    for q in [owner,cpu,foreign,closure]:
        for n,h in q.get('bindings',{}).items():
            p=Path(n)
            if p.parent==R/'tools/audit'and p.name.startswith(('prepare_kirby','check_kirby')):
                assert sha(p)==h;updates['tools/audit/'+p.name]=p
    caller=cpu['actual_Main_caller'];assert caller['GameLoop_entry_SP']==250
    witness=Path(caller['native_entry_witness_path']);assert sha(witness)==caller['native_entry_witness_sha256']
    updates['verification/native-entry-SP.json']=witness
    for n in ['ready.json','controller.lua','run.py']:
        updates['verification/native-entry-'+n]=N/'stack'/n
    updates['tools/audit/prepare_kirby_stack_native_1101_v4.py']=R/'tools/audit/prepare_kirby_stack_native_1101_v4.py'
    # Preserve earlier negative runs, the owner trace and the intermediate
    # native pass. Their hashes remain historical, not successor evidence.
    for run in ['baseline','fixed','diagnostic','fixed-routed']:
        root=N/run
        for p in root.rglob('*'):
            if p.is_file()and p.suffix in ['.lua','.json','.log','.csv']:updates['historical-native/'+run+'/'+p.relative_to(root).as_posix()]=p
    for n,p in updates.items():data[n]=p.read_bytes();manifest[n]=dict(original=str(p.resolve()),bytes=len(data[n]),sha256=sha(p))
    D.mkdir()
    source=D/'source.zip'
    with zipfile.ZipFile(source,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for n,v in sorted(data.items()):
            assert len(v)==manifest[n]['bytes']and hashlib.sha256(v).hexdigest()==manifest[n]['sha256'];z.writestr(n,v)
        z.writestr('files.json',json.dumps(manifest,indent=2)+'\n')
    assert source.stat().st_size<2000000
    source_note=dict(path=source.relative_to(R).as_posix(),sha256=sha(source),bytes=source.stat().st_size,members=len(data)+1,inherited_source_packet=previous.relative_to(R).as_posix(),inherited_sha256=sha(previous))
    capture=pack(D/'native-results.zip',{p.relative_to(child).as_posix():p for p in files})
    metal=R/'build/metal-storm-coexistence-1101-v9/source-proof.zip';metal_hash='fac9a37cc67a42d0ffe080a85cca6e20b04d5892da864c8b2b9f3aea0decadf5'
    assert sha(metal)==metal_hash;target=D/'metal-storm-player-palette.zip';shutil.copyfile(metal,target)
    tank=R/'build/mario-tank-host-1101-v2/source-proof.zip';tank_hash='6dea7920bdb5795403376f6cd11b967cb5439c8cc0c956fe35b90e334135ea84'
    assert sha(tank)==tank_hash;tank_target=D/'mario-tank-host.zip';shutil.copyfile(tank,tank_target)
    result=dict(passed=True,installed=True,backup_created=False,complete=False,user_requested_WIP=True,
        destination=str(nightly),output_sha256=pin,replaced_sha256=BASE,selectable_identities=86,total_menu_identities=90,
        checkpoint=D.relative_to(R).as_posix(),source=source_note,native=capture,
        owning_candidate=str(J/'candidate.nes'),owning_build_recipe='tools/audit/prepare_kirby_owner_main_1101_v2.py',
        verification=dict(ROM_sha256=pin,actual_Main=True,Main_ISR_minimum_SP=cpu['interrupts']['minimum_ISR_SP'],
            Main_ISR_cases=cpu['interrupts']['cases'],native_cases=3,native_mode='Hard',native_scope=ready['scope'],
            actual_Main_entry_SP=250,native_entry_SP_updates=caller['native_entry_updates'],
            native_frames=native['wall'],native_updates=native['updates'],native_screenshots=native['screenshots'],
            native_IRQ31=native['IRQ31_checks'],native_NMI=native['NMI_checks'],native_complete256_DMA=native['complete256_DMAs'],
            foreign_dispatch_receipt_sha256=sha(J/'foreign-body-CPU.json'),foreign_dispatch_ABI_verified=True,
            exact_source_closure_sha256=sha(J/'source-closure.json'),
            inherited_HUD_checkpoint=old['checkpoint'],inherited_HUD_ROM_sha256=BASE,
            inherited_HUD_evidence_not_renamed_to_successor=True),
        changes=['Native enemy contacts now reach Kirby body protection during the original eight-update inhale opening.',
                 'Copied green/red shells move3px per update and use real native enemy boxes, including ground-level and page-boundary contacts.'],
        pending=['Full1-1/shortcut/every-powerup testing and the remaining character/campaign integrations remain unfinished.',
                 'Karnov original audio and other equipment remain unfinished. Metal Storm, Shinobi and Excitebike are still unselectable.'],
        components=dict(metal_storm_palette=dict(path=target.relative_to(R).as_posix(),sha256=metal_hash,integrated=False),
                        mario_tank_host=dict(path=tank_target.relative_to(R).as_posix(),sha256=tank_hash,integrated=False)),
        storage=preflight(fresh=True))
    (D/'README.md').write_text(f'''# Kirby native contact and shell repair

The exact `{pin[:8]}` build replaces the sole Downloads nightly with no backup.
Reopen the ROM and start fresh. There are86 selectable identities.

The actual enemy-body route previously bypassed Kirby's guard entirely. Native
Mesen and Main CPU tests both reproduced injury despite an open mouth. The
repaired route reaches the existing guard, which now protects edible enemies in
front during the original eight-update capture startup. Rear/released-B and
hazard contacts remain ordinary. Copy acquisition still requires inhale/Down.

Copied green/red shells use3px/update and actual native enemy collision boxes.
The red shell reverses at32updates, retaining the prior outward reach to1px.
The native test earns both through real capture/Down, then defeats ordinarily
grounded Goombas with the respective shells. A separate fresh-inhale/spit case
also passes. All three retain6HP, real native defeats and the hardware DMA,
CHR, NMI/IRQ guards. Flat terrain/player/NPC fixtures are explicitly declared;
no health, copy, mouth, shot, input edge or outcome is injected. Three PNGs are
retained. Source Main/interrupt tests verify the stack reserve independently.
They execute the real reset/IdleLoop caller, matching the entry stack observed
in965native updates. A prior artificial banked-API caller produced a stack
overlap; that invalid caller test is preserved with its original failure.

The preceding Karnov HUD delivery remains documented under its original99bf
hash. Its records are inherited through the precise owning-link byte comparison
and foreign dispatch comparison,
not relabelled as new native runs. Original negatives and the unreachable-guard
trace are retained. Full stages, all-character playthroughs, all powerups,
remaining characters and campaigns remain required. Metal Storm's player-only
palette proposal is preserved separately and is not installed by this update.
''',encoding='utf-8',newline='\n')
    readme=(R/'README.md').read_text(encoding='utf-8')
    paragraph='**Kirby** now protects eligible enemies in front during inhale startup. The native collision route has been repaired so it reaches his guard. Copied green/red shells use native enemy boxes and a3px/update speed, fixing the tested ground-level misses. Three bounded Hard-mode emulator cases earn and use these moves without granting health or abilities; full-stage and all-powerup testing remain unfinished. See the [repair verification]('+D.relative_to(R).as_posix()+'/README.md).'
    if re.search(r'(?m)^\*\*Kirby\*\*',readme):readme=re.sub(r'(?m)^\*\*Kirby\*\*.*$',lambda _:paragraph,readme)
    else:
        marker='**Character selection**';assert marker in readme;readme=readme.replace(marker,paragraph+'\n\n'+marker,1)
    latest=f'The latest delivered nightly is `{pin[:8]}` (November 1), with **86 selectable identities**. It includes Kirby\'s inhale/contact and ground-shell repairs plus Karnov\'s equipment HUD and preceding improvements. Actual Main/ISR and three focused native Hard-mode Kirby cases pass on this exact ROM. Full stages, shortcuts, every character/powerup and steady60Hz remain unfinished. See the [verification]({D.relative_to(R).as_posix()}/README.md) and [delivery receipt]({D.relative_to(R).as_posix()}/handoff.json).'
    readme,n=re.subn(r'(?m)^The latest delivered nightly is .*$',lambda _:latest,readme);assert n==1
    assert sha(J/'candidate.nes')==pin and sha(nightly)==BASE
    shutil.copyfile(J/'candidate.nes',nightly);assert sha(nightly)==pin
    (D/'handoff.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    (N/'binding.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    (R/'README.md').write_text(readme,encoding='utf-8',newline='\n')
    p=R/'docs/qa/continuation-current.json';q=json.loads(p.read_text())
    q.update(goal_status='ACTIVE_INCOMPLETE',previous_goal_turn_classification='progress',installed_nightly=result,
        current_priority='Kirby native contact/shell repair delivered. Continue Mario the Tank and Metal Storm admission; Karnov remaining equipment/audio, full-stage/shortcut/every-upgrade and remaining roster/campaign work.',
        current_owning_candidate=str(J/'candidate.nes'),current_owning_build_recipe=result['owning_build_recipe'],
        source_override_required='Do not rebuild from the older Karnov Main alone: the current Kirby override and S2 boundary repair must remain composed.',
        storage=result['storage'])
    q['active_source_components']['metal_storm_palette']=result['components']['metal_storm_palette']
    q['active_source_components']['mario_tank_host']=result['components']['mario_tank_host']
    q['active_source_components']['kirby_repair']=dict(integrated=True,checkpoint=result['checkpoint'],ROM_sha256=pin)
    p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,installed=True,backup_created=False,ROM_sha256=pin,source_bytes=source.stat().st_size,native_bytes=capture['bytes'])))


if __name__=='__main__':main()
