"""One sparse, uninstalled Mega/Proto body-reservation experiment on8487.

No source/runtime clone, native worker, NMI work, RAM allocation or primary
write. Build leaves are deliberately flat and reusable, not evidence forests.
"""
from pathlib import Path
import difflib,hashlib,json,re,subprocess,sys,traceback
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_audio_fallback_oc import qualified

R=Path(__file__).resolve().parents[2];B=R/'build'
BASE=B/'smb-crossover-mmc5-expanded.nes'
EXPECTED='8487c439ded9bc6274e1dc8f8e051494fa96ee518553d9c2f382eccf2e71d0e6'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,v:Path(p).write_text(json.dumps(v,indent=2)+'\n')

def replace(text,old,new):
 assert text.count(old)==1,old
 return text.replace(old,new)

def build_controls():
 q=json.loads((B/'mm_body_reserve_result.json').read_text());assert q['passed']and sha(BASE)==EXPECTED
 original=q['build_command'];clean=[];i=0
 while i<len(original):
  if original[i]=='-m':i+=2;continue
  clean.append(original[i]);i+=1
 rows=[]
 for mode in ['canonical','mmc5','mmc3']:
  cmd=[v.replace(str(B/'mm_body_reserve.nes'),str(B/'mm_body_control.nes')).replace(str(B/'mm_body_reserve.lbl'),str(B/'mm_body_control.lbl')).replace(str(B/'mm_body_reserve.dbg'),str(B/'mm_body_control.dbg'))for v in clean]
  assert not any(str(B/('mm_body_reserve.'+ext))in v for v in cmd for ext in ['nes','dbg','lbl']),('Bound candidate overwrite',cmd)
  if mode!='canonical':
   cmd=[v.replace(str(B/'mm_body_reserve.cfg'),str(R/'smb1base.cfg'))for v in cmd]
   for i,v in enumerate(cmd):
    if v=='ENABLE_MMC5_EXPANDED=1':cmd[i]='ENABLE_MMC5_EXPANDED=0'
    elif v.startswith('MAPPER_MMC5='):cmd[i]='MAPPER_MMC5='+str(int(mode=='mmc5'))
    elif v.startswith('MAPPER_MMC3='):cmd[i]='MAPPER_MMC3='+str(int(mode=='mmc3'))
  p=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
  (B/'mm_body_control.log').write_text(p.stdout+p.stderr)
  assert p.returncode==0,(mode,p.stdout,p.stderr)
  if mode=='canonical':
   sys.path.insert(0,str(R/'tools'));from prepare_cv3_dmc_mirror import prepare
   prepare(R,B/'mm_body_control.nes')
  expected=q['candidate']if mode=='canonical'else {'mmc5':'f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833','mmc3':'d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'}[mode]
  actual=sha(B/'mm_body_control.nes');assert actual==expected,(mode,actual,expected)
  rows.append(dict(mode=mode,actual=actual,command=cmd))
 put(B/'mm_body_reserve_build_controls.json',dict(passed=True,rows=rows,native=False,new_directories=0,reused_output='build/mm_body_control.nes',tool_sha256=sha(__file__)))
 print(json.dumps(dict(passed=True,builds=[{k:r[k]for k in ['mode','actual']}for r in rows]),indent=2))

def main():
 proof=dict(passed=False,native=False,installed=False,new_directories=0,new_RAM=0)
 try:
  assert sha(BASE)==EXPECTED
  old=scoped_load(BASE);raw=old['raw']
  # Actual emitted ownership, not remembered highwater. Neither pool touches
  # adopted Bass71/72/78/89 or the basic-shot helper at66:B9A8.
  pools=[(4,0xbf33,88),(66,0xb9c0,400)]
  for bank,start,size in pools:
   at=16+bank*8192+(start&8191)
   assert raw[at:at+size]==b'\xff'*size,(bank,start)
   for seg in old['segs'].values():
    if 'ooffs' not in seg:continue
    s,n=int(seg['ooffs'],0),int(seg['size'],0)
    assert not(n and s<at+size and at<s+n),(bank,start,seg)
  names=['src/metasprite_engine.s','src/megaman_weapons.s','src/sprite_render.s','src/level_variants.s']
  originals={p:(R/p).read_text()for p in names}
  bindings={p:sha(R/p)for p in names+['src/entrypoint.s','smb1base-mmc5-expanded.cfg','src/ryu_platform.s']}
  e=originals[names[0]]
  e=replace(e,'''  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
  beq RotateGuestOAM
  cmp #CHARACTER_BILL
  bcs RotateGuestOAM
  lda #0
  sta GuestOamRotationActive
  jmp ClearReservedPlayer
RotateGuestOAM:''','''.if ::ENABLE_MMC5_EXPANDED
  lda SelectedCharacter
  cmp #CHARACTER_BILL
  bcs RotateGuestOAM
  lsr
  bcc MmReserveNonMega
  jmp MmReserveBegin
MmReserveNonMega:
  lsr
  sta GuestOamRotationActive
  jmp ClearReservedPlayer
.else
  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
  beq RotateGuestOAM
  cmp #CHARACTER_BILL
  bcs RotateGuestOAM
  lda #0
  sta GuestOamRotationActive
  jmp ClearReservedPlayer
.endif
RotateGuestOAM:''')
  e=replace(e,'  ; Give weapons the first OAM slots.','''.if ::ENABLE_MMC5_EXPANDED
  ldx #0
::MmReserveClear:
.endif
  ; Give weapons the first OAM slots.''')
  e=replace(e,''' .endrepeat
  ldx #0
  stx CurrentOAMOffset''',''' .endrepeat
.if !::ENABLE_MMC5_EXPANDED
  ldx #0
.endif
  stx CurrentOAMOffset''')
  e=replace(e,'''  jsr MegaManDrawShots
  lda CurrentOAMOffset
  sta RgOamPlayerStart
::MegaManProjectileOamReady:
 .if ::ENABLE_MMC5_EXPANDED
  jsr ProtoOamReservation
 .else
  jsr PlayerOAMReservation
 .endif
  clc
  adc CurrentOAMOffset
  sta CurrentOAMOffset
  jmp InitObjectLoop
RosterShots:''','''  jsr MegaManDrawShots
.if ::ENABLE_MMC5_EXPANDED
  jsr MmReserveFinish
  jmp InitObjectLoop
  .res 13,$ea
.else
  lda CurrentOAMOffset
  sta RgOamPlayerStart
::MegaManProjectileOamReady:
  jsr PlayerOAMReservation
  clc
  adc CurrentOAMOffset
  sta CurrentOAMOffset
  jmp InitObjectLoop
.endif
RosterShots:''')
  e=replace(e,'''  sta Sprite_Y_Position,x
  cpx #0
  bne ClearPlayerOAM

InitObjectLoop:''','''  sta Sprite_Y_Position,x
.if !::ENABLE_MMC5_EXPANDED
  cpx #0
.endif
  bne ClearPlayerOAM
.if ::ENABLE_MMC5_EXPANDED
  sec
.endif

InitObjectLoop:''')
  e=replace(e,'''    lda GuestOamRotationActive
    beq LegacyTailClear
      ; The full ring was hidden at entry; no linear tail clear is needed.
      pla''','''    lda GuestOamRotationActive
.if ::ENABLE_MMC5_EXPANDED
    bmi MmReserveExitBranch
.endif
    beq LegacyTailClear
      ; The full ring was hidden at entry; no linear tail clear is needed.
::MmReserveRosterTail:
      pla''')
  e=replace(e,''' .res 17,$ea
::WorldFirebarAdmissionDone:
 rts
 .assert *-WorldFirebarDrawAdmission=39,lderror,"Late world admission span"''','''::MmReserveExitBranch:
 jmp MmReserveExit
 .res 12,$ea
::WorldFirebarAdmissionDone:
 rts
 .assert *-WorldFirebarDrawAdmission=37,lderror,"Body-reservation resident span"''')
  w=originals[names[1]]
  w=replace(w,'''  .res 110,$ea
  .assert *-MegaManDrawShots=139,error,"Shot wrapper original span"''','''::MmReserveBegin:
  lda #1
  sta GuestOamRotationActive
  farcall KbOamPriority
  lda SpriteShuffleOffset
  lsr
  bcs Native
  lda MmDeathFlag
  bne Native
  lda ObjectMetasprite
  beq Native
  ldx #40
  lda ProtoVariant
  beq :+
  ldx #44
:
  ora #$80                    ; 80Mega /81Proto; old readers are boolean.
  sta GuestOamRotationActive
  lda #0
  sta RgOamRotation
  jmp MmReserveClear
Native:
  ldx #0
  jmp MmReserveClear
::MmReserveFinish:
  bit GuestOamRotationActive
  bpl Legacy
  lda CurrentOAMOffset
  sec
  sbc #40
  ldx ProtoVariant
  beq :+
  sbc #4
:
  sta RgOamUsed                ; Previous used count is dead after KbOamPriority.
  lda #0
  sta RgOamPlayerStart
  rts
Legacy:
  lda CurrentOAMOffset
  sta RgOamPlayerStart
::MegaManProjectileOamReady:
  jsr ProtoOamReservation
  clc
  adc CurrentOAMOffset
  sta CurrentOAMOffset
  rts
  .assert *-MegaManDrawShots=139,error,"Shot wrapper original span"''')
  w+='''
.if ::ENABLE_MMC5_EXPANDED
.pushseg
.segment "MM_BODY_RESERVE"
.proc MmReserveExit
  ; Reproduce the old body's logical cursor, physical return X and final SBC V.
  ; Keep physical rotation0 for the retained body-first image/partial writers.
  lda CurrentOAMOffset
  clc
  adc RgOamUsed
  sta CurrentOAMOffset
  sec
  sbc RgOamFirst
  tax
  lda RgOamFirst
  eor #$ff
  clc
  adc #1
  sta RgOamRotation
  txa
  sec
  sbc RgOamRotation
  ldy #0
  sty RgOamRotation
  jmp MmReserveRosterTail
.endproc
.assert *-MmReserveExit<=88,error,"Actual bank4 pool"
.segment "MM_BODY_PARTIAL"
.proc MmReservePartial
  ; Only a retained Proto body-first image has tag81. A new native Main
  ; resets its cursor40; shift this first partial group past all44body bytes.
  ; Native and Mega40 turns retain their exact original allocation.
  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
  bne Done
  lda GuestOamRotationActive
  cmp #$81
  bne Done
  lda CurrentOAMOffset
  cmp #40
  bne Done
  lda #44
  sta CurrentOAMOffset
Done:
  rts
.endproc
.proc MmReserveVine
  jsr MmReservePartial
'''
  body=(R/'src/ryu_platform.s').read_text().split('.proc RyuPlatformOriginalDrawVine\n',1)[1].split('\n.endproc',1)[0]
  body=replace(body,'  ldx Vine_ObjOffset,y        ;get offset to vine\n','')
  a=body.index('  ldx #$00                   ;start with the first sprite again')
  z=body.index('  ldy R0                     ;return offset set earlier',a)
  body=body[:a]+'''.repeat 6,I
  lda Vine_Start_Y_Position
  sec
  sbc Sprite_Y_Position,y
  cmp #$64
  bcc :+
  lda #$f8
  sta Sprite_Y_Position,y
:
  .if I<>5
  iny
  iny
  iny
  iny
  .endif
.endrepeat
  ; Last CPX6 always returned X6/C1; LDY R0 below owns final NZ.
  ldx #6
  sec
'''+body[z:]
  w+=body+'''
.endproc
.proc MmReserveLift
  jsr MmReservePartial
  farcall CrossoverDrawSmallPlatform
  rts
.endproc
.assert *-MmReservePartial<=400,error,"Actual bank66 pool"
.popseg
.endif
'''
  s=originals[names[2]]
  for oldname,newname in [('RyuPlatformOriginalDrawVine','MmReserveVine'),('CrossoverDrawSmallPlatform','MmReserveLift')]:
   s=replace(s,'  farcall '+oldname+'\n','.if ::ENABLE_MMC5_EXPANDED\n  farcall '+newname+'\n.else\n  farcall '+oldname+'\n.endif\n')
  levels=originals[names[3]]
  for count,comment in [(6,'dump tile number into all six sprites'),(6,'dump attributes into all six sprites'),(3,'dump vertical coordinate into Y coordinates')]:
   line=('       farcall DumpSixSpr              ;'+comment)if count==6 else('TopSP: farcall DumpThreeSpr            ;'+comment)
   inline=('TopSP:\n'if count==3 else'')+'.if ::ENABLE_MMC5_EXPANDED\n'+'\n'.join('       sta Sprite_Data+'+str(x)+',y'for x in range((count-1)*4,-1,-4))+'\n.else\n'+line.removeprefix('TopSP: ')+'\n.endif'
   levels=replace(levels,line,inline)
  levels=replace(levels,'ExSPl: ldx ObjectOffset            ;get enemy object offset and leave\n       rts\n\n.endproc','ExSPl: ldx ObjectOffset            ;get enemy object offset and leave\n       rts\n.if ::ENABLE_MMC5_EXPANDED\n       .res 9,$ea\n.endif\n\n.endproc')
  changed=dict(zip(names,[e,w,s,levels]));leaves={}
  entry=(R/'src/entrypoint.s').read_text()
  for relative,text in changed.items():
   flat=B/('mm_body_'+Path(relative).name);flat.write_text(text);leaves[relative]=str(flat)
   entry=replace(entry,'.include "'+Path(relative).name+'"','.include "'+flat.name+'"')
  cfg=(R/'smb1base-mmc5-expanded.cfg').read_text()
  cfg=replace(cfg,'    METASPRITE: load = PRGA_04, type = ro;\n','    METASPRITE: load = PRGA_04, type = ro;\n    MM_BODY_RESERVE: load=PRGA_04,type=ro,start=$bf33;\n')
  cfg=replace(cfg,'    MM_BASIC_REMAINDER: load=X5_NEW_42_TAIL,type=ro,start=$b9a8;\n','    MM_BASIC_REMAINDER: load=X5_NEW_42_TAIL,type=ro,start=$b9a8;\n    MM_BODY_PARTIAL: load=X5_NEW_42_TAIL,type=ro,start=$b9c0;\n')
  conf=B/'mm_body_reserve.cfg';conf.write_text(cfg)
  asm=B/'mm_body_reserve_entrypoint.s';asm.write_text(entry)
  mainc=B/'mm_body_reserve_main.c';mainc.write_bytes((R/'src/main.c').read_bytes())
  output=B/'mm_body_reserve.nes'
  command=json.loads((B/'bass_corner_current_result.json').read_text())['build_command']
  # Use only its proven compiler invocation; all includes now resolve the
  # authoritative adopted source, not the old Bass flat-input substitutions.
  renames={'bass_corner_current.cfg':conf.name,'bass_corner_current.':'mm_body_reserve.',
           'bass_corner_current_main.c':mainc.name,'bass_corner_current_entrypoint.s':asm.name}
  for oldname,newname in renames.items():command=[v.replace(oldname,newname)for v in command]
  result=subprocess.run(command,cwd=R,capture_output=True,text=True)
  (B/'mm_body_reserve_build.log').write_text(result.stdout+result.stderr)
  proof['build_command']=command;proof['build_exit']=result.returncode
  assert result.returncode==0,result.stdout+result.stderr
  sys.path.insert(0,str(R/'tools'));from prepare_cv3_dmc_mirror import prepare
  prepare(R,output)
  new=scoped_load(output);after=new['raw']
  banks={i:sum(a!=z for a,z in zip(raw[16+i*8192:16+(i+1)*8192],after[16+i*8192:16+(i+1)*8192]))for i in range(128)}
  banks={i:n for i,n in banks.items()if n};assert set(banks)<={0,4,26,66},banks
  assert raw[:16]==after[:16]and raw[16+128*8192:]==after[16+128*8192:]
  q,nq=qualified(BASE),qualified(output)
  moves={'::'.join(n):[v,nq.get(n)]for n,v in q.items()if nq.get(n)!=v}
  patch=''.join(''.join(difflib.unified_diff(originals[n].splitlines(True),t.splitlines(True),fromfile='8487/'+n,tofile='private/'+n))for n,t in changed.items())
  patch+=''.join(difflib.unified_diff((R/'smb1base-mmc5-expanded.cfg').read_text().splitlines(True),cfg.splitlines(True),fromfile='8487/smb1base-mmc5-expanded.cfg',tofile='private/smb1base-mmc5-expanded.cfg'))
  (B/'mm_body_reserve.patch').write_text(patch)
  assert bindings=={p:sha(R/p)for p in bindings}and sha(BASE)==EXPECTED
  proof.update(passed=True,baseline=EXPECTED,candidate=sha(output),changed_banks=banks,qualified_symbol_moves=moves,
   primary_inputs=bindings,sparse_leaves={n:dict(path=p,sha256=sha(p))for n,p in leaves.items()},
   candidate_source_cfg=dict(path=str(conf),sha256=sha(conf)),verified_pools=pools,
   original_body_records_unchanged=True,ordinary_Mega40_Proto44_capacity_preserved=True,
   phase='SpriteShuffleOffset bit0; completed-construction alternation, not guaranteed DMA alternation',
   partial_change='Only char1/tag81/cursor40 first native partial moves40→44; copies retain all six records. Other paths original.',
   limits='Build/layout experiment only. CPU/ABI/IRQ/capacity/cost/native not qualified; no adoption claim.')
 except BaseException as ex:
  proof['error']=repr(ex);proof['traceback']=traceback.format_exc();raise
 finally:
  proof['tool_sha256']=sha(__file__);put(B/'mm_body_reserve_result.json',proof)
  print(json.dumps({k:v for k,v in proof.items()if k in['passed','error','candidate','changed_banks']},indent=2))

if __name__=='__main__':
 if sys.argv[1:]==['--build-controls']:build_controls()
 else:main()
