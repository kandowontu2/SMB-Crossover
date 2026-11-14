"""Actual native IRQ/busy-NMI cuts of proposed body funding, CPU RAM only."""
from collections import Counter
from hashlib import sha256
import json

import check_dkjr_oneway_components_1114 as K
import check_dkjr_retire_lease_1113 as Lease

F,G=K.F,K.G
Q,P,H,N,W,L,C=K.Q,K.P,K.H,K.N,K.W,K.L,K.C


def main():
    parent,raw=F.load_inputs();proposal=K.M.fragments(raw,include_components=True)
    comp=proposal['_components'];start,end=comp['body_start'],comp['body_end']-7
    e73=F.T.Old.reverse(parent)
    _,seed=H.cold(e73,e73[P.B.COOKIE_AT:P.B.COOKIE_AT+16])
    seed=Q.mounted(seed,raw);K.overlay(seed,proposal['fragments'])
    N.put(seed,NmiDisable=255)
    seed.ram[2][0x8fe]=2;seed[0x6de]=32
    for i in range(4):
        at=0x210+8*i;y=120+8*(i//2);tile=2*i;x=40+8*(i&1)
        seed.ram[2][at:at+8]=bytes((y,tile,0x20,x,y+8,tile+1,0x20,x))
    contexts=[('ordinary',[]),('anchor-not-ready',[(0xc8fe,0)]),
        ('misaligned-OAM',[(0x6de,33)]),('full-OAM',[(0x6de,240)]),
        ('hidden-y',[(0xc210,240)]),('bad-pair-y',[(0xc214,129)]),
        ('odd-tile',[(0xc211,3)]),('tile-range',[(0xc211,88)]),
        ('bad-pair-tile',[(0xc215,3)]),('vertical-flip',[(0xc212,128)]),
        ('bad-pair-attr',[(0xc216,0)]),('bad-pair-x',[(0xc217,41)]),
        ('rotation',[(0x6c0b,1),(0x6c08,17)])]
    points={};reference={};body_writes=set();reads=set();active=False;cpu_now=None
    Base=type(seed)
    class Bus(Base):
        def __getitem__(self,at):
            if active and isinstance(at,int):reads.add(at)
            return super().__getitem__(at)
        def __setitem__(self,at,value):
            if active and isinstance(at,int):body_writes.add(at)
            return super().__setitem__(at,value)
    seed.__class__=Bus
    def run(name,changes,p,cut=None):
        nonlocal active,cpu_now
        m=L.clone(seed)
        m.raw_page(1,3);m.raw_page(2,2)
        for at,value in changes:m[at]=value
        hit=False;minimum=255;isr_changes=set();live_proved=False
        def watch(memory,cpu):
            nonlocal active,cpu_now,hit,minimum,isr_changes,live_proved
            cpu_now=cpu;active=True
            if start<=cpu.pc<end:
                token=(cpu.pc,cpu.p&4)
                points.setdefault(token,(name,changes,p))
                if cut and not hit and token==cut[1]:
                    active=False
                    before=bytes(memory[:0x10000])
                    live=bytes(memory[0x101+cpu.sp:0x200])
                    minimum,_=Lease.inject_checked(cpu,cut[0])
                    assert bytes(memory[0x101+cpu.sp:0x200])==live,('ISR live stack',cut)
                    live_proved=True;hit=True
                    isr_changes={at for at in range(0x10000)if memory[at]!=before[at]}
                    reads.clear()
                    active=True
        c=H.call(m,start,p=p,observe=watch)
        active=False
        assert hit==(cut is not None)
        return m,c,minimum,isr_changes,live_proved
    # Actual body paths enumerate every proposed instruction, including the
    # saved-P LSR/ROL window, before cuts are replayed from identical fixtures.
    for name,changes in contexts:
        for p in(0x21,0x61):
            m,c,*_=run(name,changes,p)
            reference[(name,p)]=(m,c)
    expected_writes=set(body_writes);emitted=K.M.A(
        '.segment "BODY"\n tsx\n lsr $0104,x\n lda $c8fa\n lsr\n rol $0104,x\n',
        dict(BODY=(0xa000,32)))['images']['BODY']
    epilogue=bytes(comp['new_body']).index(emitted)+start
    assert epilogue in{pc for pc,_ in points}
    counts=Counter();minimum=255;differences=Counter();live_checks=0
    for index,(point,(name,changes,p))in enumerate(list(points.items())):
        for kind in('IRQ','lagNMI'):
            if kind=='IRQ'and point[1]:continue
            reads.clear();body_writes.clear()
            m,c,low,changed,live=run(name,changes,p,(kind,point))
            ref,rc=reference[(name,p)]
            assert(c.a,c.x,c.y,c.p,c.sp,c.pc)==(rc.a,rc.x,rc.y,rc.p,rc.sp,rc.pc),(kind,point,'return ABI')
            assert tuple(map(bytes,m.ram))==tuple(map(bytes,ref.ram)),(kind,point,'private RAM')
            assert m.rawtags==ref.rawtags and bytes(m[0x15a:0x17b])==bytes(ref[0x15a:0x17b])
            assert bytes(m[0x200:0x300])==bytes(ref[0x200:0x300]),(kind,point,'native OAM')
            own={at for at in expected_writes if not 0x100<=at<0x200}
            assert all(m[at]==ref[at]for at in own),(kind,point,'body output')
            # The ISR may advance native audio. No subsequent body read can
            # consume a changed byte, and every body output is exact above.
            unknown={at for at in changed if not 0x100<=at<0x200 and at in reads}
            assert not unknown,(kind,point,'body consumes ISR changes',sorted(unknown))
            for at in changed:
                if not 0x100<=at<0x200:differences[hex(at)]+=1
            minimum=min(minimum,low);counts[kind]+=1;live_checks+=int(live)
        if index%40==0:print('DKJR_BODY_IRQ_PROGRESS '+json.dumps(dict(done=index+1,total=len(points))),flush=True)
    assert counts['IRQ']and counts['lagNMI']and live_checks==sum(counts.values())
    print('DKJR_BODY_FUNDING_VECTORS '+json.dumps(dict(passed=True,parent_SHA256=F.T.PIN,
        cut_points=len(points),cuts=dict(counts),minimum_ISR_SP=minimum,
        incoming_V1_context=True,saved_P_RMW_epilogue_entry=epilogue,
        live_stack_exact_at_every_RTI=True,body_outputs_ABI_private_RAM_OAM_SMC_maps_exact=True,
        ISR_changed_native_bytes_not_read_by_body=dict(differences),outputs_written=0,ROM_composed=False,
        scope='Declared body fixtures with actual current native IRQ and busy-NMI; proposed code overlaid only in CPU RAM after cold. Not complete Main/cold/raster/native qualification.'),separators=(',',':')),flush=True)


if __name__=='__main__':main()
