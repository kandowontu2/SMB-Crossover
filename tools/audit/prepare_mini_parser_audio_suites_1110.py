"""Rebind the four passing 863e Mini tests to the exact parser/audio ROM."""

import argparse
from pathlib import Path

from deliver_helper_camera_render_1110 import bindings, read
import prepare_mini_injury_helper_native_1110 as Hooks
import prepare_mini_parser_audio_native_1110 as Batch
from prepare_mini_lane_audio_native_1110 import verify_payload
from prepare_selected_native_packet_v1 import prepare, sha


R, PREVIOUS = Batch.R,Batch.PIN
ROOT = R/'build/mini-parser-audio-native-1110'
PIN = '3a3832825bc6a2628fef7b3ccc3e760262510b86a80d78bc74ec3005af3119df'
PROOF_SHA = '3441db7e094d0aa5a843928f67a15fff2c92a740ad0ebf2b18e4e1cd5e2edf0c'
BASE, PARENT = Batch.BASE,Batch.Local.PARENT_PACKETS
PARENT_VALIDATORS = Batch.Local.MarginDelivery
KERNEL = Batch.Local.Margin.Seven.KERNEL
PACKETS = ('idle','power','fire','injury')


def bind_candidate(root):
    rom,proof = root/'candidate.nes',root/'proof.json'
    manifest = rom.with_suffix('.json')
    meta,receipt = read(manifest),read(proof)
    raw = rom.read_bytes()
    assert sha(rom)==meta['candidate_SHA256']==receipt['candidate_SHA256']==PIN
    assert sha(proof)==meta['composed_proof_SHA256']==PROOF_SHA and receipt['passed']
    assert meta['parent_SHA256']==receipt['parent_SHA256']==PREVIOUS==sha(BASE)
    assert set(receipt['groups'])==set(receipt['final_minus_SHA256'])==set(Batch.ROLES)
    assert sha(KERNEL)==receipt['kernel_SHA256']==meta['kernel_SHA256']
    bindings(receipt['bindings'])
    verify_payload(raw,KERNEL)
    verify_payload(BASE.read_bytes(),KERNEL)
    for ext in ('.lbl','.dbg'):
        assert sha(rom.with_suffix(ext))==sha(BASE.with_suffix(ext))
    return rom,raw,proof,manifest


def plan(raw, name):
    old = PARENT/'native'/name
    ready_path,controller_path = old/'ready.json',old/'controller.lua'
    ready = read(ready_path)
    assert ready['ROM_sha256']==PREVIOUS and Path(ready['ROM']).resolve()==BASE.resolve()
    bindings(ready['bindings'])
    source = controller_path.read_text(encoding='utf-8')
    assert source.count(PREVIOUS)==1 and PIN not in source
    updated = source.replace(PREVIOUS,PIN,1)
    for physical,values in Hooks.PRG_HOOK.findall(updated):
        start = 16+int(physical)
        want = bytes(map(int,values.split(',')))
        assert raw[start:start+len(want)]==want,(name,hex(start),want.hex())
    refs = {Path(__file__),controller_path,ready_path,old/'capture/result.json',old/'capture/binding.json',
            KERNEL,KERNEL.with_suffix('.lbl'),*map(Path,ready['bindings'])}
    return updated,refs,ready


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--candidate',type=Path,default=ROOT)
    cli.add_argument('--output',type=Path,required=True)
    args = cli.parse_args()
    root,out = args.candidate.resolve(),args.output.resolve()
    assert out==root/'native' and not out.exists()
    rom,raw,proof,manifest = bind_candidate(root)
    with PARENT_VALIDATORS.validators() as validation:
        validation.native_suite(PARENT,BASE)
        PARENT_VALIDATORS.Prior.corrected_injury(PARENT/'native/injury',BASE)
    plans = {name:plan(raw,name) for name in PACKETS}
    out.mkdir()
    for name,(text,refs,ready) in plans.items():
        prepare(out/name,rom,text,refs|{proof,manifest},expected=PIN,timeout=ready['timeout'],
                scope=ready['scope'],allow_interactive=ready['allow_interactive'])
    assert sum(path.is_file() for path in out.rglob('*'))==12


if __name__=='__main__':
    main()
