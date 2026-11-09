"""Rebind the four passing df03 focused replays to the exact c8bd candidate."""

import argparse
from pathlib import Path
import re

from deliver_helper_camera_render_1110 import bindings, read
from prepare_mini_lane_audio_native_1110 import verify_payload, without_component
import prepare_mini_contact_platform_combo_native_1110 as Batch
from prepare_selected_native_packet_v1 import prepare, sha


R, Stage = Batch.R,Batch.Stage
ROOT = R/'build/mini-contact-platform-combo-native-1110'
PARENT = Batch.TRIPLE
PIN = 'c8bd2e2c75015b84fe7bc3c4dba5b24b87e517620ef914ff229b5d4249acbe48'
PROOF_SHA = '9bb145df9aff1a33107d5e49bfc4fad1935df8f29fea3cf01f5baddebf556916'
TIMING_SHA = '073139fe0b9b5880737a58ffdcac15d24a523500371545cc4fe012130ab48e58'
PACKETS = ('idle','power','fire','injury')
HOOK = re.compile(r'\["physical"\]=(\d+),\["memory"\]="(nes\w+)",\["bytes"\]=\{([\d,]+)\}')
CHR = 1048592
FIRE_WRAM = 2*8192+(0xd239&8191)
FIRE_WRAPPER = CHR+967*1024+(0xd239&1023)


def candidate(root):
    rom,proof_path = root/'candidate.nes',root/'proof.json'
    manifest = rom.with_suffix('.json')
    proof,meta = read(proof_path),read(manifest)
    raw,parent = rom.read_bytes(),(PARENT/'candidate.nes').read_bytes()
    assert sha(rom)==proof['candidate_SHA256']==meta['candidate_SHA256']==PIN
    assert sha(proof_path)==meta['composed_proof_SHA256']==PROOF_SHA and proof['passed']
    assert Batch.Contact.P.sha(parent)==Batch.TRIPLE_PIN
    assert proof['final_minus_SHA256'][Batch.ROLE]==proof['intermediate_native_SHA256']==Batch.TRIPLE_PIN
    assert without_component(raw,Batch.CONTACT_ROOT/'proof.json')==parent
    assert sha(Stage.KERNEL)==proof['kernel_SHA256']==meta['kernel_SHA256']
    for image in (raw,parent):
        verify_payload(image,Stage.KERNEL)
    assert raw[CHR:]==parent[CHR:]
    for ext in ('.lbl','.dbg'):
        assert sha(rom.with_suffix(ext))==sha((PARENT/'candidate.nes').with_suffix(ext))
    bindings(proof['bindings'])
    with Stage.Delivery.validators(PIN) as validation:
        route = validation.route_evidence(root/'mini')
    timing = root/'mini/capture/timing.json'
    assert sha(timing)==TIMING_SHA and route['cadence']==dict(lag_nmi=0,physical=3494,updates=3494,zero_update=0)
    assert read(timing)['interrupts']['lag_nmi']['calls']==70
    return rom,raw,{proof_path,manifest,timing,root/'mini/capture/binding.json',root/'mini/capture/result.json'}


def plan(raw,name):
    old = PARENT/'native'/name
    ready_path,controller = old/'ready.json',old/'controller.lua'
    ready,source = read(ready_path),controller.read_text(encoding='utf-8')
    assert ready['ROM_sha256']==Batch.TRIPLE_PIN and not ready['emulated_writes']
    assert Path(ready['ROM']).resolve()==(PARENT/'candidate.nes').resolve()
    bindings(ready['bindings'])
    assert source.count(Batch.TRIPLE_PIN)==1 and PIN not in source
    kernel = Stage.KERNEL.read_bytes()
    hooks = HOOK.findall(source)
    assert hooks and any(space=='nesWorkRam' for _,space,_ in hooks)
    for physical,space,values in hooks:
        offset = int(physical)
        want = bytes(map(int,values.split(',')))
        if space=='nesPrgRom':
            at,base = 16+offset,raw
        elif name=='fire' and offset==FIRE_WRAM:
            at,base = FIRE_WRAPPER,raw
        else:
            assert space=='nesWorkRam' and 0x6000<=offset<0x6000+len(kernel)
            at,base = offset-0x6000,kernel
        assert base[at:at+len(want)]==want,(name,space,hex(offset),want.hex())
    refs = {Path(__file__),controller,ready_path,old/'capture/result.json',old/'capture/binding.json',
            Stage.KERNEL,Stage.KERNEL.with_suffix('.lbl'),*map(Path,ready['bindings'])}
    return source.replace(Batch.TRIPLE_PIN,PIN,1),refs,ready


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--candidate',type=Path,default=ROOT)
    cli.add_argument('--output',type=Path,required=True)
    args = cli.parse_args()
    root,out = args.candidate.resolve(),args.output.resolve()
    assert out==root/'native' and not out.exists()
    rom,raw,refs = candidate(root)
    nightly = Stage.Delivery.NIGHTLY
    assert nightly.check(nightly.D)['ROM_sha256']==Batch.TRIPLE_PIN
    with Stage.Delivery.validators(Batch.TRIPLE_PIN) as validation:
        validation.native_suite(PARENT,PARENT/'candidate.nes')
        Stage.Delivery.Parent.Prior.corrected_injury(PARENT/'native/injury',PARENT/'candidate.nes')
    plans = {name:plan(raw,name) for name in PACKETS}
    out.mkdir()
    for name,(source,inputs,ready) in plans.items():
        prepare(out/name,rom,source,refs|inputs,expected=PIN,timeout=ready['timeout'],
                scope=ready['scope'],allow_interactive=ready['allow_interactive'])
    assert sum(path.is_file() for path in out.rglob('*'))==12


if __name__=='__main__':
    main()
