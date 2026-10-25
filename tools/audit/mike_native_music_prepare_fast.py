"""Stage authenticated StarTropics music into bank 115's declared free tail.

Private fast source only. Inline writers retain flags/registers and dirty semantics.
Only authenticated always-zero source SFX queues/freeze checks are bypassed.
"""
from pathlib import Path
import argparse,hashlib,json
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler
from mike_parodius_music_probe import SOURCE,EXPECTED
from mike_native_music_probe import ZP
ROOT=Path(__file__).resolve().parents[2]
PIECES=[(0x0400,0x0e20),(0x11bb,0x141f),(0x1541,0x1737),(0x1b39,0x1c3d),(0x2000,0x202e),(0x2048,0x249a),(0x25e4,0x29f7),(0x2c79,0x2d25),(0x2de9,0x3000),(0x1000,0x1021)]
FAMILY='''  lda SelectedCharacter
  cmp #16
  beq StFamilyMike
  php
  cmp #CHARACTER_KIRBY
  bcc StFamilyDone
  beq Kirby
  cmp #CHARACTER_TMNT
  lda #3
  rol
StFamilyDone:
  plp
  rts
StFamilyMike:
  BankPRGA #.bank(StNativeMusicUpdate)
  jmp StNativeFromFamily
Kirby:
  clc
  adc KbVariant
  plp
Done:rts'''
ADAPTER='''
; Only the first ExpandedAudioTick family call reaches this path. Discard its
; one inner return; the native updater returns to ExpandedAudioDecoded.
StNativeFromFamily:
  pla
  pla
  jmp StNativeMusicUpdate
.proc StNativeMusicUpdate
  lda #0
  sta RgAudioRequest
  lda OperMode
  jeq Mute
  lda XgAudioCharacter
  cmp #$fb
  beq Initialized
  lda #$fb
  sta XgAudioCharacter
  lda #0
  sta RgAudioSong
  sta RgAudioSilenced
  sta XgAudioEvent
  lda #1
  sta StNativePending
Initialized:
  lda AreaMusicQueue
  ora EventMusicQueue
  and #Silence
  beq Area
  lda #1
  sta RgAudioSilenced
Area:
  lda AreaMusicQueue
  and #$7f
  beq Event
  ldx #0
FindArea:
  lsr
  bcs AreaFound
  inx
  bne FindArea
AreaFound:
  lda Areas,x
  sta StNativePending
  lda #0
  sta RgAudioSilenced
  sta XgAudioEvent
Event:
  lda EventMusicQueue
  and #$7f
  beq Pause
  ldx #0
FindEvent:
  lsr
  bcs EventFound
  inx
  bne FindEvent
EventFound:
  lda Events,x
  sta StNativePending
  lda #0
  sta RgAudioSilenced
  lda #1
  sta XgAudioEvent
  cpx #6
  bne Pause
  lda #4
  sta XgAudioEvent
Pause:
  lda GamePauseStatus
  and #1
  jne Mute
  lda RgAudioSilenced
  jne Mute
  lda StNativePending
  sta RgAudioRequest
  bne Restart
  lda XgAudioEvent
  cmp #2
  jeq Mute
  ; All six source channel states are $ff at a finite tune's end. A queued
  ; original init still has its source request in $a0 until first play.
  lda StNativeZp
  bne SaveCpu
  lda StNativeRam+$10
  and StNativeRam+$11
  and StNativeRam+$12
  and StNativeRam+$13
  and StNativeRam+$14
  and StNativeRam+$15
  cmp #$ff
  bne SaveCpu
  lda XgAudioEvent
  beq LoopWholeTune
  cmp #4
  beq LoopWholeTune
  lda #2
  sta XgAudioEvent
  jmp Mute
LoopWholeTune:
  lda RgAudioSong
  sta RgAudioRequest
Restart:
  lda RgAudioRequest
  sta RgAudioSong
  inc XgAudioSong
  lda #0
  ldx #$9f
ResetState:
  sta StNativeRam,x
  dex
  cpx #$ff
  bne ResetState
  ldx #15
ResetImage:
  sta StNativeZp,x
  sta GuestNativeApu,x
  lda #1
  sta GuestNativeDirty,x
  lda #0
  dex
  bpl ResetImage
SaveCpu:
  jsr StNativeBorrow
  lda RgAudioRequest
  beq Play
  sec
  sbc #1
  ldx #0
  ldy #0
  jsr StNativeSourceInit
  lda #0
  sta StNativePending
  jmp Restore
Play:
  lda StNativeRam
  cmp GuestNativeEnable
  beq Enabled
  jsr GuestNativeStatusSTA
Enabled:
  ldx #0
  ldy #0
  jsr StNativeMusicPlay
Restore:
  jsr StNativeRestore
  jmp Queues
Mute:
  lda #0
  jsr GuestNativeStatusSTA
Queues:
  lda #0
  sta AreaMusicQueue
  sta EventMusicQueue
  sta Square1SoundQueue
  sta Square2SoundQueue
  sta NoiseSoundQueue
  rts
Areas:
  .byte 1,2,4,5,14,11,22
Events:
  .byte 13,15,9,17,15,9,5
.endproc
; The adapter never feeds original NSF SFX queues. Init is the only selected
; music writer to A2..A5/7168, and clears them with X=0. Keep pending-init's
; full original dispatch; active music enters its unmodified channel loop.
StNativeMusicPlay:
  lda StNativeZp
  bmi StNativeFullSource
  beq StNativeMusicIdle
  jmp StNativeP06CE
StNativeMusicIdle:
  rts
StNativeFullSource:
  jmp StNativeSourcePlay
StNativeStatusSTX:
  php
  pha
  txa
  jsr GuestNativeStatusSTA
  pla
  plp
  rts
'''
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--coverage',type=Path,required=True);a=p.parse_args();src=a.source.resolve();assert not src==ROOT
 raw=SOURCE.read_bytes();assert hashlib.sha256(raw).hexdigest()==EXPECTED;q=json.loads(a.coverage.read_text());assert q['source_sha256']==EXPECTED and not q['unknown_pointer_origins'];assert q['calls_per_track']==18000 and q['tracks']==[1,2,4,5,9,11,13,14,15,17,22]
 image=bytes(1024)+raw[128:];banks=list(raw[112:120]);memory=[0]*65536
 for i,b in enumerate(banks):memory[0x8000+i*4096:0x9000+i*4096]=(image[b*4096:(b+1)*4096]+bytes(4096))[:4096]
 c=MPU(memory=memory);d=Disassembler(c)
 # Exact writer-domain proof for the bypassed original source flags.
 source_flag_writers=[]
 for pc,physical in q['seen_instructions']:
  op,mode=c.disassemble[memory[pc]]
  operand=memory[pc+1]+256*memory[pc+2] if mode in ['abs','abx','aby']else memory[pc+1]if mode=='zpg'else None
  if op in ['STA','STX','STY','INC','DEC']and operand in [0xa2,0xa3,0xa4,0xa5,0x7168]:source_flag_writers.append(pc)
 assert sorted(source_flag_writers)==[0xf4b0,0xf4b2,0xf4b4,0xf4b6,0xf4b8]
 assert bytes(memory[0xf4aa:0xf4ac])==bytes([0xa2,0])

 def phys(at):return banks[(at-0x8000)//4096]*4096+(at&4095)
 seen={p:pc for pc,p in q['seen_instructions']};ptr={}
 for lo,hi,at,target in q['pointer_components']:
  for orig,part in [(lo,'<'),(hi,'>')]:
   assert orig not in ptr or ptr[orig]==(part,target),(orig,ptr.get(orig),(part,target))
   ptr[orig]=(part,target)
 def label(at):
  assert any(lo<=at<hi for lo,hi in PIECES),('Unpacked original byte',hex(at))
  return f'::StNativeP{at:04X}'
 for at in q['ROM_data_reads']:label(at)
 out=['; Generated from authenticated StarTropics original NSF and full-track provenance.','.pushseg','.segment "MIKE_NATIVE_AUDIO"','StNativeRam=XgLzHistory','StNativeZp=XgLzHistory+$100','StNativeSavedZp=XgLzHistory+$110','StNativePending=XgAudioSelection','StNativeBankStart:','.assert StNativeBankStart=$a200,lderror,"Mike tail must follow all existing music bytes"']
 apus=[];relocs=[];emitted=set();insn={};custom_writers=set()
 for lo,hi in PIECES:
  at=lo
  while at<hi:
   out.append(f'StNativeP{at:04X}:');emitted.add(at)
   if at in seen:
    pc=seen[at];size,text=d.instruction_at(pc);op,mode=c.disassemble[memory[pc]];v=memory[pc+1];word=v+256*memory[pc+2]
    if mode=='imm'and at+1 in ptr:
     part,target=ptr[at+1];text=f'{op} #{part}{label(target)}';relocs.append([pc,'immediate',part,target])
    elif mode=='rel':text=('jeq'if pc in [0xfcd3,0xfb8e]else op)+' '+label(phys(pc+size+(v-256 if v>=128 else v)))
    elif mode in ['abs','abx','aby','ind']:
     operand=label(phys(word))if word>=32768 else f'::StNativeRam+${word-0x7160:02x}'if 0x7160<=word<0x7200 else f'${word:04x}'
     text=op+' '+('('+operand+')'if mode=='ind'else operand+(',x'if mode=='abx'else',y'if mode=='aby'else''))
     if op in ['STA','STX','STY']and 0x4000<=word<=0x4015:
      if word==0x4015:helper='GuestNativeStatusSTA'if op=='STA'else'StNativeStatusSTX';assert op in ['STA','STX']and mode=='abs'
      else:
       helper=f'GuestNativeStore{op}{word-0x4000:02x}'+('X'if mode=='abx'else'Y'if mode=='aby'else'')
       if helper+':'not in(ROOT/'build/generated/guest-audio/writers.inc').read_text():
        assert mode=='abs'and op=='STA';helper=f'StNativeSTA{word-0x4000:02X}';custom_writers.add((helper,word-0x4000))
      text='jsr '+helper
      if word!=0x4015:
       offset=word-0x4000;idx=',y'if mode=='aby'else',x'if mode=='abx'else''
       assert op=='STA'and mode in ['abs','aby']
       inline=[f'sta GuestNativeApu+{offset}{idx}','php']
       inline+=['pha','lda #1',f'sta GuestNativeDirty+{offset}{idx}','pla']if mode=='aby'else[f'inc GuestNativeDirty+{offset}']
       inline+=['plp'];text='\n  '.join(inline);custom_writers.discard((helper,offset))
      apus.append(dict(source_pc=pc,helper=helper,source_address=word,mode=mode,inline_replacement=word!=0x4015))
    elif mode=='zpg'and v in ZP and v not in [0xac,0xad,0xf0,0xf1]:
     text=f'{op} ::StNativeZp+{ZP.index(v)}';relocs.append([pc,'direct_ZP',v,ZP.index(v)])
    insn[pc]=dict(label=f'StNativeP{at:04X}',source_physical=at,source_size=size,source_instruction=d.instruction_at(pc)[1],linked_instruction=text)
    out.append('  '+text);at+=size
   else:
    if at in ptr:
     part,target=ptr[at];out.append(f'  .byte {part}{label(target)}')
    else:out.append(f'  .byte ${image[at]:02x}')
    at+=1
 # Required data references never target an operand byte inside an instruction.
 for at in q['ROM_data_reads']:assert at in emitted,hex(at)
 for at in [target for part,target in ptr.values()]:assert at in emitted,hex(at)
 out+=['StNativeSourceInit=StNativeP0E13','StNativeSourcePlay=StNativeP06A4',ADAPTER]
 for name,restore in [('StNativeBorrow',False),('StNativeRestore',True)]:
  out.append(name+':')
  for i,at in enumerate([0xac,0xad,0xf0,0xf1]):
   idx=ZP.index(at)
   if restore:out.extend([f'  lda ${at:02x}',f'  sta StNativeZp+{idx}',f'  lda StNativeSavedZp+{i}',f'  sta ${at:02x}'])
   else:out.extend([f'  lda ${at:02x}',f'  sta StNativeSavedZp+{i}',f'  lda StNativeZp+{idx}',f'  sta ${at:02x}'])
  out.append('  rts')
 for name,offset in sorted(custom_writers):
  out.extend([name+':',f'  sta GuestNativeApu+{offset}','  php',f'  inc GuestNativeDirty+{offset}','  plp','  rts'])
 out+=['StNativeEnd:','.assert *-StNativeBankStart <= $1e00,error,"Mike source exceeds unused bank-115 tail"','.popseg','']
 path=src/'src/mike_native_music.s';path.write_text('\n'.join(out))
 entry=src/'src/entrypoint.s';s=entry.read_text();needle='.include "mac_native_music.s"';assert s.count(needle)==1;entry.write_text(s.replace(needle,needle+'\n.include "mike_native_music.s"'))
 cfg=src/'smb1base-mmc5-expanded.cfg';s=cfg.read_text();needle='    X5_FULL_MUSIC_0F:load=X5_NEW_73,type=ro;';assert s.count(needle)==1;cfg.write_text(s.replace(needle,needle+'\n    MIKE_NATIVE_AUDIO:load=X5_NEW_73,type=ro,align=$100;'))
 e=src/'src/expanded_audio.s';s=e.read_text();needle='::ExpandedAudioDecoded:\n.if ::ENABLE_MMC5_EXPANDED\n  jsr KbAudioFamily';assert s.count(needle)==1;s=s.replace(needle,'::ExpandedAudioDecoded:\n.if ::ENABLE_MMC5_EXPANDED\n  lda SelectedCharacter')
 start=s.index('.proc KbAudioFamily\n');end=s.index('.endproc',start);s=s[:start]+'.proc KbAudioFamily\n'+FAMILY+'\n'+s[end:];e.write_text(s)
 report=dict(status='PRIVATE_SOURCE_FAST_PREPARATION_ONLY',inactive_source_flag_writers=source_flag_writers,source_pending_init_full_dispatch=True,APU_inline_flags_AXY_preserved=True,source_sha256=EXPECTED,coverage_sha256=hashlib.sha256(a.coverage.read_bytes()).hexdigest(),calls_per_track=q['calls_per_track'],pieces=PIECES,preserved_source_bytes=sum(hi-lo for lo,hi in PIECES),pointer_components=q['pointer_components'],source_instructions=insn,APU_intercepts=apus,direct_RAM_relocations=relocs,source_generated_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),owned_history_bytes=288,new_RAM_bytes=0,new_CHR_bytes=0,PRG_bank=115,private_symbol_exception='KbAudioFamily::Kirby moves from the old genuine Kirby branch to its new genuine Kirby branch. No external calls/references permitted; public entry/span/Done must retain addresses.',preparer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),production_changes=False,native_emulator_launched=False)
 (src.parent/f'preparation-fast-{src.name}.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k not in ['source_instructions','APU_intercepts','direct_RAM_relocations','pointer_components']},indent=2))
if __name__=='__main__':main()
