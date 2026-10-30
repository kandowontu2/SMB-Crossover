"""Keep qualified FF combat/terrain and common-protocol source stages revertible."""
from pathlib import Path
import json
from checkpoint_roster_progress_1030_v2 import R,save,sha


def packet(relative,expected):
    p=R/relative
    assert sha(p)==expected,p
    h=json.loads(p.read_text());bindings=dict(h['bindings'])
    bindings[str(p)]=sha(p)
    bindings[str(Path(__file__).resolve())]=sha(__file__)
    for name,digest in bindings.items():assert sha(name)==digest,name
    return h,bindings


if __name__=='__main__':
    h,b=packet('build/final-fantasy-host-combat-qualified-v3/handoff.json',
               '6773102feabdb2983d06b4b61fce4c6a62b1cba3865c21092c18b2f77bb1c2b6')
    assert h['passed'] and h['host_combat_bytes']==492 and not h['full_Main']
    save('ff-native-combat-consumers',dict(status=h['status'],
        source_image_sha256=h['image_sha256'],API=h['API'],counts=h['counts'],
        source_change='Eight-byte selected-owner guard repairs foreign Fresh mutation; original CORE/ART/CHR/publisher unchanged.',
        limits=h['remaining']),b)
    h,b=packet('build/final-fantasy-host-terrain-qualified-v1/handoff.json',
               '6f2ca05db6f2b5fa4b7e846e57aebf1c0169827cf51cc49909911d9e0dc62044')
    assert h['passed'] and h['host_terrain_bytes']==583
    save('ff-source-native-terrain-consumers',dict(status=h['status'],
        source_image_sha256=h['image_sha256'],API=h['API'],counts=h['counts'],
        retained_failure=h['retained_failure'],limits=h['remaining']),b)
    h,b=packet('build/character-host-union-rogue-v2/handoff.json',
               '2c59d22089a3796c20fa44c0119a8d3c1abfa47af4239090a78b85690bbf6bb1')
    save('joint-common-protocol-source',dict(
        status='SOURCE_SEMANTICS_PASS_PERFORMANCE_HOLD_NO_NATIVE_INSTALL',
        ROM_sha256='445436c74a5cf4a514a74e43a13effed26e8c3c6df5b45abaa3b9ffa5f77dcf9',
        source_changes='Actual scheduler/Main/audio consumers use dedicated FamilyMainCommit5FFF; final global-clear operand5F00 to5EFF preserves it. Original PNhistory corruption retained separately.',
        CPU=dict(foreign_Main_cases=282,constructor_ABI_cases=512,
                 actual_constructor_ExRAM_stores=4712,real_constructor_NMIs=9424,
                 real_constructor_IRQs=9424,gate_interrupt_cuts=192,
                 retire_IRQ_cuts=18,PN_state_canary_cases=18),
        limits=['Measured Bill cost remains735CPU above parent per active Main in the compared source fixture; timing is an integration blocker.',
                'All original instruction addresses retained; semantics alone does not prove native cadence.',
                'DK flagpole repair and further route optimization are separate genuine source successors; no new shared admission or native qualification.']),b)
    p=R/'docs/qa/host-integration-progress-2026-10-30.json'
    j=json.loads(p.read_text())
    j['root_completed_this_continuation'] += [
        'FFcombat private492B now qualified: native geometry/HP/source contacts/9216genuine defeat-index cases/48actual deferred score-digit cases/1062realvectors. GenuineNewEnemy preservesAPXY/all64flags; sourceFresh foreignguard corrected. Flash2 aging/render and actualhooks remain parent work.',
        'FFterrain private583B B900..<BB47 implements real exact source bounds/native cells/wall and ceiling responses.4752queries/720sourceboxes/378ceiling/16worldwall/24realnativeblock+item writers pass.1941normal-lagNMI/IRQcuts preserveall143FFbytes/33SMC/livepage1.',
        'Real nativeBG staged-route fixture caught first FFterrain ceilingX112to127 displacement despite passing leaves. Two-byte actualY-resolution commit before native sides repairs all24actualBGcases; original581B negative retained. These selectors are explicitly fixture routes, not a source-linked cart/Main claim.',
        'Actualjoint445436c7 sourcecommon-protocol stage passes282foreignMain/512clearABI/18848realconstructorvectors and PN128history/28hitmask/4capsule canaries. +735BillCPU remains performanceHOLD; no shared promotion.'
    ]
    j['active_work']['Final_Fantasy']='Qualified combat492B +terrain583B source consumers and actualnativeBG staged-selector controls frozen. Genuine32KBWRAM loader/sourcecart including ROM-onlycoldportrait in progress; current host still lacks selected22Mainroutes. Actualhandlerrow/gates are next. Fullbody/effect/palette/music/pickup/flash-aging integration and nativeadmission remain open.'
    j['active_work']['joint_resource_base']='Dedicated5FFF actualsource445436c7 semantics qualified, with real9424NMI+9424IRQ constructorcuts and282foreignMain. Bill+735CPU is open; agent has exactprofile of repeatedbegin/end andforeignDrawShots/effects/drop dispatch. GenuineDK22B rebase4154 source controls passing, route optimization next. No native grant/sharedinstall.'
    j['active_work']['Arthur']='Private2846 source/native has unconditionalrequiredblackink,212lag/400. New ead1 renderer preserves complete body via protected prefix plus exact tail permutation/stablefairpriority,9024actualhardware8spriteposecases. FullDrawAllABI/vector successor underway; added559..1988CPU bridge measured, severe lag still open; no nativegrant/installation.'
    j['measured_workspace_bytes']=36658084287
    p.write_text(json.dumps(j,indent=2)+'\n')
