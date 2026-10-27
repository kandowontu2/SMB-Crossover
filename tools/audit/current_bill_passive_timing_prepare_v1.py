"""Prepare one small saved-input Bill timing prefix. Never launches Mesen."""
from pathlib import Path
import argparse
import collections
import contextlib
import io
import json
import re
import sys

from py65.devices.mpu6502 import MPU
from py65.utils import conversions, devices

import current_roster_compact_11_v1 as route

ROOT = route.ROOT
ROM_SHA = '2082c19a7364920f828e97f70040d37f1f7059bde1ea136b5c2c4532324abf36'
OBSERVER = Path(__file__).with_name('current_bill_passive_timing_v1.lua')


def scoped_symbols(path):
    scopes, symbols = {}, []
    for line in path.read_text().splitlines():
        if not line.startswith(('scope\t', 'sym\t')):
            continue
        z = dict(q.split('=', 1) for q in line.split('\t', 1)[1].split(',') if '=' in q)
        if line.startswith('scope\t'):
            scopes[z['id']] = z
        elif 'val' in z:
            symbols.append(z)
    answer = {}
    for z in symbols:
        names, key = [], z.get('scope')
        while key in scopes:
            q = scopes[key]
            name = q.get('name', '""').strip('"')
            if name:
                names.append(name)
            key = q.get('parent')
        answer[tuple(reversed(names)) + (z['name'].strip('"'),)] = z
    return answer


def source_call_closure(rom, raw, functions, jump_engine):
    """Find real JSR owners through compiled, stack-neutral tail paths.

    Untyped ca65 spans are instructions; typed spans are data. Decode each
    instruction's actual opcode/length, not arbitrary ROM byte patterns.
    A normal JSR has only its post-return continuation here. Its entry is a
    separate caller candidate. JumpEngine is the explicit exception: it pops
    that JSR's return and dispatches through the following typed word table.
    """
    segments, spans = {}, []
    for line in rom.with_suffix('.dbg').read_text().splitlines():
        if line.startswith(('seg\t', 'span\t')):
            z = dict(q.split('=', 1) for q in line.split('\t', 1)[1].split(',') if '=' in q)
            if line.startswith('seg\t'):
                segments[z['id']] = z
            else:
                spans.append(z)
    lengths = dict(imp=1, acc=1, imm=2, zpg=2, zpx=2, zpy=2, rel=2,
                   inx=2, iny=2, abs=3, abx=3, aby=3, ind=3)
    nodes, words = {}, {}
    for z in spans:
        s = segments[z['seg']]
        if 'ooffs' not in s or not int(s['size'], 0):
            continue
        at = int(s['ooffs'], 0) + int(z['start'], 0)
        pc, size = int(s['start'], 0) + int(z['start'], 0), int(z['size'], 0)
        if not (16 <= at < 16 + 128 * 8192 and 0x8000 <= pc < pc + size <= 0x10000):
            continue
        key = ((at - 16) // 8192, pc)
        code = bytes(raw[at:at + size])
        if 'type' in z:
            if size % 2 == 0:
                for i in range(0, size, 2):
                    words[(key[0], pc + i)] = int.from_bytes(code[i:i + 2], 'little')
            continue
        name, mode = MPU.disassemble[code[0]]
        if name == '???' or lengths.get(mode) != size:
            continue
        node = dict(name=name, mode=mode, bytes=list(code), span=z['id'])
        assert key not in nodes or nodes[key]['bytes'] == node['bytes']
        nodes[key] = node
    # Genuine fixed-bank mirror instructions, not a blanket PC alias.
    mirrors = 0
    for (bank, pc), node in list(nodes.items()):
        if bank == 127 and pc >= 0xe000:
            at = 16 + 125 * 8192 + (pc & 8191)
            if list(raw[at:at + len(node['bytes'])]) == node['bytes']:
                nodes[(125, pc)] = dict(node, mirror_of_bank=127)
                mirrors += 1

    def target(key, pc):
        bank, here = key
        if 0x8000 <= pc < 0xa000:
            q = (126, pc)
        elif pc >= 0xe000:
            q = (125 if bank == 125 else 127, pc)
        elif here & 0xe000 == pc & 0xe000:
            q = (bank, pc)
        else:
            return None
        return q if q in nodes else None

    reverse, dispatches, indirect = collections.defaultdict(set), [], []
    for key, n in nodes.items():
        pc, code, name = key[1], n['bytes'], n['name']
        destinations = []
        if name == 'JSR' and int.from_bytes(bytes(code[1:]), 'little') == jump_engine:
            arms, at = [], pc + 3
            while (key[0], at) in words:
                q = target(key, words[(key[0], at)])
                if q is None:
                    break
                arms.append(q)
                at += 2
            assert arms and len(arms) < 128, ('Unproved JumpEngine word table', key)
            destinations = arms
            dispatches.append(dict(bank=key[0], pc=pc, arms=[list(q) for q in arms]))
        elif name == 'JMP':
            if n['mode'] == 'abs':
                q = target(key, int.from_bytes(bytes(code[1:]), 'little'))
                destinations = [q] if q else []
            else:
                indirect.append(dict(bank=key[0], pc=pc, bytes=code))
        elif name not in ('RTS', 'RTI', 'BRK'):
            if n['mode'] == 'rel':
                q = target(key, pc + 2 + (code[1] if code[1] < 128 else code[1] - 256))
                if q:
                    destinations.append(q)
            q = (key[0], pc + len(code))
            if q in nodes:
                destinations.append(q)
        for q in destinations:
            reverse[q].add(key)

    source_callers, smc_targets, reports, witnesses = {}, {}, [], []
    for h in functions:
        # Key includes the source stack delta remaining to the measured entry.
        seeds = [(b, h['pc']) for b in h['banks']]
        assert all(k in nodes for k in seeds), ('Missing real instruction entry', h)
        todo = collections.deque((k, 0) for k in seeds)
        paths = {(k, 0): None for k in seeds}
        while todo:
            key, delta = todo.popleft()
            for previous in sorted(reverse[key]):
                name = nodes[previous]['name']
                if name in ('TXS', 'BRK', 'RTI'):
                    continue
                change = -1 if name in ('PHA', 'PHP') else 1 if name in ('PLA', 'PLP') else 0
                state = (previous, delta + change)
                # This is a finite proof boundary, never a runtime allowance.
                assert -16 <= state[1] <= 16, ('Unbounded tail-path stack behavior', h['name'], previous)
                if state not in paths:
                    paths[state] = (key, delta)
                    todo.append(state)
        neutral = {k for k, delta in paths if delta == 0}
        callers, records = {}, []
        for key, n in sorted(nodes.items()):
            if n['name'] != 'JSR':
                continue
            operand = int.from_bytes(bytes(n['bytes'][1:]), 'little')
            q = target(key, operand)
            if q not in neutral:
                continue
            ret = key[1] + 3
            owner = dict(bank=key[0], bytes=n['bytes'])
            callers.setdefault(str(ret), []).append(owner)
            records.append(dict(bank=key[0], pc=key[1], target=operand, return_pc=ret))
            if operand != h['pc']:
                path, state = [], (q, 0)
                while state is not None:
                    k, _ = state
                    path.append(dict(bank=k[0], pc=k[1], bytes=nodes[k]['bytes'],
                                     span=nodes[k]['span'], mirror_of_bank=nodes[k].get('mirror_of_bank')))
                    state = paths[state]
                witnesses.append(dict(function=h['name'], caller=records[-1],
                                      stack_neutral_instruction_path=path))
        source_callers[h['name']] = callers
        smc_targets[h['name']] = {str(pc): True for _, pc in sorted(neutral)}
        reports.append(dict(function=h['name'], actual_entry=h, neutral_entry_nodes=len(neutral),
                            source_JSR_callers=records,
                            allowed_SMC_target_PCs=sorted(int(v) for v in smc_targets[h['name']])))
    return source_callers, smc_targets, dict(
        algorithm='All17 compiled entries; backwards decoded instruction flow, direct branches/JMPs, stack-neutral paths, and explicit JumpEngine typed-word dispatch. JSR callees are separate owners; only their post-return continuation is a local edge.',
        decoded_source_instructions=len(nodes), verified_mirror_instructions=mirrors,
        jump_engine_dispatches=dispatches, indirect_JMP_inventory=indirect,
        functions=reports, non_direct_caller_witnesses=witnesses,
        boundary='This closes source-declared direct/tail/JumpEngine caller ownership. Genuine RAM farcall JSR targets must belong to the same stack-neutral closure. Arbitrary indirect targets are never accepted; an unlisted live caller still fails.')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    out = a.output.resolve()
    baseline = ROOT / 'build/verification/compact-next-bill-hard-v1'
    rom = ROOT / 'build/proto_palette_ack.nes'
    inputs = baseline / 'inputs.csv'
    assert route.sha(rom) == ROM_SHA
    old = json.loads((baseline / 'ready.json').read_text())
    result = json.loads((baseline / 'result.json').read_text())
    assert result['passed'] and result['ROM_sha256'] == ROM_SHA and result['identity'] == 'bill'
    saved = list(route.csv.DictReader(inputs.open(newline='')))
    assert len(saved) == result['polls']
    assert [int(q['poll']) for q in saved] == list(range(1, len(saved) + 1))
    assert any(int(q['frame']) == 3559 for q in saved)
    options = argparse.Namespace(rom=rom, output=out, expected_sha256=ROM_SHA, identity='bill',
                                mode='hard', frames=3560, policy=Path(old['config']['policy']), replay=inputs)
    with contextlib.redirect_stdout(io.StringIO()):
        route.prepare(options)
    ready = json.loads((out / 'ready.json').read_text())
    cfg = ready['config']
    assert cfg['character'] == 3 and cfg['variant'] == 0 and cfg['mode_value'] == 1
    cfg['capture_bytes'] = 128 * 1024 * 1024
    raw, syms, address, location, hook = route.linked(rom)
    scoped = scoped_symbols(rom.with_suffix('.dbg'))

    def bound(name, public=None, leaf=None):
        if leaf:
            z = scoped[tuple(public.split('::')) + (leaf,)]
            parent = syms[public]
            assert z['seg'] == parent['seg']
            pc = int(z['val'], 0)
            at = location(public) + pc - address(public)
        else:
            public = public or name
            pc, at = address(public), location(public)
        bank = (at - 16) // 8192
        banks = [bank]
        if bank == 127:
            clone = 16 + 125 * 8192 + (pc & 8191)
            size = int(syms[public].get('size', '3'), 0)
            if raw[at:at + size] == raw[clone:clone + size]:
                banks.append(125)
        return dict(name=name, symbol=public + ('::' + leaf if leaf else ''), pc=pc,
                    banks=banks, bytes=list(raw[at:at + 3]))

    names = ['GameLoop', 'PlayerCtrlRoutine', 'PlayerMovementSubs', 'RosterMovement',
             'PlayerBGCollision', 'BillHotProject', 'BillBGEmptyEnvelope', 'RosterWeapons',
             'RemainingWeapons', 'GuestPrepareEnemies', 'RemainingDraw', 'RosterDrawShots',
             'DrawAllMetasprites', 'MetaspriteRenderLoop', 'AudioUpdate']
    functions = [bound(n) for n in names]
    functions += [bound('BulletBlocks', 'MegaManWeapons', 'Blocks'),
                  bound('BulletEnemies', 'MegaManWeapons', 'Enemies')]
    assert len({(q['pc'], tuple(q['banks'])) for q in functions}) == len(functions)
    targets = {q['pc'] for q in functions}
    returns = {}
    # Raw candidates are NOT a claim that data bytes are executed code.
    # At actual entry, the observer verifies the stacked return, mapped
    # physical owner, literal JSR bytes and final SP at the real return.
    for bank in range(128):
        block = raw[16 + bank * 8192:16 + (bank + 1) * 8192]
        for i in range(8190):
            if block[i] != 0x20 or (block[i + 1] | block[i + 2] << 8) not in targets:
                continue
            for base in (0x8000, 0xa000, 0xc000, 0xe000):
                ret = (base + i + 3) & 65535
                if ret >= 0x8000:
                    returns.setdefault(str(ret), []).append(dict(bank=bank, bytes=list(block[i:i + 3])))
    # This measured entry also has one genuine tail caller: the head-probe
    # JSR calls a fixed-bank selector which JMPs into BillBGEmptyEnvelope.
    # Keep its real JSR owner, rather than aliasing the selector to that entry.
    head = bound('PlayerHeadProbe')
    selector = bound('BillBGHeadConsumer')
    envelope = bound('BillBGEmptyEnvelope')
    legacy = bound('BillHeadConsumer')
    assert head['pc'] == 0x9bc2 and head['banks'] == [126]
    assert selector['pc'] == 0xf113 and selector['banks'][0] == 127
    assert envelope['pc'] == 0x94b0 and envelope['banks'] == [126]
    word = lambda v: [v & 255, v >> 8]
    assert head['bytes'] == [0x20] + word(selector['pc'])
    selector_bytes = [0x08, 0x48, 0xad] + word(address('SelectedCharacter')) + [
        0xc9, cfg['character'], 0xf0, 5, 0x68, 0x28, 0x4c] + word(legacy['pc']) + [
        0x68, 0x28, 0x4c] + word(envelope['pc'])
    assert len(selector_bytes) == int(syms['BillBGHeadConsumer']['size'], 0) == 19
    for bank in selector['banks']:
        at = 16 + bank * 8192 + (selector['pc'] & 8191)
        assert list(raw[at:at + 19]) == selector_bytes
    ret = head['pc'] + 3
    assert str(ret) not in returns  # Preserve the exact v1 counterexample.
    owner = dict(bank=head['banks'][0], bytes=head['bytes'])
    returns[str(ret)] = [owner]
    accepts = lambda bank, code: any(q['bank'] == bank and q['bytes'] == code
                                    for q in returns[str(ret)])
    assert accepts(126, head['bytes'])
    assert not accepts(127, head['bytes'])
    assert not accepts(126, [0x4c] + word(selector['pc']))
    assert not accepts(126, [0x20] + word(envelope['pc']))
    tail_return = dict(return_pc=ret, call=head, selector=selector,
        selector_bytes=selector_bytes, measured_tail_entry=envelope,
        legacy_tail_entry=legacy,
        source_path='JSR selector; PHP/PHA; LDA SelectedCharacter/CMP3/BEQ owned; PLA/PLP; JMP measured entry. No extra return address is pushed.',
        metadata_controls=dict(original_missing_return=True, exact_owner_accepts=True,
            wrong_bank_rejected=True, JMP_in_place_of_JSR_rejected=True,
            wrong_JSR_target_rejected=True),
        scope='Compiled control-flow and caller-metadata controls only; not a new native timing result.')
    jump = bound('JumpEngine')
    jump_bytes = ([0x0a, 0xa8, 0x68, 0x85, address('R4'), 0x68, 0x85, address('R5'),
                   0xc8, 0xb1, address('R4'), 0x85, address('R6'), 0xc8, 0xb1, address('R4'),
                   0x85, address('R7'), 0x6c] + word(address('R6')))
    assert jump['banks'] == [126] and len(jump_bytes) == int(syms['JumpEngine']['size'], 0) == 21
    assert list(raw[location('JumpEngine'):location('JumpEngine') + 21]) == jump_bytes
    source_callers, smc_targets, closure = source_call_closure(rom, raw, functions, jump['pc'])
    closure['JumpEngine_exact_body'] = dict(jump, full_bytes=jump_bytes,
        stack_contract='JSR pushes2; JumpEngine PLA/PLA removes exactly those2 and JMPs through typed inline words. The target inherits the dispatch caller return.')
    additions = []
    for name, callers in source_callers.items():
        for ret, owners in callers.items():
            for owner in owners:
                if owner not in returns.get(ret, []):
                    returns.setdefault(ret, []).append(owner)
                    additions.append(dict(function=name, return_pc=int(ret), owner=owner))
    closure['source_proven_additions_beyond_v2'] = additions
    assert {q['return_pc'] for q in additions} == {0xa067, 0xa0a7, 0xa225, 0xa55b, 0xa1ed, 0xa4f1}
    # Every executable owner is a decoded source JSR, not an arbitrary code
    # pointer or blanket return-PC alias. Counterfactual banks/targets fail.
    control_count = 0
    all_source_returns = {ret for callers in source_callers.values() for ret in callers}
    for name, callers in source_callers.items():
        assert '65535' not in callers
        foreign = next((ret for ret in all_source_returns if ret not in callers), None)
        assert foreign is not None and callers.get(foreign) is None
        assert smc_targets[name].get('65535') is None
        for ret, owners in callers.items():
            for owner in owners:
                assert owner['bytes'][0] == 0x20
                offset = 16 + owner['bank'] * 8192 + ((int(ret) - 3) & 8191)
                assert list(raw[offset:offset + 3]) == owner['bytes']
                matches = lambda bank, code: any(q['bank'] == bank and q['bytes'] == code for q in owners)
                assert matches(owner['bank'], owner['bytes'])
                assert not matches(-1, owner['bytes'])
                assert not matches(owner['bank'], [0x4c] + owner['bytes'][1:])
                changed = owner['bytes'][:]
                changed[1] ^= 1
                assert not matches(owner['bank'], changed)
                control_count += 1
    closure['metadata_positive_negative_controls'] = dict(source_JSR_owners=control_count,
        each_exact_owner_accepts=True, each_wrong_bank_rejected=True,
        each_JMP_in_place_of_JSR_rejected=True, each_changed_JSR_target_rejected=True,
        unlisted_return_and_wrong_function_return_rejected=True,
        scope='Source/metadata controls, not a Lua/native timing qualification.')
    assert 0 < len(returns) < 2048
    smc_record = syms['FarcallJmpTarget_SMC']
    segments = {}
    for line in rom.with_suffix('.dbg').read_text().splitlines():
        if line.startswith('seg\t'):
            z = dict(q.split('=', 1) for q in line[4:].strip().split(',') if '=' in q)
            segments[z['id']] = z
    smc = segments[smc_record['seg']]
    start, size = int(smc['start'], 0), int(smc['size'], 0)
    assert smc['name'] == '"SMCCODE"' and 0x100 <= start < start + size <= 0x200
    interrupts = {}
    for key, proc in [('NMI', 'NonMaskableInterrupt'), ('IRQ', 'IrqScrollSplit')]:
        interrupts[key] = bound(proc)
        h = hook(proc, tail=True)
        interrupts[key + '_return'] = dict(name=proc + ' preRTI', pc=h['pc'],
                                         banks=interrupts[key]['banks'], bytes=[0x40])
        assert h['bytes'][0] == 0x40
        for bank in interrupts[key]['banks']:
            off = 16 + bank * 8192 + (h['pc'] & 8191)
            assert raw[off] == 0x40
    ram_names = set(re.findall(r"\br\(['\"]([^'\"]+)['\"]", OBSERVER.read_text()))
    assert not (ram_names - syms.keys())
    profile = dict(output=out.as_posix() + '/', ROM_sha256=ROM_SHA, first_frame=3500, last_frame=3560,
                   row_cap=200, byte_cap=1024 * 1024, functions=functions, returns=returns,
                   source_callers=source_callers, smc_targets=smc_targets,
                   smc_start=start, smc_end=start + size - 1, interrupts=interrupts,
                   dma_complete=cfg['hooks']['dma_complete'], ram={n: address(n) for n in sorted(ram_names)})
    text = OBSERVER.read_text()
    assert not re.search(r'emu\.(?:write\w*|setInput|setState|loadSavestate|reset|stop)\s*\(', text)
    assert text.count('emu.addMemoryCallback(') == 6 and text.count('emu.addEventCallback(') == 1
    # Exact original runner around one configuration/observer insertion.
    alias = 'for name,value in pairs(ROSTER_CONFIG.extra_ram)do assert(L[name]==nil or L[name]==value,"RAM alias conflict: "..name);L[name]=value end\n'
    original = 'ROSTER_CONFIG=' + route.lua(cfg) + '\n' + alias + 'dofile(' + route.lua(route.SCRIPT.as_posix()) + ')\n'
    insertion = 'BILL_PASSIVE_TIMING=' + route.lua(profile) + '\n' + 'dofile(' + route.lua(OBSERVER.as_posix()) + ')\n'
    generated = 'ROSTER_CONFIG=' + route.lua(cfg) + '\n' + alias + insertion + 'dofile(' + route.lua(route.SCRIPT.as_posix()) + ')\n'
    assert generated.replace(insertion, '', 1) == original
    (out / 'run.lua').write_text(generated, encoding='utf-8')
    (out / 'profile-config.json').write_text(json.dumps(profile, indent=2) + '\n')
    (out / 'command.json').write_text(json.dumps(ready['command'], indent=2) + '\n')
    dependencies = {Path(k) for k in ready['bindings']}
    dependencies.update({OBSERVER, Path(__file__).resolve(), out / 'profile-config.json', out / 'command.json',
                         baseline / 'ready.json', baseline / 'result.json',
                         baseline / 'trace.csv', baseline / 'events.jsonl',
                         Path('C:/Mesen2/Mesen.exe'), Path('C:/Mesen2/MesenCore.dll')})
    dependencies.update({Path(sys.modules[MPU.__module__].__file__),
                         Path(conversions.__file__), Path(devices.__file__)})
    ready['bindings'] = {str(f): route.sha(f) for f in sorted(dependencies)}
    ready['passive_timing'] = dict(functions=len(functions), startup_static_return_PCs=len(returns),
        warmup_first_frame=3499, detailed_window=[3500, 3560], CSV_max_rows=200, CSV_max_bytes=1048576,
        expected_CSV_rows=62, no_runtime_callback_registration=True, no_state_or_input_writes=True,
        spans='Completed at real callerPC/SP/physical bank. Inclusive minus ISR; exclusive additionally minus same-context childCPU. Completion buckets are not physical-frame CPU integrals. Open spans atcutoff censored.',
        expected_native_terminal='Original unmodified harness FALSE/exit1: finite frame bound at3560. Any earlier or other guard failure remains a failure, never normalized.',
        exact_saved_inputs=str(inputs), identity='Bill Hard variant0',
        capture='One128MiB NESPPU01 container,3568 record cap (<4000), zero native PNG/per-frame files.',
        ordinary_game_or_driver_changes=False, original_harness_sha256=route.sha(route.SCRIPT),
        host_runner_reverse_removes_only_observer_insertion=True,
        source_scope='Metadata derived only from immutable build/proto_palette_ack.nes/.dbg/.lbl; no canonical source dependencies.',
        historical_scope='Original BillHardv1 full6076-frame clear remains separate; this prefix is diagnostic, not a new clear or60fps claim.')
    ready['passive_timing']['source_proven_tail_return'] = tail_return
    ready['passive_timing']['all17_source_caller_closure'] = closure
    ready['max_total_frames'] = 3560
    ready['container_cap_bytes'] = cfg['capture_bytes']
    (out / 'ready.json').write_text(json.dumps(ready, indent=2) + '\n')
    (out / 'command.json').write_text(json.dumps(ready['command'], indent=2) + '\n')
    print(json.dumps(dict(prepared=True, native_run=False, ready=str(out / 'ready.json'),
                         ready_sha256=route.sha(out / 'ready.json'), bindings=len(dependencies),
                         functions=len(functions), return_PCs=len(returns), command=ready['command']), indent=2))


if __name__ == '__main__':
    main()
