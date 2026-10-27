"""Prepare two full Bill Hard routes with one bounded passive timing window.

Never launches an emulator. Reuses the qualified source-decoded caller closure,
controller and hardware guards; no source/runtime/ROM copies or seeded state.
"""
from pathlib import Path
import argparse
import contextlib
import hashlib
import io
import json
import re
import sys
import textwrap

import current_bill_passive_timing_prepare_v1 as previous
import current_roster_compact_11_v1 as route

R = route.ROOT
B = R / 'build'
BASE_SHA = '6be48337ffee66a22b22de9ce134d5db323649fb4de620c43bad4ca98b80f193'
NEW_SHA = '9ea11eab2fc5c373a3795b013f6ed9e0d5e9781891b2ae3bf40ad2556c27b85e'
OLD_PREP_SHA = '96825a1419459bdb8c17f6741612c0ed2fcfbbff55727426639e4130c3f44d77'
OLD_OBSERVER_SHA = '686e08d0c0b52f54807422befb43a0e96c335a302b50dd41983d87b28a90b86f'


def observer_successor():
    old = previous.OBSERVER.read_text()
    assert route.sha(previous.OBSERVER) == OLD_OBSERVER_SHA
    edits = [
        ('-- Bounded, read-only timing of an unchanged saved-input replay.',
         '-- Bounded, read-only timing during a full controller-only Bill route.'),
        ('timing_observation_complete=true,native_prefix_only=true,ROM_sha256=',
         'timing_observation_complete=true,native_prefix_only=false,ROM_sha256='),
        ('Original harness terminates at3560 with diagnostic finite-frame-bound FALSE, retaining all strict guards and closing its container; no route-clear claim.',
         'Only timing collection ends at3560. The unchanged route harness continues through controlled1-2 or its original8000-frame bound. This timing summary alone is not a route pass or matched-call FPS claim.')]
    changed = old
    for a, b in edits:
        assert changed.count(a) == 1
        changed = changed.replace(a, b)
    reverse = changed
    for a, b in reversed(edits):
        assert reverse.count(b) == 1
        reverse = reverse.replace(b, a)
    assert reverse == old
    assert not re.search(r'emu\.(?:write\w*|setInput|setState|loadSavestate|reset|stop)\s*\(', changed)
    assert changed.count('emu.addMemoryCallback(') == 6
    assert changed.count('emu.addEventCallback(') == 1
    target = B / 'bill_early_cache_timing_full.lua'
    assert not target.exists()
    target.write_text(changed, encoding='utf-8', newline='\n')
    return target, dict(parent_sha256=OLD_OBSERVER_SHA, successor_sha256=route.sha(target),
                       exact_reverse=True, changes=[dict(old=a, new=b) for a, b in edits],
                       semantics='Three comment/summary classifications only. Timing logic/callbacks/asserts unchanged; route limit is separately configured8000, no observer stop exists.')


def metadata(rom, cfg, out, observer, expected):
    """Reuse the exact qualified binding block, not its historical2082 setup."""
    source = Path(previous.__file__).read_text()
    assert route.sha(previous.__file__) == OLD_PREP_SHA
    first = '    raw, syms, address, location, hook = route.linked(rom)\n'
    last = '    text = OBSERVER.read_text()\n'
    assert source.count(first) == source.count(last) == 1
    block = source[source.index(first):source.index(last)]
    context = dict(route=route, scoped_symbols=previous.scoped_symbols,
                   source_call_closure=previous.source_call_closure,
                   rom=rom, cfg=cfg, out=out, OBSERVER=observer,
                   ROM_SHA=expected, re=re)
    exec(compile(textwrap.dedent(block), str(previous.__file__)+'::binding-block', 'exec'), context)
    profile = context['profile']
    assert profile['first_frame'] == 3500 and profile['last_frame'] == 3560
    assert profile['row_cap'] == 200 and profile['byte_cap'] == 1048576
    assert len(profile['functions']) == 17
    return profile, dict(binding_block_sha256=hashlib.sha256(block.encode()).hexdigest(),
                         source_proven_tail_return=context['tail_return'],
                         all17_source_caller_closure=context['closure'],
                         reuse='Exact qualified compiled binding/control block; fresh actual ROM/DBG metadata for this run. Historical ROM/result/saved-input assumptions are excluded.')


def prepare_one(rom, expected, out, observer, change):
    policy = R / 'tools/playthroughs/roster_samus_contra.lua'
    options = argparse.Namespace(rom=rom, output=out, expected_sha256=expected,
        identity='bill', mode='hard', frames=8000, policy=policy, replay=None)
    with contextlib.redirect_stdout(io.StringIO()):
        route.prepare(options)
    ready_path = out / 'ready.json'
    ready = json.loads(ready_path.read_text())
    cfg = ready['config']
    assert cfg['character'] == 3 and cfg['variant'] == 0 and cfg['mode_value'] == 1
    assert cfg['limit'] == 8000 and cfg['replay'] is None
    assert cfg['capture_bytes'] == 512*1024*1024
    profile, source = metadata(rom, cfg, out, observer, expected)
    original = (out / 'run.lua').read_text()
    anchor = 'dofile(' + route.lua(route.SCRIPT.as_posix()) + ')\n'
    assert original.count(anchor) == 1
    insertion = 'BILL_PASSIVE_TIMING=' + route.lua(profile) + '\n' + 'dofile(' + route.lua(observer.as_posix()) + ')\n'
    generated = original.replace(anchor, insertion + anchor)
    assert generated.replace(insertion, '', 1) == original
    (out / 'run.lua').write_text(generated, encoding='utf-8', newline='\n')
    (out / 'profile-config.json').write_text(json.dumps(profile, indent=2)+'\n')
    (out / 'command.json').write_text(json.dumps(ready['command'], indent=2)+'\n')
    ready['passive_timing'] = dict(functions=17, startup_static_return_PCs=len(profile['returns']),
        warmup_from_physical_frame=3499, detailed_actual_PPU_window=[3500,3560],
        expected_data_rows=61, expected_total_CSV_rows=62, CSV_max_rows=200, CSV_max_bytes=1048576,
        native_scope='Full unchanged8000-frame1-1 to controlled1-2 route, not deliberate3560 failure. Timing summary is separate and may be absent if the route fails/finishes before that window.',
        terminal_success='All original route checks plus natural1-2,25 completed controlled updates and>5px movement,zero deaths. No result is preclassified as PASS.',
        input='Same surviving original roster_samus_contra.lua and navigation dependency in both. Controller discovery, no per-poll saved2082 state assumptions; no game/resource/outcome writes.',
        timing_arithmetic='Inclusive excludes actualISRCPU; exclusive additionally excludes same-context measured childCPU. Completion buckets are not physical-frame integrals; do not add nested inclusive totals. Open spans at3560 censored.',
        comparison_limits='ActualPPU3500..3560 may contain different x/weapon/actors/call counts when optimized timing changes sampling. Report workload and matched-call costs separately; no direct FPS ratio from unequal windows.',
        source_boundaries=source, observer_successor=change,
        observer_startup_static=True, no_runtime_callback_registration=True,
        inherited_source_candidate_limits='Isolated RemainingWeapons V differs; whole actual caller qualified. Advanced admission routing+5..172cycles; native no-harm remains unproved.',
        hardware='Unchanged shared all256 source/value/OAMADDR/destination,attributeE3-only physicalRAM,render deadline,CHR latches,NMI/IRQAXY/P/SP/5SMC/actualbank-gap checks and motion/death/input/endpoint guards.')
    ready['storage'] = dict(total_per_run_bytes=2_000_000_000,total_per_run_files=64,
        full_PPU_container='one NESPPU01', container_bytes=cfg['capture_bytes'],
        record_limit=8008,native_PNG_files=0,native_per_frame_files=0,
        maximum_offline_selected_frames=8,timing_CSV_max_bytes=1048576,timing_CSV_max_rows=200,
        no_source_runtime_ROM_copies=True, central_capture_lease_required=True)
    ready['prepared_only'] = True
    ready['native_grant_required'] = True
    dependencies={Path(p) for p in ready['bindings']}
    dependencies.update({Path(__file__).resolve(),Path(previous.__file__).resolve(),previous.OBSERVER,
        observer,out/'profile-config.json',out/'command.json',
        B/'bill_early_cache_handoff.json',B/'bill_early_cache_controls.json',B/'bill_early_cache_build.json',
        B/'bill_early_cache_flagoff.json',R/'tools/audit/bill_early_cache_cpu_v1.py',
        Path('C:/Mesen2/Mesen.exe'),Path('C:/Mesen2/MesenCore.dll'),Path('C:/Mesen2/settings.json')})
    # Metadata decoding is host-only. Bind the actual imported local/Python CPU modules.
    for module in list(sys.modules.values()):
        f=getattr(module,'__file__',None)
        if f and ('py65' in str(f) or str(R/'tools/audit') in str(f)) and Path(f).is_file():
            dependencies.add(Path(f))
    ready['environment'] = dict(emulator='C:/Mesen2/Mesen.exe',core='C:/Mesen2/MesenCore.dll',
        observed_runtime_settings='C:/Mesen2/settings.json',settings_sha256=route.sha('C:/Mesen2/settings.json'),
        settings_writes=False,settings_copy=False,
        options=[a for a in ready['command'] if a.startswith('--option=')],
        note='Binds actual existing executable/core/adjacentsettings plus explicitCLI. No user settings restore or copy. ROOT central launcher rechecks these actual files before launch.')
    ready['bindings']={str(p):route.sha(p) for p in sorted(dependencies)}
    assert len(ready['bindings']) < 100
    ready_path.write_text(json.dumps(ready,indent=2)+'\n')
    return dict(ready=str(ready_path),ready_sha256=route.sha(ready_path),ROM_sha256=expected,
                bindings=len(dependencies),command=ready['command'])


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();out=a.output.resolve()
    assert out.is_relative_to(B.resolve()) and not out.exists()
    base=B/'samus_fixed_hud_current4a.nes';candidate=B/'bill_early_cache.nes'
    assert route.sha(base)==BASE_SHA and route.sha(candidate)==NEW_SHA
    handoff=json.loads((B/'bill_early_cache_handoff.json').read_text())
    assert handoff['source_CPU_qualified'] and handoff['native_unrun']
    assert handoff['candidate_sha256']==NEW_SHA and handoff['parent_sha256']==BASE_SHA
    observer,change=observer_successor()
    rows=[]
    for name,rom,expected in [('baseline6be',base,BASE_SHA),('candidate9ea',candidate,NEW_SHA)]:
        rows.append(prepare_one(rom,expected,out/name,observer,change))
    readies=[json.loads(Path(q['ready']).read_text()) for q in rows]
    a,b=[q['config'] for q in readies]
    allowed={'out','prefix','ROM_sha256'}
    assert {k for k in a if a[k]!=b[k]} <= allowed
    assert readies[0]['passive_timing']['observer_successor']==readies[1]['passive_timing']['observer_successor']
    assert readies[0]['environment']==readies[1]['environment']
    proof=dict(prepared_only=True,native_run=False,native_grant_required=True,
        cases=rows,maximum_native_launches=2,sequential_order=['baseline6be','candidate9ea'],
        owned_workers=1,stop_on_first_failure=True,retries=0,
        same_controller_policy=route.sha(R/'tools/playthroughs/roster_samus_contra.lua'),
        same_shared_hardware_body=route.sha(route.SCRIPT),
        same_profile_observer=route.sha(observer),
        pair_config_differences_only=sorted(allowed),
        note='ROOT owns launch/grant/lease. Actual route clear and61-frame timing observations pending. Do not infer matched-work performance before reviewing actual source calls/workloads.',
        bindings={str(p):route.sha(p) for p in [Path(__file__).resolve(),observer]+[Path(q['ready']) for q in rows]})
    (out/'pair-ready.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(dict(pair_ready=str(out/'pair-ready.json'),sha256=route.sha(out/'pair-ready.json'),cases=rows),indent=2))


if __name__=='__main__':
    main()
