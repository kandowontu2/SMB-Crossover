"""Recover the missing executable Excitebike animation selector, without ROM admission.

Read-only donor and existing component inputs. Run with the bounded producer;
the only generated files live in build/excitebike-pose-1101-v3.
"""
from pathlib import Path
import hashlib, json, random, subprocess, sys

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R / 'tools/reference'), str(R / 'tools/audit')]
import excitebike_original_cpu_1101_v2 as E
from py65.disassembler import Disassembler

O = R / 'build/excitebike-pose-1101-v3'
LO, HI = 0xe1f9, 0xe26a
BRANCH = {'BEQ': 'jeq', 'BNE': 'jne', 'BCC': 'jcc', 'BCS': 'jcs',
          'BMI': 'jmi', 'BPL': 'jpl'}


def main():
    O.mkdir(exist_ok=True)
    donor = E.machine()
    dis = Disassembler(donor)
    instructions = {}
    pc = LO
    while pc < HI:
        size, display = dis.instruction_at(pc)
        mnemonic, mode = donor.disassemble[donor.memory[pc]]
        value = int.from_bytes(bytes(donor.memory[pc + 1:pc + size]), 'little')
        instructions[pc] = mnemonic, mode, value, display
        pc += size
    assert pc == HI
    source = ['; Authenticated Excitebike original E1F9..E269 animation selector.\n',
              '.setcpu "6502"\n.macpack longbranch\n.segment "CODE"\n',
              '.import ExState\n.export ExPose, ExPoseEnd\nExPose:\n']
    for pc, (mn, mode, value, display) in instructions.items():
        source.append(f'ExPose_{pc:04X}: ; {display}\n')
        if mode == 'rel':
            target = pc + 2 + (value if value < 128 else value - 256)
            assert target in instructions
            operand = f'ExPose_{target:04X}'
            mn = BRANCH[mn]
        elif mode in ('zpg', 'zpx', 'abs', 'abx'):
            assert value < 0x800, ('Unexpected non-private operand', pc, value)
            operand = f'ExState+${value:03x}' + (',x' if mode in ('zpx', 'abx') else '')
        elif mode == 'imm':
            operand = f'#${value:02x}'
        else:
            assert mode == 'imp'
            operand = ''
        source.append(' ' + mn.lower() + (' ' + operand if operand else '') + '\n')
    source.append('ExPoseEnd:\n')
    (O / 'excitebike-pose.s').write_text(''.join(source))
    (O / 'pose.cfg').write_text('SYMBOLS { ExState:type=export,value=$c000; }\n'
        'MEMORY { CODE:start=$a000,size=$400,file=%O; }\n'
        'SEGMENTS { CODE:load=CODE,type=ro; }\n')
    for command in [
        [R / 'tools/Windows/cc65/bin/ca65.exe', '-o', O / 'pose.o', O / 'excitebike-pose.s'],
        [R / 'tools/Windows/cc65/bin/ld65.exe', '-C', O / 'pose.cfg', '-o', O / 'pose.bin',
         '-Ln', O / 'pose.lbl', O / 'pose.o']]:
        subprocess.run([str(v) for v in command], check=True, capture_output=True)
    image = (O / 'pose.bin').read_bytes()
    labels = E.T.labels(O / 'pose.lbl')
    assert labels['ExPoseEnd'] - labels['ExPose'] == len(image)
    seed_path = R / 'build/excite-prince-component-1101-v2/state-799.bin'
    seed = seed_path.read_bytes()
    rng = random.Random(0xe1f9)
    seen, cycles, count = set(), [], 0
    # Independent actor, recovery and angle axes; clocks exercise wheel/pedal poses.
    for actor in range(4):
      for recovery in range(6):
       for angle in range(16):
        for phase in range(16):
            ram = bytearray(seed)
            ram[0x9c + actor] = recovery
            ram[0xac + actor] = angle
            ram[0x3f] = phase
            ram[0x36 + actor] = phase % 7
            ram[0x52] = phase % 3
            ram[0x98 + actor] = 0 if phase % 5 else 1
            ram[0xb0 + actor] = phase % 3
            ram[0x58 + actor] = (0, 1, 13, 14)[phase & 3]
            ram[0xb8 + actor] = (0, 31, 32, 48)[phase & 3]
            ram[0x90 + actor] = 1 if phase & 1 else 0
            ram[0x94 + actor] = 1 if phase & 2 else 0
            ram[0xdc + actor] = (0, 1, 255)[phase % 3]
            ram[0xbc + actor] = phase & 1
            ram[0x370 + actor] = (phase >> 1) & 1
            old = E.machine()
            list.__setitem__(old.memory, slice(0, 2048), ram)
            class Memory(list):
                pass
            memory = Memory([0] * 65536)
            memory[0xa000:0xa000 + len(image)] = image
            memory[0xc000:0xc800] = ram
            memory[:256] = [rng.randrange(256) for _ in range(256)]
            zp = bytes(memory[:256])
            new = E.T.NesMPU(memory=memory, pc=0xa000)
            args = dict(a=rng.randrange(256), x=actor, y=rng.randrange(256), p=0x20 | (phase & 13))
            expected = E.call(old, LO, **args)
            actual = E.T.run(new, 0xa000, **args)
            assert expected[:3] == actual[:3] and expected[4] == actual[4]
            assert expected[3] & 0xef == actual[3] & 0xef
            assert bytes(old.memory[:256]) == bytes(memory[0xc000:0xc100])
            assert bytes(old.memory[512:2048]) == bytes(memory[0xc200:0xc800])
            assert bytes(memory[:256]) == zp
            seen.add(actual[0]); cycles.append(actual[5]); count += 1
    files = [Path(__file__).resolve(), R / 'tools/reference/excitebike_original_cpu_1101_v2.py',
             seed_path, O / 'excitebike-pose.s', O / 'pose.bin', O / 'pose.lbl']
    report = dict(passed=True, donor_SHA256=E.SHA, source_range=[LO, HI],
        code_bytes=len(image), CPU_cases=count, observed_pose_indices=sorted(seen),
        relocated_cycles=[min(cycles), max(cycles)], private_state_base='C000',
        host_zero_page_preserved=True, native_verified=False, installed=False,
        limits='Executable selector only; graphics packets, resources, ownership, scene lifecycle and native gameplay remain integration work.',
        bindings={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
    (O / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k:report[k] for k in ('passed', 'code_bytes', 'CPU_cases', 'observed_pose_indices', 'relocated_cycles')}))


if __name__ == '__main__':
    main()
