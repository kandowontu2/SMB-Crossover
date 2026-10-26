"""Freeze current source/runtime bindings for four unlaunched route cases."""
from pathlib import Path
import argparse
import hashlib
import json
import sys

R = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
B = D / 'mm-proto-construction-pivot-candidate-v9'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def put(p, value):
    p.write_text(json.dumps(value, indent=2) + '\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--packet', type=Path, required=True)
    a = ap.parse_args()
    assert not (a.packet / 'readiness.json').exists() and not (a.packet / 'native').exists()
    source = B / 'ready-v1/readiness.json'
    assert sha(source) == 'fb2f1aca3a9c60446a2fdbd6df772eb8da6b3ed737c578fe274dc49fcb0a628e'
    prior = D / 'mega-proto-pivot-routes0a-v1/readiness.json'
    preparation = json.loads((a.packet / 'preparation.json').read_text())
    controls = json.loads((a.packet / 'controls-v1/proof.json').read_text())
    assert preparation['passed'] and controls['passed'] and len(controls['tests']) == 13
    assert controls['native_launches'] == 0 and preparation['native_run'] is False
    bindings = json.loads(prior.read_text())['bindings']
    bindings.update(json.loads((source.parent / 'bindings.json').read_text()))
    for p, h in bindings.items():
        assert sha(p) == h, p
    env_source = D / 'mm-proto-construction-pivot-native-ready-v1/readiness.json'
    environment = json.loads(env_source.read_text())['environment']
    for name in ['emulator', 'core', 'worker_settings', 'user_settings']:
        assert sha(environment[name]) == environment[name + '_sha256'], name
        bindings[str(Path(environment[name]).resolve())] = sha(environment[name])
    extra = {Path(__file__), R / 'tools/audit/mm_proto_pivot_routes_static_prepare_v1.py',
             R / 'tools/audit/mm_proto_pivot_routes_static_controls_v1.py',
             R / 'tools/audit/parodius_visibility_hud_static_startup_v1.py',
             R / 'tools/audit/current3cee_eight_routes_run_v1.py', R / 'tools/audit/run_mesen_isolated.py',
             R / 'tools/run_mesen.py', R / 'tools/audit/tmnt_static_exec_dispatcher_v1.lua',
             R / 'docs/qa/mm-proto-pivot-routes-static-2026-10-26.txt', source, source.parent / 'bindings.json',
             D / 'tmnt-static-observer-native-ready-v1/receipt.json', env_source, prior, Path(sys.executable)}
    extra |= set(Path(environment['emulator']).parent.glob('*.dll'))
    lua = D / 'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1'
    extra |= {p for p in lua.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    extra |= {p for p in a.packet.rglob('*') if p.is_file()}
    for p in extra:
        bindings[str(p.resolve())] = sha(p)
    command = [sys.executable, '-B', str(a.packet / 'coordinator.py'), '--rom', str(B / 'candidate.nes'),
               '--archive', str(D), '--output', str(a.packet / 'native'), '--cases', 'megaman:easy', 'proto:easy',
               '--replay', '--frames', '18000']
    put(a.packet / 'command.json', command)
    bindings[str((a.packet / 'command.json').resolve())] = sha(a.packet / 'command.json')
    readiness = dict(prepared=True, source_mock_only=True, native_run=False, native_executed=False,
        ROM_sha256=preparation['ROM_sha256'], source_readiness_sha256=sha(source),
        maximum_native_launches=4, maximum_workers=1, native_workers=1, automatic_retries=0,
        stop_first_failure=True, cases=['megaman:easy', 'proto:easy'], command=command,
        environment=environment, unchanged_emulated_frame_bound=18000, unchanged_host_timeout_per_launch=240,
        source_mechanics_observers_policies_capture_guards_preserved=True,
        dispatcher_installed_once_last_at_startup=True, runtime_exec_callbacks_only_Lua_slots=True,
        controls_sha256=sha(a.packet / 'controls-v1/proof.json'),
        predecessor_readiness_sha256=sha(prior), preparation_sha256=sha(a.packet / 'preparation.json'),
        prior_dispatcher_native_receipt_sha256=sha(D / 'tmnt-static-observer-native-ready-v1/receipt.json'),
        new_native_observation_equivalence_unproved=True, bindings=bindings,
        launch_helper=str(R / 'tools/audit/current3cee_eight_routes_run_v1.py'),
        launch_helper_arguments=['--packet', str(a.packet), '--native-grant'],
        limits='Prepared only; separate ROOT grant required. Same original two controllers and independent fixed/direct-PPU captures. All new actual failures must remain, stop first without retry. Source-only mocks are not emulator/runtime equivalence. Per-live-shot fairness, every weapon, full-roster/matched performance and adoption remain separate.',
        tool_sha256=sha(__file__))
    put(a.packet / 'readiness.json', readiness)
    put(a.packet / 'catalog.json', {p.relative_to(a.packet).as_posix(): dict(bytes=p.stat().st_size, sha256=sha(p))
                                  for p in sorted(a.packet.rglob('*')) if p.is_file()})
    proof = dict(passed=True, native_run=False, native_grant=False, ROM_sha256=preparation['ROM_sha256'],
        readiness_sha256=sha(a.packet / 'readiness.json'), catalog_sha256=sha(a.packet / 'catalog.json'),
        maximum_launches=4, maximum_workers=1, bindings=len(bindings), controls=13,
        original_observer_semantic_cases=12, complete_generated_startups=2, command=command,
        source_report_sha256=sha(R / 'docs/qa/mm-proto-pivot-routes-static-2026-10-26.txt'), tool_sha256=sha(__file__))
    put(a.packet / 'freeze-proof.json', proof)
    print(json.dumps(proof, indent=2))


if __name__ == '__main__':
    main()
