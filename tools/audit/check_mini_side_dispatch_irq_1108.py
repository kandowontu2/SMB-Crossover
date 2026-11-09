"""Check native interrupts around the shorter Mini and legacy side routes."""
import argparse
from collections import Counter
import json
from pathlib import Path

from check_mini_busy_fire_interrupts_1108_v3 import lag_pcs
from check_mini_lift_admission_async_1108_v1 import clone, live, tags
from check_mini_native_side_dispatch_1108 import bind, N, sha

EXPECTED = 'b3bda384a54b2685e4cfc8a857304de71f390edc0460d52d051a2d68de746d1f'
EXIT = 0x5b00


def finish(cpu):
    for _ in range(3000):
        if cpu.pc==EXIT:
            return tuple(cpu.memory[:16]),cpu.a,cpu.x,cpu.y,cpu.p&0xef,cpu.sp
        assert cpu.memory[cpu.pc],hex(cpu.pc)
        cpu.step()
    raise AssertionError('Native side query did not return')


def run(rom):
    seed=N.fresh(bind(rom.read_bytes()))
    lag,regular=lag_pcs(seed)
    counts=Counter()
    minimum=255
    nested={}

    def interrupt(cpu, kind):
        nonlocal minimum
        bus=cpu.memory
        pc,sp=cpu.pc,cpu.sp
        before=live(cpu)
        skip=N.get(bus,'NmiSkipped')
        first_write=len(bus.writes)
        if kind=='nmi':
            cpu.nmi()
        else:
            cpu.irq()
            assert cpu.pc==0x8000
        reached=0
        for _ in range(16000):
            if (cpu.pc,cpu.sp)==(pc,sp):
                break
            minimum=min(minimum,cpu.sp)
            assert cpu.pc!=regular and bus[cpu.pc],(kind,hex(cpu.pc),hex(pc))
            reached+=cpu.pc==lag
            if kind=='nmi' and not cpu.p&4:
                key=tags(cpu),cpu.pc
                if key not in nested or cpu.sp<nested[key].sp:
                    nested[key]=clone(cpu)
            cpu.step()
        else:
            raise AssertionError(('Native interrupt did not return',kind,pc,sp))
        after=live(cpu)
        if after!=before:
            # Lag audio can publish a mapper shadow one instruction early.
            assert kind=='nmi' and before[:1]+before[2:]==after[:1]+after[2:]
            assert bytes(bus[pc:pc+3])==b'\x8d\x15\x51'
            assert after[1][1]==before[2]==cpu.a and before[1][1]!=after[1][1]
            assert before[1][:1]+before[1][2:]==after[1][:1]+after[1][2:]
        assert N.get(bus,'NmiSkipped')==(skip+(kind=='nmi'))&255 and reached==(kind=='nmi')
        assert all(at!=0x4014 and not 0x200<=at<0x304 for at,_ in bus.writes[first_write:])
        counts[kind]+=1

    for owner,probe,tile in ((41,17,0x54),(41,20,0xc2),(0,17,0x54),(4,20,0)):
        m=N.fork(seed)
        N.put(m,SelectedCharacter=owner,GameEngineSubroutine=8,NmiDisable=255,
              Player_X_Position=246,Player_PageLoc=2,Player_Y_Position=112,Player_Y_HighPos=1)
        N.invoke(m,'BlockBufferColli_Side',y=probe)
        m[m[9]+256*m[10]+m[5]]=tile
        cpu=N.NesMPU(memory=m,pc=0xe497)
        cpu.sp=196
        cpu.a,cpu.x,cpu.y,cpu.p=0x95,3,probe,0x21
        cpu.stPushWord(EXIT-1)
        expected=finish(clone(cpu))
        cut=set()
        for _ in range(3000):
            if cpu.pc==EXIT:
                break
            tag,pc=tags(cpu),cpu.pc
            if 0x15a<=pc<0x17b or (tag==0xa1 and 0xbea2<=pc<0xbf05) or (tag==0xfc and 0xad9b<=pc<0xadd0):
                key=tag,pc,tuple(m.rawtags),cpu.p&4
                if key not in cut:
                    cut.add(key)
                    for kind in ('nmi','irq'):
                        if kind=='irq' and cpu.p&4:
                            continue
                        fork=clone(cpu)
                        interrupt(fork,kind)
                        assert finish(fork)==expected,(owner,pc,kind)
            cpu.step()
        assert cpu.pc==EXIT and cut
    for cpu in nested.values():
        interrupt(cpu,'nested_irq')
    assert minimum>0x7a and all(counts[kind] for kind in ('irq','nmi','nested_irq'))
    return dict(passed=True,ROM_SHA256=sha(rom),cuts=counts,minimum_ISR_SP=minimum,
                entry_SP=196,scope='Live registered IRQ and lag NMI cuts around reached Mini and legacy side paths. Tank cold guard hit is a separate native test.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    assert sha(args.rom)==EXPECTED
    result=run(args.rom)
    args.output.mkdir(exist_ok=True)
    (args.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':
    main()
