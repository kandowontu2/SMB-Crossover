"""Replay the actual Sophia castle contact with narrowly bound firebar probes."""
from pathlib import Path
from fractions import Fraction
import hashlib
import json
import subprocess
import sys
import xml.etree.ElementTree as ET

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-gq-sophia-firebar-hh'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    H.mkdir(exist_ok=False)
    source = R / 'reference/crossover2/main.xml'
    root = ET.parse(source).getroot()
    symbols = {n.get('spriteId') or n.get('shapeId'): n for n in root.find('tags') if n.get('spriteId') or n.get('shapeId')}
    sophia = symbols['113']
    rect = next(n for n in sophia.find('subTags') if n.get('type', '').startswith('PlaceObject') and n.get('depth') == '1')
    assert rect.get('characterId') == '14'
    sprite = symbols['14']
    shape_ref = next(n for n in sprite.find('subTags') if n.get('type', '').startswith('PlaceObject'))
    assert shape_ref.get('characterId') == '13'
    shape = symbols['13'].find('shapeBounds')
    m = rect.find('matrix')
    assert (shape.get('Xmin'), shape.get('Ymin'), shape.get('Xmax'), shape.get('Ymax')) == ('0', '0', '160', '160')
    # SWF twips /20 to Flash pixels /2 to NES coordinates. Normal frame only;
    # current source frame and character foot anchor still need native binding.
    width = Fraction(160) * Fraction(m.get('scaleX')) / 40
    height = Fraction(160) * Fraction(m.get('scaleY')) / 40
    assert width == 19 and height == Fraction(31, 2)
    source_rect = dict(symbol=113, depth=1, child_sprite=14, shape=13,
        matrix=m.attrib, shape_bounds=shape.attrib, width_NES=str(width), height_NES=str(height),
        local_x_NES=str(Fraction(m.get('translateX')) / 40),
        local_y_NES=str(Fraction(m.get('translateY')) / 40),
        qualification='Normal source frame geometry only. Native foot anchor/current source frame, cached source bounds timing and full firebar phase/pixel parity are not yet certified.')
    parent = V / 'agent-lsr-link-gq-route-a/policy-g-passive.lua'
    text = parent.read_text()
    old_base = V / 'agent-lsr-link-gq-route-a/policy-f.lua'
    new_base = V / 'root49-gq-sophia-route-gw/policy.lua'
    old = json.dumps(old_base.as_posix())
    assert text.count(old) == 1
    text = text.replace(old, json.dumps(new_base.as_posix()))
    text = text.replace("r('SelectedCharacter')==4", "r('SelectedCharacter')==11")
    text = text.replace('15280', '11100').replace('15300', '11130')
    text = text.replace('link-firebar-source-probe.csv', 'sophia-firebar-source-probe.csv')
    policy = H / 'policy.lua';policy.write_text(text)
    replay = R / 'build/roster-through-2-2/root49hg-sophia-live-11-v0-mmc3/inputs.csv'
    rom = V / 'agent-lsr-link-ceiling-c/source/build/smb-crossover-mmc3.nes'
    assert sha(rom) == 'a5583527ebfaf4cac1bb4384518ddf2a93a72abc79469e773e525b8ce227bb12'
    command = [sys.executable, str(R / 'tools/playthroughs/roster_run.py'), '--character', '11',
        '--mapper', 'mmc3', '--rom', str(rom), '--tag', 'root49hh-sophia-firebar',
        '--policy', str(policy), '--replay', str(replay), '--frames', '11129', '--timeout', '900', '--workspace-cap-gb', '60']
    report = dict(status='PREPARED_PASSIVE_ACTUAL_SOPHIA_FIREBAR_REPLAY',
        script_sha256=sha(__file__), parent_probe_sha256=sha(parent), new_base_policy_sha256=sha(new_base),
        policy_sha256=sha(policy), input_sha256=sha(replay), ROM_sha256=sha(rom),
        source_XML_sha256=sha(source), normal_source_rectangle=source_rect,
        component_or_runtime_changes=False, emulated_writes=False, state_loads=False,
        qualification='Investigate actual contact before changing route. The inherited sourceFrame CSV column is a raw RgBillBurst observation, not an asserted Sophia source frame.', command=command)
    (H / 'binding.json').write_text(json.dumps(report, indent=2) + '\n')
    rc = subprocess.run(command, cwd=R).returncode
    (H / 'host-result.json').write_text(json.dumps(dict(exit=rc), indent=2) + '\n')
    raise SystemExit(rc)


if __name__ == '__main__':
    main()
