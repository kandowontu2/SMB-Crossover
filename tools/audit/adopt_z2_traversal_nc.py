"""Admit the frozen physical Jump and camera repair over the MZ source."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT/'build/verification/new-pipe-playability-agent/handoff-z2-pipes-h'
OUTPUT = ROOT/'build/verification/traversal-adoption-nc/z2'
SHA = '00f335d41e777c02f484a715e07538242899b74899974aa3b7154e5ca809c1ea'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not OUTPUT.exists()
    assert digest(PACKET/'manifest.json') == SHA
    packet = json.loads((PACKET/'manifest.json').read_text())
    parent = json.loads((ROOT/'build/checkpoints/full-roster-mz/manifest.json').read_text())
    assert packet['parent']['expanded_sha256'] == parent['ROMs']['mmc5-expanded']
    for item in packet['artifacts']:
        path = PACKET/item['path']
        assert path.stat().st_size == item['bytes'] and digest(path) == item['sha256'], item['path']
    assert [item['path'] for item in packet['changes']] == ['src/zelda2_link_motion.s']
    for item in packet['changes']:
        name = item['path']
        assert digest(ROOT/name) == parent['source_files'][name] == item['before_sha256']
        assert digest(PACKET/'source'/name) == item['after_sha256']
    OUTPUT.mkdir(parents=True)
    for item in packet['changes']:
        name = item['path']
        before = OUTPUT/'before'/name
        before.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT/name, before)
        shutil.copyfile(PACKET/'source'/name, ROOT/name)
    (OUTPUT/'adoption.json').write_text(json.dumps(dict(parent='full-roster-mz',
        packet_sha256=SHA, changes=packet['changes'], resident_growth=0,
        source_game_physics_unchanged=True), indent=2)+'\n')
    print('Adopted narrow Z2 camera and physical first-Jump delivery repair')


if __name__ == '__main__':
    main()
