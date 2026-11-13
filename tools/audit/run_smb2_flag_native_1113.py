"""Root's serial native qualification of the private SMB2 flag handoff."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import compose_smb2_flag_handoff_1113 as C
import replay_smb2_flag_handoff_1113 as Replay
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

R=Path(__file__).resolve().parents[2]
OUT=R/'build/smb2-flag-native-1113'
PARENT='7ef2de351d3a4ae60b3ada2eb1aa56b330873dc106ad43428ec6803bf420d4fc'
CANDIDATE='0e9e9254927236bcc651e79da36a77924eea5481421858a05f869b15298412e1'
NIGHTLY=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--variant',choices=tuple(str(v)for v in range(8))+('all',),default='4')
    p.add_argument('--metadata',action='store_true')
    p.add_argument('--next-area-diagnostic',action='store_true')
    args=p.parse_args()
    assert check(NIGHTLY)['ROM_sha256']==PARENT
    raw=NIGHTLY.read_bytes();image,info=C.proposal(raw)
    assert sha256(image).hexdigest()==CANDIDATE and C.inverse(image)==raw
    assert info['new_RAM_bytes']==info['new_ROM_bytes']==0
    variants=range(8)if args.variant=='all'else(int(args.variant),)
    if not args.metadata:
        OUT.mkdir(exist_ok=True)
        assert {p.name for p in OUT.iterdir()}<= {'candidate.nes','controller.lua'}
        (OUT/'candidate.nes').write_bytes(image)
    for variant in variants:
        text=Replay.controller(image,variant)
        if variant==4:
            assert sha256(text.encode()).hexdigest()=='09c0f838b1c8f592d7a470f51892cafe03227dbd898e5c1b61d317fc1873c453'
        if args.next_area_diagnostic:
            import replay_smb2_next_area_diagnostic_1113 as Diagnostic
            text=Diagnostic.controller(image,variant)
        summary=dict(ROM_SHA256=CANDIDATE,parent_SHA256=PARENT,
            identity=Replay.Root.NAMES[variant],variant=variant,
            script_SHA256=sha256(text.encode()).hexdigest(),
            controls_unchanged_from_public_diagnostic=True,next_area_diagnostic=args.next_area_diagnostic,
            private_only=True,installed=False,native_run=not args.metadata)
        if not args.metadata:
            script=OUT/'controller.lua'
            script.write_text(text,encoding='utf-8',newline='\n')
            q=run(script,OUT/'candidate.nes',OUT/'capture',CANDIDATE,240)
            receipt=q['receipt']
            compact={k:receipt.get(k)for k in('passed','reason','terminal','physical_frames',
                'all_returned_Main','return_counts','idle','last_pit','injury_entries',
                'flag','castle','entrance','next_area_updates','next_phase','capture_files','runtime_state_writes')}
            summary.update(passed=q['passed'],receipt_SHA256=q['receipt_SHA256'],
                receipt=compact,outputs_written=q['outputs_written'])
            if args.next_area_diagnostic:
                summary['images']=q['images']
            print(json.dumps(summary,separators=(',',':')),flush=True)
            assert q['passed'],'Private SMB2/Doki native full-stage qualification failed'
        else:print(json.dumps(summary,separators=(',',':')),flush=True)
    assert check(NIGHTLY)['ROM_sha256']==PARENT


if __name__=='__main__':main()
