"""Bind optimized407/505 component calls to the frozen actual-native source states."""
from pathlib import Path
import argparse
import csv
import gzip
import json
from tmnt_native_storage_driver import ROOT, OB, sha
from tmnt_native_storage_multiply_cpu import Linked


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['experiment', 'baseline', 'candidate', 'output']:
        p.add_argument('--' + name, type=Path, required=True)
    a = p.parse_args()
    assert not a.output.resolve().is_relative_to(ROOT)
    a.output.mkdir(parents=True, exist_ok=False)
    actual = a.experiment / 'native-pilots-v1/diagnostic-candidate-easy-v3/source-state.csv'
    with actual.open() as stream: states = {int(row['sourceTick']): bytes.fromhex(row['ZP14_RAM174_hex']) for row in csv.DictReader(stream)}
    gold = json.loads(gzip.decompress((OB / 'probe-v2/song-02.json.gz').read_bytes()))
    parent, child = Linked(a.baseline, True), Linked(a.candidate, True)
    cases = []
    for tick in range(506):
        if tick in [407, 505]: assert parent.state() == child.state() == states[tick - 1]
        x, y = parent.call(gold[tick], 2), child.call(gold[tick], 2)
        assert parent.state() == child.state() == states[tick]
        assert parent.registers() == child.registers()
        if tick in [407, 505]:
            cases.append(dict(sourceTick=tick, isolated_parent_CPUcycles=x, isolated_candidate_CPUcycles=y,
                              saved_CPUcycles=x - y, actual_native188byte_before_after_exact=True,
                              original_APU_requests=len(gold[tick]['writes'])))
    assert [row['saved_CPUcycles'] for row in cases] == [362, 10]
    proof = dict(passed=True, source_only=True, native_run=False, baseline_ROM_sha256=sha(a.baseline), candidate_ROM_sha256=sha(a.candidate),
                 actual_native_a983_state_stream_sha256=sha(actual), cases=cases,
                 surrounding_506_original_calls_state_APU_ABI_exact=True, checker_sha256=sha(Path(__file__)),
                 limits='Actual frozen native source-state inputs/outputs bind isolated CPU calls. Other adapter/hardware DMC states follow the disclosed CPU fixture; no fresh native clock, source-waveform or eight-draw recovery claim.')
    (a.output / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps(proof))


if __name__ == '__main__':
    main()
