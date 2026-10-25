"""Classify frozen literal-inventory hits without altering historical evidence."""
from pathlib import Path
import argparse
import hashlib
import json

sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--archive', type=Path, required=True)
    p.add_argument('--inventory', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    inventory = json.loads(a.inventory.read_text(encoding='utf-8'))
    assert inventory['audit_complete']
    classes = []
    for row in inventory['hits']:
        path = Path(row['path'])
        assert sha(path) == row['sha256'], 'Frozen script changed'
        relative = path.relative_to(a.archive).as_posix()
        if relative.startswith(('final-item-matrix-v1/', 'current84-abilities-v1/')):
            assert all(x['literal'] in ['True', 'False'] and 'hard' in x['context'] for x in row['bare_python_literals'])
            category = 'Progression/acquired-ability configuration: actual Easy; declared Hard withdrawn. Includes preparation drafts and failed/superseded attempts, not only final receipts.'
        elif relative.startswith('zelda2-terrain-candidate-v4/native-components-v'):
            assert relative.split('/')[1] in ['native-components-v1', 'native-components-v2', 'native-components-v3']
            assert all(x['literal']=='True' and 'fairy' in x['context'] for x in row['bare_python_literals'])
            failed = path.parent/'native-proof.json'
            prior = json.loads(failed.read_text(encoding='utf-8'))
            assert prior['passed'] is False and prior['emulator_exit'] != 0
            category = 'Failed pre-adoption Fairy fixture. Retained failure, not accepted geometry evidence.'
        else:
            raise AssertionError('Unclassified literal hit: '+relative)
        classes.append(dict(path=str(path), sha256=row['sha256'], classification=category))
    zroot = a.archive/'zelda2-terrain-candidate-v4'
    accepted = zroot/'native-components-v4/native-proof.json'
    adoption = zroot/'adoption-v1/proof.json'
    z = json.loads(accepted.read_text(encoding='utf-8'))
    ad = json.loads(adoption.read_text(encoding='utf-8'))
    assert z['passed'] is True and z['emulator_exit']==0
    assert any(x['path']==str(accepted) and x['sha256']==sha(accepted) for x in ad['evidence'])
    clean_scripts = {str(Path(x['path'])) for x in json.loads((a.inventory.parent/'files.json').read_text(encoding='utf-8')) if not x['bare_python_literals']}
    assert str(accepted.parent/'run.lua') in clean_scripts
    correction = a.archive/'current84-abilities-v1/mode-correction-v1/proof.json'
    old = json.loads(correction.read_text(encoding='utf-8'))
    assert old['audit_passed'] and old['affected_final_runs']==18 and old['withdrawn_hard_labels']==9
    result = dict(audit_passed=True, game_ROM_changed=False, original_receipts_edited=False,
                  frozen_files_scanned=inventory['scanned_files'], literal_hit_files=len(classes),
                  inventory=dict(path=str(a.inventory), sha256=sha(a.inventory)),
                  classifications=classes,
                  withdrawal=dict(path=str(correction), sha256=sha(correction), invalid_Hard_labels=9, affected_final_runs=18),
                  Zelda_accepted_evidence=dict(path=str(accepted), sha256=sha(accepted),
                      adoption_path=str(adoption), adoption_sha256=sha(adoption),
                      scope='Adopted v4 has integer Fairy flags; v1–3 were failed, unadopted attempts.'),
                  scope='Exact selected frozen roots only. No capitalized literal hits in the other scanned scripts; that excludes this specific defect, not other fixture defects or a new gameplay/mode pass. Historical raw receipts remain unchanged. Separate genuine Hard reruns are required and bound elsewhere.',
                  tool_sha256=sha(Path(__file__)))
    (a.output/'proof.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ['classifications']}))


if __name__ == '__main__':
    main()
