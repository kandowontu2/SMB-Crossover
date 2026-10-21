"""Bind Sophia's actual flat-form state, original rectangle and firebar negative."""
from pathlib import Path
from fractions import Fraction
import csv
import hashlib
import importlib.util
import json
import xml.etree.ElementTree as ET

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
P = R / 'build/roster-through-2-2'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = V / 'root49-sophia-body-lead-hj.json'
    assert not out.exists()
    hg = P / 'root49hg-sophia-live-11-v0-mmc3'
    hh = P / 'root49hh-sophia-firebar-11-v0-mmc3'
    hi = P / 'root49hi-sophia-body-11-v0-mmc3'
    streams = ['inputs.csv', 'trace.csv', 'events.csv', 'audio-events.csv', 'chr.csv',
        'oam.csv', 'render.csv', 'scroll-writes.csv', 'stomp-events.csv']
    assert all((hh / n).read_bytes() == (hi / n).read_bytes() for n in streams)
    assert all((hg / n).read_bytes() == (hi / n).read_bytes() for n in streams[:3])
    parser = V / 'agent49g-samus-crouch-fix-proposal-b/image.py'
    assert sha(parser) == '54fef35b891a96d5d0e36ca6cdeec9ee90b990666395714bc32e80cd1cabb0fb'
    spec = importlib.util.spec_from_file_location('sophia_body_review', parser)
    m = importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    im = m.Image(V / 'agent-lsr-link-ceiling-c/source/build/smb-crossover-mmc3.nes')
    assert sha(im.path) == 'a5583527ebfaf4cac1bb4384518ddf2a93a72abc79469e773e525b8ce227bb12'
    snapshot = hi / 'actual-firebar-body.bin'
    data = snapshot.read_bytes();assert len(data) == 10240
    def rd(address):
        assert 0 <= address < 0x800 or 0x6000 <= address < 0x8000
        return data[address if address < 0x800 else address - 0x6000 + 0x800]
    def r(name, index=0):
        return rd(im.ram[name] + index)
    normal = {n: r(n) for n in ('SelectedCharacter', 'CrossoverBehaviorVersion', 'PlayerStatus',
        'Player_State', 'PlayerFacingDir', 'XgWall', 'XgCeiling', 'XgRise', 'XgWallContact',
        'XgWallLock', 'XgHoverActive', 'RgCrouch', 'RgAttack', 'RgShootPose', 'RgPose',
        'GuestHurtTicks', 'GuestPowerupActive', 'MmDeathFlag', 'MmUnderwater', 'GuestLegacyHurt')}
    assert normal['SelectedCharacter'] == 11 and normal['CrossoverBehaviorVersion'] == 0
    assert normal['RgPose'] == 2 and normal['PlayerFacingDir'] == 1
    assert all(value == 0 for name, value in normal.items() if name not in ('SelectedCharacter', 'RgPose', 'PlayerFacingDir'))
    py, px = r('Player_Y_Position'), r('Player_X_Position') + 256 * r('Player_PageLoc')
    assert py == 112 and px == 740 and r('Player_Y_HighPos') == 1
    assert r('MmYFraction') + 256 * r('MmYFraction', 1) == 0
    cells = []
    for x in (px + 2, px + 8, px + 13):
        tile = rd(im.ram['Block_Buffer_1'] + (x // 256 % 2) * 208 + ((144 - 32) // 16) * 16 + x % 256 // 16)
        assert tile == 98
        cells.append(dict(x=x, y=144, tile=tile))
    xml = R / 'reference/crossover2/main.xml'
    root = ET.parse(xml).getroot()
    ids = {n.get('spriteId') or n.get('shapeId'): n for n in root.find('tags') if n.get('spriteId') or n.get('shapeId')}
    sprite = ids['113'];frame = 1;changes = []
    for node in sprite.find('subTags'):
        if node.get('depth') == '1' and node.get('type', '').startswith('PlaceObject'):
            changes.append(dict(frame=frame, item=node.attrib, matrix=node.find('matrix').attrib))
        if node.get('type') == 'ShowFrameTag':frame += 1
    assert [x['frame'] for x in changes] == [1, 28]
    matrix = changes[0]['matrix']
    assert Fraction(matrix['scaleX']) * 160 / 40 == 19
    assert Fraction(matrix['scaleY']) * 160 / 40 == Fraction(31, 2)
    assert Fraction(matrix['translateY']) / 40 == -Fraction(31, 2)
    source_top = Fraction(144) - Fraction(31, 2)
    assert source_top == Fraction(257, 2)
    with (hi / 'sophia-firebar-source-probe.csv').open(newline='') as stream:
        rows = list(csv.DictReader(stream))
    fatal = next(x for x in rows if x['event'] == 'ForceInjury')
    pre = next(x for x in rows if x['event'] == 'ChgSDir')
    assert fatal['R0R7'] == pre['R0R7'] == '4:37:15:2:116:0:123:115'
    assert pre['body'] == '113:120:127:144'
    assert pre['x'] == '740' and pre['y'] == '112' and pre['yf'] == '0'
    complete = next(x for x in rows if x['event'] == 'endFrame' and x['frame'] == '11129')
    parts = [tuple(map(int, x.split(':'))) for x in complete['parts'].split(';')[0].split(':', 7)[7].split('/')]
    assert [y for x, y in parts] == [100, 103, 106, 109, 112, 115]
    container_upper_bound = max(y for x, y in parts) + 13
    assert container_upper_bound == 128 < source_top
    files = {snapshot, xml, parser, V / 'root49-gq-sophia-firebar-hh/binding.json',
        V / 'root49-gq-sophia-body-hi/binding.json', hi / 'sophia-firebar-source-probe.csv'}
    for name in ('HitTester', 'HRect'):
        files.add(R / f'reference/crossover2/extracted/scripts/com/smbc/data/{name}.as')
    files.update(R / ('reference/crossover2/extracted/scripts/com/smbc/' + n) for n in (
        'characters/Character.as', 'characters/Sophia.as', 'main/AnimatedObject.as', 'data/MovieClipInfo_SophiaMc.as'))
    for folder in (hg, hh, hi):
        files.update(folder / n for n in streams if (folder / n).exists())
        files.update((folder / 'manifest.json', folder / 'result.json'))
    report = dict(status='BOUND_SOPHIA_NORMAL_BODY_AND_ACTUAL_FIREBAR_NEGATIVE',
        script_sha256=sha(__file__), ROM_sha256=sha(im.path), snapshot_sha256=sha(snapshot),
        actual_flat_normal_state=normal, actual_ground_cells=cells, source_HRect_changes=changes,
        source_normal_dimensions_NES=dict(width='19', height='31/2', local_top='-31/2'),
        native_body=dict(left=113, top=120, right=127, bottom=144, height=24),
        source_ground_anchor='Actual authored ground top144, nativePY112+32; original flat HRect bottom0 is source ny at this same ground. Prior/current native vertical position is stationary112; source cached display bounds do not change its vertical interval.',
        source_normal_top_NES=str(source_top), actual_complete_bar_centers=parts,
        conservative_whole_container_upper_bound=128,
        exact_HG_HH_HI_all21_trace_fields_and_inputs=True, exact_HH_HI_all9_CSVs=True,
        conclusion='The flat normal source body is15.5NES pixels tall, while current native body is24. The admitted legacy PY sampler also lies above the source body and causes this reproducible firebar death. Correct the source body and its consumers before continuing this point.',
        qualifications=['This binds the normal flat form; wall/ceiling/vine orientations and their terrain axis behavior still require source contracts.',
            'Full source/native firebar birth, angle, anchor and pixel-positive parity is not certified. The conditional geometry follows the complete actual emitted native piece layout.',
            'The inherited sourceFrame CSV field is raw RgBillBurst, not a Sophia frame; actual flat-form admission is bound separately from full RAM and original main HRect.',
            'No repaired runtime, complete2-2 route, all-arsenal or final recording claim.'],
        next_action='Implement source-shaped Sophia flat body/consumer behavior with exact fractional edges; retain other source orientation requirements and test them subsequently. Do not hide this contact with another controller wait.',
        references={p.relative_to(R).as_posix():dict(sha256=sha(p), bytes=p.stat().st_size) for p in sorted(files)},
        runtime_changes=False, accepted_release=False, goal_complete=False)
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'], sha(out))


if __name__ == '__main__':
    main()
