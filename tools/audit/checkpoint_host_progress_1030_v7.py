"""Preserve DK's actual clear and FF work without promoting private candidates."""
from pathlib import Path
import json
from checkpoint_roster_progress_1030_v2 import R, save, sha


def read(path, expected=None):
    path = R/path
    if expected:
        assert sha(path) == expected, path
    value = json.loads(path.read_text())
    return value, path


def bind(into, paths):
    for path in paths:
        value, path = read(path)
        additions = {str(path): sha(path)}
        for key in ['bindings', 'exact_unchanged_inputs']:
            additions.update(value.get(key, {}))
        for name, digest in additions.items():
            assert sha(name) == digest, name
            assert name not in into or into[name] == digest, name
            into[name] = digest
    into[str(Path(__file__).resolve())] = sha(__file__)


if __name__ == '__main__':
    dk, dk_path = read('build/dk-union13-qualified-v6/handoff.json',
                      '996a874bf9b9f9111a9582578a760b91b80516d2b39e59246c49cac429d22e6f')
    assert dk['native_route_pass'] and dk['source_CPU_controls_pass']
    assert dk['zero_deaths'] and dk['real1_2_updates'] == 25
    assert sha(dk['candidate']) == dk['candidate_sha256']
    bindings = {}
    bind(bindings, [dk_path])
    save('dk-native-flagpole-clear', dict(
        status='PRIVATE_SOURCE_AND_EASY_NATIVE_ROUTE_PASS_JOINT_REBASE_PENDING',
        ROM_sha256=dk['candidate_sha256'], native=dict(
            physical_frames=4000, complete_Main=3590, lossless_frames=3330,
            decoded_lossless_sha256='9eac1efe67807c7e9bda76ca9681be5ea972c9ff47b781ff2d64e79b8c19bd50',
            real_1_2_updates=25, zero_deaths=True, process_exit=0),
        source_change='22 ROM bytes route DK automatic flagpole/exit side queries through the genuine native probe; normal 42px body probes unchanged.',
        CPU_regression='1280 normal and512 automatic side ABI cases,300 complete foreign Main updates (zero cycle delta), real vectors and source abilities/items passed.',
        root_visual_review='Viewed eight selected whole frames including normal combat, flagpole, castle exit and real underground body.',
        retained_negatives='Single-poll input, missing barrel line-of-sight, unlatched facing, actual 11000-frame flag stall, and engine4-only reattachment all retained in source evidence.',
        limits=dk['limits']), bindings)

    audit, audit_path = read('build/final-fantasy-execution-audit-v1/handoff.json',
                            '6576763c124d3267cd243c7cac65057cb34a713fc39e3ad5ce0b708c112af866')
    bindings = {}
    bind(bindings, [audit_path,
        R/'build/final-fantasy-execution-audit-v1/resource-closure.json',
        R/'build/final-fantasy-execution-audit-v1/cpu-controls-v2.json',
        R/'build/final-fantasy-execution-audit-v1/postflight-bindings.json',
        R/'build/final-fantasy-ram3-kernel-v1/build-proof.json',
        R/'build/final-fantasy-host-combat-v1/build-proof.json'])
    save('ff-ram3-source-and-execution-audit', dict(
        status='OFFLINE_SOURCE_EXECUTION_PASS_HOST_COMBAT_V1_RETAINED_UNQUALIFIED',
        audit_status_at_freeze=audit['status'], kernel_sha256=audit['source_kernel_sha256'],
        current_source_ROM_sha256=audit['current_FF_ROM_sha256'], CPU=audit['CPU'],
        source_code=audit['code'],
        resource_grant='Separate root ff-ram3-private-allocation grants RAM3 and CHR893..<901 conditional on actual dense Parodius source. The older read-only audit correctly states that it made no allocation.',
        prototype='Native FF target geometry, HP/defeat and source contact consumers assembled into484 private bytes. V1 is retained unqualified: foreign Fresh resets FF Ready before its owner guard; a separate source successor repairs this.',
        limits=['No actual source loader, native gameplay, menu admission or shared header adoption from this checkpoint.',
                'Original CORE3211/publisher20/ART3410/CHR32768 bytes preserved; current FF host terrain/render/palette/music integration still required.',
                'Initial NMI ownership-fixture negative retained; corrected804 real vector cases preserve all143 FF bytes.']), bindings)

    negative, negative_path = read('build/character-host-union-rogue-pn-negative-v1/handoff.json',
                                  '6b6072e8ef38e573204e8a46f22839e630a5021326469dca05ad016614f828c5')
    bindings = {}
    bind(bindings, [negative_path])
    save('joint-rogue-parodius-memory-negative', dict(
        status=negative['status'], ROM_sha256=negative['ROM_sha256'],
        proven_collision=negative['proven_collision'], failed_case=negative['failed_case'],
        source_passes_before_failure=negative['prior_passes'],
        remedy='Separate private allocation reserves dedicated FamilyMainCommit5FFF; actual global constructor source shifts only the last clear operand5F00 to5EFF, preserving every other reset and all instruction cycles.',
        limits=['This original candidate remains failed. No normalization of active Parodius history is permitted.',
                'Source successor must genuinely rebind all consumers and pass constructor/interrupt/full foreign controls; allocation alone does not qualify it.']), bindings)

    p = R/'docs/qa/host-integration-progress-2026-10-30.json'
    progress = json.loads(p.read_text())
    progress['root_completed_this_continuation'] += [
        'DK private07d5 source fix uses native side probes during flagpole/exit engines4/5 only. 4000-frame actualEasy1-1 clear plus25real1-2 updates, zero deaths,3330 lossless frames checksum-verified. Root viewed eight whole-frame selections; joint source rebase remains required.',
        'FF current-source RAM3 prototype preserves CORE3211, native publisher20, ART3410 and CHR32768. 192 source pairs/2304ticks/804 real normal-lagNMI+IRQ controls pass; all143FF bytes preserved. Genuine host combat first source consumer assembled, then separately reviewed.',
        'Private FF RAM3/eight CHR carrier pages allocated only with actual densePN source and genuine forcedblank loader/router; no shared/header change.',
        'Actual Rogue joint source uncovered common5FB6 protocol overwriting active Parodius history104to0. Failed original frozen; dedicated5FFF protocol byte and same-cycle constructor final-clear operand correction privately allocated. Source successor underway.'
    ]
    progress['active_work']['DK_route'] = 'Private07d5 source/native clear passes; native4000frames,3590Main,3330verifiedlossless,zero deaths,25real1-2. Genuine current joint source rebase required. Nativeeveryitem/Hard/P2/campaign remain open.'
    progress['active_work']['Final_Fantasy'] = 'Currentaadbbb source/kernel execution verified. Private RAM3 and CHR893..<901 granted conditional on densePN; actual source loader/router in progress. Genuine host combat adapter source qualification underway. Terrain/complete render/palette/music and native admission still required; no shared installation.'
    progress['active_work']['joint_resource_base'] = 'Actual db3ab7 source merge failed real PNhistory5FB6 ownership. Frozen negative preserved. DedicatedFamilyMainCommit5FFF source successor now passes282foreignMain pairs, realRogue/Gimmick vector controls and960existing-host Main updates. Measured+634..1656CPU foreign overhead is an open timing regression. Constructor controls and genuineDK22B source rebase next; no native grant.'
    p.write_text(json.dumps(progress, indent=2)+'\n')
