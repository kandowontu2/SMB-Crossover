"""Compose the frozen CV3/camera repair beside the independent Z2 repair."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT/'build/player-guide-agent/cv3-pipe-private/adoption-packet'
OUTPUT = ROOT/'build/verification/traversal-adoption-nc/cv3'
SHA = 'b5bea1ca4e9ea174968c911ad6b77625566432bd481557ec2aa17d787d70f19b'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not OUTPUT.exists()
    assert digest(PACKET/'manifest.json') == SHA
    packet = json.loads((PACKET/'manifest.json').read_text())
    parent = json.loads((ROOT/'build/checkpoints/full-roster-mz/manifest.json').read_text())
    assert packet['parent_ROM']['sha256'] == parent['ROMs']['mmc5-expanded']
    for group in ('scripts', 'evidence'):
        for item in packet[group]:
            path = ROOT/item['path']
            assert path.resolve().is_relative_to(PACKET.resolve())
            assert path.stat().st_size == item['bytes'] and digest(path) == item['sha256'], item['path']
    assert {item['path'] for item in packet['changed_files']} == {'src/x5_bounce.s', 'src/cv3_combat.s'}
    for item in packet['changed_files']:
        name = item['path']
        assert digest(ROOT/name) == parent['source_files'][name] == item['before_sha256']
        assert digest(ROOT/item['staged']['path']) == item['after_sha256']
    OUTPUT.mkdir(parents=True)
    for item in packet['changed_files']:
        name = item['path']
        before = OUTPUT/'before'/name
        before.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT/name, before)
        shutil.copyfile(ROOT/item['staged']['path'], ROOT/name)
    (OUTPUT/'adoption.json').write_text(json.dumps(dict(parent='full-roster-mz plus Z2 repair',
        packet_sha256=SHA, changes=packet['changed_files'], resident_growth=0,
        adapted_ordinary_air_displacement=2, prior_hurt_byte='5CC3'), indent=2)+'\n')
    print('Adopted bounded CV3 traversal and new-family camera repair')


if __name__ == '__main__':
    main()
