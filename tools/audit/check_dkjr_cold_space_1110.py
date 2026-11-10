"""Compare the exact and packed DK Jr. cold leaves on the MMC5 CPU bus."""
from hashlib import sha256
import json
import sys

import check_dkjr_gap_cap_probe_1110 as Gap
from check_mini_funded_actor_1108_v3 import slim_fork


N, C = Gap.N, Gap.C
SOURCE = Gap.B.R / 'tools/reference/dkjr_cold_compact_1110.s'
sys.path.insert(0,str(SOURCE.parent))
from sonic_sms_compact_cold_worker_1110 import assemble

START, END = 0xd25e, 0xd2d5
PREIMAGE = 'cf8d2da03ec64fc89b860499805be3e706fe7c85f0ead368250c164c21affa7a'


def invoke(seed, worker, fault):
    class Trace(type(seed)):
        reads = 0

        def __getitem__(self, at):
            value = super().__getitem__(at)
            if at==0x2007:
                self.reads += 1
                if self.reads==fault:
                    return value ^ 1
            return value

    m = slim_fork(seed)
    m.__class__ = Trace
    m.raw_page(1,3)
    m.raw_page(2,2)
    m.ram[3][:] = bytes(8192)
    m.ram[2][START-0xc000:END-0xc000] = worker.ljust(END-START,b'\xff')
    m.writes.clear()
    m.ppu_log.clear()
    c = N.NesMPU(memory=m,pc=START)
    c.a,c.x,c.y,c.p,c.sp = 83,71,109,0x24,224
    c.stPushWord(0x5aff)
    for step in range(130000):
        if (c.pc,c.sp)==(0x5b00,224):
            break
        assert m[c.pc]
        c.step()
    else:
        raise AssertionError((hex(c.pc),c.sp,m.reads))
    writes = [(at,value) for at,value in m.writes if at in (0x5130,0x5123,0x2006)]
    return (c.a,c.x,c.y,c.p,c.sp),m.reads,bytes(m.ram[3]),tuple(m.rawtags),writes,step


def main():
    raw = Gap.NIGHTLY.read_bytes()
    digest = sha256(raw).hexdigest()
    assert digest in (Gap.PIN,Gap.SECOND)
    carrier = 1048592+960*1024
    old = raw[carrier+START-0xd000:carrier+END-0xd000]
    assert sha256(old).hexdigest()==PREIMAGE
    linked = assemble(SOURCE.read_text(encoding='utf-8'),{'DK_COLD':(START,END-START)})
    new = linked['images']['DK_COLD']
    assert linked['symbols']['DkColdEnd']==0xd2c7
    seed = C.cold(raw,raw[534485:534501])
    witnesses = []
    for fault in (None,1027,2050,16400):
        before,after = [invoke(seed,worker,fault) for worker in (old,new)]
        assert before[:-1]==after[:-1]
        assert bool(after[0][3]&1)==(fault is None)
        witnesses.append(dict(fault=fault,reads=after[1],regs=after[0],mapper_writes=len(after[4]),
                              steps=[before[-1],after[-1]]))
    assert witnesses[0]['reads']==16400 and witnesses[0]['mapper_writes']==80
    print(json.dumps(dict(image_SHA256=digest,old_bytes=len(old),new_bytes=len(new),
                          assembled_SHA256=sha256(new).hexdigest(),free=[0xd2c7,END],
                          witnesses=witnesses),separators=(',',':')),flush=True)


if __name__=='__main__':
    main()
