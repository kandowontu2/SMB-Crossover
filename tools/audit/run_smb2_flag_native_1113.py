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
WITH_MIRRORS='2c62e1a0de1b732cfa57af59e71c0775396e067bf04aa101e78f644c3e4c9c4b'
PUBLIC_BUB='f88cfe5aee15bb3921c691b7f06d905246be9ff88b9b43eea71c2405722724a7'
WITH_PRIORITY='dadb9d80702148fe40b1a64d1cfff7ff2df65248b9c72e7c167d32e3589670be'
WITH_FOREGROUND='2448c558298d9f1b6d178dcdc00e90db90ae7d85b95e37c0101130701aab261a'
CURRENT_FOREGROUND='3684f3d2a418a484befd80fca351d0dc5f9b472f6f067a0a7894994ea343679d'
WITH_POSTBG='12397b1c2557834f6a2b7e23c9915d5dc40c6cabff7a6ee844c1adebf6564c52'
NIGHTLY=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--variant',choices=tuple(str(v)for v in range(8))+('all',),default='4')
    p.add_argument('--metadata',action='store_true')
    p.add_argument('--next-area-diagnostic',action='store_true')
    p.add_argument('--mirrors',action='store_true',help='Explicit flag plus three source-qualified fixed-bank mirrors; retains the old private proposal.')
    p.add_argument('--pipe-priority',action='store_true',help='Explicit separately pinned current-Doki priority successor; requires --mirrors.')
    p.add_argument('--visual',action='store_true',help='Two bounded in-memory natural-route PNGs; requires --pipe-priority.')
    p.add_argument('--terrain-profiles',action='store_true',help='Use independently measured variant controls, including original Down60 charged jumps; requires --pipe-priority.')
    p.add_argument('--foreground',action='store_true',help='Explicit separately pinned normal-play foreground successor; requires --pipe-priority.')
    p.add_argument('--current-bub',action='store_true',help='Merge the exact foreground repair with delivered Bub/Bob optimizations; requires --foreground.')
    p.add_argument('--downloads',action='store_true',help='Launch exact installed merged candidate in its actual Downloads context; requires --current-bub.')
    p.add_argument('--postbg',action='store_true',help='Explicit six-operand sample-bank fallback repair; requires --current-bub.')
    args=p.parse_args()
    if args.terrain_profiles:
        assert args.pipe_priority and not args.next_area_diagnostic and not args.visual
    if args.foreground:
        assert args.pipe_priority and not args.next_area_diagnostic
    if args.current_bub:assert args.foreground
    if args.postbg:assert args.current_bub
    if args.downloads:assert args.current_bub
    public_now=check(NIGHTLY)['ROM_sha256']
    assert public_now in(PARENT,PUBLIC_BUB,CURRENT_FOREGROUND,WITH_POSTBG)
    public_image=NIGHTLY.read_bytes()
    if public_now==WITH_POSTBG:
        import compose_smb2_postbg_mirror_1113 as PostBG
        public_image=PostBG.inverse(public_image)
        assert sha256(public_image).hexdigest()==CURRENT_FOREGROUND
    if sha256(public_image).hexdigest()==CURRENT_FOREGROUND:
        import compose_smb2_foreground_current_1113 as Current
        public_image=Current.inverse(public_image)
        assert sha256(public_image).hexdigest()==PUBLIC_BUB
    raw=public_image
    if sha256(raw).hexdigest()==PUBLIC_BUB:
        import bub_native_noops_1113 as Bub
        raw=Bub.combined_reverse(raw)
        assert sha256(raw).hexdigest()==PARENT
    image,info=C.proposal(raw)
    assert sha256(image).hexdigest()==CANDIDATE and C.inverse(image)==raw
    assert info['new_RAM_bytes']==info['new_ROM_bytes']==0
    control_image=image
    candidate=CANDIDATE
    if args.mirrors:
        import compose_smb2_foot_mirror_1113 as Mirror
        image,mirror_info=Mirror.all_mirrors_proposal(control_image)
        assert sha256(image).hexdigest()==WITH_MIRRORS
        assert Mirror.all_mirrors_inverse(image)==control_image
        assert mirror_info['changed_bytes']==180 and mirror_info['extra_RAM_bytes']==mirror_info['extra_ROM_bytes']==0
        candidate=WITH_MIRRORS
    if args.pipe_priority:
        assert args.mirrors
        import compose_smb2_pipe_priority_1113 as Priority
        mirror_image=image
        image,priority_info=Priority.proposal(mirror_image)
        assert sha256(image).hexdigest()==WITH_PRIORITY
        assert Priority.inverse(image)==mirror_image and priority_info['changed_bytes']==132
        candidate=WITH_PRIORITY
    priority_image=image
    if args.foreground:
        import compose_smb2_pipe_foreground_1113 as Foreground
        image,foreground_info=Foreground.proposal(priority_image)
        assert sha256(image).hexdigest()==WITH_FOREGROUND
        assert Foreground.inverse(image)==priority_image and foreground_info['changed_bytes']==150
        candidate=WITH_FOREGROUND
    if args.current_bub:
        import compose_smb2_foreground_current_1113 as Current
        image,current_info=Current.proposal(public_image)
        assert sha256(image).hexdigest()==CURRENT_FOREGROUND
        assert Current.inverse(image)==public_image and current_info['changed_bytes']==516
        candidate=CURRENT_FOREGROUND
    if args.postbg:
        import compose_smb2_postbg_mirror_1113 as PostBG
        postbg_parent=image
        image,postbg_info=PostBG.proposal(postbg_parent)
        assert sha256(image).hexdigest()==WITH_POSTBG
        assert PostBG.inverse(image)==postbg_parent and postbg_info['changed_operand_bytes']==6
        candidate=WITH_POSTBG
    if args.downloads:
        assert public_now==candidate and NIGHTLY.read_bytes()==image
    variants=range(8)if args.variant=='all'else(int(args.variant),)
    if not args.metadata:
        OUT.mkdir(exist_ok=True)
        assert {p.name for p in OUT.iterdir()}<= {'candidate.nes','controller.lua'}
        (OUT/'candidate.nes').write_bytes(image)
    for variant in variants:
        text=Replay.controller(control_image,variant)
        if variant==4:
            assert sha256(text.encode()).hexdigest()=='09c0f838b1c8f592d7a470f51892cafe03227dbd898e5c1b61d317fc1873c453'
        if args.next_area_diagnostic:
            import replay_smb2_next_area_diagnostic_1113 as Diagnostic
            text=Diagnostic.controller(control_image,variant)
        if args.mirrors:
            assert text.count(CANDIDATE)==1
            text=text.replace(CANDIDATE,WITH_PRIORITY if args.pipe_priority else candidate)
            Replay.Root.Base.LuaRuntime().compile(text)
        if args.pipe_priority and variant==4 and not args.next_area_diagnostic:
            assert sha256(text.encode()).hexdigest()=='f4b9ebfaee4cd75245ecd3cb0e38b5d4ab6c00127fc2a9f125270448a5ddf5cc'
        if args.visual:
            assert args.pipe_priority and not args.next_area_diagnostic
            import replay_smb2_priority_visual_1113 as Visual
            text=Visual.controller(priority_image,variant)
        if args.terrain_profiles:
            import replay_smb2_variants_stage_1113 as Terrain
            text=Terrain.profile_controller(priority_image,variant,full=True)
        if args.foreground:
            assert text.count(WITH_PRIORITY)==1
            text=text.replace(WITH_PRIORITY,WITH_FOREGROUND)
            Replay.Root.Base.LuaRuntime().compile(text)
        if args.current_bub:
            assert text.count(WITH_FOREGROUND)==1
            text=text.replace(WITH_FOREGROUND,CURRENT_FOREGROUND)
            Replay.Root.Base.LuaRuntime().compile(text)
        if args.postbg:
            assert text.count(CURRENT_FOREGROUND)==1
            text=text.replace(CURRENT_FOREGROUND,WITH_POSTBG)
            Replay.Root.Base.LuaRuntime().compile(text)
        summary=dict(ROM_SHA256=candidate,parent_SHA256=PARENT,current_Downloads_SHA256=public_now,
            identity=Replay.Root.NAMES[variant],variant=variant,
            script_SHA256=sha256(text.encode()).hexdigest(),
            controls_unchanged_from_public_diagnostic=not args.terrain_profiles,terrain_profiles=args.terrain_profiles,normal_foreground=args.foreground,next_area_diagnostic=args.next_area_diagnostic,all_fixed_mirrors=args.mirrors,pipe_priority=args.pipe_priority,
            current_Bub_preserved=args.current_bub,postbg_sample_aliases=args.postbg,
            private_only=not args.downloads,installed=args.downloads,native_run=not args.metadata)
        if not args.metadata:
            script=OUT/'controller.lua'
            script.write_text(text,encoding='utf-8',newline='\n')
            rom=NIGHTLY if args.downloads else OUT/'candidate.nes'
            q=run(script,rom,OUT/'capture',candidate,240)
            receipt=q['receipt']
            compact={k:receipt.get(k)for k in('passed','reason','terminal','physical_frames',
                'all_returned_Main','return_counts','idle','last_pit','injury_entries',
                'flag','castle','entrance','next_area_updates','next_phase','image_tags','capture_files','runtime_state_writes')}
            summary.update(passed=q['passed'],receipt_SHA256=q['receipt_SHA256'],
                receipt=compact,outputs_written=q['outputs_written'])
            if args.next_area_diagnostic or args.visual:
                summary['images']=q['images']
            print(json.dumps(summary,separators=(',',':')),flush=True)
            assert q['passed'],'Private SMB2/Doki native full-stage qualification failed'
            if args.visual:
                assert len(q['images'])==2 and set(receipt['image_tags'])=={'side_pipe','underground_grounded'}
                if args.foreground:
                    assert receipt['image_tags']['side_pipe']['attribute']&32
                    assert receipt['image_tags']['underground_grounded']['attribute']==0
        else:print(json.dumps(summary,separators=(',',':')),flush=True)
    assert check(NIGHTLY)['ROM_sha256']==public_now


if __name__=='__main__':main()
