"""Freeze the finite current3cee Octopus/Sophia read-only attribution packet."""
from pathlib import Path
import argparse, hashlib, json, shutil, sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/audit'))
from check_tmnt_render_oa import load, address, location

D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
SHA = '3cee18caa732b2e85e3bdb00faf719223324f9bf24e72dd30c56be355da33b99'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for data in iter(lambda: f.read(1048576), b''):
            h.update(data)
    return h.hexdigest()


def get(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def put(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--packet', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    ready = get(args.packet / 'readiness.json')
    execution = get(args.packet / 'execution.json')
    analysis = args.packet / 'analysis-v2'
    assert execution['passed'] and execution['worker_released']
    assert get(analysis / 'proof.json')['passed']
    assert get(args.packet / 'analysis-v1/failure.json')['passed'] is False
    bindings = dict(ready['bindings'])
    for path, digest in get(analysis / 'bindings.json').items():
        assert path not in bindings or bindings[path] == digest
        bindings[path] = digest
    assert all(sha(path) == digest for path, digest in bindings.items())
    bundle = load(Path(ready['rom']))
    assert sha(ready['rom']) == SHA
    source = Path(ready['rom']).parent / 'source/src'
    owners = []
    for file, line, symbol, meaning in [
        ('metasprite_engine.s', 303, 'DrawAllMetasprites', 'Weapons and native actor sprites precede the logical body reservation; body is written into the reserved span later.'),
        ('metasprite_engine.s', 400, 'RosterProjectileOamReady', 'The actual logical body start follows production projectile/native actor output.'),
        ('metasprite_engine.s', 1098, 'MetaspriteRenderLoop', 'Compiled records emit parts in reverse source order into the rotated physical OAM ring.'),
        ('meta_knight.s', 5, 'KbOamPriority', 'Production rotates the whole used OAM ring. The body-layer pivot clamp is selected only for Meta Knight.'),
        ('parodius_render.s', 22, 'PnRecordPointer', 'Octopus body and other native Parodius actors select original immutable record pointers.'),
        ('parodius_render.s', 59, 'PnPublish', 'Body/weapon/pickup physical CHR pages are published with completed actor drawing.'),
        ('parodius_render.s', 127, 'PnDraw', 'Production iterates native Parodius actors before the player body reservation.')]:
        path = source / file
        # Exact frozen source and linked label bytes, rather than a new source build.
        at = location(bundle, symbol)
        owners.append(dict(source_path=str(path), source_sha256=sha(path), source_line=line,
                           symbol=symbol, CPU_address=address(bundle, symbol),
                           physical_bank=(at - 16) // 8192,
                           first16_ROM_bytes=bundle['raw'][at:at + 16].hex(), observation=meaning))
        bindings[str(path)] = sha(path)
    at = location(bundle, 'PlayerOutlineCharacters')
    flags = bundle['raw'][at:at + 13]
    assert flags == bytes([0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0])
    source_scope = dict(passed=True, ROM_sha256=SHA, owners=owners,
                        compiled_outline_table=flags.hex(), Sophia_table_index11=flags[11],
                        Octopus_outline_bypass='Compiled X5PlayerOutlineFlag bypasses legacy outline processing for IDs >=13.',
                        flag_scope='GuestHurtVisible=0 is an unused shared field for these paths, not proof of a hidden body. Relevant actual body tuples and native hurt/invulnerability flags are recorded.',
                        interpretation='No first bad CPU/CHR/OAM write was found. The observed visibility loss occurs when valid opaque body parts are excluded by the physical first-eight scanline admission. The allocation/rotation owners are an actionable source lead, not a qualified repair.',
                        future_boundary='Any repair must retain source art/pose colors, projectile and enemy admission fairness, completed draw cadence and real hardware sprite limits. Old unguarded body-reorder rejection remains negative; no bytes are proposed or changed here.')
    put(args.output / 'source-owner.json', source_scope)
    selected = []
    for case in ['octopus', 'sophia']:
        rows = get(analysis / (case + '-attribution.json'))['findings']
        reduced = []
        for row in rows:
            assert row['flags_at_body']['CrossoverBehaviorVersion'] == 0
            assert row['flags_at_body']['GuestHurtTicks'] == row['flags_at_body']['GuestInvulTicks'] == 0
            if case == 'octopus':
                assert row['flags_at_body']['VvHurt'] == 0 and row['flags_at_body']['PnDrawFlags'] & 1
            brief = {k: v for k, v in row.items() if k != 'opaque_exclusions'}
            brief['representative_opaque_exclusions'] = row['opaque_exclusions'][:3]
            reduced.append(brief)
        selected.append(dict(case=case, mode='Easy', numeric_mode=0, epochs=reduced))
        shutil.copyfile(analysis / (case + '-actual-PPU.png'), args.output / (case + '-actual-PPU.png'))
    put(args.output / 'selected-epochs.json', selected)
    put(args.output / 'agent-visual-review.json', dict(
        agent_visual_review=True, selected_actual_whole_PPU_frames=19,
        exact_source_paths=[str(analysis / (case + '-actual-PPU.png')) for case in ['octopus', 'sophia']],
        findings=['Actual partial bodies are visible in the whole PPU frames, with both wrapped and nonwrapped body spans affected.',
                  'Octopus1423/1907/2150/2151/3360 have marked body-color loss. Sophia1523 and3064..3066 show large body loss;3064..3066 share one unchanged completed DMA.',
                  'Comparison controls include intact Sophia948/2037/2551/3063/3067 and Octopus2876. This is a selected-frame inspection, not an exhaustive visual verdict.',
                  'No obvious displaced background blocks or new CHR corruption are seen in these19 frames. Parodius HUD lettering remains tiny and dense.'],
        limits='Agent image inspection, not a human review. Full pixel visibility, every pose/item, audio fidelity, prior natural Buffer2 coverage and all flicker remain open.'))
    # Retain every failed offline artifact; no negative is replaced by the v2 model.
    for folder in [args.packet / 'analysis-v1', analysis]:
        bindings.update({str(p): sha(p) for p in folder.iterdir() if p.is_file()})
    for file in ['readiness.json', 'execution.json', 'launch.json']:
        bindings[str(args.packet / file)] = sha(args.packet / file)
    for case in ready['cases']:
        native = Path(case['output'])
        proof = get(native / 'proof.json')
        archive = proof['raw_lossless_archive']
        assert sha(archive['path']) == archive['sha256']
        bindings[archive['path']] = archive['sha256']
        for file in ['proof.json', 'visibility-frames.jsonl', 'visibility-bus.jsonl',
                     'visibility-publications.jsonl', 'added-observer-result.json']:
            bindings[str(native / file)] = sha(native / file)
    for path in [D / 'root-current3cee-vehicle-integrity-v1/proof.json',
                 D / 'root-current37-render-observations-v1/observations.json',
                 ROOT / 'tools/audit/current3cee_vehicle_visibility_report_v1.py']:
        bindings[str(path)] = sha(path)
    report = '''Current3cee Octopus/Sophia body visibility attribution - 2026-10-26

Two explicitly granted read-only exact-input native replays completed PASS. The one sequential Mesen worker is released; no further native grant remains. ROM3cee18caa732b2e85e3bdb00faf719223324f9bf24e72dd30c56be355da33b99, original controller/capture layers and hardware eight-sprite limit are unchanged. No production, source, settings, controller, audio or emulated gameplay state was changed.

Octopus Easy0:4,801 actual saved PPU frames; Sophia Easy0:5,088. Each probe's full raw stream hash/byte count, frame-index and twelve original gameplay/input/render/CHR/audio/scroll CSV files exactly match its passing original direct route. Each added observer has19 static memory callbacks plus2 static frame callbacks; no added runtime registration and no emulated write. Each logs7,242 ordered actual start/end frame rows for PPU480..4100. ROOT independently checked all1,249 readiness bindings, raw/index/log identities, all2,454 Octopus/1,388 Sophia completed DMA snapshots and all11/10 dumped physical CHR pages against the frozen ROM. Complete DMA means256 writes and exact256-byte source/hardware equality, not the4014 write callback alone.

The bounded offline attribution uses19 actual epochs:9 Octopus and10 Sophia. Every selected body record matches immutable compiled ROM bytes, its reversed/attributed source-part projection matches physical hardware OAM, the full source/hardware DMA is complete before actual startFrame, and OAM/CHR/palette/PPUCTRL are stable through the measured visible interval. The model decodes actual8x16 sprite bitplanes from the observed physical CHR pages, applies actual flips/palettes and selects the first eight Y-intersecting physical OAM slots, including transparent parts that still consume admission.8,832 calibrated admitted front-sprite pixels exactly match actual captured RGB.

Octopus has893 eligible opaque body-pixel exclusions in these selected epochs; all893 have actual RGB different from the calibrated source body color. Sophia has809 exclusions:802 source-body-color absences and7 equal-RGB ambiguous pixels, retained as ambiguous. These are pixel placements, with repeated displayed epochs counted separately, not unique images/parts. No background tile reconstruction is claimed. The native body/hurt flags show actual body drawing, VvHurt0 for Octopus and zero GuestHurtTicks/GuestInvulTicks for all19; unused GuestHurtVisible0 is not treated as an intentional-hidden-body signal.

Concrete examples: Octopus actual PPU1423 publication606/DMA1043 has body slots58..63,0 and45 first-eight body candidate pixels versus218 in the unlimited-sprite candidate. At x131/y105, physical CHR page834 byte866 low0/high4 bit2 is opaque white, yet body slot61 is outside actual first-eight slots52,53,54,55,56,57,59,60; actual RGB is sky-colored. Octopus2150 also loses body pixels without wrapping: slots55..61,36/202 candidate pixels. Sophia3064..3066 share publication959/DMA1434, slots59..63,0 and137/311 candidate pixels. At3065 x115/y78 the physical page150 byte631 low255/high255 bit7 is opaque black; slot63 is excluded behind first-eight slots0,50,51,52,53,54,55,61 and the actual pixel is sky-colored. All exact source bytes, actual timestamps, palettes, row slots and pixel witnesses are saved in the attribution JSON.

This identifies real eight-sprite admission/priority visibility loss. It does not identify a corrupt CHR/record/OAM write. Production DrawAllMetasprites emits weapons/native actors first, reserves the logical body span afterwards and writes the body later. KbOamPriority rotates the whole used physical ring; its special body-layer pivot clamp is selected only for Meta Knight. PnDraw can contribute native actor records before Octopus's reservation; Sophia's acquired shots are likewise present in the actual publication. Both wrapped and nonwrapped spans can lose substantial opaque body pixels. A future priority/body solution must preserve enemies/projectiles, exact colors/shapes and draw cadence; no source fix is proposed or qualified here. The previously rejected unguarded body reorder remains rejected.

Offline analysis-v1 remains FALSE and immutable: it incorrectly substituted dominant sky RGB for every no-sprite coordinate; Sophia1523 overlaps a normal green bush. Separate analysis-v2 retains every compiled-body/opaque/first-eight/admitted-front-pixel assertion, makes no background reconstruction, records all exclusions and distinguishes actual body-color absence from equal-RGB ambiguity. This model correction is separate from the two unchanged native passes.

Agent inspection covered all19 selected whole PPU frames in two sheets. Partial bodies are apparent; no obvious displaced/green-block corruption is seen in this sample. The HUD remains tiny/dense. The original route guards and new read-only publication observations are retained; this packet does not introduce a full five-SMC/NMI/stack/IRQ timing oracle. No all-frame/source-fidelity, every-item, audio-fidelity, flicker-fix, timing-improvement or full-roster completion claim follows. ROOT's existing render observations are descriptive differing-route counts, not FPS or causal comparisons. Original areaFALSE/natural Buffer2 overlap and earlier Roll/Sophia crowded-visibility limits remain unchanged.

Stable commands already consumed the exact two-run grant:
python -B tools/audit/current3cee_vehicle_visibility_v1.py run --packet "C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py/current3cee-vehicle-visibility-v1" --native-grant
This command is intentionally one-shot and cannot be rerun against that packet. Offline analysis is reproducible into a new directory:
python -B tools/audit/current3cee_vehicle_visibility_analysis_v2.py --packet "C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py/current3cee-vehicle-visibility-v1" --output <fresh-external-directory>

Exact parent/current ROM and all tools, source-owner files, native receipts, raw archives, selected frames, both offline analysis versions and ROOT independent receipts are bound in bindings.json. No installed build mutation occurred.
'''
    (args.output / 'report.txt').write_text(report, encoding='utf-8')
    for file in args.output.iterdir():
        if file.is_file():
            bindings[str(file)] = sha(file)
    put(args.output / 'bindings.json', bindings)
    put(args.output / 'proof.json', dict(
        passed=True, bounded_attribution_only=True, ROM_sha256=SHA,
        no_game_or_controller_changes=True, native_workers_released=True,
        native_cases=execution['completed'], actual_modes={'octopus': 0, 'sophia': 0},
        saved_direct_PPU_frames=9889, selected_attribution_epochs=19,
        original_native_guards_and_direct_streams_exact=True,
        body_visibility_defect_attributed=True, visibility_defect_fixed=False,
        opaque_first8_exclusions=1702, source_body_color_absent_pixels=1695,
        equal_RGB_ambiguous_pixels=7, admitted_front_sprite_RGB_checks=8832,
        preserved_offline_v1_passed=False,
        execution_sha256=sha(args.packet / 'execution.json'),
        offline_v2_sha256=sha(analysis / 'proof.json'),
        root_independent_integrity_sha256=sha(D / 'root-current3cee-vehicle-integrity-v1/proof.json'),
        report_sha256=sha(args.output / 'report.txt'),
        bindings=len(bindings), bindings_sha256=sha(args.output / 'bindings.json'),
        limits='No native retry/fix, reconstructed background, every-frame/item/audio fidelity, general no-flicker or performance verdict. Existing areaFALSE and naturalBuffer2 limitation remain open.'))
    assert all(sha(path) == digest for path, digest in bindings.items())
    print(json.dumps(dict(passed=True, bindings=len(bindings),
                          proof_sha256=sha(args.output / 'proof.json'),
                          manifest_sha256=sha(args.output / 'bindings.json'),
                          report_sha256=sha(args.output / 'report.txt'), native_workers_released=True), indent=2))


if __name__ == '__main__':
    main()
