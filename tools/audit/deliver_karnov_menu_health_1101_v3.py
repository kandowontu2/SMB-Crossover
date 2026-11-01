"""Freeze tested current WIP and replace the single Downloads nightly."""
from pathlib import Path
import hashlib,json,shutil,zipfile
from build_storage_guard_v1 import preflight
R=Path(__file__).resolve().parents[2]
J=R/'build/karnov-host-resource-base-1101-v1'
O=R/'build/karnov-menu-health-native-1101-v3'
D=R/'docs/qa/checkpoints/2026-11-01/karnov-menu-health-nightly-v3'
EXPECTED='e8d35a95ffe8e396dc1d8b32ca78d57d376fc14de9a2f4b37754012448fde09a'
PREVIOUS='be751275d00757ecaa51defcd2ccd5ea235921aa4b1f34337fa6c5c6e1877962'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def validate(q):
    for n,h in q.get('bindings',{}).items():
        p=Path(n);p=p if p.is_absolute()else R/p
        assert sha(p)==h,p


def pack(path,files):
    manifest={n:dict(sha256=sha(p),bytes=p.stat().st_size,original=str(p.resolve()))for n,p in files.items()}
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for n,p in sorted(files.items()):z.writestr(n,p.read_bytes())
        z.writestr('files.json',json.dumps(manifest,indent=2)+'\n')
    assert path.stat().st_size<2000000
    return dict(path=path.relative_to(R).as_posix(),sha256=sha(path),bytes=path.stat().st_size,members=len(files)+1)


def main():
    preflight(private_root=O,reserved_bytes=6000000,reserved_files=12,fresh=True)
    assert not D.exists()and not(O/'binding.json').exists()
    assert sha(J/'candidate.nes')==EXPECTED
    stage=json.loads((J/'terrain-assembly.json').read_text());validate(stage)
    assert stage['passed']and stage['health']and stage['rebound']and stage['menu_input']
    suite=json.loads((J/'menu-health-suite.json').read_text());validate(suite)
    assert suite['passed']and suite['ROM_sha256']==EXPECTED
    cpu={}
    for n,h in suite['receipts'].items():
        p=J/n;assert sha(p)==h;q=json.loads(p.read_text());validate(q)
        assert q['passed']and q['ROM_sha256']==EXPECTED;cpu[n]=q
    composed_root=R/'build/karnov-menu-input-composed-1101-v3'
    composed=json.loads((composed_root/'result.json').read_text());validate(composed)
    assert composed['passed']and composed['ROM_sha256']==EXPECTED and not composed['overlay']
    assert composed['playable']==86 and composed['identities']==90
    native={};native_files={}
    for name in ['opening','injury','menu']:
        child=O/name;ready=json.loads((child/'ready.json').read_text());validate(ready)
        binding=json.loads((child/'capture/binding.json').read_text());q=json.loads((child/'capture/result.json').read_text())
        assert binding['exit_code']==0 and binding['ready_sha256']==sha(child/'ready.json')
        assert q['passed']and q['ROM_sha256']==binding['ROM_sha256']==EXPECTED
        files=[p for p in child.rglob('*')if p.is_file()]
        assert len(files)<=64 and sum(p.suffix=='.png'for p in files)<=4
        assert sum(p.stat().st_size for p in files)<128000000
        for p in files:native_files[name+'/'+p.relative_to(child).as_posix()]=p
        native[name]=q
    assert len(native['menu']['transitions'])==124 and not native['menu']['anomalies']
    assert native['menu']['heading_errors']==native['menu']['visible_mask_writes']==0
    assert native['opening']['jumped']and native['opening']['landed']and native['opening']['maximum_projectiles']==1
    assert native['injury']['blue_health_seen']and native['injury']['health_calls']>0 and not native['injury']['death_seen']
    prior=R/'docs/qa/checkpoints/2026-11-01/requested-wip86-native-v2/source.zip'
    with zipfile.ZipFile(prior)as z:manifest=json.loads(z.read('files.json'))
    sources={n:Path(v['original'])for n,v in manifest.items()if not n.endswith('.json')}
    for n in ['kr-health.inc','kr-rebound.inc','menu-input.inc','characters.s','menu-input-entry.s','candidate.cfg','terrain-assembly.json','main-build.json','link.json','terrain-main-build.json','terrain-kernel-build.json','terrain-first-link.json','terrain-images-build.json','terrain-final-link.json','ingress-union-build.json','menu-health-suite.json']:
        sources['host/'+n]=J/n
    for n in suite['receipts']:sources['host/'+n]=J/n
    for n in ['build_karnov_gameplay_host_1101_v1.py','prepare_karnov_rebound_1101_v2.py','prepare_karnov_health_1101_v2.py','check_karnov_health_1101_v2.py','check_karnov_rebound_1101_v2.py','check_karnov_life_restart_1101_v3.py','prepare_menu_input_1101_v3.py','check_menu_input_1101_v3.py','check_menu_input_composed_1101_v3.py','check_karnov_menu_access_1101_v3.py','check_karnov_menu_health_suite_1101_v3.py','prepare_karnov_menu_health_native_1101_v3.py','deliver_karnov_menu_health_1101_v3.py']:
        sources['tools/audit/'+n]=R/'tools/audit'/n
    for n in ['karnov_health_1101_v2.inc','karnov_host_rebound_1101_v2.inc','menu_input_1101_v3.inc']:
        sources['tools/reference/'+n]=R/'tools/reference'/n
    sources['parent-source/characters.s']=R/'build/bt-p2-cf-menu-source-1031-v2/joint/src/characters.s'
    for n in ['baseline.json','result.json']:sources['menu-composed/'+n]=composed_root/n
    D.mkdir();source=pack(D/'source.zip',sources);natives=pack(D/'native-results.zip',native_files)
    # Preserve the agents' compact source components; these are not wired into
    # this ROM and must not be advertised as additional playable functionality.
    components={}
    for label,root,archive,expected in [
        ('pickups','karnov-pickup-component-1101-v2','source-proof.zip','56de530e2827d217bb98eeea1eb9c08f1d63363ba768aedbdb7f4aed049170e1'),
        ('combat','karnov-combat-component-1101-v2','source-and-proof.zip','87eb2bebe69fa5af709febae60a2e117ddce4d011e17cc41f26783998be1ce2a')]:
        p=R/'build'/root/archive;assert sha(p)==expected
        target=D/(label+'-component.zip');shutil.copyfile(p,target)
        components[label]=dict(path=target.relative_to(R).as_posix(),sha256=sha(target),integrated=False)
    nightly=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
    previous=sha(nightly);assert previous==PREVIOUS
    shutil.copyfile(J/'candidate.nes',nightly);assert sha(nightly)==EXPECTED
    result=dict(passed=True,installed=True,backup_created=False,user_requested_WIP=True,complete=False,
        destination=str(nightly),output_sha256=EXPECTED,replaced_sha256=previous,
        selectable_identities=86,previously_verified_identities=85,total_menu_identities=90,
        selection='Rygar -> Select -> Karnov -> A/Start',checkpoint=D.relative_to(R).as_posix(),source=source,native=natives,
        changes=['Real alternate consumers run before simultaneous Select+confirm. Select edges during roster construction are deferred; B/title reentry retains the chosen alternate. Cold reset retains original defaults.',
            'Karnov now uses original first-hit health/blue palette/128-update immunity, fatal/death animation, life loss and fresh next-life state.',
            'Public stomp rows27/31 restart original jump state. Post-BG reconciliation has its own private row36, preventing stomp velocity from being overwritten.'],
        verification=dict(ROM_sha256=EXPECTED,source_CPU_suite=list(suite['receipts']),menu_native_calls=composed['actual_native_calls'],menu_identities=90,Start_A=composed['Start_A_cases'],combined_cases=composed['combined_equals_separate_cases'],deferred_edges=composed['deferred_BuildScreen_contexts'],title_reentries=composed['all_identity_title_reentries'],native_menu_transitions=124,native_menu_frames=native['menu']['frames'],sampled_gray_anomalies=0,heading_errors=0,visible_mask_writes=0,opening_Main=native['opening']['Main'],opening_source_shots=native['opening']['maximum_projectiles'],injury_Main=native['injury']['Main'],injury_ISR_returns=native['injury']['ISR_returns'],first_injury_and_invulnerability_observed=True,life_restart='Source CPU actual native parser/Main/NMI; declared depleted-health fixture. Not a controller-earned fatal collision.'),
        components=components,
        pending=['Karnov native projectile enemy/block combat and contact-earned pickups/options are not integrated yet; compact agent components are preserved separately.','Original audio, equipment activation, native option HUD/icons, full1-1/shortcut/every-powerup testing remain unfinished.','Metal Storm, Shinobi and Excitebike remain source components without selectable host integration.','The exact user-reported inaccessible-selection path remains unknown; three reproduced input traps are now fixed, not a claim that every input-device configuration was tested.'],
        diagnostics=['Earlier encounter attempts used CPU-address reads for banked source state; corrected to physical nesWorkRam before current qualification. Old three-projectile observation was invalid; current starting weapon shows one actual source projectile.','A broader controller death route failed to regain contact with the same goomba before reaching the locked left camera edge. It was not counted as a passing death/restart test; that boundary has a separate explicit source-CPU fixture.'],
        storage=preflight(fresh=True))
    (D/'handoff.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    (D/'README.md').write_text('''# Current selectable WIP: menu input and Karnov health

The single Downloads nightly is replaced directly, without a backup. Reopen it
and start fresh. Choose Rygar, press Select for Karnov, then A/Start.

Three actual alternate-selection traps are fixed: simultaneous Select+confirm,
Select pressed while the roster is being constructed, and alternate loss when
returning via B/title. Current composed code passes all90 menu identities and
3,020 native-code calls. The native124-transition sweep has no sampled gray
roster anomalies, heading errors or visible PPUMASK writes.

Karnov now has original health/damage/death and a source-state stomp rebound.
The exact ROM has native controller openings for jump/landing, source shooting,
camera, and a real first injury through expiry of the original128-update timer.
Actual death/life-loss/parser restart/control is verified in the CPU model with
a declared depleted-health fixture; no controller-earned fatal-hit claim.

The source suite also checks donor leaves, native collision queries, 770 real
interrupt cuts, all85 existing scene owners and72 actual Main interrupt cuts.
The guide to test scope and remaining limits is handoff.json. This is86
selectable identities, with Karnov still unfinished, not86 complete characters.

Pickups and combat ZIPs are independent agent source/proof components. They are
not runtime features in this ROM. Their integration, option activation/icons,
original audio and full-stage testing remain next work. Metal Storm, Shinobi
and Excitebike also remain unintegrated source components.

The composed menu receipt binds the preceding Downloads ROM as its historical
initializer reference. That file was intentionally replaced after validation.
Source/native ZIPs contain compact overlays, recipes and receipts; prior frozen
composition dependencies remain required. No ROMs, debug objects or videos are
embedded in these packets.
''',encoding='utf-8')
    (O/'binding.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    p=R/'docs/qa/continuation-current.json';state=json.loads(p.read_text())
    state['installed_nightly']=result
    state['current_priority']='Delivered current86 WIP e8d35a95 with three alternate-input fixes, Karnov original health/death/next-life and separate stomp/post-BG rows. All exact-candidate source/native gates pass. Next integrate contact pickups through reviewed puretransformer, then source projectile combat only after carrier ownership, forcedblank copy/readback and real Main stack proof. Publish each usable integrated WIP to same Downloads file without backup; preserve full roster/campaign/every-powerup goals.'
    k=state['Karnov_current'];k.update(installed=True,installed_nightly_sha256=EXPECTED,installed_selectable=86,previously_verified_identities=85,current_WIP_checkpoint=result['checkpoint'])
    k['current_WIP_policy']='Same selectable test WIP is delivered promptly. Complete-character qualification remains unfinished; historical component records below retain their original hashes/scopes.'
    k['current_menu_health']=dict(checkpoint=result['checkpoint'],ROM_sha256=EXPECTED,services=stage['implemented_services'],resident_bytes=stage['resident_bytes'],kernel_bytes=stage['kernel_bytes'],new_menu_helper='107B existing PROTO_MENU padding +26B appended existing PROTO_PALETTE_ACK;0 ROM29/kernel/newSRAM',verification=result['verification'],components=components)
    k['next']=['Integrate reviewed pickup puretransformer tools/audit/prepare_karnov_pickup_host_1101_v3.py; source-based block item selection, real emergence/contact, original progression/options; actual Main/ISR qualification required.','Combat source1040B+C2context32+A3wrapper12 passes isolated contacts/interrupts. CHR1019/1020 carrier still requires all-other-owner closure, forcedblank copy/readback before cookies, and real Main-depth stack proof. Never allocate from zero-fill alone.','Wire original option activation/Select/icons/HUD and audio, then full1-1/shortcut/every-powerup; other source characters and campaigns remain in scope.']
    state['storage']=result['storage'];p.write_text(json.dumps(state,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items()if k not in ['storage','diagnostics']}))


if __name__=='__main__':main()
