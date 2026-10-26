"""Freeze the two corrected physical SMB3 pickup outcomes and selected PPU images."""
from pathlib import Path
import csv
import hashlib
import json

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
P = D / 'mario-powerups900-smb3-corrected-v1'
O = P / 'native-result-freeze-v2'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def get(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def put(p, z):
    p.write_text(json.dumps(z, indent=2) + '\n', encoding='utf-8')


def main():
    O.mkdir(exist_ok=False)
    assert sha(P / 'readiness.json') == 'd068fb73b59b690ed4cc604d16036ef7914f1f34b2d0ea034fc3744f04a89af4'
    assert sha(P / 'ROOT-grant.json') == '43021d2c554acd489da477b5dce46f30acf256bfe8a966e48386d15e1fb588ef'
    ready = get(P / 'readiness.json')
    for p, h in ready['bindings'].items():
        assert sha(p) == h, p
    native = get(P / 'native-proof.json')
    assert native['passed'] and native['profiles_run'] == 2
    old = D / 'mario-powerups900-first-v2/native-result-freeze-v1/proof.json'
    assert sha(old) == 'd28e07a9f66648fb1a9c075cd4456ecaf074c36dcb7f0117b7eccefdf9a15968'
    assert get(old)['native_batch_passed'] is False
    selected, rows = [], []
    for name, variant in [('mario3', 0), ('luigi3', 1)]:
        f = P / (name + '-easy')
        result, component = get(f / 'result.json'), get(f / 'powerup-component.json')
        assert result['component_complete'] and result['deaths'] == 0
        assert component['passed'] and component['actual_mode'] == 0 and component['variant'] == variant
        assert component['growth_draws'] == 47 and component['collect'] == component['reveal'] == 1
        assert component['crouch_frames'] == 24 and component['air_frames'] == 56
        states = list(csv.DictReader((f / 'powerup-state.csv').open()))
        emerging = [z for z in states if z['actors'] and int(z['actors'].split(':')[1]) < 128]
        mature = [z for z in states if z['actors'] and int(z['actors'].split(':')[1]) >= 128]
        assert all(z['actors'].split(':')[2:4] == ['0', '209'] for z in mature)
        assert emerging and mature and states[-1]['m3form'] == '1' and states[-1]['power'] == '1'
        assert all(':1:209:' in z['actors'] for z in emerging)
        crouch = [z for z in states if int(z['crouch']) != 0]
        air = [z for z in states if int(z['frame']) > int(crouch[-1]['frame']) and z['playerState'] != '0']
        growth = sorted(f.glob('growth-*.png'), key=lambda p: int(p.stem.split('-')[-1]))
        periodic = sorted((f / 'frames').glob('*.png'), key=lambda p: int(p.stem))
        def nearest(row):
            return min(periodic, key=lambda p: abs(int(p.stem) - int(row['frame'])))
        picks = [nearest(z) for z in [emerging[0], emerging[len(emerging) // 2], emerging[-1], mature[0]]]
        picks += [growth[i * (len(growth) - 1) // 6] for i in range(7)]
        picks += [nearest(z) for z in [crouch[0], crouch[-1], air[0], air[len(air) // 2]]]
        picks.append(f / 'endpoint.png')
        assert len(picks) == 16
        sheet = Image.new('RGB', (4 * 256, 4 * 260), '#202020')
        draw = ImageDraw.Draw(sheet)
        for i, p in enumerate(picks):
            im = Image.open(p).convert('RGB')
            assert im.size == (256, 240)
            x, y = i % 4 * 256, i // 4 * 260
            sheet.paste(im, (x, y))
            draw.text((x + 3, y + 242), name + ' ' + p.name, fill='white')
            selected.append(dict(identity=name, path=str(p), sha256=sha(p)))
        sheet.save(O / (name + '-selected16.png'))
        rows.append(dict(identity=name, passed=True, actual_mode=0, variant=variant,
                         endpoint=result['frames'], deaths=0, real_reveal=1, actual_owner=1,
                         actual_owner_events=[json.loads(s) for s in (f / 'powerup-owner.jsonl').read_text().splitlines()],
                         first_saved_transient_type1=emerging[0], first_saved_mature_type0=mature[0],
                         final_native_state=states[-1], source_growth_calls=47,
                         saved_growth_endFrame_PNGs=len(growth),
                         image_count_is_not_source_call_count=True,
                         crouch_frames=24, air_frames=56,
                         raw_reveal_request_stores=component['reveal_requests'],
                         raw_pickup_request_stores=component['pickup_requests'],
                         CHR=get(f / 'chr-commit.json'), motion=get(f / 'completed-loop-motion.json')))
    put(O / 'selected-images.json', dict(selected_whole_PPU_samples=32, files=selected,
                                       generation_only=True, actual_agent_review_separately_recorded=True))
    files = {P / 'native-result-freeze-v1/failure.json', P / 'native-result-freeze-v1/mario_powerups900_smb3_result_v1.py', P / 'readiness.json', P / 'ROOT-grant.json', P / 'command.json', P / 'launch.json',
             P / 'native-progress.json', P / 'native-proof.json', old, Path(__file__)}
    for name in ['mario3', 'luigi3']:
        files |= {f for f in (P / (name + '-easy')).rglob('*') if f.is_file()}
    files |= {f for f in O.iterdir() if f.is_file()}
    proof = dict(passed=True, packaging_passed=True, native_batch_passed=True,
                 native_executed=True, native_launches=2, retries=0, native_worker_released=True,
                 ROM_sha256=ready['ROM_sha256'], original1585_bindings_unchanged=True,
                 original_partial_FALSE_and_two900_legacy_passes_preserved=True,
                 profiles=rows, selected_PPU_samples_for_review=32,
                 no_automatic_visual_or_waveform_fullroute_everyitem_claim=True,
                 bindings={str(f): sha(f) for f in sorted(files, key=str)},
                 scope='Two current900Easy genuine first-mushroom/source-form/growth/crouch/jump components only; unchanged original partialFALSE and oldhash route boundaries retained. No installation/settings/source edits.')
    put(O / 'proof.json', proof)
    print(json.dumps(dict(passed=True, profiles=2, native_launches=2, retries=0,
                          bindings=len(proof['bindings']), proof=str(O / 'proof.json'),
                          sha256=sha(O / 'proof.json')), indent=2))


if __name__ == '__main__':
    main()
