"""One unchanged current326 adaptive control after candidate death. No native."""
from pathlib import Path
import argparse
import contextlib
import csv
import io
import json

import current_roster_compact_11_v1 as route

R = route.ROOT
B = R / 'build'
CAND = B / 'verification/bill-inert-pool326-hard-ready-v2'
OUT = B / 'verification/bill-inert-pool326-baseline-hard-ready-v1'
ROM = B / 'zelda2_easy_glove.nes'
BASE = '32694243361bb1366f6fd64c054ea2451f86b2517fc020d9c2b5d66bbf07bfa0'
NEW = '44204c9b573a82dd4838df1821afeaad8ffab8b264ebb234f31a8e156434ff5a'
put = lambda p, q: p.write_text(json.dumps(q, indent=2) + '\n', newline='\n')


def main():
    assert not OUT.exists()
    ready = json.loads((CAND / 'ready.json').read_text())
    assert route.sha(CAND / 'ready.json') == '836acffb430c5a4781a019b655b6216c9b2df74f98364820cacb0a120287f683'
    for p, expected in ready['bindings'].items():
        assert route.sha(p) == expected, p
    result = json.loads((CAND / 'result.json').read_text())
    launch = json.loads((CAND / 'launch.json').read_text())
    assert not result['passed'] and result['reason'] == 'Zero-death 1-1 route' and result['frames'] == 1811
    assert result['ROM_sha256'] == NEW and launch['changed_inputs'] == [] and launch['exit_code'] == 1
    assert launch['settings_before'] == launch['settings_after']
    assert route.sha(ROM) == BASE
    cfg = ready['config']
    assert cfg['replay'] is None and cfg['limit'] == 8000
    policy = Path(cfg['policy'])
    assert route.sha(policy) == '17b0683a72af2046c7a17f9d16ccf3b0a8322eca7a55a8c0000b9f4a22208847'
    with contextlib.redirect_stdout(io.StringIO()):
        route.prepare(argparse.Namespace(identity='bill', mode='hard', rom=ROM,
                      expected_sha256=BASE, output=OUT, frames=8000, policy=policy, replay=None))
    rp = OUT / 'ready.json'
    baseline = json.loads(rp.read_text())
    bc = baseline['config']
    differences = {k for k in cfg if cfg[k] != bc[k]}
    assert differences == {'ROM_sha256', 'out', 'prefix'}, differences
    original = 'ROSTER_CONFIG=' + route.lua(bc) + '\n'
    new = 'ROSTER_CONFIG=' + route.lua(cfg) + '\n'
    body = (OUT / 'run.lua').read_text()
    assert body.count(original) == 1
    assert body.replace(original, new, 1) == (CAND / 'run.lua').read_text(), 'Literal generated guards/mechanics/metadata outside exact config differences'
    put(OUT / 'command.json', baseline['command'])
    comparison = dict(prepared_only=True, native_run=False, parent_ROM_sha256=BASE,
        failed_candidate_ROM_sha256=NEW, candidate_result_sha256=route.sha(CAND / 'result.json'),
        candidate_ready_sha256=route.sha(CAND / 'ready.json'),
        candidate_failure='Actual death1811/x851/y176/engine11, not a hardware failure; root cause pending matched baseline',
        config_differences=sorted(differences), all_other_config_RAM_hooks_equal=True,
        literal_generated_body_after_exact_config_normalization=True,
        same_actual_policy=route.sha(policy), same_runtime_environment=ready['environment'],
        unchanged8000_zero_death_25control12_guards=True,
        scope='ONE adaptive current326 baseline, not replay/extrapolation and not a candidate retry. No engine/controller/guard changes. ROOT owns launch.')
    put(OUT / 'matched-controls.json', comparison)
    baseline['environment'] = ready['environment']
    baseline['storage'] = ready['storage']
    baseline['maximum_native_launches'] = 1
    baseline['native_grant_required'] = True
    baseline['matched_candidate_negative'] = comparison
    deps = {Path(p) for p in baseline['bindings']}
    deps.update({Path(__file__).resolve(), CAND / 'ready.json', CAND / 'result.json', CAND / 'launch.json',
                 OUT / 'command.json', OUT / 'matched-controls.json',
                 Path('C:/Mesen2/Mesen.exe'), Path('C:/Mesen2/MesenCore.dll'), Path('C:/Mesen2/settings.json')})
    baseline['bindings'] = {str(p): route.sha(p) for p in sorted(deps)}
    put(rp, baseline)
    print(json.dumps(dict(ready=str(rp), sha256=route.sha(rp), bindings=len(deps),
                         native_run=False, command=baseline['command'])))


if __name__ == '__main__':
    main()
