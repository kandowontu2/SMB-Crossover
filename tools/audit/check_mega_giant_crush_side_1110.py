"""Qualify Giant-only side passage and the preserved Rogue source byte view."""

import argparse
from itertools import product
import json
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory

import check_mega_giant_impact_1110 as I
import check_shared_side_tank_precheck_1110 as Side

C, M, R, A = I.C,I.M,I.R,I.A
PIN = '7e031446492f9b59e30ab374724075b325462e00064b167f6a9e900765dd7ac9'
IMPACT = R/'build/mega-giant-impact-1110/proof.json'
SOURCE = R/'tools/reference/mega_giant_mario_crush_side_1110.s'
LIMITS = (0x24,0x6d,0x8a,0xc6)
PROTECTED = {0xc2,0xc3,0xc5,0x5f,0x60,0x6c,0x1f}


def source_image():
    proof = I.F.read(IMPACT)
    assert proof['passed'] and proof['parent_SHA256']==I.PIN
    old = I.BASE.read_bytes()
    assert I.sha(old)==I.PIN
    raw = I.T.install(old,proof['patches'])
    assert I.sha(raw)==proof['expected_memory_only_SHA256']==PIN
    return raw


def link(out):
    with TemporaryDirectory(dir=out,prefix='link-') as name:
        cfg,obj,binary,lbl = [Path(name)/f'side.{ext}' for ext in ('cfg','o','bin','lbl')]
        cfg.write_text('MEMORY{B:start=$bf00,size=$100,file=%O,fill=yes,fillval=0;}'
                       'SEGMENTS{GIANT_SIDE:load=B,type=ro;}')
        cc = R/'tools/Windows/cc65/bin'
        subprocess.run([cc/'ca65.exe',SOURCE,'-o',obj],check=True)
        subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',binary,'-Ln',lbl],check=True)
        labels = {row.split()[2][1:]:int(row.split()[1],16) for row in lbl.read_text().splitlines()}
        return binary.read_bytes(),labels


def compose(raw,out):
    assert I.sha(raw)==PIN
    old = re.search(r'^RdaPage6:\s*(.*?)^(?:RdaPage7:|\.segment)',A.ROGUE.read_text(),re.M|re.S)[1]
    page = bytes(int(v,16) for v in re.findall(r'\$([0-9a-fA-F]{2})\b',old))
    assert len(page)==256 and page[:36][-1]==0x64 and not any(page[36:])
    assert page==A.native_slice(raw,33,0xbf00,256)
    assert A.native_slice(raw,97,0xc469,23)==bytes.fromhex('09808d45018d1551a00049d4f0062005b74c38c44c00bf')
    assert [(table,i) for table,hi,n in ((0xbba7,0xbc67,192),(0xbe3f,0xbe5f,32))
            for i in range(n) if A.native_slice(raw,62,table+i,1)[0]&127==33]==[(0xbba7,7)]
    assert A.native_slice(raw,62,0xbc67+7,1)==b'\xbf'
    assert A.native_slice(raw,33,0xbeef,5)==bytes.fromhex('68284c8b95')
    code,labels=link(out)
    assert labels['GiantReadRogue33']==0xbf00 and code.count(page[:36])==1
    jump=b'\x4c'+labels['GiantSideNative'].to_bytes(2,'little')
    edits=((33,0xbf00,page,code),(33,0xbef1,bytes.fromhex('4c8b95'),jump),
           (97,0xc474,bytes.fromhex('d4f0'),bytes.fromhex('dad0')),(62,0xbba7+7,b'\xa1',b'\x21'))
    patches=[]
    for bank,pc,before,after in edits:
        assert A.native_slice(raw,bank,pc,len(before))==before and len(before)==len(after),(bank,hex(pc))
        patches.append(dict(physical_PRG=bank,PC=pc,file_offset=A.at(bank,pc),
                            old_hex=before.hex(),new_hex=after.hex()))
    return I.T.install(raw,patches),patches,labels


def native_leaf(before,after,labels):
    bundles = Side.Tank.Contact.L.bundles(before,after)
    seeds = [Side.N.fresh(b) for b in bundles]
    counts = {'owner':0,'filtered':0,'foreign':0,'async':0}
    at = (161,labels['GiantSideNative'])
    vectors = ('irq','lag_nmi')
    active = [(0,9,8,tile,flags) for tile,flags in product(range(256),(0x21,0x60,0x65,0xa5))]
    stale = [(0,v,g,tile,0x21) for v,g,tile in product((0,2,9),(4,5,7,8),(0,0x23,0x54,0x61,0xc2))
             if (v,g)!=(9,8)]
    foreign = [(raw,9,8,tile,0x21) for raw,tile in product((1,2,3,5,6,7,8,9,10),(0,0x23,0x61,0xc2))]
    for raw,variant,engine,tile,p in (*active,*stale,*foreign):
        typed = (raw,variant,engine)==(0,9,8)
        filtered = typed and tile not in PROTECTED and (tile==0x23 or 0<tile<LIMITS[tile>>6])
        pair=[Side.new_leaf(seed,raw,variant,engine,17,253,176,tile,p) for seed in seeds]
        for cpu in pair:
            Side.W.run(cpu,Side.done)
        x,z=pair
        expected=(0,x.x,x.y,(x.p&0x6d)|2) if filtered else (x.a,x.x,x.y,x.p&0xef)
        assert (z.a,z.x,z.y,z.p&0xef)==expected,(raw,variant,engine,tile,expected,Side.registers(z,0xef))
        assert Side.live_stack(x)==Side.live_stack(z)
        old_mem,new_mem=Side.W.memory(x.memory),Side.W.memory(z.memory)
        if filtered:
            assert old_mem[3][0x179-0x15a]==tile and new_mem[3][0x179-0x15a]==0
            assert old_mem[:3]==new_mem[:3] and old_mem[4:]==new_mem[4:]
            assert old_mem[3][:0x179-0x15a]==new_mem[3][:0x179-0x15a]
            assert old_mem[3][0x17a-0x15a:]==new_mem[3][0x17a-0x15a:]
        else:
            assert old_mem==new_mem,(raw,variant,engine,tile)
        assert Side.writes(x.memory,0)==Side.writes(z.memory,0)
        counts['owner' if typed else 'foreign']+=1
        counts['filtered']+=filtered

    for tile,kind in product((0x23,0x54,0x61,0xc2,0xc5),vectors):
        cpu=Side.new_leaf(seeds[1],0,9,8,17,253,176,tile,0x21)
        hits=[]
        def witness(c):
            if Side.ISR.point(c)==at and not hits:
                hits.append(C.vector(c,kind))
        Side.W.run(cpu,Side.done,witness)
        assert len(hits)==1 and cpu.a==(tile if tile in PROTECTED else 0),(tile,kind,hits,cpu.a)
        counts['async']+=1
    return counts


def audio(before,after,labels):
    pair=[M.fresh(C.bundle(raw)) for raw in (before,after)]
    count=0
    for table,n in ((0xbba7,192),(0xbe3f,32)):
        for row in range(n):
            tag=A.native_slice(before,62,table+row,1)[0]
            if tag&128 and (n,row)!=(192,7):
                continue
            logical,bank=(0x80+row%32,row//32) if n==192 else (0xa0+row,0)
            for offset in range(256):
                p=(0x20,0x21,0x60,0x65)[offset%4]
                x,z=[A.call_audio(m,logical,offset,bank,p)[0] for m in pair]
                assert x==z,(logical,bank,offset,x,z)
                count+=1
    for offset,kind in product((0,35,36,127,255),('irq','lag_nmi')):
        old=A.call_audio(pair[0],0x87,offset,0,0x61,(kind,0xc434))
        new=A.call_audio(pair[1],0x87,offset,0,0x61,(kind,labels['GiantReadRogue33']))
        assert old[0]==new[0] and old[2]['handler']==new[2]['handler']
    return dict(canonical_reads=count,real_vectors=10)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    out=parser.parse_args().output.resolve()
    assert out.is_relative_to(R/'build') and out!=R/'build'
    out.mkdir(exist_ok=True)
    before=source_image()
    after,patches,labels=compose(before,out)
    print('Memory only',I.sha(after),labels,flush=True)
    queries=native_leaf(before,after,labels)
    print('Native side queries',queries,flush=True)
    audio_cases=audio(before,after,labels)
    print('Canonical Rogue audio',audio_cases,flush=True)
    q=dict(passed=True,parent_SHA256=PIN,expected_memory_only_SHA256=I.sha(after),ROM_written=False,
           patches=patches,labels=labels,native_side=queries,canonical_audio=audio_cases,
           scope='Native side queries in active raw0 variant9 yield empty only for donor sweep material or pending23. '
                 'Native head/foot, pipes, hidden items and exits retain ordinary routing. Source sweep still owns actual destruction.',
           bindings={str(p.relative_to(R)):I.sha(p.read_bytes()) for p in
                     (IMPACT,SOURCE,Path(__file__).resolve(),A.ROGUE)})
    with (out/'proof.json').open('x') as f:
        json.dump(q,f,indent=2)
        f.write('\n')


if __name__=='__main__':
    main()
