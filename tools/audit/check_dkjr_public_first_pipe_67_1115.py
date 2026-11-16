"""Actual67 public DK Jr first-pipe causal source trace; no modified game code."""
import ast
from collections import deque
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
from unittest.mock import patch

import recover_dkjr_current_identity_67_1115 as Identity
import check_dkjr_head_bridge_1113 as H

B, N, W = H.B, H.N, H.W
HASH = lambda value: sha256(value).hexdigest()


def one(text, before, after):
    assert text.count(before) == 1, before
    return text.replace(before, after, 1)


def first_active_cold(raw):
    """Use genuine Select/Start/parser/cold, stopping before the old60-input study.

    The changed comparison belongs solely to the retained audit's loop limit.
    No game instruction or emulated state is patched.
    """
    module = B.C.Starts
    path = Identity.R / 'tools/audit/check_current_roster_stage_ingress_1110.py'
    tree = ast.parse(path.read_text())
    function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'stage')
    hits = 0
    for node in ast.walk(function):
        if (isinstance(node, ast.Compare) and isinstance(node.left, ast.Name)
                and node.left.id == 'ticks' and len(node.ops) == 1
                and isinstance(node.ops[0], ast.GtE)
                and len(node.comparators) == 1 and isinstance(node.comparators[0], ast.Constant)
                and node.comparators[0].value == 60):
            node.comparators[0].value = 0
            hits += 1
    assert hits == 1
    scope = dict(module.__dict__)
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(path), 'exec'), scope)
    with patch.object(module, 'stage', scope['stage']):
        opening, memory = H.cold(raw, Identity.PUBLIC_COOKIE)
    assert opening['opening_updates'] == 0
    opening['scope'] = 'Actual compiled Select/Start/parser/cold at first active1-1; zero extra opening inputs'
    assert B.state(memory)['x'] == 40 and B.state(memory)['lives'] == 2
    return opening, memory


def source_text(raw):
    text = Identity.controller(raw, kind='delivered-public-67')
    text = one(text, "local rom=os.getenv('SMB_STDOUT_ROM_SHA')or''", f'local rom="{Identity.PIN}"')
    text = one(text, "os.getenv('SMB_TEST_VARIANT')=='0'", 'true')
    assert text.count("os.getenv('SMB_DKJR_FAST_ROUTE')=='1'") == 2
    text = text.replace("os.getenv('SMB_DKJR_FAST_ROUTE')=='1'", 'true')
    return one(text, "emu.addEventCallback(guarded('input',function()",
               "if CPU_CONTROLLER_OPENING then frame=541;playing=true end\n"
               "emu.addEventCallback(guarded('input',function()")


def run(raw):
    ownership, payload = Identity.identity(raw)
    text = source_text(raw)
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    LuaRuntime().compile(text)
    opening, memory = first_active_cold(raw)
    writes = {0xa000+i for i in range(0x1fde) if payload[i:i+3] == bytes.fromhex('8d6bc0')}
    assert writes
    ticks = entries = returns = 0
    pending = None
    first_bad = None
    state_writes = deque(maxlen=3)
    carry_rows = deque(maxlen=2)
    state_write_count = carry_count = 0

    def snapshot():
        source = memory.ram[2]
        actors = []
        for slot in range(6):
            if N.get(memory, 'Enemy_Flag', slot):
                actors.append(dict(slot=slot, id=N.get(memory, 'Enemy_ID', slot),
                                   x=N.get(memory, 'Enemy_X_Position', slot)+256*N.get(memory, 'Enemy_PageLoc', slot),
                                   y=N.get(memory, 'Enemy_Y_Position', slot),
                                   passenger=N.get(memory, 'PlatformCollisionFlag', slot),
                                   vy=N.get(memory, 'Enemy_Y_Speed', slot)))
        return dict(tick=ticks, entries=entries, returns=returns, **B.state(memory),
                    prior=source[0x6c], origin=source[0x76], limit=source[0x7b], age=source[0x7e],
                    fraction=source[0x7f], acc=int.from_bytes(source[0x82:0x84], 'little'),
                    impulse=int.from_bytes(source[0x86:0x88], 'little'),
                    query_kind=source[0x8db], query=list(source[0x3e:0x42]),
                    support=list(source[0x840:0x850]), walls=list(source[0x880:0x890]),
                    held=N.get(memory, 'SavedJoypadBits'), bits=memory.controller_pad,
                    bbox=list(memory[0x658:0x65c]), actors=actors)

    def observe(m, cpu):
        nonlocal entries, returns, pending, first_bad, state_write_count, carry_count
        pc = cpu.pc
        if pending == (pc, cpu.sp):
            returns += 1
            pending = None
        if pc == 0xd65e and m.rawtags[2] == 2:
            entries += 1
            pending = ((m[0x100+((cpu.sp+1)&255)]+256*m[0x100+((cpu.sp+2)&255)]+1)&65535,
                       (cpu.sp+2)&255)
        if pc in writes and m.rawtags[1] == 3:
            state_write_count += 1
            row = dict(PC=pc, A=cpu.a, P=cpu.p, SP=cpu.sp, **snapshot())
            state_writes.append(row)
            if cpu.a == 5 and first_bad is None:
                first_bad = row
        if pc == 0xac29 and m.rawtags[1] == 199:
            slot = cpu.x
            if slot < 6 and N.get(m, 'Enemy_ID', slot) == 37:
                carry_count += 1
                carry_rows.append(dict(PC=pc, slot=slot, **snapshot()))

    class PipeWindowComplete(Exception):
        pass

    def after(m):
        nonlocal ticks
        ticks += 1
        state = B.state(m)
        if ticks % 250 == 0:
            print('DKJR_PUBLIC_PIPE_PROGRESS ' + json.dumps(dict(tick=ticks, **state), separators=(',', ':')),
                  file=output, flush=True)
        if state['x'] >= 510 or (ticks >= 1500 and first_bad is None):
            raise PipeWindowComplete()

    output = __import__('sys').stdout
    result = None
    window = False
    with redirect_stdout(io.StringIO()):
        try:
            result = B.route(memory, raw, 1600, controller_text=text, observe_extra=observe, after_frame=after)
        except PipeWindowComplete:
            window = True
    summary = None if result is None else {key: result.get(key) for key in ('passed', 'stopped', 'logical_updates', 'final')}
    if result is not None and result.get('receipt'):
        summary['reason'] = result['receipt'].get('reason')
    report = dict(source_diagnostic_complete=True, actual_ROM_SHA256=Identity.PIN,
                  source_controller_Lua_SHA256=HASH(text.encode()), opening=opening,
                  native_negative_receipt='2704666e8811bb87f69ceb78a37d0d1c659105c0a8e7f1344d70e6c7c4c81aa0',
                  current_owner_SHA256=ownership['complete_DK_owner_SHA256'],
                  first_source5_writer=first_bad, state_writes=list(state_writes),
                  last_carry_rows=list(carry_rows), final=snapshot(),
                  aggregate_counts=dict(entries=entries, returns=returns, ticks=ticks,
                                        state_writes=state_write_count, actual_carry_calls=carry_count),
                  source_window_complete=window, result=summary,
                  game_bytes_modified=False, game_state_or_actor_seeds=False,
                  output_files=0, native_claim=False, physical_timing_claim=False)
    encoded = json.dumps(report, sort_keys=True, separators=(',', ':'))
    print('DKJR_PUBLIC_FIRST_PIPE ' + encoded, flush=True)
    print('DKJR_PUBLIC_FIRST_PIPE_SHA256 ' + HASH(encoded.encode()), flush=True)
    return report


if __name__ == '__main__':
    run(Identity.NIGHTLY.read_bytes())
