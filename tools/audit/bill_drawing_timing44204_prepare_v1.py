"""One saved-success Bill drawing timing packet; metadata only, never native."""
from pathlib import Path
from argparse import Namespace
import contextlib
import csv
import io
import json
import re
import sys

import bill_early_cache_cpu_v1 as H
import current_bill_passive_timing_prepare_v1 as timing
from current_bill_enemy_timing_prepare_v1 import decoded_direct_JSRs
import current_roster_compact_11_v1 as route

R = route.ROOT
B = R / 'build'
ROM = B / 'bill_inert_pool.nes'
EXPECTED = '44204c9b573a82dd4838df1821afeaad8ffab8b264ebb234f31a8e156434ff5a'
PARENT = B / 'verification/bill-landing-candidate326-hard-ready-v1'
OLD = B / 'verification/bill-enemy-children326-ready-v2'
OUT = B / 'verification/bill-drawing-timing44204-ready-v1'
ADDED = ['PlayerGfxHandler', 'DrawMetasprite']
FIRST, LAST = 3443, 3503
put = lambda p, q: p.write_text(json.dumps(q, indent=2) + '\n', newline='\n')


def cpu_call_controls(b, profile):
    actual = []
    for outer, name in [('GameCoreRoutine', 'PlayerGfxHandler'), ('DrawAllMetasprites', 'DrawMetasprite')]:
        for inject in (False, True):
            q = H.setup(b, enemies=0, buttons=1)
            q.put(Player_State=0, Player_Y_Position=176, BillBodyPrevValid=1,
                  Player_X_Position=52, Player_PageLoc=3, NmiDisable=255)
            if name == 'DrawMetasprite':
                H.run(q, 'RosterGraphics')
            c, row = H.run(q, outer, stop=name)
            hook = next(h for h in profile['functions'] if h['name'] == name)
            assert c.pc == hook['pc'] and q.m.banks[(c.pc-0x8000)//8192] in hook['banks']
            sp = c.sp
            ret = (q.m[0x100+(sp+1)%256] + 256*q.m[0x100+(sp+2)%256] + 1) % 65536
            code = [q.m[ret-3+i] for i in range(3)]
            bank = -1 if ret < 0x8000 else q.m.banks[(ret-0x8000)//8192]
            if profile['smc_start'] <= ret <= profile['smc_end']:
                accepts = lambda pc, owner, op: (profile['smc_start'] <= pc <= profile['smc_end']
                    and op[0] == 0x20 and str(op[1]+256*op[2]) in profile['smc_targets'][name])
            else:
                accepts = lambda pc, owner, op: any(a['bank'] == owner and a['bytes'] == op
                    for a in profile['source_callers'][name].get(str(pc), []))
                assert not accepts(ret, -1, code)
            assert accepts(ret, bank, code)
            assert not accepts(0x5b00, bank, code)
            assert not accepts(ret, bank, [0x4c]+code[1:])
            wrong = code[:]
            wrong[1] ^= 1
            assert not accepts(ret, bank, wrong)
            irq = None
            if inject:
                before = (c.pc, c.a, c.x, c.y, c.p & 0xcf, c.sp)
                banks = q.m.banks[:]
                fields = H.smc_fields(b)
                smc = {a: q.m[a] for a in fields}
                assert not c.p & 4
                c.irq()
                steps = 0
                while (c.pc, c.sp) != (before[0], before[-1]) and steps < 3000:
                    c.step()
                    steps += 1
                assert (c.pc, c.a, c.x, c.y, c.p & 0xcf, c.sp) == before
                assert q.m.banks == banks and all(q.m[a] == v for a, v in smc.items())
                irq = dict(actual_hardware_IRQ=True, steps=steps, AXYP_SP_banks_SMC_restored=True)
            steps = 0
            while not (c.pc == ret and c.sp == (sp+2)%256) and steps < 50000:
                c.step()
                steps += 1
            assert c.pc == ret and c.sp == (sp+2)%256
            assert (-1 if ret < 0x8000 else q.m.banks[(ret-0x8000)//8192]) == bank
            assert c.sp != (sp+1)%256, 'The literal return close requires exactly restored SP'
            actual.append(dict(outer=outer, actual_entry=name, entry_pc=hook['pc'], entry_banks=hook['banks'],
                entry_SP=sp, return_pc=ret, return_bank=bank, return_JSR=code,
                actual_outer_prefix_steps=len(row['trace']), complete_callee_steps=steps,
                IRQ=irq, unknown_return_wrong_target_nonJSR_rejected=True,
                wrong_return_SP_does_not_close=True, scope='Real CPU caller/callee/IRQ, metadata predicate controls; not a standalone Lua callback VM execution.'))
    return actual


def main():
    resuming = OUT.exists()
    if resuming:
        failure = json.loads((OUT/'preparation-negative.json').read_text())
        assert not (OUT/'prepare-controls.json').exists() and not (OUT/'launch.json').exists()
        assert route.sha(OUT/'ready.json') == failure['generic_ready_sha256']
        assert route.sha(OUT/'run.lua') == failure['generic_run_sha256']
    result = json.loads((PARENT / 'result.json').read_text())
    parent = json.loads((PARENT / 'ready.json').read_text())
    assert result['passed'] and result['ROM_sha256'] == route.sha(ROM) == EXPECTED
    assert (result['frames'], result['polls'], result['completed_loops']) == (5992, 5991, 5058)
    inputs = PARENT / 'inputs.csv'
    saved = list(csv.DictReader(inputs.open(newline='')))
    assert len(saved) == 5991 and [int(q['poll']) for q in saved] == list(range(1, 5992))
    policy = Path(parent['config']['policy'])
    assert route.sha(policy) == parent['bindings'][str(policy)]
    trace = [{k:int(v) for k,v in q.items()} for q in csv.DictReader((PARENT / 'trace.csv').open(newline=''))]
    window = [q for q in trace if FIRST <= q['frame'] <= LAST]
    assert len(window) == 61 and all(q['engine'] == 8 and q['world'] == q['level'] == 0 for q in window)
    assert (min(q['x'] for q in window), max(q['x'] for q in window)) == (1888, 1938)
    assert max(q['foregroundCycles'] for q in window) == 38836
    old = json.loads((OLD / 'profile-config.json').read_text())
    old_ready = json.loads((OLD / 'ready.json').read_text())
    observer = B / 'bill_early_cache_timing_full.lua'
    assert route.sha(observer) == old_ready['bindings'][str(observer)]
    text = observer.read_text()
    assert text.count('emu.addMemoryCallback(') == 6 and text.count('emu.addEventCallback(') == 1
    assert not re.search(r'emu\.(?:write\w*|setInput|setState|loadSavestate|reset|stop)\s*\(', text)
    b = H.scoped_load(ROM)
    raw = b['raw']
    def bound(name, symbol=None, banks=None):
        symbol = symbol or name
        at, pc = H.location(b, symbol), H.address(b, symbol)
        banks = banks or [(at-16)//8192]
        code = list(raw[at:at+3])
        for bank in banks:
            assert list(raw[16+bank*8192+(pc&8191):16+bank*8192+(pc&8191)+3]) == code
        return dict(name=name, symbol=symbol, pc=pc, banks=banks, bytes=code)
    entries = [bound(h['name'], h['symbol'], h['banks']) for h in old['functions']] + [bound(n) for n in ADDED]
    assert entries[:24] == old['functions'] and len(entries) == 26
    assert [(h['pc'],h['banks']) for h in entries[-2:]] == [(0xa2bc,[1]), (0xa3f1,[4])]
    callers, smc, closure = timing.source_call_closure(ROM, raw, entries, H.address(b, 'JumpEngine'))
    direct = decoded_direct_JSRs(ROM, raw, entries)
    cross = []
    for name, rets in direct.items():
        for ret, owners in rets.items():
            for owner in owners:
                if owner not in callers[name].get(ret, []):
                    callers[name].setdefault(ret, []).append(owner)
                    cross.append(dict(function=name, return_pc=int(ret), owner=owner))
    controls = 0
    for h in entries:
        name = h['name']
        if not callers[name]:
            assert name in ['RosterMovement','RosterWeapons','RemainingDraw','PlayerGfxHandler']
            assert smc[name] == {str(h['pc']):True}
        for ret, owners in callers[name].items():
            for owner in owners:
                at = 16+owner['bank']*8192+((int(ret)-3)&8191)
                assert list(raw[at:at+3]) == owner['bytes'] and owner['bytes'][0] == 0x20
                accept = lambda bank, code: any(q['bank'] == bank and q['bytes'] == code for q in owners)
                assert accept(owner['bank'], owner['bytes']) and not accept(-1, owner['bytes'])
                assert not accept(owner['bank'], [0x4c]+owner['bytes'][1:])
                wrong = owner['bytes'][:];wrong[1] ^= 1
                assert not accept(owner['bank'], wrong)
                controls += 1
    returns = {}
    for rets in callers.values():
        for ret, owners in rets.items():
            for owner in owners:
                if owner not in returns.get(ret, []):returns.setdefault(ret, []).append(owner)
    profile = json.loads(json.dumps(old))
    profile.update(output=OUT.as_posix()+'/', ROM_sha256=EXPECTED, first_frame=FIRST, last_frame=LAST,
                   functions=entries, returns=returns, source_callers=callers, smc_targets=smc)
    assert profile['row_cap'] == 200 and profile['byte_cap'] == 1048576
    for name, value in profile['ram'].items():assert H.address(b, name) == value
    sy = b['syms']['FarcallJmpTarget_SMC'];seg = b['segs'][sy['seg']]
    assert seg['name'] == '"SMCCODE"' and profile['smc_start'] == int(seg['start'],0)
    assert profile['smc_end'] == int(seg['start'],0)+int(seg['size'],0)-1
    actual_cpu = cpu_call_controls(b, profile)
    if not resuming:
        with contextlib.redirect_stdout(io.StringIO()):
            route.prepare(Namespace(identity='bill', mode='hard', rom=ROM, expected_sha256=EXPECTED,
                                    output=OUT, frames=8000, policy=policy, replay=inputs))
    ready = json.loads((OUT/'ready.json').read_text());cfg = ready['config']
    assert cfg['limit'] == 8000 and cfg['capture_bytes'] == 512*1024*1024 and cfg['replay'] == inputs.as_posix()
    _, _, address, location, hook = route.linked(ROM)
    for kind, name, key in [('NMI','NonMaskableInterrupt','nmi'),('IRQ','IrqScrollSplit','irq')]:
        actual_banks = cfg['hooks'][key].get('banks',[cfg['hooks'][key]['bank']])
        banks = profile['interrupts'][kind]['banks']
        assert set(banks) == set(actual_banks)
        entry = bound(name, banks=banks);tail = hook(name, tail=True)
        assert set(profile['interrupts'][kind]['banks']) == set(banks)
        assert profile['interrupts'][kind] == entry
        assert profile['interrupts'][kind+'_return']['pc'] == tail['pc'] and tail['bytes'][0] == 64
        for bank in banks:assert raw[16+bank*8192+(tail['pc']&8191)] == 64
    assert profile['dma_complete'] == cfg['hooks']['dma_complete']
    generic = (OUT/'run.lua').read_text()
    anchor = 'dofile('+route.lua(route.SCRIPT.as_posix())+')\n'
    insertion = 'BILL_PASSIVE_TIMING='+route.lua(profile)+'\n'+'dofile('+route.lua(observer.as_posix())+')\n'
    assert generic.count(anchor) == 1
    run = generic.replace(anchor, insertion+anchor)
    assert run.replace(insertion,'',1) == generic and not re.search(r'\\u[0-9a-fA-F]{4}', run)
    (OUT/'run.lua').write_text(run,newline='\n')
    put(OUT/'profile-config.json',profile);put(OUT/'command.json',ready['command'])
    prep = dict(passed=True, native_run=False, Lua_VM_executed=False, ROM_sha256=EXPECTED,
        saved_success_result_sha256=route.sha(PARENT/'result.json'), saved_polls=5991,
        saved_inputs_sha256=route.sha(inputs), saved_trace_sha256=route.sha(PARENT/'trace.csv'),
        window=dict(first=FIRST,last=LAST,actual_rows=61,x_range=[1888,1938],
                    sampled_foreground_peak=38836,active_engine8_rows=61,first_trace=window[0],last_trace=window[-1],
                    selection='Centered around actual3473 source-duration sample peak; not old3500 work equivalence.'),
        added_entries=entries[-2:],total_spans=26,original24_entry_metadata_exact=True,
        source_JSR_positive_wrongbank_wrongtarget_nonJSR_controls=controls,
        actual_CPU_callers_and_complete_returns=actual_cpu,
        fresh_source_closure=closure,cross_window_direct_owners=cross,
        static_observer_sha256=route.sha(observer),guard_body_sha256=route.sha(route.SCRIPT),
        scope='Complete saved5991-poll successful44204 route, normal8000 bound/zero-death/25controlled1-2 guards. Timing only3443..3503,61completion buckets; no FPS/call omission/enemy-type inference. Actual native outcome pending.',
        limits='Warmup starts first-1; ISR gross/exclusive nesting and open spans/censored descendants must be retained. Literal inherited observer summary prose still says3560, but actual first_frame3443/last_frame3503 and frames field govern; code/guards are unchanged.')
    put(OUT/'prepare-controls.json',prep)
    ready['passive_drawing_timing'] = dict(window=[FIRST,LAST],added_functions=ADDED,total_spans=26,
        observer_reused_literal=True,callbacks_startup_only=True,strict_caller_SP_bank_JSR_SMC_ISR_checks=True,
        no_emulated_writes=True,source_controls=str(OUT/'prepare-controls.json'),
        exact_historical_ROM_scope=EXPECTED,no_native_safety_performance_claim=True)
    ready['environment'] = parent['environment']
    ready['storage'] = dict(total_per_run_bytes=2_000_000_000,total_per_run_files=64,
        one_compact_PPU_container_bytes=512*1024*1024,native_PNG_files=0,
        maximum_offline_distinct_selected_epochs_including_diagnostics=8,central_capture_lease_required=True,
        timing_CSV_rows=200,timing_CSV_bytes=1048576)
    ready['maximum_native_launches'] = 1;ready['native_grant_required'] = True
    deps = {Path(p) for p in ready['bindings']}
    deps.update([Path(__file__),Path(timing.__file__),Path(H.__file__),
        R/'tools/audit/current_bill_enemy_timing_prepare_v1.py',observer,
        OLD/'ready.json',OLD/'profile-config.json',PARENT/'ready.json',PARENT/'result.json',
        PARENT/'launch.json',PARENT/'trace.csv',inputs,
        OUT/'profile-config.json',OUT/'prepare-controls.json',OUT/'command.json',
        Path('C:/Mesen2/Mesen.exe'),Path('C:/Mesen2/MesenCore.dll'),Path('C:/Mesen2/settings.json')])
    if resuming:deps.add(OUT/'preparation-negative.json')
    for module in list(sys.modules.values()):
        path=getattr(module,'__file__',None)
        if path and ('py65' in str(path) or str(R/'tools/audit') in str(path)) and Path(path).is_file():deps.add(Path(path))
    ready['bindings'] = {str(p):route.sha(p) for p in sorted(deps)}
    put(OUT/'ready.json',ready)
    assert all(route.sha(p)==h for p,h in ready['bindings'].items())
    print(json.dumps(dict(ready=str(OUT/'ready.json'),sha256=route.sha(OUT/'ready.json'),bindings=len(deps),
        source_controls_sha256=route.sha(OUT/'prepare-controls.json'),owned_tool_sha256=route.sha(Path(__file__)),
        command=str(OUT/'command.json'),actual_CPU_call_controls=len(actual_cpu),window=[FIRST,LAST],native_run=False)))


if __name__ == '__main__':
    main()
