"""Retain the native Y packet in ordinary dispatch, including SMB2 interrupts."""

import argparse
from collections import Counter
from contextlib import contextmanager
from itertools import product
import json
from pathlib import Path

import check_native_enemy_ordinary_dispatch_1110 as Q
import check_native_enemy_ordinary_dispatch_irq_1110 as IRQ
from check_mini_funded_actor_1108_v3 import install, registers, run


B, D, P, N, R = Q.B,Q.D,Q.P,Q.N,Q.R
Edge, LATE, OWNERS = Q.Edge,Q.LATE,Q.OWNERS
NORMAL, SCRATCH = Q.NORMAL,Q.SCRATCH
STUB, END = 0xb7db,0xb7e0
NEW = bytes.fromhex('a60db517c915b0034cdbb7e91420098a')
STUB_BYTES = bytes.fromhex('a0024c58a4')    # LDY #2 / JMP RunNormalEnemies
SOURCE = R/'tools/prepare_smb2_roster_main_v2.py'
LINKED_SOURCE = R/'build/bt-ready-menu-1031-v2/joint/src/object.s'
ORIGINAL_JOIN = Q.join


def patches(raw):
    p = Q.patch(raw)
    p['new_hex'] = NEW.hex()
    for path in (SOURCE,LINKED_SOURCE):
        src = path.read_text()
        assert 'S2MainEnemyAdmission:' in src and '.res 52-(*-GrowThePowerUp),$ea' in src
        assert 'sta Enemy_SprAttrib,x\nclc\nrts\n.res' in '\n'.join(line.strip() for line in src.splitlines())
    D.check_span(raw,0,0xb7be,bytes.fromhex('ad0260c919d00fa9fb8d6c01a9bc8d6d01a9f64c5a01a9009d88051860')
                 +b'\xea'*5+bytes.fromhex('b51fc906'))
    bank = raw[16:8208]
    hits = [(i+0xa000,target) for i, op in enumerate(bank[:-2]) if op in (0x20,0x4c)
            and STUB <= (target:=bank[i+1]+256*bank[i+2]) < END]
    assert not hits, hits
    return [p,dict(physical_PRG=0,CPU_half_open=[STUB,END],file_offset=D.offset(0,STUB),
                   old_hex='ea'*5,new_hex=STUB_BYTES.hex())]


def finite(before,after):
    cpus = []
    for image in (before,after):
        mem = bytearray(65536)
        for bank,pc in ((0,0xa000),(126,0x8000)):
            at = D.offset(bank,pc)
            mem[pc:pc+8192] = image[at:at+8192]
        cpus.append(N.NesMPU(memory=mem))
    counts = Counter()
    for eid,slot,flags in product(range(256),(0,2,5,234,255),(0x20,0x25,0x69,0xe4)):
        snapshots = []
        for c in cpus:
            m = c.memory
            m[:0x800] = bytes(0x800)
            m[0x0d],m[(0x17+slot)&255] = slot,eid
            c.pc,c.a,c.x,c.y,c.p,c.sp = Q.START,99,6,91,flags,244
            c.processorCycles = 0
            c.stPushWord(Q.STOP-1)
            run(c,lambda q:q.pc==(NORMAL if eid<0x15 else Q.JUMP+18))
            snapshots.append((registers(c),bytes(m[:256]),bytes(m[0x101+c.sp:0x200]),c.processorCycles))
        a,b = snapshots
        if eid<0x15:
            assert a[0][1:3]==b[0][1:3] and a[0][3]^b[0][3]==0x80 and a[0][4]==b[0][4]
            assert a[1][:7]+a[1][11:]==b[1][:7]+b[1][11:] and a[2]==b[2]
        else:
            assert a[:-1]==b[:-1],(eid,slot,flags,a,b)
        counts['ordinary' if eid<0x15 else 'retained',a[-1]-b[-1]] += 1
    return [[role,saving,count] for (role,saving),count in sorted(counts.items())]


def join(a,b,visitor=None):
    assert D.bank_pc(a)==D.bank_pc(b)==(128,NORMAL)
    # The direct path now reproduces Y. LDY #2 clears N, while the old
    # target high-byte load sets it. The native first load kills both A/NZ.
    ar,br = registers(a),registers(b)
    assert ar[1:3]==br[1:3] and (ar[3]^br[3]) in (0,0x80) and ar[4]==br[4]
    pending = {i for i,(x,y) in enumerate(zip(Q.raw_zp(a),Q.raw_zp(b),strict=True)) if x!=y}
    assert pending<=SCRATCH
    for c in (a,b):
        c.memory.pending_dispatch = frozenset(pending)
    for site in ((128,NORMAL),(128,0xb7be)):
        assert D.bank_pc(a)==D.bank_pc(b)==site
        if visitor:
            visitor(a,b)
        for c in (a,b):
            c.memory.dispatch_site = site
            c.step()
    assert registers(a)==registers(b)
    site,steps = ORIGINAL_JOIN(a,b,visitor)
    return site,steps+2


@contextmanager
def qualified_join():
    assert Q.join is ORIGINAL_JOIN
    Q.join = join
    try:
        yield
    finally:
        Q.join = ORIGINAL_JOIN


def whole(before,after):
    with qualified_join():
        return Q.whole(before,after)


def vectors(before,after):
    with qualified_join():
        return IRQ.vectors(before,after)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    args = cli.parse_args()
    raw = Q.BASE.read_bytes()
    changes = patches(raw)
    after = install(raw,changes)
    direct = finite(raw,after)
    print('Finite',direct,flush=True)
    gameplay = whole(raw,after)
    print('GameLoop',sum(len(row['cycles_saved']) for row in gameplay),flush=True)
    vectors_result = vectors(raw,after)
    print('Vectors',vectors_result['cuts'],flush=True)
    inputs = (Path(__file__),Path(Q.__file__),Path(IRQ.__file__),SOURCE,LINKED_SOURCE,
              R/'src/reset.s',R/'src/object.s',R/'src/common.s',Edge.KERNEL,Edge.E.PEAK,LATE)
    result = dict(passed=True,parent_SHA256=Q.PIN,expected_memory_only_SHA256=P.sha(after),ROM_written=False,
                  patches=changes,all_8bit_dispatch=direct,whole_GameLoop=gameplay,vectors=vectors_result,
                  supersedes=dict(image='7cb380b72a31215e98c4a1a6c12dedf8ad3717a362172b29e1ebc6715568d791',
                                  reason='SMB2 raw25 FF NMI during FarCallCommon at 0171 exposed live incoming Y in SMC audio staging',
                                  first_transient_writer=0x727c,old_value=2,unsafe_value=29),
                  bindings={str(p.resolve()):P.sha(p.read_bytes()) for p in inputs})
    args.output.mkdir(exist_ok=True)
    (args.output/'proof-v2.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['expected_memory_only_SHA256'],flush=True)


if __name__ == '__main__':
    main()
