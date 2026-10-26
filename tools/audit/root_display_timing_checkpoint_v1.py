"""Freeze the actual failed integration and successful three-byte timing repair."""
from pathlib import Path
import csv
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
OUT = ROOT / 'docs/qa/checkpoints/2026-10-26/display-timing-integration'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not OUT.exists()
    OUT.mkdir(parents=True)
    catalog = {}

    def copy(p, name):
        p = Path(p)
        q = OUT / name
        q.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, q)
        assert sha(p) == sha(q)
        catalog[name] = dict(source=str(p), sha256=sha(q))

    base = D / 'cv3-remaining-legacy-wrapper-v2/native-hard1F-v3'
    old = D / 'root-combined4285-hard1f-v2'
    new = D / 'root-padding6c69-hard1f-v1'
    padding = D / 'world-firebar-padding-v2'
    packets = {}
    for name, p, count, expected in [('held4285', old, 166, False), ('repair6c69', new, 167, True)]:
        ready = json.loads((p / 'readiness-source-only.json').read_text())
        for f, h in ready['all_frozen_bindings'].items():
            assert sha(f) == h, f
        launch = json.loads((p / 'native/proof.json').read_text())
        verdict = json.loads((p / 'native/comparison/proof.json').read_text())
        game = json.loads((p / 'fixture/proof.json').read_text())
        assert launch['native_guard_passed'] and game['passed']
        assert verdict['passed'] is expected
        assert game['updates'] == 240 and game['draws'] == count
        assert verdict['original_source_frames'] == verdict['complete_mixer_flushes'] == 280
        assert verdict['legacy1F_unchanged_complete_hardware_control']['hardware_stores'] == 850
        assert verdict['legacy1F_unchanged_complete_hardware_control']['equal']
        for f in ['readiness-source-only.json', 'native/proof.json', 'native/comparison/proof.json',
                  'fixture/proof.json', 'fixture/preparation.json', 'startup/proof.json', 'observer/proof.json']:
            copy(p / f, name + '/' + f)
        records = [json.loads(s) for s in (p / 'fixture/dma-bus.jsonl').read_text().splitlines()]
        done = [q for q in records if q['kind'] == 'DMA-complete']
        assert len(done) == count
        baseline = [json.loads(s) for s in (base / 'dma-bus.jsonl').read_text().splitlines()]
        baseline = [q for q in baseline if q['kind'] == 'DMA-complete']
        assert len(baseline) == 167
        for actual, reference in zip(done, baseline):
            assert actual['source_exact'] and actual['data_writes'] == 256
            assert actual['hardware_hex'] == reference['hardware_hex']
            assert actual['stamp']['frame'] == reference['stamp']['frame']
        timing = list(csv.DictReader((p / 'fixture/deadline-timing.csv').open()))
        entry = next(q for q in timing if q['kind'] == 'NMI-entry' and q['ppuFrame'] == '717')
        publication = [q for q in timing if q['kind'] == 'publication-write' and q['ppuFrame'] == '717']
        packets[name] = dict(ROM_sha256=ready['candidate_ROM_sha256'], strict_verdict=expected,
                             native_guard_passed=True, actual_complete_DMA=count,
                             matched_complete_hardware_pages_and_physical_epochs=count,
                             source_ticks=280, mixer_flushes=280, physical_legacy_stores=850,
                             actual_PPU717_NMI_entry=entry, actual_PPU717_publications=publication,
                             final_RGB_sha256=sha(p / 'fixture/case-end.argb'),
                             final_RGB_equals_installed2cb=sha(p / 'fixture/case-end.argb') == sha(base / 'case-end.argb'))
    assert not packets['held4285']['final_RGB_equals_installed2cb']
    assert packets['repair6c69']['final_RGB_equals_installed2cb']
    for f in ['proof.json', 'cpu-v1/proof.json', 'review.patch', 'source/src/metasprite_engine.s', 'ready-v1/receipt.json']:
        copy(padding / f, 'padding-source/' + f)
    for f in ['startup.log', 'failed-preparer-v1.py.txt', 'failure-classification.json']:
        copy(D / 'root-combined4285-hard1f-v1' / f, 'retained-preparation-failure/' + f)
    copy(old / 'comparison-v3-negative/proof.json', 'comparator-false-exit-control.json')
    for n in ['root_combined4285_hard1f_prepare_v2.py', 'root_padding6c69_hard1f_prepare_v1.py',
              'cv3_remaining_sfx_lifecycle_verify_v3.py', 'world_firebar_padding_prepare_v2.py',
              'world_firebar_padding_cpu_v1.py']:
        copy(ROOT / 'tools/audit' / n, 'frozen-tools/' + n)
    report = dict(packets=packets, production_adopted=False, goal_complete=False,
                  original_failed_integration_preserved=True, no_native_retries=True,
                  source_changes='Exactly EA EA EA -> JMP genuine Done at bank4:A271; remaining17NOPs/39B span/old PCs retained.',
                  CPU_cases=274, IRQ_injections=111, exact_cycles_saved_per_call=37,
                  verifier_erratum='v2 writes passed:false but exits0 for a cadence-only failure. The original receipt is unchanged; v3 preserves its comparison and exits1, verified against the actual held4285 recording. Shell exit0 is not acceptance.',
                  limits='One strict staged Hard1F240 control per candidate. No global60Hz, waveform, full-roster1-1/item/campaign, new-menu-on6c or natural pending-HUD/Buffer2-overlap certification.',
                  copied_bindings=catalog)
    (OUT / 'root-review.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(copied=len(catalog), held_DMA=166, repaired_DMA=167, adopted=False)))


if __name__ == '__main__':
    main()
