"""Project actual US side-view instructions into the approved owned overlay.

No shared source/build changes. Source room-spawn and tile-memory interface are
explicit host boundaries; original control/physics/action instructions remain.
"""
from pathlib import Path
import re,json
from py65.devices.mpu6502 import MPU
import dragon_power_map_v1 as D
ROOT=D.ROOT
RAM={0:'R0',1:'R1',0x26:'DpClock',0x27:'DpSecondPhase',0x42:'DpExit',0x4a:'DpSpawnFlag',0x87:'DpKickAge',
     0xd6:'DpSpawnSide',0xd9:'DpFlags',0xdf:'DpHeld',0xe0:'DpFresh',0xe4:'DpSourcePrevious',0xf7:'DpX',0xf8:'DpY'}
RAM.update({v:f'DpMath+{v}'for v in range(2,16)})
RAM.update({v:f'DpContacts+{v-0x400}'for v in range(0x400,0x40d)})
RAM.update({v:f'DpPlatform+{v-0x446}'for v in range(0x446,0x44b)})
RAM.update({0x2d:'DpAction',0x2e:'DpHP',0x2f:'DpProtection',0x30:'DpPose',0x31:'DpAttribute',
 0x32:'DpActionFlags',0x33:'DpTimer',0x34:'DpVertical',0x35:'DpHorizontal',0x36:'DpSeconds',
 0x37:'DpSpecial',0x38:'DpJumping',0x39:'DpGroundY',0x3a:'DpShotState',0x3b:'DpWaves',
 0x3c:'DpShotY',0x3d:'DpShotYPage',0x3e:'DpShotX',0x3f:'DpShotXPage'})
EXTERNAL={0x98a8:'DpAudioRequest',0xecba:'DpSpawnHook',0xed2c:'DpHostTileQuery',0x984d:'DpSceneExitRequest'}
DATA={0xe867:34,0xea7e:2,0xec60:8,0xee36:32}
def main():
 m=D.memory(3);cpu=MPU(memory=m);todo=[0xe82e,0xec4d]
 for p,n in [(0xe867,17),(0xee36,16),(0xec60,4)]:todo +=[m[p+i*2]|m[p+i*2+1]<<8 for i in range(n)]
 code={}
 while todo:
  pc=todo.pop()
  if pc in code or pc in EXTERNAL:continue
  assert 0xe82e<=pc<0xefb9,hex(pc)
  ins,mode=cpu.disassemble[m[pc]];n={'imp':1,'acc':1,'imm':2,'zpg':2,'zpx':2,'zpy':2,'inx':2,'iny':2,'rel':2,'abs':3,'abx':3,'aby':3,'ind':3}[mode]
  code[pc]=(ins,mode,n)
  target=m[pc+1]|m[pc+2]<<8 if n==3 else None
  if ins in ['JSR','JMP'] and mode=='abs':
   if target not in EXTERNAL:todo.append(target)
  if mode=='rel':todo.append((pc+2+(m[pc+1]if m[pc+1]<128 else m[pc+1]-256))&65535)
  if ins not in ['RTS','RTI','JMP']:todo.append(pc+n)
 lines=['; Generated from DragonPowerUSA SHA'+D.SHA+'.',
        '; Every label is a genuine original instruction/data boundary. No fake aliases.',
        '.pushseg','.segment "DRAGON_POWER_CORE"','DpNativeStart:']
 branch={'BCC':'jcc','BCS':'jcs','BEQ':'jeq','BNE':'jne','BMI':'jmi','BPL':'jpl','BVC':'jvc','BVS':'jvs'}
 for pc in sorted(set(code)|set(DATA)):
  label=f'DpN{pc:04X}'
  lines.append(label+':')
  if pc in DATA:
   if pc in [0xe867,0xee36,0xec60]:
    lines.append(' .word '+','.join(f'DpN{m[a]|m[a+1]<<8:04X}'for a in range(pc,pc+DATA[pc],2)))
   else:lines.append(' .byte '+','.join(str(v)for v in m[pc:pc+DATA[pc]]))
   continue
  ins,mode,n=code[pc];operand=''
  if mode=='rel':
   target=(pc+2+(m[pc+1]if m[pc+1]<128 else m[pc+1]-256))&65535
   op=branch[ins];operand=f'DpN{target:04X}'
  else:
   op=ins.lower()
   if mode=='acc':operand='a'
   elif mode=='imm':operand=f'#${m[pc+1]:02x}'
   elif mode!='imp':
    value=m[pc+1]|(m[pc+2]<<8 if n==3 else 0)
    if ins in ['JSR','JMP']and mode=='abs':operand=EXTERNAL.get(value,f'DpN{value:04X}')
    elif value in DATA or value-1 in DATA:operand=f'DpN{value-(value-1 in DATA):04X}'+('+1'if value-1 in DATA else'')
    else:
     assert value in RAM,(hex(pc),ins,mode,hex(value));operand=RAM[value]
    if mode in ['zpx','abx']:operand+=',x'
    if mode in ['zpy','aby']:operand+=',y'
    if mode=='ind':operand='('+operand+')'
    if mode=='iny':operand='('+operand+'),y'
    if mode=='inx':operand='('+operand+',x)'
  lines.append(f' {op} {operand}'.rstrip()+f' ;3:{pc:04X} '+m[pc:pc+n].hex())
  if pc+n in EXTERNAL and ins not in ['RTS','RTI','JMP']:
   lines.append(' jmp '+EXTERNAL[pc+n]+' ; genuine original fall-through crosses projected boundary')
 lines+=['DpNativeEnd:','.export DpN'+',DpN'.join(f'{pc:04X}'for pc in [0xe82e,0xe906,0xe99a,0xe9b3,0xea20,0xea3d,0xec4d,0xee70,0xeecb]),'.popseg']
 p=ROOT/'src/dragon_power_native.inc';p.write_text('\n'.join(lines)+'\n')
 print(json.dumps(dict(source_instructions=len(code),original_instruction_bytes=sum(n for _,_,n in code.values()),output=D.binding(p)),indent=2))
if __name__=='__main__':main()
