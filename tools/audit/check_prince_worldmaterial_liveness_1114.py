"""Current decoded caller-liveness proof for the specialized private readers."""
from hashlib import sha256
import json
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler
import prince_cold_packet_1111 as Packet
import replay_prince_pipe_usability_1114 as F


def run(raw):
    assert sha256(raw).hexdigest()==F.PIN
    _,chunks,_=Packet.extract(raw);rt=chunks[0]
    tail=bytes.fromhex('ae9dc0ac9ec028ad9fc060')
    at=rt.index(tail,0x1de2);end=0xa000+at+len(tail)
    mem=[0]*65536;mem[0xa000:0xa000+len(rt)]=rt
    d=Disassembler(MPU(memory=mem));ins={};pc=0xbde2
    while pc<end:
        size,text=d.instruction_at(pc);assert text[:3]!='???',(hex(pc),text)
        ins[pc]=(size,text);pc+=size
    assert pc==end
    x_ops=[(pc,text)for pc,(_,text)in ins.items()if text.startswith(('STX','TXA','TXS','INX','DEX','CPX'))or',X'in text]
    assert x_ops==[(0xbde6,'STX $c09d')],x_ops
    v_reads=[(pc,text)for pc,(_,text)in ins.items()if text.startswith(('BVC','BVS'))]
    assert not v_reads
    calls=[(pc,text)for pc,(_,text)in ins.items()if text.startswith('JSR')]
    assert all(pc<0xbe8f or text in('JSR $a49a','JSR $b310')for pc,text in calls),calls
    a_defs={};a_users={'ADC','SBC','AND','ORA','EOR','CMP','ASL','LSR','ROL','ROR','STA','TAX','TAY','PHA','BIT'}
    for call in(0xbe8f,0xbecb,0xbef5):
        todo=[call+3];seen=set();defs=[]
        while todo:
            pc=todo.pop()
            if pc in seen:continue
            seen.add(pc);size,text=ins[pc];op=text[:3]
            assert op not in a_users,(hex(call),hex(pc),text)
            if op=='LDA':defs.append(pc);continue
            assert op not in('JSR','RTS','JMP'),(hex(call),hex(pc),text)
            if op.startswith('B')and op!='BIT':
                todo.append(int(text.split('$')[1],16))
            todo.append(pc+size)
        a_defs[hex(call)]=[hex(pc)for pc in sorted(set(defs))]
    return dict(ROM_SHA256=F.PIN,decoded_runtime_SHA256=sha256(rt).hexdigest(),
        WorldMaterial_half_open=[hex(0xbde2),hex(end)],
        entry_bytes=rt[0x1de2:0x1df0].hex(),saved_XY_P_restore_PC=hex(0xa000+at),
        restore_bytes=tail.hex(),first_A_reloads_on_all_C_paths=a_defs,
        X_consumers_in_outer_function=[dict(PC=hex(pc),instruction=text)for pc,text in x_ops],
        V_consumers_before_restore=0,
        subsequent_calls=[dict(PC=hex(pc),instruction=text)for pc,text in calls if pc>=0xbe8f],
        contract='Specialized helper may clobber A/X/V/N/Z; C feeds the original branch, A is reloaded, outer savedX/Y/P are restored.',
        qualification='Decoded caller/source instruction proof only; hardware interrupts and code allocation remain separate.',
        outputs=0,Mesen=False)


if __name__=='__main__':print(json.dumps(run(F.ROM.read_bytes()),separators=(',',':')),flush=True)
