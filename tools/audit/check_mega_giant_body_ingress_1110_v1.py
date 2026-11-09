"""Reach the Mega Giant box from the real native player-control callsite."""

import argparse
import hashlib
from itertools import product
import json
from pathlib import Path
import subprocess
import tempfile

from check_mega_giant_geometry_1110_v1 import M, R, ROM, HOST_PIN, SOURCE, DONOR, DONOR_PIN
from check_mega_giant_geometry_1110_v1 import address, bundle, invoke, sha
from prepare_mini_side_alias_1108 import compare_memory


GATE=R/'tools/reference/mega_giant_mario_body_ingress_1110_v1.s'
CALL=0xa147
RETURN=0xa14a
FIXTURE_ADDRESS=0x5b80


def compile_fixture(out):
    with tempfile.TemporaryDirectory(prefix='ingress-',dir=out) as work:
        work=Path(work)
        cfg=work/'ingress.cfg'
        cfg.write_text('MEMORY { CODE:start=$5b80,size=$400,file=%O; } '
                       'SEGMENTS { GIANT_GATE:load=CODE,type=ro; GIANT:load=CODE,type=ro; }\n')
        cc=R/'tools/Windows/cc65/bin'
        for path,name in ((GATE,'gate'),(SOURCE,'body')):
            subprocess.run([cc/'ca65.exe',path,'-o',work/(name+'.o')],check=True)
        binary=work/'ingress.bin'
        subprocess.run([cc/'ld65.exe','-C',cfg,work/'gate.o',work/'body.o','-o',binary],check=True)
        return binary.read_bytes()


def start_native(b):
    m=M.fresh(b)
    M.put(m,CrossoverMenuIndex=0)
    M.invoke(m,'MenuResolveCharacter')
    M.invoke(m,'QueueSelection')
    M.put(m,SavedJoypad1Bits=16,SavedJoypad2Bits=0,CrossoverMenuButtons=0)
    start=M.invoke(m,'CrossoverMenuInput')
    M.invoke(m,'ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    M.invoke(m,'PauseRoutine',a=0)
    for _ in range(600):
        if M.get(m,'OperMode_Task')==3 and M.get(m,'GameEngineSubroutine')==8:
            return m
        M.put(m,SavedJoypadBits=0,SavedJoypad1Bits=0,SavedJoypad2Bits=0,A_B_Buttons=0,
              Left_Right_Buttons=0,Up_Down_Buttons=0,NmiDisable=255)
        M.invoke(m,'GameLoop')
        M.consume(m)
    raise AssertionError('Title did not reach 1-1')


def play(m,donor,code,variant,keys):
    b=m.bundle
    M.put(m,SavedJoypadBits=keys,SavedJoypad1Bits=keys,SavedJoypad2Bits=0,NmiDisable=255)
    cpu=M.NesMPU(memory=m,pc=address(b,'GameLoop'))
    cpu.p,cpu.sp=0x31,252
    cpu.stPushWord(0x5aff)
    observations=[]
    owned_pc=0
    for _ in range(18000):
        pc=cpu.pc
        if pc==0x5b00:
            break
        if m.rawtags[1]==129 and pc==CALL:
            # Private identity is presented at the reached real call. Keep
            # all unimplemented Giant menu/movement/render routes outside it.
            M.put(m,MarioVariant=variant)
        if pc==FIXTURE_ADDRESS:
            owned_pc+=1
        if m.rawtags[1]==129 and pc==RETURN:
            donor[0x3ad]=M.get(m,'Player_Rel_XPos')
            donor[0x3b8]=M.get(m,'Player_Rel_YPos')
            donor[0x3d0]=M.get(m,'Player_OffscreenBits')
            donor[0x499]=1+int(bool(M.get(m,'CrouchingFlag')))
            invoke(donor,0xe29c)
            invoke(donor,0xeb5f)
            got=bytes(m[0x658:0x65c])
            wanted=bytes(donor[0x4ac:0x4b0])
            if code and variant==9:
                assert got==wanted,(keys,list(got),list(wanted))
            observations.append((list(got),list(wanted)))
            M.put(m,MarioVariant=0)
        assert m[pc],(hex(pc),m.rawtags)
        cpu.step()
    else:
        raise AssertionError(('GameLoop did not return',hex(cpu.pc)))
    assert cpu.sp==252 and len(observations)==1
    assert owned_pc==bool(code)
    return observations[0]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    out=args.output.resolve()
    assert sha(ROM)==HOST_PIN and sha(DONOR)==DONOR_PIN
    raw=ROM.read_bytes()
    old=bundle(raw)
    patch_at=16+8192+(CALL&8191)
    assert raw[patch_at:patch_at+3]==bytes.fromhex('2069b9')
    patched=raw[:patch_at]+bytes.fromhex('20805b')+raw[patch_at+3:]
    code=compile_fixture(out)
    seeds=[start_native(b) for b in (old,bundle(patched))]
    for seed in seeds:
        seed[FIXTURE_ADDRESS:FIXTURE_ADDRESS+len(code)]=code
    donor=bytearray(65536)
    donor[0x8000:]=DONOR.read_bytes()[16:32784]
    measurements=[]
    for variant,keys in product((0,9),(0,1,2,4,128,129)):
        pair=[M.fork(m) for m in seeds]
        vanilla=play(pair[0],donor,b'',variant,keys)
        giant=play(pair[1],donor,code,variant,keys)
        if variant==0:
            assert vanilla==giant
            compare_memory(*pair)
        else:
            assert vanilla[0]!=giant[0]
        measurements.append(dict(variant=variant,keys=keys,parent_box=vanilla[0],fixture_box=giant[0]))
    q=dict(passed=True,source_CPU_only=True,ROM_written=False,host_SHA256=HOST_PIN,donor_SHA256=DONOR_PIN,
           private_CPU_fixture_address=FIXTURE_ADDRESS,code_bytes=len(code),code_SHA256=hashlib.sha256(code).hexdigest(),
           call_bank=1,call_PC=CALL,call_preimage='2069b9',cases=measurements,
           scope='Native title and parser, then real native GameLoop. At its existing box callsite only, present a private Mario variant9 fixture and replace just its body box. Real donor geometry is consumed by the remainder of the frame. This is not a persistent executable lease, a menu route, or an original injury/terrain implementation.',
           bindings={str(path):sha(path) for path in (Path(__file__),SOURCE,GATE,ROM,DONOR)})
    (out/'body-ingress-proof.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps(dict(passed=True,cases=len(measurements),code_bytes=len(code),first=measurements[6])))


if __name__=='__main__':
    main()
