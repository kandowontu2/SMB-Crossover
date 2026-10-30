"""Prepare the existing finite PN controller against original V13/final resource base."""
from pathlib import Path
import hashlib
import json

R = Path(__file__).resolve().parents[2]
O = R/'build/character-host-union-resources-v1'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    assert not (O/'native-prepared.json').exists()
    controls = json.loads((O/'controls.json').read_text())
    assert controls['passed'] and sha(O/'ice/candidate.nes') == controls['ROM_sha256']
    for path, digest in controls['source_bindings'].items():
        assert sha(path) == digest, path
    parent = R/'build/character-host-union-v13'
    original = R/'tools/audit/parodius_chr_compact_native_v1.py'
    text = original.read_text()
    changes = [
        ("O=R/'build/parodius-chr-compact-v1'", "O=R/'build/character-host-union-resources-v1'"),
        ("R/'build/character-host-union-v7/native_cold.lua'", "R/'build/character-host-union-v13/native_cold.lua'"),
        ("R/'build/character-host-union-v5/candidate.nes'if a.parent else O/'candidate.nes'",
         "R/'build/character-host-union-v13/candidate.nes'if a.parent else O/'ice/candidate.nes'"),
        ("(O/'build-proof.json')", "(O/'native-proof.json')"),
        ("emulator_options=['--nes.ramPowerOnState=AllZeros'",
         "emulator_options=['--doNotSaveSettings','--nes.removeSpriteLimit=false','--nes.ramPowerOnState=AllZeros'")]
    for before, after in changes:
        assert text.count(before) == 1, before
        text = text.replace(before, after)
    driver = O/'native-adapter.py'
    assert not driver.exists()
    driver.write_text(text, newline='\n')
    proof = dict(parent_sha256=sha(parent/'candidate.nes'), candidate_sha256=controls['ROM_sha256'])
    (O/'native-proof.json').write_text(json.dumps(proof, indent=2)+'\n')
    inputs = dict(controls['source_bindings'])
    for path in [Path(__file__).resolve(), original, parent/'native_cold.lua', O/'controls.json',
                 O/'native-proof.json', driver]:
        inputs[str(path)] = sha(path)
    prepared = dict(prepared=True, native_run=False, parent_ROM_sha256=proof['parent_sha256'],
                    candidate_ROM_sha256=proof['candidate_sha256'], source_bindings=inputs,
                    modifications='Only paths/template version and explicit normal sprite limit/doNotSaveSettings options. Original finite up/down/shoot controller and all behavior assertions retained.',
                    runs='Serial --variant1/2/3, each --parent then candidate; one screenshot container per run, no frame-file forest.',
                    queue='Do not launch while another native capture owns the global lease.')
    (O/'native-prepared.json').write_text(json.dumps(prepared, indent=2)+'\n')
    print(json.dumps(dict(prepared=True, candidate=proof['candidate_sha256'], driver=str(driver))))


if __name__ == '__main__':
    main()
