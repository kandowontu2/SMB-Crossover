"""Apply the authorized Sunny shared admissions once; sparse flat preimages."""
from pathlib import Path
import base64,hashlib,json
R=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 names=['src/new_roster_dispatch.s','src/character_select.s','src/entrypoint.s','src/mmc5.s',
        'src/player.s','src/object.s','smb1base-mmc5-expanded.cfg']
 out=R/'build/sunny_integration_preimages.json'
 assert not out.exists(),'Never reapply over a later source state'
 out.write_text(json.dumps({n:dict(sha256=sha(R/n),base64=base64.b64encode((R/n).read_bytes()).decode()) for n in names},indent=2)+'\n')
 def edit(n,fn):
  p=R/n;raw=p.read_bytes();text=raw.decode();newline='\r\n' if b'\r\n' in raw else '\n'
  text=text.replace('\r\n','\n');new=fn(text)
  p.write_bytes(new.replace('\n',newline).encode())
 def once(s,old,new):
  assert s.count(old)==1,(old,s.count(old));return s.replace(old,new)
 def dispatch(s):
  s=once(s,'.macro NrGate Name,Ice,City,Legacy','.macro NrGate Name,Ice,City,Sunny,Legacy')
  s=once(s,' beq ToCity\n pla',' beq ToCity\n cmp #CHARACTER_SUNNY\n beq ToSunny\n pla')
  s=once(s,' farcall City,jmp\n.endproc\n.endmacro',' farcall City,jmp\nToSunny:\n pla\n plp\n farcall Sunny,jmp\n.endproc\n.endmacro')
  targets={'Movement':'SunnyNativeMovement','Graphics':'SunnyGraphicsIntegrated','Draw':'SunnyDraw',
   'Portrait':'SunnyPortrait','Weapons':'SunnyWeapons','Injury':'SunnyInjuryStart',
   'InjuryStatus':'SunnyInjuryStatus','DeathStart':'SunnyDeathStart','Death':'SunnyNativeDeath',
   'Visible':'SunnyVisible','Head':'SunnyHead'}
  lines=s.splitlines()
  for i,line in enumerate(lines):
   if line.startswith('NrGate Nr'):
    parts=line.split(',');key=parts[0].split('NrGate Nr')[1];parts.insert(-1,targets[key]);lines[i]=','.join(parts)
  s='\n'.join(lines)+'\n'
  # Same native/owned branch for simple non-inventory admissions.
  for proc,label in [('NrReset','Own'),('NrPrepare','Own'),('NrRise','Native'),
      ('NrPrivate','Native'),('NrPickupCollision','Own'),('NrSide','Native'),('NrWorldPaletteIndex','Native')]:
   a=s.index('.proc '+proc+'\n');z=s.index('.endproc',a);part=s[a:z]
   anchor=' cmp #CHARACTER_RIVER_CITY\n beq '+label+'\n'
   part=once(part,anchor,anchor+' cmp #CHARACTER_SUNNY\n beq '+label+'\n')
   s=s[:a]+part+s[z:]
  a=s.index('.proc NrReset\n');z=s.index('.endproc',a);part=s[a:z]
  part=once(part,' lda SelectedCharacter\n cmp #CHARACTER_ICE_CLIMBERS\n bne City',
      ' lda SelectedCharacter\n cmp #CHARACTER_SUNNY\n beq Sunny\n cmp #CHARACTER_ICE_CLIMBERS\n bne City')
  part += 'Sunny:farcall SunnyReset,jmp\n';s=s[:a]+part+s[z:]
  for proc,target in [('NrBody','SunnyBody'),('NrPickup','SunnyCollectIntegrated'),
                      ('NrUi','SunnyUi'),('NrStatusName','SunnyStatusName'),('NrFullPower','SunnyFullPower')]:
   a=s.index('.proc '+proc+'\n');z=s.index('.endproc',a);part=s[a:z]
   anchor=' lda SelectedCharacter\n';part=once(part,anchor,anchor+' cmp #CHARACTER_SUNNY\n beq Sunny\n')
   part += 'Sunny:\n'+(' pla\n plp\n' if proc in ['NrBody','NrUi','NrStatusName'] else '')+' farcall '+target+',jmp\n'
   s=s[:a]+part+s[z:]
  for proc,target in [('NrAdder','SunnyAdder'),('NrBox','SunnyBox')]:
   a=s.index('.proc '+proc+'\n');z=s.index('.endproc',a);part=s[a:z]
   anchor=' cmp #CHARACTER_RIVER_CITY\n beq City\n';part=once(part,anchor,anchor+' cmp #CHARACTER_SUNNY\n beq Sunny\n')
   part+='Sunny:pla\n plp\n farcall '+target+',jmp\n';s=s[:a]+part+s[z:]
  s=once(s,' farcall IcGlobalInit,jmp',' farcall IcGlobalInit\n farcall SunnyGlobalInit,jmp')
  a=s.index('.proc NrFreshGameInit\n');z=s.index('.endproc',a);part=s[a:z]
  part=once(part,' sta RcMarker\n rts',' sta RcMarker\n farcall SunnyGlobalInit\n rts');s=s[:a]+part+s[z:]
  a=s.index('.proc NrColors\n');z=s.index('.endproc',a);part=s[a:z]
  anchor=' cmp #CHARACTER_RIVER_CITY\n beq Own\n';part=once(part,anchor,anchor+' cmp #CHARACTER_SUNNY\n beq Own\n')
  part=once(part,' lda SelectedCharacter\n cmp #CHARACTER_ICE_CLIMBERS\n bne City',
    ' lda SelectedCharacter\n cmp #CHARACTER_SUNNY\n beq Sunny\n cmp #CHARACTER_ICE_CLIMBERS\n bne City')
  part+='Sunny:farcall SunnyColorsIntegrated,jmp\n';s=s[:a]+part+s[z:]
  s=once(s,'.proc NrQueueSelectName\n','.segment "NEW_ROSTER_NAMES"\n.proc NrQueueSelectName\n')
  s=once(s,'  lda SelectedCharacter\n.if ::ENABLE_MMC5_EXPANDED\n  cmp #CHARACTER_ICE_CLIMBERS',
    '  lda SelectedCharacter\n.if ::ENABLE_MMC5_EXPANDED\n  cmp #CHARACTER_SUNNY\n  bne SunnyOtherName\n  lda #43\n  jmp NameIndex\nSunnyOtherName:\n  cmp #CHARACTER_ICE_CLIMBERS')
  s=once(s,'  .byte "   DOC LOUIS    ","   MIKE TYSON   "','  .byte "   DOC LOUIS    ","   MIKE TYSON   ","     SUNNY      "')
  s=once(s,'.assert * <= $b000,lderror,"Roster dispatcher overlaps Rogue Dawn reservation"',
     '.segment "NEW_ROSTER_GATE"\n.assert * <= $b000,lderror,"Roster dispatcher overlaps Rogue Dawn reservation"')
  return s
 edit('src/new_roster_dispatch.s',dispatch)
 def entry(s):
  s=once(s,'.include "ice_climbers_state.inc"','.include "ice_climbers_state.inc"\n.include "sunny_state.inc"')
  return once(s,'.include "new_roster_dispatch.s"','.include "new_roster_dispatch.s"\n.include "sunny.s"\n.include "sunny_integration.s"')
 edit('src/entrypoint.s',entry)
 def player(s):
  for label in ['PlayerChangeSize:','PlayerFireFlower:']:
   at=s.index(label);end=s.index('\n  lda TimerControl',at);part=s[at:end]
   part=once(part,'.if ::ENABLE_CROSSOVER\n  lda SelectedCharacter',
      '.if ::ENABLE_CROSSOVER\n.if ::ENABLE_MMC5_EXPANDED\n  lda SelectedCharacter\n  cmp #CHARACTER_SUNNY\n  bne :+\n  farcall SunnyPowerupUpdate,jmp\n:\n.endif\n  lda SelectedCharacter')
   s=s[:at]+part+s[end:]
  return s
 edit('src/player.s',player)
 edit('src/object.s',lambda s:once(s,'RemainingBatchDone:\n  lda SelectedCharacter',
    'RemainingBatchDone:\n.if ::ENABLE_MMC5_EXPANDED\n  lda SelectedCharacter\n  cmp #CHARACTER_SUNNY\n  bne :+\n  farcall SunnyNativeWeaponTail,jmp\n:\n.endif\n  lda SelectedCharacter'))
 def mmc(s):
  s=once(s,'(.bank(RcArtStart))|MMC5_PRG_ROM\n::Cv3ResidentRosterBank:',
    '(.bank(RcArtStart))|MMC5_PRG_ROM,$ff,(94)|MMC5_PRG_ROM\n::Cv3ResidentRosterBank:')
  return once(s,'::Cv3ResidentRosterBank:\n lda SelectedCharacter\n cmp #CHARACTER_SIMON',
      '::Cv3ResidentRosterBank:\n ; Sole RosterGraphicsBank caller has X=SelectedCharacter-CHARACTER_BILL.\n cpx #CHARACTER_SIMON-CHARACTER_BILL')
 edit('src/mmc5.s',mmc)
 def cfg(s):
  s=once(s,'    MIKE_UNUSED_CHR_MEM: start=$b5000,size=$8000,type=ro,fill=yes,file=%O,fillval=$00;',
     '    SUNNY_CHR_MEM: start=$b5000,size=$4000,type=ro,fill=yes,file=%O,fillval=$00;\n    CELESTE_UNUSED_CHR_MEM: start=$b9000,size=$4000,type=ro,fill=yes,file=%O,fillval=$00;')
  anchor='    NEW_ROSTER_GATE: load=X5_NEW_7C,type=ro,start=$a000,optional=yes;'
  return once(s,anchor,anchor+'\n    SUNNY_CORE: load=X5_NEW_51,type=ro,start=$b200,optional=yes;\n    SUNNY_ART: load=X5_NEW_5E,type=ro,start=$ce00,optional=yes;\n    SUNNY_CHR: load=SUNNY_CHR_MEM,type=ro,optional=yes;\n    NEW_ROSTER_NAMES: load=X5_NEW_51,type=ro,start=$b700,optional=yes;')
 edit('smb1base-mmc5-expanded.cfg',cfg)
 print(json.dumps(dict(applied=True,preimages=str(out),changed={n:sha(R/n) for n in names})))

if __name__=='__main__':main()
