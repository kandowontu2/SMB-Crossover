"""Compose original directional shapes with resolved-contact 6502 leaves."""
import json, random
from pathlib import Path
import port_sonic_shapes_1102_v17 as S

R=S.R;sha=S.sha;NesMPU=S.NesMPU
O=R/'build/sonic-sms-shape-contacts-1102-v18'

def main():
    O.mkdir(exist_ok=True)
    prior=R/'build/sonic-sms-shapes-1102-v17';q=json.loads((prior/'receipt.json').read_text())
    assert q['passed']
    for path,digest in q['bindings'].items():assert sha(Path(path))==digest,path
    donor=R/'build/sonic-sms-original-1102-v2/out/s1.sms';rom=donor.read_bytes()
    assert sha(donor)==q['original_ROM_SHA256']
    code=(prior/'component.bin').read_bytes()
    labels={line.split()[2].lstrip('.'):int(line.split()[1],16)for line in (prior/'labels.txt').read_text().splitlines()}
    rng=random.Random(110218);cycles=[];cases=4096
    for _ in range(cases):
        actor=[rng.randrange(256)for _ in range(26)];actor[24]&=~32
        m=[0]*65536;m[0x8000:0x8000+len(code)]=code
        m[0x70:0x76]=actor[1:7];m[0x20:0x23]=actor[7:10]
        m[0x60:0x63]=actor[10:13];m[0x41:0x43]=actor[13:15];m[0x30]=actor[24]
        expected=actor[:]
        # The world-query seam supplies each axis's original zone flag.
        # X clamping/slide affects the following Y lookup exactly as in donor.
        for axis in [0,1]:
            tile=rng.randrange(47)|rng.choice([0,64,128,192])
            offset,probe,flag=S.original_shape(rom,axis,expected,tile)
            expected[24]&=~(64 if axis==0 else 128)
            expected=S.P.original(rom,expected,axis,offset,probe,flag)
            m[0x82]=tile
            cpu=NesMPU(memory=m,pc=labels['HorizontalTerrain'if axis==0 else'VerticalTerrain']);cpu.sp=224;cpu.p=0x30;cpu.stPushWord(0x5aff)
            for _ in range(220):
                if cpu.pc==0x5b00:break
                cpu.step()
            else:raise AssertionError('Shape/contact composition bound')
            assert m[0x70:0x76]==expected[1:7]and m[0x20:0x23]==expected[7:10]and m[0x60:0x63]==expected[10:13]and m[0x30]==expected[24],(axis,tile,actor,expected,m[0x70:0x76],m[0x20:0x23],m[0x60:0x63],m[0x30])
            assert m[0x41:0x43]==actor[13:15]and cpu.sp==224
            cycles.append(cpu.processorCycles)
    result=dict(passed=True,private=True,installed=False,composed_XY_cases=cases,axis_calls=len(cycles),bytes_6502=len(code),axis_cycles=[min(cycles),max(cycles)],original_ROM_SHA256=sha(donor),scope='Compiled6502 directional lookup and contact leaves, sequential X then Y, versus actual donor lookup data plus original contact instructions. Caller supplies each original tile flag; bit5 collision-bypass dispatcher is outside this seam. Position fractions, cross-axis slides, support flags and signed velocities match. Full world queries, Main, native ABI/render/audio and character admission remain incomplete.',bindings={str(p):sha(p)for p in [Path(__file__),Path(S.__file__),Path(S.P.__file__),prior/'receipt.json',prior/'component.bin',prior/'labels.txt']})
    (O/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

if __name__=='__main__':main()
