"""Assemble and execute the real cache decoder against all four data profiles."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
import traceback

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R/'tools'), str(R/'tools/audit')]
from verify_native_relocation import NesMPU
from private_build_outputs_v1 import validate
from pack_smb2j_campaign_data_1031_v2 import encode, decode

O = R/'build/smb2j-cache-decoder-1031-v1'
P = R/'build/smb2j-campaign-data-1031-v2'
SOURCE = R/'tools/reference/smb2j_cache_decoder_1031_v1.inc'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


class Memory(list):
    def __init__(self, code, packed, locked=False, corrupt=None):
        super().__init__([0]*65536)
        self[0xc738:0xc738+len(code)] = code
        self.packed, self.reads, self.stores = packed, 0, []
        self.locked, self.corrupt = locked, corrupt
        self[0xa000:0xc000] = [(i*19+71)&255 for i in range(8192)]

    def __getitem__(self, key):
        if key == 0x2007:
            assert self.reads < len(self.packed), 'Decoder read beyond exact packed input'
            byte = self.packed[self.reads]
            self.reads += 1
            return byte
        value = super().__getitem__(key)
        return value ^ 1 if key == self.corrupt else value

    def __setitem__(self, key, value):
        if isinstance(key, int) and 0xa000 <= key < 0xc000:
            self.stores.append((key,value))
            if self.locked:
                return
        super().__setitem__(key,value)


def run(code, packed, flags=0x30, locked=False, corrupt=None):
    m = Memory(code, packed, locked, corrupt)
    c = NesMPU(memory=m)
    c.pc, c.sp, c.p, c.a, c.x, c.y = 0xc738, 224, flags, 79, 83, 91
    m[0x1e0], m[0x1df] = 0x7f, 0xff
    c.sp = 222
    low = c.sp
    for steps in range(500000):
        if c.pc == 0x8000:
            assert c.sp == 224
            return m, c, steps, low
        c.step()
        low = min(low,c.sp)
    raise AssertionError(('Decoder instruction bound',hex(c.pc)))


def main():
    assert not O.exists()
    O.mkdir()
    stage = json.loads((P/'data-stage.json').read_text())
    for name, expected in stage['bindings'].items():
        assert sha(name) == expected, name
    src = '.export J2DecodeCache\nPPUDATA=$2007\n' + ''.join(f'R{i}=${i+3:02x}\n' for i in range(8)) + '.segment "CODE"\n' + SOURCE.read_text()
    (O/'decoder.s').write_text(src,encoding='utf-8',newline='\n')
    (O/'decoder.cfg').write_text('MEMORY { M:start=$c738,size=$09d0,type=ro,file=%O; }\nSEGMENTS { CODE:load=M,type=ro; }\n')
    commands = [
        [str(R/'tools/Windows/cc65/bin/ca65.exe'),'-g',str(O/'decoder.s'),'-o',str(O/'decoder.o')],
        [str(R/'tools/Windows/cc65/bin/ld65.exe'),'-C',str(O/'decoder.cfg'),'-o',str(O/'decoder.bin'),'-Ln',str(O/'decoder.lbl'),str(O/'decoder.o')],
    ]
    for i,command in enumerate(commands):
        guard = validate(command,O,cwd=R)
        result = subprocess.run(command,cwd=R,capture_output=True,text=True)
        (O/f'build-{i}.json').write_text(json.dumps(dict(command=command,output_guard=guard,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr),indent=2)+'\n')
        assert result.returncode == 0,result.stderr
    code = (O/'decoder.bin').read_bytes()
    q = dict(passed=False,source_CPU=True,native=False,installed=False,decoder_bytes=len(code))
    try:
        rows=[]
        for profile in stage['profiles']:
            expected=(P/(profile['name']+'.cache.bin')).read_bytes()
            packed=(P/(profile['name']+'.lzss')).read_bytes()
            for flags in [0x30,0xff]:
                m,c,steps,low=run(code,packed,flags)
                assert c.p&1 and bytes(m[0xa000:0xc000])==expected
                assert len(m.stores)==8192 and m.reads==len(packed)
                assert min(a for a,v in m.stores)==0xa000 and max(a for a,v in m.stores)==0xbfff
                rows.append(dict(profile=profile['name'],flags=flags,CPU=c.processorCycles,instructions=steps,minimum_SP=low,packed_reads=m.reads,verified_stores=len(m.stores)))
        expected=(P/'worlds1-4.cache.bin').read_bytes()
        packed=(P/'worlds1-4.lzss').read_bytes()
        for locked,corrupt in [(True,None),(False,0xa123),(False,0xbfff)]:
            m,c,steps,low=run(code,packed,locked=locked,corrupt=corrupt)
            assert not c.p&1
        # Every possible byte and overlapping long distances exercise the same
        # assembled code, not a Python-only codec comparison.
        patterns=[bytes([v])*8192 for v in [0,255,37]]
        patterns += [bytes(range(256))*32, bytes((i*23+i//17)&255 for i in range(8192))]
        for expected in patterns:
            packed=encode(expected)
            assert decode(packed,8192)==expected
            m,c,steps,low=run(code,packed)
            assert c.p&1 and bytes(m[0xa000:0xc000])==expected and len(m.stores)==8192
        q.update(passed=True,profiles=rows,readback_failure_cases=3,synthetic_byte_and_overlap_cases=len(patterns),
                 imported_scratch_addresses=list(range(3,11)),
                 scope='Standalone actual6502 leaf decoder. No mapper wrapper, authentication, RAM4/header expansion or host campaign is installed.')
    except Exception as error:
        q.update(error=repr(error),traceback=traceback.format_exc())
    refs=[Path(__file__),SOURCE,P/'data-stage.json',O/'decoder.s',O/'decoder.cfg',O/'decoder.bin',O/'decoder.lbl',*O.glob('build-*.json'),Path(sys.modules[NesMPU.__module__].__file__)]
    q['bindings']={str(p.resolve()):sha(p) for p in refs}
    (O/'controls.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in q.items() if k not in ['bindings','traceback','profiles']}))
    assert q['passed'],q.get('error')


if __name__ == '__main__':
    main()
