"""Apply the actual native logical->physical OAM rotation contract."""
from pathlib import Path
import json,re,sys
from py65.devices.mpu6502 import MPU
sys.path.insert(0,str(Path(__file__).resolve().parent))
import prepare_mini_mario_chr_override_1103_v39 as C
import check_mini_mario_step_1103_v18 as T
W,R,O=C.W,C.R,C.O
def main():
 src=(O/'mini-host-v39.s').read_text();src='GuestOamRotationActive=$6c0b\nRgOamRotation=$6c08\n'+src
 a=src.index('MiniNativeDraw:\n');b=src.index('MiniNativeDrawEnd:\n',a);part=src[a:b]
 needle=' txa\n and #3\n bne Render_Done\n';assert part.count(needle)==1
 part=part.replace(needle,needle+''' lda GuestOamRotationActive
 beq MiniNativePhysicalReady
 txa
 clc
 adc RgOamRotation
 tax
MiniNativePhysicalReady:
''')
 needle=' txa\n clc\n adc #4\n sta CurrentOAMOffset';assert part.count(needle)==1;part=part.replace(needle,' lda CurrentOAMOffset\n clc\n adc #4\n sta CurrentOAMOffset');src=src[:a]+part+src[b:]
 data,L=C.assemble(O/'mini-host-v42',src,0xa000,0x2000);assert len(data)<=5120
 # All64native aligned rotations, each63legal logical slots, both inactive
 # and active branches. Only the exact physical4-byte owned slot may change.
 cases=0;S=C.H.symbols()
 for active in[0,1]:
  for rotation in range(0,256,4):
   for logical in range(0,252,4):
    m=MPU();m.memory[0xa000:0xa000+len(data)]=data;m.memory[0x6c0b]=active;m.memory[0x6c08]=rotation;m.memory[S['CurrentOAMOffset']]=logical;m.memory[0xc310]=0;m.memory[0xc311:0xc315]=[120,0,192,0]
    before=[(i*17+33)&255 for i in range(256)];m.memory[0x200:0x300]=before;m.a=0x51;m.x=0x52;m.y=0x53;m.p=0x64;T.call(m,L['MiniNativeDraw'])
    physical=(logical+(rotation if active else 0))&255;expected=before[:];expected[physical:physical+4]=[191,1,0,120]
    assert m.memory[0x200:0x300]==expected,(active,rotation,logical,physical)
    assert m.memory[S['CurrentOAMOffset']]==logical+4 and m.memory[0xc315]==1
    assert(m.a,m.x,m.y)==(0x51,0x52,0x53)and m.p&0xcf==0x65&0xcf
    # The next ordinary native sprite's rotated logical slot is disjoint.
    nxt=(logical+4+(rotation if active else 0))&255;assert set(range(physical,physical+4)).isdisjoint(range(nxt,nxt+4))
    cases+=1
 for logical in[1,2,3,249,250,251,252,253,254,255]:
  m=MPU();m.memory[0xa000:0xa000+len(data)]=data;m.memory[S['CurrentOAMOffset']]=logical;m.memory[0xc311:0xc315]=[120,0,192,0];before=list(m.memory[0x200:0x300]);T.call(m,L['MiniNativeDraw']);assert m.memory[0x200:0x300]==before and m.memory[S['CurrentOAMOffset']]==logical
 out=dict(passed=True,bytes=len(data),SHA256=W.sha(data),labels=L,vectors=[int.from_bytes(data[i*3+1:i*3+3],'little')for i in range(38)],all64_rotations_and_logical_slots=cases,invalid_alignment_capacity_rejections=10,other252_OAM_bytes_preserved=True,next_native_rotated_slot_disjoint=True,logical_offset_advance=4,AXYP_restored_except_C1=True,no_new_RAM=True,source_authority='src/metasprite_engine.s::MetaspriteRenderLoop adds RgOamRotation to logical X when GuestOamRotationActive, stores logical offset after unrotation. Mini uses unchanged logicalCurrentOAMOffset+4 after exactrotated4bytewrite.',scope='Only private native rendererOAMphysicaladdress/logicallength bookkeeping changed. No sourcemotion, camera, CHR, sourceposes orpalette changes. Rootnativefullroute acceptance pending.',bindings={p.relative_to(R).as_posix():W.sha(p.read_bytes())for p in[Path(__file__),O/'mini-host-v39.s',O/'mini-host-v39.json',R/'src/metasprite_engine.s']})
 (O/'mini-host-v42.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k]for k in['passed','bytes','SHA256','labels','all64_rotations_and_logical_slots']}))
if __name__=='__main__':main()
