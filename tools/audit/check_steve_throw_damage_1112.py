"""Check the native two-HP adapter and receipt-before-cooldown ordering."""
import json
from itertools import product
from py65.devices.mpu6502 import MPU
import check_steve_throw_controls_live_1111 as Controls

H = Controls.H


def main():
    fields = dict(SteveBotActor=0x6000, JnEnemyHurt=0x6010, JnEnemyHP=0x6020,
                  Square1SoundQueue=0x6030, DefeatEnemy=0x5001)
    source = H.ROOT / 'tools/reference/steve_throw_damage_1112.s'
    linked = H.assemble(Controls.Live.bindings(fields)+source.read_text(), {'THROW_DAMAGE': (0xae00, 256)})
    code = linked['images']['THROW_DAMAGE']
    count = 0
    for actor, slot, hp, hurt, cue in product((1, 3), range(6), (0, 1, 2, 3, 16, 255), (0, 1, 12), (0, 0x40)):
        cpu = MPU()
        m = cpu.memory
        m[0xae00:0xae00+len(code)] = code
        m[0x6000], m[0x6010+slot], m[0x6020+slot], m[0x6030] = actor, hurt, hp, cue
        cpu.pc, cpu.x, cpu.sp = 0xae00, slot, 0xf0
        cpu.stPushWord(0x4fff)
        for _ in range(80):
            if cpu.pc in (0x5000, 0x5001):
                break
            cpu.step()
        else:
            raise AssertionError('damage leaf did not return')
        assert m[0x6000] == actor|192
        assert cpu.x == slot
        fatal = not hurt and hp <= 2
        assert (cpu.pc == 0x5001) == fatal
        assert cpu.sp == (0xee if fatal else 0xf0)
        assert m[0x6010+slot] == (hurt or 12)
        assert m[0x6020+slot] == (hp-2 if not hurt and hp > 2 else hp)
        assert m[0x6030] == (cue|8 if not hurt and hp > 2 else cue)
        count += 1
    print(json.dumps(dict(cases=count, bytes=len(code), output_files=0,
                          scope='Adapter leaf; native defeat is a tail-call sentinel, not an executed kill.')))


if __name__ == '__main__':
    main()
