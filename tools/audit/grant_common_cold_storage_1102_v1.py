"""Reserve source-proven resident pads for the shared cold owner manager."""
import hashlib
import json
from pathlib import Path
from prepare_selected_native_packet_v1 import R, sha

O = R / 'build/common-cold-storage-1102-v1'
P = R / 'build/prince-actor-1101-v1'
ROM = R / 'build/excitebike-pose-1101-v3/current4.nes'
PIN = 'cf1412eb78ed6531d2f7478c9790f96314a95f2f3fdd6c2b80bfbefd24fca3a8'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def bound(name):
    q = read(P / name)
    assert q['passed'], name
    for path, digest in q.get('bindings', {}).items():
        assert sha(R / path) == digest, (name, path)
    return q


def main():
    O.mkdir(exist_ok=True)
    assert sha(ROM) == PIN
    raw = ROM.read_bytes()
    declared = bound('resident-padding-proposal.json')
    playback = bound('resident-pad-consumers-v2.json')
    ingress = bound('resident-pad-ingress-v2.json')
    assert playback['ROM_SHA256'] == ingress['ROM_SHA256'] == PIN
    assert playback['all_nine_legal_track_state_machines_closed']
    assert playback['actual_source_code_and_data_reads_never_enter_pad']
    assert ingress['no_source_DMC_address_length_or_start']
    assert ingress['no_actual_source_C_E_mapping_to123']
    assert ingress['actual_all256_gate_identity_cases'] == 256
    assert ingress['actual37foreign_owner_retirement_and_Mac_reentry_cases'] == 37
    bank = 16 + 123 * 8192
    assert hashlib.sha256(raw[bank:bank + 8192]).hexdigest() == declared['whole_source_bank_exact']['sha256']
    spans = []
    for row in declared['declared_pads']:
        lo, hi = row['CPU_half_open']
        at = bank + lo - 0xa000
        assert row['physical_PRG_bank'] == 123 and row['bytes'] == hi - lo
        assert hashlib.sha256(raw[at:at + hi - lo]).hexdigest() == row['preimage_SHA256']
        spans.append(dict(physical_PRG_bank=123, CPU_half_open=[lo, hi], bytes=hi - lo,
                          file_offset=at, preimage_SHA256=row['preimage_SHA256'],
                          source_res_directive=row['source_res_directive']))
    assert sum(row['bytes'] for row in spans) == 247
    grant = dict(granted=True, owner='Shared authenticated cold owner manager', date='2026-11-02',
                 base_ROM_SHA256=PIN, resident_PRG_spans=spans,
                 source_consumer_closure='Nine exact source track cycles plus actual queue, restart, pause, title, retirement and DMC ingress.',
                 conditions=[
                     'One common allocation shared by Excitebike/Bub/Bob and later measured owners, never multiple competing writes.',
                     'Preserve every original Mac audio instruction and data byte outside the three source-declared pads.',
                     'Shared worker support must be measured per payload format. Full-page copy support does not imply support for Prince packed/compressed streams.',
                     'Existing Ex resident code may be factored only with its complete ABI, headers, SMC/map/PPU restoration and foreign retirement validated on the current cf parent.',
                     'Authenticate complete two-bank owner headers and retire genuine trapped actors before invalidation or overwrite.',
                     'Current raw37 cookie must bind the cf recovery payload, never a stale parent cookie.',
                     'Shared routing, menu admission and additional RAM are not granted by this storage reservation.'
                 ],
                 shared_router_granted=False, additional_RAM_granted=False,
                 raw39_reserved=True, menu_admitted=False, native_playable=False,
                 host_ROM_changed=False,
                 evidence={name: sha(P / name) for name in [
                     'resident-padding-proposal.json', 'resident-pad-consumers-v2.json', 'resident-pad-ingress-v2.json']})
    dest = R / 'docs/qa/allocations/common-cold-1102-v1.json'
    assert not dest.exists()
    dest.write_text(json.dumps(grant, indent=2) + '\n', encoding='utf-8')
    cp = R / 'docs/qa/checkpoints/2026-11-02/common-cold-storage-v1'
    cp.mkdir(parents=True, exist_ok=True)
    for name in grant['evidence']:
        (cp / name).write_bytes((P / name).read_bytes())
    (O / 'grant.json').write_text(json.dumps(grant, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(granted=True, resident_PRG_bytes=247, ROM_changed=False,
                          menu_admitted=False, shared_routing_granted=False)))


if __name__ == '__main__':
    main()
