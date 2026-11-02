"""Bind the reviewed palette/HUD successor; this does not publish a ROM."""
import hashlib
import json
from pathlib import Path
from build_storage_guard_v1 import preflight

R = Path(__file__).resolve().parents[2]
O = R / 'build/bubble-visible-grant-1102-v6'
B = R / 'build/bubble-bobble-source-1101-v1'

def digest(data):
    return hashlib.sha256(data).hexdigest()

def main():
    preflight(private_root=O, fresh=True)
    O.mkdir(exist_ok=True)
    manifest = B / 'native-visible-successor-00971.json'
    assert digest(manifest.read_bytes()) == 'eb4050468e969dd1dc99783871c60b539e40be083b2a4528496c2b22ebe420eb'
    m = json.loads(manifest.read_text())
    f = json.loads((B / 'native-visible-qualified-1102-v6.json').read_text())
    for path, row in f['files'].items():
        assert digest((R / path).read_bytes()) == row['SHA256'], path
    archive = R / f['archive']
    assert digest(archive.read_bytes()) == f['archive_SHA256']
    original = (R / m['base_ROM']).read_bytes()
    assert digest(original) == m['base_ROM_SHA256']
    candidate = bytearray(original)
    spans = []
    for patch in m['patches']:
        a = patch['offset']; old = bytes.fromhex(patch['old']); new = bytes.fromhex(patch['new'])
        assert len(old) == len(new) and original[a:a+len(old)] == old
        assert all(a+len(old) <= x or a >= y for x,y in spans)
        spans.append((a,a+len(old)))
        candidate[a:a+len(old)] = new
    assert len(spans) == 10 and sum(a != b for a,b in zip(original,candidate)) == 220
    assert digest(candidate) == m['in_memory_candidate_SHA256'] == '4395ed57aaeccfd05ca743fc603f0d1b69b4991b072b55e68b49507cffc8c2ab'
    cp = R / 'docs/qa/checkpoints/2026-11-02/bubble-visible-v6'
    assert not cp.exists()
    cp.mkdir(parents=True)
    (cp / 'inputs.zip').write_bytes(archive.read_bytes())
    (cp / 'manifest.json').write_bytes((B / 'native-visible-qualified-1102-v6.json').read_bytes())
    (cp / 'proposal.json').write_bytes(manifest.read_bytes())
    receipt = dict(granted=True, private_native_testing_only=True, production_admitted=False,
        installed=False, base_ROM_SHA256=m['base_ROM_SHA256'], candidate_SHA256=digest(candidate),
        proposal_SHA256=digest(manifest.read_bytes()), actual_changed_bytes=220,
        scope='Nine existing private carriers and the complete 16-byte shared Bub/Bob authentication cookie. No new RAM or carrier allocation.',
        verification='CPU: in-place seven-character HUD name, full original HUD packet retained; native area backdrop; typed menu callback; original actor/world differential; IRQ and lag-NMI cuts.',
        remaining='Actual native palette/HUD, controls, Easy stomp, full 1-1, regressions and Downloads delivery remain unqualified.',
        checkpoint=str(cp.relative_to(R)).replace('\\','/'))
    dest = R / 'docs/qa/allocations/bubble-visible-1102-v6.json'
    assert not dest.exists()
    dest.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    (O / 'result.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt))

if __name__ == '__main__':
    main()
