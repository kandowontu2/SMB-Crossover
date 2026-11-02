"""Preserve actual cold handoffs and their palette/HUD negative without shipping it."""
import json
from pathlib import Path
from prepare_selected_native_packet_v1 import R, sha
from build_storage_guard_v1 import preflight
from nightly_patch_guard_v1 import check

O = R / 'build/bub-cold-palette-record-1102-v2'
FRONT = R / 'build/bub-menu-candidate-1102-v2'
PRIVATE = '00971c9fa4906440e1f52d37ca76b7adde287e902a31e72982dee171b35bfa60'
INSTALLED = '1966a4883a888a5e62f90c4d3e96d25ecf028ddd7d714214727793418d633243'


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def native(p):
    result, binding, ready = [read(p / n) for n in ['capture/result.json', 'capture/binding.json', 'ready.json']]
    assert result['passed'] and binding['exit_code'] == 0
    assert binding['ROM_sha256'] == ready['ROM_sha256'] == PRIVATE
    for name, h in ready['bindings'].items():
        assert sha(name) == h, name
    return dict(result=result, binding=binding, ready_SHA256=sha(p / 'ready.json'))


def main():
    O.mkdir(exist_ok=True)
    storage = preflight(private_root=O, fresh=True)
    dest = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
    assert sha(dest) == INSTALLED and check(dest)['passed']
    bub = FRONT / 'native-combined2-bub-cold'
    bob = FRONT / 'native-combined3-bob-cold'
    probe = R / 'build/bubble-bobble-source-1101-v1/native-palette-probe-1102-v1'
    rows = dict(Bub=native(bub), Bob=native(bob), passive_probe=native(probe))
    q = read(probe / 'capture/bub-palette-probe.json')
    assert q['passive'] and q['script_RAM_writes'] == 0 and q['ROM_sha256'] == PRIVATE
    assert q['final']['palette'][0] == 15
    assert q['final']['palette'][29:32] == [42, 38, 48]
    cp = R / 'docs/qa/checkpoints/2026-11-02/bub-cold-palette-negative-v1'
    assert not cp.exists()
    cp.mkdir(parents=True)
    proof = dict(private_ROM_SHA256=PRIVATE, installed_ROM_SHA256=INSTALLED,
        production_admitted=False, installed=False, full11=False, helpers_added=False,
        native_cold=rows, passive_palette_probe=q,
        failure='Actual cold handoffs succeed, but the sky remains black and the HUD header is incomplete/green. '
                'The opaque Bub sprite RGB is correct; original backdrop/header composition is missing.',
        next='Private v6 must preserve the original complete status packet while patching only the name and '
             'queue the source-native area backdrop before opaque body RGB. Then native controls, graphics, '
             'Easy contact policy, affected regressions, full1-1 and delivery remain to qualify.')
    (cp / 'receipt.json').write_text(json.dumps(proof, indent=2) + '\n', encoding='utf-8')
    (cp / 'actual-negative.png').write_bytes((bub / 'capture/active-owner.png').read_bytes())
    p = R / 'docs/qa/continuation-current.json'
    current = read(p)
    assert current['installed_nightly']['ROM_sha256'] == INSTALLED
    current['Bub_Bob_resource_followup'].update(
        shared_native_grant='docs/qa/allocations/bubble-shared-native-1102-v5.json',
        shared_native_source_checkpoint='docs/qa/checkpoints/2026-11-02/bubble-native-proxy-v5',
        resident_loader_granted=True, production_menu_admitted=False, menu_admitted=False,
        native_playable=False, private_native_ROM_SHA256=PRIVATE,
        private_cold_palette_checkpoint=str(cp.relative_to(R)).replace('\\', '/'),
        remaining=proof['next'], private_visual_failure=proof['failure'])
    current['WWF_death_followup']['authored_gap_reference'] = dict(
        source='src/level_tiles.s::L_GroundArea6', ROM_file_offset=20956, stream_bytes=101,
        SHA256='162fc0bf0e2e7bd2ecda0ac1bf3551ee5f45a3f116fa6343badda72005c0b4ec',
        stream_pair_offset=30, pair='6c02', page=5, pit_left_x=1376, pit_right_exclusive_x=1424,
        native_decoder='rowC/type0 -> Hole_Empty; low length2 -> three16px columns',
        note='Authored pit confirmed. Legacy full11 fixture2240 gap marker is inaccurate; genuine full-stage clears still reach active1-2.')
    current['WWF_death_followup']['helper_proposal'] = 'Source-compacted generic native actor28, isolated gate8/raw29/all6, center1400/left1376/Y208/width48; CPU only, no ROM/grant/assisted crossing yet.'
    current['goal_status'] = 'ACTIVE_INCOMPLETE'
    current['previous_goal_turn_classification'] = 'progress'
    current['storage']['latest_build_check'] = storage
    p.write_text(json.dumps(current, indent=2) + '\n', encoding='utf-8')
    (O / 'receipt.json').write_text(json.dumps(dict(passed=True, negative_preserved=True,
        private_candidate_installed=False, nightly_unchanged=True, checkpoint=str(cp.relative_to(R))), indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(preserved=True, Bub_cold=True, Bob_cold=True, visual_negative=True, nightly_unchanged=True)))


if __name__ == '__main__':
    main()
