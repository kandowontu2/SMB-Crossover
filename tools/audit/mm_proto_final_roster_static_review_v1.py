"""Independent read-only review/binding of ROOT's37 prepared static routes."""
from pathlib import Path
import argparse
import ast
import hashlib
import json
import re
import sys
import traceback
from mm_proto_pivot_routes_static_controls_v1 import generic, observer_case
from parodius_visibility_hud_static_startup_v1 import MOCK
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location

R = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
P = D / 'final-roster-static-preparation-ce635-v2'
PRIOR = D / 'final-roster-controller-preparation-ce635-v1'
B = D / 'root-render-audio-palette-hud-union-v2'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
put = lambda p, z: Path(p).write_text(json.dumps(z, indent=2) + '\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    assert not a.output.resolve().is_relative_to(R)
    a.output.mkdir(parents=True, exist_ok=False)
    counts = dict(semantic=0, startup=0, syntax=0)
    try:
        prep = json.loads((P / 'preparation.json').read_text())
        old = json.loads((PRIOR / 'readiness.json').read_text())
        assert prep['prepared'] and prep['source_only'] and not prep['native_run']
        assert prep['ROM_sha256'] == sha(B / 'candidate.nes') == 'ce635f6e8793d096ba50adec9cdf1fc2dd41fd487e4acd4d0972af03af9ea111'
        assert len(prep['previews']) == len(old['cases']) == 37
        assert not (P / 'native').exists()
        for f, h in old['bindings'].items():
            assert sha(f) == h, f
        packet_before = {str(f.resolve()): sha(f) for f in P.rglob('*') if f.is_file()}
        core = (P / 'tmnt_static_exec_dispatcher_v1.lua').read_text()
        assert sha(P / 'tmnt_static_exec_dispatcher_v1.lua') == '899878286b9ac199ad0a1b80852a5a902c8e77ba58571c0420bc0fcaa13783f2'
        assert core == (R / 'tools/audit/tmnt_static_exec_dispatcher_v1.lua').read_text()
        # Independent exact reversal of the only runner/controller changes.
        runner = (P / 'runner.py').read_text()
        prefix = 'dofile(' + json.dumps((P / 'tmnt_static_exec_dispatcher_v1.lua').as_posix()) + ')\n'
        suffix = '\nTMNT_STATIC_EXEC.install()\n'
        oldwrite = " (out/'harness.lua').write_text(core)"
        added = ' core=' + repr(prefix) + '+core+' + repr(suffix) + '\n' + oldwrite
        reverse = runner.replace(added, oldwrite, 1)
        reverse = reverse.replace(" p.add_argument('--prepare-only',action='store_true',help='Generate Lua only; no emulator')\n", '', 1)
        reverse = reverse.replace(' if a.prepare_only:return 0\n', '', 1)
        assert reverse == (D / 'current3cee-eight-routes-v1/runner.py').read_text()
        coord = (P / 'coordinator.py').read_text()
        rev = coord.replace('        if not passed:break\n', '', 1).replace("            if not entry['replay']['passed']:break\n", '', 1)
        for new, prior in [(P / 'runner.py', D / 'current3cee-eight-routes-v1/runner.py'),
                           (P / 'capture.py', D / 'current3cee-eight-routes-v1/capture.py'),
                           (P / 'selected-aggregate.json', PRIOR / 'selected-aggregate.json')]:
            rev = rev.replace(str(new).replace('\\','\\\\'), str(prior).replace('\\','\\\\'), 1)
        assert rev == (PRIOR / 'coordinator.py').read_text()
        assert (P / 'capture.py').read_bytes() == (D / 'current3cee-eight-routes-v1/capture.py').read_bytes()
        assert "'--timeout', '240'" in coord and 'default=240' in (P / 'capture.py').read_text()
        for name in ['runner.py','coordinator.py','capture.py']:
            compile((P / name).read_text(), name, 'exec')
        deps = D / 'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1'
        sys.path.insert(0, str(deps))
        from lupa.lua54 import LuaRuntime
        tests = [generic(LuaRuntime, core)]
        scenarios = ['normal_and_reuse','wrong_pc_sp_retains_inside','stack_and_return_wrap',
                     'wrong_entry_bank_then_valid','literal_no_return_bank_guard','different_return_and_stale_DMA']
        for name in ['legacy_chr_observer_of.lua','chr_commit_observer.lua']:
            module = (R / 'tools/audit' / name).read_text()
            for scenario in scenarios:
                before, after = [observer_case(LuaRuntime, core, module, static, scenario, name.startswith('legacy')) for static in [False, True]]
                assert before[:2] == after[:2], (name, scenario)
                tests.append(dict(module=name, scenario=scenario,
                    all_mock_files_and_ordered_reads_state_calls_exact=True,
                    dynamic_native_callbacks=before[2], static_native_callbacks=after[2], reads_and_states=len(before[1])))
                counts['semantic'] += 1
        rt = LuaRuntime()
        lua_files = sorted(P.rglob('*.lua'))
        for f in lua_files:
            rt.compile(f.read_text())
            assert not re.search(r'\b(?:True|False)\b', f.read_text())
            assert not re.search(r'\bemu\.removeMemoryCallback\s*\(', f.read_text())
            counts['syntax'] += 1
        b = scoped_load(B / 'candidate.nes')
        policy_map = {tuple(x['case'].split(':')):x for x in json.loads((PRIOR / 'policy-map.json').read_text())}
        start = []
        policy_bindings = []
        for row in prep['previews']:
            name, mode = row['identity'], row['mode']
            folder = P / ('preview-' + name + '-' + mode)
            policy = P / (name + '-' + mode + '-preview-policy.lua')
            original = Path(policy_map[name,mode]['preview']).read_text()
            assert policy.read_text().split('\n',1)[1] == original.split('\n',1)[1]
            assert (folder / 'policy.lua').read_bytes() == policy.read_bytes()
            # Rebound literal L fields must be the actual linked state, not
            # remembered addresses. Runtime wrapper aliases are separate.
            for symbol, value in re.findall(r'^L\.(\w+)=(\d+)\s*$', policy.read_text(), flags=re.M):
                if symbol in b['syms']:
                    assert address(b,symbol) == int(value), (name, symbol, value)
                    policy_bindings.append(dict(identity=name, symbol=symbol, value=int(value)))
            harness = (folder / 'harness.lua').read_text()
            assert harness.startswith(prefix) and harness.endswith(suffix)
            assert harness.count('TMNT_STATIC_EXEC.install()') == 1
            assert sha(folder / 'harness.lua') == row['harness_sha256']
            assert sha(folder / 'run.lua') == row['generated_run_sha256']
            assert not re.search(r'\bemu\.(?:write\w*|setState|loadSavestate|reset)\s*\(', policy.read_text())
            audit = (folder / 'audit.lua').read_text()
            assert not re.search(r'\bemu\.(?:write\w*|setState|loadSavestate|reset)\s*\(', audit)
            legacy = name in ['mario','luigi','megaman','samus','bill','lance','link','simon','pit','rygar','scrooge','bass','ryu','sophia']
            observer = (R / 'tools/audit' / ('legacy_chr_observer_of.lua' if legacy else 'chr_commit_observer.lua')).read_text()
            assert observer in audit
            runtime = LuaRuntime(unpack_returned_tuples=True)
            runtime.execute(MOCK + "\nL=setmetatable({},{__index=function()return 0 end});B=setmetatable({},{__index=function()return 0 end});emu.setInput=function()end")
            runtime.execute((folder / 'run.lua').read_text())
            n = runtime.eval('#callbacks')
            assert runtime.eval('callbacks[#callbacks].kind==emu.callbackType.exec and callbacks[#callbacks].lo==0 and callbacks[#callbacks].hi==65535')
            assert runtime.eval('TMNT_STATIC_EXEC.status().host_exec_dispatchers') == 1
            # The real mock host callback function is captured before install.
            # Guard its phase/count; emu.addMemoryCallback remains the real
            # Lua slot interceptor, so actual late exec registration is still
            # permitted and tested in the12 real-observer scenarios above.
            for frame in range(1,440):
                runtime.execute(f"state['ppu.frameCount']={frame};runevents(emu.eventType.inputPolled);runevents(emu.eventType.endFrame)")
            assert runtime.eval('#callbacks') == n
            start.append(dict(identity=name, mode=mode, full_startup_inactive_mock_frames=439,
                host_memory_callbacks=n, host_exec_dispatchers=1,
                Lua_exec_registrations=runtime.eval('TMNT_STATIC_EXEC.status().lua_exec_registrations'),
                actual_observer='legacy' if legacy else 'explicit-CHR', original_modules_unmodified=True))
            counts['startup'] += 1
        assert counts == dict(semantic=12,startup=37,syntax=187), counts
        # Current source/runtime/dependencies; no copying or mutation of the
        # ROOT preparation, ROM, policy source, emulator or user settings.
        source = json.loads((B / 'source-manifest.json').read_text())
        assert len(source) == 871
        bindings = dict(packet_before)
        bindings.update(old['bindings'])
        for rel,h in source.items():
            f = B / 'source' / rel
            assert sha(f) == h, rel
            bindings[str(f.resolve())] = h
        # Bind the executable literally selected by runner AND capture.
        m = re.search(r"'--emulator',('(?:[^'\\]|\\.)*')",runner)
        assert m
        emulator = Path(ast.literal_eval(m[1]))
        assert str(emulator).replace('\\','\\\\') in (P / 'capture.py').read_text()
        assert emulator.is_file() and (emulator.parent / 'MesenCore.dll').is_file()
        env_files = [emulator, emulator.parent / 'MesenCore.dll', emulator.parent / 'settings.json', emulator.parent / 'MesenNesDB.txt',
                     Path(sys.executable), R / 'tools/run_mesen.py', R / 'tools/audit/run_mesen_isolated.py']
        env_files += list(emulator.parent.glob('*.dll'))
        user = Path('C:/Mesen2/settings.json')
        if user.is_file():
            env_files.append(user)
        for word in ['--doNotSaveSettings','--nes.removeSpriteLimit=false','--nes.ramPowerOnState=AllZeros',
                     '--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false']:
            assert word in runner and word in (P / 'capture.py').read_text()
        environment = dict(executable=str(emulator), executable_sha256=sha(emulator),
            core=str(emulator.parent / 'MesenCore.dll'), core_sha256=sha(emulator.parent / 'MesenCore.dll'),
            portable_settings=str(emulator.parent / 'settings.json'), portable_settings_sha256=sha(emulator.parent / 'settings.json'),
            user_settings_context=str(user), user_settings_applied_unproved=True,
            explicit_CLI='8sprite limit, allzero RAM, nonrandomized CPU/PPU and mapper, doNotSaveSettings',
            Python=sys.version, Lua='Lua54', emulated_bound=18000, host_timeout_per_launch=240)
        extras = [*env_files, Path(__file__), R / 'tools/audit/root_final_roster_static_prepare_v2.py',
                  B / 'candidate.nes', B / 'candidate.dbg', B / 'candidate.lbl', B / 'candidate.map', B / 'proof.json', B / 'source-manifest.json',
                  P / 'preparation.json', PRIOR / 'readiness.json', PRIOR / 'policy-map.json',
                  D / 'tmnt-static-observer-native-ready-v1/receipt.json',
                  R / 'tools/playthroughs/roster_harness.lua', R / 'tools/playthroughs/roster_audit.lua',
                  R / 'tools/audit/legacy_chr_observer_of.lua', R / 'tools/audit/chr_commit_observer.lua', R / 'tools/audit/roll_render_observer.lua']
        pending = [Path(__file__),R / 'tools/audit/root_final_roster_static_prepare_v2.py']
        seen = set()
        while pending:
            f = pending.pop()
            if f in seen:
                continue
            seen.add(f)
            extras.append(f)
            for node in ast.walk(ast.parse(f.read_text())):
                names = [node.module] if isinstance(node,ast.ImportFrom) else [x.name for x in node.names] if isinstance(node,ast.Import) else []
                for name in names:
                    if name:
                        dep = R / 'tools/audit' / (name.split('.')[0]+'.py')
                        if dep.is_file():
                            pending.append(dep)
        extras += [f for f in deps.rglob('*') if f.is_file() and '__pycache__' not in f.parts]
        for f in extras:
            assert f.is_file(),f
            bindings[str(f.resolve())] = sha(f)
        assert packet_before == {str(f.resolve()):sha(f) for f in P.rglob('*') if f.is_file()}
        put(a.output / 'semantic-controls.json', tests)
        put(a.output / 'actual37-startups.json', start)
        put(a.output / 'actual-policy-symbols.json', policy_bindings)
        put(a.output / 'environment.json', environment)
        put(a.output / 'bindings.json', dict(sorted(bindings.items())))
        put(a.output / 'proof.json', dict(passed=True, source_mock_only=True, native_launches=0, native_granted=False,
            ROM_sha256=prep['ROM_sha256'], original_preparation_sha256=sha(P / 'preparation.json'),
            exact_runner_coordinator_reverse_and_capture_bytes=True, controller_bodies_unchanged=True,
            callback_module_sha256=sha(P / 'tmnt_static_exec_dispatcher_v1.lua'),
            source_files=871, source_manifest_sha256=sha(B / 'source-manifest.json'), counts=counts,
            generic_order_range_late_callback_controls=9, actual_observer_semantic_scenarios=12,
            actual_generated_startups=37, input_inactive_mock_frames_per_identity=439,
            exact_PC_SP_bank_and_original_missing_return_bank_guard_semantics=True,
            no_runtime_host_callback_mutation_in_covered_active_observer_models=True,
            ROOT_preparation_unchanged=True, bindings=len(bindings), bindings_sha256=sha(a.output / 'bindings.json'),
            environment_sha256=sha(a.output / 'environment.json'), semantic_sha256=sha(a.output / 'semantic-controls.json'),
            startup_sha256=sha(a.output / 'actual37-startups.json'), policy_symbol_sha256=sha(a.output / 'actual-policy-symbols.json'), tool_sha256=sha(__file__),
            limitations='Source and inactive/controlled Lua models only; not37native routes or host C++ mutation emulation. Actual startup exact effective settings/CPU/PPU/DMA still need native evidence. Original observer return closures have no bank predicate, retained honestly. Discovery/direct host240unchanged; stop-first/retries0. All sources/runtime/settings/inputs read-only. No game/adoption/launch.'))
        print(json.dumps(dict(proof=str(a.output / 'proof.json'), sha256=sha(a.output / 'proof.json'), bindings=len(bindings), counts=counts),indent=2))
    except BaseException as e:
        put(a.output / 'failure.json', dict(passed=False,native_run=False,error=repr(e),traceback=traceback.format_exc(),counts=counts))
        (a.output / 'failed-tool.py').write_bytes(Path(__file__).read_bytes())
        raise


if __name__ == '__main__':
    main()
