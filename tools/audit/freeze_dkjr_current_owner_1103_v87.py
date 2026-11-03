"""Compact current-owner/native-ingress milestone; no shared admission claim."""
import json
import zipfile
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A

R,O=A.R,A.O


def main():
    names=[
        'check_dkjr_native_rare_gate_1103_v71.py','check_dkjr_native_bbox_foreign_1103_v72.py',
        'check_dkjr_native_bbox_foreign_1103_v73.py','prepare_dkjr_native_event_1103_v74.py',
        'check_dkjr_native_event_1103_v75.py','audit_dkjr_native_event_1103_v76.py',
        'check_dkjr_native_event_1103_v77.py','check_dkjr_native_rare_ingress_1103_v78.py',
        'prepare_dkjr_current_owner_1103_v79.py','check_dkjr_current_cold_1103_v80.py',
        'check_dkjr_current_cold_1103_v81.py','check_dkjr_current_foreign_1103_v82.py',
        'check_dkjr_current_main_1103_v83.py','audit_dkjr_current_main_1103_v84.py',
        'check_dkjr_current_main_1103_v85.py','check_dkjr_current_main_1103_v86.py',Path(__file__).name]
    sources=[R/'tools/audit'/n for n in names]
    receipt_names=[
        'native-rare-gate-v71.json','native-bbox-current-foreign-v72-negative.json',
        'native-bbox-current-foreign-v73.json','native-event-v74-layout.json',
        'native-event-v75-negative.json','native-event-v76-diagnostic.json','native-event-v77-CPU.json',
        'native-rare-ingress-v78-CPU.json','native-owner-proposal-v79.json',
        'native-current-cold-v80-negative.json','native-current-cold-v81-CPU.json',
        'native-current-foreign-v82-CPU.json','native-current-main-v83-negative.json',
        'native-current-main-v84-diagnostic.json','native-current-main-v85-negative.json','native-current-main-v86-CPU.json']
    for name in receipt_names:
        q=json.loads((O/name).read_text());assert bool(q['passed'])==('negative'not in name),name
        for path,digest in q.get('bindings',{}).items():
            assert A.sha((R/path).read_bytes())==digest,('stale',name,path)
    generated=[O/n for n in receipt_names]
    generated += [O/f'native-event-v74.{ext}'for ext in ['s','cfg','bin','lbl']]
    generated += [O/f'native-event-{kind}-v74.bin'for kind in ['pause','main','ports']]
    for stem in ['native-owner','native-selector']:
        generated += [O/f'{stem}-v79.{ext}'for ext in ['s','cfg','bin','lbl']]
    generated += [O/'native-owner-extra-v79.bin',O/'native-payload-v79.bin',O/'native-cookie-v79.bin']
    archive=O/'native-current-owner-v87-inputs.zip';members=[]
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in sorted(set(sources+generated)):
            rel,data=p.relative_to(R).as_posix(),p.read_bytes();z.writestr(rel,data)
            members.append(dict(path=rel,bytes=len(data),SHA256=A.sha(data)))
    proposal=json.loads((O/'native-owner-proposal-v79.json').read_text())
    main=json.loads((O/'native-current-main-v86-CPU.json').read_text())
    out=dict(passed=True,status='FROZEN_CURRENT_PRIVATE_OWNER_COLD_AND_NATIVE_INGRESS',qualified=False,
        ROM_written=False,installed=False,native_owner_admitted=False,resident_grant=False,menu_grant=False,
        archive=archive.relative_to(R).as_posix(),archive_bytes=archive.stat().st_size,archive_SHA256=A.sha(archive.read_bytes()),
        members=members,source_files=[dict(path=p.relative_to(R).as_posix(),SHA256=A.sha(p.read_bytes()))for p in sources],
        parent_nightly_SHA256=proposal['parent_nightly_SHA256'],parent_current_Prince_memory_SHA256=proposal['parent_memory_SHA256'],
        memory_only_SHA256=proposal['expected_memory_only_SHA256'],cookie=proposal['cookie'],
        assembly=dict(body_bytes=proposal['body_bytes'],body_spare=proposal['body_spare'],metadata_end=proposal['metadata_end'],metadata_spare=proposal['metadata_spare'],
            manager_bytes=proposal['manager_bytes'],extra_bytes=proposal['extra_bytes'],selector_bytes=proposal['selector_bytes'],foreign_UI_table=proposal['selector_labels']['ExForeignLo']),
        approved_native_gate_grant='docs/qa/allocations/dkjr-shared-gates-1103-v104.json',
        evidence=[
            'Current cf7 native rare classifier:131072cases,130560non40 exact target/AXYP/SP, only40 adds authority. Positive current Sh36/Ex37/Prince38/Bub39 cold/Fresh plus144full native bbox comparisons preserve foreign source/native/SMC/stack/maps.',
            '180actual fixed native stomp events restart genuine originalD257 once, including equal source states/host velocities;4source hitstop/defeat/unconstructed guards and30ordinaryMainepochs never infer bounce. Actual Easy HandlePECollisions Goomba/Koopa reaches EnemyStomped and original transition.',
            'Actual complete native GameCore item16/23/24 reaches for24legal item/score-owner/status cases.768real native head-range calls match unchanged fixed127:E1F0 AXYP/R0..7/private/maps exactly.',
            'New current resident proposal is531+92+176bytes, using source-compiled retirement/local-reject factors; ExForeignLo stays A7DA and its native indexed consumers remain unpatched. Typed11carrier11264B payload includes original art and measured helpers; hash-derived complete cookie.',
            'Complete physical cold/readback for Ex37/Prince38/Bub39/DK40;16ordered transitions;128bad-header bytes reject before private writes. All8192code bytes except16intentional final header commits,2048metadata and2304zeroed state match; genuineFresh initializes original state1/counter36.',
            '888actual positive constructed foreign public-row comparisons preserve full source/private/native/ZP/liveSMC/liveStack/maps/PPU/AXYP/SP.',
            '280actual current GameCore epochs in explicit legal native flatfloor: idle no drift;Right80+50;Left60minus38 exactly original fractional arithmetic;15px jump and latched aerialRight despite Left input. These are CPU controls, not Mesen/native stage acceptance.',
        ],
        descriptive_correction=dict(path='native-current-main-v86-CPU.json',field='rows[].source_jump_resets',
            actual_meaning='Counts all originalD257 state-transition initializations, including ground and landing, not just jump starts. Directional control has ground/takeoff/landing three transitions and only one jump.'),
        CPU_scope=dict(idle_mean_Main_CPU=main['rows'][0]['mean_Main_CPU'],right_mean_Main_CPU=main['rows'][1]['mean_Main_CPU'],
            actual_frame_cadence_measured=False,overwhelming_idle_cost_unresolved=True,shared_auth_optimization_owner='excitebike_sol61 coordinated current79 source, no shared fastpath granted'),
        retained_negatives=[
            dict(path='native-bbox-current-foreign-v72-negative.json',kind='constructor guard oracle',detail='ShFresh correctly rejected after fixture unblanked;73 keeps its genuine forced-blank boundary.'),
            dict(path='native-event-v75-negative.json',kind='dead-stack/observer oracle',detail='76 proves only original01DF/01E0 dead return-stack difference; metadata event resides inbank2.77 fixes comparison/observer only.'),
            dict(path='native-current-cold-v80-negative.json',kind='header publication oracle',detail='81 accounts for16intentional final committed header bytes instead of comparing them toFF source.'),
            dict(path='native-current-main-v83-negative.json',kind='invalid viewport fixture',detail='84firstwriter is native129:AA59 KeepOnscr with missing right boundary0;sourceactor staysX40.85supplies legal255 bound.'),
            dict(path='native-current-main-v85-negative.json',kind='fraction rounding oracle',detail='86genuine originalD6E1 proves60leftupdates floor minus37.5 to minus38, not minus37; no source code change.'),
        ],
        immutable_prior=dict(manifest='build/dkjr-native-source-1102-v2/native-bbox-v70.json',archive_SHA256='6556c307d4c96f705f6505f667715f14ac2418ae68a99dcc86770b012d630df1'),
        external_current_owner=dict(manifest='build/prince-actor-1101-v1/strike-manifest-v130.json',
            SHA256=A.sha((R/'build/prince-actor-1101-v1/strike-manifest-v130.json').read_bytes()),
            scope='Other-agent read-only direct inputs, not archived or mutated here. Preserve its compact checkpoint before expanded Prince outputs are pruned; no recursive historical rehydration.'),
        remaining=[
            'Resident fourth-owner loop/selector and focused-only DK/Jr menu are ungranted; actual native scene gate still admits37..39. New exact source/foreign/lifecycle proof and root grant required.',
            'Ten unsupported private rows remain explicitCclear; neither all37functional policies nor source/private menu admission is claimed.',
            'Current populated DK pause/foreign retirement, Sh/raw-invalid/virtual37 all-public parity, full constructor/death/respawn/scene/cold corruption and actual FF/NMI/nested audio lifetimes remain pending.',
            'Root owns native menu/gameplay/cadence/1-1.15px donor jump requires practical intended-vine/native-helper placement proposal; no SMB fruit/vine/helper placements or crossing is granted/verified. Shared DK family portrait/focused-only Select limitation retained.',
        ],scope='Compact qualified source slices and explicit proposal/negative receipts only. No NES/DBG/object files, shared mutation, native emulator, installation or commit.')
    (O/'native-current-owner-v87.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k]for k in ['passed','status','archive_bytes','archive_SHA256','assembly','CPU_scope']}))


if __name__=='__main__':main()
