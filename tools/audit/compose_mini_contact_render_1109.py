"""Apply independently verified collision and draw paths to the current nightly."""

import argparse
import json
from pathlib import Path
import shutil

from compose_mini_frame_budget_1108 import check_full_cpu, compose, digest, load
from qualify_mini_busy_1109 import BASE, PIN, ROOT, run_suite
from prepare_selected_native_packet_v1 import sha


CURRENT = ROOT/'build/mini-columns-transport-1109/candidate.nes'
CURRENT_PIN = 'ee9b3f55e010f7673a046e6dbc20b220b13cd83dcc95f95c799e6f9def565f6b'
COLLISION = ROOT/'build/mini-native-side-single-map-1109'
RENDER = ROOT/'build/mini-render-bookkeeping-1109-v1'
KERNEL = ROOT/'build/mini-kernel-transport-1109/v2/kernel.bin'


def build(output, typed=False):
    old, current = BASE.read_bytes(), CURRENT.read_bytes()
    assert digest(old) == PIN and digest(current) == CURRENT_PIN
    candidate, collision = bytearray(current), bytearray(old)
    refs = []
    for name in ('proof.json','head-proof.json'):
        path = COLLISION/name
        for rom in (candidate,collision):
            compose(old,rom,load(path),parent=PIN)
        refs.append(path)
    path = COLLISION/'async-proof.json'
    irq = load(path)
    assert irq['passed'] and irq['include_head'] and irq['parent_SHA256'] == PIN
    assert irq['memory_only_SHA256'] == digest(collision)
    refs.append(path)

    path, vector_path = (RENDER/name for name in ('measurement.json','actual-vectors.json'))
    measured, irq = load(path), load(vector_path)
    assert irq['passed'] and irq['base_SHA256'] == PIN and irq['bindings'][str(path)] == sha(path)
    assert irq['memory_only_SHA256'] == measured['memory_only_SHA256']
    render_proof = dict(measured,patches=[measured['patch']],
                        expected_memory_only_SHA256=measured['memory_only_SHA256'])
    compose(old,candidate,render_proof,parent=PIN)
    refs.extend((path,vector_path))
    if typed:
        typed_path, typed_vectors = (RENDER/name for name in ('typed-goomba.json','typed-goomba-current-vectors.json'))
        measured, irq = load(typed_path), load(typed_vectors)
        proof = dict(measured,patches=[measured['patch']],expected_memory_only_SHA256=measured['memory_only_SHA256'])
        independently_tested = bytearray(current)
        compose(old,independently_tested,render_proof,parent=PIN)
        compose(old,independently_tested,proof,parent=PIN)
        assert irq['passed'] and irq['memory_only_SHA256'] == digest(independently_tested)
        compose(old,candidate,proof,parent=PIN)
        refs.extend((typed_path,typed_vectors))

    rows = check_full_cpu(current,candidate,{})
    assert all(row['min_saved'] >= 0 for row in rows),rows
    output.mkdir()
    rom = output/'candidate.nes'
    rom.write_bytes(candidate)
    for ext in ('.dbg','.lbl'):
        shutil.copyfile(CURRENT.with_suffix(ext),rom.with_suffix(ext))
    metadata = load(CURRENT.with_suffix('.json'))
    metadata.update(candidate_SHA256=sha(rom),parent_SHA256=CURRENT_PIN,whole_GameCore=rows,
                    contact_render_proofs={str(p):sha(p) for p in refs})
    rom.with_suffix('.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print(json.dumps(dict(ROM_SHA256=sha(rom),whole_GameCore=rows)),flush=True)
    return rom


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    cli.add_argument('--test',action='store_true')
    cli.add_argument('--typed',action='store_true')
    args = cli.parse_args()
    rom = build(args.output,args.typed)
    if args.test:
        run_suite(args.output/'native',rom,KERNEL,('route','idle','power'))
        run_suite(args.output/'native',rom,None,('fire',))


if __name__ == '__main__':
    main()
