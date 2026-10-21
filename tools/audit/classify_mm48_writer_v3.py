"""Host-only classification of root's retained strict writer negative."""
from pathlib import Path
from collections import Counter
import hashlib
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / 'build/verification/mm48-permanent-zp-writer-report-v3'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = HERE / 'root-classification-a.json'
    assert not out.exists()
    spec = importlib.util.spec_from_file_location('lossless_writer_codec', HERE / 'packing.py')
    codec = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(codec)
    source = HERE / 'all-writers-a.json'
    data = json.loads(source.read_text())
    writes = codec.unpack(data['ordered_EC_FF_writes'])
    canonical = json.dumps(writes, sort_keys=True, separators=(',', ':')).encode()
    assert hashlib.sha256(canonical).hexdigest() == data['ordered_EC_FF_writes']['original_rows_canonical_sha256']
    assert data['cases_started'] == 72 and len(writes) == 10082
    groups = []
    for index, group in enumerate(data['character_results']):
        first = 6497 + index * 7
        assert group['last_original_case_id'] == first + group['cases_started'] - 1
        last = group['last_original_case_id']
        group_writes = [w for w in writes if first <= w['case'] <= last]
        foreign = Counter((w['binary'], w['physical8kBank'], w['pc'], w['actual_bytes8'], w['address'])
                          for w in group_writes
                          if w['entry'] == 'AudioUpdate' and w['physical8kBank'] not in (11, 12, 63))
        groups.append(dict(character=group['away_character'],
                           original_first_case=first, original_last_case=last,
                           started_calls=group['cases_started'], strict_status=group['status'],
                           strict_error=group['error'],
                           actual_foreign_writer_rows=[
                               dict(binary=k[0], physical8kBank=k[1], PC=f'{k[2]:04X}',
                                    bytes8=k[3], address=f'{k[4]:02X}', count=n)
                               for k, n in sorted(foreign.items())]))
    assert [g['character'] for g in groups if g['strict_error']] == [2, 3, 5]
    # Check exact symbol identity for the two private snapshot disagreements.
    labels = (ROOT / 'build/checkpoints/roster-audit-v48/smb-crossover-mmc5.lbl').read_text()
    assert 'al 0071DD .RgAudioCpuZp' in labels
    report = dict(status='root-classified strict prototype negative; NOT qualification',
                  report=dict(path=str(source.relative_to(ROOT)), sha256=sha(source), bytes=source.stat().st_size),
                  frozen_runner_sha256=sha(HERE / 'frozen.json'),
                  original_strict_verifier_sha256=data['original_verifier_sha256'],
                  cases=72, decoded_writes=10082,
                  complete_ordered_write_roundtrip_and_hash_exact=True,
                  groups=groups,
                  findings=[
                      'Samus first away call6513 actually writes EC/ED in native physicalbank15 atBA5F/BA64 and corrupts proposed live MM3 logical first2bytes.',
                      'Bill first away call6520 stops at private RgAudioCpuZp offsets12..15 ($71E9..$71EC) mismatch; Simon6534 stops at offsets18..21 ($71EF..$71F2). Actual highZP write rows retained. No general RAM exclusion or repaired oracle applied.',
                      'Nine remaining independent away groups pass all7 original strict calls, including return. Samus/Bill/Simon stop at first strict failure; later away/return coverage for these groups is not claimed.',
                      'V3 compact output changes representation only. All10082 complete original ordered writer dictionaries roundtrip and match canonical hash.',
                      'This is CPU-model-only evidence from original unqualified isolated48 prototype, with no NMI/IRQ interruption/hardware/PPU/PCM/route qualification.',
                  ], model_calls_in_classifier=0, native_calls=0, shared_runtime_writes=0)
    out.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(report=str(out.relative_to(ROOT)), sha256=sha(out), bytes=out.stat().st_size)))


if __name__ == '__main__':
    main()
