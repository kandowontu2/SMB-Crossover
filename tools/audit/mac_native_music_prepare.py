"""Stage the nine authenticated Punch-Out music tracks in one native MMC5 bank.

Only writes into an explicitly supplied private source tree. It retains source
instruction lengths, rebases actual pointer words and leaves all game labels,
RAM allocations, CHR and fixed DPCM data in place. No emulator qualification.
"""
from pathlib import Path
import argparse, hashlib, json
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler

ROOT=Path(__file__).resolve().parents[2]
NSF=next((ROOT/'reference/new-roster-audio/mac').glob('*.nsf'))
SHA='9a7a3ae5f16b745f74296478ec208b5b87ad5ec2773a14b243f7e631a2dd8d68'

ADAPTER=r'''
; Nine source music tracks only. $fc is not a compressed playlist index.
.proc LmNativeMusicUpdate
  lda #0
  sta RgAudioRequest
  lda OperMode
  jeq Mute
  lda XgAudioCharacter
  cmp #$fc
  beq Initialized
  lda #$fc
  sta XgAudioCharacter
  lda #0
  sta RgAudioSong
  sta RgAudioSilenced
  sta XgAudioEvent
  lda #20
  sta LmNativePending
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
  sta LmNativePending
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
  sta LmNativePending
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
  lda LmNativePending
  sta RgAudioRequest
  bne Restart
  lda XgAudioEvent
  cmp #2
  jeq Mute
  ; Source $f6 becomes zero only at the complete finite tune's end.
  ; A fresh NSF init queues the selection in $f2 until its first play call.
  lda LmNativeZp+6
  ora LmNativeZp+2
  bne SaveCpu
  lda XgAudioEvent
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
  ldx #47
ResetState:
  sta LmNativeRam,x
  dex
  bpl ResetState
  ldx #15
ResetImage:
  sta LmNativeZp,x
  sta GuestNativeApu,x
  lda #1
  sta GuestNativeDirty,x
  lda #0
  dex
  bpl ResetImage
SaveCpu:
  jsr LmNativeBorrowMain
  lda $fc
  sta LmNativeSavedZp+12
  lda LmNativeZp+12
  sta $fc
  lda $fd
  sta LmNativeSavedZp+13
  lda LmNativeZp+13
  sta $fd
  lda RgAudioRequest
  beq Play
  sec
  sbc #1
  ldx #0
  ldy #0
  jsr LmNativeSourceInit
  lda #0
  sta LmNativePending
  jmp Restore
Play:
  lda GuestNativeEnable
  cmp #15
  beq Enabled
  lda #15
  jsr GuestNativeStatusSTA
Enabled:
  ldx #0
  ldy #0
  jsr LmNativeMusicPlay
Restore:
  jsr LmNativeRestoreMain
  lda $fc
  sta LmNativeZp+12
  lda LmNativeSavedZp+12
  sta $fc
  lda $fd
  sta LmNativeZp+13
  lda LmNativeSavedZp+13
  sta $fd
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
  .byte 20,22,1,23,2,1,23
Events:
  .byte 7,9,6,4,9,6,23
.endproc
; The public adapter supplies music, never original Punch-Out SFX requests.
; Keep the source's two ordered hardware-control stores, original music
; routine, and queue-clearing epilogue. Only the inactive SFX bit scans are
; omitted. Retain the complete source entry for any nonzero source SFX flag.
.proc LmNativeMusicPlay
  lda $f0
  ora $f1
  ora $f3
  ora $f4
  ora $f5
  ora $f7
  bne FullSource
  lda #$c0
  sta $4017
  lda #15
  jsr GuestNativeStatusSTA
  jsr LmNativeBankStart+$08e2
  lda #0
  sta $f0
  sta $f1
  sta $f2
  sta $f3
  rts
FullSource:
  jmp LmNativeSourcePlay
.endproc
; These stores use the established guest/world-effect mixer. The original
; source's direct $4017 store remains direct and occurs once per native play.
.macro LmNativeWriter Name,Op,Offset
.proc Name
  Op GuestNativeApu+Offset
  php
  inc GuestNativeDirty+Offset
  plp
  rts
.endproc
.endmacro
LmNativeWriter LmNativeSTA00,sta,0
LmNativeWriter LmNativeSTA04,sta,4
LmNativeWriter LmNativeSTA08,sta,8
LmNativeWriter LmNativeSTA0C,sta,12
LmNativeWriter LmNativeSTA0E,sta,14
LmNativeWriter LmNativeSTX00,stx,0
LmNativeWriter LmNativeSTX04,stx,4
LmNativeWriter LmNativeSTY08,sty,8
LmNativeAdapterEnd:
.assert LmNativeAdapterEnd-LmNativeMusicUpdate <= $200,error,"Mac adapter exceeds its 512-byte source hole"
.res $200-(*-LmNativeMusicUpdate),$ff
'''

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--coverage',type=Path,required=True);a=p.parse_args()
 assert a.source.resolve()!=ROOT
 raw=NSF.read_bytes();assert hashlib.sha256(raw).hexdigest()==SHA
 body=raw[128:];q=json.loads(a.coverage.read_text());assert q['source_sha256']==SHA
 seen=set(q['seen_instructions']);used=set(q['ROM_data_reads']);memory=[0]*32768+list(body);cpu=MPU(memory=memory);dis=Disassembler(cpu)
 # $8c8c..$8fff is originally blank. The $9800..$99ff data belong only to
 # unselected songs; every declared music selection ran 18,000 source calls.
 for pc in seen:
  size,_=dis.instruction_at(pc);used.update(range(pc,pc+size))
 assert not used.intersection(range(0x8c8c,0x9000))
 assert not used.intersection(range(0x9800,0x9a00))
 assert {v for v in q['RAM_accesses']if v<256}==set(range(0xf0,0xfa))|{0xfc,0xfd}
 assert body[0xc8c:0x1000]==bytes(0x374)
 pieces=[(0x8000,0x8c8c,0),(0xf400,0xf494,0xc8c),(0xf53c,0xf63f,0xd20),(0xf674,0xf767,0xe23),(0x9000,0x9800,0x1000),(0x9a00,0xa000,0x1a00)]
 def offset(at):
  # Some indexed table bases are one byte before their first accessed byte.
  # Keep the whole main window's coordinate system, even across unused holes.
  if 0x8000<=at<0xa000:return at-0x8000
  for lo,hi,dest in pieces:
   if lo<=at<hi:return dest+at-lo
  raise AssertionError(('Unpacked original address',hex(at)))
 def target(at):return f'::LmNativeBankStart+${offset(at):04x}'
 # All observed code and ROM reads must fit the packed source.
 for at in seen|set(q['ROM_data_reads']):offset(at)
 pointers={x[0]:x[1]for x in q['pointer_components']}
 assert all(hi==lo+1 for lo,hi in pointers.items())
 apu=[];relocations=[]
 def writer(op,mode,at):
  if at==0x4015:
   assert op=='STA' and mode=='abs';return 'GuestNativeStatusSTA'
  assert at<=0x400f
  suffix='X'if mode=='abx'else'Y'if mode=='aby'else''
  name=f'GuestNativeStore{op}{at-0x4000:02x}{suffix}'
  if name+':' not in (a.source/'build/generated/guest-audio/writers.inc').read_text():
   assert not suffix;name=f'LmNative{op}{at-0x4000:02X}'
  return name
 out=['; Generated from authenticated original Punch-Out NSF and complete-track provenance.','; One 8 KiB bank; selected music only, no NSF sound-effect entry points.','.pushseg','.segment "MAC_NATIVE_AUDIO"','LmNativeRam=XgLzHistory','LmNativeZp=XgLzHistory+$100','LmNativeSavedZp=XgLzHistory+$110','LmNativePending=XgAudioSelection','LmNativeBankStart:']
 order=sorted(pieces,key=lambda x:x[2]);cursor=0
 for lo,hi,dest in order:
  if cursor==0x1800:
   out.append(ADAPTER);cursor+=512
  assert dest>=cursor,(hex(dest),hex(cursor))
  if cursor==0xf16:
   # Same loads/stores as the loop, using only the twelve observed source
   # bytes. These ten transfers and their inverse fit the remaining blank
   # gap; the two discontinuous bytes stay inline in the adapter.
   for name,restore in [('LmNativeBorrowMain',False),('LmNativeRestoreMain',True)]:
    out.append(name+':')
    for i in range(10):
     at=f'${240+i:02x}'
     if restore:out.extend([f'  lda {at}',f'  sta LmNativeZp+{i}',f'  lda LmNativeSavedZp+{i}',f'  sta {at}'])
     else:out.extend([f'  lda {at}',f'  sta LmNativeSavedZp+{i}',f'  lda LmNativeZp+{i}',f'  sta {at}'])
    out.append('  rts')
   cursor+=202
  if dest>cursor:out.append(f'.res ${dest-cursor:x},$ff')
  out.append(f'.assert *-LmNativeBankStart=${dest:04x},error,"Mac packed offset"')
  pc=lo
  while pc<hi:
   if pc in seen:
    size,text=dis.instruction_at(pc);op,mode=cpu.disassemble[memory[pc]];v=memory[pc+1];at=v+256*memory[pc+2]
    if mode in ['abs','abx','aby','ind']:
     if at>=0x8000:operand=target(at)
     elif 0x700<=at<0x800:operand=f'::LmNativeRam+${at-0x700:02x}'
     else:operand=f'${at:04x}'
     text=op+' '+('('+operand+')'if mode=='ind'else operand+(',x'if mode=='abx'else',y'if mode=='aby'else''))
     if op in ['STA','STX','STY']and 0x4000<=at<=0x4015:
      helper=writer(op,mode,at);text='jsr '+helper;apu.append(dict(source_pc=pc,packed_pc=0xa000+offset(pc),op=op,mode=mode,address=at,helper=helper))
     if at>=0x8000 or 0x700<=at<0x800:relocations.append(dict(pc=pc,address=at,operand=operand))
    elif mode=='rel':
     destpc=pc+size+(v-256 if v>=128 else v)
     text=op+' '+target(destpc)
    # Every source instruction retains its original width.
    out.append('  '+text);pc+=size
   elif pc in pointers:
    at=memory[pc]+256*memory[pc+1];out.append('  .word '+target(at));pc+=2
   else:
    run=[]
    while pc<hi and pc not in seen and pc not in pointers and len(run)<16:
     run.append(memory[pc]);pc+=1
    out.append('  .byte '+','.join(f'${v:02x}'for v in run))
  cursor=dest+hi-lo
 out+=['.assert *-LmNativeBankStart=$2000,error,"Mac bank must retain exact 8 KiB footprint"','LmNativeSourceInit = LmNativeBankStart+$1f80','LmNativeSourcePlay = LmNativeBankStart','.popseg','']
 native=a.source/'src/mac_native_music.s';native.write_text('\n'.join(out))
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
 report=dict(source_NSF=str(NSF),source_sha256=SHA,coverage_sha256=hashlib.sha256(a.coverage.read_bytes()).hexdigest(),source_calls_per_track=18000,source_songs=[1,2,4,6,7,9,20,22,23],packed_pieces=pieces,source_unreferenced_adapter_hole=[0x9800,0x9a00],APU_intercepts=apu,relocated_operands=relocations,relocated_pointer_words=pointers,owned_history_bytes=288,new_RAM_bytes=0,new_CHR_bytes=0,PRG_bank=123,PRG_bytes=8192,source_generated_sha256=hashlib.sha256(native.read_bytes()).hexdigest(),preparer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),hardware_qualified=False)
 (a.source.parent/'preparation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k not in ['relocated_operands','APU_intercepts','relocated_pointer_words']}))
if __name__=='__main__':main()
