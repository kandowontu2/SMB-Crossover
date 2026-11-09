"""Check the shared quiet-effect guard on the real MMC5 audio path."""

import argparse
from collections import Counter
import json
from pathlib import Path
import tempfile

import check_guest_expansion_sweep_vectors_1110_v1 as V
from check_mini_funded_actor_1108_v3 import install, registers, run
from check_native_audio_dirty_clear_irq_1110 import resume_matches


M, N, R = V.M, V.N, V.R
BASE = R / 'build/mini-margin-trial-1110/candidate.nes'
PIN = '863e1e3c536c3e6b8027e212a0a430356805886609fc2c264263d3cdb163fc9f'
SOURCE = R / 'tools/reference/guest_audio_quiet_tick_1110.s'
START, END = 0xf0b2, 0xf0d8
WORKER = 0xf069
OLD = bytes.fromhex('ad450148a9878d155120b4bf688d1551ad450148a99d8d155120eca4688d155160eaeaeaeaea')
GATE_FIELDS = ('AvAudioId', 'AvAudioRequest', 'AvAudioOldMask')


def compile_patch(raw, output):
    assert M.sha(raw) == PIN
    b = M.bundle(raw)
    for name, address in zip(GATE_FIELDS, (0x7fa6, 0x7fa7, 0x7fa9), strict=True):
        assert M.address(b, name) == address
    assert M.address(b, 'SophiaLandAudioTick') == 0xbfb4
    assert M.address(b, 'RemainingAudioTick') == 0xb421
    assert M.address(b, 'GuestAudioFinish') == 0xa4ec
    offset = 16 + 127*8192 + (START & 8191)
    assert raw[offset:offset+len(OLD)] == OLD
    footer = offset + WORKER-START
    assert raw[footer-3:footer+6] == bytes.fromhex('4cb9bceaeaeaeaeaea')
    foreign = 16 + 63*8192 + (0xb52a & 8191)
    assert raw[foreign:foreign+3] == bytes.fromhex('4ccef0')
    with tempfile.TemporaryDirectory(dir=output, prefix='mix-') as folder:
        text = SOURCE.read_text()
        new, _ = M.assemble(Path(folder)/'quiet', text, START, END-START)
        worker, _ = M.assemble(Path(folder)/'worker', 'ASSEMBLE_FINISH_WORKER=1\n'+text, WORKER, 6)
    assert new[0xf0ce-START:0xf0d3-START] == OLD[0xf0ce-START:0xf0d3-START]
    row = dict(physical_PRG=127, CPU_half_open=[START,END], file_offset=offset,
               old_hex=OLD.hex(), new_hex=new.hex())
    tail = dict(physical_PRG=127, CPU_half_open=[WORKER,WORKER+6], file_offset=footer,
                old_hex='ea'*6, new_hex=worker.hex())
    return install(raw, [row,tail]), [row,tail]


class IrqBus(N.Bus):
    irq_only = False

    def __getitem__(self, address):
        if self.irq_only and isinstance(address, int):
            assert not 0xa000 <= address < 0xc000, ('IRQ reads A window', hex(address))
        return super().__getitem__(address)

    def __setitem__(self, address, value):
        if self.irq_only and isinstance(address, int):
            assert address != 0x5115, ('IRQ changes A window', value)
        super().__setitem__(address, value)


def exact_nmi(m, side, flag, request, cuts=None):
    N.put(m,NmiDisable=flag,VRAM_Buffer_AddrCtrl=0,VRAM_Buffer1_Offset=0)
    c = V.start(m)
    quiet = None
    drops = []
    lag, normal = V.lag_path(m)
    seen = Counter()

    def at_end(z):
        return (z.pc,z.sp) == (0x5b00,214)

    for _ in range(24000):
        if at_end(c):
            break
        pc = c.pc
        tag = m.rawtags[(pc-0x8000)//8192] if pc >= 0x8000 else -1
        if tag == 255 and pc in (lag,normal):
            seen[pc] += 1
        if tag == 255 and pc == START:
            assert quiet is None
            if request:
                N.put(m,AvAudioRequest=1)
            quiet = not any(N.get(m,name) for name in GATE_FIELDS)
        if tag == 135 and pc == 0xbfb4:
            seen['tick'] += 1
        if tag == 157 and pc == 0xa4ec:
            seen['finish'] += 1
        if cuts is not None and tag == 255 and (START <= pc < END or WORKER <= pc < WORKER+6) and not c.p&4:
            cuts.setdefault((pc,quiet), (V.clone(c),tuple(m.writes)))
        assert m[pc], (side, flag, hex(pc), c.sp)
        before = len(m.writes)
        c.step()
        if side == 0 and tag == 255 and (pc == 0xf0bf or pc == 0xf0b8 and quiet):
            wanted = 0x87 if pc == 0xf0b8 else N.get(m,'CurrentBank')
            assert m.writes[before:] == [(0x5115,wanted)]
            drops.append((pc,wanted))
            del m.writes[before:]
    assert at_end(c)
    assert seen[lag] == int(flag == 255) and seen[normal] == int(flag == 0)
    assert registers(c,0xef) == (0xa7,23,61,0x24,214)
    if quiet is not None:
        assert seen['finish'] == 1 and seen['tick'] == int(side == 0 or not quiet)
        assert len(drops) == (1+int(quiet) if side == 0 else 0)
    return c, quiet


def vectors(before,after):
    images = [M.bundle(raw) for raw in (before,after)]
    saved = Counter()
    nested = Counter()
    original_bus = N.Bus
    N.Bus = IrqBus
    try:
        for owner in range(42):
            for flag in (0,255):
                pair = [M.seed(b,owner) for b in images]
                for tick in range(16):
                    for m in pair:
                        N.put(m,AreaMusicQueue=1 if tick==0 else 0,EventMusicQueue=4 if tick==14 else 0,
                              Square1SoundQueue=32 if tick in (2,5) else 0,Square2SoundQueue=1 if tick==6 else 0,
                              NoiseSoundQueue=1 if tick==9 else 0,GamePauseStatus=int(tick==13),FrameCounter=tick)
                    cut = {} if owner in (2,4,25,41) and tick in (2,5,9,13) else None
                    request = tick in (5,9)
                    a,old = exact_nmi(pair[0],0,flag,request)
                    b,new = exact_nmi(pair[1],1,flag,request,cut)
                    assert old == new, (owner,flag,tick,old,new)
                    assert registers(a) == registers(b)
                    try:
                        M.compare_state(a.memory,b.memory)
                    except AssertionError as error:
                        raise AssertionError((owner,flag,tick,old,error)) from error
                    assert bytes(a.memory[0x100:0x17b]) == bytes(b.memory[0x100:0x17b])
                    role = 'unchanged' if new is None else 'quiet' if new else 'effect'
                    saved[role,flag,a.processorCycles-b.processorCycles] += 1
                    if cut:
                        for probe,prior in cut.values():
                            lowest = V.interrupt(probe)
                            assert lowest > 0x7a
                            resume_matches(probe,prior,b)
                            nested[owner,flag] += 1
                    pair = [a.memory,b.memory]
    finally:
        N.Bus = original_bus
    assert all(any(role==r and flag==f for role,flag,_ in saved) for r in ('quiet','effect') for f in (0,255))
    assert all(any(flag==f for _,flag in nested) for f in (0,255))
    return dict(cycle_savings=[[*k,n] for k,n in sorted(saved.items())],
                nested_IRQ=[[*k,n] for k,n in sorted(nested.items())])


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    output = cli.parse_args().output
    output.mkdir(exist_ok=True)
    assert not (output/'proof.json').exists()
    before = BASE.read_bytes()
    after, patches = compile_patch(before,output)
    checks = vectors(before,after)
    print(json.dumps(checks),flush=True)
    proof = dict(passed=True,ROM_written=False,parent_SHA256=PIN,expected_memory_only_SHA256=M.sha(after),
                 patches=patches,**checks,bindings={str(path.resolve()):M.sha(path.read_bytes())
                    for path in (Path(__file__),SOURCE,Path(V.__file__),R/'src/remaining_audio.s')})
    (output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')


if __name__ == '__main__':
    main()
