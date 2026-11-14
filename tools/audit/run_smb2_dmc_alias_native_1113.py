"""Root-only bounded actual Downloads DMC-alias timing observation."""
import argparse
from hashlib import sha256
import json

import replay_smb2_dmc_alias_native_1113 as Replay
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=Replay.Terrain.Flag.R/'build/smb2-flag-native-1113'
LUA='b80d9992f21e4b9632de3a9b8abd4352270368f8394285deb226be0968d10e46'
MODULE='c39e3abea1bd7ada4397e28635038ceb281fcc3f36d2e18816051f6aa1b9e95e'
SCENE_LUA='5bd36d95616f88bc30946c7b6d0a2a6aa7d7948964848236ecef02b7e76e016f'
SCENE_MODULE='62d5bf8cd39ac07b45115f0031063d3914c9c670a56f30e1990130657d09b9d8'
POSTBG_LUA='ff9bc7b38a268d8cc211b57d76340b51baa4840791bf55905b206be28a8bd58f'
POSTBG_MODULE='1c6c137f1b2a61946d49b82af8005b71641ed85fe3ff6c30e11132f604777a9d'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--scene-only',action='store_true')
    p.add_argument('--postbg',action='store_true',help='Strict private repaired candidate; requires --scene-only.')
    p.add_argument('--downloads',action='store_true',help='Launch the byte-identical installed repaired candidate; requires --postbg.')
    args=p.parse_args()
    assert sha256(Replay.Path(Replay.__file__).read_bytes()).hexdigest()==MODULE
    if args.postbg:assert args.scene_only
    if args.downloads:assert args.postbg
    public_now=check(Replay.NIGHTLY)['ROM_sha256']
    raw=Replay.NIGHTLY.read_bytes()
    expected=LUA
    candidate=Replay.PIN
    rom=Replay.NIGHTLY
    if args.postbg:
        import replay_smb2_postbg_native_1113 as Fixed
        assert sha256(Replay.Path(Fixed.__file__).read_bytes()).hexdigest()==POSTBG_MODULE
        if public_now==Fixed.C.CANDIDATE:
            parent=Fixed.C.inverse(raw)
        else:
            assert public_now==Fixed.C.PIN
            parent=raw
        image,info=Fixed.C.proposal(parent)
        assert Fixed.C.inverse(image)==parent and info['changed_operand_bytes']==6
        candidate=Fixed.C.CANDIDATE
        if args.downloads:
            assert public_now==candidate and raw==image
        else:
            rom=OUT/'candidate.nes'
            rom.write_bytes(image)
        text=Fixed.controller(image)
        expected=POSTBG_LUA
    elif args.scene_only:
        assert public_now==Replay.PIN
        import replay_smb2_dmc_scene_native_1113 as Scene
        assert sha256(Replay.Path(Scene.__file__).read_bytes()).hexdigest()==SCENE_MODULE
        text=Scene.controller(raw)
        expected=SCENE_LUA
    else:
        assert public_now==Replay.PIN
        text=Replay.controller(raw)
    assert sha256(text.encode()).hexdigest()==expected
    script=OUT/'controller.lua'
    script.write_text(text,encoding='utf-8',newline='\n')
    q=run(script,rom,OUT/'capture',candidate,240)
    receipt=q['receipt']
    trace=receipt.get('dmc_alias',{})
    events=[]
    keep=('kind','frame','Main','cycle','pc','sp','a','world','level','engine',
          'status4015','active_bank','pending_bank','enable','bankA','bankC',
          'mapped_pc','resident','smc_target','smc_next_bank','tail_target',
          'tail_bank','stack_return','apu','address','value','writer',
          'expected_target','expected_bank','token','entry_Main','entry_cycle',
          'entry_sp','entry_return','chain_stage','native_target_seen',
          'farcall_return_seen','resident_return_seen','farcall_return')
    for _,event in sorted(trace.get('events',{}).items(),key=lambda item:int(item[0])):
        events.append({k:event[k]for k in keep if k in event})
    compact={k:v for k,v in trace.items()if k!='events'}
    if args.scene_only:
        all_events=events
        audio=[e for e in all_events if e.get('kind')in('status_after_start','alias_after_select')][:8]
        events=[e for e in all_events if e.get('kind','').startswith('scene_')]+audio
        compact['retained_event_count']=len(all_events)
        compact['printed_event_projection']=True
    compact['events']=events
    print(json.dumps(dict(passed=q['passed'],ROM_SHA256=candidate,Lua_SHA256=expected,
        current_Downloads_SHA256=public_now,postbg=args.postbg,Downloads_launch=args.downloads,
        scene_only=args.scene_only,
        receipt_SHA256=q['receipt_SHA256'],physical_frames=receipt.get('physical_frames'),
        all_returned_Main=receipt.get('all_returned_Main'),terminal=receipt.get('terminal'),
        reason=receipt.get('reason'),trace=compact,outputs_written=q['outputs_written']),
        separators=(',',':')),flush=True)
    assert check(Replay.NIGHTLY)['ROM_sha256']==public_now
    assert q['passed'],'Native DMC timing observer or retained full route failed'
    if args.postbg:
        counts=trace['chain_counts']
        entries=counts['resident_entries']
        assert entries>100
        assert counts.get('scene_matched_stale_target',0)==0,counts
        assert counts['scene_matched_canonical_target']==counts['resident_returns']==counts['farcall_returns']==entries,counts
        assert trace['tail_dropped']==0
        assert any(e.get('kind')=='scene_matched_canonical_target'and e['resident']['bank']in(119,120)
                   and e['status4015']&16 and e['apu'].get('apu.dmc.bytesRemaining',0)>0 for e in events),events


if __name__=='__main__':main()
