"""Compile current-SMB terrain producer inside the private DK Jr component."""
import json,re,subprocess,sys,zipfile
from pathlib import Path
import prepare_dkjr_native_source_1102_v2 as P
from py65.disassembler import Disassembler
R=P.R;O=P.O
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
CURRENT=R/'build/bub-menu-candidate-1102-v2/combined-event.nes'
PIN='613b3300b09e530ec920835b95df53f3115d865ed854e273809d4cafa52407ce'


def main():
 checkpoint=R/'docs/qa/checkpoints/2026-11-02/dkjr-native-source-v2';frozen=json.loads((checkpoint/'manifest.json').read_text());assert P.sha((checkpoint/'inputs.zip').read_bytes())==frozen['archive_SHA256']
 with zipfile.ZipFile(checkpoint/'inputs.zip')as archive:
  def frozen_read(name):
   rel='build/dkjr-native-source-1102-v2/'+name;data=archive.read(rel);assert P.sha(data)==frozen['files'][rel]['SHA256'];return data
  source=frozen_read('component.s').decode().replace('\r\n','\n');baseline=json.loads(frozen_read('layout.json'))
 b=scoped_load(R/'build/excitebike-pose-1101-v3/current4.nes');raw=CURRENT.read_bytes();assert P.sha(raw)==PIN
 names=['Block_Buffer_1','Block_Buffer_2','MTileAttribute','ScreenLeft_X_Pos','ScreenLeft_PageLoc','Enemy_Flag','Enemy_ID','Enemy_State','Enemy_Y_HighPos','Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position','Vine_Start_Y_Position','Vine_Height','Vine_FlagOffset','Vine_ObjOffset','BoundingBox_UL_Corner','AreaPointer','WorldNumber','SavedJoypadBits','Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos']
 source=source.replace('DkjrComponentEnd:\n.export DkjrComponentEnd','')
 old='D_e8a5: ; original $E8A5: sta $0f\n sta $c00f'
 assert source.count(old)==1;source=source.replace(old,'D_e8a5: ; original $E8A5: sta $0f\n jsr DkjrNativeTerrainHook\n sta $c00f')
 native={n:address(b,n)for n in names};prefix='.export DkjrNativeWorldEnable,DkjrNativeWorldDisable,DkjrNativeTerrainHook,DkjrNativeWorldBuild\n'
 for n,pc in native.items():prefix+=n+'=$%04x\n'%pc
 source=prefix+source
 # Exact post-read controller normalization. Native owns the hardware read;
 # no guessed direction/heldA policy replaces the donor's F23E..F266 code.
 mem=P.D.Bus();ds=Disassembler(P.D.T.NesMPU(memory=mem,pc=0))
 recovered=[(0xf23e,0xf266,'controller normalization'),(0xcec9,0xced4,'private audio request'),(0xec17,0xec3b,'private expired-popup cleanup')]
 for lo,hi,role in recovered:
  if lo!=0xf23e:
   source=source.replace('DImport_%04x'%lo,'D_%04x'%lo)
   trap='D_%04x: jmp D_%04x ; explicit independent donor/native phase import'%(lo,lo)
   assert source.count(trap)==1;source=source.replace(trap,'')
  pc=lo
  while pc<hi:
   n,s=ds.instruction_at(pc);s=s.lower();op=s.split()[0]
   if op in['bcc','bcs','beq','bne','bmi','bpl','bvc','bvs']:s='j'+op[1:]+' D_%04x'%int(s.split('$')[1],16)
   elif '#'not in s:s=re.sub(r'\$([0-9a-f]+)',lambda m:'$%04x'%(int(m[1],16)+0xc000),s)
   source+='\nD_%04x: ; original $%04X %s\n %s\n'%(pc,pc,role,s);pc+=n
  assert pc==hi
 source+='''
.export DkjrNormalizePad,DkjrNativeControls
DkjrNormalizePad=D_f23e
; Native SavedJoypadBits is the complete NES button byte. Source actor0
; remains actor0; the native current-player selection happened at its input.
DkjrNativeControls:
 lda SavedJoypadBits
 ldx #0
 jmp DkjrNormalizePad
'''
 source+='''
; All addresses C800..C900 are private MEASUREMENT context, not host leases.
; C800/40/80 lists, C8C0..D8 pointer tables; D8..FF producer scratch.
WMode=$c8da
WKind=$c8db
WCount=$c8dd
WX=$c8de
WPage=$c8df
WEndX=$c8e0
WEndPage=$c8e1
WY=$c8e2
WEndY=$c8e3
WL=$c8e4
WT=$c8e5
WR=$c8e6
WB=$c8e7
WLeft=$c8e8
WRight=$c8e9
WTop=$c8ea
WBottom=$c8eb
WTile=$c8ec
WScreenLo=$c8ed
WScreenHi=$c8ee
WError=$c8ef
WObject=$c8f0
WDeltaX=$c8f1
WDeltaY=$c8f2
WAnchorX=$c8f3
WAnchorY=$c8f4
.export DkjrNativeImportAnchor,DkjrNativePublishAnchor
; Explicit cold/script resynchronization only, NOT a per-Main
; physics reset. DK's32px OAM origin is8px left of the native16px anchor;
; sourceOAMY=nativeAnchorY+15, so original Land(top-17) publishes top-32.
; Reject unrepresentable/offscreen inputs before changing original state.
DkjrNativeImportAnchor:
 lda Player_Y_HighPos
 cmp #1
 bne AnchorReject
 lda Player_Y_Position
 cmp #225
 bcs AnchorReject
 clc
 adc #15
 sta WAnchorY
 lda Player_X_Position
 sec
 sbc ScreenLeft_X_Pos
 sta WAnchorX
 lda Player_PageLoc
 sbc ScreenLeft_PageLoc
 bne AnchorReject
 lda WAnchorX
 sec
 sbc #8
 bcc AnchorReject
 cmp #224
 bcs AnchorReject
 sec
 sbc $c213
 sta WDeltaX
 lda WAnchorY
 sec
 sbc $c210
 sta WDeltaY
 ldx #28
TranslateBody:
 lda $c210,x
 clc
 adc WDeltaY
 sta $c210,x
 lda $c213,x
 clc
 adc WDeltaX
 sta $c213,x
 dex
 dex
 dex
 dex
 bpl TranslateBody
 sec
 rts
AnchorReject:
 clc
 rts
; After the source owner resolves movement/support, publish only its native
; position cache. Velocity/contact/camera event ownership is not implied.
DkjrNativePublishAnchor:
 lda $c213
 cmp #224
 bcs AnchorReject
 lda $c210
 cmp #15
 bcc AnchorReject
 sec
 sbc #15
 sta WAnchorY
 lda $c213
 clc
 adc #8
 adc ScreenLeft_X_Pos
 sta Player_X_Position
 lda ScreenLeft_PageLoc
 adc #0
 sta Player_PageLoc
 lda WAnchorY
 sta Player_Y_Position
 lda #1
 sta Player_Y_HighPos
 sec
 rts
DkjrNativeWorldEnable:
 lda #$ff
 sta $c800
 sta $c840
 sta $c880
 jsr DkjrUseNativeGeometry
 bcc :+
 lda #1
 sta WMode
:
 rts
DkjrNativeWorldDisable:
 lda #0
 sta WMode
 jmp DkjrUseOriginalGeometry
DkjrNativeTerrainHook:
 php
 pha
 txa
 pha
 tya
 pha
 lda WMode
 beq HookReturn
 tsx
 lda $0103,x
 sta WKind
 jsr DkjrNativeWorldBuild
HookReturn:
 pla
 tay
 pla
 tax
 pla
 plp
 rts
DkjrNativeWorldBuild:
 lda #0
 sta WCount
 sta WError
 ldx WKind
 lda ListOffsets,x
 sta StoreRect+1
 sta StoreEnd+1
 lda $c03e
 sta WLeft
 lda $c040
 sta WRight
 sec
 sbc WLeft
 cmp #33
 jcs InvalidWindow
 lda $c03f
 sta WTop
 lda $c041
 sta WBottom
 ldx WKind
 cpx #3
 bne OrdinaryY
 ; Source support wrapper will probe bottom+1..bottom+2 after this hook.
 clc
 adc #1
 sta WTop
 adc #1
 sta WBottom
OrdinaryY:
 lda WBottom
 sec
 sbc WTop
 cmp #17
 jcs InvalidWindow
 lda WTop
 cmp #240
 jcs EmptyWindow
 cmp #32
 bcs :+
 lda #32
:
 and #$f0
 sta WY
 lda WBottom
 cmp #32
 jcc EmptyWindow
 cmp #240
 bcc :+
 lda #239
:
 and #$f0
 sta WEndY
 lda WRight
 clc
 adc ScreenLeft_X_Pos
 and #$f0
 sta WEndX
 lda ScreenLeft_PageLoc
 adc #0
 sta WEndPage
Row:
 lda WLeft
 clc
 adc ScreenLeft_X_Pos
 and #$f0
 sta WX
 lda ScreenLeft_PageLoc
 adc #0
 sta WPage
Column:
 lda WX
 lsr
 lsr
 lsr
 lsr
 sta WTile
 lda WY
 sec
 sbc #32
 ora WTile
 tay
 lda WPage
 and #1
 bne SecondBuffer
 lda Block_Buffer_1,y
 jmp Cell
SecondBuffer:
 lda Block_Buffer_2,y
Cell:
 sta WTile
 ldx WKind
 cpx #2
 bcc VineCell
 tax
 lda MTileAttribute,x
 and #3
 cmp #1
 bne NextColumn
 beq Candidate
VineCell:
 cmp #$26                   ; Native vine cell; exclude flagpole24/25.
 bne NextColumn
Candidate:
 lda WX
 sec
 sbc ScreenLeft_X_Pos
 sta WScreenLo
 lda WPage
 sbc ScreenLeft_PageLoc
 sta WScreenHi
 beq OnScreen
 cmp #$ff
 bne NextColumn
 lda WScreenLo
 cmp #$f1
 bcc NextColumn
 lda #0
 sta WL
 lda WScreenLo
 clc
 adc #15
 sta WR
 jmp RectY
OnScreen:
 lda WScreenLo
 cmp #$ff
 beq NextColumn
 sta WL
 clc
 adc #15
 bcc :+
 lda #$ff
:
 sta WR
RectY:
 lda WY
 sta WT
 clc
 adc #15
 sta WB
 lda WKind
 cmp #2
 bcs AppendCell
 ; Climbable source-format rectangles use the real cell center, not edges.
 lda WScreenLo
 clc
 adc #8
 sta WL
 sta WR
 lda WScreenHi
 adc #0
 bne NextColumn
 lda WL
 cmp #$ff
 beq NextColumn
AppendCell:
 jsr AppendRect
NextColumn:
 lda WX
 cmp WEndX
 bne AdvanceX
 lda WPage
 cmp WEndPage
 beq EndRow
AdvanceX:
 lda WX
 clc
 adc #16
 sta WX
 bcc :+
 inc WPage
:
 jmp Column
EndRow:
 lda WY
 cmp WEndY
 beq EmptyWindow
 clc
 adc #16
 sta WY
 jmp Row
InvalidWindow:
 lda #1
 sta WError
 jmp PublishEnd
EmptyWindow:
 jsr NativeObjects
PublishEnd:
 ldy WCount
 lda #$ff
StoreEnd:
 sta $c800,y
 rts
; A growing native vine is one continuous spine. Actual VineObjectHandler
; only runs slot5; DrawVine shares that relative origin across its1/2stacks.
; Admit only the visible grown interval from rootY to original startY;
; the source-format center is rootX+8. Native flagpole cells remain excluded.
NativeObjects:
 lda WKind
 cmp #2
 bcc GrowingVine
 cmp #3
 jcs Platforms
 rts
GrowingVine:
 lda Vine_FlagOffset
 jeq ObjectsDone
 cmp #3
 jcs ObjectsDone
 tay
 lda Vine_ObjOffset
 cmp #5
 beq VineRootListed
 cpy #2
 bne ObjectsDone
 lda Vine_ObjOffset+1
 cmp #5
 bne ObjectsDone
VineRootListed:
 lda Vine_Height
 cmp #8
 bcc ObjectsDone
 cmp VineMaximum-1,y
 bcc VineHeightValid
 bne ObjectsDone
VineHeightValid:
 lda Enemy_Flag+5
 beq ObjectsDone
 bmi ObjectsDone
 lda Enemy_ID+5
 cmp #$2f
 bne ObjectsDone
 lda Enemy_Y_HighPos+5
 cmp #1
 bne ObjectsDone
 lda Enemy_X_Position+5
 sec
 sbc ScreenLeft_X_Pos
 sta WScreenLo
 lda Enemy_PageLoc+5
 sbc ScreenLeft_PageLoc
 sta WScreenHi
 lda WScreenLo
 clc
 adc #8
 sta WL
 sta WR
 lda WScreenHi
 adc #0
 bne ObjectsDone
 lda WL
 cmp #$ff
 beq ObjectsDone
 lda Enemy_Y_Position+5
 cmp #32
 bcs :+
 lda #32
:
 sta WT
 lda Vine_Start_Y_Position
 cmp #240
 bcc :+
 lda #239
:
 sta WB
 cmp WT
 bcc ObjectsDone
 jmp IntersectAppend
ObjectsDone:
 rts
; Native published boxes are authoritative: no inferred object widths.
; Platforms contribute only their top plane to floor/full-support queries.
; Horizontal/vertical carry remains an explicit later native event adapter.
Platforms:
 ldx #5
PlatformLoop:
 stx WObject
 lda Enemy_Flag,x
 beq NextPlatform
 bmi NextPlatform
 lda Enemy_ID,x
 cmp #$24
 bcc NextPlatform
 cmp #$2d
 bcs NextPlatform
 cmp #$2b
 bcs PlatformStateValid
 lda Enemy_State,x
 bmi NextPlatform
PlatformStateValid:
 lda Enemy_Y_HighPos,x
 cmp #1
 bne NextPlatform
 txa
 clc
 adc #1
 asl
 asl
 tay
 lda BoundingBox_UL_Corner,y
 cmp #$ff
 beq NextPlatform
 sta WL
 lda BoundingBox_UL_Corner+2,y
 cmp WL
 bcc NextPlatform
 sta WR
 lda Enemy_ID,x
 cmp #$2b
 bcs SmallPlatformPlanes
 lda BoundingBox_UL_Corner+1,y
 jsr AppendPlatformY
 jmp NextPlatform
SmallPlatformPlanes:
 ; SmallPlatformBoundBox uses native control4: [0,0,24,8]. Its collision
 ; pass may leave eitherY published. Preserve its authoritative horizontal
 ; bounds; derive both trueY planes using actual CrossoverLiftSecondY.
 lda Enemy_Y_Position,x
 jsr AppendPlatformY
 ldx WObject
 lda AreaPointer
 cmp #$62
 bne VanillaSecond
 lda WorldNumber
 cmp #1
 beq SourceSecond
 cmp #4
 bne VanillaSecond
SourceSecond:
 lda Enemy_State,x
 jmp AppendSecond
VanillaSecond:
 lda Enemy_Y_Position,x
 clc
 adc #$80
AppendSecond:
 jsr AppendPlatformY
NextPlatform:
 ldx WObject
 dex
 jpl PlatformLoop
 rts
AppendPlatformY:
 cmp #32
 bcc PlatformYDone
 cmp #240
 bcs PlatformYDone
 sta WT
 sta WB
 jmp IntersectAppend
PlatformYDone:
 rts
IntersectAppend:
 lda WR
 cmp WLeft
 bcc IntersectDone
 lda WRight
 cmp WL
 bcc IntersectDone
 lda WB
 cmp WTop
 bcc IntersectDone
 lda WBottom
 cmp WT
 bcc IntersectDone
 jmp AppendRect
IntersectDone:
 rts
AppendRect:
 ldy WCount
 cpy #60
 bcc :+
 lda #1
 sta WError
 rts
:
 ldx #0
CopyRect:
 lda WL,x
StoreRect:
 sta $c800,y
 iny
 inx
 cpx #4
 bne CopyRect
 sty WCount
 rts
ListOffsets:.byte $40,$40,$80,0,0
VineMaximum:.byte $30,$60 ; actual native VineHeightData, byte-bound below
DkjrNativeWorldEnd:
.export DkjrNativeWorldEnd
DkjrComponentEnd:
.export DkjrComponentEnd
'''
 source='.macpack longbranch\n'+source.replace('.macpack longbranch\n','')
 (O/'native-world-v3.s').write_text(source);cfg='MEMORY{C:start=$a000,size=$2000,file=%O;}SEGMENTS{DKJR:load=C,type=rw;}';(O/'native-world-v3.cfg').write_text(cfg)
 cc=R/'tools/Windows/cc65/bin'
 for cmd in[[cc/'ca65.exe',O/'native-world-v3.s','-g','-o',O/'native-world-v3.o'],[cc/'ld65.exe','-C',O/'native-world-v3.cfg',O/'native-world-v3.o','-o',O/'native-world-v3.bin','-Ln',O/'native-world-v3.lbl']]:
  p=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert p.returncode==0,p.stderr
 blob=(O/'native-world-v3.bin').read_bytes();labels={n:int(a,16)for a,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',(O/'native-world-v3.lbl').read_text(),re.M)};assert len(blob)<=8160
 at=location(b,'MTileAttribute');assert raw[at:at+256]==b['raw'][at:at+256]
 contracts=[]
 for name,end,length,path,role in[
  ('VineHeightData',None,2,'src/object.s','Actual1/2stack growth maxima48/96'),
  ('VineObjectHandler','WarpZoneObject',None,'src/object.s','Only slot5 runs; flag1/2, height8 draw threshold and rootY growth'),
  ('Setup_Vine','InitRetainerObj',None,'src/object.s','Root/startY and ordered Vine_ObjOffset publication'),
  ('RyuPlatformOriginalDrawVine','RyuPlatformCodeEnd',None,'src/ryu_platform.s','One root-origin continuous spine, two48px stacks, startY visibility clipping'),
  ('CrossoverLiftSecondY','CrossoverLiftPlayerY',None,'src/level_lift_bridges.inc','Exact first/second native platform ordinates, area62 world2/5 stateY policy'),
  ('BoundBoxCtrlData',None,80,'src/collision.s','Actual published bbox profiles; small platforms use control4=[0,0,24,8]'),
  ('SmallPlatformBoundBox','GetMaskedOffScrBits',None,'src/collision.s','Actual published bbox/offscreen preparation entry')]:
  pos=location(b,name);size=length or address(b,end)-address(b,name);data=raw[pos:pos+size];assert data==b['raw'][pos:pos+size],name
  contracts.append(dict(name=name,CPU_address=address(b,name),file_offset=pos,bytes=size,SHA256=P.sha(data),source=path,source_SHA256=P.sha((R/path).read_bytes()),role=role))
 assert raw[location(b,'VineHeightData'):][:2]==bytes([48,96])
 q=dict(passed=True,ROM_written=False,native_allocation=False,base_native_ROM_SHA256=PIN,inherited_checkpoint=str(checkpoint.relative_to(R)).replace('\\','/'),inherited_archive_SHA256=frozen['archive_SHA256'],component_bytes=len(blob),private_code_spare=8160-len(blob),measurement_context_half_open=[0xc800,0xc900],original_state_bytes=2048,measurement_extra_context_bytes=256,additional_original_ranges=[dict(start=lo,end=hi,bytes=hi-lo,role=role)for lo,hi,role in recovered],remaining_import_count=11,provisional_physical_demand=dict(code_1K_pages=8,uncompressed_art_1K_pages=2,art_bytes=1728,art_tail_bytes_not_code_granted=320,service_vector_and_resident_loader_included=False),native_bindings=native,native_source_contracts=contracts,native_MTileAttribute_file_offset=at,native_MTileAttribute_SHA256=P.sha(raw[at:at+256]),labels=labels,code_SHA256=P.sha(blob),implemented=['Native BlockBuffer solid/climb26 cells','Actual VineObjectHandler slot5/root/start/growth geometry','Actual published native platform top planes24..2C including both small-liftY surfaces','Exact original controller normalization from native SavedJoypadBits','Exact original private audio request and expired-popup cleanup','Explicit cold/script anchor translation and source position publication'],unimplemented=['Actual native Main/coordinate event admission, velocity/body/head/side policies','Native platform current-bbox publication phase and carry event admission','Eleven native life/contact/fruit/UI service imports, real audio publication and owner/router/CHR/menu/ISR'],scope='Compiled private terrain/control/coordinate leaves, with source phase regression only. Lists admit at most15 nearby rectangles; overflow marks WError and must be rejected by future owner adapter. No native executable owner or ROM write.')
 baseline.update(component_bytes=len(blob),imports={n[8:].upper():pc for n,pc in labels.items()if n.startswith('DImport_')},code_SHA256=P.sha(blob))
 assert len(baseline['imports'])==11
 (O/'native-world-v3-source-layout.json').write_text(json.dumps(baseline,indent=2)+'\n')
 (O/'native-world-v3-layout.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q[k]for k in['passed','ROM_written','native_allocation','component_bytes','private_code_spare','remaining_import_count','code_SHA256']}))


if __name__=='__main__':main()
