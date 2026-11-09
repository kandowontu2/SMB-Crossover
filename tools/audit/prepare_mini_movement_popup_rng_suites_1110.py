"""Rebind the four tested f003 Mini regression controllers to f518."""

import argparse
from pathlib import Path

import deliver_mini_helper_powered_injury_1110 as Prior
import prepare_mini_injury_helper_native_1110 as Hooks
import prepare_mini_movement_popup_rng_native_1110 as Batch
from deliver_helper_camera_render_1110 import bindings, read
from prepare_mini_lane_audio_native_1110 import verify_payload
from prepare_selected_native_packet_v1 import prepare, sha


R, PARENT, PREVIOUS = Batch.R,Batch.BASE,Batch.PIN
ROOT = R/'build/mini-movement-popup-rng-native-1110'
PIN = 'f5183f7ada374443222dc0b30a0777a8218aac154c04f84855d140245370daaa'
PROOF_SHA = '90084535e20a1e281464f5b9f3e56f1723539ed86e8d7de731f96f9a17989959'
INJURY = R/'build/mini-injury-status-v2-native-1110'
PACKETS = {**{name:PARENT.parent/'native'/name for name in ('idle','power','fire')},'injury':INJURY}


def stage(root, output):
    rom,proof = root/'candidate.nes',root/'proof.json'
    meta = rom.with_suffix('.json')
    manifest = read(meta)
    assert sha(rom)==manifest['candidate_SHA256']==PIN
    assert sha(proof)==manifest['composed_proof_SHA256']==PROOF_SHA
    assert manifest['kernel_SHA256']==sha(Batch.Movement.KERNEL)==Batch.Movement.KERNEL_PIN
    assert sha(PARENT)==PREVIOUS
    raw = rom.read_bytes()
    verify_payload(raw,Batch.Movement.KERNEL)
    verify_payload(PARENT.read_bytes(),Batch.Movement.KERNEL)
    for ext in ('.lbl','.dbg'):
        assert sha(rom.with_suffix(ext))==sha(PARENT.with_suffix(ext))

    with Prior.native_validators() as validation:
        validation.native_suite(PARENT.parent,PARENT)
    Prior.corrected_injury(INJURY,PARENT)
    plans = []
    for name,old in PACKETS.items():
        ready_path,controller_path = old/'ready.json',old/'controller.lua'
        result_path,binding_path = old/'capture/result.json',old/'capture/binding.json'
        ready = read(ready_path)
        assert ready['ROM_sha256']==PREVIOUS and Path(ready['ROM']).resolve()==PARENT.resolve()
        bindings(ready['bindings'])
        text = controller_path.read_text(encoding='utf-8')
        assert text.count(PREVIOUS)==1 and PIN not in text
        updated = text.replace(PREVIOUS,PIN,1)
        assert updated.replace(PIN,PREVIOUS,1)==text
        for physical,values in Hooks.PRG_HOOK.findall(updated):
            start = 16+int(physical)
            want = bytes(map(int,values.split(',')))
            assert raw[start:start+len(want)]==want,(name,hex(start),want.hex())
        refs = {Path(__file__),controller_path,ready_path,result_path,binding_path,proof,meta,
                Batch.Movement.KERNEL,Batch.Movement.KERNEL.with_suffix('.lbl'),*map(Path,ready['bindings'])}
        plans.append((name,updated,refs,ready))
    output.mkdir()
    for name,updated,refs,ready in plans:
        prepare(output/name,rom,updated,refs,expected=PIN,timeout=ready['timeout'],scope=ready['scope'],
                allow_interactive=ready['allow_interactive'])
    assert sum(path.is_file() for path in output.rglob('*'))==12


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--candidate',type=Path,default=ROOT)
    cli.add_argument('--output',type=Path,required=True)
    args = cli.parse_args()
    root,output = args.candidate.resolve(),args.output.resolve()
    assert output==root/'native' and not output.exists()
    stage(root,output)


if __name__=='__main__':
    main()
