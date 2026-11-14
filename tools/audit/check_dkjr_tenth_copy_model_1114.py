"""Isolated 6502/PPU-buffer model of the unallocated tenth-copy request.

No candidate ROM or live overlay is composed. A minimal CPU address space
executes the exact measured copier and uses declared input pages. It tests
copy/readback arithmetic, not ownership, native interrupts or header commit.
"""
from hashlib import sha256
import argparse
import json

import measure_dkjr_floor_entry_handlers_1114 as M

S=M.S;F=S.Replay;G=F.Gate
P,H,N=G.P,G.H,G.N


class CopyMemory:
    def __init__(self,code,pages,fault=None,status=0):
        self.data=bytearray((0xa5,))*65536
        self.data[0xd25e:0xd25e+len(code)]=code
        self.pages=pages;self.fault=fault;self.written=set();self.payload_writes=[]
        self.ppu_address=0;self.ppu_latch=0;self.ppu_buffer=0
        self.chr_high=0;self.chr_page=0;self.ppu_reads=0
        self.status=status

    def __getitem__(self,at):
        if isinstance(at,slice):return self.data[at]
        at&=65535
        if at==0x2002:
            self.ppu_latch=0
            result=self.status;self.status&=0x7f
            return result
        if at==0x2007:
            result=self.ppu_buffer
            # The last prefetch at1000 is discarded before the next map.
            offset=self.ppu_address-0xc00
            self.ppu_buffer=self.pages[self.chr_page][offset]if 0<=offset<1024 else 0
            self.ppu_address=(self.ppu_address+1)&0x3fff;self.ppu_reads+=1
            return result
        value=self.data[at]
        if at==self.fault and at in self.written:return value^1
        return value

    def __setitem__(self,at,value):
        at&=65535;value&=255
        if at==0x5130:self.chr_high=value&3
        elif at==0x5123:self.chr_page=(self.chr_high<<8)|value
        elif at==0x2006:
            if not self.ppu_latch:self.ppu_address=value<<8
            else:self.ppu_address=(self.ppu_address&0xff00)|value
            self.ppu_latch^=1
        else:
            self.data[at]=value
            if 0xa000<=at<0xd100:
                self.written.add(at);self.payload_writes.append(at)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--current-kind',choices=M.Input.KINDS,default='hidden-421')
    args=ap.parse_args();measured=M.measure(current_kind=args.current_kind)
    code=bytes.fromhex(measured['cold_extension']['proposed_hex_with_REVIEW_ONLY_page931'])
    _,old=F.load_inputs();private,_=S.proposal(old);body=P.T.payload(private)
    numbers=(817,833,847,856,867,881,882,883,959,931)
    pages={page:body[i*1024:(i+1)*1024]for i,page in enumerate(numbers[:9])}
    extra=bytes((i*73+19)&255 for i in range(768))+body[9216:9472]
    pages[931]=extra
    expected=set(range(0xa000,0xc000))|set(range(0xc900,0xd100))
    old_code=bytes.fromhex(measured['cold_extension']['current_preimage_hex'])
    def execute(memory,incoming):
        c=N.NesMPU(memory=memory,pc=0xd25e);c.a,c.x,c.y,c.p,c.sp=83,71,91,incoming,224
        c.stPushWord(0x5aff);minimum=c.sp
        for steps in range(400000):
            if (c.pc,c.sp)==(0x5b00,224):return c,minimum
            minimum=min(minimum,c.sp);c.step()
        raise AssertionError(('Copy model CPU bound',hex(c.pc),memory.fault))
    cases=[]
    modes=[(p,None,status)for p in (0x20,0x21,0x61,0xff)for status in (0,0x40,0x80,0xc0)]
    modes.extend((0x61,at,0)for at in (0xcd00,0xce80,0xcfff,0xd000,0xd0ff))
    for incoming,fault,status in modes:
        memory=CopyMemory(code,pages,fault,status)
        c,minimum=execute(memory,incoming)
        assert memory.written<=expected
        assert c.sp==224
        if fault is None:
            assert memory.written==expected and len(memory.payload_writes)==10240
            assert bytes(memory.data[0xa000:0xc000])==body[:8192]
            assert bytes(memory.data[0xc900:0xcd00])==body[8192:9216]
            assert bytes(memory.data[0xcd00:0xd000])==extra[:768]
            assert bytes(memory.data[0xd000:0xd100])==body[9216:9472]
            assert (c.a,c.x,c.y)==(8,0,0)and c.p&0x83==3
            reference,_=execute(CopyMemory(old_code,pages,status=status),incoming)
            assert (c.a,c.x,c.y,c.p,c.sp)==(reference.a,reference.x,reference.y,reference.p,reference.sp)
            assert bytes(memory.data[3:6])==bytes((0,0xd1,10))
            assert memory.ppu_reads==20500
        else:assert not c.p&1
        # This private primitive does not publish a raw2 ready header.
        assert bytes(memory.data[0xdfe0:0xdff0])==bytes((0xa5,))*16
        cases.append(dict(incoming_P=incoming,initial_PPU_status=status,fault_address=fault,
            accepted=bool(c.p&1),AXY=[c.a,c.x,c.y],P=c.p,SP=c.sp,minimum_SP=minimum,
            data_writes=len(memory.payload_writes),PPU_reads=memory.ppu_reads,
            full_duplicate_metadata_exact=fault is None))
    print('DKJR_TENTH_COPY_MODEL '+json.dumps(dict(passed=True,
        private_input_SHA256=S.PIN,review_target_only=931,CHR_or_RAM_lease_granted=False,
        current_review_input=measured['current_review_input'],
        tested_worker_SHA256=sha256(code).hexdigest(),worker_bytes=len(code),
        complete_target_half_open=[[0xa000,0xc000],[0xc900,0xd100]],
        requested_extra_RAM_half_open=[0xcd00,0xd000],
        duplicated_metadata_half_open=[0xd000,0xd100],
        synthetic_page_shape_SHA256=sha256(extra).hexdigest(),cases=cases,
        ROM_composed=False,ROM_written=False,outputs_written=0,
        native_or_IRQ_or_ownership_claim=False,
        status_contract='Full returned P matches current copier for incomingV1 and PPU status00/40/80/C0. BIT2002 sets V from PPU status. This private worker does not preserve incomingV; the outer public cold wrapper remains responsible for its saved-P ABI.',
        scope='Exact measured118B worker on an isolated6502 bus with buffered PPU reads and declared page data. Confirms bounded10240-byte copy/echo,768B extra destination,256B exact metadata overlap, original success ABI and five new-window readback failures. Not a game candidate or resource grant.'),separators=(',',':')),flush=True)


if __name__=='__main__':main()
