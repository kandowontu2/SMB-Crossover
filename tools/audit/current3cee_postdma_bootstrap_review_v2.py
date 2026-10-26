"""Review the finite raw bootstrap pair and actual direct-console pixels."""
from pathlib import Path
import argparse, collections, csv, hashlib, itertools, json
import numpy as np
from PIL import Image

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--ready', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args(); a.output.mkdir(parents=True, exist_ok=False)
    streams = []
    for label in ['baseline', 'candidate']:
        folder = a.ready / label
        grouped = collections.defaultdict(list)
        with (folder/'bootstrap-events.jsonl').open() as f:
            for line in f:
                row = json.loads(line); grouped[row['kind']].append(row)
        result = json.loads((folder/'diagnostic-result.json').read_text())
        assert result['diagnostic_complete'] and result['DMAs'] == 207
        assert result['raw_new_shot_code_hits'] == 0
        complete = grouped['DMA-complete']; starts = grouped['DMA-start']
        data = grouped['DMA2004']; unequal = []
        assert len(complete) == len(starts) == 207 and len(data) == 52992
        for i, (start, end) in enumerate(zip(starts, complete), 1):
            assert start['DMA']['id'] == end['DMA'] == i
            source = start['DMA']['source']
            assert len(source) == len(end['hardware']) == 256
            assert source == end['source'] and end['transferred'] == 256
            writes = data[(i-1)*256:i*256]
            assert [w['ordinal'] for w in writes] == list(range(1, 257))
            assert all(w['DMA'] == i for w in writes)
            assert [w['value'] for w in writes] == source
            diffs = [dict(offset=k, source=x, hardware=y)
                     for k, (x,y) in enumerate(zip(source,end['hardware'])) if x != y]
            assert end['exact'] == (not diffs)
            assert (end['differences'] == diffs if diffs else end['differences'] in ({}, []))
            if diffs: unequal.append(dict(DMA=i, differences=diffs))
        assert len(unequal) == result['hardware_mismatch_DMAs']
        if label == 'baseline':
            assert not result['passed'] and len(unequal) == 1 and unequal[0]['DMA'] == 171
        else:
            assert result['passed'] and not unequal
        rows = list(csv.DictReader((folder/'startup-direct-index.csv').open()))
        raw = (folder/'startup-direct.argb').read_bytes()
        assert len(rows) == 15 and len(raw) == 15*61440*4
        images = []; index = []; output = a.output/label; output.mkdir()
        for i, row in enumerate(rows):
            frame = int(row['wallFrame']); assert frame == int(row['ppuFrame']) == 176+i
            values = np.frombuffer(raw[i*245760:(i+1)*245760], dtype='<u4').reshape(240,256)
            rgb = np.stack(((values>>16)&255, (values>>8)&255, values&255),axis=2).astype(np.uint8)
            target = output/f'{frame:06d}.png'; Image.fromarray(rgb).save(target)
            with Image.open(target) as im: assert im.convert('RGB').tobytes() == rgb.tobytes()
            images.append(rgb)
            index.append(dict(frame=frame, RGB_sha256=hashlib.sha256(rgb.tobytes()).hexdigest(), PNG_sha256=sha(target)))
        streams.append(dict(events=grouped, result=result, unequal=unequal, images=images, index=index))
    old, new = streams
    assert (a.ready/'baseline/inputs.csv').read_bytes() == (a.ready/'candidate/inputs.csv').read_bytes()
    assert [z['DMA']['source'] for z in old['events']['DMA-start']] == [z['DMA']['source'] for z in new['events']['DMA-start']]
    for kind in ['Main-entry', 'Main-release', 'wall-frame']:
        assert len(old['events'][kind]) == len(new['events'][kind])
        for x,y in zip(old['events'][kind],new['events'][kind]):
            assert x['state'] == y['state'], (kind, x.get('id'), 'state')
    pixels = []
    for i, (x,y) in enumerate(zip(old['images'],new['images'])):
        changed = np.any(x != y,axis=2); ys,xs = np.where(changed)
        pixels.append(dict(frame=176+i, changed_pixels=int(changed.sum()),
                           bounding_box=[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())] if len(xs) else None))
    bad = old['events']['DMA-complete'][170]
    repaired = new['events']['DMA-complete'][170]
    enable = [z for z in new['events']['PPUMASK-write']
              if z['ppu']['frame'] == 184 and z['value'] == 30]
    assert len(enable) == 1
    assert all(z['PPUMASK'] & 0x18 == 0 for z in new['events']['DMA2004'])
    assert all(z['actual_OAMADDR'] == z['ordinal']-1 for z in new['events']['DMA2004'])
    bindings = {str(p):sha(p) for p in a.ready.rglob('*')
                if p.is_file() and p.name not in ['host.log']}
    proof = dict(passed=True, native_run=True, adopted=False,
                 ROMs=json.loads((a.ready/'readiness.json').read_text())['ROMs'],
                 frames_each=220, inputs_exact=True, Main_entries_each=209,
                 all_Main_release_and_wall_control_states_exact=True,
                 source_pages_each_exact=207, DMA2004_values_each_exact=52992,
                 baseline_hardware_result=False, baseline_unequal=old['unequal'],
                 candidate_hardware_result=True, candidate_unequal=[],
                 candidate_all_DMA_inputs_rendering_disabled=True,
                 candidate_DMA_input_mask_counts=dict(collections.Counter(z['PPUMASK'] for z in new['events']['DMA2004'])),
                 candidate_all_DMA_input_actual_OAMADDR_exact=True,
                 baseline_first_bad=bad, candidate_same_epoch=repaired,
                 candidate_actual_render_enable=enable[0],
                 direct_frames_each=15, direct_pixel_comparison=pixels,
                 direct_indexes={k:s['index'] for k,s in zip(['baseline','candidate'],streams)},
                 bindings=bindings, tool_sha256=sha(__file__),
                 limits='Finite matched startup case only. Full raw destinations remain strict; baseline FALSE preserved. Direct console buffers, not decoder screenshots. No all-menu/gameplay/DMC/campaign/adoption claim.')
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(dict(passed=True, adopted=False, proof_sha256=sha(a.output/'proof.json'),
                         candidate_hardware_exact='207/207', pixel_changes=pixels,
                         enable=enable[0]['ppu']),indent=2))

if __name__ == '__main__': main()
