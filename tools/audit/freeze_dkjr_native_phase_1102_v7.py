"""Compact authoritative DK Jr phase/score input; no ROM, PNG, DBG or objects."""
import json,shutil,zipfile
from pathlib import Path
import prepare_dkjr_native_score_1102_v7 as P
R=P.R;O=P.O;W=P.W


def main():
    cpu=json.loads((O/'native-score-v7-CPU.json').read_text());phase=json.loads((O/'native-score-v7-phase-CPU.json').read_text());assert cpu['passed']and phase['passed']
    for q in [cpu,phase]:
        for rel,h in q['bindings'].items():assert W.P.sha((R/rel).read_bytes())==h,rel
    names=['prepare_dkjr_native_carry_1102_v4.py','check_dkjr_native_carry_1102_v4.py',
        'measure_dkjr_native_link_1102_v5.py','check_dkjr_native_link_1102_v5.py','audit_dkjr_hanging_art_1102_v5.py',
        'prepare_dkjr_native_phase_1102_v6.py','check_dkjr_native_phase_1102_v6.py',
        'prepare_dkjr_native_score_1102_v7.py','check_dkjr_native_score_1102_v7.py','freeze_dkjr_native_phase_1102_v7.py']
    source=[R/'tools/audit'/n for n in names]
    generated=[O/('native-score-v7'+s)for s in ['.s','.cfg','.bin','.lbl','-layout.json','-CPU.json','-phase-CPU.json']]
    # Retain aggregate evidence of inherited carry/landing/life and the art
    # difference, not the superseded generated component/source trees.
    generated += [O/n for n in ['native-carry-v4-CPU.json','native-link-v5-proof.json','native-phase-v6-CPU.json','hanging-art-v5.json']]
    packet=O/'native-phase-v7-qualified.zip';files=source+generated
    with zipfile.ZipFile(packet,'w',zipfile.ZIP_DEFLATED,9)as z:
        for p in files:
            item=zipfile.ZipInfo(p.relative_to(R).as_posix(),(1980,1,1,0,0,0));item.compress_type=zipfile.ZIP_DEFLATED;z.writestr(item,p.read_bytes())
    checkpoint=R/'docs/qa/checkpoints/2026-11-02/dkjr-native-phase-v7'
    q=dict(passed=True,source_only=True,native_playable=False,ROM_written=False,installed=False,archive_bytes=packet.stat().st_size,archive_SHA256=W.P.sha(packet.read_bytes()),
        component_bytes=cpu['component_bytes'],component_SHA256=cpu['component_SHA256'],header_reserved_spare=cpu['header_reserved_spare'],
        source_files=[p.relative_to(R).as_posix()for p in source],files={p.relative_to(R).as_posix():dict(bytes=p.stat().st_size,SHA256=W.P.sha(p.read_bytes()))for p in files},
        base_ROM_SHA256=P.PIN,donor_ROM_SHA256=P.D.SHA,original_credits='Nintendo — original NES Donkey Kong Jr. routines, state, art and controls from authenticated World Rev1 image.',
        inherited_checkpoint='docs/qa/checkpoints/2026-11-02/dkjr-native-world-v3',
        direct_rebuild='Compile archived native-score-v7.s with ca65 -g; ld65 -C native-score-v7.cfg. This authoritative exact assembly input avoids restoring historical expanded dependency trees.',
        source_phase_comparisons=sum(phase['checks'].values()),native_score_cases=cpu['checks'],native_phase_guards=phase['rejected_native_phase_guards'],
        movement=dict(original_jump_rise=15,latched_air_direction=True,two_original_vine_hands=True,original_pre_snap_platform_fall_injury=True),
        resources=dict(code_bytes=cpu['component_bytes'],nominal_code_carrier_pages=8,original_state_bytes=2048,measurement_context_bytes=256,immutable_art_currently_qualified_bytes=1728,
            nominal_art_pages=2,service_vector_budget=114,spare_after_vector_before_remaining_ports=cpu['header_reserved_spare']-114,host_grants=False),
        remaining=['Native world-fruit producer/current enemy capture/defeat/release token lifecycle','Native body/fruit/point8x16 OAM/CHR/palette/status presentation and camera/script constructor transport',
            'Typed actual Main/fullbox/head/side/contact/pickup/scene/events and public owner/cold/header/retire/IRQ/NMI/resource admission','Native controls and1-1; intended15px jump requires verified native platform/vine helpers at obstacles'],
        art_caveat='Actual hanging fruit is not always identical to falling sprite art. The existing1728B atlas is not claimed to close source hanging-fruit or point-popup presentation.',
        helpers_added=False,scope='Private compiled native terrain/platform/carry/life/control/source-phase/native-score readiness. Original actor imports are no longer self-JMPs in this native-profile1 phase. Native score service executes only in isolated legal Mario0 fixtures; no DK rawID/menu/ROM or fullnative/playability claim.')
    manifest=O/'native-phase-v7-qualified.json';manifest.write_text(json.dumps(q,indent=2)+'\n');checkpoint.mkdir(parents=True,exist_ok=True)
    for src,name in [(packet,'inputs.zip'),(manifest,'manifest.json')]:
        dst=checkpoint/name
        if dst.exists():assert src.read_bytes()==dst.read_bytes()
        else:shutil.copyfile(src,dst)
        assert src.read_bytes()==dst.read_bytes()
    print(json.dumps(dict(passed=True,checkpoint=checkpoint.relative_to(R).as_posix(),archive_bytes=q['archive_bytes'],archive_SHA256=q['archive_SHA256'],component_bytes=q['component_bytes'],git_files=[*q['source_files'],(checkpoint/'inputs.zip').relative_to(R).as_posix(),(checkpoint/'manifest.json').relative_to(R).as_posix()])))


if __name__=='__main__':main()
