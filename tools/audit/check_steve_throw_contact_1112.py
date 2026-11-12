"""Compare composed damage ordering to the original admitted overlap path."""
import json
from itertools import product
from py65.devices.mpu6502 import MPU
import check_steve_shatterhand_robot_death_1112 as Death
import check_steve_throw_controls_live_1111 as Controls


def main():
    raw = Death.D.DONOR.read_bytes()
    _, fields = Death.link(raw)
    fields.update(JnEnemyHurt=0x6100, JnEnemyHP=0x6110, Square1SoundQueue=0x6120,
                  DefeatEnemy=0x5001)
    source = Controls.Live.bindings(fields)
    for name in ('steve_shatterhand_robot_death_1112.s', 'steve_throw_damage_1112.s',
                 'steve_throw_contact_1112.s'):
        source += '\n'+(Controls.H.ROOT/'tools/reference'/name).read_text()
    layout = {'ROBOT_DEATH': (0xab00, 512), 'THROW_DAMAGE': (0xad00, 128),
              'THROW_CONTACT': (0xae00, 128)}
    linked = Controls.H.assemble(source, layout)
    count = 0
    for flag, hp, cooldown in product((1, 0x21), (1, 2, 16), (0, 7)):
        donor, host = MPU(), MPU()
        donor.memory[0x8000:0xc000] = raw[16+8*8192:16+10*8192]
        d = donor.memory
        d[0x60] = flag
        d[0x61:0x69] = bytes.fromhex('0020002000010001')
        d[0xac], d[0xbc], d[0xcc], d[0xdc] = 0, 0x20, 0, 0x20
        d[0x600], d[0x6e0], d[0x6f0] = 1, 7 if cooldown else 60, 6
        d[0x60c], d[0x6ec], d[0x6fc] = 1, 60, hp
        d[0x65c], d[0x66c], d[0x67c] = 0x80, 0x5e, 1
        Death.invoke(donor, 0x83e2, x=0)
        for name, (origin, _) in layout.items():
            code = linked['images'][name]
            host.memory[origin:origin+len(code)] = code
        for name, value in dict(SteveBotActor=1, SteveBotAge=60, SteveBotHP=hp,
                                JnEnemyHP=6, JnEnemyHurt=cooldown).items():
            host.memory[fields[name]] = value
        Death.invoke(host, linked['symbols']['SteveThrowContactDamage'], a=flag, x=0)
        for name, at in (('SteveBotActor', 0x60c), ('SteveBotAge', 0x6ec),
                         ('SteveBotHP', 0x6fc), ('SteveThrowTimer', 0x62c), ('JnEnemyHP', 0x6f0)):
            assert host.memory[fields[name]] == d[at], (flag, hp, cooldown, name)
        count += 1
    print(json.dumps(dict(original_contact_comparisons=count, bytes=len(linked['images']['THROW_CONTACT']),
                          output_files=0, mounted=False, audio_compared=False)))


if __name__ == '__main__':
    main()
