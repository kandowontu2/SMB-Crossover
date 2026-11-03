"""Freeze private item/status/source-bbox work without implying owner admission."""
import json
import zipfile
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A

R, O = A.R, A.O


def main():
    names = [
        'prepare_dkjr_native_item_status_1102_v60.py',
        'check_dkjr_native_item_status_1102_v61.py',
        'check_dkjr_native_status_ingress_1102_v62.py',
        'check_dkjr_native_collector_1102_v63.py',
        'audit_dkjr_native_ingress_1102_v64.py',
        'prepare_dkjr_native_bbox_1102_v65.py',
        'check_dkjr_native_bbox_1102_v66.py',
        'check_dkjr_native_bbox_irq_1102_v68.py',
        'check_dkjr_native_bbox_port_irq_1102_v69.py',
        Path(__file__).name,
    ]
    sources = [R / 'tools/audit' / n for n in names]
    receipts = [
        'native-items-v60-layout.json', 'native-items-v61-negative.json',
        'native-items-v62-CPU.json', 'native-collector-v63-CPU.json',
        'native-ingress-v64-census.json', 'native-bbox-v65-layout.json',
        'native-bbox-v66-CPU.json', 'native-bbox-v68-IRQ.json',
        'native-bbox-v69-direct.json', 'native-bbox-v69-nested.json',
    ]
    for n in receipts:
        j = json.loads((O / n).read_text())
        assert bool(j['passed']) == ('negative' not in n), n
        for path, digest in j.get('bindings', {}).items():
            assert A.sha((R / path).read_bytes()) == digest, ('stale input', n, path)
    generated = [O / n for n in receipts]
    for stem, version in [('native-items', 60), ('native-bbox', 65)]:
        generated += [O / f'{stem}-v{version}.{ext}' for ext in ['s', 'cfg', 'bin', 'lbl']]
        generated += [O / f'{stem}-{kind}-v{version}.bin' for kind in ['pause', 'main', 'ports']]
    generated += [O / f'native-bbox-gate-v65.{ext}' for ext in ['s', 'cfg', 'bin', 'lbl']]
    prior = R / 'docs/qa/checkpoints/2026-11-03/dkjr-score-tail-v59/helper-manifest.json'
    # The durable root may name the copied manifest differently; identify only
    # its exact original payload, never extract the predecessor archive.
    if not prior.exists():
        prior = R / 'docs/qa/checkpoints/2026-11-03/dkjr-score-tail-v59/manifest.json'
    prior_data = prior.read_bytes()
    prior_json = json.loads(prior_data)
    assert prior_json['archive_SHA256'] == 'f64a968c9cbdddd0e4636aaed957ce7f99f05fd0c127d475445f44f64771b1eb'
    q = json.loads((O / 'native-bbox-v65-layout.json').read_text())
    direct = json.loads((O / 'native-bbox-v69-direct.json').read_text())
    nested = json.loads((O / 'native-bbox-v69-nested.json').read_text())
    assert direct['actual_interrupts'] == dict(IRQ=379, lagNMI=379)
    assert nested['actual_interrupts'] == dict(nestedIRQ=859)
    assert nested['minimum_ISR_SP'] == 130
    archive = O / 'native-bbox-v70-inputs.zip'
    members = []
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in sorted(set(sources + generated)):
            rel, data = p.relative_to(R).as_posix(), p.read_bytes()
            z.writestr(rel, data)
            members.append(dict(path=rel, bytes=len(data), SHA256=A.sha(data)))
    out = dict(
        passed=True, status='FROZEN_PRIVATE_NATIVE_ITEMS_STATUS_AND_SOURCE_BBOX',
        qualified=False, ROM_written=False, installed=False,
        native_owner_admitted=False, shared_grant=False, shared_mutation=False,
        archive=archive.relative_to(R).as_posix(), archive_bytes=archive.stat().st_size,
        archive_SHA256=A.sha(archive.read_bytes()), members=members,
        source_files=[dict(path=p.relative_to(R).as_posix(), SHA256=A.sha(p.read_bytes())) for p in sources],
        assembly=dict(body_bytes=q['body_bytes'], body_end=q['body_end'],
            body_spare=q['header_spare'], metadata_end=q['metadata_end'],
            metadata_spare=q['metadata_spare'], pause_thaw=q['labels']['DkPauseThaw'],
            implemented_rows=q['implemented_vector_rows'], unfinished_rows=q['unimplemented_rows'],
            new_unconditional_RAM=0),
        proposal=q['ungranted_shared_gate_proposal'],
        evidence=[
            '32 prepare/320 maturity/96 direct status and18 actual same-owner native WriteGameText cases; all160 buffer bytes except seven DK JR name tiles and native AXYP preserved, including nonzero buffer offsets.',
            '24 genuine unchanged MarioSourcePowerupCollision comparisons cover all four item types, both native score owners and three status tiers. This is a direct legal service fixture, not actual raw40 rare ingress qualification.',
            'Actual native Main census demonstrates legacy generic bounding box and native rare fallback bypassing private16/23/24. The census is successful negative coverage, not functional admission.',
            '432 genuine D2BD pose/facing/grip cases with current world/camera/Y and stale OAM origins preserve all original2048 bytes and transport the original shape to current body pixels. Actual GameCore reaches private16 once with the proposal in memory.',
            'All256 selectors/four flags and3060 foreign-header-reject full-state cases preserve the exact existing38B port behavior. Positive authenticated current Sh/Bub/Prince owners remain pending.',
            '379 actual IRQ and379 genuine FF lag-NMI PC/SP/A/C/I port/header/frame/source shapes plus859 independent nested native IRQ cuts preserve resumed GameCore/source/private/SMC state. Minimum ISR SP130; no I1 shape was reached in this fixture.',
        ],
        retained_negative=dict(path='native-items-v61-negative.json', kind='overbroad oracle',
            detail='The old comparison used another Mario0 owner buffer tail beyond the actual header. Distinct62 compares the same raw40 native pipeline with only its name callback suppressed; old negative remains immutable.'),
        immutable_prior=dict(manifest=prior.relative_to(R).as_posix(), manifest_SHA256=A.sha(prior_data),
            archive_SHA256=prior_json['archive_SHA256'], purpose='Frozen51..59 source/packet/score/actualFF dependencies; no recursive predecessor extraction.'),
        remaining=[
            'Latest cf7 Bub cookie/payload and authoritative Prince owner/cold/retirement/source fingerprint rebind; positive authenticated foreign owner parity required before the37B gate can be granted.',
            'Twelve CLR vector rows and actual raw40 item/bounce/contact/head/vine/menu caller authority remain unfinished. Direct service rows are not a substitute for actual ingress.',
            'Complete final payload-derived cookie/two-header cold copy/readback, real IRQ lifetimes and all owner transitions; no public/menu/ROM/native admission yet.',
            'No SMB fruit/vine/helper placements. Original15px jump retained; helper-assisted1-1 requires explicit placement proposal/inventory and root native verification. Focused-only Select/shared genuine DK portrait remain declared initial limitations.',
        ],
        scope='Private conditional resources and memory-only proposed source-funded native port. Historical owner fixture is not current cf7 or positive authenticated foreign qualification. No ROM/shared/menu writes, Mesen, installation or commit.',
    )
    (O / 'native-bbox-v70.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k: out[k] for k in ['passed', 'status', 'archive_bytes', 'archive_SHA256', 'assembly']}))


if __name__ == '__main__':
    main()
