"""Read only two actual Bill runs; write one compact review and whole-image sheet."""
from pathlib import Path
import csv
import hashlib
import json
import sys

from PIL import Image, ImageDraw

R = Path(__file__).resolve().parents[2]
B = R / 'build'
sys.path.insert(0, str(R / 'tools/audit'))
import final_inventory_compact_capture_v1 as capture

OLD = B / 'verification/bill-inert-pool326-baseline-hard-ready-v1'
NEW = B / 'verification/bill-inert-pool326-hard-ready-v2'
OUT = B / 'bill_inert_pool_native_review.json'
SHEET = B / 'bill_inert_pool_matched_contact.png'
REPORT = R / 'docs/qa/bill-inert-pool-native-2026-10-28.txt'
BASE = '32694243361bb1366f6fd64c054ea2451f86b2517fc020d9c2b5d66bbf07bfa0'
CAND = '44204c9b573a82dd4838df1821afeaad8ffab8b264ebb234f31a8e156434ff5a'


def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for part in iter(lambda: f.read(1024 * 1024), b''):
            h.update(part)
    return h.hexdigest()


def read(p):
    return json.loads(Path(p).read_text())


def rows(p):
    return [{k: int(v) for k, v in q.items()} for q in csv.DictReader(Path(p).open(newline=''))]


def main():
    assert not OUT.exists() and not SHEET.exists() and not REPORT.exists(), 'Preserve this frozen review'
    result = [read(p / 'result.json') for p in (OLD, NEW)]
    launches = [read(p / 'launch.json') for p in (OLD, NEW)]
    ready = [read(p / 'ready.json') for p in (OLD, NEW)]
    for q, launch, expected, passed in zip(result, launches, (BASE, CAND), (True, False)):
        assert q['ROM_sha256'] == expected and q['passed'] is passed
        assert launch['changed_inputs'] == [] and launch['settings_before'] == launch['settings_after']
        assert launch['exit_code'] == (0 if passed else 1)
        assert q['adapter']['full_closed'] and q['adapter']['per_frame_files'] == 0
    assert result[0]['frames'] == 6095 and result[0]['completed_loops'] == 5142
    assert result[1]['frames'] == 1811 and result[1]['reason'] == 'Zero-death 1-1 route'
    assert launches[0]['settings_before'] == launches[1]['settings_before']
    configs = [q['config'] for q in ready]
    differing_config = sorted(k for k in configs[0] if configs[0][k] != configs[1][k])
    assert differing_config == ['ROM_sha256', 'out', 'prefix']
    import current_roster_compact_11_v1 as route
    scripts = [(p / 'run.lua').read_text() for p in (OLD, NEW)]
    assert scripts[0].replace('ROSTER_CONFIG=' + route.lua(configs[0]) + '\n',
                              'ROSTER_CONFIG=' + route.lua(configs[1]) + '\n', 1) == scripts[1]
    traces = [rows(p / 'trace.csv') for p in (OLD, NEW)]
    trace = [{q['frame']: q for q in t} for t in traces]
    first_difference = {}
    for key in ('loops', 'x', 'y', 'state', 'mask', 'engine', 'power', 'camera'):
        first_difference[key] = next(dict(frame=a['frame'], baseline=a[key], candidate=b[key])
                                     for a, b in zip(*traces) if a[key] != b[key])
    assert first_difference['mask']['frame'] == 467
    landing = next(q for q in traces[0] if q['world'] == q['level'] == 0 and 840 <= q['x'] < 870
                   and q['state'] == 0 and q['y'] == 176 and q['engine'] == 8)
    terminal = traces[1][-1]
    assert (landing['frame'], landing['x'], landing['loops'], landing['mask']) == (1838, 850, 1639, 69)
    assert (terminal['frame'], terminal['x'], terminal['y'], terminal['engine'], terminal['mask']) == (1811, 851, 176, 11, 5)
    assert landing['poll'] % 12 < 5 and terminal['poll'] % 12 >= 5
    assert not any(q['state'] == 0 and q['engine'] == 8 and q['x'] >= 840 for q in traces[1])
    policy = R / 'tools/playthroughs/roster_samus_contra.lua'
    text = policy.read_text()
    assert 'b.b=c.poll%12<5' in text and 'and c.grounded and holdA==0' in text
    policy_lines = [dict(line=i, text=line) for i, line in enumerate(text.splitlines(), 1)
                    if 'c.poll%12<5' in line or 'c.grounded and holdA==0' in line]
    selected = [(NEW, 'candidate44204 FALSE', (1771, 1796, 1809, 1811)),
                (OLD, 'matched326 PASS', (1802, 1827, 1838, 1844))]
    sheet = Image.new('RGB', (4 * 264, 2 * 278), '#dddddd')
    draw = ImageDraw.Draw(sheet)
    image_rows = []
    for row, (folder, label, frames) in enumerate(selected):
        wanted = set(frames)
        found = {}
        decoded = 0
        for meta, raw in capture.records(folder / 'captures.nesppuv1'):
            decoded += 1
            frame = meta['stamp']['ppu_frame']
            if meta['kind'] == 1 and frame in wanted:
                found[frame] = (meta, raw)
            if frame >= max(frames):
                break
        assert set(found) == wanted
        for col, frame in enumerate(frames):
            meta, raw = found[frame]
            tr = trace[1 if folder == NEW else 0][frame]
            image = Image.frombytes('RGBA', (256, 240), raw, 'raw', 'BGRA').convert('RGB')
            x, y = col * 264 + 4, row * 278 + 34
            sheet.paste(image, (x, y))
            draw.text((x, row * 278 + 2), f'{label} PPU{frame}', fill='black')
            draw.text((x, row * 278 + 16), f"x{tr['x']} y{tr['y']} M{tr['loops']} mask{tr['mask']}", fill='black')
            image_rows.append(dict(profile=label, PPU=frame, record=meta, trace=tr,
                                   BGRA_sha256=hashlib.sha256(raw).hexdigest(), prefix_records_decoded=decoded))
    sheet.save(SHEET)
    bindings = {str(p): sha(p) for p in [Path(__file__), Path(capture.__file__), Path(route.__file__), policy,
        R / 'tools/playthroughs/roster_samus_contra_nav.lua', B / 'bill_inert_pool.patch',
        B / 'bill_inert_pool_cpu.json', B / 'bill_inert_pool_final.json', B / 'bill_inert_pool_verify_build.json',
        B / 'bill_inert_pool_ordinary.json', R / 'tools/audit/bill_inert_pool_baseline_prepare_v1.py',
        B / 'bill_inert_pool_death_images.json']}
    for folder in (OLD, NEW):
        for name in ('ready.json', 'run.lua', 'command.json', 'launch.json', 'result.json', 'trace.csv',
                     'inputs.csv', 'events.jsonl', 'captures.nesppuv1', 'captures-index.jsonl'):
            p = folder / name
            bindings[str(p)] = sha(p)
    proof = dict(review_completed=True, candidate_native_accepted=False, root_cause_proven=False,
        baseline=result[0], candidate=result[1], launches=launches,
        matched_control=dict(config_differences=differing_config, generated_guard_body_reverse_exact=True,
                             same_adaptive_policy=True, fixed_input_equivalence=False),
        first_endframe_differences=first_difference, baseline_first_local_landing=landing,
        candidate_terminal=terminal, candidate_last_air=trace[1][1809],
        current_source_inference='Earlier source controls preserve complete caller outcomes; native controller consumes poll-based B pulses and landing-gated avoidance. Scheduling and differing legal input responses are demonstrated; no captured contact/kill writer or enemy slot establishes the final causal collision.',
        limits=['EndFrame state is a sample, not collision-writer provenance or exact input-consumption time.',
                'Sampled Goombas are visibly near descending Bill; exact enemy ID/slot/state is not in the route trace.',
                'Candidate death is genuine and remains FALSE. Baseline PASS does not waive it or prove universal game equivalence.',
                'Wall/Main/DMA totals are route outcomes, not FPS or matched-work performance.',
                'Only eight selected unmodified whole images reviewed; neither full stream is visually certified.'],
        proposed_next='A separate Bill-only input successor may anticipate a supported landing near a live short enemy before contact, with a real release-then-press B edge and early braking. It requires actual source movement/collision and context controls; no successor or native retry is silently applied here.',
        source_policy_lines=policy_lines, selected_images=image_rows,
        sheet=dict(path=str(SHEET), sha256=sha(SHEET), actual_whole_frames=8, per_frame_files_created=0,
                   full_stream_scan=False, pixel_edits=False), bindings=bindings)
    OUT.write_text(json.dumps(proof, indent=2) + '\n', newline='\n')
    report = f'''Bill inert-pool native comparison, 2026-10-28

HELD: source-qualified candidate {CAND} failed the unchanged zero-death guard at physical1811/x851/y176/engine11. It is not adopted. Matched current326 baseline {BASE} passed6095wall/5142completedMain/3813DMAs/5208wholePPU and25controlled1-2updates. Both launch receipts have unchanged bindings/settings. Native guard bodies, policy, RAM/hook config, runtime and caps are identical after exactly ROM/output config normalization.

The first sampled policy mask difference is467, long before the failure; power acquisition is also earlier on candidate. These are adaptive runs, not a fixed-input differential. At candidate1809/Main1638 Bill is airborne atx850/y171 with mask5 (Right+Down); at1811 he is dead atx851/y176 with mask5. Matched baseline first lands1838/Main1639/x850/y176 alive with mask69 (Right+Down+B), then1839 uses mask68 (Down+B), crouches/stops and later jumps safely. Original policy pulses B from poll%12<5 and admits its short-enemy prone response only when grounded. Candidate terminal poll1810 has remainder10/Boff; baseline landing poll1837 has remainder1/Bon. This is a concrete scheduling/input-phase distinction, not proof that one final missing B pulse caused death.

Eight exact whole images show two nearby Goombas during descent, the failed candidate contact region and matched baseline landing/prone response. No pit is present at that sampled contact. The route log does not identify the actual enemy contact/kill writer, slot or source collision state; the interruptedPC at the endFrame death sample must not be represented as that writer. Exact collision cause is consequently unproved. Earlier complete source caller/state/flags/RAM/OAM/IRQ qualification remains separately scoped. Candidate source changes only31bytes inbank6; no source behavior omission was demonstrated by this native comparison. Independent review remains required.

No controller/guard/product patch or native launch was performed by this reviewer. A possible narrow successor is Bill-only anticipatory safe landing/real B-edge control around a live short enemy; changing wall-time cadence alone is not asserted sufficient. It needs a separate explicitly reviewed source-context control and readiness, while the existing failure stays unchanged. No full-route speed/FPS or adoption claim follows from these totals.

Exact compact receipt: {OUT}
Receipt SHA256: {sha(OUT)}
Matched sheet (four candidate + four current326 originals): {SHEET}
Sheet SHA256: {sha(SHEET)}
Partial stream decoding stops after selected records; only these eight frames were visually reviewed. The older historical9ea sheet remains separate and is not the matched baseline.

Owned publication files: tools/audit/bill_inert_pool_baseline_prepare_v1.py; tools/audit/bill_inert_pool_native_review_v1.py; this report. Existing source/control files and the literal negative/native outputs remain frozen. ROOT owns publication/adoption/native decisions.
'''
    REPORT.write_text(report, newline='\n')
    print(json.dumps(dict(receipt=str(OUT), receipt_sha256=sha(OUT), report=str(REPORT),
                          report_sha256=sha(REPORT), sheet=str(SHEET), sheet_sha256=sha(SHEET),
                          owned_tools={str(p): sha(p) for p in [Path(__file__), R / 'tools/audit/bill_inert_pool_baseline_prepare_v1.py']})))


if __name__ == '__main__':
    main()
