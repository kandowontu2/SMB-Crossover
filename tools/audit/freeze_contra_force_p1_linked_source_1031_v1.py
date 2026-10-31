"""Freeze compact actual-linked CF P1 source evidence. Files only; no Git."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import zipfile

R = Path(__file__).resolve().parents[2]
P = R / 'build/contra-force-p1-coherent-cart-v2'
O = R / 'docs/qa/checkpoints/2026-10-31/contra-force-p1-linked-source-v1'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def put(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def labels(path):
    return {m[2]: int(m[1], 16) for m in re.finditer(r'^al ([0-9a-fA-F]+) \.([^\s]+)', path.read_text(), re.M)}


def main():
    assert not O.exists()
    O.mkdir()
    stage = json.loads((P / 'source-stage.json').read_text())
    assert stage['passed'] and stage['candidate'] == 'fbbc7b892e22f5bf808e74a04cbe9f2220f245dbd3e097994775a78d4a27fa08'
    for path, digest in stage['bindings'].items():
        assert sha(path) == digest, path
    directories = ['contra-force-p1-coherent-endpoints-v2', 'contra-force-p1-coherent-groups-v1',
                   'contra-force-p1-coherent-queue-v1', 'contra-force-p1-coherent-lifecycle-v1',
                   'contra-force-p1-coherent-api-vectors-v1', 'contra-force-p1-coherent-foreign-v1']
    receipts = [R / 'build' / d / 'controls.json' for d in directories]
    for path in receipts:
        doc = json.loads(path.read_text())
        assert doc['passed'], path
        for name, digest in doc['bindings'].items():
            assert sha(name) == digest, name

    oldjoint = R / 'build/bt-ready-menu-1031-v2/joint'
    oldlabels = labels(oldjoint / 'candidate.lbl')
    newlabels = labels(P / 'joint/candidate.lbl')
    moved = {name: [value, newlabels.get(name)] for name, value in oldlabels.items() if newlabels.get(name) != value}
    assert moved == {'Restore': [57273, 44738]}, moved
    old_recipe = json.loads((oldjoint.parent / 'final-link.json').read_text())['command']
    exports = set()
    census = []
    for name in old_recipe:
        if Path(name).suffix != '.o':
            continue
        text = subprocess.run([str(R / 'tools/Windows/cc65/bin/od65.exe'), '--dump-exports', name],
                              capture_output=True, text=True, check=True).stdout
        names = re.findall(r'Name:\s*"([^"]*)"', text)
        exports.update(names)
        census.append(dict(object=name, sha256=sha(name), exports=names))
    assert 'Restore' not in exports
    for name in exports:
        if name in oldlabels:
            assert newlabels.get(name) == oldlabels[name], ('Actual exported PC moved', name)
    put(O / 'public-symbol-proof.json', dict(passed=True, actual_parent_objects=len(census),
         actual_parent_exports=len(exports), all_old_exported_values_exact=True,
         old_LBL_values=len(oldlabels), old_LBL_changed_only_unexported_convenience_alias=moved,
         qualified_resolved_DBG_values_exact=stage['all_old_resolved_symbols_exact_except_private_replaced_draw_labels'],
         explanation='The new private67B worker has an unexported Restore label. Flat LBL convenience names select its address; every genuine old exported value and every qualified old DBG value outside the explicitly replaced59B draw routine remains exact.',
         object_export_census=census))

    groups = json.loads(receipts[1].read_text())['checks']
    vectors = json.loads(receipts[4].read_text())['checks']
    foreign = json.loads(receipts[5].read_text())['checks']
    source_scope = dict(status='FROZEN_ACTUAL_LINKED_PRIVATE_CF_P1_FINITE_SOURCE_QUALIFICATION',
        candidate=stage['candidate'], parent=stage['parent'], source=True, native=False,
        CF_ready=False, admitted=False, installed=False, actual_restore67_linked=True,
        synthetic_instruction_overlay=False, main_menu_M3_BT_objects_unchanged=True,
        changed_ROM_bytes=stage['changed_ROM_bytes'], allowed_envelopes=stage['allowed_envelopes'],
        current_installed68_unchanged='01a40d4019ae00220c7279c9ab8d4f6f25afb44af1612a6a1483a257448f0fa9',
        positive_scope=dict(
            all4_class_2native_state_complete_draws=8, stale_C1_poisoned_cookie_normalPPU_cases=16,
            unique_authenticated_source_shot_frames=groups['unique_actual_source_frames'],
            paired_complete_Draw_normalNMI=groups['paired_complete_Draws'],
            actual_A91_worker_API_flags=320, genuine_joined_ISR_cases=vectors['actual_vector_cases'],
            joined_instruction_seams=vectors['linked_instruction_seams'],
            actual_constructor_acquires=16, actual_MenuResolve_retires=16,
            real_native_queue_full_retry_lag_paused_heartbeat_late_store=True,
            established_47_identity_wholeMain_cases=foreign['established_47_identity_282_Main']['cases'],
            established_wholeMain_CPU_delta=foreign['established_47_identity_282_Main']['CPU_delta'],
            focused_Samus_FF_native_DrawAll=foreign['focused_native_Samus_FF_DrawAll']),
        hardware=dict(normal_limit=8, max_demand=groups['maximum_line_demand'],
                      overloaded_finite_cases=len(groups['overloaded_finite_cases']),
                      total_finite_cases=groups['paired_complete_Draws'],
                      all_hardware_pixels_visible_claimed=False),
        retained_negatives=[
            'Historical0b16 genuine C1 then badcookie leaves stale yellow on native P1; retained immutable. This linked67B successor now restores it through actual normalNMI.',
            'Historical67B v1 source macro precedence emitted C2 target and is explicitly unadoptable; only corrected a75 source linked here.',
            'Coherent producer v1 stopped before any compiler because linker metadata was queried in DBG rather than its real LBL table; v2 corrects that observer lookup only.',
            'Endpoint fixture v1 demanded all guest RAM be unchanged across public6; actual router records exactly five existing target/A/P scratch bytes. Separatev2 asserts those writes and every other bank/source/OAM byte unchanged.',
            'Prior research vector oracle failures and 256-main-segment layout proposal remain immutable; Stage2 existingRODATA source layout is the actual prerequisite here.',
            'Root BT native still has independent lives-color/game-body visibility blockers. This CF graft preserves its parent BT code exactly and does not admit BT/CF.'],
        remaining=['CF remains menu-pending; natural cold controller/native admission has not run.',
                   'Crowded normal eight-sprite hardware visibility remains limited; no repaired-crowding claim.',
                   'Root owns later BT fixes, coherent readiness and native/install. No native or download change here.'])
    put(O / 'scope-and-negatives.json', source_scope)
    (O / 'README.md').write_text('''# Contra Force linked P1 source successor

Actual fbbc is a genuine source link on the root BT-ready f0b7 source child. It preserves the actual main/menu/M3/BT objects and installs the corrected67B A91 worker through the prequalified M3 prefix/RODATA layout. No instruction fetch overlay or binary ROM patch is used.

Finite actual-cartridge CPU controls pass complete-group/pixel/final-CHR/PPU pairs, stale-cookie native-P1 restoration, native queue-full and late-publisher ordering, acquire/retire, full-flag worker ABI,80 joined real interrupt cuts and282 established foreign Main pairs. The latter is the declared47-identity suite, not a new all68 native campaign. Its actual Main CPU delta is +8.

CF is still pending and has no native/controller admission claim. Crowding still reaches12sprites/line with192of246 finite pairs above8. The root BT parent has separate native lives/body negatives; no BT repair or new readiness is included here.

The compact archive contains changed source/recipes/controls and the retained new negatives. It excludes NES,objects,EXEs,largeDBG/LBL,compiled carrier/cookies and duplicate parent archives. Complete existing frozen source/kernel prerequisites and actual parent inputs remain hash-bound by the source-stage. No Git staging/commit/install occurs.
''')

    tools = [R / 'tools/audit' / name for name in [
        'prepare_contra_force_p1_coherent_cart_v1.py', 'prepare_contra_force_p1_coherent_cart_v2.py',
        'contra_force_p1_coherent_controls_v1.py', 'contra_force_p1_coherent_controls_v2.py',
        'contra_force_p1_coherent_foreign_v1.py', Path(__file__).name]]
    allowed = {'.s', '.inc', '.cfg', '.dep', '.json', '.diff', '.md', '.txt'}
    files = set(tools + receipts)
    files.update(p for p in P.iterdir() if p.is_file() and p.suffix in allowed)
    files.update(p for p in (P / 'joint').iterdir() if p.is_file() and p.suffix in allowed)
    files.update(p for p in (R / 'build/contra-force-p1-kernel-v1').iterdir() if p.is_file() and p.suffix in ['.s', '.inc', '.cfg'])
    for name in ['contra-force-p1-coherent-cart-v1/negative.json',
                 'contra-force-p1-coherent-endpoints-v1/controls.json',
                 'contra-force-p1-restore-arena-api-vectors-v3/controls.json',
                 'contra-force-p1-acquire-retire-controls-v1/controls.json',
                 'contra-force-p1-queue-order-controls-v1/controls.json',
                 'contra-force-p1-coherent-foreign-v1/legacy-main/controls.json']:
        files.add(R / 'build' / name)
    files.update([O / 'README.md', O / 'scope-and-negatives.json', O / 'public-symbol-proof.json'])
    for path in files:
        assert path.is_file(), path
    members = {p.relative_to(R).as_posix(): sha(p) for p in sorted(files)}
    put(O / 'source-members.json', members)
    with zipfile.ZipFile(O / 'source-only.zip', 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in members:
            archive.write(R / name, name)
    with zipfile.ZipFile(O / 'source-only.zip') as archive:
        assert set(archive.namelist()) == set(members)
        for name, digest in members.items():
            assert hashlib.sha256(archive.read(name)).hexdigest() == digest
    externals = [P / 'joint/candidate.nes', P / 'joint/candidate.dbg', P / 'joint/candidate.lbl',
                 P / 'joint/cf-stream.bin', P / 'joint/cf-cookie.bin',
                 R / 'docs/qa/checkpoints/2026-10-31/contra-force-p1-source-experiment-v1/handoff.json']
    handoff = dict(**source_scope, archive_members=len(members), archive_bytes=(O / 'source-only.zip').stat().st_size,
                   complete_source_stage_bindings_verified=len(stage['bindings']),
                   actual_link_recipe=str(P / 'candidate-link.json'),
                   actual_config=str(P / 'joint/candidate.cfg'),
                   bindings={str(p.resolve()): sha(p) for p in files | set(externals) |
                             {O / 'source-only.zip', O / 'source-members.json'}})
    put(O / 'handoff.json', handoff)
    owned = tools + [O / name for name in ['README.md', 'scope-and-negatives.json', 'public-symbol-proof.json',
                                         'source-members.json', 'source-only.zip', 'handoff.json', 'owned-files.json']]
    put(O / 'owned-files.json', dict(files=[p.relative_to(R).as_posix() for p in owned],
                                    stage_or_commit_by_agent=False, immutable_after_creation=True))
    print(json.dumps(dict(path=str(O / 'handoff.json'), sha256=sha(O / 'handoff.json'),
                          members=len(members), archive_bytes=(O / 'source-only.zip').stat().st_size,
                          owned=str(O / 'owned-files.json'), owned_sha256=sha(O / 'owned-files.json'))), flush=True)


if __name__ == '__main__':
    main()
