"""Freeze two unlaunched exact0a robot profiles and finite source controls."""
from pathlib import Path
import argparse
import hashlib
import json
import difflib
from final_item_abilities_run import lua
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location

R = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
B = D/'mm-proto-construction-pivot-candidate-v9'
P = D/'mm-proto-weapon-boundary0a-v1'
OLD = D/'mm-proto-weapon-boundary-v1/native-ready-v3'
SHA = '0a7dd88e6732bc189e432a9d55b18dd8f7ecf68a22e3b20f0a13ab7276241c09'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
get = lambda p: json.loads(Path(p).read_text())
put = lambda p, z: Path(p).write_text(json.dumps(z, indent=2)+'\n')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    assert not a.output.resolve().is_relative_to(R)
    a.output.mkdir(parents=True, exist_ok=False)
    assert sha(B/'candidate.nes') == SHA
    b = scoped_load(B/'candidate.nes')
    oldcfg = get(OLD/'native/config.json')
    oldscript = (OLD/'native/run.lua').read_text()
    oldprefix = 'FINAL_ITEM_PROGRESSIVE='+lua(oldcfg)+'\n'
    assert oldscript.startswith(oldprefix)
    unchanged = oldscript[len(oldprefix):]
    bindings, rows, diffs = {}, [], []
    for variant, folder, stem in [(0, 'mega-hard-ready-v2', 'mega'), (1, 'proto-hard-ready-v1', 'proto')]:
        ready = P/folder
        proof = get(ready/'readiness.json')
        assert proof['prepared'] and not proof['native_run'] and proof['ROM_sha256'] == SHA
        assert proof['identity']['variant'] == variant and proof['mode_numeric'] == 1
        assert not (ready/'native/result.json').exists()
        for name, value in get(ready/'bindings.json').items():
            assert sha(name) == value, name
            bindings[name] = value
        cfg = get(ready/'native/config.json')
        script = (ready/'native/run.lua').read_text()
        prefix = 'FINAL_ITEM_PROGRESSIVE='+lua(cfg)+'\n'
        assert script.startswith(prefix) and script[len(prefix):] == unchanged
        assert all(cfg[n] == oldcfg[n] for n in ['cases', 'charge', 'rush', 'primary', 'effect_records', 'dma_protocol', 'drop_arrays', 'smc_fields', 'irq_scroll_stores'])
        hook_checks = []
        for name, h in cfg['hooks'].items():
            if name == 'PrimaryArtReady':
                target = 'ProtoLegacyDrawShotsCold::Pointer';delta = 2
            elif name in ['finish', 'NmiReturn']:
                target = 'GameLoop' if name == 'finish' else 'NonMaskableInterrupt'
                delta = int(b['syms'][target]['size'], 0)-1
            else:
                target = name;delta = 0
            off = location(b, target)+delta
            assert h['address'] == address(b, target)+delta
            assert h['physical_bank'] == (off-16)//8192
            assert h['bytes'] == list(b['raw'][off:off+len(h['bytes'])])
            hook_checks.append(dict(hook=name, real_symbol=target, offset=delta, **h))
        art = get(P/(stem+'-art-v1')/'proof.json')
        live = get(P/(stem+'-live-models-v1')/'proof.json')
        assert art['passed'] and live['passed'] and art['variant'] == variant
        assert art['ROM_sha256'] == SHA and art['script_sha256'] == sha(ready/'native/run.lua')
        assert live['script_sha256'] == sha(ready/'native/run.lua')
        for sub in [ready, P/(stem+'-art-v1'), P/(stem+'-live-models-v1')]:
            for x in sub.rglob('*'):
                if x.is_file():bindings[str(x.resolve())] = sha(x)
        rows.append(dict(variant=variant, profile=proof['profile'], readiness=str(ready/'readiness.json'),
                         readiness_sha256=sha(ready/'readiness.json'), command=get(ready/'command.json'),
                         unchanged_actual_six_component_guard_body=True,
                         unchanged_cases_thresholds_costs_art_records_and_hardware_guards=True,
                         true_hook_checks=hook_checks, full_art_caller_cases=art['full_caller_cases'],
                         actual_art_callback_models=art['actual_pointer_callback_models'],
                         actual_component_callback_models=len(live['actual_generated_callback_models'])))
        diffs.append(dict(variant=variant, changed_config_fields=[n for n in sorted(set(oldcfg)|set(cfg)) if oldcfg.get(n) != cfg.get(n)]))
    files = [Path(__file__), R/'tools/audit/mm_proto_weapon_boundary_prepare_v4.py',
             R/'tools/audit/mm_proto_weapon_boundary_prepare_v5.py',
             R/'tools/audit/mm_proto_weapon_art_owner_controls_v2.py',
             R/'tools/audit/mm_proto_weapon_boundary_live_models_v3.py',
             R/'docs/qa/mm-proto-weapon-boundary0a-2026-10-26.txt',
             OLD/'readiness.json', OLD/'native/run.lua', OLD/'native/config.json',
             P/'mega-hard-ready-v1/failure.json', P/'mega-hard-ready-v1/failed-tool.py']
    for x in files:bindings[str(x.resolve())] = sha(x)
    put(a.output/'bindings.json', dict(sorted(bindings.items())))
    put(a.output/'source-delta.json', dict(config_only_against_old_prepared_script=True,
                                        actual_gameplay_guard_body_byte_exact=True, rows=diffs))
    put(a.output/'readiness.json', dict(prepared=True, native_run=False, native_granted=False,
        ROM_sha256=SHA, profile_count=2, per_profile_cases=6, profiles=rows,
        bindings=len(bindings), bindings_sha256=sha(a.output/'bindings.json'),
        source_delta_sha256=sha(a.output/'source-delta.json'), tool_sha256=sha(__file__),
        first_failure_retained='V4 incorrectly classified the genuine code alias RosterOamReady in the historically named ram config as RAM; V5 refreshes code aliases, asserts actual below8000 RAM unchanged. No native launch or game failure.',
        maximum_native_launches_authorized=0,
        limits='Both profiles source/CPU/mock prepared only, fresh grant required. Same declared powered tier/resources/arena/contact staging as prior3b fixture. No natural acquisition, allweapon, audible SFX or native Proto/charge/Rush visibility/cadence claim.'))
    print(json.dumps(dict(readiness=str(a.output/'readiness.json'), sha256=sha(a.output/'readiness.json'), bindings=len(bindings)), indent=2))


if __name__ == '__main__':
    main()
