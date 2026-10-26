"""Freeze the three granted outcomes, retained failure and selected real PPU images."""
from pathlib import Path
import csv
import hashlib
import json
import sys

from PIL import Image, ImageDraw
from check_tmnt_render_oa import address, load, location

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
P = D / 'mario-powerups900-first-v2'
O = P / 'native-result-freeze-v1'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def get(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def put(p, z):
    p.write_text(json.dumps(z, indent=2) + '\n', encoding='utf-8')


def main():
    O.mkdir(exist_ok=False)
    ready = get(P / 'readiness.json')
    assert sha(P / 'readiness.json') == 'c5394d962a482e1de38400bbbceb57273ab7346589f9136a9aa17316c75b0a96'
    assert sha(P / 'ROOT-grant.json') == 'bb0b8edf8b5c5c4b607f05cc5d6b2dd4252eeb8c4619f87c02417ad41f70956a'
    for f, h in ready['bindings'].items():
        assert sha(f) == h, f
    native = get(P / 'native-proof.json')
    assert native['passed'] is False and native['profiles_run'] == 3
    assert [v['passed'] for v in native['profiles']] == [True, True, False]
    assert not (P / 'luigi3-easy/native-host.log').exists()
    rows = []
    selected = []
    for name in ['mario', 'luigi']:
        f = P / (name + '-easy')
        result, component = get(f / 'result.json'), get(f / 'powerup-component.json')
        assert result['component_complete'] and result['deaths'] == 0
        assert component['passed'] and component['actual_mode'] == 0
        assert component['transform_updates'] == 60 and component['collect'] == component['reveal'] == 1
        assert component['crouch_frames'] == 24 and component['air_frames'] == 54
        states = list(csv.DictReader((f / 'powerup-state.csv').open()))
        crouch = [z for z in states if int(z['crouch']) != 0]
        air = [z for z in states if int(z['frame']) > int(crouch[-1]['frame']) and z['playerState'] != '0']
        growth = sorted(f.glob('growth-*.png'), key=lambda p: int(p.stem.split('-')[-1]))
        assert len(growth) == 60
        picks = [growth[i] for i in [0, 9, 19, 29, 39, 49, 59]]
        periodic = sorted((f / 'frames').glob('*.png'), key=lambda p: int(p.stem))
        for z in [crouch[0], crouch[-1], air[0], air[len(air) // 2]]:
            picks.append(min(periodic, key=lambda p: abs(int(p.stem) - int(z['frame']))))
        picks.append(f / 'endpoint.png')
        assert len(picks) == 12
        sheet = Image.new('RGB', (4 * 256, 3 * 260), '#202020')
        draw = ImageDraw.Draw(sheet)
        for i, p in enumerate(picks):
            image = Image.open(p).convert('RGB')
            assert image.size == (256, 240)
            x, y = i % 4 * 256, i // 4 * 260
            sheet.paste(image, (x, y))
            draw.text((x + 3, y + 242), name + ' ' + p.name, fill='white')
            selected.append(dict(identity=name, file=str(p), SHA256=sha(p)))
        sheet.save(O / (name + '-selected12.png'))
        rows.append(dict(identity=name, passed=True, actual_mode=0, variant=component['variant'],
                         endpoint=result['frames'], deaths=0, physical_reveal=1, actual_collect=1,
                         original_growth_updates=60, saved_growth_PPU_images=60,
                         crouch_frames=24, air_frames=54, reveal_request_stores=component['reveal_requests'],
                         pickup_request_stores=component['pickup_requests'],
                         final_native_state=states[-1],
                         actual_owner_events=[json.loads(s) for s in (f / 'powerup-owner.jsonl').read_text().splitlines()],
                         CHR=get(f / 'chr-commit.json'), motion=get(f / 'completed-loop-motion.json')))
    f = P / 'mario3-easy'
    states = list(csv.DictReader((f / 'powerup-state.csv').open()))
    mature = [z for z in states if ':128:0:209:' in z['actors']]
    assert mature and mature[0]['frame'] == '616' and mature[-1]['frame'] == '717'
    log = (f / 'native-host.log').read_text()
    assert 'FAIL Actual first mushroom delivery type' in log
    assert not (f / 'powerup-component.json').exists() and not (f / 'result.json').exists()
    rom = D / 'current3cee-postdma-mask-v1/canonical-v2/candidate.nes'
    bundle = load(rom)
    proc = 'M3RisePickup'
    off = location(bundle, proc)
    raw = bundle['raw'][off:off + int(bundle['syms'][proc]['size'], 0)]
    at = address(bundle, 'PowerUpType')
    pattern = bytes([0xa9, 0, 0x95, at]) if at < 256 else bytes([0xa9, 0, 0x9d, at & 255, at >> 8])
    delta = raw.index(pattern)
    zero_store = dict(physical_bank=(off - 16) // 8192, CPU_PC=address(bundle, proc) + delta + 2,
                      bytes=list(pattern), target=at,
                      source='src/smb3_mario_pickups.s::M3RisePickup, mature$d1 branch')
    assert zero_store['physical_bank'] == 90 and zero_store['CPU_PC'] == 0xa443
    cfg = get(f / 'configuration.json')['item']
    failure = dict(passed=False, native_executed=True, retry=False,
                   first_assertion='Actual first mushroom delivery type',
                   classification='Fixture expected emerging type1 at collection; source correctly switches mature$d1 mushroom to walking type0',
                   first_saved_mature_state=mature[0], last_saved_state=states[-1],
                   retained_native_collection_entry=cfg['hooks']['M3CollectPickup'],
                   actual_assembled_maturation_zero_store=zero_store,
                   no_game_source_defect_established=True,
                   M3_growth_crouch_jump_SFX_and_completion_not_certified=True,
                   minimal_future_fixture_correction='Expect PowerUpType0 at mature$d1 collection. Keep all stamp/owner/maturity/coldsmall/47-growth and body controls. Requires separately reviewed preparation/grant; no retry performed.')
    put(O / 'mario3-first-failure.json', failure)
    sheet = Image.new('RGB', (4 * 256, 260), '#202020')
    draw = ImageDraw.Draw(sheet)
    for i, n in enumerate([568, 616, 672, 712]):
        p = f / 'frames' / (f'{n:06d}.png')
        image = Image.open(p).convert('RGB')
        assert image.size == (256, 240)
        sheet.paste(image, (i * 256, 0))
        draw.text((i * 256 + 3, 242), 'SMB3 ' + str(n), fill='white')
        selected.append(dict(identity='mario3', file=str(p), SHA256=sha(p)))
    sheet.save(O / 'mario3-selected4.png')
    put(O / 'selected-images.json', dict(selected_whole_PPU_frames=len(selected), files=selected,
                                       generation_only=True, visual_review_separately_recorded=True))
    paths = {P / 'native-proof.json', P / 'native-progress.json', P / 'launch.json', P / 'ROOT-grant.json',
             P / 'readiness.json', P / 'command.json', Path(__file__)}
    for name in ['mario', 'luigi', 'mario3']:
        folder = P / (name + '-easy')
        paths |= {p for p in folder.rglob('*') if p.is_file()}
    paths |= {p for p in O.iterdir() if p.is_file()}
    bindings = {str(p): sha(p) for p in sorted(paths, key=str)}
    proof = dict(packaging_passed=True, native_batch_passed=False, native_worker_released=True,
                 native_executed=True, native_launches=3, granted_maximum=4, retries=0,
                 stop_first_failure_honored=True, unrun=['luigi3-easy'],
                 ROM_sha256=ready['ROM_sha256'], original1006_bindings_unchanged=True,
                 passed_components=rows, retained_failure=failure,
                 selected_images_for_review=28, visual_review_not_automatic=True,
                 no_source_waveform_all_items_all_modes_or_full_route_claim=True,
                 bindings=bindings,
                 scope='Two passingEasy physical-mushroom components plus one preserved fixture-negative. All old readiness/source/native negatives remain; no source/runtime/settings/default/Git mutation or rerun.')
    put(O / 'proof.json', proof)
    print(json.dumps(dict(packaging_passed=True, native_batch_passed=False, launches=3, retries=0,
                          bindings=len(bindings), proof=str(O / 'proof.json'), SHA256=sha(O / 'proof.json')), indent=2))


if __name__ == '__main__':
    main()
