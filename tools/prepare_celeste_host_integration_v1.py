"""Sparse shared Celeste admissions. Mutable work in progress, no native claim."""
from pathlib import Path
import argparse,base64,difflib,hashlib,json,zlib
R=Path(__file__).resolve().parents[1];P=R/'build/celeste_host_preimages.json'
def edit(name,fn):
 p=R/name;raw=p.read_bytes();saved=json.loads(P.read_text()) if P.exists()else{}
 if name not in saved:
  saved[name]=dict(sha256=hashlib.sha256(raw).hexdigest(),zlib_base64=base64.b64encode(zlib.compress(raw,9)).decode());P.write_text(json.dumps(saved,indent=2)+'\n')
 nl='\r\n' if b'\r\n' in raw else '\n';s=raw.decode().replace('\r\n','\n');new=fn(s);assert new!=s,name;p.write_bytes(new.replace('\n',nl).encode())
def once(s,a,b):assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def phase1():
 edit('src/entrypoint.s',lambda s:once(s,'.include "sunny_integration.s"','.include "sunny_integration.s"\n.include "celeste_mario.s"\n.include "celeste_mario_host.s"'))
 def config(s):
  s=once(s,'CELESTE_UNUSED_CHR_MEM:','CELESTE_MARIO_CHR_MEM:')
  a='    NEW_ROSTER_NAMES: load=X5_NEW_51,type=ro,start=$b700,optional=yes;'
  return once(s,a,a+'\n    CELESTE_MARIO_HOST: load=X5_NEW_51,type=ro,start=$bb10,optional=yes;\n    CELESTE_MARIO_CORE: load=X5_NEW_62,type=ro,start=$b000,optional=yes;\n    CELESTE_MARIO_CHR: load=CELESTE_MARIO_CHR_MEM,type=ro,optional=yes;')
 edit('smb1base-mmc5-expanded.cfg',config)
 def resident(s):
  start=s.index('.proc CrossoverGraphicsBank\n');end=s.index('.endproc',start);old=s[start:end]
  body='''.proc CrossoverGraphicsBank
.if ::ENABLE_MMC5_EXPANDED
  ; Same resident68B capsule, no shared SMC/bank-A trip in IRQ/NMI.
  lda SelectedCharacter
  cmp #CHARACTER_PIT
  bcc Small
  jmp ExpandedGraphicsBank
Small:
  cmp #CHARACTER_BILL
  bcc First
  jmp RosterGraphicsBank
First:
  cmp #CHARACTER_SAMUS
  beq Samus
  cmp #CHARACTER_MEGAMAN
  beq Mega
  lda MarioVariant
  cmp #4
  beq Celeste
Native:
  clc                         ; old default's CMP#SAMUS returns carry0
  lda #.bank(MmMM_HAIR_STANDRight)|MMC5_PRG_ROM
  bne Publish
Samus:
  lda #.bank(SmP0_STANDRight)|MMC5_PRG_ROM
  bne Publish
Celeste:
  lda #.bank(CmArtStart)|MMC5_PRG_ROM
  bne Publish
Mega:
  lda ObjectMetasprite
  cmp #METASPRITE_SAMUS_BODY
  beq MegaBody
  bne Native
MegaBody:
  lda #.bank(SsMegaTHROWRight)|MMC5_PRG_ROM
Publish:
  BankPRGC a
  rts
  .res 68-(*-CrossoverGraphicsBank),$ea
  .assert *-CrossoverGraphicsBank=68,error,"Resident graphics ABI capsule"
.else
'''+old.split('\n',1)[1]+'.endif\n'
  return s[:start]+body+s[end:]
 edit('src/samus.s',resident)
 def dynamic(s):
  start=s.index('.proc MmDynamicPlayerPrgOwner\n');end=s.index('.endproc',start);p=s[start:end]
  p=once(p,'  lda SelectedCharacter\n  cmp #CHARACTER_MEGAMAN','  lda SelectedCharacter\n  beq Celeste\n  cmp #CHARACTER_MEGAMAN')
  p=once(p,'Done:\n  jmp HpNativePointerEnd','Done:\n  jmp HpNativePointerEnd\nCeleste:\n  lda MarioVariant\n  cmp #4\n  bne Done\n  lda #.bank(CmArtStart)|MMC5_PRG_ROM\n  bne Publish')
  return s[:start]+p+s[end:]
 edit('src/megaman_weapons.s',dynamic)
 print('phase1 source only; variant4 remains absent from menu pending qualification')
def phase2():
 def roster(s):
  # CmActive is published by the real menu resolver, preserved across areas,
  # and recreated by fresh-game init before the first private-owner dispatch.
  macro='''.macro NrCeleste Target
 php
 pha
 lda CmActive
 beq :+
 pla
 plp
 farcall Target,jmp
:pla
 plp
.endmacro
'''
  s=once(s,'.macro NrGate ',macro+'.macro NrGate ')
  s=once(s,'NrGate NrInjuryStatus,IcInjuryStatus,RcInjuryStatus,SunnyInjuryStatus,JnInjuryStatusDispatch','''.proc NrInjuryStatus
 NrCeleste CmHostInjuryStatus
 farcall NrLegacyInjuryStatus,jmp
.endproc
NrGate NrLegacyInjuryStatus,IcInjuryStatus,RcInjuryStatus,SunnyInjuryStatus,JnInjuryStatusDispatch''')
  for name,target in [('NrPickup','CmHostPickup'),('NrUi','CmHostUi'),('NrStatusName','CmHostStatusName'),('NrColors','CmHostColors')]:
   s=once(s,'.proc '+name+'\n','.proc '+name+'\n NrCeleste '+target+'\n')
  for name,lab in [('NrReset','Own'),('NrPrepare','Own'),('NrRise','Native'),('NrPrivate','Native'),('NrPickupCollision','Own')]:
   a='.proc '+name+'\n php\n pha\n lda SelectedCharacter'
   b='.proc '+name+'\n php\n pha\n lda CmActive\n bne '+lab+'\n lda SelectedCharacter'
   s=once(s,a,b)
  s=once(s,' sta InvPickupOwner,x',' sta InvPickupOwner,x') if False else s
  # Prepare must publish the actual ID0 rather than the boolean owner tag.
  a='.proc NrPrepare';i=s.index(a);j=s.index('.endproc',i)
  p=s[i:j].replace('Own:\n sta InvPickupOwner,x','Own:\n lda SelectedCharacter\n sta InvPickupOwner,x');s=s[:i]+p+s[j:]
  a='.proc NrReset';i=s.index(a);j=s.index('.endproc',i);p=s[i:j]
  p=once(p,' lda SelectedCharacter\n cmp #CHARACTER_SUNNY\n beq Sunny',' lda CmActive\n beq :+\n farcall CmHostEnsure,jmp\n:\n lda SelectedCharacter\n cmp #CHARACTER_SUNNY\n beq Sunny');s=s[:i]+p+s[j:]
  s=once(s,' sta RcMarker                 ; initialize lazily, preserve selected owner\'s RAM',' sta RcMarker                 ; initialize lazily, preserve selected owner\'s RAM\n sta CmMarker\n sta CmActive')
  s=once(s,' farcall SunnyGlobalInit\n rts\n.endproc',' farcall SunnyGlobalInit\n farcall CmHostFresh,jmp\n.endproc')
  s=once(s,'.proc NrMenuToggle\n','.proc NrMenuToggle\n lda CrossoverMenuIndex\n bne NrOtherToggle\n lda CrossoverMenuPressed\n and #Select_Button\n beq NrOtherToggle\n lda MarioVariant\n beq NrToLuigi\n cmp #1\n beq NrToCeleste\n lda #0\n beq NrMarioPublish\nNrToLuigi:lda #1\n bne NrMarioPublish\nNrToCeleste:lda #4\nNrMarioPublish:sta MarioVariant\n sec\n rts\nNrOtherToggle:\n')
  s=once(s,'.proc NrQueueSelectName\n  lda SelectedCharacter','.proc NrQueueSelectName\n  lda CmActive\n  beq :+\n  lda #44\n  jmp NameIndex\n:\n  lda SelectedCharacter')
  s=once(s,'"     SUNNY      "','"     SUNNY      "," CELESTE MARIO  "')
  s=s.replace('.assert * <= $b000,lderror,"Roster dispatcher overlaps Rogue Dawn reservation"','.assert * <= $ae00,lderror,"Roster dispatcher overlaps Rogue auxiliary reservation"')
  return s
 edit('src/new_roster_dispatch.s',roster)
 def player(s):
  i=s.index('CrossoverMarioMovement:\n');j=s.index('CrossoverGuestDispatch:',i)
  old=s[i:j]
  # Genuine old dry labels move with their code to the host segment.
  host=old.replace('CrossoverMarioMovement:','CmHostMarioMovement:').replace('  lda SwimmingFlag','  lda CmActive\n  beq :+\n  farcall CmHostMovement,jmp\n:\n  lda SwimmingFlag',1)
  host=host.replace('jne CrossoverVanillaMovement','jne CmHostVanilla').replace('  jsr MarioSourceMovement\n  rts','  farcall MarioSourceMovement,jmp').replace('  jmp CrossoverVanillaMovement','  farcall CrossoverVanillaMovement,jmp')
  host+='CmHostVanilla:\n  farcall CrossoverVanillaMovement,jmp\n'
  s=s[:i]+'.if ::ENABLE_MMC5_EXPANDED\n  farcall CmHostMarioMovement,jmp\n.else\n'+old+'.endif\n'+s[j:]
  # Keep the public entry genuine; only its old private dispatch labels move.
  s=s.replace('.if ::ENABLE_MMC5_EXPANDED\n  farcall CmHostMarioMovement,jmp','.if ::ENABLE_MMC5_EXPANDED\nCrossoverMarioMovement:\n  farcall CmHostMarioMovement,jmp',1)
  i=s.index('  lda TimerControl    ;check master timer control',s.index('PlayerChangeSize:'));j=s.index('\n;-------------------------------------------------------------------------------------',i)
  tail=s[i:j]
  s=s[:i]+'.if ::ENABLE_MMC5_EXPANDED\n.pushseg\n.segment "CELESTE_MARIO_HOST"\n'+tail+'\n.popseg\n.else\n'+tail+'\n.endif\n'+s[j:]
  a='GuestDeathGraphicsReady:\n  lda SelectedCharacter'
  s=once(s,a,'GuestDeathGraphicsReady:\n.if ::ENABLE_MMC5_EXPANDED\n  lda CmActive\n  beq :+\n  farcall CmHostGraphics,jmp\n:\n.endif\n  lda SelectedCharacter')
  edit('src/celeste_mario_host.s',lambda t:once(t,'.proc CmHostMovement\n',host+'\n.proc CmHostMovement\n'))
  return s
 edit('src/player.s',player)
 def post(s):
  a='.proc MegaManSlideSmallGap\n'
  s=once(s,a,a+'.if ::ENABLE_MMC5_EXPANDED\n  lda CmActive\n  beq :+\n  farcall CmHostAfterBG,jmp\n:\n.endif\n')
  # Real short branches reclaim only unexecuted long-branch instruction bytes.
  i=s.index('.proc MegaManSlideSmallGap\n');j=s.index('.pushseg',i);p=s[i:j]
  for old,new in [('jeq Done','beq Done'),('jne Done','bne Done'),('jcc Done','bcc Done')]:
   p=p.replace('  '+old,' .if ::ENABLE_MMC5_EXPANDED\n  '+new+'\n .else\n  '+old+'\n .endif')
  return s[:i]+p+s[j:]
 edit('src/megaman_physics.s',post)
 def env(s):
  return once(s,'NativeHead:\n  lda #1','NativeHead:\n.if ::ENABLE_MMC5_EXPANDED\n  lda CmActive\n  beq :+\n  sta SmCeilingHit\n:\n.endif\n  lda #1')
 edit('src/megaman_environment.s',env)
 def object_(s):
  i=s.index('CheckAttackButton:\n',s.index('.proc ProcFireball_Bubble'));j=s.index('\nProcFireballs:',i);old=s[i:j]
  host=old.replace('ProcFireballs','CmHostFireballs')+'\nCmHostFireballs:\n  farcall ProcFireballs,jmp\n'
  s=s[:i]+'.if ::ENABLE_MMC5_EXPANDED\n  farcall CheckAttackButton,jmp\n.pushseg\n.segment "CELESTE_MARIO_HOST"\n'+host+'.popseg\n.else\n'+old+'\n.endif\n'+s[j:]
  a='  lda PlayerStatus           ;check player\'s status\n  cmp #$02\n  bcc ProcAirBubbles'
  s=once(s,a,'.if ::ENABLE_MMC5_EXPANDED\n  lda CmActive\n  beq :+\n  farcall CmHostDashTail,jmp\n:\n.endif\n'+a)
  return s
 edit('src/object.s',object_)
 def menu(s):
  i=s.index('.proc MenuResolveCharacter\n');j=s.index('.endproc',i);old=s[i:j]
  return s[:i]+'.proc MenuResolveCharacter\n.if ::ENABLE_MMC5_EXPANDED\n  farcall CmHostResolveCharacter,jmp\n  .res 34-(*-MenuResolveCharacter),$ea\n.else\n'+old.split('\n',1)[1]+'.endif\n'+s[j:]
 edit('src/character_select.s',menu)
 def injury(s):
  return once(s,'            farcall MarioSourceInjuryStart',' .if ::ENABLE_MMC5_EXPANDED\n            farcall CmHostMarioInjury\n .else\n            farcall MarioSourceInjuryStart\n .endif')
 edit('src/collision.s',injury)
 def bounce(s):
  for name,target in [('X5SpringDispatch','CmHostSpring'),('X5StompDispatch','CmHostStomp')]:
   a='.proc '+name+'\n  php\n  pha\n'
   s=once(s,a,a+'  lda CmActive\n  beq :+\n  pla\n  plp\n  farcall '+target+',jmp\n:\n')
  return s
 edit('src/x5_bounce.s',bounce)
 edit('src/cheats_four.s',lambda s:once(s,'Mario:lda PlayerStatus','Mario:\n lda CmActive\n beq :+\n farcall CmHostFullPower,jmp\n:\n lda PlayerStatus'))
 print('phase2 applied; not built/qualified')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--phase1',action='store_true');p.add_argument('--phase2',action='store_true');a=p.parse_args()
 if a.phase1:phase1()
 if a.phase2:phase2()
