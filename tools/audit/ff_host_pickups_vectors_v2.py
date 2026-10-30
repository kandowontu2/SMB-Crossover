"""Extend the unchanged vector assertions to a genuine two-instruction seam.

BankPRGC immediate expands to LDA/STA-shadow/LDA/STA-hardware. A normal NMI
can restore hardware from the new shadow before that second LDA. The previous
observer accepted only the following STA, missing this exact original site.
No cartridge, source state or expected restored-bank value is normalized.
"""
import ff_ram3_execution_controls_v2 as E
from check_tmnt_render_oa import address
get=E.get;cpu_state=E.cpu_state


def pending_store(m,c,slot,op):
    if bytes(m[c.pc:c.pc+3])==op:return True
    if slot!=2 or m.rawtags[1]!=3:return False
    start=address(m.bundle,'FfGraphicsBank')
    at=address(m.bundle,'CurrentBankC')
    actual=bytes(m[start:start+11])
    expected=bytes([0xa9,0xdd,0x8d,at&255,at>>8,0xa9,0xdd,0x8d,0x16,0x51,0x60])
    return c.pc==start+5 and actual==expected and get(m,'CurrentBankC')==0xdd


def interrupt(m,c,kind):
    b=m.bundle;live_zp=(kind=='IRQ' or get(m,'NmiDisable')!=0);before=(cpu_state(c),m.rawtags[:],get(m,'CurrentBank'),get(m,'CurrentBankC'),
                       bytes(m[0x15a:0x17b]),bytes(m[0x101+c.sp:0x200]),bytes(m[:256]),
                       [bytes(x) for x in m.ram])
    expected=m.rawtags[:]
    for slot,name,op in [(1,'CurrentBank',b'\x8d\x15\x51'),(2,'CurrentBankC',b'\x8d\x16\x51')]:
        if kind=='NMI' and expected[slot]!=get(m,name):
            assert pending_store(m,c,slot,op),('unclassified pending hardware store',hex(c.pc))
            expected[slot]=get(m,name)
    oldcycles=c.processorCycles;low=c.sp
    if kind=='NMI':c.nmi()
    else:
        assert not c.p&c.INTERRUPT
        c.irq()
    for steps in range(100000):
        if cpu_state(c)==before[0]:break
        low=min(low,c.sp)
        assert m[c.pc]!=0,('real ISR BRK',kind,hex(c.pc),m.rawtags)
        c.step()
    else:raise AssertionError(('real ISR did not RTI',kind,cpu_state(c),before[0]))
    assert m.rawtags==expected and [get(m,'CurrentBank'),get(m,'CurrentBankC')]==list(before[2:4])
    assert bytes(m[0x15a:0x17b])==before[4],('all33SMC',kind)
    assert bytes(m[0x101+c.sp:0x200])==before[5],('live page1',kind)
    assert bytes(m[3:5])==before[6][3:5] and bytes(m[9:11])==before[6][9:11],('actual borrowed pairs',kind)
    if live_zp:
        changed=[i for i,(a,z) in enumerate(zip(before[6],m[:256])) if a!=z]
        audio=range(address(b,'XgAudioPtr'),address(b,'XgAudioZeroPageEnd'))
        assert all(kind=='NMI' and i in audio for i in changed),('live foreground ZP',kind,changed)
    assert [bytes(x) for x in m.ram]==before[7],('ISR wrote RAM0..3 payload banks',kind)
    return dict(kind=kind,CPU=c.processorCycles-oldcycles,minimum_SP=low,
                raw_maps=m.rawtags[:],AXYP_SP_SMC33_page1_R0_R1_R6_R7_exact=True)
