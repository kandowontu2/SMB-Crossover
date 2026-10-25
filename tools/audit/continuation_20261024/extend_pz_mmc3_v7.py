"""Private MMC3 storage/banking repair; never installed by this module."""
from pathlib import Path
import re,json

def once(t,a,b):
 assert t.count(a)==1,(a,t.count(a));return t.replace(a,b)

def apply(source):
 # Retain the original driver and direct hardware bank publication. Its new
 # resident allocation avoids both the full C-bank tail and foreground SMC.
 p=source/'src/gradius_audio.s';t=p.read_text()
 a='.assert *-VgAudioDispatch=23,error,"Native audio fits the existing 24-byte C-bank tail"'
 t=once(t,a,'.if ::MAPPER_MMC3\n.assert *-VgAudioDispatch<=48,error,"Resident MMC3 native-audio dispatch allocation"\n.else\n'+a+'\n.endif');p.write_text(t)
 p=source/'smb1base-mmc3-oversized.cfg';t=p.read_text()
 t=once(t,'VG_AUDIO_DISPATCH:load=XG_AUDIO_MEM,type=ro;','VG_AUDIO_DISPATCH:load=PRGLow,type=ro;')
 t=once(t,'BILL_BODY_COLD: load=PRGA_09, type=ro,','BILL_BODY_COLD: load=M3_FREE_E6, type=ro,')
 t=once(t,'SAMUS_CROUCH_WATER: load = PRGFix,','SAMUS_CROUCH_WATER: load = PRGLow,');p.write_text(t)

 # These two native-audio families never execute the expanded LZ decoder.
 # Keep their complete, contiguous gameplay/pause overlays in its inactive
 # history, away from live native audio. Menu alternatives remain resident.
 moved=[]
 for p in(source/'src').iterdir():
  if not p.is_file()or not p.name.startswith(('zelda2','cv3'))or p.suffix not in('.s','.inc'):continue
  t=p.read_text()
  def remap(m):
   n=int(m[1],16)
   if n>=0x5fe0:return m[0]
   moved.append(dict(file=p.name,old=n,new_offset=n-0x5c00))
   return 'XgLzHistory+$%03x'%(n-0x5c00)
  t=re.sub(r'M3State_(5[c-f][0-9a-f]{2})',remap,t,flags=re.I)
  if p.name=='zelda2_link_state.inc':t=once(t,'Z2TransientEnd=RgAudioRam+$80','Z2TransientEnd=XgLzHistory+$280')
  p.write_text(t)
 p=source/'src/x5_profiles.s';t=p.read_text()
 a='  lda SelectedCharacter\n  cmp #CHARACTER_MEGAMAN\n'
 b='''  lda SelectedCharacter
  cmp #CHARACTER_LINK
  beq NativeWideClear
  cmp #CHARACTER_SIMON
  bne NativeWideDone
NativeWideClear:
  lda #0
  tax
NativeWideClearLoop:
  sta XgLzHistory,x
  sta XgLzHistory+$100,x
  sta XgLzHistory+$200,x
  sta XgLzHistory+$300,x
  inx
  bne NativeWideClearLoop
NativeWideDone:
  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
'''
 t=once(t,a,b);p.write_text(t)

 # The historical fixed73c5 control range now contains helper-platform state.
 # Only one direct-body mode byte is used by the actual MMC3 implementation.
 p=source/'src/entrypoint.s';t=p.read_text()
 def stable(m):
  n=int(m[1],16);assert n<0x5ff8,(hex(n),'Review new persistent state')
  return f'M3State_{n:04x}=HpRamEnd+${n-0x5fe0:02x}'
 t=re.sub(r'M3State_(5f[e-f][0-9a-f])=[^\n]+',stable,t);p.write_text(t)

 p=source/'src/mmc3_oversized.s';t=p.read_text()
 t=once(t,'X5ChrMode=$73e0','X5ChrMode=HpRamEnd+24')
 t=once(t,'X5SpecialChrUpper=$73ec','X5SpecialChrUpper=HpRamEnd+25')
 t=once(t,'X5HudChrUpper=$73ed','X5HudChrUpper=HpRamEnd+26')
 t=once(t,'X5WideChrActive=$73ee','X5WideChrActive=HpRamEnd+27\n.assert HpRamEnd+28<=XgLzHistory,error,"MMC3 controls stay in the actual alignment gap"')
 t=once(t,'M3CacheProfile=$73db','M3CacheProfile=RgAudioCpuZp+158')
 t=once(t,'M3CacheLoads=$73dc','M3CacheLoads=RgAudioCpuZp+159')
 a=t.index('M3Masks=');b=t.index('M3CacheBase=',a)
 t=t[:a]+'''M3Masks=RgAudioZp+24             ; first128 key bytes, native prefixes untouched
M3MasksHigh=RgAudioCpuZp+24       ; final16 key bytes
M3Wanted=RgAudioCpuZp+40         ;8key bytes plus4 expected page-bit masks
M3Map=RgAudioCpuZp+56            ;64 source-pair assignments
M3Queue=RgAudioCpuZp+120         ;11 upload pair indices
M3Pending=RgAudioCpuZp+131
M3Cursor=RgAudioCpuZp+132
M3Victim=RgAudioCpuZp+133
M3Target=RgAudioCpuZp+134
M3Count=RgAudioCpuZp+135
M3HardwareBody=RgAudioCpuZp+136
M3Scan=RgAudioCpuZp+137
M3DrawSlot=RgAudioCpuZp+138
M3HardwareSpecial=RgAudioCpuZp+139
M3PageLo=RgAudioCpuZp+140         ;18entries, source page low byte
M3PageHigh=RgAudioZp+152          ;5 packed bytes,2 high bits per entry
M3RequestedLo=RgAudioZp+157
M3RequestedHi=RgAudioZp+158
M3RequestedPair=RgAudioZp+159
.assert M3PageLo+18<=M3CacheProfile,error,"Page directory does not touch controls"
.assert M3RequestedPair<RgAudioCpuZp,error,"Cache stays in inactive audio padding"
.macro M3ReadMask
 .local High,Done
 cpx #128
 bcs High
 lda M3Masks,x
 jmp Done
High:lda M3MasksHigh-128,x
Done:
.endmacro
.macro M3WriteMask
 .local High,Done
 cpx #128
 bcs High
 sta M3Masks,x
 jmp Done
High:sta M3MasksHigh-128,x
Done:
.endmacro
'''+t[b:]
 t=once(t,'X5ClearChrModes:\n lda #0\n ldx #11','X5ClearChrModes:\n lda #0\n ldx #0')
 # Body pages for the actual newer alternatives, all within the80page window.
 t=once(t,'M3ChooseProfile:\n lda SelectedCharacter','''M3ChooseProfile:
 lda SelectedCharacter
 cmp #9
 bne CheckShipAlternate
 lda RlVariant
 jeq LegacyProfile
 lda #14
 rts
CheckShipAlternate:
 cmp #18
 bne PriorProfiles
 lda VvVariant
 beq BaseShip
 cmp #4
 jcs LegacyProfile
 clc
 adc #14
 rts
BaseShip:lda #5
 rts
PriorProfiles:lda SelectedCharacter''')
 for name,addition in [('M3FirstLo',',<304,<832,<896,<960'),('M3FamilyLo',',<304,<832,<896,<960'),('M3FamilyHi',',>304,>832,>896,>960'),('M3FamilyCount',',76,64,64,64'),('M3SpecialLo',',<366,<834,<898,<962'),('M3SpecialHi',',>366,>834,>898,>962')]:
  pattern=r'('+name+r':\s*\.byte[^\n]+)';assert len(re.findall(pattern,t))==1
  t=re.sub(pattern,lambda m:m[1]+addition,t)
 # A changed auxiliary pool is part of the cache identity, not merely its tile
 # mask. All current Roll/Parodius pools publish consecutive1K pages6 and7.
 t=once(t,'X5SetPhysicalChr:\n cpy #5','''X5SetPhysicalChr:
 cpy #6
 bne NotAuxiliary
 sta M3RequestedLo
 stx M3RequestedHi
 lda #1
 sta M3RequestedPair
 rts
NotAuxiliary:
 cpy #7
 beq IgnorePartner
 cpy #5''')
 t=once(t,'X5SetSpecialChr:\n ;','X5SetSpecialChr:\n sta M3RequestedLo\n stx M3RequestedHi\n ;')
 t=once(t,' stx M3CacheProfile\n inc M3CacheLoads',''' stx M3CacheProfile
 lda M3SpecialLo,x
 sta M3RequestedLo
 lda M3SpecialHi,x
 sta M3RequestedHi
 lda #0
 sta M3RequestedPair
 inc M3CacheLoads''')
 t=once(t,' ldx #143\nClearMasks:sta M3Masks,x\n dex\n cpx #$ff\n bne ClearMasks',''' ldx #127
ClearMasks:sta M3Masks,x
 dex
 cpx #$ff
 bne ClearMasks
 ldx #15
ClearHighMasks:sta M3MasksHigh,x
 dex
 cpx #$ff
 bne ClearHighMasks''')
 t=once(t,'CacheSearch:\n stx M3Target\n txa','CacheSearch:\n stx M3Target\n jsr M3PageMatches\n bcc Miss\n ldx M3Target\n txa')
 t=once(t,' ldx R0\n lda M3Masks,x',' ldx R0\n M3ReadMask')
 t=once(t,' lda M3Wanted,y\n sta M3Masks,x',' lda M3Wanted,y\n M3WriteMask')
 t=once(t,' bcc SaveKey\n lda #0',' bcc SaveKey\n jsr M3PageStore\n lda #0')
 t=once(t,'Search:\n ; Canonical','Search:\n jsr M3PageExpected\n ; Canonical')
 t=once(t,' ldy M3CacheProfile\n lda M3SpecialLo,y\n sta R0\n lda M3SpecialHi,y',' lda M3RequestedLo\n sta R0\n lda M3RequestedHi')
 # No memory beyond the two160byte slabs is used. Their first24bytes remain
 # exclusive to native audio; only foreground cache lookup pays this key work.
 insert='''
M3PageExpected:
 lda M3RequestedHi
 and #3
 sta M3Wanted+8
 asl
 asl
 sta M3Wanted+9
 asl
 asl
 sta M3Wanted+10
 asl
 asl
 sta M3Wanted+11
 rts
M3PageMatches:
 lda M3PageLo,x
 cmp M3RequestedLo
 bne M3PageNo
 txa
 and #3
 tay
 txa
 lsr
 lsr
 tax
 lda M3PageHigh,x
 eor M3Wanted+8,y
 and M3PageMasks,y
 bne M3PageNo
 sec
 rts
M3PageNo:clc
 rts
M3PageStore:
 ldx M3Target
 lda M3RequestedLo
 sta M3PageLo,x
 txa
 and #3
 tay
 txa
 lsr
 lsr
 tax
 lda M3PageHigh,x
 and M3PageInverse,y
 ora M3Wanted+8,y
 sta M3PageHigh,x
 rts
M3PageMasks:.byte 3,12,48,192
M3PageInverse:.byte 252,243,207,63
'''
 t=once(t,'M3Bits:.byte 1,2,4,8,16,32,64,128',insert+'\nM3Bits:.byte 1,2,4,8,16,32,64,128');p.write_text(t)
 (source.parent/'private-changes-v5.json').write_text(json.dumps(dict(native_wide_state_mappings=moved,new_RAM_bytes=0,cache_entries=18,native_audio_prefix_preserved=24,cache_source_page_bits=10,source_ownership='Zelda II/CV3 use the inactive expanded history; graphics cache uses only unused tails of native audio ZP images; resident controls append after actual helper state.'),indent=2))

