"""Keep the360-frame controller policy intact after a terminal wall timeout."""
from pathlib import Path
import hashlib
import json

R = Path(__file__).resolve().parents[2]
P = R/'build/smb3plus-low-factor-native-1031-v1'
O = R/'build/smb3plus-low-factor-native-1031-v2'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists()
    prior = json.loads((P/'toad/capture/capture-budget.json').read_text())
    assert prior['returncode'] == 4294967295 and prior['seconds'] >= 60
    assert not (P/'toad/capture/result.json').exists()
    assert prior['violations'] == []
    packets = []
    for name in ['toad', 'peach']:
        source, dest = P/name, O/name
        q = json.loads((source/'ready.json').read_text())
        for p, digest in q['bindings'].items():
            assert sha(p) == digest, p
        dest.mkdir(parents=True)
        for file in ['controller.lua', 'run.py']:
            (dest/file).write_bytes((source/file).read_bytes())
            assert sha(dest/file) == sha(source/file)
        q.update(host_timeout_seconds=90,
            retry_reason='The completed first attempt hit Mesen60s wall timeout at323/360 gameplay frames without a product assertion or budget violation. Native process is terminal. Keep controller/observations360frames unchanged; increase only host time allowance.',
            retained_negative=str(P/'toad/capture/capture-budget.json'))
        for p in [Path(__file__), source/'ready.json', dest/'controller.lua', dest/'run.py', P/'toad/capture/capture-budget.json']:
            q['bindings'][str(p.resolve())] = sha(p)
        (dest/'ready.json').write_text(json.dumps(q, indent=2)+'\n', encoding='utf-8', newline='\n')
        packets.append(dict(identity=name, ready=str(dest/'ready.json'), sha256=sha(dest/'ready.json')))
    (O/'prepared.json').write_text(json.dumps(dict(prepared=True, native=False,
        exact_same_controller_bytes=True, host_timeout_seconds=90,
        screenshot_file_storage_caps_unchanged=True, packets=packets), indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps(dict(prepared=True, native=False, packets=packets)))


if __name__ == '__main__':
    main()
