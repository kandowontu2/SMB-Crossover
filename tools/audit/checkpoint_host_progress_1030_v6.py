"""Finish v5 checkpoint remainder using Arthur's actual separate source closure."""
from pathlib import Path
import json
from checkpoint_roster_progress_1030_v2 import R, save, sha


def read(path, expected):
    path = R/path
    assert sha(path) == expected, path
    value = json.loads(path.read_text())
    bindings = dict(value['bindings'])
    bindings[str(path)] = expected
    bindings[str(Path(__file__).resolve())] = sha(__file__)
    return value, bindings


if __name__ == '__main__':
    ar, native_bindings = read('build/arthur-host-render-fast-v1/native-handoff-v1.json',
                              'd5cbba11a142af82116c8ecb0f55e9509fa04467ae98bd7e79c987e4aedccbfe')
    source_path = R/'build/arthur-host-render-fast-v1/handoff.json'
    assert sha(source_path) == '0858045263efcf6aa1e11cb4ad7b7a830112edb82131fd85c94e8aa1d959a485'
    source = json.loads(source_path.read_text())
    closure_path = R/'build/arthur-host-render-fast-v1/source-closure.json'
    assert sha(closure_path) == '882405a107217c7c9618b0833664843f2d3818a72c6aaaec78bba886e5d2a21e'
    closure = json.loads(closure_path.read_text())
    bindings = {str((R/path).resolve()):digest for path,digest in closure['files'].items()}
    bindings[str(closure_path)] = sha(closure_path)
    for path, digest in native_bindings.items():
        assert path not in bindings or bindings[path] == digest, path
        bindings[path] = digest
    bindings[str(source_path)] = sha(source_path)
    assert ar['process_exit'] == 0 and ar['semantic_result']['passed']
    assert ar['normal_eight_sprite_limit'] and not ar['script_RAM_writes']
    save('arthur-render-transport-native', dict(
        status='BOUNDED_NATIVE_SEMANTICS_PASS_SEVERE_LAG_AND_CROWDING_STILL_OPEN',
        ROM_sha256=ar['candidate_sha256'], native=ar['semantic_result'],
        matched_CPU_Main_saving_mean=753.792,
        same_controller_native_comparison=ar['comparison'],
        root_visual_review='Viewed actual game-controlled, source-lance and double-jump PNGs: coherent body/weapon, blue world, ground and ARTHUR HUD.',
        source_changes='Same-bank selected worker dispatch plus exact C2 CHR publisher transport; source cache, body pixels, native queries and state preserved.',
        limits=['212 lag NMIs in400 gameplay frames remains severe; this private candidate is unadmitted.',
                'Native mean saves415.267CPU; changed video phase means source-case754CPU is not a native FPS claim.',
                'Required black ink already ignores Shadows. Normal hardware sprite overload remains unchanged; fair actor/weapon display still required.',
                'Further same-bank worker replication has not been granted shared capacity.']), bindings)

    plan, bindings = read('build/character-host-union-rogue-v1/corrected-player-padding-proposal-v1/proposal.json',
                          '44e77eb94f2f131ab0fbca0313c41452175c7bcd8fdd151dd4d3dde486fffd77')
    assert not plan['numeric_or_absolute_aliases_into_proposed_padding']
    assert not plan['known_SMC_or_pointer_consumers_inside_padding']
    for case in plan['linked_cases']:
        assert not case['labels_inside_proposed_span']
        rom = Path(case['packet'])/'candidate.nes'
        assert sha(rom) == case['ROM_sha256']
        raw = rom.read_bytes()
        start = 16+8192+0x1969
        assert raw[start:start+40] == bytes([234])*40
        assert raw[start+40] == 96
    save('typed-rogue-player-padding-correction', dict(
        status='ROOT_APPROVED_CORRECTED_SOURCE_PADDING_NO_JOINT_RUNTIME_CLAIM',
        supersedes_plan_addresses_only=True,
        rejected='Old Rogue B958 gate address is live V13 LuigiSourceMovementBridge code; must never overwrite it.',
        source_owner='Actual src/luigi_native.s .res83 after two tail farcalls, before original Done RTS.',
        approved_existing_spans=['A1:B969..<B98124bytes gate',
                                 'A1:B981..<B99015bytes selector'],
        preserve=['B990 EA', 'B991 Done RTS', 'B93E LuigiNativeTraction',
                  'B957 LuigiSourceMovementBridge', 'A1:A147..<A16B existing hook',
                  'all original V13 terrain entries, actual consumers and SMC aliases'],
        root_decision='Proceed only with genuine source reassembly and native/foreign ABI controls inside verified owned padding. Retain failed old-origin link/source as a negative.',
        limits=['No new byte lease, shared installation, joint gameplay or final timing-parity claim.']), bindings)

    progress_path = R/'docs/qa/host-integration-progress-2026-10-30.json'
    progress = json.loads(progress_path.read_text())
    progress['root_completed_this_continuation'] += [
        'Qualified Rogue audio relocation, Quick actual-Main renderer and typed joint plan frozen to GitHub6327ff66; no private candidate promoted.',
        'FF genuinely linked to current753b host through87 real imports, reproducing the exact parent and preserving67378 qualified old symbols. CORE3211/ART3410/CHR32768 match frozen source. Current-host720life/632pixel/1328native-draw/1512contact/256CHR/432pose leaf controls pass; no admission.',
        'Arthur2846 actual400-game-frame smoke passes normal8-sprite semantics with required ink unchanged. Lag216to212; native mean23771.948to23356.681CPU. Root viewed body/lance/double jump. Severe lag and overload remain open.',
        'Corrected joint gate proposal: independent RogueB958 overlapped live V13 Luigi. Actual source-owned B969..<B990 padding approved, B990EA/B991RTS and both Luigi entries preserved; failed origin assertion retained.'
    ]
    progress['active_work']['Arthur'] = 'Private2846 source/native rendering transport verified; native212lag/400 and mean23356.681CPU remain severe. Required ink unconditional. Fair overload rendering and further capacity-reviewed optimization pending; not installed.'
    progress['active_work']['Final_Fantasy'] = 'Current aadbbb89 genuine component link and complete frozen leaf assertions pass. All4 classes remain pending: native host terrain/combat/complete OAM-palette/music integration still required. CORE almost full; no RAM3 or additional CHR allocation made.'
    progress['active_work']['joint_resource_base'] = '3925 resource and RCR753 source qualified. Rogue ca26 audio source and Quick df2b render component frozen. Genuine source joint composition in progress; corrected PLAYER gate B969..<B990 replaces invalid oldRogue B958 proposal, all live Luigi entries retained. One common NMI and typed foreign paths still require actual qualification.'
    progress['active_work']['DK_route'] = 'Controller-only min8A, real barrel LOS and facing-ack successors retain negatives. Facing-ack run reached flagpole with zero deaths; native end sequence now stalls because feet collision grounds before native flag award threshold. Agent preserving original bounded terminal and reproducing first actual write; source repair pending. No clear claim.'
    progress_path.write_text(json.dumps(progress, indent=2)+'\n')
