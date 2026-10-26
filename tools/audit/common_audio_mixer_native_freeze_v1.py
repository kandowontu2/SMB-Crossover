"""Freeze completed independent common-mixer450 result; never launches."""
from pathlib import Path
import argparse
import json
from smb3_host_current3b_cpu_v1 import D, R, sha, put


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    source = D/'common-audio-mixer-current3b-v3'
    native = D/'common-audio-mixer-f4efd-mega450-ready-v1'
    sr, nr = source/'source-freeze-v1/readiness.json', native/'readiness.json'
    assert sha(sr) == '0f06bee8a51b1303facfd554fc767335dae32ef901dffb9d62d5924e79a4b2d1'
    assert sha(nr) == '72f4d33b00dbdf892bc7d7b70064f997e06f12fab828a781e63bac64c59217f0'
    s, n = [json.loads(f.read_text()) for f in [sr, nr]]
    bindings = {Path(v['path']): v['sha256'] for v in s['bindings']}
    bindings.update({Path(f): h for f, h in n['bindings'].items()})
    review = native/'review-v1'
    bindings.update({Path(f): h for f, h in json.loads((review/'bindings.json').read_text()).items()})
    grant = native/'ROOT-grant.json'
    assert sha(grant) == 'd9d4df72e7e4f3b2fe60c8548973171754cfa1da290d99543de9810119248782'
    for f, h in bindings.items():
        assert sha(f) == h, f
    for kind in ['user_settings', 'worker_settings', 'emulator', 'core']:
        assert sha(n['environment'][kind]) == n['environment'][kind+'_sha256']
    run = json.loads((native/'native-receipt.json').read_text())
    q = json.loads((review/'proof.json').read_text())
    assert run['passed'] and run['worker_released'] and run['launches'] == 1 and run['retries'] == 0
    assert q['passed'] and q['RGB_byte_identity_pass'] and q['lossless_pairs'] == 275
    assert q['baseline_actual_DMAs'] == q['candidate_actual_DMAs'] == 402
    assert q['visible_prefix_deficit_frames'] == 0 and q['actual_input_polls'] == [449, 449]
    result = run['result']
    assert [result[k] for k in ['NMI_checks', 'IRQ31_checks', 'scoped_enables']] == [442, 79, 72]
    report = R/'docs/qa/common-audio-mixer-native-2026-10-26.txt'
    extras = {Path(__file__), report, sr, nr, grant}
    extras.update(f for f in native.iterdir() if f.is_file())
    extras.update(f for f in review.iterdir() if f.is_file())
    bindings.update({f: sha(f) for f in extras})
    receipt = dict(passed=True, native_run=True, adopted=False,
        ROM_sha256=run['ROM_sha256'], parent_ROM_sha256=q['baseline_ROM_sha256'],
        source_readiness_sha256=sha(sr), native_readiness_sha256=sha(nr),
        launches=1, retries=0, worker_released=True,
        full256_DMAs=402, safe_enables=72, NMI_checks=442, IRQ31_checks=79,
        actual_input_polls=449, lossless_PPU_pairs=275,
        cumulative_visible_DMA_deficit_frames=0, different_RGB_pairs=0,
        manual_wholeframe_review=dict(frames=[184,372,403,438,444,450],
            result='Pairs identical; existing hardware sprite contention remains in both.'),
        no_waveform_allroster_route_fairness_or_adoption_claim=True,
        report=str(report), bindings={str(f.resolve()): h for f,h in sorted(bindings.items())})
    put(a.output/'readiness.json', receipt)
    print(json.dumps(dict(passed=True, bindings=len(bindings),
        readiness_sha256=sha(a.output/'readiness.json'), worker_released=True)))


if __name__ == '__main__':
    main()
