"""Compare committed candidate bursts and animation calls to the original."""
from pathlib import Path
import argparse,csv,hashlib,importlib.util,json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/reference'))
import export_parodius_art as art
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def original(reference,raw,variant,cpu):
 poses=art.records(raw);source=raw[131088:];rows=list(csv.DictReader((reference/'render-burst.csv').open()))
 animation=cpu.memory[0x932e+variant];frames=set(art.native.native_animations(cpu)[animation]['data'][:-1:2])
 assert {int(r['pose'])for r in rows}==frames
 for r in rows:
  pose=int(r['pose']);assert int(r['skin'])==10 and int(r['active'])==16
  assert int(r['ctrl'])&32 and int(r['paletteOverride'])==(1 if variant==2 else 0)
  palette=bytes.fromhex(r['palette'])
  assert [list(palette[16+i*4:20+i*4])for i in range(4)]==art.PALETTES
  actual=[tuple(bytes.fromhex(r['oam'])[i:i+4])for i in range(0,256,4)]
  expected=[((int(r['y'])+p['dy'])&255,p['tile'],(p['attr']&0xc0)|1 if variant==2 else p['attr'],(int(r['x'])+p['dx'])&255)for p in poses[pose]['parts']]
  assert set(expected)<=set(actual),'Original cartridge must commit every source burst sprite'
  pp=(reference/f'start-ppu-{pose}.bin').read_bytes()
  assert pp[:1024]==source[10240:11264],'Original visible CHR must really use skin10'
 return dict(poses=len(frames),animation=animation,original_DMA_and_physical_CHR_match=True,trace_sha256=sha(reference/'render-burst.csv'))


def case(folder,raw,cpu,variant):
 rows=list(csv.DictReader((folder/'death.csv').open()));assert len(rows)>80
 source=raw[131088:];poses=art.records(raw);pixels=0;peak=0
 from check_parodius_packed_art import compose
 expected_palette={1:[0x30,0x15,0x08],2:[0x30,0x28,0x06],3:[0x21,0x03,0x06]}[variant]
 signed=lambda v:v if v<128 else v-256
 for r in rows:
  pose=int(r['pose']);parts=poses[pose]['parts'];record=bytes.fromhex(r['record'])
  palette=bytes.fromhex(r['palette']);assert palette[17:20]==bytes(expected_palette),(r['frame'],'Native character death palette')
  page=int(r['bank']);data=(folder/f'death-chr-{page}.bin').read_bytes();assert len(data)==1024
  packed_parts=[tuple(record[i:i+4])for i in range(1,len(record),4)];assert len(packed_parts)*4==record[0]
  def read(tile):
   assert tile<64 and not tile&1;return art.pixels(data,tile,[0,0,0,0,0,0,0,0])
  actual_pixels=compose([(signed(dx),signed(dy),tile,attr)for tile,attr,dy,dx in packed_parts],read,lambda p,v:palette[16+4*p+v]&63)
  expected_pixels=compose([(p['dx']+8,p['dy']+8,p['tile'],(p['attr']&0xc0)|1 if variant==2 else p['attr'])for p in parts],
   lambda tile:art.pixels(source,tile,[10,4,11,5,0,0,0,0]),lambda p,v:0x27 if variant==3 and art.PALETTES[p][v]==0x28 else art.PALETTES[p][v])
  assert actual_pixels==expected_pixels,(r['frame'],'Original character death pixels/colors with declared Pentarou yellow quantization')
  oam=bytes.fromhex(r['oam']);actual=[tuple(oam[i:i+4])for i in range(0,256,4)]
  intended=[(int(r['y'])+signed(dy),tile,(attr|int(r['attr']))&0xf3,(int(r['x'])+signed(dx))&255)for tile,attr,dy,dx in packed_parts]
  assert set(intended)<=set(actual),(r['frame'],'Completed DMA contains all original body parts')
  scan=max(sum(yy<240 and yy+1<=line<yy+17 for yy,_,_,_ in actual)for line in range(int(r['y'])+1,int(r['y'])+17))
  assert scan<=8,'The isolated death body must fit the real sprite scanline budget'
  peak=max(peak,scan)
  # Compare decoded pixels, so packing and palette-layer changes cannot hide
  # a missing source pixel or an undeclared color substitution.
  pixels+=len(expected_pixels)
 trace=list(csv.DictReader((folder/'native-animation.csv').open()));assert len(trace)>100
 animation=cpu.memory[0x932e+variant]
 assert [int(trace[0][k])for k in('animation','pose','delay','cursor')]==[animation,0,0,0]
 cpu.memory[0x6770]=animation;cpu.memory[0x6410]=cpu.memory[0x6710]=cpu.memory[0x6740]=0
 for r in trace:
  state=[cpu.memory[a]for a in(0x6770,0x6410,0x6710,0x6740)]
  assert [int(r[k])for k in('animation','pose','delay','cursor')]==state,(r,state,'Original animation routine differential')
  cpu.a=cpu.x=cpu.y=0;cpu.p=0x30;cpu.sp=0xfd;cpu.memory[0x1fe]=0xef;cpu.memory[0x1ff]=0x7f;cpu.pc=0xc98a
  n=0
  while cpu.pc!=0x7ff0:
   cpu.step();n+=1;assert n<300
 return dict(frames=len(rows),native_animation_calls=len(trace),source_pixel_observations=pixels,
  original_pixels_and_declared_colors=True,Pentarou_yellow28_to27=variant==3,all_intended_sprites_committed=True,peak_body_scanline_sprites=peak,
  original_animation_instruction_differential=True,trace_sha256=sha(folder/'native-animation.csv'),DMA_trace_sha256=sha(folder/'death.csv'))


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--folder',type=Path,required=True);p.add_argument('--reference',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 raw,cpu=art.native.source_cpu();run=json.loads((a.folder/'results.json').read_text());assert run['passed']
 report=dict(passed=True,rom_sha256=run['rom_sha256'],source_sha256=art.native.SHA,
  original_capture={str(v):original(a.reference if v==1 else ROOT/f'build/verification/parodius-death-nr/original-variant-{v}',raw,v,cpu)for v in(1,2,3)},variants={str(v):case(a.folder/str(v)/'build/verification',raw,cpu,v)for v in(1,2,3)},
  scope='Character-specific original death pixels/timing, actual terrain-kill/DMA/movable-respawn arenas. Pentarou yellow28 maps to shared yellow27; NPC palettes unchanged. SMB retains its respawn timer. No full-campaign/audio/performance certification.')
 a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))


if __name__=='__main__':main()
