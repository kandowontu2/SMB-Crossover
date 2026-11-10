"""Run the Sonic portrait and original-motion controllers in the shared Mesen queue."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import stage_sonic_original_scene_1110 as Stage
from deliver_manual_title_1110 import SOURCE_BASE, apply_ips, ips_for
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

PIN='d2542ff3c9f78ac26eb7e19d64a7708711bc766515f634b05952bab1be9103f0'
OPENING=Stage.R/'tools/playthroughs/sonic_original_motion_stdout_1110_v2.lua'
OPENING_PIN='052a4f436c6b2a697b6e79c35b14bd006842b89a53ae56a9430fb25c0e404ba8'
PORTRAITS=Stage.R/'tools/playthroughs/sonic_static_portrait_stdout_1110.lua'
PORTRAITS_PIN='b2f4d172657a4a10930c93330595e3dad52af66c9fccda9e62675b4761bc860d'
FULL_STAGE=Stage.R/'tools/playthroughs/sonic_original_full_stage_stdout_1110.lua'
FULL_STAGE_PIN='2c2ee3f821affcff8c8748a35918fd7c9531760332a3e6d0b5d392f4154fa4ee'


def compact(result):
    return dict(passed=result['passed'],receipt_SHA256=result['receipt_SHA256'],
        script_SHA256=result['script_SHA256'],actual_Mesen=True,
        receipt=result['receipt'],other_processes_untouched=result['other_processes_untouched'],
        outputs_written=result['outputs_written'])


def qualify(rom,output):
    assert sha256(PORTRAITS.read_bytes()).hexdigest()==PORTRAITS_PIN
    assert sha256(OPENING.read_bytes()).hexdigest()==OPENING_PIN
    assert sha256(FULL_STAGE.read_bytes()).hexdigest()==FULL_STAGE_PIN
    results={}
    for name,script in (('portraits',PORTRAITS),('opening',OPENING),('full_stage',FULL_STAGE)):
        result=run(script,rom,output/name,PIN,120)
        results[name]=compact(result)
        print(json.dumps(dict(event='actual_Sonic_'+name,**results[name]),sort_keys=True),flush=True)
        assert result['passed'],results[name]['receipt']
    portraits=results['portraits']['receipt']
    assert portraits['menu']['cells']==portraits['lives']['cells']==4
    assert portraits['menu']['CHR_page']==portraits['lives']['CHR_page']==224
    opening=results['opening']['receipt']
    assert opening['terminal']['x']==200 and opening['terminal']['lives']==2
    assert opening['calls']['OriginalSonicFrame']==81 and opening['calls']['SonicHostConstruct']==1
    full=results['full_stage']['receipt']
    assert full['native_flag'] and full['native_castle'] and full['native_entrance'] and full['active_1_2']
    assert full['terminal']['lives']==2 and full['terminal']['level']==1
    assert len(full['jump_events'])==17 and full['calls']['OriginalSonicFrame']==1423
    return results


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--install',action='store_true')
    parser.add_argument('--opening-receipt-sha')
    parser.add_argument('--portrait-receipt-sha')
    parser.add_argument('--full-stage-receipt-sha')
    args=parser.parse_args()
    output=args.output.resolve()
    assert output.is_relative_to(Stage.R/'build') and output!=Stage.R/'build' and not output.exists()
    candidate=Stage.CANDIDATE.read_bytes()
    assert sha256(candidate).hexdigest()==PIN
    if not args.install:
        results=qualify(Stage.CANDIDATE,output)
        print(json.dumps(dict(passed=True,private_candidate=True,ROM_SHA256=PIN,
            output_files=0,receipts={name:q['receipt_SHA256'] for name,q in results.items()}),sort_keys=True),flush=True)
        return
    expected={'opening':args.opening_receipt_sha,'portraits':args.portrait_receipt_sha,
              'full_stage':args.full_stage_receipt_sha}
    assert all(pin and len(pin)==64 for pin in expected.values())
    image,_,_,record=Stage.reconstruct()
    assert image==candidate
    before=check(Stage.NIGHTLY)
    old=Stage.NIGHTLY.read_bytes()
    assert sha256(old).hexdigest()==before['ROM_sha256']==Stage.PARENT
    patch=ips_for(image)
    assert apply_ips(SOURCE_BASE.read_bytes(),patch)[0]==image
    Stage.NIGHTLY.write_bytes(image)
    try:
        assert Stage.NIGHTLY.read_bytes()==image and check(Stage.NIGHTLY)['ROM_sha256']==PIN
        results=qualify(Stage.NIGHTLY,output)
        assert {name:q['receipt_SHA256'] for name,q in results.items()}==expected
        assert Stage.NIGHTLY.read_bytes()==Stage.CANDIDATE.read_bytes()==image
        after=check(Stage.NIGHTLY)
        assert after['ROM_sha256']==PIN
    except BaseException:
        Stage.NIGHTLY.write_bytes(old)
        assert Stage.NIGHTLY.read_bytes()==old
        raise
    print(json.dumps(dict(passed=True,directly_installed=True,ROM_SHA256=PIN,
        previous_ROM_SHA256=Stage.PARENT,IPS_SHA256=sha256(patch).hexdigest(),IPS_bytes=len(patch),
        patch_reconstruction_equals_tested_Downloads=True,backup_files=0,output_files=0,
        guard_before=before,guard_after=after,source_record=record,
        receipts={name:q['receipt_SHA256'] for name,q in results.items()}),sort_keys=True),flush=True)


if __name__=='__main__':main()
