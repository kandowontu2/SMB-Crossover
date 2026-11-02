"""Record native menu acceptance and bounded WWF traversal negatives precisely."""
import json
from pathlib import Path
from prepare_selected_native_packet_v1 import R, sha
from build_storage_guard_v1 import preflight
from nightly_patch_guard_v1 import check

O = R / 'build/roster-progress-1102-v4'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    O.mkdir(exist_ok=True)
    storage = preflight(private_root=O, fresh=True)
    nightly = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
    pin = '1966a4883a888a5e62f90c4d3e96d25ecf028ddd7d714214727793418d633243'
    assert sha(nightly) == pin and check(nightly)['passed']
    menu = R / 'build/bub-menu-candidate-1102-v2/native-menu3'
    result, binding = read(menu / 'capture/result.json'), read(menu / 'capture/binding.json')
    assert result['passed'] and binding['exit_code'] == 0
    assert result['positions'] == 33 and result['observations'] == 55
    assert result['active_data_writes'] == result['late_enables'] == 0
    runs = []
    for root in ['hogan-full11-1102-v3', 'hogan-gap-probe-1102-v4', 'hogan-gap-probe-1102-v5']:
        p = R / 'build' / root / 'native'
        ready, b, q = read(p / 'ready.json'), read(p / 'capture/binding.json'), read(p / 'capture/result.json')
        assert ready['ROM_sha256'] == b['ROM_sha256'] == pin
        assert b['exit_code'] == 1 and not q['passed'] and q['reason'] == 'lost-life'
        for path, h in ready['bindings'].items():
            assert sha(path) == h, path
        item = dict(root=root, result=q, ready_SHA256=sha(p / 'ready.json'))
        if (p / 'capture/flights.json').exists():
            item['jump_aggregates'] = read(p / 'capture/flights.json')
        runs.append(item)
    cp = R / 'docs/qa/checkpoints/2026-11-02/hogan-gaps-v5'
    assert not cp.exists()
    cp.mkdir(parents=True)
    proof = dict(ROM_SHA256=pin, runs=runs, full11=False, helpers_added=False,
                 interpretation='The x+8 controller clears four pipes and the first pit, then '
                 'loses a life at the next opening pit. Its last jump starts1368, reaches '
                 'minimumY110 and ends1412. The later x+4 policy walks off without a second '
                 'jump. Original directional attacks and a native helper proposal still '
                 'require source review; these inputs do not exhaust every intended ability.')
    (cp / 'receipt.json').write_text(json.dumps(proof, indent=2) + '\n', encoding='utf-8')
    p = R / 'docs/qa/helper-platform-inventory-1101.md'
    text = p.read_text(encoding='utf-8')
    old = ('Hogan now crosses all four1-1 pipes in a natural controller attempt without\n'
           'helpers, then fails the first gap under an early-jump policy. A subsequent\n'
           'native death repair is verified for all six WWF identities. No WWF helper\n'
           'placement or impossible-crossing claim follows from that unfinished route.')
    assert old in text
    text = text.replace(old, 'Hogan crosses all four 1-1 pipes and the first pit without helpers under\n'
                        'the later-edge controller. The next opening pit still fails: the x+8\n'
                        'launch starts at world X1368, rises from Y176 to Y110, and falls at X1412.\n'
                        'Waiting until x+4 loses ground support before a second jump can begin.\n'
                        'Original directional attacks and helper placement remain under review.\n'
                        'No WWF helper has been added or assigned a final location. Native death\n'
                        'recovery is verified for all six wrestlers. The route remains unfinished;\n'
                        'see `docs/qa/checkpoints/2026-11-02/hogan-gaps-v5/receipt.json`.')
    p.write_text(text, encoding='utf-8', newline='\n')
    p = R / 'docs/qa/continuation-current.json'
    q = read(p)
    assert q['installed_nightly']['ROM_sha256'] == pin
    q['goal_status'] = 'ACTIVE_INCOMPLETE'
    q['previous_goal_turn_classification'] = 'progress'
    q['Bub_Bob_resource_followup'].update(
        private_ingress_checkpoint='docs/qa/checkpoints/2026-11-02/bubble-native-ingress-v4',
        frontend_native_checkpoint='docs/qa/checkpoints/2026-11-02/bub-static-frontend-native-v4',
        frontend_native_result=result,
        remaining='Native static menu passes; v5 dedicated contact37, actual Main, original trap/timeout '
                  'and foreign ports pass private CPU tests. Final source-funded shared routing/ports '
                  'grant, composed native gameplay, confirmation admission and full1-1 are pending. '
                  'Installed nightly has no Bub/Bob admission.',
        frontend_native_negatives=['Importer pre-Lua failure retained.',
                                   'Observer Select/confirm priority error retained; corrected '
                                   'observer follows source Select-before-confirm and menu3 passes.'])
    q['Prince_resource_followup'].update(
        supplement_checkpoint='docs/qa/checkpoints/2026-11-02/prince-source-supplement-v2',
        payload_bytes=41880, physical_spare_bytes=1128,
        remaining='Original contact, landing, native point/material queries and 408-pose renderer '
                  'are source/CPU qualified in v2 supplement. New v7 private coordinate glue is '
                  'being compiled with original four-phase timing; state-code amendment, final '
                  'fit/loader, native controls and full1-1 remain pending.')
    q['WWF_death_followup']['traversal_checkpoint'] = str(cp.relative_to(R)).replace('\\', '/')
    q['WWF_death_followup']['next'] = 'Review original directional attacks and source-funded native helper reuse for the next opening pit; no helper added.'
    q['storage']['latest_build_check'] = storage
    p.write_text(json.dumps(q, indent=2) + '\n', encoding='utf-8')
    (O / 'receipt.json').write_text(json.dumps(dict(passed=True, nightly_unchanged=True,
                  native_menu=result, WWF_routes_complete=False, helpers_added=False,
                  storage=storage), indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(passed=True, nightly_unchanged=True, menu_positions=33,
                          WWF_routes_complete=False, helpers_added=False)))


if __name__ == '__main__':
    main()
