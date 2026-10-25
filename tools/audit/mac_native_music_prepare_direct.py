"""Private same-bank Mac driver with non-indirect source ZP in owned SRAM.

Original $0700 channel state was already directly relocated. This removes ten
unneeded live-ZP transfers; only the authentic ($F8),Y pointer is borrowed.
"""
from pathlib import Path
import argparse,hashlib,json
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler
from mac_native_music_prepare import ADAPTER,ROOT,NSF,SHA

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--coverage',type=Path,required=True);a=p.parse_args();assert a.source.resolve()!=ROOT
 q=json.loads(a.coverage.read_text());raw=NSF.read_bytes();assert hashlib.sha256(raw).hexdigest()==SHA==q['source_sha256'];body=raw[128:];mem=[0]*32768+list(body);cpu=MPU(memory=mem);dis=Disassembler(cpu)
 seen=set(q['seen_instructions']);pointers={v[0]:v[1]for v in q['pointer_components']};pieces=[(0x8000,0x8c8c),(0xf400,0xf494),(0xf53c,0xf63f),(0xf674,0xf767),(0x9000,0x9800),(0x9a00,0x9f92),(0x9fa0,0xa000)]
 zp=sorted(v for v in q['RAM_accesses']if v<256);assert zp==list(range(240,250))+[252,253]
 assert all(cpu.disassemble[mem[pc]][1]not in ['zpx','zpy','inx']for pc in seen)
 assert all(mem[pc+1]==248 for pc in seen if cpu.disassemble[mem[pc]][1]=='iny')
 used=set(q['ROM_data_reads'])
 for pc in seen:
  n,_=dis.instruction_at(pc);used.update(range(pc,pc+n))
 for lo,hi in [(0x8c8c,0x9000),(0x9800,0x9a00),(0x9f92,0x9fa0)]:assert not used.intersection(range(lo,hi)),(hex(lo),hex(hi))
 def copied(at):return any(lo<=at<hi for lo,hi in pieces)
 targets={0x8000,0x88e2,0x9f80,0x9000,0x8fff}
 direct=[];apu=[]
 grown={pc:1 for pc in seen if cpu.disassemble[mem[pc]][1]=='zpg'and mem[pc+1]not in [248,249]}
 longbranches=set()
 def virtual(at):
  if 0x8000<=at<0x8c8c:return at-0x8000+sum(v for pc,v in grown.items()if pc<at and pc<0x8c8c)
  raise AssertionError(('Branch outside main code',hex(at)))
 for _ in range(20):
  more=[]
  for pc in seen:
   op,mode=cpu.disassemble[mem[pc]]
   if mode!='rel'or not 0x8000<=pc<0x8c8c:continue
   target=pc+2+(mem[pc+1]-256 if mem[pc+1]>=128 else mem[pc+1]);delta=virtual(target)-virtual(pc)-2
   if pc not in longbranches and not -128<=delta<=127:more.append(pc)
  if not more:break
  for pc in more:grown[pc]=3;longbranches.add(pc)
 else:raise AssertionError('Branch-width closure did not converge')
 for pc in seen:
  op,mode=cpu.disassemble[mem[pc]];n,_=dis.instruction_at(pc);at=mem[pc+1]+256*mem[pc+2]
  if mode=='rel':targets.add(pc+n+(mem[pc+1]-256 if mem[pc+1]>=128 else mem[pc+1]))
  elif mode in ['abs','abx','aby','ind']and at>=32768:targets.add(at)
 for lo,hi in pointers.items():assert hi==lo+1;targets.add(mem[lo]+256*mem[hi])
 assert all(copied(at)or at==0x8fff for at in targets),list(map(hex,[at for at in targets if not copied(at)and at!=0x8fff]))
 label=lambda at:f'::LmDirect{at:04X}'
 def writer(op,mode,at):
  if at==0x4015:return 'GuestNativeStatusSTA'
  suffix='X'if mode=='abx'else'Y'if mode=='aby'else'';name=f'GuestNativeStore{op}{at-0x4000:02x}{suffix}'
  if name+':'not in(a.source/'build/generated/guest-audio/writers.inc').read_text():assert not suffix;name=f'LmNative{op}{at-0x4000:02X}'
  return name
 lines=['; Original nine-track Punch-Out music; non-indirect ZP fields directly owned.','.pushseg','.segment "MAC_NATIVE_AUDIO"','LmNativeDirectZp=1','LmNativeRam=XgLzHistory','LmNativeZp=XgLzHistory+$100','LmNativeSavedZp=XgLzHistory+$110','LmNativePending=XgAudioSelection','LmNativeBankStart:']
 def emit(lo,hi):
  pc=lo
  while pc<hi:
   if pc in targets:lines.append(label(pc)+':')
   if pc in seen:
    n,text=dis.instruction_at(pc);op,mode=cpu.disassemble[mem[pc]];v=mem[pc+1];at=v+256*mem[pc+2]
    if mode=='rel':text=('j'+op[1:].lower()if pc in longbranches else op)+' '+label(pc+n+(v-256 if v>=128 else v))
    elif mode=='zpg'and v not in [248,249]:
     assert v in zp;text=op+f' ::LmNativeZp+${v-240:02x}';direct.append(dict(source_pc=pc,mode=mode,op=op,source_address=v,owned_image_offset=v-240))
    elif mode in ['abs','abx','aby','ind']:
     operand=label(at)if at>=32768 else f'::LmNativeRam+${at-0x700:02x}'if 0x700<=at<0x800 else f'${at:04x}'
     text=op+' '+('('+operand+')'if mode=='ind'else operand+(',x'if mode=='abx'else',y'if mode=='aby'else''))
     if op in ['STA','STX','STY']and 0x4000<=at<=0x4015:
      text='jsr '+writer(op,mode,at);apu.append(dict(source_pc=pc,address=at,mode=mode,op=op))
    lines.append('  '+text);pc+=n
   elif pc in pointers:
    if pc+1 in targets:lines.append(label(pc+1)+' = *+1')
    lines.append('  .word '+label(mem[pc]+256*mem[pc+1]));pc+=2
   else:
    values=[]
    while pc<hi and pc not in seen and pc not in pointers and(not values or pc not in targets)and len(values)<16:values.append(mem[pc]);pc+=1
    lines.append('  .byte '+','.join(f'${v:02x}'for v in values))
 # Main code grows only where zero-page operands become absolute. Every
 # branch/call uses source-address labels; note headers retain their window.
 for lo,hi in pieces[:4]:emit(lo,hi)
 lines+=['.assert *-LmNativeBankStart <= $1000,error,"Mac direct-ZP core exceeds blank source gap"','.res $1000-(*-LmNativeBankStart),$ff','LmDirect8FFF=LmDirect9000-1']
 emit(0x9000,0x9800)
 text=ADAPTER
 save=text.index('SaveCpu:\n');end=text.index('  lda RgAudioRequest\n  beq Play',save)
 text=text[:save]+'''SaveCpu:
  lda $f8
  sta LmNativeSavedZp+8
  lda LmNativeZp+8
  sta $f8
  lda $f9
  sta LmNativeSavedZp+9
  lda LmNativeZp+9
  sta $f9
'''+text[end:]
 start=text.index('Restore:\n');end=text.index('  jmp Queues',start)
 text=text[:start]+'''Restore:
  lda $f8
  sta LmNativeZp+8
  lda LmNativeSavedZp+8
  sta $f8
  lda $f9
  sta LmNativeZp+9
  lda LmNativeSavedZp+9
  sta $f9
'''+text[end:]
 text=text.replace('jsr LmNativeBankStart+$08e2','jsr LmDirect88E2')
 for at in [0xf0,0xf1,0xf2,0xf3,0xf4,0xf5,0xf7]:
  for op in ['lda','ora','sta']:text=text.replace(f'{op} ${at:02x}\n',f'{op} LmNativeZp+${at-240:02x}\n')
 lines.append(text);emit(0x9a00,0x9f92)
 lines+=['.assert *-LmNativeBankStart <= $1fa0,error,"Mac direct init exceeds original unused pad"','.res $1fa0-(*-LmNativeBankStart),$ff']
 emit(0x9fa0,0xa000)
 lines+=['.assert *-LmNativeBankStart=$2000,error,"Mac direct-ZP bank must remain 8 KiB"','LmNativeSourceInit=LmDirect9F80','LmNativeSourcePlay=LmDirect8000','.popseg','']
 native=a.source/'src/mac_native_music.s';native.write_text('\n'.join(lines))
 # Same owned source edits as v6; no accepted game-PC or mapper-slot change.
 entry=a.source/'src/entrypoint.s';s=entry.read_text();assert s.count('.include "gradius_audio.s"')==1;entry.write_text(s.replace('.include "gradius_audio.s"','.include "gradius_audio.s"\n.include "mac_native_music.s"'))
 cfg=a.source/'smb1base-mmc5-expanded.cfg';s=cfg.read_text();needle='    VIC_NATIVE_AUDIO:load=X5_NEW_7A,type=ro;';assert s.count(needle)==1;cfg.write_text(s.replace(needle,needle+'\n    MAC_NATIVE_AUDIO:load=X5_NEW_7B,type=ro;'))
 g=a.source/'src/gradius_audio.s';s=g.read_text();assert s.count('  jmp ExpandedAudioTick')==1;g.write_text(s.replace('  jmp ExpandedAudioTick','  jmp LmNativeMusicGate'))
 ch=a.source/'src/collision.s';s=ch.read_text();needle='  .res 44,$ea\n  .assert *-SmallPlatformCollision=63';assert s.count(needle)==1
 gate='''::LmNativeMusicGate:
  lda SelectedCharacter
  cmp #15
  bne LmNativeMusicLegacy
  BankPRGA #.bank(LmNativeMusicUpdate)
  jmp LmNativeMusicUpdate
LmNativeMusicLegacy:
  jmp ExpandedAudioTick
  .res 26,$ea
  .assert *-SmallPlatformCollision=63'''
 ch.write_text(s.replace(needle,gate))
 report=dict(source_sha256=SHA,coverage_sha256=hashlib.sha256(a.coverage.read_bytes()).hexdigest(),source_calls_per_track=18000,source_music_songs=[1,2,4,6,7,9,20,22,23],direct_ZP_operands=direct,expanded_relative_branches=sorted(longbranches),retained_indirect_pointer=[248,249],original_ZP_accesses=zp,all_indexed_indirect_operands_verified=True,source_RAM_0700_already_direct=True,APU_intercepts=apu,new_RAM_bytes=0,new_CHR_bytes=0,PRG_bank=123,PRG_bytes=8192,source_generated_sha256=hashlib.sha256(native.read_bytes()).hexdigest(),preparer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),hardware_qualified=False)
 (a.source.parent/'preparation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k not in ['direct_ZP_operands','APU_intercepts']}))
if __name__=='__main__':main()
