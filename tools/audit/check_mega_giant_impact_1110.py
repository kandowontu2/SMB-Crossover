"""Link and qualify the Mega Giant native body defeat and shatter repair."""

import argparse
from collections import Counter
import hashlib
from itertools import product
import json
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory

import check_mega_giant_f33_1110 as F
import check_native_contact_tank_precheck_1110 as T

C, G, M, R, S, A = F.C, F.G, F.M, F.R, F.S, F.Rr
BASE = R / 'build/manual-title-delivery-1110/candidate.nes'
PIN = '9906787a73b6d319cd30a2d3a89f50e4aa6892d912a9c22e9c5e19a14e581835'
SOURCE = R / 'tools/reference/mega_giant_mario_impact_1110.s'
SELECTION = R / 'build/mega-giant-f33-1110/proof-v2.json'
CONTACT = (254, 0x9699)
SCOPES = (
    ('BOWSER', 0xbe00, 16, 0),
    ('BE_READ', 0xbe20, 32, 0),
    ('CONTACT', 0xbe44, 60, 0),
    ('BLOCK', 0xb174, 12, 0xea),
    ('AUDIO_VIEW', 0xb705, 63, 0),
)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def link(output):
    memory = ''.join(f'M{i}:start=${pc:x},size={n},file=%O,fill=yes,fillval={fill};'
                     for i, (_, pc, n, fill) in enumerate(SCOPES))
    segments = ''.join(f'{name}:load=M{i},type=ro;'
                       for i, (name, *_rest) in enumerate(SCOPES))
    with TemporaryDirectory(dir=output, prefix='link-') as folder:
        cfg, obj, binary, labels = [Path(folder) / f'impact.{s}' for s in ('cfg','o','bin','lbl')]
        cfg.write_text('MEMORY{' + memory + '} SEGMENTS{' + segments + '}')
        cc = R / 'tools/Windows/cc65/bin'
        subprocess.run([cc/'ca65.exe', SOURCE, '-o', obj], check=True)
        subprocess.run([cc/'ld65.exe', '-C', cfg, obj, '-o', binary, '-Ln', labels], check=True)
        symbols = {row.split()[2][1:]:int(row.split()[1], 16)
                   for row in labels.read_text().splitlines()}
        return binary.read_bytes(), symbols


def compose(raw, output):
    assert sha(raw) == PIN
    original_page = re.search(r'^RdaPage78:\s*(.*?)^RdaPage79:', A.ROGUE.read_text(), re.M|re.S)[1]
    page = bytes(int(n,16) for n in re.findall(r'\$([0-9a-fA-F]{2})\b', original_page))
    assert len(page) == 256 and page == A.native_slice(raw,90,0xbe00,256)
    assert A.native_slice(raw,90,0xb16f,5) == bytes.fromhex('d0f44c6bb8')
    existing_read = bytes.fromhex('08a5e9c9b0f014c9b1f01cc9b7f010c9b8f018c9bcd01aa93fd006'
                                  'a99dd002a904c5e89010b00aa97fd002a98fc5e8b00428b1e86028a90060')
    assert len(existing_read) == 57
    original_packet = bytes.fromhex('8d6a01a9968d6c01a9af8d6d01a9ce205a01')
    assert raw[16:1048592].count(original_packet) == 1
    assert A.native_slice(raw,126,0x9690,9) == bytes.fromhex('b417c02ed0034c289b')
    assert A.native_slice(raw,126,0x96ab,3) == bytes.fromhex('900160')
    assert 0x51 not in A.native_slice(raw,126,0x8e1a,14)
    assert A.native_slice(raw,126,0x8e28,5) == bytes.fromhex('a00dd91a8e')
    compiled, symbols = link(output)
    patches = []

    def add(bank, pc, before, after):
        assert before == A.native_slice(raw,bank,pc,len(before)) and len(before) == len(after),(bank,hex(pc))
        patches.append(dict(physical_PRG=bank,PC=pc,file_offset=A.at(bank,pc),
                            old_hex=before.hex(),new_hex=after.hex()))

    consumed = 0
    for name, pc, n, fill in SCOPES:
        before = (existing_read.ljust(n,b'\0') if name == 'AUDIO_VIEW' else bytes((fill,))*n)
        add(90,pc,before,compiled[consumed:consumed+n])
        consumed += n
    assert consumed == len(compiled)
    target = symbols['GiantContact']
    next_packet = bytes((0x8d,0x6a,1,0xa9,target&255,0x8d,0x6c,1,0xa9,target>>8,
                         0x8d,0x6d,1,0xa9,0xda,0x20,0x5a,1))
    add(126,0x9699,original_packet,next_packet)
    target = symbols['GiantCrushAsBrick']
    add(90,0xbcde,bytes.fromhex('a50620f59e'),bytes((0x20,target&255,target>>8,0xea,0xea)))
    table = ((0xbba7,0xbc67,192),(0xbe3f,0xbe5f,32))
    rows = [(banktab,i) for banktab,hitab,n in table for i in range(n)
            if A.native_slice(raw,62,banktab+i,1)==b'\xda'
            and A.native_slice(raw,62,hitab+i,1)==b'\xbe']
    assert rows == [(0xbba7,97)]
    add(62,0xbba7+97,b'\xda',b'\x5a')
    result = bytearray(raw)
    touched = set()
    for patch in patches:
        at = patch['file_offset']
        data = bytes.fromhex(patch['new_hex'])
        offsets = set(range(at,at+len(data)))
        assert not touched & offsets
        touched.update(offsets)
        result[at:at+len(data)] = data
    return bytes(result),patches,symbols


def donor():
    raw = C.DONOR.read_bytes()
    assert sha(raw) == C.DONOR_PIN
    mem = bytearray(65536)
    mem[0x8000:] = raw[16:32784]
    assert mem[0xd913:0xd916] == bytes.fromhex('4c95d7')
    assert mem[0xbd23:0xbd28] == bytes.fromhex('a9129d9001')
    counts = {}
    for enemy in (0,3,6,12,13,18,51):
        mem[0x0f],mem[0x16],mem[0x1e] = 1,enemy,0
        hits = Counter()
        C.plain_call(mem,0xd913,lambda c:hits.update((c.pc,)))
        assert hits[0xd795] == 1
        assert (mem[0x0f],mem[0x1e]&32) == ((0,0) if enemy == 13 else (1,32)),(enemy,mem[0x0f],mem[0x1e])
        counts[enemy] = mem[0x1e]
    return counts


def audio(before, after, labels):
    pair = [M.fresh(C.bundle(raw)) for raw in (before,after)]
    samples = 0
    for banktab, hitab, n in ((0xbba7,0xbc67,192),(0xbe3f,0xbe5f,32)):
        for row in range(n):
            tag = A.native_slice(before,62,banktab+row,1)[0]
            if tag&127 != 90:
                continue
            high = A.native_slice(before,62,hitab+row,1)[0]
            logical,bank = (0x80+row%32,row//32) if n==192 else (0xa0+row,0)
            for offset in range(256):
                p = (0x20,0x21,0x60,0x65)[(row+offset)%4]
                a,z = [A.call_audio(m,logical,offset,bank,p)[0] for m in pair]
                assert a == z,(row,offset,a,z)
                if high == 0xbe:
                    assert z[4] == A.native_slice(before,90,(high<<8)+offset,1)[0],(row,offset,z)
                samples += 1
    for kind, offset in product(('irq','lag_nmi'),(0,31,32,63,64,67,68,127,128,255)):
        b = A.call_audio(pair[0],0x81,offset,3,0x61,(kind,0xc434))
        n = A.call_audio(pair[1],0x81,offset,3,0x61,(kind,labels['GiantReadBE']))
        assert b[0] == n[0] and b[2]['handler'] == n[2]['handler']
    return dict(exact_authored_reads=samples,real_vectors=20)


def contact(before, after, labels):
    bundles = T.Contact.L.bundles(before,after)
    seeds = {key:[T.cold(image,key) for image in bundles] for key in (None,0,25,39,41)}
    counts = Counter()
    wrapped = (218, labels['GiantContact'])
    defeat = (254,0x9af5)
    for raw,variant,mode,p in [(r,r%10,r%2,p) for r,p in product(range(1,256),(0x21,0x65))]+[
            (0,v,h,p) for v,h,p in product(range(9),(0,1),(0x21,0x65))]:
        # Preserve real installed overlays for raw25/39/41 and Tank.
        key = raw if raw in (25,39,41) else 0 if raw == 0 and variant == 7 else None
        pair = [T.setup(s,raw,mode,p,variant=variant,whole=True) for s in seeds[key]]
        checks = []
        for cpu in pair:
            hits = []
            T.run(cpu,T.done,lambda c:hits.append(T.point(c)) if T.point(c)==T.NATIVE else None)
            checks.append(hits)
        x,z = pair
        assert checks[0] == checks[1]
        assert T.registers(x,0xef) == T.registers(z,0xef),(raw,variant,mode,p)
        assert T.live_stack(x) == T.live_stack(z)
        T.Contact.A.P.compare_memory(x.memory,z.memory)
        assert bytes(x.memory[0x15a:0x17b]) == bytes(z.memory[0x15a:0x17b])
        assert x.memory.ram_writes == z.memory.ram_writes
        counts['foreign'] += 1

    hit_cases = Counter()
    for enemy,mode,vertical,area in product((0,3,6,12,13,18,45,51),(0,1),(0,4,252),(0,1)):
        cpu = T.setup(seeds[None][1],0,mode,0x21,variant=9,enemy=enemy,whole=True)
        m = cpu.memory
        T.N.put(m,Player_Y_Speed=vertical,AreaType=area)
        if enemy == 13:
            m[0x6e2] = 0x55
        if enemy == 45:
            T.N.put(m,BowserHitPoints=5,DuplicateObj_Offset=2,WorldNumber=0)
        seen = Counter()
        T.run(cpu,T.done,lambda c:seen.update((T.point(c),)))
        assert seen[wrapped] == 1 and seen[(254,0x976c)] == 0,(enemy,mode,vertical,area,seen[wrapped])
        assert T.N.get(m,'GameEngineSubroutine') == 8
        assert m[0x1f] == 0 and m[0x10] == 0 if enemy == 13 else m[0x1f]&32,(enemy,m[0x1f],m[0x10])
        if enemy == 13:
            assert m[0x6e2] == 0 and m[0x17] == 13
        assert seen[defeat] == int(enemy not in (13,45))
        hit_cases[enemy] += 1

    for enemy,kind in product((6,13,45),('irq','lag_nmi')):
        cpu = T.setup(seeds[None][1],0,0,0x21,variant=9,enemy=enemy,whole=True)
        if enemy == 45:
            T.N.put(cpu.memory,BowserHitPoints=5,DuplicateObj_Offset=2,WorldNumber=0)
        hits = []
        def interrupt(c):
            if T.point(c) == wrapped and not hits:
                hits.append(C.vector(c,kind))
        T.run(cpu,T.done,interrupt)
        assert len(hits) == 1
        assert cpu.memory[0x10] == 0 if enemy == 13 else cpu.memory[0x1f]&32
        counts[kind] += 1

    for enemy,engine,overlap in ((6,7,True),(6,8,False),(46,8,True)):
        x,z = [T.setup(s,0,0,0x21,variant=9,enemy=enemy,overlap=overlap,whole=True)
               for s in seeds[None]]
        for cpu in (x,z):
            T.N.put(cpu.memory,GameEngineSubroutine=engine)
            hits = []
            T.run(cpu,T.done,lambda c:hits.append(T.point(c)) if T.point(c) == wrapped else None)
            assert not hits
        T.Contact.A.P.compare_memory(x.memory,z.memory)
        counts['native_rejection_or_pickup'] += 1
    return dict(**counts,hostile_confirmed_contacts=dict(hit_cases))


def live(after, labels):
    b = C.bundle(after)
    stage = F.read(SELECTION)['symbols']
    resident = F.read(G.RESIDENT)['storage']['symbols']
    offset = 16+128*8192
    meta = after[offset+212*1024:offset+213*1024]
    code = after[offset+214*1024:offset+215*1024]
    cookie = A.native_slice(after,84,0xbeec,16)
    m,cold = S.select_and_start(b,stage,cookie,meta,code)
    lives = M.get(m,'NumberofLives')
    defeat = []
    for update in range(360):
        x = C.world_x(m)
        M.put(m,SavedJoypadBits=1,SavedJoypad1Bits=1,SavedJoypad2Bits=0,NmiDisable=255)
        def visit(cpu):
            if (C.tag(m,cpu.pc),cpu.pc) == (254,0x9af5):
                defeat.append((update,C.world_x(m),cpu.x,m[0x17+cpu.x]))
        G.run_cpu(m,C.address(b,'GameLoop'),p=0x31,observe=visit)
        assert M.get(m,'GameEngineSubroutine') == 8 and M.get(m,'NumberofLives') == lives,(update,x,defeat)
        M.consume(m)
        m.writes.clear()
        m.ram_writes.clear()
        m.ppu_log.clear()
        if defeat and C.world_x(m)>=395:
            break
    assert defeat and defeat[0][3] == 6 and C.world_x(m)>=395,(defeat,C.world_x(m))

    results = []
    for tile,cut in product((0xc0,0xc1,0x51,0x58,0xc2,0xc3,0xc5,0x5f,0x60,0x6c,0x1f),
                            (None,('irq',labels['GiantCrushAsBrick'],218),('lag_nmi',labels['GiantCrushAsBrick'],218))):
        shatter = tile in (0xc0,0xc1,0x51,0x58)
        if cut and not shatter:
            continue
        seed = M.fork(m)
        C.place(seed,417,1)
        target = C.cell(448,176)
        for height in (144,160,176,192):
            seed[C.cell(448,height)] = 0
        seed[target] = tile
        seed.writes.clear()
        row = C.play(seed,resident,cut=cut)
        state_base = C.address(b,'Block_State')
        states = [seed[state_base+i] for i in (0,1)]
        shatters = [addr-state_base for addr,value in seed.writes
                    if state_base<=addr<state_base+2 and value==0x12]
        replacement = [seed[C.address(b,'Block_Metatile')+i] for i in (0,1)]
        if shatter:
            assert seed[target] in (0,0x23) and shatters and all(replacement[i]==0 for i in shatters),(tile,row,states,shatters,replacement,seed[target])
            assert bool(row['cuts']) == bool(cut)
            for _ in range(12):
                if seed[target] == 0:
                    break
                M.consume(seed)
                C.play(seed,resident)
            assert seed[target] == 0,(tile,row,states,replacement,seed[target])
        else:
            assert seed[target] == tile,(tile,row,seed[target])
        results.append(dict(tile=tile,shatter=shatter,cut=cut and cut[0],shatter_slots=shatters,
                            states=states,final_tile=seed[target]))
    return dict(actual_title_entrance=cold,held_Right_only_first_Goomba=defeat[0],final_world_X=C.world_x(m),
                lives=lives,block_and_structural_cases=results)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    out = cli.parse_args().output.resolve()
    assert out.is_relative_to(R/'build') and out != R/'build'
    out.mkdir(exist_ok=True)
    raw = BASE.read_bytes()
    after,patches,labels = compose(raw,out)
    print('Memory only',sha(after),labels,flush=True)
    donor_checks = donor()
    audio_checks = audio(raw,after,labels)
    print('Donor and canonical Rogue reader passed',donor_checks,audio_checks,flush=True)
    contact_checks = contact(raw,after,labels)
    print('Native contact passed',contact_checks,flush=True)
    live_checks = live(after,labels)
    print('Cold, walk and block cases passed',live_checks,flush=True)
    receipt = dict(passed=True,parent_SHA256=PIN,expected_memory_only_SHA256=sha(after),patches=patches,
                   labels=labels,ROM_written=False,donor_body_defeat=donor_checks,
                   canonical_Rogue_audio=audio_checks,native_contact=contact_checks,
                   Giant_live=live_checks,bindings={str(p.relative_to(R)):sha(p.read_bytes())
                       for p in (SOURCE,Path(__file__).resolve(),SELECTION,A.ROGUE,G.RESIDENT)})
    with (out/'proof.json').open('x') as output:
        json.dump(receipt,output,indent=2)
        output.write('\n')


if __name__ == '__main__':
    main()
