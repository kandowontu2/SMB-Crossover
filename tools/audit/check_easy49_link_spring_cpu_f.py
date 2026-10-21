"""Source-oracle CPU checks for Easy Link's spring and unaffected identities."""
from pathlib import Path
import hashlib, importlib.util, itertools, json, sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-easy-link-spring-e'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    sys.dont_write_bytecode = True
    report_path = H / 'report.json'
    review = json.loads(report_path.read_text())
    assert review['status'] == 'PASS_PRIVATE_LINK_SPRING_BUILD_ONLY'
    assert all(sha(H / 'source' / n) == h for n, h in review['source_hashes'].items())
    dependency = V / 'agent49-megaman-easy-hard-implementation-a/verify_cpu.py'
    helpers = module('spring_f_helpers', dependency)
    image_module = helpers.image_module
    rows = []
    powers = {1: (475, 1000), 2: (300, 700), 3: (400, 800), 4: (450, 950),
              5: (500, 1000), 6: (500, 1000), 7: (660, 1320), 9: (475, 1000),
              10: (500, 1000), 11: (400, 930), 12: (720, 1440)}
    for mapper in ['mmc3', 'mmc5']:
        for kind in ['candidate', 'control']:
            directory = H if kind == 'candidate' else V / 'root49-easy-union-c'
            path = directory / ('source/build/smb-crossover-' + mapper + '.nes')
            im = image_module.Image(path)
            L = im.ram
            data = [0] * 65536
            for bank, pc in [(62, 0x8000), (12, 0xc000), (63, 0xe000)]:
                data[pc:pc + 8192] = im.raw[16 + bank * 8192:16 + (bank + 1) * 8192]
            mem = helpers.Memory(data, im.raw)
            cpu = helpers.cpu_module.NesMPU(memory=mem)
            labels = {}
            for line in path.with_suffix('.lbl').read_text().splitlines():
                values = line.split()
                if len(values) == 3:
                    labels[values[2][1:]] = int(values[1], 16)
            smc = next(x for x in im.data['seg'] if x['name'] == 'SMCCODE')
            smcraw = im.raw[smc['ooffs']:smc['ooffs'] + smc['size']]
            smcaddr = labels['__SMCCODE_RUN__']
            basebytes = bytes((i * 17 + 91) & 255 for i in range(2048))
            srambytes = bytes((i * 29 + 7) & 255 for i in range(8192))
            smcwrites = {labels[n] + 1 for n in ['SafecallA_SMC', 'NextBank_SMC', 'SafereturnA_SMC', 'FarcallJmpTarget_SMC']}
            smcwrites.add(labels['FarcallJmpTarget_SMC'] + 2)
            output = {L[n] + i for n, size in [('MmVY', 3), ('Player_Y_Speed', 1), ('Player_State', 1),
                                               ('MmJumpReleased', 1), ('MmFrictionYActive', 1),
                                               ('SmSourceJumped', 1), ('XgRise', 1)] for i in range(size)}
            bankram = {L['CurrentBank']} | ({L['BankShadow']} if 'BankShadow' in L else set())
            allowed = output | smcwrites | bankram
            count, failures = 0, 0
            identities = range(13) if kind == 'candidate' else [4]
            modes = range(2) if kind == 'candidate' else [0]
            for char, mode, boost in itertools.product(identities, modes, range(2)):
                flags = range(256) if char in [1, 4, 9] else [0, 1, 2, 4, 8, 16, 32, 64, 128, 255]
                for p in flags:
                    mem.context = None
                    mem[:2048] = basebytes
                    mem[0x6000:0x8000] = srambytes
                    mem[smcaddr:smcaddr + len(smcraw)] = smcraw
                    mem.switch(0)

                    def put(n, value):
                        list.__setitem__(mem, L[n], value & 255)

                    put('CurrentBank', 128 if im.mapper == 5 else 0)
                    if 'BankShadow' in L:
                        put('BankShadow', 7)
                    put('SelectedCharacter', char)
                    put('CrossoverBehaviorVersion', mode)
                    put('JumpspringForce', 0xf4 if boost else 0xf9)
                    put('ObjectOffset', 3)
                    cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = 0x5b, 3, 0xa7, p, 0xed
                    cpu.stPushWord(0x7eff)
                    cpu.pc = labels['MegaManSpringVelocity']
                    mem.writes = []
                    before = bytes(mem[:0x8000])
                    steps = 0
                    while cpu.pc != 0x7f00:
                        mem.context = (cpu.pc, mem[cpu.pc])
                        cpu.step()
                        steps += 1
                        assert steps < 3000
                    mem.context = None
                    assert (cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp) == (0x5b, 3, 0xa7, p | 0x30, 0xed)
                    if char not in [0, 8]:
                        power = powers[char][boost]
                        if char == 1 and mode == 0:
                            power = [400, 860][boost]
                        if char == 4 and mode == 0:
                            power = [400, 800][boost]
                        expected = round(-power / 120 * 65536) & 0xffffff
                        actual = sum(mem[L['MmVY'] + i] << (8 * i) for i in range(3))
                        if actual != expected:
                            assert kind == 'control'
                            assert actual == (round(-powers[char][boost] / 120 * 65536) & 0xffffff)
                            failures += 1
                        assert mem[L['Player_Y_Speed']] == actual >> 16
                        assert mem[L['Player_State']] == 1
                        assert mem[L['MmJumpReleased']] == mem[L['MmFrictionYActive']] == 0
                    for pc, op, address, value in mem.writes:
                        if address in [0x8000, 0x8001, 0x5115]:
                            continue
                        if 0x100 <= address < 0x200 and address not in smcwrites and address not in bankram:
                            assert op in [0x08, 0x48, 0x20] and address > 0x190
                            continue
                        assert address in allowed, (hex(pc), op, hex(address))
                    touched = {address for _, _, address, _ in mem.writes if address < 0x8000}
                    assert all(before[address] == mem[address] for address in range(0x8000) if address not in touched)
                    count += 1
            assert (kind == 'candidate' and count == 3472 and failures == 0) or (kind == 'control' and count == failures == 512)
            rows.append(dict(mapper=mapper, kind=kind, ROM_sha256=sha(path), cases=count,
                             source_velocity_failures=failures, resident_entry=im.hook('MegaManSpringVelocity'),
                             cold_closure=im.hook('MegaManSpringVelocityModes')))
            print(mapper, kind, count, failures, flush=True)
    result = dict(status='PASS_SOURCE_LINK_SPRING_CPU', rows=rows, script_sha256=sha(__file__),
                  helper_sha256=sha(dependency), build_review_sha256=sha(report_path),
                  scope='Actual compiled helper, all flag patterns for Link/MegaMan/Bass, exact Q16 source constants, AXYP/SP and complete physical RAM outside predicted stack/SMC/outputs. No native spring contact, IRQ or timing claim.',
                  route_proof=False, accepted_release=False, goal_complete=False)
    destination = H / 'cpu-review-f.json'
    assert not destination.exists()
    destination.write_text(json.dumps(result, indent=2) + '\n')
    print(result['status'], sha(destination), flush=True)


if __name__ == '__main__':
    main()
