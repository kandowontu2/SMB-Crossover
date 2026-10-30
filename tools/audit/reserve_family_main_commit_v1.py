"""Allocate one dedicated common publication byte after rejecting real PN overlaps."""
import json
from pathlib import Path
from checkpoint_roster_progress_1030_v2 import R, D, save, sha


if __name__ == '__main__':
    path = R/'build/character-host-union-common-protocol-v1/proposal.json'
    assert sha(path) == 'd526ba047e990c8f95c1814c893e644077e980b39f05cfca162ff46fe5ee2265'
    proposal = json.loads(path.read_text())
    assert proposal['request']['start'] == '5FFF' and proposal['request']['bytes'] == 1
    assert not proposal['future_5FFF_literal_claims']
    assert proposal['source_change']['instruction_bytes_new'] == [157,255,94]
    bindings = dict(proposal['bindings'])
    for item in list(bindings):
        if Path(item).suffix == '.json':
            child = json.loads(Path(item).read_text())
            for source, digest in child.get('bindings', {}).items():
                assert isinstance(digest, str) and len(digest) == 64, source
                assert source not in bindings or bindings[source] == digest, source
                bindings[source] = digest
    for item, digest in bindings.items():
        assert sha(item) == digest, item
    bindings[str(path)] = sha(path)
    bindings[str(Path(__file__).resolve())] = sha(__file__)
    name = 'family-main-commit-private-allocation'
    save(name, dict(
        status='ROOT_APPROVED_PRIVATE_COMMON_PROTOCOL_1BYTE_NO_SHARED_INSTALL',
        allocation=proposal['request'],
        replaces='RdsCommit at5FB6, which corrupts active Parodius history; standalone frozen leaves remain immutable.',
        retained_rejected_candidates=proposal['rejected_candidates'],
        source_evidence=dict(compiled_cases=len(proposal['compiled_cases']),
                             actual_source_files=proposal['source_files_audited'],
                             bound_source_files=proposal['all_bound_source_files'],
                             indexed_writer_groups=len(proposal['indexed_writer_groups']),
                             indirect_writer_groups=len(proposal['indirect_writer_groups']),
                             future_ledgers=proposal['future_allocation_ledgers_checked']),
        sole_compatible_source_clear_change=proposal['source_change'],
        genuine_consumers=proposal['consumers'],
        requirements=proposal['required_controls']+[
            'New private source successor only. Genuinely reassemble/rebind every actual scheduler/Main/audio consumer and old5FB6 alias; no carried numeric consumers or binary overlay.',
            'Declare FamilyMainCommit5FFF once as globally dedicated protocol state; selected-owner constructors must never claim or clear it.',
            'Preserve every other ExRAM byte reset, instruction address, native caller AXYP/SP and actual cycle cost; test constructor at every write with real NMI/IRQ.',
            'Use real RdsBoot initialization before enabling NMI. Existing standalone Rogue/SMB2 leaves do not become joint-qualified by this allocation.',
            'Retain db3ab7a0 native PN-history negative104to0 and all source/ABI failures; no source masking or normalized foreign bytes.'
        ],
        limits=['Allocation and explicit source-clear exception only. No PRG/ZP/header/CHR/WRAM growth.',
                'No new joint gameplay, timing parity, shared installation or native readiness claim.']), bindings)
    review = D/name/'root-review.json'
    reservation = D/name/'root-review-and-reservations.json'
    reservation.write_bytes(review.read_bytes())
    print(json.dumps(dict(reservations=str(reservation),sha256=sha(reservation))))
