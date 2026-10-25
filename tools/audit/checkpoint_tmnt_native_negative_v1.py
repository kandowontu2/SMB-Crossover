"""Keep the authentic-music cadence rejection and its measured next lead."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py/tmnt-native-storage-current50b5-v1')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    packet = D / 'native-negative-ready-v1'
    assert sha(packet / 'receipt.json') == '3a66c12fdefbc16e34ff7091aec44fed866f1a7f4e2bbea3eb6fa9e7235f9cb0'
    receipt = json.loads((packet / 'receipt.json').read_text())
    assert receipt['native_gate_failed'] and not receipt['accepted']
    assert receipt['added_draw_losses'] == 8 and receipt['Hard_prepared_not_run']
    assert sha(packet / 'diagnosis.json') == receipt['diagnosis_sha256']
    assert sha(packet / 'report.txt') == receipt['report_sha256']
    for path, value in receipt['native_artifact_bindings'].items():
        assert sha(Path(path)) == value
    tools = {'tools/audit/' + name: value for name, value in receipt['tools'].items()}
    hot = D / 'source-hot-lead-ready-v1'
    assert sha(hot / 'receipt.json') == 'd5097cb19d86f28ff19d777ba77245ebc64bbc88eae970e1aad7b383d8586d9c'
    lead = json.loads((hot / 'receipt.json').read_text())
    assert not lead['optimized_implementation']
    assert sha(hot / 'report.txt') == lead['report_sha256']
    for path, value in lead['proofs'].items():
        assert sha(Path(path)) == value
    for name, proof in [('tmnt_native_storage_hot_cpu.py', 'hot-source-407-505-v2/proof.json'),
                        ('tmnt_native_storage_math_lead.py', 'hot-multiply-contract-v1/proof.json')]:
        tools['tools/audit/' + name] = json.loads((D / proof).read_text())['tool_sha256']
    assert all(sha(ROOT / name) == value for name, value in tools.items())
    tools[Path(__file__).relative_to(ROOT).as_posix()] = sha(Path(__file__))
    out = ROOT / 'docs/qa/checkpoints/2026-10-25/tmnt-a983-native-held'
    out.mkdir(parents=True, exist_ok=False)
    copies = {'native-HELD.json': packet / 'receipt.json', 'native-report.txt': packet / 'report.txt',
              'diagnosis.json': packet / 'diagnosis.json', 'source-lead.json': hot / 'receipt.json',
              'source-lead-report.txt': hot / 'report.txt',
              'original-multiply-contract.json': D / 'hot-multiply-contract-v1/proof.json',
              'actual-hot-source-profile.json': D / 'hot-source-407-505-v2/proof.json'}
    for name, path in copies.items():
        shutil.copyfile(path, out / name)
    result = dict(goal_complete=False, production_changes=False, adoption_qualified=False,
                  files={p.name: sha(p) for p in out.iterdir()}, tools=tools,
                  external_packet=packet.as_posix(),
                  all_native_artifact_hashes_independently_checked=len(receipt['native_artifact_bindings']),
                  limits='Failed Easy native performance gate. Hard/broad native coverage remains '
                         'unrun. The next multiply optimization is only a source lead here.')
    (out / 'manifest.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(checkpoint=out.as_posix(), native_gate_failed=True,
                          checked_native_files=result['all_native_artifact_hashes_independently_checked'])))


if __name__ == '__main__':
    main()
