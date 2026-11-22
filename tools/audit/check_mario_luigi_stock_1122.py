"""Bounded stdout-only checks of exact installed standard Mario/Luigi stock."""

import argparse
from collections import defaultdict
import json
import os
from pathlib import Path
from unittest.mock import patch

import replay_mario_luigi_stock_1122 as Replay
from check_ff_stdout_controller_source_1110 import LuaRuntime

C = Replay.Current
R, ROM, H, N, Frames = C.R, C.ROM, C.H, C.N, C.Frames


def run(raw, form, item, limit=4200):
    text = Replay.controller(raw, form, item)
    print('STANDARD_BOUND '+json.dumps(dict(form=form, item=item, controller_SHA256=H(text.encode()))), flush=True)
    m = C.cold(raw, form)
    print('STANDARD_COLD '+json.dumps(dict(form=form, item=item, owner=N.get(m, 'SelectedCharacter'),
        variant=N.get(m, 'MarioVariant'))), flush=True)
    lua = LuaRuntime(unpack_returned_tuples=True)
    callbacks = {0: defaultdict(list), 1: defaultdict(list)}
    events = defaultdict(list)
    ctx = dict(cpu=None, pc=0, status=None, receipt=None)
    api = lua.table()
    api.memType = lua.table_from(dict(nesDebug=0, nesWorkRam=1, nesPrgRom=2))
    api.callbackType = lua.table_from(dict(exec=0, write=1))
    api.eventType = lua.table_from(dict(inputPolled=0, endFrame=1))

    def read(at, kind=0):
        if kind == 2:
            return raw[16+at]
        if kind == 1:
            return m.ram[at//8192][at%8192]
        return m[at]

    def mapped(pc):
        if pc < 0x8000:
            return None
        tag = m.rawtags[(pc-0x8000)//8192]
        return lua.table_from(dict(memType=2 if tag & 128 else 1,
                                   address=(tag & 127)*8192+(pc & 8191)))

    def state():
        c = ctx['cpu']
        d = {f'cpu.{k}': getattr(c, k) if c else 0 for k in ('pc', 'sp', 'a', 'x', 'y', 'p')}
        d['cpu.pc'], d['cpu.ps'] = ctx['pc'], d['cpu.p']
        return lua.table_from(d)

    def memory(fn, kind, lo, hi=None):
        assert kind in (0, 1)
        for at in range(lo, (hi if hi is not None else lo)+1):
            callbacks[kind][at].append(fn)

    def pad(p, port):
        assert port == 0
        m.controller_pad = sum(v for n, v in C.Shared.BITS.items() if p[n])

    def emit(line):
        if line.startswith('SMB_NATIVE_RECEIPT '):
            ctx['receipt'] = json.loads(line.removeprefix('SMB_NATIVE_RECEIPT '))

    api.read, api.convertAddress, api.getState, api.setInput = read, mapped, state, pad
    api.addMemoryCallback = memory
    api.addEventCallback = lambda fn, kind: events[kind].append(fn)
    api.stop = lambda status: ctx.update(status=status)
    lua.globals().emu = api
    lua.globals().print = emit
    with patch.dict(os.environ, {'SMB_STDOUT_ROM_SHA': H(raw)}):
        lua.execute(text)
    base_cpu, old_write = N.NesMPU, type(m).__setitem__

    class CPU(base_cpu):
        def step(self):
            ctx.update(cpu=self, pc=self.pc)
            for fn in tuple(callbacks[0].get(self.pc, ())):
                fn()
            return super().step()

    def write(bus, at, value):
        if bus is m and isinstance(at, int):
            for fn in tuple(callbacks[1].get(at, ())):
                fn(at, value)
        return old_write(bus, at, value)

    with patch.object(N, 'NesMPU', CPU), patch.object(type(m), '__setitem__', write):
        for age in range(limit):
            for fn in tuple(events[0]):
                fn()
            Frames.frame(m, whole_pass=True)
            for fn in tuple(events[1]):
                fn()
            if ctx['status'] is not None:
                break
            if age % 500 == 499:
                print('PROGRESS '+json.dumps(dict(form=form, item=item, Main=age+1,
                    x=N.get(m, 'Player_X_Position')+256*N.get(m, 'Player_PageLoc'))), flush=True)
    receipt = ctx['receipt'] or {}
    return dict(passed=ctx['status'] == 0 and receipt.get('passed') is True,
                form=form, item=item, ROM_SHA256=H(raw), source_passes=age+1,
                controller_SHA256=H(text.encode()), receipt=receipt,
                receipt_SHA256=H(json.dumps(receipt, sort_keys=True, separators=(',', ':')).encode()),
                controller_only=True, gameplay_seeds=0, outputs=0, Mesen=False)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--form', choices=(*C.FORMS, 'both'), default='both')
    p.add_argument('--item', choices=(*C.ITEMS, 'both'), default='both')
    p.add_argument('--validate', action='store_true')
    a = p.parse_args()
    raw = ROM.read_bytes()
    forms = tuple(C.FORMS) if a.form == 'both' else (a.form,)
    items = tuple(C.ITEMS) if a.item == 'both' else (a.item,)

    def deny(*args, **kwargs):
        raise AssertionError('Standard stock source test attempted files or process launch')

    cases = []
    with patch.object(Path, 'write_bytes', deny), patch.object(Path, 'write_text', deny), patch('subprocess.Popen', deny):
        for form in forms:
            for item in items:
                if a.validate:
                    script = Replay.controller(raw, form, item)
                    q = dict(passed=True, form=form, item=item, controller_SHA256=H(script.encode()),
                             route_executed=False, outputs=0, Mesen=False)
                else:
                    q = run(raw, form, item)
                report = dict(q)
                if q['passed'] and 'receipt' in q:
                    # Inner hash always covers the full observed receipt;
                    # successful stdout omits its repetitive final-frame tail.
                    report['receipt'] = {k: v for k, v in q['receipt'].items() if k != 'tail'}
                    report['receipt_tail_omitted'] = True
                print('STANDARD_STOCK '+json.dumps(report, separators=(',', ':')), flush=True)
                cases.append(q)
                if not q['passed']:
                    return 1
    assert ROM.read_bytes() == raw
    print('STANDARD_STOCK_ALL '+json.dumps(dict(passed=True, cases=len(cases), outputs=0, Mesen=False)), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
