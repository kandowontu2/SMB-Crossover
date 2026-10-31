"""Check actual source boundaries before reserving a private Thomas loader."""
from pathlib import Path
import hashlib
import json
import sys

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R / 'tools/audit'), str(R / 'tools')]
from wwf_resource_inventory_1031_v1 import fields
from check_tmnt_render_oa import address, location
from link_pit_rygar_sophia_audit_cpu import scoped_load

J = R / 'build/contra-force-world-roles-1031-v2/joint'
P = R / 'build/wwf-ready74-first-host-resource-v1/resource-contract.json'
O = R / 'docs/qa/checkpoints/2026-10-31/thomas-first-host-resource-v1'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists()
    prior = json.loads(P.read_text())
    assert prior['passed'] and prior['all_labels_exact']
    for path, digest in prior['bindings'].items():
        assert sha(path) == digest, path
    raw = (J / 'candidate.nes').read_bytes()
    assert sha(J / 'candidate.nes') == prior['current_sha256']
    bundle = scoped_load(J / 'candidate.nes')
    segs = [fields(line) for line in (J / 'candidate.dbg').read_text().splitlines()
            if line.startswith('seg\t')]
    base = 16 + 85 * 8192
    expected = [('CV3_GFX_85', 0xc000, 2268),
                ('DRAGON_POWER_ART', 0xc900, 2618),
                ('ROGUE_AUDIO_PAGES_1', 0xd900, 1792)]
    for name, start, size in expected:
        segment = next(s for s in segs if s['name'] == name)
        assert (segment['start'], segment['size']) == (start, size), name
        assert segment['ooffs'] == base + start - 0xc000, name
    assert address(bundle, 'DpAdmissionColdEnd') == 0xd33a
    a, z = base + 0x133a, base + 0x1900
    assert location(bundle, 'DpAdmissionColdEnd') == a
    assert raw[a:z] == bytes([255]) * 1478
    assert not [s for s in segs if s.get('size') and 'ooffs' in s
                and s['ooffs'] < z and a < s['ooffs'] + s['size']]
    first, last = 16 + 1048576 + 426 * 1024, 16 + 1048576 + 442 * 1024
    assert raw[first:last] == bytes(16 * 1024)
    assert not [s for s in segs if s.get('size') and 'ooffs' in s
                and s['ooffs'] < last and first < s['ooffs'] + s['size']]
    assert [address(bundle, 'R' + str(i)) for i in range(8)] == list(range(3, 11))
    files = [Path(__file__), P, J / 'candidate.nes', J / 'candidate.dbg', J / 'candidate.cfg',
             R / 'build/functional-roster-visuals58-v1/joint/dp-component.s',
             R / 'build/functional-roster-visuals58-v1/joint/dp-component.o',
             R / 'build/rogue-audio-page-relocation-v5/relocated/pages.o',
             R / 'docs/qa/checkpoints/2026-10-31/thomas-c2-cold-source-v1/handoff.json']
    receipt = dict(passed=True, source_only=True, native=False, installed=False,
         parent_sha256=sha(J / 'candidate.nes'),
         conditional_grant=dict(scope='Private Thomas source integration; no admission or physical hook grant.',
              CHR_pages=[426, 442], total_CHR_pages=16,
              resident=dict(physical_bank=85, C_view=[0xd33a, 0xd900],
                            A_alias=[0xb33a, 0xb900], bytes=1478,
                            file_range=[a, z], preimage_sha256=hashlib.sha256(raw[a:z]).hexdigest()),
              selected_RAM_banks=[1, 2, 3], new_global_or_ZP_bytes=0,
              exact_host_scratch_addresses=list(range(3, 11)),
              ready_owner='SelectedCharacter10, Thomas FmAlts40 only, complete matching cookie/epoch'),
         source_boundary_evidence=expected,
         restrictions=['Do not change existing CV3/DragonPower/Rogue audio bytes or labels.',
              'Literal00..07 in the frozen lab is not the host scratch grant:00..02 are native NMI-owned. Rebind true logical pointer pairs to imported actualR0..R7.',
              'This reserves16 CHR pages total; measure sparse zero/FF/template/art/metadata/audio storage rather than assuming a literal24KB carrier.',
              'No RAM opcode or selected-state write before full owner/cookie/epoch authentication. Use genuine current5FFF retirement and forced-blank loading.',
              'Loader must execute from stable reviewed A/C aliases while replacing mappings and restore real native interrupt/stack/map contracts.',
              'Actual source/CPU/NMI fit and root native review remain required before character admission.'],
         bindings={str(path.resolve()): sha(path) for path in files})
    O.mkdir(parents=True)
    path = O / 'resource-contract.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(dict(passed=True, contract=str(path), sha256=sha(path),
                         CHR_pages=16, resident_bytes=1478, host_R0=3)))


if __name__ == '__main__':
    main()
