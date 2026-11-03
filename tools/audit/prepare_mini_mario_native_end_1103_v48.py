"""Private Mini native end/lives drawing repair over exact installed 8daf."""
from pathlib import Path
import json,sys
from py65.devices.mpu6502 import MPU
sys.path.insert(0,str(Path(__file__).resolve().parent))
import prepare_mini_mario_chr_override_1103_v39 as C
import check_mini_mario_step_1103_v18 as T
W,R=C.W,C.R
O=R/'build/mini-mario-native-end-1103-v48'
PRIOR=R/'build/mini-mario-host-1103-v22'
ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PIN='8daf59cc958e2a3a645882ea53c6bd75e9a7c641793054f8ce534358f369a7d7'
def main():
 O.mkdir(exist_ok=True);S=C.H.symbols();raw=ROM.read_bytes();assert W.sha(raw)==PIN
 old=(PRIOR/'mini-host-v43.bin').read_bytes();prior=json.loads((PRIOR/'mini-host-v43.json').read_text())
 assert W.sha(old)==prior['SHA256']=='6bf222a7083eb278058547a9e4ddb8d1085fdeb611caa73ac05e19e3d568c30e'
 assert raw[1048592+962*1024:1048592+962*1024+len(old)]==old
 src=(PRIOR/'mini-host-v43.s').read_text();src='.export MiniHostNativeCanvas,MiniHostFilterSolid,MiniHostPortrait\n'+src
 needle='MiniHostDraw:\n jsr MiniHostGraphics\n jsr MiniHostPixelX'
 assert src.count(needle)==1
 src=src.replace(needle,'''MiniHostDraw:
 jsr MiniHostGraphics
 lda GameEngineSubroutine
 cmp #8
 beq MiniHostDrawSource
 jsr MiniHostNativeCanvas
 jmp MiniNativeDraw
MiniHostDrawSource:
 jsr MiniHostPixelX''')
 a=src.index('MiniHostPortrait:\n');b=src.index('MiniHostBox:\n',a)
 src=src[:a]+'''MiniHostPortrait:
 lda #0
 sta MiniPose
 jsr MiniHostGraphics
 jsr MiniHostNativeCanvas
 jmp MiniNativeDraw
MiniHostNativeCanvas:
 sec
 lda Player_X_Position
 sbc ScreenLeft_X_Pos
 sta MiniRenderX
 lda Player_PageLoc
 sbc ScreenLeft_PageLoc
 sta MiniRenderX+1
 clc
 lda Player_Y_Position
 adc #16
 sta MiniRenderY
 lda Player_Y_HighPos
 adc #$FF
 sta MiniRenderY+1
 rts

'''+src[b:]
 needle='MiniHostFilterSolid:\n php\n';assert src.count(needle)==1
 src=src.replace(needle,needle+' ldx GameEngineSubroutine\n cpx #8\n bne @keep\n')
 data,L=C.assemble(O/'mini-host-v48',src,0xa000,0x2000);assert len(data)<=5120
 attrs=(R/'build/mini-mario-native-tile-1103-v13/native-attributes.bin').read_bytes()
 def mem(code=data):
  m=MPU();m.memory[0x8000:0xa000]=raw[16+126*8192:16+127*8192];m.memory[0xe000:0x10000]=raw[16+127*8192:16+128*8192];m.memory[0xa000:0xa000+len(code)]=code;m.memory[0xd300:0xd400]=attrs
  for n,v in dict(Player_X_Position=47,Player_Y_Position=176,Player_Y_HighPos=1,GameEngineSubroutine=8).items():m.memory[S[n]]=v
  return m
 getters=0
 for engine in[4,5,7,8]:
  for pc,entry,y in[(S['BlockBufferColli_Side'],'MiniHostSide',17),(S['BlockBufferColli_Head'],'MiniHostHead',14)]:
   for tile in[0,0x54,0xc2,0x24,0x25,0x26]:
    a,b=mem(),mem()
    for m in[a,b]:
     m.memory[S['GameEngineSubroutine']]=engine;m.memory[0x300:0x4a0]=[tile]*416;m.memory[3:5]=[0x55,0xaa];m.a=99;m.x=11;m.y=y;m.p=0x24
    T.call(a,pc);T.call(b,L[entry]);expected=tile if engine!=8 or tile in[0xc2,0xc3]or attrs[tile]&3!=1 else 0
    assert b.a==expected and b.memory[3:11]==a.memory[3:11]
    assert(b.x,b.y)==(a.x,a.y)==(0,y)and b.p&0x41==a.p&0x41
    assert bool(b.p&2)==(expected==0)and bool(b.p&128)==bool(expected&128);getters+=1
 # A bounded legal castle-wall fixture. Use exact installed native getter,
 # ImpedePlayerMove and ChkStop instructions. No simulated full-stage claim.
 wall=[]
 for kernel,labels,name in[(old,prior['labels'],'retained43negative'),(data,L,'repaired48')]:
  m=mem(kernel);m.memory[S['GameEngineSubroutine']]=5;m.memory[0x300:0x4a0]=[0x54]*416;m.y=17
  T.call(m,labels['MiniHostSide']);tile=m.a;m.memory[S['Player_CollisionBits']]=255;m.memory[S['Player_X_Speed']]=24;m.memory[S['R0']]=1
  if tile:T.call(m,S['ImpedePlayerMove'])
  collision=m.memory[S['Player_CollisionBits']]
  m.memory[0xa000:0xc000]=raw[16+8192:16+2*8192]
  T.call(m,S['ChkStop']);star=m.memory[S['StarFlagTaskControl']]
  assert(collision,star)==((255,0)if name=='retained43negative'else(254,1))
  wall.append(dict(component=name,native_tile_return=tile,collision_bits=collision,StarFlagTaskControl=star))
 canvas=0
 for engine in[0,4,5,7,9,11]:
  for y,high in[(124,1),(176,1),(248,0),(240,1)]:
   m=mem();m.memory[S['GameEngineSubroutine']]=engine;m.memory[S['Player_X_Position']]=84;m.memory[S['Player_PageLoc']]=12;m.memory[S['ScreenLeft_X_Pos']]=20;m.memory[S['ScreenLeft_PageLoc']]=12;m.memory[S['Player_Y_Position']]=y;m.memory[S['Player_Y_HighPos']]=high
   m.memory[0xc200:0xc281]=[(i*7+11)&255 for i in range(129)];before=m.memory[0xc200:0xc281];m.memory[0xc310]=0;m.memory[7:11]=[255]*4
   T.call(m,L['MiniHostDraw']);expected_y=(((high-1)*256+y+16)&65535)
   assert m.memory[0xc311:0xc315]==[64,0,expected_y&255,expected_y>>8]
   assert m.memory[0xc200:0xc281]==before,'Native scripted drawing must never advance/import source state'
   assert m.memory[0x6b05:0x6b08]==[4,5,107]and m.memory[S['ObjectMetasprite']]==0
   canvas+=1
 # Actual DrawPlayer_Intermediate sets these native coordinates and leaves
 # old R4..R7 setup commented out. Neither stale source nor R4..R7 may win.
 m=mem();m.memory[S['Player_X_Position']]=0x60;m.memory[S['Player_Y_Position']]=0x58;m.memory[S['Player_PageLoc']]=3;m.memory[S['ScreenLeft_PageLoc']]=3;m.memory[7:11]=[0xed,0xab,0xcd,0xef];m.memory[0xc310]=55
 T.call(m,L['MiniHostPortrait']);assert m.memory[0xc310:0xc315]==[0,0x60,0,0x68,0]
 assert m.memory[0x200:0x204]==[0x67,1,0,0x60]
 # Normal engine8 rendering and its source state stay instruction-equivalent
 # in output; exercise camera low phase and active rotation in four pairs.
 ordinary=0
 for camera in[0,37]:
  for rotation in[0,60]:
   pair=[mem(old),mem(data)]
   for m in pair:
    m.memory[0xc250:0xc254]=list((123*16+7).to_bytes(2,'little')+(200*16+15).to_bytes(2,'little'));m.memory[0xc310]=5;m.memory[S['ScreenLeft_X_Pos']]=camera;m.memory[0x6c0b]=int(rotation!=0);m.memory[0x6c08]=rotation;m.memory[S['CurrentOAMOffset']]=24
   T.call(pair[0],prior['labels']['MiniHostDraw']);T.call(pair[1],L['MiniHostDraw'])
   assert pair[0].memory[0x200:0x300]==pair[1].memory[0x200:0x300]and pair[0].memory[0xc200:0xc316]==pair[1].memory[0xc200:0xc316];ordinary+=1
 native_bytes={}
 for name,bank,pc,count in[('outside8_movement_fallback',1,0xa62a,9),('castle_ChkStop',1,S['ChkStop'],27),('native_ImpedePlayerMove',126,S['ImpedePlayerMove'],64)]:
  at=16+bank*8192+pc-(0x8000 if bank==126 else 0xa000);native_bytes[name]=dict(PRG=bank,CPU=pc,file_offset=at,hex=raw[at:at+count].hex())
 out=dict(passed=True,ROM_written=False,native_admitted=False,parent_ROM_SHA256=PIN,bytes=len(data),SHA256=W.sha(data),five_pages_spare=5120-len(data),labels=L,vectors=[int.from_bytes(data[i*3+1:i*3+3],'little')for i in range(38)],native_getter_contexts=getters,native_castle_wall_fixture=wall,native_canvas_contexts=canvas,actual_native_lives_portrait=dict(native_X=96,native_Y=88,canvas_X=96,canvas_Y=104,pose=0,unpopulated_R4_R7_ignored=True),normal_engine8_draw_pairs=ordinary,source_state_untouched_by_scripted_draw=True,actual_native_bytes=native_bytes,scope='Source/private compiled leaves only over exact installed8daf. Native terminal engine5/CollisionBitsFF/StarFlag0 diagnosis is root-owned end47. Ordinary sourceStep/motion/physics and source-based engine8 drawing unchanged. Head/Side pass genuine native packets outside8; pure native canvas projects Xworld-camera and Ynative+16 for scripted movement/lives portrait. No new RAM, shared instructions, invented animation or source-state import outside8. Root exact candidate/native fullstage required.',bindings={p.relative_to(R).as_posix():W.sha(p.read_bytes())for p in[Path(__file__),PRIOR/'mini-host-v43.bin',PRIOR/'mini-host-v43.s',PRIOR/'mini-host-v43.json',R/'src/player.s',R/'src/collision.s',R/'src/screen_render.s',C.H.BASELABELS]})
 (O/'mini-host-v48.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({k:out[k]for k in['passed','bytes','SHA256','five_pages_spare','labels','native_getter_contexts','native_castle_wall_fixture','native_canvas_contexts']}))
if __name__=='__main__':main()
