"""Correlate saved731 Luigi state/images with actual compiled palette owners."""
from pathlib import Path
import csv
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
S = D / 'mm-proto-clean-menu-candidates-v1/clean-menu-irq'
N = D / 'luigi-flower731-rg-owner-v1/luigi-easy'
O = D / 'luigi-palette731-source-v1'
ROM = '731c918b0f448564587d90fca2979afc9fc0e5eb9b26616f4241801e2e73e16c'
sys.path.insert(0, str(ROOT / 'tools/audit'))
from robots_weapon_cpu_v1 import Arena
from check_tmnt_render_oa import load


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p, q):
    assert not p.exists(), p
    p.write_text(json.dumps(q, indent=2) + '\n', encoding='utf-8')
def buffered(q):
    data = [q.get('VRAM_Buffer1', i) for i in range(q.get('VRAM_Buffer1_Offset'))];rows = []
    while data:
        address = data[0] * 256 + data[1];count = data[2];assert not count & 192
        rows.append(dict(PPU_address=address, values=data[3:3 + count]));data = data[3 + count:]
    return rows


def main():
    assert sha(S / 'candidate.nes') == ROM;O.mkdir(exist_ok=False);b = load(S / 'candidate.nes')
    with (N / 'flower-state.csv').open() as f:state = {int(r['frame']):r for r in csv.DictReader(f)}
    with (N / 'render.csv').open() as f:render = {int(r['frame']):r for r in csv.DictReader(f)}
    selected = [1568, 1616, 1713, 1714, 1720, 1760, 1761, 1768, 1984]
    actual = []
    for frame in selected:
        r = state[frame];v = render[frame]
        actual.append(dict(frame=frame, growing=int(r['growing']), growth_age=int(r['age']),
            PlayerStatus=int(r['power']), engine=int(r['engine']), RgShootPose=int(v['shoot']),
            rgTypes=r['rgTypes'], sample_file='growth-2-1713.png' if frame == 1713 else f'frames/{frame:06}.png'))
    assert state[1713]['growing'] == '1' and state[1713]['age'] == '59' and state[1713]['power'] == '1'
    assert all(state[f]['growing'] == '0' and state[f]['power'] == '2' and render[f]['shoot'] == '0' for f in [1720, 1760, 1761])
    put(O / 'actual-native-state-points.json', actual)
    growth = []
    for age in range(60):
        q = Arena(b, 8);q.put(CrossoverBehaviorVersion=0, PlayerStatus=1, GuestPowerupActive=1,
            GuestPowerupOld=1, GuestPowerupTarget=2, GuestPowerupDisplay=2 if (age // 6) & 1 else 1,
            GuestPowerupAge=age, GuestLegacyHurt=0, VRAM_Buffer1_Offset=0)
        q.invoke('GuestPowerupPalette');rows = buffered(q)
        expected = [[26,39,23], [26,39,48], [22,39,48], [15,36,48]][age // 6 & 3]
        if age // 6 & 3 == 0 and (age // 6) & 1:expected = [48,39,22]
        assert rows == [dict(PPU_address=0x3f11, values=expected)]
        growth.append(dict(age=age, rows=rows))
    assert growth[59]['rows'] == [dict(PPU_address=0x3f11, values=[26,39,48])]
    stable = []
    for power, pose in [(p, pose) for p in range(3) for pose in [0, 1, 4, 7]]:
        q = Arena(b, 8);q.put(CrossoverBehaviorVersion=0, PlayerStatus=power, RgPose=pose,
            RgShootPose=8 if pose == 7 else 0, GuestPowerupActive=0, VRAM_Buffer1_Offset=0, AreaType=1)
        q.invoke('GetPlayerColors');rows = buffered(q)
        body = next(r for r in rows if r['PPU_address'] == 0x3f10)
        assert body['values'] == ([34,48,39,22] if power == 2 else [34,26,39,23])
        stable.append(dict(power=power, pose=pose, source_rows=rows))
    q = Arena(b, 8);q.put(CrossoverBehaviorVersion=0, PlayerStatus=1, GuestPowerupActive=1,
        GuestPowerupOld=1, GuestPowerupTarget=2, GuestPowerupDisplay=2,
        GuestPowerupAge=59, GuestLegacyHurt=0, VRAM_Buffer1_Offset=0, AreaType=1)
    q.invoke('GuestPowerupUpdate');finish = dict(power=q.get('PlayerStatus'), active=q.get('GuestPowerupActive'), rows=buffered(q))
    assert finish['power'] == 2 and finish['active'] == 0
    assert next(r['values'] for r in finish['rows'] if r['PPU_address'] == 0x3f10) == [34,48,39,22]
    put(O / 'actual-compiled-palette-components.json', dict(growth=growth, stable=stable, actual_finish=finish))
    images = [N / 'growth-2-1713.png', N / 'frames/001720.png', N / 'frames/001760.png', N / 'frames/001768.png']
    assert all(p.is_file() for p in images)
    files = [Path(__file__), S / 'candidate.nes', S / 'candidate.dbg', N / 'flower-state.csv', N / 'render.csv'] + images
    files += [S / 'source/src' / n for n in ['guest_powerups.s','x5_palette.s','screen_render.s']]
    files += list(O.iterdir())
    put(O / 'proof.json', dict(passed=True, source_CPU_only=True, new_native_run=False, ROM_sha256=ROM,
        actual_saved_native_states=True, captured_native_PPU_palette_RAM=False, growth_cases=60, stable_pose_cases=12,
        finish_cases=1, body_colors_at_growth_age59=[26,39,48], stable_Fire_body_colors=[48,39,22],
        first_source_allocation_frame=1761, stable_Fire_images_before_first_fire=[1720,1760],
        result='Growth59 green/white is replacement-flash palette. Stable Fire white/red is already visible before first shot and matches current compiled Luigi source data; no firing-triggered palette ownership bug established.',
        bindings={str(p):sha(p) for p in files},
        scope='Actual saved731 RAM observations plus newly executed isolated palette-owner CPU components and viewed selected complete images. No new native palette-RAM observation, original Crossover art/palette parity or waveform claim.'))
    print(json.dumps(dict(passed=True, proof_sha256=sha(O / 'proof.json'), bindings=len(files)), indent=2))


if __name__ == '__main__':main()
