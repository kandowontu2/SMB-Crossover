"""Offline verification of the single granted3b ARM/question native control."""
from pathlib import Path
import argparse
import collections
import csv
import hashlib
import json
from PIL import Image, ImageDraw

R = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
BASE = D/'bass-arm-question-boundary-v1/native-ready-v3'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    assert not a.output.resolve().is_relative_to(R)
    a.output.mkdir(parents=True, exist_ok=False)
    native = BASE/'native'
    assert sha(BASE/'readiness.json') == '72147685d2c120b799a442d407d2519944c6f3c20d2b927f4ce8ff9224849364'
    assert sha(BASE/'ROOT-native-grant.json') == 'c27d2779570bb888538151895b3987a6aab2262880b10b47c63ecf55828bb786'
    for name, h in json.loads((BASE/'bindings.json').read_text()).items():
        assert sha(name) == h, name
    launch = json.loads((BASE/'launch-outcome.json').read_text())
    assert launch['returncode'] == 0 and launch['native_attempts'] == 1 and launch['retries'] == 0
    assert not (native/'first-failure.json').exists()
    outcome = json.loads((native/'native-bass-gallery.json').read_text())
    assert outcome['passed'] and not outcome['acquisition'] and not outcome['goal_complete']
    assert outcome['actual_mode_readback'] == 0 and len(outcome['cases']) == 1
    case = outcome['cases'][0]
    assert case['selected'] and case['lifted'] and case['used']
    assert case['throws'] == case['heads'] == case['blockReturns'] == 1
    assert case['fragments'] == 4 and case['continuedUpdates'] == 250
    assert case['rewardStamp'] == {'stamp': 8, 'update': 76, 'slot': 5}
    assert case['mature'] - case['revealed'] == 47
    assert outcome['updates'] == 320

    events = [json.loads(s) for s in (native/'events.jsonl').read_text().splitlines()]
    created = [q for q in events if q['kind'] == 'actual-question-reward-created']
    assert len(created) == 1 and created[0]['data']['y'] == 136
    assert len([q for q in events if q['kind'] == 'arm-question-regression-complete']) == 1
    epochs = [json.loads(s) for s in (native/'ability-dma-epochs.jsonl').read_text().splitlines()]
    counts = collections.Counter(q['kind'] for q in epochs)
    completed = [q for q in epochs if q['kind'] == 'completed-DMA-before-render-enable']
    assert completed
    for q in completed:
        assert q['source'] == q['hardware'] and len(q['source']) == 256
        assert not q['differences'] and len(q['writes']) == 256
        assert q['page'] == 2 and q['start']['oamaddr'] == q['complete']['oamaddr'] == 0
        assert q['start']['mask'] & 24 == q['complete']['mask'] & 24 == 0
        for i, w in enumerate(q['writes']):
            assert w['value'] == q['source'][i] and w['stamp']['oamaddr'] == i
            assert w['stamp']['mask'] & 24 == 0
    enables = [q for q in epochs if q['kind'] == 'actual-PPUMASK-write' and q['scoped'] and q['enabling']]
    assert enables and all(q['safe'] for q in enables)

    pixels = (native/'actual-ppu.argb').read_bytes()
    frames = list(csv.DictReader((native/'actual-ppu-index.csv').open(newline='')))
    capture = json.loads((native/'ppu-capture-native-result.json').read_text())
    size = 256*240*4
    assert len(pixels) == len(frames)*size == capture['bytes']
    assert len(frames) == capture['frames'] == 666
    by_hash = collections.defaultdict(list)
    for i, row in enumerate(frames):
        assert int(row['ordinal']) == i+1 and int(row['mode']) == 0
        by_hash[hashlib.sha256(pixels[i*size:(i+1)*size]).hexdigest()].append(row)
    names = ['setup', 'held', 'throw', 'contact', 'four-fragments', 'reveal', 'mature', 'complete']
    sheet = Image.new('RGB', (1024, 4*514), '#151923')
    draw = ImageDraw.Draw(sheet)
    samples = []
    for i, name in enumerate(names):
        path = native/('arm-question-'+name+'.argb')
        raw = path.read_bytes()
        assert len(raw) == size and sha(path) in by_hash
        image = Image.frombytes('RGBA', (256, 240), raw, 'raw', 'BGRA').convert('RGB')
        image.save(a.output/(name+'.png'))
        x, y = (i % 2)*512, (i // 2)*514
        sheet.paste(image.resize((512, 480), Image.Resampling.NEAREST), (x, y+32))
        matches = by_hash[sha(path)]
        draw.text((x+8, y+8), name+' | actual PPU '+','.join(q['ppu_frame'] for q in matches[:5]), fill='white')
        samples.append(dict(name=name, source=str(path), sha256=sha(path),
                            actual_ppu_matches=matches, PNG_sha256=sha(a.output/(name+'.png'))))
    sheet.save(a.output/'actual-stages.png')
    (a.output/'samples.json').write_text(json.dumps(samples, indent=2)+'\n')
    proof = dict(passed=True, offline_review=True, native_launches=1, retries=0,
        ROM_sha256='3b112e1d79ba7348f2f7a4c426f4675845a5781017ab74690feb235121a66287',
        actual_mode=0, initialized_scene_not_acquisition=True, observed_case=case,
        actual_updates=outcome['updates'], actual_NMIs=outcome['nmis'], minSP=outcome['minSP'],
        native_post_publication_DMA_checks=outcome['complete_dma_checks'],
        native_CHR_checks=outcome['hardware_chr_checks'], native_IRQ_scroll_stores=outcome['irq_scroll_stores'],
        APU_including_DMA_controller_writes=outcome['apuWrites_includingDMAController'],
        allmode_physical_DMA_completions=len(completed), independently_checked_DMA_data_writes=256*len(completed),
        allmode_epoch_rows=dict(counts), scoped_safe_render_enables=len(enables),
        actual_PPU_frames=len(frames), actual_PPU_bytes=len(pixels),
        eight_actual_stage_samples_bound=True, agent_visual_review_pending=True,
        limits='One configured powered BassEasy/right-facing ARM native-boundary control. Initial scene/tier/ownership/stock are declared; no natural acquisition, other modes/facings/pages/resources, global freeze absence, full gallery, audio listening or matched performance claim. Native NMI assertion covers A/SP, not all AXY. Source seven-player-field assertions passed at the one native Blocks return. Capture/strict guard pass is not universal visual acceptance.',
        tool_sha256=sha(__file__))
    (a.output/'proof.json').write_text(json.dumps(proof, indent=2)+'\n')
    print(json.dumps(proof, indent=2))


if __name__ == '__main__':
    main()
