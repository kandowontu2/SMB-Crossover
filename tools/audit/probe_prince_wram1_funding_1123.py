"""Read-only exact6201 WRAM1 funding/ABI census, no candidate or files.

The frozen312-byte prototype stays unchanged. This diagnostic uses only
declared RAM1 CPU canaries and actual FarCallCommon; it grants no allocation,
cold loader, whole-frame integration, spawn or natural pickup qualification.
"""
import json
from pathlib import Path
from unittest.mock import patch

from py65.disassembler import Disassembler
from py65.devices.mpu6502 import MPU
import probe_prince_platform_import_1123 as F
import compose_dkjr_shinobi_1123 as DK
import install_mega_giant_item_semantics_1123 as Mega

H,W,N=F.H,F.W,F.N
PIN='6201e3b6680659fc1b1fab4e09125f9dc05e3b9e2b9a9beebcb656ef1bc2f36f'
FROZEN='b40bc74e3b2659f5fcd10d7e8fb570d16140b7bb76a9566c5c071b26faf58956'


def binding(raw):
    assert H(raw)==PIN and H(Path(F.__file__).read_bytes())==FROZEN
    parent=DK.recover_parent(Mega.recover_parent(raw))
    assert H(parent)==F.Q.PIN
    proof=F.Q.authenticate(parent)
    assert F.Q.P.Packet.extract(raw)==F.Q.P.Packet.extract(parent)
    b=dict(W.Symbols.bundle(),raw=raw)
    for name in ('FarCallCommon','PositionPlayerOnVPlat','PlayerCtrlRoutine'):
        at=W.location(b,name)
        assert raw[at:at+64]==parent[at:at+64]
    return proof


def rows(raw):
    _,parts,lengths=F.Q.P.Packet.extract(raw)
    memory=bytearray(65536)
    memory[0xa000:0xa000+len(parts[0])]=parts[0]
    memory[0xc800:0xc800+len(parts[1])]=parts[1]
    decoder=Disassembler(MPU(memory=memory))
    result=[]
    for name,start,end in (('fallback',0xd6d1,0xd756),('action',0xa6fc,0xa71b),
                           ('logical',0xbd82,0xbda2),('point67',0xb310,0xb353)):
        pc=start;calls=[];code=[]
        while pc<end:
            size,op=decoder.instruction_at(pc)
            if op.startswith(('JSR','JMP')):calls.append([hex(pc),op])
            code.append((pc,size,op))
            pc+=size
        assert pc==end,(name,hex(pc),hex(end))
        result.append(dict(name=name,start=start,end=end,bytes=end-start,
                           SHA256=H(memory[start:end]),calls=calls,
                           code=code))
    return parts,lengths,result


def call(m,pc,*,a=1,x=71,y=109,p=0x31):
    cpu=N.NesMPU(memory=m,pc=pc)
    cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp=a,x,y,p,224
    cpu.stPushWord(0x5aff)
    seen=[]
    for _ in range(10000):
        if cpu.pc==0x5b00:break
        if cpu.pc in(0xa000,0xa020,0xa040,0xb3d1,0xc312):
            seen.append([hex(cpu.pc),tuple(m.rawtags),cpu.sp])
        assert m[cpu.pc]!=0,('Actual farcall BRK',hex(cpu.pc),m.rawtags)
        cpu.step()
    else:raise AssertionError(('Actual farcall bound',hex(cpu.pc)))
    assert cpu.sp==224
    return dict(regs=[cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp],cycles=cpu.processorCycles,seen=seen)


def farcall_matrix(raw):
    def auth(image):assert image==raw;return binding(raw)
    cold=F.Q.P.clone(F.Q.P.cold,dict(authenticate=auth))
    model=cold(raw)
    for _ in range(12):model.controller_pad=0;F.Q.Engine.Frames.frame(model,cold=True)
    assert model.ram[2][0x6cf]==5
    smc=W.address(model.bundle,'FarCallCommon')
    safecall=W.address(model.bundle,'SafecallA_SMC')+1
    target=W.address(model.bundle,'FarcallJmpTarget_SMC')+1
    # Actual source C312 is in raw2, which remains mapped during a raw1 call.
    leaves={0xa000:bytes.fromhex('adcfc660'),0xa020:bytes.fromhex('2012c3ad84c060')}
    # Nested raw1 -> real FarCallCommon -> raw3 B3D1 -> raw1 -> outer raw3.
    nested=(bytes((0xa9,85,0x8d,safecall&255,safecall>>8,
                   0xa9,0xd1,0x8d,target&255,target>>8,
                   0xa9,0xb3,0x8d,(target+1)&255,(target+1)>>8,
                   0xa9,3,0x20,smc&255,smc>>8,0x60)))
    leaves[0xa040]=nested
    result=[]
    for entry,code in leaves.items():
        for flags in(0x31,0x71,0xf1,0x30):
            m=N.fork(model)
            for pc,body in leaves.items():m.ram[1][pc-0xa000:pc-0xa000+len(body)]=body
            m.raw_page(1,3);m.raw_page(2,2);N.put(m,CurrentBank=3,CurrentBankC=2)
            m[safecall]=85;m[target]=entry&255;m[target+1]=entry>>8
            before=tuple(bytes(m.ram[b])for b in(2,3))
            foreground=bytes(m[0x15a:0x17b]);zp=bytes(m[3:11])
            q=call(m,smc,p=flags)
            assert m.rawtags[1:3]==[3,2] and N.get(m,'CurrentBank')==3 and N.get(m,'CurrentBankC')==2
            assert tuple(bytes(m.ram[b])for b in(2,3))==before
            assert bytes(m[3:11])==zp and q['regs'][1:3]==[71,109]
            expected={0xa000:5,0xa020:208,0xa040:0}[entry]
            assert q['regs'][0]==expected,(hex(entry),q)
            q.update(entry=hex(entry),input_P=flags,
                     changed_foreground_offsets=[hex(0x15a+i)for i,(a,b)in enumerate(zip(foreground,m[0x15a:0x17b]))if a!=b])
            result.append(q)
    return result


def main():
    raw=F.Q.P.G.ROM.read_bytes();proof=binding(raw)
    parts,lengths,extents=rows(raw)
    oldcode,lab=F.assemble(F.ASM,F.symbols(raw));assert H(oldcode)==F.CODE_SHA
    packet=F.Q.P.Packet
    head,_,_=packet.extract(raw)
    spare=len(packet.PAGES)*1024-len(head)-sum(lengths)
    assert spare==579
    # Size-only relocation envelope: discard original BDE2 call/branch from
    # fallback, retain its complete body and all direct RAM3 dependencies.
    blobs=[oldcode,parts[1][0xd6d1-0xc800+5:0xd756-0xc800],
           parts[0][0x6fc:0x71b],parts[0][0x1d82:0x1da2],parts[0][0x1310:0x1353]]
    packed=packet.encode(b''.join(blobs))
    assert packet.decode(packed,sum(map(len,blobs)))==b''.join(blobs)
    summary=dict(ROM=PIN,frozen_prototype=FROZEN,packet_spare=spare,
                 code_and_legacy_raw_bytes=sum(map(len,blobs)),
                 size_only_packed_bytes=len(packed),extra_loader_and_gateways_not_included=True,
                 extents=[{k:v for k,v in row.items()if k!='code'}for row in extents],
                 binding=proof,outputs=0)
    print('PRINCE_WRAM1_CENSUS '+json.dumps(summary,separators=(',',':')),flush=True)
    def deny(*a,**k):raise AssertionError('Funding diagnostic attempted output/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        calls=farcall_matrix(raw)
    report=dict(passed=True,ROM=PIN,real_FarCallCommon_cases=len(calls),calls=calls,
                RAM2_RAM3_ZP_and_published_maps_preserved=True,
                source_files_edited=1,outputs=0,Mesen=False,
                candidate_or_cold_loader_or_allocation_claim=False)
    digest=H(json.dumps(report,sort_keys=True,separators=(',',':')).encode())
    print('PRINCE_WRAM1_ABI '+json.dumps(dict(report,SHA256=digest),separators=(',',':')),flush=True)


if __name__=='__main__':main()
