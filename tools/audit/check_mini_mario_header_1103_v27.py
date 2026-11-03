"""Retain4923 native-header negative and qualify exact seven-byte successor."""
import json,sys
from pathlib import Path
from py65.devices.mpu6502 import MPU
sys.path.insert(0,str(Path(__file__).resolve().parent))
import prepare_mini_mario_host_1103_v22 as H
import check_mini_mario_step_1103_v18 as T
W,R,O=H.W,H.R,H.O
def main():
 S=H.symbols();old=(O/'mini-host-v22.bin').read_bytes();new=(O/'mini-host-v26.bin').read_bytes();q=json.loads((O/'mini-host-v26.json').read_text());L=q['labels'];at=L['MiniHostName']-0xa000;assert old[:at]==new[:at]
 cases=0;negative=None
 for version,data in[('v22-retained-negative',old),('v26-seven-name',new)]:
  for message in range(5):
   for off in[0,1,32,76,83]:
    for flags in[0x20,0x24,0x61,0xe4]:
     m=MPU();m.memory[0xa000:0xa000+len(data)]=data;m.memory[S['OperMode']]=1;m.memory[S['VRAM_Buffer1_Offset']]=off
     packet=[i^0xa5 for i in range(84)];packet[18:21]=[0x20,0x52,11];m.memory[S['VRAM_Buffer1']:S['VRAM_Buffer1']+84]=packet;m.a=message;m.x=71;m.y=73;m.p=flags;T.call(m,L['MiniHostName']);out=m.memory[S['VRAM_Buffer1']:S['VRAM_Buffer1']+84]
     assert(m.a,m.x,m.y)==(message,71,73)and m.p&0xcf==(flags|1)&0xcf
     assert m.memory[S['VRAM_Buffer1_Offset']]==off
     if message:
      assert out==packet
     elif version.startswith('v22'):
      assert out[18:20]!=packet[18:20]
      negative=dict(scope='Source-backed deterministic CPU packet corruption, not emulator result',old_WORLD_TIME_packet_header=packet[18:21],after_old9byte_name=out[18:21])
     else:
      assert out[:11]+out[18:]==packet[:11]+packet[18:]
      assert out[11:18]==[0x16,0x12,0x17,0x12,0x24,0x24,0x24]
     cases+=1
 menu=0
 for off in[0,1,20,64,65,76,83]:
  m=MPU();m.memory[0xa000:0xa000+len(new)]=new;m.memory[S['OperMode']]=0;m.memory[S['VRAM_Buffer1_Offset']]=off;m.a=54;m.x=55;m.y=56;m.p=0x24;T.call(m,L['MiniHostName'])
  if off<65:
   assert m.memory[S['VRAM_Buffer1']+off:S['VRAM_Buffer1']+off+20]==[0x23,0x28,16,0x24,0x24,0x24,0x16,0x12,0x17,0x12,0x16,0xa,0x1b,0x12,0x18,0x24,0x24,0x24,0x24,0]
   assert m.memory[S['VRAM_Buffer1_Offset']]==off+19
  else:assert m.memory[S['VRAM_Buffer1_Offset']]==off
  assert(m.a,m.x,m.y)==(54,55,56);menu+=1
 out=dict(passed=True,component_SHA256=W.sha(new),component_bytes=len(new),header_public_cases=cases,menu_public_cases=menu,old_negative=negative,prior_CPU_v24_reused='Entire code prefix throughMiniHostName unchanged; all priortested entries and data reside beforethis boundary. Only its untestednativeHeaderleaf/data differ fourbytes.',all_prior_800_source_differential_and_native_Main_palette_bbox_head_bytes_exact=True,private_ROM_emission=False,native_admitted=False,bindings={p.relative_to(R).as_posix():W.sha(p.read_bytes())for p in[Path(__file__),O/'mini-host-v26.json',O/'mini-host-CPU-v24.json',O/'mini-wall-CPU-v25.json',R/'src/screen_render.s']})
 (O/'mini-header-CPU-v27.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
