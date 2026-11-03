"""Freeze the compact Ready handshake/source/async milestone; no ROM admission."""
import json
import zipfile
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A

R,O=A.R,A.O


def main():
    names=[
        'check_dkjr_entrance_order_1103_v88.py','prepare_dkjr_entrance_anchor_1103_v89.py',
        'prepare_dkjr_anchored_owner_1103_v90.py','check_dkjr_anchored_entrance_1103_v91.py',
        'check_dkjr_anchored_entrance_1103_v92.py','audit_dkjr_ready_domains_1103_v93.py',
        'check_dkjr_ready_domains_1103_v94.py','check_dkjr_anchored_lifetime_1103_v95.py',
        'check_dkjr_anchored_lifetime_1103_v96.py','check_dkjr_anchored_lifetime_1103_v97.py',
        'check_dkjr_anchored_irq_1103_v98.py','check_dkjr_pipe_reanchor_1103_v99.py',Path(__file__).name]
    sources=[R/'tools/audit'/name for name in names]
    receipts=[
        'native-entrance-v88-negative.json','native-entrance-v89-layout.json',
        'native-owner-proposal-v90.json','native-entrance-v91-negative.json',
        'native-entrance-v92-CPU.json','native-ready-domains-v93-census.json',
        'native-ready-domains-v94-CPU.json','native-anchored-lifetime-v95-negative.json',
        'native-anchored-lifetime-v96-negative.json','native-anchored-lifetime-v97-CPU.json',
        'native-anchored-v98-direct.json','native-anchored-v98-nested.json','native-pipe-reanchor-v99-CPU.json']
    for name in receipts:
        q=json.loads((O/name).read_text());assert bool(q['passed'])==('negative'not in name),name
        for rel,digest in q.get('bindings',{}).items():assert A.sha((R/rel).read_bytes())==digest,('stale',name,rel)
    generated=[O/name for name in receipts]
    for stem in ['native-entrance-v89','native-ready-domains-v93','native-owner-v90','native-selector-v90']:
        generated += [O/f'{stem}.{ext}'for ext in ['s','cfg','bin','lbl']]
    generated += [O/f'native-{prefix}-{kind}-v{version}.bin'for prefix,version in [('entrance',89),('ready-domains',93)]for kind in ['pause','main','ports']]
    generated += [O/'native-owner-extra-v90.bin',O/'native-payload-v90.bin',O/'native-cookie-v90.bin']
    archive=O/'native-entrance-ready-v100-inputs.zip';members=[]
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in sorted(set(sources+generated)):
            data=p.read_bytes();rel=p.relative_to(R).as_posix();z.writestr(rel,data)
            members.append(dict(path=rel,bytes=len(data),SHA256=A.sha(data)))
    proposal=json.loads((O/'native-owner-proposal-v90.json').read_text())
    direct=json.loads((O/'native-anchored-v98-direct.json').read_text())
    nested=json.loads((O/'native-anchored-v98-nested.json').read_text())
    out=dict(passed=True,status='FROZEN_PRIVATE_ENTRANCE_READY_SOURCE_AND_ASYNC',qualified=False,
        ROM_written=False,installed=False,native_owner_admitted=False,shared_resident_grant=False,menu_grant=False,
        archive=archive.relative_to(R).as_posix(),archive_bytes=archive.stat().st_size,archive_SHA256=A.sha(archive.read_bytes()),
        members=members,source_files=[dict(path=p.relative_to(R).as_posix(),SHA256=A.sha(p.read_bytes()))for p in sources],
        parent_nightly_SHA256=proposal['parent_nightly_SHA256'],parent_current_Prince_memory_SHA256=proposal['parent_memory_SHA256'],
        historical_memory_only_SHA256=proposal['expected_memory_only_SHA256'],cookie=proposal['cookie'],
        assembly=dict(body_bytes=proposal['body_bytes'],body_spare=proposal['body_spare'],metadata_end=proposal['metadata_end'],metadata_spare=proposal['metadata_spare'],
            historical_resident_manager=proposal['manager_bytes'],historical_resident_extra=proposal['extra_bytes'],historical_selector=proposal['selector_bytes']),
        Ready=dict(address=0xc8fe,values={'0':'cold/reset/unconstructed','1':'source constructed; awaits legitimate native engine8 entrance','2':'native post-entrance anchor imported; source phase may run'},
            direct_readers=8,direct_writers=3,indexed_aliases_excluded=21,original_indirect_sites_unchanged=23,
            exact_writers=['Cold clears only with invalid overlay/forcedblank/disabledinterrupts','ConstructSTA1','ResetSTA0','FirstvalidAnchorINC1→2'],
            native_Reset19='Actual65:B0C5 JMPB100 JSRCoRetire invalidates bothheaders/thaws. PrivateReady2 may remain in unreachable retiredRAM; nextcold clears it. It is not the privateReset19 leaf.'),
        evidence=[
            'Retained88 actual defect: ctor at0/high0 then genuine nativeentrance40/176/high1; oldfirstMain source remained248/15/state4.89 fixes one explicit firstvalid import; no fixedY/newRAM/velocity inference.',
            '92 genuine table-driven Entrance_GameTimerSetup/PlayerEntrance→firstGameCore anchors source32/191/Ready2 at actualnative40/176/high1. Nine pending gameplay guards do not advance original2048/HP/items/lives or emit staleOAM; stableunbankedzeroheader remains.',
            '94 all42 compiled public/worldroots/3807instructions: onlyConstruct1/Reset0/AnchorINC writeReady. All21 indexed/SMCpotential aliases sourcebounded belowC8FE; unchanged23 original fruit/render/descriptorindirect domains.',
            '97 earned capture1→firstD1AE2→terminal61→thaw62 preserves original60sourceupdates. Twelve populatedFresh15/scene36/ROMReset19/residentRetire cases unwind once, preserve nestedEngine9/different-area native timer and positive newbirth. Seventeenpending passivepolicies preserve original2048.',
            '98 firstanchor/import/FullBox/sourcefruit/ScoreFlush in fullGameCore:856IRQ+856actualFFlagNMI and4903independentnestedIRQ continuations. Fullprivate/R0..7/SMC/native/AXYP/SP exact except sourcebound outeraudio clocks; NmiSkippedonce/regularNMIexcluded. All reachedI1 foregroundshapes included; reachedcount0.',
            '99 actualAltEntrance2 table-drivenpipe starts belowviewport, remains sourcepending during95genuineentryupdates, nativechoosesX56/Y144/high1. Firstactualengine8 imports source48/159/Ready2 before originalphase; sourcecounter36/state1 retained throughoutentry.',
        ],
        interrupts=dict(direct=direct['actual_interrupts'],nested=nested['actual_interrupts'],minimum_direct_SP=direct['minimum_ISR_SP'],minimum_nested_SP=nested['minimum_ISR_SP'],I1_foreground_shapes=direct['I1_foreground_NMI_shapes']),
        retained_negatives=[
            dict(path='native-entrance-v88-negative.json',kind='actualintegrationdefect',resolved_by='compiled89 firstvalid nativeentrance handoff'),
            dict(path='native-entrance-v91-negative.json',kind='fixturelabel',resolved_by='92 uses actualpublished65:B0F8 scene36; no fictitious HuGenericFresh'),
            dict(path='native-anchored-lifetime-v95-negative.json',kind='actualpublicResetAPI oracle',resolved_by='96 diagnoses2 not0;97 asserts actualROMheaderretire, not privateReset'),
            dict(path='native-anchored-lifetime-v96-negative.json',kind='sameResetoracle detailed',resolved_by='97 publicReset19 headerinvalid/unreachableReady2 semantics; no runtimechange'),
        ],
        immutable_prior=dict(manifest='build/dkjr-native-source-1102-v2/native-current-owner-v87.json',archive_SHA256='b0c6ce8f6bb5414bf0c4fe17740a918a15c9f7c3092532d06ba7ad8a2c2a8b73'),
        external_Prince_model=dict(manifest='build/prince-actor-1101-v1/strike-manifest-v130.json',SHA256=A.sha((R/'build/prince-actor-1101-v1/strike-manifest-v130.json').read_bytes()),
            scope='Historical source-model input only. ActualPrince143/144 exposed entrance/palette/status defects; canonical149/159 successor is in progress. Resident531/92/176 DK factor is not additive with its selector/extra/finalizer funding. Recombine and requalify actual finalowner before admission.'),
        remaining=[
            'Combine final stablePrince manager/status/finalizer with DK fourth-owner factor and no-cache performance factor; prove exact sourcefunding/preimages/foreignABI/header/cold/retire/lifecycle/IRQ, then root grant. Historical90resident layout is ungranted.',
            'Actual native scene gate still admits37..39; exact owning40range extension and focused-onlyDK28/Jr40 Select/Start/name/pending/portrait/respawn persistence need proof/grant before composition. NativeReset19 is ROMretirement, so do not count its privatevector as publicexecution.',
            'Ten private policies remain explicitreject. No fullnative menu/gameplay/cadence/1-1 claim; rootowns Mesen/nativequeue. Source15px jump needs intendedvines/nativehelpers proposal/crossing; no stagefruit/vine/helper placement yet.',
            'Currentnative privateMain costs remain~47KCPU idle in historical86model; sharedcomplete-auth optimization is separatelyowned byexcitebike, no authenticationcache or globalwriterproof claimed.',
        ],scope='Compact directsource/compiledcomponent/negative/aggregateCPU receipts only. No NES/DBG/O/captureforest, sharedmutation, emulator, installation or commit. Root may copy this ZIP/manifest and explicit13sourcefiles; keep frozen inputs unchanged.')
    (O/'native-entrance-ready-v100.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k]for k in ['passed','status','archive_bytes','archive_SHA256','assembly','interrupts']}))


if __name__=='__main__':main()
