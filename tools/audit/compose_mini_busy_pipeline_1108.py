"""Rebase disjoint, tested busy-frame optimizations on the delivered nightly."""
import argparse
import json
from pathlib import Path
import shutil

from check_mini_native_side_dispatch_1108 import BASE, PIN, R, sha
from compose_mini_frame_budget_1108 import check_full_cpu, compose, load

SIDE = R/'build/mini-native-side-dispatch-rom-1108/proof.json'
SIDE_IRQ = R/'build/mini-side-dispatch-irq-1108/proof.json'
TANK = R/'build/mini-side-tank-candidate-v2-1108/capture'
AUDIO = R/'build/mini-audio-transport-1108-v4/result.json'
AUDIO_IRQ = AUDIO.with_name('irq.json')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--patch-proof',type=Path,action='append',default=[])
    args=parser.parse_args()
    assert sha(BASE)==PIN
    side,audio,side_irq,audio_irq=(load(path) for path in (SIDE,AUDIO,SIDE_IRQ,AUDIO_IRQ))
    assert side_irq['passed'] and side_irq['ROM_SHA256']==side['expected_memory_only_SHA256']
    assert audio_irq['passed'] and audio_irq['image_SHA256']==audio['expected_memory_only_SHA256']
    assert audio_irq['proof_SHA256']==sha(AUDIO)
    assert load(TANK/'binding.json')['ROM_sha256']==side_irq['ROM_SHA256']
    assert load(TANK/'binding.json')['exit_code']==0 and load(TANK/'result.json')['passed']
    assert 'TANK_SIDE 708' in (TANK/'candidate-controller.log').read_text()
    parent=BASE.read_bytes()
    candidate=bytearray(parent)
    for path in (SIDE,AUDIO,*args.patch_proof):
        compose(parent,candidate,load(path),parent=PIN)
    assert candidate[1048592:]==parent[1048592:]
    manifest=load(BASE.with_suffix('.json'))
    rows=check_full_cpu(parent,candidate,{})
    args.output.mkdir()
    rom=args.output/'candidate.nes'
    rom.write_bytes(candidate)
    for suffix in ('.lbl','.dbg'):
        shutil.copyfile(BASE.with_suffix(suffix),rom.with_suffix(suffix))
    manifest.update(parent_SHA256=PIN,candidate_SHA256=sha(rom),busy_pipeline_CPU=rows,
                    busy_pipeline_proofs={str(path):sha(path) for path in (SIDE,SIDE_IRQ,AUDIO,AUDIO_IRQ,*args.patch_proof)})
    (args.output/'candidate.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(dict(candidate_SHA256=sha(rom),busy_pipeline_CPU=rows)))


if __name__=='__main__':
    main()
