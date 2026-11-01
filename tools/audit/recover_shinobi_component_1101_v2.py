"""Recover the original Tengen Shinobi actor, scripts, renderer and weapon unit.

This is a private source/CPU component, not an enabled SMB character.  Only the
exact donor and one historical intro snapshot are read; no emulator is run.
"""
from pathlib import Path
import argparse, hashlib, json, re, subprocess, sys, zipfile
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R/'tools'), str(R/'tools/audit')]
from private_build_outputs_v1 import validate

ROM = Path('C:/NES/Shinobi (USA) (Unl).nes')
EXPECTED = '24e1e425b84776ab2116b4dd1a85545f78e9a507caa8367a490cc77adab46874'
SPANS = [(0x8000, 0x8623), (0x9bba, 0xa8f0), (0xc875, 0xcadc)]
WORDS = {**{a: None for a in range(0x80fd, 0x8119, 2)}, 0x9c4c: None,
         **{a: None for a in range(0x9ec1, 0x9ecd, 2)}}
POSES = [0, 1, 2, 3, 4, 5, 8, 9, 0x39, 0x3a, 0x3b, 0x3c, 0x3d,
         0x4a, 0x4c, 0x4d, 0x4e, 0x4f, 0x57, 0x5e, 0x5f]
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
save = lambda p, x: p.write_text(json.dumps(x, indent=2)+'\n', encoding='utf-8')


def original_memory(raw):
    m = MPU()
    m.memory[0x8000:0xe000] = raw[16:16+0x6000]
    m.memory[0xe000:] = raw[16+0x1e000:16+0x20000]
    return m


def inside(a):
    return any(lo <= a < hi for lo, hi in SPANS)


def graph(m):
    roots = [m.WordAt(a) for a in range(0x9b94, 0x9bba, 2)]
    roots += [m.WordAt(a) for a in WORDS]
    roots += [0x8000, 0x801d, 0x8026, 0x802f, 0x8038, 0x805a,
              0x8215, 0x8250, 0x83fc, 0xa196, 0xc875, 0xc880, 0xc9da, 0xc978]
    d = Disassembler(m); todo = list(roots); code = {}; external = {}; ram = {}; reads = {}
    while todo:
        pc = todo.pop()
        if pc in code: continue
        if not inside(pc): external.setdefault(pc, []); continue
        n, text = d.instruction_at(pc)
        mn, mode = m.disassemble[m.memory[pc]]
        assert text != '???' and mn not in ['BRK', 'RTI'], (hex(pc), text)
        a = m.memory[pc+1] + (m.memory[pc+2]*256 if n == 3 else 0) if n > 1 else None
        code[pc] = dict(size=n, text=text, mnemonic=mn, mode=mode, operand=a,
                        bytes=list(m.memory[pc:pc+n]))
        if mn in ['JSR', 'JMP']:
            if mode == 'ind':
                assert pc in [0x80fa, 0x9c49, 0x9ebe], (hex(pc), text)
            elif inside(a): todo.append(a)
            else: external.setdefault(a, []).append(pc)
        elif mode == 'rel': todo.append((pc+2+(a if a < 128 else a-256)) & 65535)
        elif mode in ['abs', 'abx', 'aby', 'zpg', 'zpx', 'zpy', 'iny', 'inx', 'ind']:
            (ram if a < 0x8000 else reads).setdefault(a, []).append(pc)
        if mn not in ['RTS', 'RTI', 'JMP']: todo.append(pc+n)
    occupied = set()
    for pc, z in code.items():
        for a in range(pc, pc+z['size']):
            assert a not in occupied, (hex(pc), hex(a))
            occupied.add(a)
    words = {a: m.WordAt(a) for a in WORDS}
    for a in words: assert a not in occupied and a+1 not in occupied, hex(a)
    return code, external, ram, reads, words


def scripts(m, code, words):
    immediate = {}; roots = []
    # Original code installs little-endian interpreter pointers in these fields.
    for pc, z in code.items():
        if z['mnemonic'] != 'LDA' or z['mode'] != 'imm': continue
        p = pc+2
        if list(m.memory[p:p+3]) != [0x9d, 0x3f, 0x04]: continue
        assert m.memory[p+3] == 0xa9 and list(m.memory[p+5:p+8]) == [0x9d, 0x4a, 0x04]
        a = m.memory[pc+1] + 256*m.memory[p+4]
        assert inside(a), hex(a)
        immediate[pc] = ('<', a); immediate[p+3] = ('>', a); roots.append(a)
    # Each opcode consumes its exact original operand count. $82 is the sole
    # two-byte address operand; $8e..ff terminates without consuming an operand.
    todo = list(roots); seen = set(); streams = {}
    sizes = {0: 2, 1: 2, 2: 3, 3: 1, 4: 1, 5: 2, 6: 1, 7: 2,
             8: 2, 9: 2, 10: 1, 11: 1, 12: 2, 13: 2}
    while todo:
        pc = todo.pop(); start = pc; commands = []
        while pc not in seen:
            assert inside(pc) and pc not in code, hex(pc)
            seen.add(pc); op = m.memory[pc]; commands.append([pc, op])
            if op < 0x80: pc += 1; continue
            if op >= 0x8e: break
            if op in [0x8a, 0x8b]: break  # persistent interpreter stop flags
            n = sizes[op & 15]
            if op == 0x82:
                a = m.WordAt(pc+1); assert inside(a)
                words[pc+1] = a; todo.append(a); break
            pc += n
        streams[start] = commands
    return immediate, streams


def art_graph(m):
    """Read the complete animator/packet closure of every reachable player pose.

    The source renderer consumes five-byte rectangle records. Attribute bit04
    chains another rectangle; dimensions use source8x8 sprite mode here.
    """
    data = set(); words = {}; poses = []
    def add(a,n):
        assert 0xe000<=a<a+n<=0x10000, (hex(a),n)
        data.update(range(a,a+n))
    for pose in POSES:
        header = m.WordAt(0xe620+pose*2); count=m.memory[header]
        assert 1<=count<=32,(pose,count)
        add(header,4+2*count);timer=m.WordAt(header+2)
        if timer>=0xe000:add(timer,count)
        else:assert timer==0 and count<=4,(pose,timer,count)
        words[header+2]=timer; packets=[]
        for frame in range(count):
            at=header+4+2*frame;p=m.WordAt(at);words[at]=p;packets.append(p)
            for _ in range(32):
                add(p,5)
                if not(m.memory[p+4]&4):break
                p+=5
            else:raise AssertionError(('Unterminated pose packet',pose,frame))
        poses.append(dict(pose=pose,header=header,count=count,timer=timer,packets=packets))
    return data,words,poses


def emit(m, code, words, immediate, portable):
    label = lambda a: f'Sh_{a:04X}'
    out = []
    for index, (lo, hi) in enumerate(SPANS):
        out.append(f'.segment "PART{index}"')
        pc = lo
        while pc < hi:
            if pc not in code:
                if pc in words:
                    a = words[pc]; value = label(a) if inside(a) else f'${a:04x}'
                    out.append(f'{label(pc+1)} = {label(pc)}+1')
                    out.append(f'{label(pc)}: .word {value}'); pc += 2; continue
                out.append(f'{label(pc)}: .byte ${m.memory[pc]:02x}'); pc += 1; continue
            z = code[pc]; mn, mode, a = z['mnemonic'], z['mode'], z['operand']; text = z['text']
            if mode == 'rel':
                target = (pc+2+(a if a < 128 else a-256)) & 65535
                text = mn.lower()+' '+label(target)
                if portable: text = 'j'+text[1:]
            elif mode == 'imm' and portable and pc in immediate:
                prefix, target = immediate[pc]; text = mn.lower()+' #'+prefix+label(target)
            elif mode == 'imm' and portable and pc == 0x803c:
                text = 'lda #>(ShState+$0300)'
            elif mode in ['abs', 'abx', 'aby', 'zpg', 'zpx', 'zpy', 'iny', 'inx', 'ind']:
                if mn in ['JSR', 'JMP'] and mode != 'ind':
                    target = label(a) if inside(a) else f'ShExternal_{a:04X}'
                elif inside(a): target = label(a)
                elif portable and a < 0x8000:
                    assert a < 0x800, (hex(pc), text)
                    target = f'ShScratch+${a:02x}' if a < 4 else f'ShState+${a:04x}'
                else: target = f'${a:04x}' if z['size'] == 3 else f'${a:02x}'
                token = re.search(r'\$[0-9a-fA-F]+', text); assert token
                text = text[:token.start()]+target+text[token.end():]
                if not portable and z['size'] == 3 and a < 256: text = text.replace(target, 'a:'+target, 1)
                if portable and (mn, mode) in [('STY', 'zpx'), ('STX', 'zpy')]:
                    t = 'TYA' if mn == 'STY' else 'TXA'; suffix = ',X' if mn == 'STY' else ',Y'
                    text = 'php\n pha\n '+t+'\n sta '+target+suffix+'\n pla\n plp'
            out.append(f'{label(pc)}: {text} ; original ${pc:04x}')
            pc += z['size']
    return '\n'.join(out)+'\n'


def build(out):
    out.mkdir(exist_ok=True); source = out/'source'; source.mkdir(exist_ok=True)
    assert sha(ROM) == EXPECTED
    raw = ROM.read_bytes(); m = original_memory(raw)
    code, external, ram, reads, words = graph(m)
    immediate, streams = scripts(m, code, words)
    art_data,art_words,art_poses=art_graph(m)
    print('Recovered instructions', len(code), 'external callbacks', [hex(a) for a in external], flush=True)
    extern = ''.join(f'ShExternal_{a:04X}=${a:04x}\n' for a in sorted(external))
    for portable in [False, True]:
        mode = 'portable' if portable else 'original'
        (source/(mode+'.inc')).write_text(emit(m, code, dict(words), immediate, portable), encoding='utf-8')
        head = '.setcpu "6502"\n.macpack longbranch\nShState=$6000\nShScratch=$00\n'+extern
        head += '.include "'+mode+'.inc"\n'
        (source/(mode+'.s')).write_text(head, encoding='utf-8')
        if portable:
            config = 'MEMORY { LAB:start=$9000,size=$4000,file=%O,fill=yes,fillval=$ff; }\nSEGMENTS { '+''.join(f'PART{i}:load=LAB,type=ro; ' for i in range(3))+'}\n'
        else:
            config = 'MEMORY { '+''.join(f'M{i}:start=${a:04x},size=${b-a:04x},file=%O; ' for i, (a,b) in enumerate(SPANS))+'}\nSEGMENTS { '+''.join(f'PART{i}:load=M{i},type=ro; ' for i in range(3))+'}\n'
        (source/(mode+'.cfg')).write_text(config, encoding='utf-8')
        cc = R/'tools/Windows/cc65/bin'
        commands = [[cc/'ca65.exe', '-g', '-I', source, source/(mode+'.s'), '-o', out/(mode+'.o')],
                    [cc/'ld65.exe', '-C', source/(mode+'.cfg'), out/(mode+'.o'), '-o', out/(mode+'.bin'), '-Ln', out/(mode+'.lbl'), '--dbgfile', out/(mode+'.dbg')]]
        for command in commands:
            command = list(map(str, command)); validate(command, out, cwd=source)
            q = subprocess.run(command, cwd=source, capture_output=True, text=True)
            assert q.returncode == 0, q.stderr
    original = bytes(v for lo, hi in SPANS for v in m.memory[lo:hi])
    assert (out/'original.bin').read_bytes() == original, 'Semantic donor reproduction mismatch'
    # Exact archived intro fixture, not a gameplay recording or qualification.
    archive = R/'build/_recovery/legacy-sources-2026-10-31.zip'
    member = 'full-menu-source-art-v1/native/shinobi-discovery-v1/frame-00600.bin'
    with zipfile.ZipFile(archive) as z:
        entry = next(x for x in json.loads(z.read('index.json')) if x['path'] == member)
        fixture = z.read('objects/'+entry['sha256'])
    assert hashlib.sha256(fixture).hexdigest() == entry['sha256'] and len(fixture) == 14638
    (out/'intro-reference.bin').write_bytes(fixture)
    (out/'source-fixed.bin').write_bytes(bytes(m.memory[0xe000:]))
    (out/'source-body.chr').write_bytes(raw[16+0x20000+4096:16+0x20000+8192])
    report = dict(passed=True, source_CPU_component=True, native_port=False, installed=False,
        donor=str(ROM), donor_sha256=EXPECTED, mapper=64, original_semantic_bytes=len(original),
        original_semantic_ranges=SPANS, original_all_recovered_ranges_byte_exact=True,
        recovered_instructions=len(code), original_player_states=[m.WordAt(a) for a in range(0x9b94,0x9bba,2)],
        magic_targets=[m.WordAt(a) for a in range(0x9ec1,0x9ecd,2)],
        script_roots=list(streams), script_commands=streams,
        relocated_script_immediates={f'{a:04X}':[p,t] for a,(p,t) in immediate.items()},
        relocated_pointer_words={f'{a:04X}':v for a,v in words.items()},
        art=dict(reachable_pose_ids=POSES,poses=art_poses,original_unique_data_bytes=len(art_data),
                 analyzed_art_words=len(art_words),art_relocation_implemented=False,
                 original_fixed_bank_required_by_portable_unit=True,
                 relocation_caveat='Animations with timer pointer0000 consume borrowed RAM00 onward as their timer bytes. Relocating their header changes incidental timer values; do not silently normalize the timer or claim exact animation timing.'),
        callbacks={f'{a:04X}':v for a,v in external.items()},
        RAM_fields={f'{a:04X}':v for a,v in ram.items()}, ROM_reads={f'{a:04X}':v for a,v in reads.items()},
        original_intro=dict(archive_member=member, sha256=entry['sha256'], gameplay=False,
                            reason='Historical captures600..2399 retain state0/intro fields; no gameplay claim.'),
        private_layout=dict(code=[0x9000,0xd000], state=[0x6000,0x6800], borrowed_ZP=[0,4],
                            host_resource_grant=False, source_fixed_data=[0xe000,0x10000]),
        scope='Assembled authentic19-state actor, six magic entry points, motion/script interpreter, animation/OAM renderer, native four-slot weapon initialization/update. Original semantic source exactly reproduces all declared donor spans. No SMB hooks, native qualification, audio, collision or whole-stage claim.')
    report['bindings'] = {str(p.resolve()):sha(p) for p in [ROM, Path(__file__), *sorted(source.iterdir()), out/'original.bin', out/'portable.bin', out/'intro-reference.bin', out/'source-fixed.bin', out/'source-body.chr']}
    save(out/'assembly.json', report)
    print(json.dumps({k:v for k,v in report.items() if k not in ['bindings','callbacks','RAM_fields','ROM_reads','script_commands']}))


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--output', type=Path, default=R/'build/shinobi-component-1101-v2')
    build(p.parse_args().output.resolve())
