"""Freeze the isolated WWF recovery and native proxy source, not a host allocation."""
from pathlib import Path
import ast
import hashlib
import importlib.metadata
import json
import platform
import sys
import zipfile

R = Path(__file__).resolve().parents[2]
O = R / 'build/wwf-native-proxy-qualified-v1'
D = R / 'docs/qa/checkpoints/2026-10-31/wwf-native-proxy-source-v1'
L = R / 'build/wwf-native-proxy-lab-v1'
F = R / 'build/wwf-frame-recovery-v2'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def save(p, q):
    Path(p).write_text(json.dumps(q, indent=2) + '\n')


def local_imports(seeds):
    """Pin all statically imported project modules used by the actual CPU fixtures."""
    seen, todo = set(), list(seeds)
    roots = [R / 'tools/audit', R / 'tools']
    while todo:
        p = todo.pop().resolve()
        if p in seen:
            continue
        seen.add(p)
        for node in ast.walk(ast.parse(p.read_text(encoding='utf-8-sig'))):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name.split('.')[0] for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module.split('.')[0]]
            for name in names:
                for root in roots:
                    q = root / (name + '.py')
                    if q.is_file() and q.resolve() not in seen:
                        todo.append(q)
                        break
    return seen


def main():
    assert not O.exists() and not D.exists()
    O.mkdir()
    D.mkdir(parents=True)
    builds = [F / 'build-proof.json', L / 'build-proof.json']
    tests = [R / 'build' / name / 'controls.json' for name in [
        'wwf-frame-recovery-controls-v1',
        'wwf-isolated-host-phase-controls-v7',
        'wwf-native-proxy-controls-v3',
    ]]
    reports = [json.loads(p.read_text()) for p in builds + tests]
    assert all(q.get('passed', q.get('source', False)) for q in reports)
    external = set()
    for q in reports:
        for path, expected in q['bindings'].items():
            assert sha(path) == expected, path
            external.add(Path(path).resolve())
    prior = R / 'docs/qa/checkpoints/2026-10-31/wwf-selected-host-lab-v1/handoff.json'
    current = R / 'docs/qa/checkpoints/2026-10-31/contra-force-jump-contact-source-v1/handoff.json'
    assert sha(prior) == '1f472a5c7ad79103454b5cd08c116ff29c039588f57c2df92197240833e1c31d'
    assert sha(current) == '072c8e8855ff60b0524d9f62a2e7e2e3e9c762660f3e9bff0c96031f8ba86359'
    proof = reports[1]
    labels = proof['labels']
    assert proof['host_candidate'] == 'a12661c1ddad2e15a8ce0589e86b5510703fd390e6346a982b14a6be0b742e3c'
    assert (L / 'vm.bin').read_bytes() == (R / 'build/wwf-c2-symbol-relocation-v3/vm.bin').read_bytes()
    ranges = {
        'selected_original_state': [0xc000, 0xc800],
        'host_context': [0xc800, 0xc810],
        'proxy_context': [0xc820, 0xc860],
        'descriptors': [0xc8c0, 0xcab2],
        'recovery_and_intro': [0xcc00, 0xcf8b],
        'native_proxy_core': [0xd000, 0xd2c3],
        'scoped_pointer_wrappers': [0xd400, 0xd885],
        'host_code_data': [0xd900, 0xdba2],
        'selected_contact': [0xdc00, 0xdd8f],
        'native_proxy_tail': [0xdd90, 0xdfc2],
        'phase_scratch': [0xdfd0, 0xdfd4],
    }
    assert sum(hi - lo for lo, hi in ranges.values()) == 7036
    occupancy = []
    for raw, name in [(1, None), (2, 'c2.bin'), (3, 'vm.bin')]:
        image = (L / name).read_bytes() if name else None
        assert image is None or len(image) == 8192
        for index in range(8):
            row = dict(raw_selected_bank=raw, page_in_bank=index,
                       image_offset=index * 1024, bytes=1024)
            if image is None:
                row.update(status='UNBUILT_A1_MUSIC_NO_SYNTHETIC_FILL',
                           source_bytes=None, classification=None)
            else:
                block = image[index * 1024:(index + 1) * 1024]
                kind = ('zero' if block == bytes(1024) else
                        'FF' if block == bytes([255]) * 1024 else
                        'uniform_other' if len(set(block)) == 1 else 'nonuniform')
                row.update(status='ACTUAL_ASSEMBLED_IMAGE', classification=kind,
                           source_image=str(L / name), sha256=hashlib.sha256(block).hexdigest(),
                           zero_bytes=block.count(0), FF_bytes=block.count(255),
                           distinct_values=len(set(block)))
            occupancy.append(row)
    save(O / 'selected-template-occupancy.json', dict(
        source=True, no_new_cart=True, complete_24KB_template_built=False,
        actual_image_bytes=16384, unbuilt_A1_bytes=8192,
        note='Uniform selected state is still required runtime RAM, not released capacity. A sparse loader is not implemented or granted.',
        C2_emitted_ranges=ranges, C2_emitted_bytes=7036,
        A3_VM_emitted_bytes=7726, pages=occupancy))
    api = dict(
        source=True, isolated_CPU_lab=True, no_host_allocation=True,
        native_host=False, installed=False, readiness_unchanged=True,
        prior_source_handoff=dict(path=str(prior), sha256=sha(prior)),
        current_host_reference=dict(path=str(current), sha256=sha(current),
                                    candidate=proof['host_candidate']),
        actual_compiled_entries={n: labels[n] for n in [
            'WfHostCold', 'WfHostFrame', 'WfFrameRecovery',
            'WfFrameRecoveryCore', 'WfIntroFillCore', 'WfProxyContext',
            'WfProxyReset', 'WfHostPoint', 'WfProxyNoteReuse',
            'WfProxySnapshot', 'WfProxyCollect', 'WfProxyCommit',
            'WfHostImport', 'WfHostExport',
        ]},
        actual_current_native_imports=proof['host_imports'],
        public_proxy_ABI=proof['contracts']['public'],
        epoch_precondition=(
            'Before using this proxy in a real host, every native enemy constructor, '
            'erase, replacement and slot-reuse path must call WfProxyNoteReuse for '
            'the affected slot before new identity publication. The compiled worker '
            'and identical-tuple reuse test do not establish physical hook coverage. '
            'No such hooks are installed by this packet.'),
        call_order=[
            'Apply preceding actual native terrain/platform clamps, then WfHostImport.',
            'For an eligible ordinary enemy, WfProxySnapshot marshals the current native actor into source actor1.',
            'Execute the selected actor source update in the genuine phase order; recovery/grapple CF14 remains real source.',
            'WfProxyCollect preserves raw source health/action transitions; WfProxyCommit rechecks tuple and epoch before ShellOrBlockDefeat.',
            'WfHostExport applies source X/jump-offset deltas, then the future actual native terrain/platform resolution sequence must run.',
        ],
        coordinates={
            '2E/2F': 'Original ring depth/ground plane; never converted into platformer jump Y.',
            '30/31': 'Signed source jump/body displacement, exported as a delta from imported native Y.',
            'native_fall': 'Only unsupported source offset0 calls genuine ImposeGravitySprObj; native falling/support remain distinct.',
            'X': 'Native 16-bit world page/X imported, source origin rebased128, source delta exported with real page carry.',
            '42/43': 'Descriptor-byte9 body-anchor heights, not health. Earlier immutable final_health wording is corrected.',
            '79/7A': 'Raw original health/endurance/damage operations, including recovery and knockdown thresholds, retained.',
        },
        source_phase=(
            'Original76=$20 intro countdown and B14D health fill occur in original order; '
            'selector/VM waits for countdown0. Actor0 VM executes on original71 even parity, '
            'CF14 recovery/grapple follows, phase71 advances modulo6 while unpaused, '
            'and8D video count advances on every accepted frame. No physical NMI cadence hook.'),
        footprint=dict(A3_VM_code_dispatch_scripts=7726, C2_emitted_code_data_state_context=7036,
                       C2_ranges=ranges, native_proxy_code=1269, proxy_context=64,
                       new_global_RAM=0, new_ZP=0, borrowed_native_R0_R7=list(range(3, 11))),
        resource_constraints=[
            'All addresses are isolated laboratory resources, not granted physical host allocations.',
            'C2 has7036 emitted bytes before future per-wrestler rendering metadata and native music state. Full-family metadata is not asserted to fit.',
            'The lab host/proxy contexts need source relocation before any conflicting music-state layout; no overlap is accepted.',
            'Menu mask/helper space is root-owned and jointly funded; this packet allocates none.',
        ],
        dynamic_VM_handlers=dict(observed=60, total=90),
        remaining_semantics=[
            *proof['limits'],
            'RingClamp/RingBounds/AI and queued audio boundaries still use declared donor oracles in the VM lab.',
            'Full proxy/Main/terrain/platform sequencing, physical enemy epoch hooks, authenticated cache loader and retirement, rendering/audio, common ISR and native WWF controller route remain uninstalled.',
            'The source-hit fixture enters authored E91A..E92D directly; it does not establish natural controller eligibility for every attack.',
            'No new real MMC5 ISR cut suite has been run on the proxy instructions; existing proxy full-flags/live-stack/map results do not imply it.',
        ],
    )
    save(O / 'integration-api.json', api)
    save(O / 'verification-summary.json', dict(
        source=True, CPU='Project NesMPU: binary ADC/SBC with D retained',
        recovery_pairs=8768, genuine_cold_cases=24, accepted_frame_pairs=4608,
        native_cold_parser_GameLoop_NMI_pairs=167, parsed_world_points=20,
        native_point_ABI_cases=33536, stale_actor_rejections=640,
        genuine_source_hit_native_defeat_pairs=128, source_coordinate_pairs=3072,
        genuine_native_fall_pairs=256,
        no_physical_epoch_hooks=True, no_native_launch=True,
        results={str(p.relative_to(R)): sha(p) for p in tests},
    ))
    note = '''Isolated WWF genuine recovery/grapple and native proxy source successor.

This packet freezes compiled source and finite CPU controls. It does not change a cartridge, install hooks, allocate physical resources, or unlock a wrestler. The exact current host reference is a12661c1ddad2e15a8ce0589e86b5510703fd390e6346a982b14a6be0b742e3c. All host imports are derived from that actual DBG, with fixed native callback banks explicitly pinned.

The CE2A..D0B2 closure containing CF14 is translated from real native opcodes, alongside B14D intro health fill and the original76 countdown. Recovery/intro plus public scratch scope emit907B. The original VM code/scripts remain byte-identical. Six-character source recovery/grapple threshold controls pass8768 pairs;24 genuine cold constructors and4608 accepted source-frame pairs retain original order and returned CPU/source-state contracts. No prerecorded timeline replaces the VM.

The native proxy is1269B plus64B selected context. Ring depth2E/2F stays separate from signed jump offset30/31. Source X and jump deltas are imported/exported around actual native position, page carry, clamps and falling. Actual native BlockBufferAddr/MTileAttribute, ShellOrBlockDefeat and ImposeGravitySprObj execute in the CPU fixture. Unsupported fall uses native gravity; source jump arithmetic is not rewritten.

IMPORTANT EPOCH PRECONDITION: real CheckpointEnemyID/EraseEnemyObject and every other constructor/replacement/reuse path must notify WfProxyNoteReuse before slot identity publication. No physical notification hooks are installed. Snapshot/commit compares all nine native actor fields plus the selected epoch, but identical-tuple slot reuse is safe only when that notification contract is actually covered. Ordinary enemies alone are admitted; boss/powerup/frenzy/Podoboo behavior is not generalized.

The exact host fixture runs167 real native parser GameLoop/NMI pairs before explicitly injecting executable lab images into private RAM3/C2. This is API-arena injection, not a WWF loader, Ready, cookie or natural-entry proof. It then passes33536 point-query ABI cases,640 stale/reused actor rejections,128 genuine source-hit-to-native-defeat comparisons,3072 source-motion/page-carry pairs and256 exact native falling comparisons. Source health200->183 is produced by authored E91A..E92D; this action-entry fixture does not establish naturally eligible controller attacks. The source/native return packets and ordered application writes are compared. All public proxy AXYP except resultC, scopedR0..7, live upper stack and raw maps are retained. No new common/MMC5 interrupt-cut claim is made for proxy instructions.

Actual lab footprint: A3 VM/code/scripts7726B; C2 emitted code/data/state/context7036B, excluding linker holes. Future full-family rendering metadata/music does not already fit by assertion. No shared PRG/CHR/RAM or menu-helper grant is inferred. Root jointly owns menu-mask funding. Original RingClamp/RingBounds/AI and sound queues still use declared donor oracles; physical Main/terrain/platform placement, epoch coverage, native rendering/audio, cache lifecycle and common interrupts remain integration work.

CPU model is project NesMPU, retaining D while ADC/SBC stays binary. Prior stock-py65 equality is a narrower archived result. The earlier body-anchor fields42/43 are explicitly distinguished from original health/endurance79/7A. Actual link logs retain deliberate absolute imports of native ZP position fields; these address-size warnings do not change the referenced values or tested ABI.

Retained negatives include a receipt-only limits KeyError after phase-v6 cases and a stale-guard fixture that repeatedly damaged one target to zero, then incorrectly demanded another health decline. The successor clones genuine cold+intro state per independent case and does not seed HP/Ready. No failed source artifact is overwritten.

Replay source-only ZIP contains actual assembled source, compiler/link recipes with validated private outputs, control/dependency modules, reports and negatives. Binary products, donor ROM, host ROM, parent ZIPs and capture forests are externally hash-pinned rather than duplicated. Builders have immutable output names: to replay, first create a new source child and rebase ALL compiler/config output paths through private_build_outputs_v1 validation. Never execute an inherited recipe against its frozen output directory.
'''
    (O / 'README.txt').write_text(note)
    own_names = [
        'prepare_wwf_frame_recovery_v1', 'prepare_wwf_frame_recovery_v2',
        'prepare_wwf_native_proxy_lab_v1', 'wwf_frame_recovery_controls_v1',
        'wwf_isolated_host_phase_controls_v6', 'wwf_isolated_host_phase_controls_v7',
        'wwf_native_proxy_controls_v1', 'wwf_native_proxy_controls_v2', 'wwf_native_proxy_controls_v3',
    ]
    own_tools = {R / 'tools/audit' / (name + '.py') for name in own_names}
    tools = local_imports(own_tools)
    files = tools | {Path(__file__), *builds, *tests, prior, current,
                     R / 'tools/reference/wwf_native_proxy_lab_v1.s',
                     O / 'README.txt', O / 'integration-api.json', O / 'verification-summary.json',
                     O / 'selected-template-occupancy.json'}
    for root in [L, F, R / 'build/wwf-c2-symbol-relocation-v3',
                 R / 'build/wwf-selected-contact-v2']:
        files |= {p for p in root.iterdir() if p.is_file() and
                  p.suffix in {'.s', '.cfg', '.json'}}
    for name in ['wwf-isolated-host-phase-controls-v6', 'wwf-isolated-host-phase-controls-v7',
                 'wwf-native-proxy-controls-v1', 'wwf-native-proxy-controls-v2']:
        root = R / 'build' / name
        files |= {p for p in root.rglob('*') if p.is_file() and p.suffix in {'.json', '.s', '.cfg'}}
    # Keep actual linked binary artifacts/labels externally bound, not archived copies.
    for p in external:
        if p.is_relative_to(R) and p.suffix in {'.py', '.s', '.cfg', '.json'}:
            files.add(p)
    for p in [R / 'tools/Windows/cc65/bin/ca65.exe', R / 'tools/Windows/cc65/bin/ld65.exe']:
        external.add(p)
    for p in [L / 'lab.map', F / 'lab.map']:
        external.add(p)
    save(O / 'toolchain.json', dict(python=platform.python_version(),
                                  py65=importlib.metadata.version('py65'),
                                  executable=sys.executable,
                                  compiler_sha256=sha(R / 'tools/Windows/cc65/bin/ca65.exe'),
                                  linker_sha256=sha(R / 'tools/Windows/cc65/bin/ld65.exe')))
    files.add(O / 'toolchain.json')
    files = {p.resolve() for p in files}
    bindings = {str(p): sha(p) for p in sorted(files | external)}
    members = {p for p in files if p.suffix in {'.py', '.s', '.cfg', '.json', '.txt'}}
    assert len(members) < 220
    assert sum(p.stat().st_size for p in members) < 5000000
    with zipfile.ZipFile(O / 'source-only.zip', 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in sorted(members):
            z.write(p, p.relative_to(R).as_posix())
    with zipfile.ZipFile(O / 'source-only.zip') as z:
        assert len(z.namelist()) == len(members)
        for p in members:
            assert hashlib.sha256(z.read(p.relative_to(R).as_posix())).hexdigest() == sha(p)
    for p, expected in bindings.items():
        assert sha(p) == expected, p
    handoff = dict(
        source=True, isolated_CPU_lab=True, no_host_allocation=True,
        native_host=False, installed=False, readiness_unchanged=True,
        status='WWF_RECOVERY_NATIVE_PROXY_COMPILED_CPU_PASS_NO_PHYSICAL_HOOKS',
        source_build=sha(L / 'build-proof.json'), host_candidate=proof['host_candidate'],
        VM_SHA256=sha(L / 'vm.bin'), C2_SHA256=sha(L / 'c2.bin'),
        bindings=bindings,
        members={p.relative_to(R).as_posix(): sha(p) for p in sorted(members)},
        archive_sha256=sha(O / 'source-only.zip'),
        archive_bytes=(O / 'source-only.zip').stat().st_size,
        footprint=api['footprint'], verification=sha(O / 'verification-summary.json'),
        epoch_precondition=api['epoch_precondition'], limits=api['remaining_semantics'],
    )
    save(O / 'handoff.json', handoff)
    for name in ['handoff.json', 'source-only.zip', 'integration-api.json',
                 'verification-summary.json', 'README.txt', 'toolchain.json',
                 'selected-template-occupancy.json']:
        (D / name).write_bytes((O / name).read_bytes())
    owned = own_tools | {Path(__file__), R / 'tools/reference/wwf_native_proxy_lab_v1.s'}
    (D / 'owned-files.txt').write_text('\n'.join(
        p.relative_to(R).as_posix() for p in sorted(owned)) + '\n' + D.relative_to(R).as_posix() + '/\n')
    print(json.dumps(dict(passed=True, handoff=str(D / 'handoff.json'),
                          SHA256=sha(D / 'handoff.json'), bindings=len(bindings),
                          members=len(members), archive_bytes=handoff['archive_bytes'])))


if __name__ == '__main__':
    main()
