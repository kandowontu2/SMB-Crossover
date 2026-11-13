"""Run the current Prince pickup controller against real Main/NMI, stdout only.

The CPU peripheral model supplies the cold menu arena and frame scheduling.
The game performs menu confirmation, parsing, movement, item birth and pickup.
The controller's title/menu waits are skipped only after that actual ingress.
This is not a physical-cadence, raster or Mesen qualification.
"""

import argparse
from collections import defaultdict
from hashlib import sha256
import json
import sys
from unittest.mock import patch

import replay_prince_current_pickups_1113 as Replay
import check_thomas_powerups_current_1112 as Base


N, W, Frames = Base.N, Base.W, Base.Frames
PIN = Replay.PIN
CONTROLLER_PIN = '12f55c86840aa9750d0312c806f629b23e8cec5e8aa67483ffe77762934d3e66'


class MemoryPath:
    def __init__(self, name='memory', files=None):
        self.name = name
        self.files = {} if files is None else files

    def __truediv__(self, name):
        return MemoryPath(self.name+'/'+name, self.files)

    def mkdir(self, **_kwargs):
        pass

    def write_text(self, value, **_kwargs):
        self.files[self.name] = value

    def read_text(self, **_kwargs):
        return self.files[self.name]


def controller():
    """Use the native recipe itself; divert its writes and launch to memory."""
    class Ready(Exception):
        pass
    texts = []
    def take(script, *_args, **_kwargs):
        texts.append(script.read_text())
        raise Ready()
    with patch.object(Replay, 'OUTPUT', MemoryPath()), patch.object(Replay, 'run', take), \
            patch.object(sys, 'argv', ['prince-current', '--collect-sword']):
        try:
            Replay.main()
        except Ready:
            pass
    assert len(texts) == 1
    text = texts[0]
    assert sha256(text.encode()).hexdigest() == CONTROLLER_PIN
    return text


def cold(raw):
    assert sha256(raw).hexdigest() == PIN
    Replay.Packet.extract(raw)
    bundle = dict(W.Symbols.bundle(), raw=raw)
    previous = N.Bus
    N.Bus = W.ControllerBus
    try:
        model = W.UI.seed(bundle, 29)
    finally:
        N.Bus = previous
    W.UI.key(model, 32)
    assert N.get(model, 'SelectedCharacter') == 38
    start = W.UI.key(model, 16)
    N.invoke(model, 'NativeRareGameMenuRoutineCore::ChkContinue',
             a=start['A'], x=start['X'], y=start['Y'], p=start['P'])
    N.invoke(model, 'PauseRoutine', a=0)
    idle = W.address(bundle, 'IdleLoop')
    for epoch in range(700):
        if tuple(N.get(model, n) for n in ('OperMode', 'OperMode_Task', 'GameEngineSubroutine')) == (1, 3, 8):
            break
        model.controller_pad = 0
        W.clear_logs(model)
        N.consume(model)
        cpu = N.NesMPU(memory=model, pc=idle)
        cpu.sp, cpu.p = 255, 0x31
        cpu.stPushWord(0xe33b)
        for _ in range(4_000_000):
            if (cpu.pc, cpu.sp) == (idle+12, 252):
                break
            assert model[cpu.pc], ('BRK', hex(cpu.pc), model.rawtags)
            cpu.step()
        else:
            raise AssertionError('Prince cold frame bound')
        assert not model.blocked
    else:
        raise AssertionError('Prince ingress bound')
    assert N.get(model, 'Player_X_Position') == 40 and N.get(model, 'Player_PageLoc') == 0
    assert N.get(model, 'NumberofLives') == 2 and model.ram[2][0x6cf] == 5
    cookie = raw[Replay.Packet.COOKIE:Replay.Packet.COOKIE+16]
    assert all(bytes(model.ram[b][0x1fe0:0x1ff0]) == cookie for b in (2, 3))
    return model, dict(actual_menu=True, parser_updates=epoch, x=40, health=5, lives=2)


def route(model, raw, limit):
    from check_ff_stdout_controller_source_1110 import LuaRuntime, DLL, DLL_SHA
    assert sha256(DLL.read_bytes()).hexdigest() == DLL_SHA
    lua = LuaRuntime(unpack_returned_tuples=True)
    text = controller()
    begin = 'local route=coroutine.create(function()\n'
    end = '  initial=state()\n'
    lo, hi = text.index(begin)+len(begin), text.index(end, text.index(begin))
    # The native title navigation is already performed by cold(). Keep the
    # original active-game route and all of its controller decisions intact.
    bound = text[:lo]+text[hi:]
    events, callbacks = {}, {0: defaultdict(list), 1: defaultdict(list)}
    context = dict(cpu=None, exit=None, receipt=None)
    emu = lua.table()
    emu.memType = lua.table_from(dict(nesDebug=0, nesWorkRam=1, nesPrgRom=2, nesSpriteRam=3))
    emu.eventType = lua.table_from(dict(inputPolled=0, endFrame=1))
    emu.callbackType = lua.table_from(dict(exec=0, write=1))
    def read(at, kind=0):
        if kind == 1:
            return model.ram[at//8192][at%8192]
        if kind == 2:
            return raw[16+at]
        assert kind == 0, kind
        return model[at]
    def mapped(pc):
        if pc < 0x8000:
            return None
        tag = model.rawtags[(pc-0x8000)//8192]
        return lua.table_from(dict(memType=2 if tag&128 else 1,
                                   address=(tag&127)*8192+(pc&8191)))
    def cpu_state():
        cpu = context['cpu']
        return lua.table_from({f'cpu.{k}': getattr(cpu, attr) if cpu else 0
                               for k, attr in (('pc','pc'),('sp','sp'),('a','a'),
                                               ('x','x'),('y','y'),('ps','p'))})
    def set_input(pad, port):
        assert port == 0
        model.controller_pad = sum(bit for name, bit in (('right',1),('left',2),
            ('down',4),('up',8),('start',16),('select',32),('b',64),('a',128)) if pad[name])
    def emit(value):
        if value.startswith('SMB_NATIVE_RECEIPT '):
            context['receipt'] = json.loads(value[len('SMB_NATIVE_RECEIPT '):])
    def add_memory(fn, kind, lo, hi=None):
        assert kind in callbacks
        for pc in range(lo, lo+1 if hi is None else hi+1):
            callbacks[kind][pc].append(fn)
    emu.read, emu.convertAddress, emu.getState, emu.setInput = read, mapped, cpu_state, set_input
    emu.addEventCallback = lambda fn, kind: events.setdefault(kind, fn)
    emu.addMemoryCallback = add_memory
    emu.stop = lambda code: context.update(exit=code)
    lua.globals().emu, lua.globals().print = emu, emit
    lua.globals().os.getenv = lambda name: PIN if name == 'SMB_STDOUT_ROM_SHA' else '3' if name == 'SMB_TEST_VARIANT' else None
    lua.execute(bound)
    ParentBus, ParentMPU = type(model), N.NesMPU
    class ObservedBus(ParentBus):
        def __setitem__(self, at, value):
            if isinstance(at, int):
                for fn in tuple(callbacks[1].get(at, ())):
                    fn(at, value)
            return super().__setitem__(at, value)
    class ObservedMPU(ParentMPU):
        def step(self):
            context['cpu'] = self
            for fn in tuple(callbacks[0].get(self.pc, ())):
                fn()
            return super().step()
    model.__class__ = ObservedBus
    with patch.object(N, 'NesMPU', ObservedMPU):
        for tick in range(limit):
            events[0]()
            Frames.frame(model)
            events[1]()
            if context['exit'] is not None:
                break
    receipt = context['receipt'] or {}
    later = receipt.get('later_route', {})
    return dict(passed=context['exit']==0, stopped=context['exit'] is not None,
        logical_updates=tick+1, controller_SHA256=CONTROLLER_PIN,
        CPU_binding_SHA256=sha256(bound.encode()).hexdigest(),
        phase=receipt.get('phase'), reason=receipt.get('reason'),
        terminal=receipt.get('terminal'), injuries=receipt.get('injuries'),
        flower=later.get('flower'), sword=later.get('sword'),
        sword_trace=later.get('swordTrace'), events=receipt.get('events'),
        position_or_actor_injection=False, output_files=0,
        scope='CPU model with actual Main/NMI and current ROM; no native cadence/raster claim')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--limit', type=int, default=4500)
    args = p.parse_args()
    raw = Base.C.ROM.read_bytes()
    model, opening = cold(raw)
    print(json.dumps(dict(opening=opening, ROM_SHA256=PIN)), flush=True)
    result = route(model, raw, args.limit)
    print(json.dumps(result), flush=True)
    assert result['passed'], (result['phase'], result['reason'])


if __name__ == '__main__':
    main()
