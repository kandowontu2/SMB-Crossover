"""Review exact Prince159 lifetimes and emit a private native candidate only."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'build/prince-live-root-candidate-1103-v113'
P = ROOT/'build/prince-actor-1101-v1'
D = ROOT/'docs/qa/checkpoints/2026-11-03/prince-live-source-v113'
ALLOCATION = ROOT/'docs/qa/allocations/prince-live-lifetime-1103-v113.json'
NIGHTLY = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(exist_ok=False)
    proposal_path = P/'live-lifetime-proposal-v172.json'
    q = json.loads(proposal_path.read_text())
    assert q['passed'] and q['proposal_only'] and not q['ROM_written'] and not q['granted']
    for name, digest in q['bindings'].items():
        assert sha((ROOT/name).read_bytes()) == digest, name
    base = NIGHTLY.read_bytes()
    assert sha(base) == q['base_cf7_SHA256'] == 'cf7f157aa39493149b24039c190f09244ce68bc47f0a87f06f01adb47a2c70dd'
    manifest = json.loads((P/'backdrop-manifest-v159.json').read_text())
    prior = json.loads((P/'strike-manifest-v130.json').read_text())
    prior_rows = {r['file_offset']:r for r in prior['patches']}
    shared_offsets = {r['file_offset'] for r in q['exact_pending_shared_spans']}
    assert shared_offsets == {534352,535426,536080}
    raw = bytearray(base)
    touched = set()
    for row in manifest['patches']:
        offset = row['file_offset']
        before,after = bytes.fromhex(row['old_hex']),bytes.fromhex(row['new_hex'])
        assert len(before) == len(after) == row['bytes']
        assert sha(before) == row['old_SHA256'] and sha(after) == row['new_SHA256']
        assert raw[offset:offset+len(before)] == before
        assert not touched.intersection(range(offset,offset+len(after)))
        touched.update(range(offset,offset+len(after)))
        if row.get('physical_PRG') is not None and offset not in shared_offsets:
            assert after == bytes.fromhex(prior_rows[offset]['new_hex']), ('unapproved new shared change',offset)
        raw[offset:offset+len(after)] = after
    assert sha(raw) == q['proposed159_memory_SHA256'] == manifest['expected_memory_only_SHA256']
    for row in q['exact_pending_shared_spans']:
        offset = row['file_offset']
        new = bytes.fromhex(row['proposed159_hex'])
        assert bytes.fromhex(row['current_cf7_hex']) == base[offset:offset+len(new)]
        assert raw[offset:offset+len(new)] == new
        assert row['CPU_half_open'][1]-row['CPU_half_open'][0] == len(new)
    assert q['requested_conditional_execution_lifetimes'] == {
        'new_live_RAM3_execution':[0xBFA3,0xBFD8],
        'C2_installer_execution':[0xC766,0xC77F],
        'cold_packet_temporary_payload':[0xC200,0xC235],
        'cold_staged_installer_source':[0xC72E,0xC747],
        'existing_source_state_staging':[0xC100,0xC747]}
    irq = json.loads((P/'live-policy-ISR-v170.json').read_text())
    nested = json.loads((P/'post-return-nested-IRQ-CPU-v171.json').read_text())
    assert irq['passed'] and irq['real_IRQ_and_genuine_FF_NMI'] == {'IRQ':1177,'lagNMI':1208}
    assert nested['passed'] and nested['counts'] == {'lag_NMI_gather':1208,'nested_IRQ':777}
    assert irq['minimum_SP'] == 130 and nested['minimum_nested_IRQ_SP'] == 125
    frontend_path = ROOT/'docs/qa/allocations/prince-current-frontend-1103-v105.json'
    frontend = json.loads(frontend_path.read_text())
    assert frontend['granted'] and len(frontend['approved_exact_patches']) == 9
    for row in frontend['approved_exact_patches']:
        offset = row['file_offset']
        before,after = bytes.fromhex(row['old_hex']),bytes.fromhex(row['new_hex'])
        assert len(before)==len(after) and raw[offset:offset+len(before)]==before
        assert not touched.intersection(range(offset,offset+len(after)))
        raw[offset:offset+len(after)] = after
    expected = q['expected_private_native_with_unchanged_v105_frontend_SHA256']
    assert sha(raw) == expected == '6c9e85a94d34a4623d21789d5293c61af2ad14d214f5780f57613a51ae6bb25a'
    grant = dict(status='APPROVED_EXACT_PRIVATE_NATIVE_CANDIDATE_ONLY',granted=True,
        owner='Prince raw38 alternate on Excitebike slot29',base_ROM_SHA256=sha(base),
        approved_component_SHA256=q['proposed159_memory_SHA256'],expected_candidate_SHA256=expected,
        exact_shared_spans=q['exact_pending_shared_spans'],
        conditional_execution_lifetimes=q['requested_conditional_execution_lifetimes'],
        lifetime_conditions=q['staging_lifecycle'],A_C_map_contract=q['actual_C2_Amap_contract'],
        scope='Exact159+unchanged105frontend composition reviewed from original cf7 preimages. All57 direct proposal bindings verified, original already-granted other PRG patches remain identical130. Existing44carriers/runtime/state lifetimes only; no broad padding, physical-page or globalRAM grant. Approves one private emulator candidate and bounded control/death probes, not nightly/install or full-stage/audio/geometry qualification.',
        limits=[q['verification_limits'],q['grounded_followup'],
            'DK101 and auth83 are separate ungranted combined proposals; no additive resource assumption.'],
        bindings={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in (
            Path(__file__),proposal_path,P/'backdrop-manifest-v159.json',frontend_path)})
    assert not ALLOCATION.exists()
    ALLOCATION.write_text(json.dumps(grant,indent=2)+'\n')
    candidate = OUT/'prince-live-private.nes'
    candidate.write_bytes(raw)
    assert sha(candidate.read_bytes()) == expected
    for suffix in ('.lbl','.dbg'):
        old = P/('prince-private-v140'+suffix)
        candidate.with_suffix(suffix).write_bytes(old.read_bytes())
    files = [Path(__file__),proposal_path,ALLOCATION,
        ROOT/'tools/audit/prepare_prince_live_native_1103_v174.py',
        *(ROOT/name for name in q['bindings'])]
    files = list(dict.fromkeys(files))
    D.mkdir(parents=True,exist_ok=False)
    archive = D/'inputs.zip'
    with ZipFile(archive,'w',ZIP_DEFLATED,compresslevel=9) as z:
        for f in files:
            z.writestr(f.relative_to(ROOT).as_posix(),f.read_bytes())
    with ZipFile(archive) as z:
        for f in files:
            assert z.read(f.relative_to(ROOT).as_posix()) == f.read_bytes()
    assert archive.stat().st_size < 512000
    receipt = dict(passed=True,private_native_candidate=True,installed=False,
        candidate=str(candidate.relative_to(ROOT)),candidate_SHA256=expected,
        source_checkpoint=str(D.relative_to(ROOT)),archive_bytes=archive.stat().st_size,
        archive_SHA256=sha(archive.read_bytes()),
        source_files=list(dict.fromkeys([str(Path(__file__).relative_to(ROOT)),
            *q['durable_source_files'],'tools/audit/prepare_prince_live_native_1103_v174.py'])),
        review=grant['scope'],native_validation='Pending; Downloads remains cf7.',
        copied_sidecars='Only native-symbol sidecars from140. Private hooks remain individually byte-bound by159/174; no unchanged private-code debug claim.')
    for f in (D/'receipt.json',OUT/'receipt.json'):
        f.write_text(json.dumps(receipt,indent=2)+'\n')
    handoff = ROOT/'docs/qa/continuation-current.json'
    current = json.loads(handoff.read_text())
    current['Prince_native_current_1103'].update(status='EXACT159_LIFETIME_GRANTED_PRIVATE_NATIVE_PENDING',
        current_candidate=receipt['candidate'],current_candidate_SHA256=expected,
        current_lifetime_grant=ALLOCATION.relative_to(ROOT).as_posix(),
        current_source_checkpoint=D.relative_to(ROOT).as_posix())
    handoff.write_text(json.dumps(current,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))


if __name__=='__main__':
    main()
