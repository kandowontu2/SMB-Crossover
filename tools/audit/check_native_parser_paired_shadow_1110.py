"""Prove paired second-page shadow writes and blank native collision cells."""

import argparse
from collections import Counter
from contextlib import contextmanager
from itertools import product
import json
from pathlib import Path
import subprocess
import tempfile

import check_mini_movement_prefix_1110 as M
import check_native_column_parser_local_1110 as Local
import check_native_parser_triple_shadow_1110 as Triple
import check_native_parser_triple_shadow_irq_1110 as Async
from check_mini_funded_actor_1108_v3 import install, live_stack, registers, run


R, D, N, P, Q = M.R,M.D,M.N,M.P,M.Q
BASE = R/'build/mini-contact-draw-native-1110/candidate.nes'
PIN = 'dd805e86b5d22cd7b7b3222915b821a92bc882ef63a139e5e3b6def7186e8a13'
PROFILE = R/'build/mini-dd-clear-and-nmi-profile-1110/capture/instruction-sample.json'
SOURCE = R/'tools/reference/native_parser_paired_shadow_1110.s'
OLD = (
    (2,0xa2e4,bytes.fromhex('2014a320efbfada00420dc95a200a0008403bca104b936ef293ff00198a4039109986910a8e8e00d90e6ac02604c7690')),
    (126,0x9076,bytes.fromhex('d004a8e00d60a509290f09c0a8a20038a50930128a99516099f16199d16698e910a8b0f0900320ddbf'
                             'a9d16509850ba963650a850ca9c08503a20ba0b0bd7168f00bdda104d004a901d002a900910b98186910a8e8e00d90e460eaea')),
    (2,0xbfdd,bytes.fromhex('8a99216199c16299a16798e910a8b0f060eaa9128d6c01a9a08d6d01a99a4c5a01ffff')),
)
PROTECTED = (0x6051,0x61f1,0x66d1)
MODELS = (('empty',(0,)*13),('flat',(0,)*11+(0x54,0x54)),('pipe',(0,)*7+(0x13,0x14,0x15,0x15,0x54,0x54)),
          ('dense',(0x54,)*13),('mixed',(0,0x54,0x13,0x0b,0,0x63,0x42,0x24,0xc3,0,0x15,0x54,0)))


def link(raw, out):
    assert P.sha(raw)==PIN
    for bank,pc,blob in OLD:
        D.check_span(raw,bank,pc,blob)
    D.check_span(raw,2,0xbfd9,bytes.fromhex('205a0160'))
    D.check_span(raw,127,0xef36,b'\0')
    for bank,pc,blob in ((126,0x95d8,'00d00303484a4a4a4aa8b9da95850a68290f1879d895850960'),
                         (2,0xa20c,'2014a3'),(26,0xa012,'2059ab')):
        D.check_span(raw,bank,pc,bytes.fromhex(blob))
    prg = raw[16:1048592]
    for code,sites in (('20ddbf',[(126,0x109c)]),('4c7690',[(2,0x0311)]),('20efbf',[(2,0x02e7)])):
        key = bytes.fromhex(code)
        actual = [(i//8192,i%8192) for i in range(len(prg)-2) if prg[i:i+3]==key]
        assert actual==sites,(code,actual)
    sample = json.loads(PROFILE.read_text())
    assert json.loads(PROFILE.with_name('binding.json').read_text())['ROM_sha256']==PIN
    assert sample['scene']['frame']==1460
    reached = {key:value for key,value in sample['foreground_opcodes'].items()
               if key.startswith('2:bf') and 0xbfdd<=int(key[2:],16)<0xbfef}
    assert sum(reached.values())==343 and reached['2:bfde']==65

    with tempfile.TemporaryDirectory(dir=out,prefix='shadow-') as tmp:
        cfg,obj,binary,lbl = (Path(tmp)/f'paired.{ext}' for ext in ('cfg','o','bin','lbl'))
        cfg.write_text('MEMORY { C:start=$A2E4,size=$30,file=%O; F:start=$9076,size=$5C,file=%O; '
                       'L:start=$BFDD,size=$23,file=%O; } '
                       'SEGMENTS { COLUMN:load=C,type=ro; FIXED:load=F,type=ro; LEVEL:load=L,type=ro; }')
        cc = R/'tools/Windows/cc65/bin'
        subprocess.run([cc/'ca65.exe',SOURCE,'-o',obj],check=True)
        subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',binary,'-Ln',lbl],check=True)
        code = binary.read_bytes()
        labels = {fields[2][1:]:int(fields[1],16) for line in lbl.read_text().splitlines()
                  if (fields:=line.split())}
    assert labels['StoreColumn']==0xa2e7 and labels['ResetHealthColumn']==0x9076
    assert labels['ClearFirst']==0xbfdd and labels['NativeThenVariant']==0xbfee
    rows = []
    for bank,pc,blob in OLD:
        rows.append(M.patch(bank,pc,blob,code[:len(blob)]))
        code = code[len(blob):]
    assert not code
    return install(raw,rows),rows,labels,reached


def set_tail(m, column, owner, tiles, provenance):
    m.raw_page(1,130)
    N.put(m,CurrentBank=130,SelectedCharacter=owner,BlockBufferColumnPos=column)
    for row,(tile,ground) in enumerate(zip(tiles,provenance,strict=True)):
        m[0x04a1+row],m[0x6871+row] = tile,ground
    for base in PROTECTED:
        m[base:base+416] = bytes((i*13+0x31)&255 for i in range(416))
    m[3],m[11],m[12] = 0x59,0xa5,0x67
    m.writes.clear()
    m.ram_writes.clear()
    m.ppu_log.clear()


def tails(before,after):
    images = [P.bundle(raw) for raw in (before,after)]
    counts = Counter()
    cases = [(column,owner,flags,name,tiles) for column,owner,flags,(name,tiles) in product(
        range(32),(0,2,25,41),(0x21,0xe5),MODELS)]
    cases += [(col,owner,0x61,'tile alphabet',tuple((i+row*7)&255 for row in range(13)))
              for i,col,owner in product(range(256),(0,15,16,31),(0,41))]
    for column,owner,flags,name,tiles in cases:
        provenance = tuple(tiles[row] if row==11 else tiles[row]^column for row in range(13))
        cpus,trace = [],[]
        for side,image in enumerate(images):
            m = N.Bus(image)
            set_tail(m,column,owner,tiles,provenance)
            c = M.cpu_at(m,0xa2ea if side==0 else 0xa2e7,242,flags,x=7,y=19)
            run(c,Async.end)
            cpus.append(c)
            trace.append(tuple((address,value) for address,value in m.writes
                               if any(base<=address<base+416 for base in PROTECTED)))
        a,b = cpus
        assert registers(a)==registers(b) and live_stack(a)==live_stack(b),(column,owner,flags,name)
        assert Triple.H.state(a.memory)==Triple.H.state(b.memory),(column,owner,flags,name)
        if owner:
            assert trace[0][:39]==trace[1][:39] and len(trace[0])==41
            assert trace[1][39:]==tuple(row for row in trace[0][39:] if row[1])
        else:
            assert not trace[0] and not trace[1]
        counts[column//16,owner,name,a.processorCycles-b.processorCycles] += 1
    return [[*key,count] for key,count in sorted(counts.items())]


def whole(before,after):
    images = [P.bundle(raw) for raw in (before,after)]
    counts = Counter()
    for area,column,owner in product((0x20,0x23,0x25,0x27,0x2c,0x31,0x40,0x41,0x61),
                                     (0,7,15,16,23,31),(0,2,25,41)):
        pair = [Local.prepare_column(image,area,column,owner,'native') for image in images]
        for c in pair:
            run(c,Local.done)
        a,b = pair
        assert registers(a)==registers(b) and live_stack(a)==live_stack(b)
        assert Triple.H.state(a.memory)==Triple.H.state(b.memory),(area,column,owner)
        counts[area,column//16,owner,a.processorCycles-b.processorCycles] += 1
    scene = Q.read_scene(PROFILE)
    loops = []
    for owner,rows in M.cold_seeds(before,after).items():
        for column in (0,15,16,31):
            pair = [Q.Edge.prepare(seed,scene,False) for seed in rows]
            for c in pair:
                N.put(c.memory,AreaParserTaskNum=4,BlockBufferColumnPos=column)
                run(c,Q.at_end)
            assert Q.state(pair[0])==Q.state(pair[1]),(owner,column)
            loops.append([owner,column,pair[0].processorCycles-pair[1].processorCycles])
    return dict(loaded_columns=[[ *key,count] for key,count in sorted(counts.items())],GameLoop=loops)


@contextmanager
def vector_binding(before):
    saved = Async.fixture,Async.OLD_PROVENANCE,Q.Edge.KERNEL,Q.Edge.KERNEL_PIN
    fixture = Async.fixture

    def start(seed,owner,column,flags,screen):
        c = fixture(seed,owner,column,flags,screen)
        N.put(c.memory,BlockBufferColumnPos=column)
        incumbent = seed.bundle['raw'][D.offset(2,0xa2e4):D.offset(2,0xa2e4)+3]==before[
            D.offset(2,0xa2e4):D.offset(2,0xa2e4)+3]
        c.pc = 0xa2ea if incumbent else 0xa2e7
        return c

    try:
        Async.fixture,Async.OLD_PROVENANCE = start,0x909f
        Q.Edge.KERNEL,Q.Edge.KERNEL_PIN = M.KERNEL,M.KERNEL_PIN
        yield
    finally:
        Async.fixture,Async.OLD_PROVENANCE,Q.Edge.KERNEL,Q.Edge.KERNEL_PIN = saved


def vectors(before,after,labels):
    with vector_binding(before):
        return Async.vectors(before,after,labels)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    cli.add_argument('--vectors-only',action='store_true')
    args = cli.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(R/'build') and out!=R/'build'
    raw = BASE.read_bytes()
    assert P.sha(raw)==PIN
    proof = out/'proof.json'
    if args.vectors_only:
        saved = json.loads(proof.read_text())
        assert saved['passed'] and saved['parent_SHA256']==PIN
        for name,digest in saved['bindings'].items():
            assert P.sha(Path(name).read_bytes())==digest,name
        after = install(raw,saved['patches'])
        assert P.sha(after)==saved['expected_memory_only_SHA256']
        result = vectors(raw,after,saved['labels'])
        target = out/'irq.json'
        refs = (Path(__file__),Path(Async.__file__),proof,R/'src/reset.s')
    else:
        out.mkdir()
        after,rows,labels,reached = link(raw,out)
        tail = tails(raw,after)
        print('All buffer columns, tile IDs and three shadow maps passed.',flush=True)
        result = dict(patches=rows,labels=labels,actual_DD_1460_page2_opcodes=reached,
                      column_tails=tail,**whole(raw,after))
        target = proof
        refs = (Path(__file__),SOURCE,BASE,PROFILE,PROFILE.with_name('binding.json'),M.KERNEL,
                Path(Local.__file__),Path(Triple.__file__),R/'src/level_tiles.s',R/'src/level_variants.s')
    assert not target.exists()
    result.update(passed=True,ROM_written=False,parent_SHA256=PIN,expected_memory_only_SHA256=P.sha(after),
                  bindings={str(p.resolve()):P.sha(p.read_bytes()) for p in refs})
    target.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(result['expected_memory_only_SHA256'],result.get('cuts',result.get('GameLoop')),flush=True)


if __name__=='__main__':
    main()
