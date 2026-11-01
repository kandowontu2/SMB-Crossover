"""Checkpoint original Karnov components and source-proved current-cart fit."""
from pathlib import Path
import hashlib,json,sys,zipfile
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from build_storage_guard_v1 import inventory
B=R/'build/karnov-original-source-1101-v1';W=R/'build/karnov-original-weapons-1101-v1';A=R/'build/karnov-original-art-1101-v1';H=R/'build/karnov-host-resource-base-1101-v1'
O=R/'build/karnov-source-checkpoint-1101-v1';K=R/'docs/qa/checkpoints/2026-11-01/karnov-original-component-v1'
DEST=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes');EXPECTED='f6415a64767b9ea1ada79ac5ccab433d7b1f4ae5f8bb13e53f04adeca717a3f1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')


def bound(p):
    q=json.loads(p.read_text(encoding='utf-8'));assert q['passed']
    for f,h in q['bindings'].items():assert sha(f)==h,f
    return q


def archive(path,files):
    files={p.resolve()for p in files};assert len(files)<128 and sum(p.stat().st_size for p in files)<4_000_000
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in sorted(files):z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(path)as z:assert z.testzip()is None
    return dict(path=path.relative_to(R).as_posix(),sha256=sha(path),bytes=path.stat().st_size,members=len(files))


def main():
    assert not O.exists()and not K.exists();assert sha(DEST)==EXPECTED
    actor=bound(B/'assembly.json');physics=bound(B/'CPU-controls.json');weapon=bound(W/'assembly.json');shots=bound(W/'CPU-controls.json');art=bound(A/'art-controls.json');resources=bound(H/'baseline-controls.json')
    native_roots=[R/'build'/n for n in ['karnov-native-reference-1101-v1','karnov-palette-native-1101-v1','karnov-frame-order-native-1101-v1']]
    for p in native_roots:bound(p/'controls.json')
    O.mkdir();K.mkdir(parents=True)
    source={p for root in [B/'source',W/'source']for p in root.iterdir()if p.is_file()}
    source|={B/n for n in ['assembly.json','CPU-controls.json','build-commands.json']};source|={W/n for n in ['assembly.json','CPU-controls.json','build-commands.json']}
    source|={A/n for n in ['body.chr','art-controls.json','original-poses.png']};source|={H/n for n in ['baseline-controls.json','candidate.cfg','entrypoint.s','character_select.s','cf_menu_body.inc','main-build.json','link.json','main.dep']}
    source|={R/'build/karnov-current-resource-audit-1101-v1/inventory.json'}
    names=['probe_karnov_original_1101_v1.py','probe_karnov_palette_1101_v1.py','probe_karnov_frame_order_1101_v1.py','recover_karnov_actor_1101_v1.py','check_karnov_actor_1101_v1.py','recover_karnov_art_1101_v1.py','recover_karnov_weapons_1101_v1.py','check_karnov_weapons_1101_v1.py','inventory_ready85_karnov_1101_v1.py','prepare_karnov_host_resources_1101_v1.py','freeze_karnov_source_1101_v1.py']
    source|={R/'tools/audit'/n for n in names};source|={R/'tools/reference/karnov_original_probe_1101_v1.lua'}
    proof=set()
    for root in native_roots:
        proof|={root/'controller.lua',root/'controls.json'};proof|={p for p in(root/'capture').iterdir()if p.is_file()}
    src=archive(K/'source.zip',source);nat=archive(K/'native-reference.zip',proof)
    plan=dict(passed=True,goal_complete=False,source_CPU=True,native_original=True,native_port=False,admitted=False,installed=False,installed_nightly_sha256=EXPECTED,installed_playable=85,donor_sha256=actor['donor_sha256'],source=src,native_reference=nat,
        recovered_actor_instructions=actor['recovered_instructions'],original_fixed_16KiB_exact=actor['entire_fixed_16KiB_reproduced'],original_bank11_8KiB_exact=weapon['original_bank11_8KiB_exact'],private_actor_weapon_bytes=shots['combined_actor_weapon_bytes'],
        actor_CPU=dict(selector_pairs=physics['selector_boundary_pairs'],coherent_updates=physics['source_sequence_updates'],engine_executions=physics['total_engine_executions'],jump_rises=sorted(set(physics['source_jump_rises']))),
        weapon_CPU=dict(boundaries=shots['normal_projectile_boundaries']+shots['boomerang_boundaries'],coherent_updates=shots['coherent_updates'],engine_executions=shots['total_engine_executions'],clear_helper_executions=shots['native_clear_helper_executions'],order=shots['real_original_order']),
        graphics=dict(cases=art['original_render_cases'],pages=art['packed_CHR_pages'],patterns=art['unique_8x16_patterns'],palette=art['original_body_palette'],intentional_hidden_source_cases=art['hidden_source_cases']),
        private_resource_partition=dict(resident=resources['resident'],CHR_kernel=resources['CHR_kernel'],CHR_body=resources['CHR_body'],RAM='Not granted/implemented by this partition. Future selected C2/RAM3 use requires full cookie/epoch/IRQ/owner checks.',baseline_all_bytes_and_symbols_exact=True,baseline_candidate=EXPECTED),
        active_roots=dict(actor=B.relative_to(R).as_posix(),weapons=W.relative_to(R).as_posix(),art=A.relative_to(R).as_posix(),host=H.relative_to(R).as_posix()),
        next=['Implement the source-sized selected-owner kernel, cold loader and guarded36-service host dispatcher, preserving all85 playable identities','Recover/use native health/injury leaves CA2B..CA50/CB69..CB8B and palette-command helper C2C7..C2DF; actual collision admission currently belongs to C969','Recover actual options activation/stock/timers and earned Super Fireball pickups; source weapon-state fixtures do not prove collectible progression','Connect native SMB head/side/feet/camera/pipes/flagpole and independent source projectile slots to native enemies/blocks; retain original clamp as an explicit host boundary adaptation','Publish actual six-cell art, default/injured palettes and authentic bullet/boomerang patterns; unused pairs in body source page3 may hold projectile art after complete read closure','Recover original audio and qualify IRQ/NMI/SMC/private pointer restoration before controller-earned native admission','Continue Metal Storm/Shinobi/Excitebike/Prince of Persia, Sonic3 and other named goal characters; then every1-1/shortcut/every-powerup audit'],
        limits=['Karnov remains coming soon in the installed85 build. Source proof is not a playable character or native host qualification.','Original sound/terrain/scene callbacks are isolated in CPU tests; no acoustic, complete original-game or physical-console fidelity claim.','All32 selector roots are recovered; finite fixtures do not establish complete options, health, terrain, combat, music or campaign behavior.','The pointer wrapper restores borrowed ZP in isolated tests; real interrupt/mapper admission remains required.','Source snapshots and proofs are frozen here; active build roots remain unqualified/mutable for continued integration. Do not recursively restore historical trees or reuse stale mutable bindings after edits.'],
        primary_manual='https://www.gamingalexandria.com/highquality/NES/Karnov/Karnov%20-%20Manual%20(Searchable).pdf')
    save(K/'handoff.json',plan)
    (K/'README.md').write_text('''# Original Karnov component — private source progress

Karnov is still **COMING SOON** in the installed85-character nightly. This
packet recovers his own NES code and art; it does not enable a Rygar reskin.
The donor SHA and finite verification scope are in `handoff.json`.

The controller covers all32 source selector roots, including the native
injury-timer prefix, jump/walk/crouch/attack and ladder/flying/swimming/script
states. Its generated original instructions and tables, plus explicitly
untouched fixed-bank ranges, reconstruct the complete original16KiB exactly.
The corresponding weapon-bank reconstruction reproduces its8KiB exactly.
Those are byte-reproduction statements, not semantic disassemblies of every
untouched byte. The private actor/weapon/clear component occupies3,969 bytes.

CPU checks compare4,096 actor boundaries and5,760 coherent movement updates.
The declared floor/ceiling cases produce48-pixel normal and88-pixel boot jumps.
Another2,688 projectile boundaries and1,440 coherent updates cover all nine
slots, single/double/triple fireballs and four boomerang phases, catch/reuse,
miss/reversion and the actual clear helper. In total30,848 engine executions
pass. Private RAM/events/flags/Y/SP agree; differing A/X bytes are accepted
only with last-writer proof that they are relocated dispatch-pointer bytes.
Sound/terrain/scene callbacks are explicitly isolated in these comparisons.

Original Mesen observations establish the actual loop order: body rendering,
shot rendering, player update, then projectile update. A separate original
PPU observation verifies the source body page and default0F/28/16/0F palette.
All256 original six-cell render cases retain source pixels, positions and
flips after moving their tiles from sprite window4 to0. The five original
pages and134 unique tile pairs include70 deliberately hidden source cases.

The current85 ROM has an unused13-page ship tail after the live world/UI
pages. Explicit source splits reserve399..<407 for a future kernel and
407..<412 for body patterns. The actual menu helper's remaining FF pad
reserves2,432 resident bytes in bank29/B630..<BFB0. Rebuilding these source
partitions reproduces every installed ROM byte and every old symbol. PRG125
is an active post-link fixed/DMC mirror and is excluded from reclamation.
No RAM, executable host gate, new admission or nightly update is made here.

Health/options/pickups, real SMB terrain/contact/camera/scene adapters, native
sprite publication, audio, guarded owner loading and interrupt qualification
remain required. The [original Data East manual](https://www.gamingalexandria.com/highquality/NES/Karnov/Karnov%20-%20Manual%20(Searchable).pdf)
documents A jump, B shoot and Select option activation; those original option
controls and stock limits still need their actual source integration.

`source.zip` contains only this component, art, recipes and source partition.
`native-reference.zip` keeps bounded original-ROM observers, compact field
logs and selected PNGs. No ROM, object, debugger, video or frame-image forest
is archived. Reuse existing frozen inputs and recover only exact needed files.
The full requested roster and every-character level/powerup goal remain open.
''',encoding='utf-8')
    hand=R/'docs/qa/continuation-current.json';q=json.loads(hand.read_text(encoding='utf-8'));q.update(previous_goal_turn_classification='progress',goal_status='ACTIVE_INCOMPLETE',current_priority='Finish Karnov host integration from the verified original actor/weapon/art components and byte-identical resource baseline. Installed85 remains unchanged until a real86-identity candidate passes. Preserve all remaining characters and full1-1/shortcut/every-powerup objective.',Karnov_current=plan)
    q['other_full_objective_work']=['Karnov source component is ready for host integration; options/health/pickups/audio/real gameplay still pending','Metal Storm, Shinobi, Excitebike and Prince of Persia remain pending','Sonic3-reference integration, Donkey Kong Jr., Jay McCray, Steve Hermann, Mega Giant Mario and Getsu Fuma remain required','Finish authentic moves/upgrades/audio and known graphics/lag issues across the enabled roster','Every character clears1-1 and the shortcut route and uses every powerup','SMB2J and All Night Nippon campaigns remain separate ongoing requested work'];save(hand,q)
    build_bytes,build_files=inventory(R/'build',5_000_000_000,20_000);workspace_bytes,workspace_files=inventory(R,70_000_000_000,500_000)
    save(O/'storage.json',dict(build_bytes=build_bytes,build_files=build_files,workspace_bytes=workspace_bytes,workspace_files=workspace_files,new_videos=0,new_frame_image_sequences=0))
    save(O/'result.json',plan);print(json.dumps(dict(passed=True,checkpoint=str(K),source_bytes=src['bytes'],native_reference_bytes=nat['bytes'],installed_nightly_changed=False,build_bytes=build_bytes,build_files=build_files)))


if __name__=='__main__':main()
