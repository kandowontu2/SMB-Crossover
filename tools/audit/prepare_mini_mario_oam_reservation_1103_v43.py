"""Publish one real native player reservation independently of the zero body header."""
from pathlib import Path
import json,sys
from py65.devices.mpu6502 import MPU
sys.path.insert(0,str(Path(__file__).resolve().parent))
import prepare_mini_mario_chr_override_1103_v39 as C
import check_mini_mario_step_1103_v18 as T
W,R,O=C.W,C.R,C.O

def main():
 src=(O/'mini-host-v42.s').read_text();src='SmPose=$6b05\n'+src
 needle=' lda #<ObjectMetasprite\n sta SmPosePtr\n lda #>ObjectMetasprite\n sta SmPosePtr+1'
 replacement=' lda #4\n sta SmPose\n lda #<SmPose\n sta SmPosePtr\n lda #>SmPose\n sta SmPosePtr+1'
 assert src.count(needle)==2;src=src.replace(needle,replacement)
 data,L=C.assemble(O/'mini-host-v43',src,0xa000,0x2000);assert len(data)<=5120
 S=C.H.symbols();native=(R/'src/metasprite_engine.s').read_text()
 a=native.index('  lda CurrentOAMOffset\n  sta RgOamPlayerStart\n::RosterProjectileOamReady:')
 b=native.index('  jmp InitObjectLoop',a);leaf=native[a:b]
 names=['CurrentOAMOffset','RgOamPlayerStart','SmPosePtr','R0','R1']
 fixture='.setcpu "6502"\n.segment "CODE"\n.export NativeReserve\n'+''.join(f'{n}=${S[n]:04x}\n'for n in names)+'NativeReserve:\n'+leaf+' rts\n'
 reserve,N=C.assemble(O/'native-reservation-v43',fixture,0x6000,0x200)
 def cpu():
  m=MPU();m.memory[0xa000:0xa000+len(data)]=data;m.memory[0x6000:0x6000+len(reserve)]=reserve
  m.memory[0xc310]=0;m.memory[0xc311:0xc315]=[120,0,192,0];return m
 cases=0
 for active in[0,1]:
  for rotation in range(0,256,4):
   for logical in range(0,252,4):
    m=cpu();m.memory[0x6c0b]=active;m.memory[0x6c08]=rotation;m.memory[S['CurrentOAMOffset']]=logical
    m.memory[S['ObjectMetasprite']]=99;m.memory[0x6b05:0x6b08]=[0,0,0]
    T.call(m,L['MiniHostGraphics'])
    assert m.memory[S['ObjectMetasprite']]==0 and m.memory[0x6b05:0x6b08]==[4,5,107]
    # Exact genuine reservation saves the player's logical start and advances
    # the enemy cursor by four before any enemy is rendered.
    T.call(m,N['NativeReserve']);assert m.memory[S['RgOamPlayerStart']]==logical
    assert m.memory[S['CurrentOAMOffset']]==logical+4
    body=(logical+(rotation if active else 0))&255
    enemy=(logical+4+(rotation if active else 0))&255
    assert set(range(body,body+4)).isdisjoint(range(enemy,enemy+4))
    before=[(i*17+33)&255 for i in range(256)];m.memory[0x200:0x300]=before
    # Native body pass restores saved logical start after rendering enemies.
    m.memory[S['CurrentOAMOffset']]=m.memory[S['RgOamPlayerStart']]
    m.memory[S['ObjectMetasprite']]=77;m.memory[0x6b05:0x6b08]=[0,0,0]
    m.a=0x51;m.x=0x52;m.y=0x53;m.p=0x64;T.call(m,L['MiniNativeDraw'])
    expected=before[:];expected[body:body+4]=[191,1,0,120]
    assert m.memory[0x200:0x300]==expected and m.memory[S['CurrentOAMOffset']]==logical+4
    assert m.memory[S['ObjectMetasprite']]==0 and m.memory[0x6b05:0x6b08]==[4,5,107]
    assert(m.a,m.x,m.y)==(0x51,0x52,0x53)and m.p&0xcf==0x65&0xcf
    assert m.memory[0xc315]==1;cases+=1
 # Historical zero-header design deterministically reserves no player slot.
 m=cpu();m.memory[S['CurrentOAMOffset']]=0;m.memory[S['ObjectMetasprite']]=0
 m.memory[S['SmPosePtr']]=S['ObjectMetasprite']&255;m.memory[S['SmPosePtr']+1]=S['ObjectMetasprite']>>8
 T.call(m,N['NativeReserve']);assert m.memory[S['CurrentOAMOffset']]==0
 out=dict(passed=True,bytes=len(data),SHA256=W.sha(data),labels=L,vectors=[int.from_bytes(data[i*3+1:i*3+3],'little')for i in range(38)],all64_rotations_and_logical_slots=cases,native_reservation_source_SHA256=W.sha(leaf.encode()),reserved_player_bytes=4,SmPose=0x6b05,SmPosePtr=0x6b06,ObjectMetasprite_header=0,other252_OAM_bytes_preserved=True,next_native_rotated_slot_disjoint=True,logical_offset_advance=4,AXYP_restored_except_C1=True,no_new_RAM=True,retained_zero_header_negative_enemy_cursor=0,scope='Graphics and NativeDraw both publish native SmPose=4 and stable SmPosePtr=&SmPose. Independent ObjectMetasprite header remains0 to bypass legacy native player-bank publishing. Exact source RosterProjectileOamReady reserves four player bytes before enemies; rotated body output uses saved logical start. No source motion, camera, CHR, pose or palette changes. Root native acceptance pending.',bindings={p.relative_to(R).as_posix():W.sha(p.read_bytes())for p in[Path(__file__),O/'mini-host-v42.s',O/'mini-host-v42.json',R/'src/metasprite_engine.s',C.H.BASELABELS]})
 (O/'mini-host-v43.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({k:out[k]for k in['passed','bytes','SHA256','labels','all64_rotations_and_logical_slots']}))
if __name__=='__main__':main()
