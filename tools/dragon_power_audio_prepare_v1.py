"""Exact original Dragon Power driver/data projection into approved96:A980.

No scheduler/shared source edit. Original far-return entry8F62 and98CF are
omitted; genuine direct driver/request entries remain. No stream/event cuts.
"""
import json,re,subprocess
import dragon_power_component_v1 as B
from py65.devices.mpu6502 import MPU
D=B.D;ROOT=B.ROOT;OUT=ROOT/'build/dragon-power-audio-v1'
DATA=[(0x8040,0x8f62),(0x9301,0x9319),(0x9345,0x9419)]
CODE=[(0x8f68,0x9301),(0x9319,0x9345),(0x98a8,0x98cf),(0x98d5,0x98fb)]
SIZES={'imp':1,'acc':1,'imm':2,'zpg':2,'zpx':2,'zpy':2,'inx':2,'iny':2,'rel':2,'abs':3,'abx':3,'aby':3,'ind':3}
def generate():
 m=D.memory(3);c=MPU(memory=m);code={};needed=set()
 for lo,hi in CODE:
  pc=lo
  while pc<hi:
   op,mode=c.disassemble[m[pc]];n=SIZES[mode];assert op!='???'and pc+n<=hi,(hex(pc),op,mode)
   code[pc]=(op,mode,n);pc+=n
 for p in range(0x8040,0x81f4,4):
  addr=m[p+2]|m[p+3]<<8
  assert addr==65535 or 0x81f4<=addr<0x8f62
  if addr!=65535:needed.add(addr)
 for pc,(op,mode,n)in code.items():
  if n==3:
   v=m[pc+1]|m[pc+2]<<8
   if 0x8040<=v<0x9419 or v in code:needed.add(v)
 lines=['; Actual USA Dragon Power source projection. Immutable sourceSHA '+D.SHA,
  '; Original far-return stubs8F62..67/98CF..D4 omitted. No event/voice/tick cut.',
  '.pushseg','.segment "DRAGON_POWER_AUDIO"','DpAudioNativeStart:']
 allspans=sorted([(a,b,False)for a,b in DATA]+[(a,b,True)for a,b in CODE])
 for lo,hi,iscode in allspans:
  pc=lo
  while pc<hi:
   if pc in needed or pc in code or pc in [0x8040,0x81f4]:lines.append(f'DpAN{pc:04X}:')
   if not iscode:
    if 0x8042<=pc<0x81f4 and(pc-0x8042)%4==0:
     v=m[pc]|m[pc+1]<<8
     lines.append(' .word '+(f'DpAN{v:04X}'if v!=65535 else'$ffff'));pc+=2
    else:lines.append(f' .byte ${m[pc]:02x} ;3:{pc:04X}');pc+=1
    continue
   op,mode,n=code[pc];operand='';v=m[pc+1]|(m[pc+2]<<8 if n==3 else 0)
   if mode=='rel':
    v=(pc+2+(m[pc+1]if m[pc+1]<128 else m[pc+1]-256))&65535
    assert v in code;operand=f'DpAN{v:04X}'
   elif mode=='imm':
    operand=f'#${v:02x}'
    if pc==0x98ba:operand='#<DpAN8040'
    if pc==0x98c1:operand='#>DpAN8040'
   elif mode=='acc':operand='a'
   elif mode!='imp':
    if 0x688<=v<0x700:operand=f'DpAudioState+{v-0x688}'
    elif 0x3f0<=v<0x3fc:operand=f'DpAudioState+{120+v-0x3f0}'
    elif 0x8040<=v<0x9419 or v in code:operand=f'DpAN{v:04X}'
    else:
     assert v in range(0x12,0x17)or v in [0x4000,0x4001,0x4002,0x4003,0x4008,0x4015],(hex(pc),hex(v))
     operand=f'${v:02x}'if n==2 else f'${v:04x}'
    if 0x4000<=v<=0x4015:
     assert op=='STA'
     operand='GuestNativeStatusSTA'if v==0x4015 else'GuestNativeStoreSTA'+f'{v-0x4000:02x}'+('Y'if mode=='aby'else'')
     if v==0x4008:operand='DpAudioStore08'
     op='JSR'
    else:
     if mode in ['zpx','abx']:operand+=',x'
     if mode in ['zpy','aby']:operand+=',y'
     if mode=='iny':operand='('+operand+'),y'
     if mode=='inx':operand='('+operand+',x)'
   lines.append(' '+op.lower()+(' '+operand if operand else'')+f' ;3:{pc:04X} '+m[pc:pc+n].hex())
   pc+=n
 lines+=['DpAudioNativeEnd:','.export DpAN8040,DpAN8F68,DpAN98A8,DpAudioNativeStart,DpAudioNativeEnd','.popseg']
 p=ROOT/'src/dragon_power_audio_native.inc';p.write_text('\n'.join(lines)+'\n')
 return dict(source=D.binding(D.ROM),source_instruction_count=len(code),original_bytes=sum(n for _,_,n in code.values()),
  native_projection_bytes=5152,omitted_far_stubs=['3:8F62..8F67','3:98CF..98D4'],generated=D.binding(p))
def build():
 OUT.mkdir(exist_ok=True);recipe=generate()
 for ext,h in B.EXPECTED.items():assert D.digest(B.HOST.with_suffix('.'+ext).read_bytes())==h
 s=B.labels(B.HOST.with_suffix('.lbl'))
 names='SelectedCharacter RgAudioRam RgAudioCpuZp RgAudioCharacter RgAudioSong RgAudioSilenced RgAudioRequest GuestNativeApu GuestNativeDirty GuestNativeStatusSTA'.split()
 names +=['GuestNativeStoreSTA'+n for n in ['00Y','01Y','02Y','03Y']]
 pre='\n'.join(f'{n}=${s[n]:04x}'for n in names)+'\n'
 (OUT/'component.s').write_text(pre+'.include "dragon_power_audio.s"\n')
 (OUT/'component.cfg').write_text('MEMORY { A:start=$A980,size=$1680,bank=96,file=%O; }\nSEGMENTS { DRAGON_POWER_AUDIO:load=A,type=ro; }\n')
 cc=ROOT/'tools/Windows/cc65/bin'
 commands=[[str(cc/'ca65.exe'),'-g','-I',str(ROOT/'src'),str(OUT/'component.s'),'-o',str(OUT/'component.o')],
  [str(cc/'ld65.exe'),'-C',str(OUT/'component.cfg'),'-o',str(OUT/'component.bin'),'-Ln',str(OUT/'component.lbl'),
   '--dbgfile',str(OUT/'component.dbg'),str(OUT/'component.o')]]
 for cmd in commands:
  q=subprocess.run(cmd,capture_output=True,text=True)
  if q.returncode:
   p=OUT/'first-build-failure.txt'
   if not p.exists():p.write_text(q.stdout+q.stderr)
   raise RuntimeError(q.stdout+q.stderr)
 code=(OUT/'component.bin').read_bytes();assert len(code)<=5760
 s.update(B.labels(OUT/'component.lbl'))
 recipe.update(compiled=D.binding(OUT/'component.bin'),total_bytes=len(code),end_inclusive=f'{0xa980+len(code)-1:04X}',
  state_bytes=137,borrowed_ZP=['12','13','14','15','16'],remaining=5760-len(code))
 (OUT/'build.json').write_text(json.dumps(recipe,indent=2)+'\n')
 print(json.dumps(recipe,indent=2));return code,s
if __name__=='__main__':build()
