"""Recover/test the donor injury initializer; external animator calls are isolated.

This is a source component, not a playable ROM or native damage proof.
"""
from pathlib import Path
import hashlib, json, re, subprocess, sys
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler
import recover_shinobi_component_1101_v2 as S

R = Path(__file__).resolve().parents[2]
OUT = R/'build/shinobi-injury-1101-v3'


def main():
    raw = S.ROM.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == S.EXPECTED
    original = S.original_memory(raw)
    d = Disassembler(original)
    lines = ['; Original Tengen Shinobi injury entry and motion script.',
             '; Requires original animator/interpreter leaves and injury pose 6.',
             '.export ShInjuryScript', '.segment "SHINOBI_KERNEL"']
    pc = 0xda1b
    while pc < 0xda5e:
        n, text = d.instruction_at(pc)
        mn, mode = original.disassemble[original.memory[pc]]
        if mode == 'rel':
            target = pc+2+((original.memory[pc+1]+128)%256-128)
            text = mn+' Sh_'+f'{target:04X}'
        elif mn == 'JSR':
            text = 'JSR Sh_'+f'{original.WordAt(pc+1):04X}'
        elif mode == 'abx':
            text = re.sub(r'\$([0-9a-f]+)', r'ShState+$\1', text)
        elif pc == 0xda45:
            text = 'LDA #<ShInjuryScript'
        elif pc == 0xda4a:
            text = 'LDA #>ShInjuryScript'
        lines.append(f'Sh_{pc:04X}: {text}')
        pc += n
    assert pc == 0xda5e
    script = bytes(original.memory[0xda5e:0xda78])
    assert script[-1] == 0x8b
    lines += ['ShInjuryScript: .byte '+','.join(f'${v:02x}' for v in script)]
    source = '\n'.join(lines)+'\n'
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/'injury.inc').write_text(source)
    (OUT/'test.s').write_text('.setcpu "6502"\nShState=$c000\nSh_83AB=$b000\nSh_8327=$b001\nSh_8086=$b002\n.include "injury.inc"\n')
    (OUT/'test.cfg').write_text('MEMORY { M:start=$a000,size=$1000,file=%O; }\nSEGMENTS { SHINOBI_KERNEL:load=M,type=ro; }\n')
    cc = R/'tools/Windows/cc65/bin'
    subprocess.run([str(cc/'ca65.exe'),str(OUT/'test.s'),'-o',str(OUT/'test.o')],check=True)
    subprocess.run([str(cc/'ld65.exe'),'-C',str(OUT/'test.cfg'),str(OUT/'test.o'),'-o',str(OUT/'test.bin'),'-Ln',str(OUT/'test.lbl')],check=True)
    labels = {name.lstrip('.'):int(a,16) for a,name in re.findall(r'^al (\w+) (\S+)',(OUT/'test.lbl').read_text(),re.M)}
    code = (OUT/'test.bin').read_bytes()
    # Calls are trapped at matching boundaries, not claimed as animator proof.
    def run(m, entry, calls):
        m.pc=entry; m.sp=0xfd; m.memory[0x1fe]=0xfe; m.memory[0x1ff]=0x7f
        trace=[]
        for _ in range(100):
            if m.pc == 0x7fff: return trace
            if m.pc in calls:
                trace.append(calls[m.pc]); m.memory[m.pc]=0x60
            m.step()
        raise AssertionError('initializer did not return')
    count=0
    for facing in range(256):
        a=S.original_memory(raw); b=MPU()
        state=bytes((i*13+facing)%256 for i in range(0x800))
        a.memory[:0x800]=state; b.memory[0xc000:0xc800]=state
        a.memory[0x363]=b.memory[0xc363]=facing
        b.memory[0xa000:0xa000+len(code)]=code
        ta=run(a,0xda1b,{0x83ab:0,0x8327:1,0x8086:2})
        tb=run(b,0xa000,{0xb000:0,0xb001:1,0xb002:2})
        assert ta==tb==[0,1,2]
        assert b.memory[0xc43f]+256*b.memory[0xc44a]==labels['ShInjuryScript']
        b.memory[0xc43f]=0x5e; b.memory[0xc44a]=0xda
        assert a.memory[0x300:0x800]==b.memory[0xc300:0xc800]
        assert (a.a,a.x,a.y,a.p,a.sp)==(b.a,b.x,b.y,b.p,b.sp)
        count+=1
    (OUT/'result.json').write_text(json.dumps(dict(passed=True,cases=count,donor_sha256=S.EXPECTED,
        assembled_bytes=len(code),script_bytes=len(script),scope='Injury initializer relocation; three external animator/interpreter calls trapped. No native gameplay proof.',
        remaining=['Include injury/death graphics','Wire native damage and death','Resolve remaining source callbacks','Controller-only 1-1']),indent=2)+'\n')
    print(json.loads((OUT/'result.json').read_text()))


if __name__ == '__main__': main()

