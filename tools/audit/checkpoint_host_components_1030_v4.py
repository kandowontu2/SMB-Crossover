"""Freeze reviewed source components without treating them as a released joint ROM."""
from pathlib import Path
import json

from checkpoint_roster_progress_1030_v2 import R, save, sha


def checkpoint(folder, expected, name, report):
    path = R / 'build' / folder / 'handoff.json'
    assert sha(path) == expected, path
    handoff = json.loads(path.read_text())
    bindings = dict(handoff['bindings'])
    bindings[str(path)] = sha(path)
    bindings[str(Path(__file__).resolve())] = sha(__file__)
    report['component_handoff'] = str(path)
    report['component_handoff_sha256'] = expected
    save(name, report, bindings)


if __name__ == '__main__':
    checkpoint('rogue-audio-page-relocation-v5',
               '6dadffaf12ec6c9b0c4543b95e9eb6d5cf7b0e5231fe28e2bcdcc5da2cff868f',
               'rogue-audio-source-relocation', dict(
                   status='SOURCE_RELOCATION_CPU_PASS_NO_JOINT_ENGINE_OR_NATIVE_RUN',
                   ROM_sha256='ca26b6dd231908dfc98e49f4fb16b8e24d0c44c7a4d40d0228ece44f30a90ded',
                   checks=dict(actual_reader_bytes=57344, source_JSR_flag_cases=6144,
                               original_cartridge_full_NMI_pairs=612,
                               temporary_page_interrupt_cases=20,
                               full_Control192_Main_NMI_IRQ_pairs=2,
                               lower_map_aliases=42, upper_raw_map_aliases=1),
                   source_change='Relocate ten original256-byte audio pages into explicitly granted Quick storage; rebind every real lower and upper/raw alias. Retire old A79 depot.',
                   invariants='All runtime instructions, other named PCs, page contents, header, CHR and RAM layout unchanged. Actual APU events/cycles, maps/shadows and all33 SMC bytes match.',
                   retained_negatives='Earlier segment-order/include failures, lower-only alias returning FF instead of0, and overly broad temporary-state assertion are retained with their corrections.',
                   limits=['Isolated source component; no new joint native qualification or shared installation.',
                           'Copied parent receipts are labelled inherited; final authoritative compile logs are bound separately.']))
    checkpoint('quickman-wram-render-cpu-v7',
               '704dbbf3e7f2f108385d085a479388feec145a6c82b64330610efcd3bfd6525a',
               'quickman-actual-main-render-source', dict(
                   status='ACTUAL_MAIN_RENDER_CPU_PASS_FOREIGN_TIMING_HOLD',
                   ROM_sha256='df2b18c499a42660c12e81d86732afb92714952d281e0924859a3ffa14b48e1d',
                   checks=dict(actual_Main_pose_facing_cases=180,
                               warm_real_NMI_hardware_CHR_cases=120,
                               render_interrupt_seams=212,
                               retained_PRG_bytes=1989, reviewed_PRG_lease=7500),
                   source_change='Route actual Main through genuine Quick body/fan rendering; suppress duplicate legacy body and publish a source-owned empty descriptor.',
                   foreign_timing_delta_CPU=[0, 123, 132],
                   integration_API='QwOwnedDraw A70:AA09 requires actual joint typed owner selection and genuine reassembly, not a global legacy farcall overlay.',
                   limits=['Foreign latency remains a blocker; no native run or shared installation.',
                           'Source renderer and native actor parity do not establish 60Hz.']))
    checkpoint('character-host-union-rogue-plan-v1',
               '966aaa313fad41420fbb6dd24fac7801ad8ee4ae4d6b4758f1474a4dc0f0f575',
               'typed-rogue-union-source-plan', dict(
                   status='ROOT_REVIEWED_OFFLINE_PLAN_IMPLEMENTATION_SEPARATE',
                   source_change='Genuinely compose resource base3925, qualified RCR ink producer753b, relocated Rogue source and V13 consumers, with one common NMI family gate.',
                   authorized_existing_spans=['A1:A147..<A16B 36bytes',
                                              'A1:B958..<B970 24bytes',
                                              'A93:AFA7..<AFE7 64bytes'],
                   root_decision='Proceed with exact typed source reassembly and ABI/consumer closure inside these existing spans. Preserve four V13 moved terrain entries, six rebound operands and actual page1/SMC/bank protocols.',
                   timing='Earlier +10CPU estimate covers only the described body/Game/bbox repack. Other real Nr dispatch costs must be measured; this is not a final Bill parity result.',
                   limits=['Plan is not an implemented engine or new native evidence.',
                           'No new bank/RAM/CHR lease, geometry or physics change authorized by this plan.',
                           'Quick and Arthur require genuine later source composition; private source passes are not shared readiness.']))
