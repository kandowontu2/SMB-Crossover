"""Verify one exact0a Mega/ProtoHard native unit and bind actual whole images."""
from pathlib import Path
import argparse
import collections
import csv
import hashlib
import json
from PIL import Image, ImageDraw

R = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
BASE = D / 'mm-proto-weapon-boundary-v1/native-ready-v3'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--profile', required=True, type=Path)
    args = parser.parse_args()
    base = args.profile.resolve()
    out = args.output.resolve()
    assert not out.is_relative_to(R)
    out.mkdir(parents=True, exist_ok=False)
    ready = json.loads((base / 'readiness.json').read_text())
    assert ready['ROM_sha256'] == '0a7dd88e6732bc189e432a9d55b18dd8f7ecf68a22e3b20f0a13ab7276241c09'
    variant = ready['identity']['variant']
    assert json.loads((base / 'launch-binding-v1.json').read_text())['native_grant_explicit']
    bindings = json.loads((base / 'bindings.json').read_text())
    assert len(bindings) == 903
    for path, digest in bindings.items():
        assert sha(path) == digest, path
    launch = json.loads((base / 'launch-outcome-v1.json').read_text())
    assert launch['returncode'] == 0 and launch['attempt'] == 1 and launch['no_retry']
    native = base / 'native'
    assert not (native / 'first-failure.json').exists()
    result = json.loads((native / 'native-mm-weapon-profile.json').read_text())
    assert result['passed'] and result['actual_mode_readback'] == 1
    assert result['hard'] and not result['acquisition'] and not result['goal_complete']
    assert result['updates'] == 656 and len(result['cases']) == 6
    cases = result['cases']
    for q, expected, charges in zip(cases[:3], [[1], [1, 2], [1, 3]], [[0], [0, 56], [0, 87]]):
        assert [s['type'] for s in q['primarySpawns']] == expected
        assert [s['charge'] for s in q['primarySpawns']] == charges
        assert q['finalAmmo'] == q['beforeAmmo'] == [0] * 7 + [20]
    rush, gate, balance = cases[3:]
    assert rush['summoned'] and rush['existingAttack'] and rush['rushDraws'] == 122
    assert rush['landed'] == 479 and rush['bounced'] == rush['launch'] == 499
    assert rush['finalAmmo'] == [0] * 7 + [8] and rush['completed'] == 570
    assert gate['refused'] and gate['beforeAmmo'] == gate['finalAmmo'] == [0] * 7 + [3]
    assert balance['balanceChoice'] and balance['refillCredits'] == 8
    assert balance['beforeAmmo'] == [60, 4, 0, 0, 0, 0, 0, 8]
    assert balance['finalAmmo'] == [60, 12, 0, 0, 0, 0, 0, 8]
    events = [json.loads(line) for line in (native / 'events.jsonl').read_text().splitlines()]
    event_counts = collections.Counter(q['kind'] for q in events)
    assert event_counts['mm-weapon-component-complete'] == 6
    assert event_counts['actual-rush-direct-debit'] == 1
    assert event_counts['actual-mm-balancer-credit'] == 2
    epochs = [json.loads(line) for line in (native / 'ability-dma-epochs.jsonl').read_text().splitlines()]
    epoch_counts = collections.Counter(q['kind'] for q in epochs)
    completed = [q for q in epochs if q['kind'] == 'completed-DMA-before-render-enable']
    for q in completed:
        assert q['source'] == q['hardware'] and len(q['source']) == 256
        assert not q['differences'] and len(q['writes']) == 256
        assert q['page'] == 2 and q['start']['oamaddr'] == q['complete']['oamaddr'] == 0
        assert q['start']['mask'] & 24 == q['complete']['mask'] & 24 == 0
        for i, write in enumerate(q['writes']):
            assert write['value'] == q['source'][i] and write['stamp']['oamaddr'] == i
            assert write['stamp']['mask'] & 24 == 0
    enables = [q for q in epochs if q['kind'] == 'actual-PPUMASK-write' and q['scoped'] and q['enabling']]
    assert completed and enables and all(q['safe'] for q in enables)
    pixels = (native / 'actual-ppu.argb').read_bytes()
    frames = list(csv.DictReader((native / 'actual-ppu-index.csv').open(newline='')))
    capture = json.loads((native / 'ppu-capture-native-result.json').read_text())
    size = 256 * 240 * 4
    assert len(pixels) == len(frames) * size == capture['bytes']
    assert len(frames) == capture['frames'] and capture['original_done_seen']
    by_hash = collections.defaultdict(list)
    for i, row in enumerate(frames):
        assert int(row['ordinal']) == i + 1 and int(row['mode']) in (0, 1)
        if int(row['mode']) == 0:
            assert int(row['updates']) == 0 and row['phase'] == 'menu'
        by_hash[hashlib.sha256(pixels[i * size:(i + 1) * size]).hexdigest()].append(row)
    samples = []
    groups = collections.defaultdict(list)
    raw_bindings = {str(path): sha(path) for path in native.iterdir() if path.is_file()}
    # A colon in native art names is a Windows alternate stream. Read and bind it
    # explicitly; the whole completed-PPU stream remains the independent oracle.
    for event in events:
        if event['kind'] != 'ppu-frame-captured':
            continue
        name = event['data']['name']
        path = native / (name + '.argb')
        raw = path.read_bytes()
        digest = sha(path)
        assert len(raw) == size and digest in by_hash, name
        raw_bindings[str(path)] = digest
        matched = by_hash[digest]
        actual = [q for q in matched if int(q['ppu_frame']) == event['wall']]
        assert actual, (name, event, matched)
        clean_name = name.replace(':', '-')
        image = Image.frombytes('RGBA', (256, 240), raw, 'raw', 'BGRA').convert('RGB')
        image.save(out / (clean_name + '.png'))
        sample = dict(name=name, source=str(path), sha256=digest,
                      actual_event=event, actual_ppu_matches=matched,
                      PNG_sha256=sha(out / (clean_name + '.png')))
        samples.append(sample)
        group = 'primary' if name.startswith(('basic-', 'weak-', 'full-')) else 'support'
        groups[group].append((sample, image))
    for group, items in groups.items():
        sheet = Image.new('RGB', (3 * 512, ((len(items) + 2) // 3) * 508), '#151923')
        draw = ImageDraw.Draw(sheet)
        for i, (sample, image) in enumerate(items):
            x, y = (i % 3) * 512, (i // 3) * 508
            sheet.paste(image.resize((512, 480), Image.Resampling.NEAREST), (x, y + 28))
            draw.text((x + 6, y + 5), sample['name'] + ' | PPU ' + str(sample['actual_event']['wall']), fill='white')
        sheet.save(out / (group + '-actual-whole-images.png'), optimize=True)
    (out / 'samples.json').write_text(json.dumps(samples, indent=2) + '\n')
    raw_bindings.update({str(base / name): sha(base / name) for name in
                         ['launch-binding-v1.json', 'launch-outcome-v1.json',
                          'readiness.json', 'bindings.json', 'command.json']})
    (out / 'external-raw-manifest.json').write_text(json.dumps(raw_bindings, indent=2, sort_keys=True) + '\n')
    proof = dict(passed=True, offline_verification=True, native_launches=1, retries=0,
                 ROM_sha256=ready['ROM_sha256'],
                 actual_mode=1, variant=variant, facing=1, tier=1, staged_not_acquisition=True,
                 cases=cases, updates=result['updates'], nmis=result['nmis'], minSP=result['minSP'],
                 post_publication_DMA_checks=result['complete_dma_checks'],
                 hardware_CHR_checks=result['hardware_chr_checks'], IRQ31_stores=result['irq_scroll_stores'],
                 APU_including_DMA_controller=result['apuWrites_includingDMAController'],
                 allmode_physical_DMA_pages=len(completed), independently_checked_DMA_writes=256 * len(completed),
                 allmode_epoch_counts=dict(epoch_counts), event_counts=dict(event_counts),
                 scoped_safe_render_enables=len(enables), actual_PPU_frames=len(frames),
                 actual_PPU_bytes=len(pixels), actual_whole_image_samples=len(samples), source_profile=str(base), source_profile_readiness_sha256=sha(base/'readiness.json'),
                 raw_manifest_sha256=sha(out / 'external-raw-manifest.json'),
                 sample_manifest_sha256=sha(out / 'samples.json'), agent_visual_review_pending=True,
                 limits='One staged selected Mega/ProtoHard tier1/right-facing native-boundary unit. No natural acquisition, actual enemy/block damage, Easy/tier2 native, full pool, every weapon, both facings, matched performance, soundtrack listening or universal visual acceptance. NMI assertions cover A/SP, not all AXY. Source-time event pictures can precede a newly requested publication. All sample pictures are bound to the original whole completed-PPU stream. Native art capture names with colons used Windows alternate streams and are bound explicitly; public names are sanitized. Startup uninitialized-read diagnostics remain in original emulator log.',
                 tool_sha256=sha(__file__))
    # Consecutive completed PPU images are the presentation oracle for the
    # Rush source-time capture labels; they can precede a new publication.
    land_wall = next(z['actual_event']['wall'] for z in samples if z['name'] == 'rush-lifecycle-landed')
    wanted = list(range(land_wall-3, land_wall+33))
    by_frame = {int(z['ppu_frame']):i for i,z in enumerate(frames)}
    consecutive = Image.new('RGB', (1024, 260*((len(wanted)+3)//4)), '#151923')
    draw = ImageDraw.Draw(consecutive)
    consecutive_bindings = []
    for j,n in enumerate(wanted):
        i = by_frame[n];raw = pixels[i*size:(i+1)*size]
        image = Image.frombytes('RGBA',(256,240),raw,'raw','BGRA').convert('RGB')
        x,y = j%4*256,j//4*260
        consecutive.paste(image,(x,y+20));draw.text((x,y),f'variant{variant} actual PPU {n}',fill='white')
        consecutive_bindings.append(dict(actual_frame=n,index_row=frames[i],raw_sha256=hashlib.sha256(raw).hexdigest()))
    consecutive.save(out/'rush-consecutive-actual-PPU.png',optimize=True)
    (out/'rush-consecutive-bindings.json').write_text(json.dumps(consecutive_bindings,indent=2)+'\n')
    proof['rush_consecutive_bindings_sha256']=sha(out/'rush-consecutive-bindings.json')
    proof['rush_consecutive_sheet_sha256']=sha(out/'rush-consecutive-actual-PPU.png')
    proof['rush_consecutive_completed_PPU_images']=len(wanted)
    (out / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps(proof, indent=2))


if __name__ == '__main__':
    main()
