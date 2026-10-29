"""Private737d Pit/GB-Pit presentation only; approved exact bounded leases."""
from pathlib import Path
import difflib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import pit_retold_layout_plan_v2 as V
from sunny_integrated_controls_v1 import *
P=R/'build/kamikaze-mario-host-v4';O=R/'build/pit-retold-host-v1'

def assets(b):
 V.V.PATCH,_=V.V.A.ips();V.G.ROLE='PIT';V.G.COLORS=V.G.targets('PIT')
 def data(n,k):return b['raw'][location(b,n):location(b,n)+k]
 banks=data('XgPITBanks',252);mapping=data('ChrPhysicalMap',256)
 pages=[bytearray(b['raw'][1048592+mapping[213+min(g,3)]*1024:1048592+mapping[213+min(g,3)]*1024+1024])for g in range(5)]
 constraints={};records={};targets=[]
 for g in range(5):
  for t in range(0,22,2):constraints[(g,t)]=bytes(pages[g][t*16:t*16+32])
 for i in range(252):
  pose=V.G.POSES[i%84];grid=V.G.layers(V.target(pose));group=4 if pose=='WALK3'else banks[i]-213
  ptr=data('XgPITRightLo',252)[i]+256*data('XgPITRightHi',252)[i]
  at=16+31*8192+ptr-0xc000;old=b['raw'][at:at+1+b['raw'][at]];rec=bytearray(old);covered=set()
  repair=pose in['CROUCH','DIE','CROUCHSHOOT','CROUCHATTACK1','CROUCHATTACK2','CROUCHATTACK3']
  for j in range(1,len(rec),4):
   if repair and rec[j+2]==17 and rec[j+3]in[1,9]:rec[j+2]=16
   t,a,y,x=rec[j:j+4];x=x if x<128 else x-256;y=y if y<128 else y-256;p=a&3
   values=[[0]*8 for _ in range(16)]
   for yy in range(16):
    for xx in range(8):
     tx,ty=32+x+xx,32+y+yy;sx=7-xx if a&64 else xx;sy=15-yy if a&128 else yy
     if 0<=tx<96 and 0<=ty<80:covered.add((p,tx,ty));values[sy][sx]=grid[p][ty][tx]
   raw=V.V.encode(values);key=(group,t)
   if key in constraints:assert constraints[key]==raw,('pattern conflict',i,pose,key)
   else:constraints[key]=raw
  assert not any(grid[p][y][x]and(p,x,y)not in covered for p in grid for y in range(80)for x in range(96)),('uncovered original pixel',i,pose)
  if bytes(rec)!=old:records[ptr]=dict(pose=pose,right=bytes(rec))
  targets.append(dict(index=i,pose=pose,group=group,old_pointer=ptr))
 for(g,t),raw in constraints.items():pages[g][t*16:t*16+32]=raw
 assert len(records)==5
 lines=[]
 for n,row in enumerate(records.values()):
  right=row['right'];left=bytearray(right)
  for j in range(1,len(left),4):left[j+1]^=64;left[j+3]=(8-left[j+3])&255
  for face,raw in[('Right',right),('Left',left)]:
   lines+=['GbPitRecord'+str(n)+face+':',' .byte '+','.join(f'${v:02x}'for v in raw)]
 for face in['Right','Left']:
  for suffix,op in[('Lo','<'),('Hi','>')]:lines+=['GbPit'+face+suffix+':',' .byte '+','.join(op+'GbPitRecord'+str(n)+face for n in range(5))]
 return b''.join(pages),'\n'.join(lines)+'\n',targets

CODE='''; Private Retold/local-original art adaptation. No physics/gear changes.
.macpack longbranch
.include "inc/common.inc"
.include "inc/charmap.inc"
PitVariant=$5fe0
.export PitVariant,GbPitPose,GbPitMenuNavigate,GbPitQueueName,GbPitRenderEnd,GbPitMenuEnd
.import SelectedCharacter,PlayerFacingDir,RgPose,SmChrBank,PlayerChrBank,CurrentCHRBank
.import X5ChrMode,X5WideChrActive,ReloadCHRBank,SmPosePtr,GbPitCommon
.import XgPITBanks,XgPITRightLo,XgPITRightHi,XgPITLeftLo,XgPITLeftHi
.import CrossoverMenuPressed,CrossoverMenuIndex,NrMenuNavigate,KmQueueName
.import VRAM_Buffer1_Offset,VRAM_Buffer1,SafecallA_SMC,FarcallJmpTarget_SMC,FarCallCommon
.macro GbCall Target,Bank,Tail
 sta SafecallA_SMC+1
 lda #<Target
 sta FarcallJmpTarget_SMC+1
 lda #>Target
 sta FarcallJmpTarget_SMC+2
 lda #Bank|$80
 .if Tail
 jmp FarCallCommon
 .else
 jsr FarCallCommon
 .endif
.endmacro
.segment "GB_PIT_RENDER"
GbPitRenderStart:
.proc GbPitPose
 lda PitVariant
 bne Alternate
 lda XgPITBanks,x
 sta SmChrBank
 lda PlayerFacingDir
 cmp #1
 bne LegacyLeft
 lda XgPITRightLo,x
 sta SmPosePtr
 lda XgPITRightHi,x
 jmp GbPitCommon
LegacyLeft:
 lda XgPITLeftLo,x
 sta SmPosePtr
 lda XgPITLeftHi,x
 jmp GbPitCommon
Alternate:
 php
 phy
 lda RgPose
 cmp #3
 bne BasePage
 lda #<812
 bne Publish
BasePage:
 lda XgPITBanks,x
 sec
 sbc #$d5
 clc
 adc #<808
Publish:
 sta SmChrBank
 sta PlayerChrBank
 cmp CurrentCHRBank
 bne ChangeChr
 lda X5ChrMode
 cmp #$83
 beq ChrReady
ChangeChr:
 lda SmChrBank
 sta CurrentCHRBank
 lda #$83
 sta X5ChrMode
 lda #1
 sta ReloadCHRBank
ChrReady:
 lda #1
 sta X5WideChrActive
 lda RgPose
 cmp #5
 beq Crouch
 cmp #12
 beq Crouch
 cmp #21
 beq Bow
 cmp #24
 bcc Original
 cmp #27
 bcs Original
 sec
 sbc #22
 tay
 jmp Changed
Crouch:ldy #0
 beq Changed
Bow:ldy #1
Changed:
 lda PlayerFacingDir
 cmp #1
 bne ChangedLeft
 lda GbPitRightLo,y
 sta SmPosePtr
 lda GbPitRightHi,y
 jmp High
ChangedLeft:
 lda GbPitLeftLo,y
 sta SmPosePtr
 lda GbPitLeftHi,y
 jmp High
Original:
 lda PlayerFacingDir
 cmp #1
 bne OriginalLeft
 lda XgPITRightLo,x
 sta SmPosePtr
 lda XgPITRightHi,x
 jmp High
OriginalLeft:
 lda XgPITLeftLo,x
 sta SmPosePtr
 lda XgPITLeftHi,x
High:
 sta SmPosePtr+1
 ply
 plp
 ; The genuine old facing CMP owns C; V/D/I survive physical-page arithmetic.
 lda PlayerFacingDir
 cmp #1
 lda SmPosePtr+1
 jmp GbPitCommon
.endproc
__RECORDS__
GbPitRenderEnd:
.assert *<=$e000,lderror,"Approved31:DDE6..<E000 only"
.segment "GB_PIT_MENU"
.proc GbPitMenuNavigate
 php
 pha
 lda SelectedCharacter
 cmp #6
 bne Legacy
 lda CrossoverMenuPressed
 and #4
 beq Legacy
 pla
 plp
 lda PitVariant
 eor #1
 sta PitVariant
 lda CrossoverMenuIndex
 rts
Legacy:
 pla
 plp
 GbCall NrMenuNavigate,124,1
.endproc
.proc GbPitQueueName
 GbCall KmQueueName,81,0
 php
 pha
 phx
 phy
 lda SelectedCharacter
 cmp #6
 bne Done
 lda PitVariant
 beq Done
 ldx VRAM_Buffer1_Offset
 ldy #15
Copy:
 dex
 lda Name,y
 sta VRAM_Buffer1,x
 dey
 bpl Copy
Done:
 ply
 plx
 pla
 plp
 rts
Name:.byte "     GB PIT     "
.endproc
GbPitMenuEnd:
.assert *<=$b680,lderror,"Approved66:B600..<B680 only"
.segment "GB_PIT_CHR"
.incbin "__CHR__"
'''

def main():
 assert not(O/'handoff.json').exists();parent=json.loads((P/'source-closure.json').read_text())
 for p,h in parent['actual_dependencies'].items():assert sha(p)==h,p
 b=scoped_load(P/'candidate.nes');assert sha(P/'candidate.nes')=='737d71af449b70a73b1d13f228efb6cfa819ea027219f605344861fb0e2b0624'
 assert b['raw'][16+31*8192+0x1de6:16+32*8192]==bytes([255])*538
 assert b['raw'][16+66*8192+0x1600:16+66*8192+0x1680]==bytes([255])*128
 assert b['raw'][1048592+808*1024:1048592+813*1024]==bytes(5120)
 (O/'src').mkdir(parents=True,exist_ok=True)
 pixels,records,targets=assets(b);(O/'pit-retold.chr').write_bytes(pixels)
 (O/'component.s').write_text(CODE.replace('__RECORDS__',records).replace('__CHR__',(O/'pit-retold.chr').as_posix()))
 old=(R/'src/expanded.s').read_text();line='Pit: XgPoseCase "PIT"';assert old.count(line)==1
 span=address(b,'ExpandedPose::Rygar')-address(b,'ExpandedPose::Pit')
 expanded=old.replace(line,'Pit:\n .if ::ENABLE_MMC5_EXPANDED\n jmp GbPitPose\n .res '+str(span-3)+',$ea\n .else\n XgPoseCase "PIT"\n .endif')
 (O/'src/expanded.s').write_text(expanded)
 menu=(P/'overlay/src/character_select.s').read_text()
 assert menu.count('farcall NrMenuNavigate')==menu.count('farcall KmQueueName,jmp')==1
 menu=menu.replace('farcall NrMenuNavigate','jsr GbPitMenuNavigate\n  jmp GbPitNavContinue\n  .res 12,$ea\nGbPitNavContinue:').replace('farcall KmQueueName,jmp','jmp GbPitQueueName\n  .res 15,$ea')
 (O/'src/character_select.s').write_text(menu)
 exports='SelectedCharacter PlayerFacingDir RgPose SmChrBank PlayerChrBank CurrentCHRBank X5ChrMode X5WideChrActive ReloadCHRBank SmPosePtr XgPITBanks XgPITRightLo XgPITRightHi XgPITLeftLo XgPITLeftHi CrossoverMenuPressed CrossoverMenuIndex NrMenuNavigate KmQueueName VRAM_Buffer1_Offset VRAM_Buffer1 SafecallA_SMC FarcallJmpTarget_SMC FarCallCommon'.split()
 entry=(P/'overlay/src/entrypoint.s').read_text()+'\n.if ::ENABLE_MMC5_EXPANDED\n.import GbPitPose,GbPitMenuNavigate,GbPitQueueName\n.export GbPitCommon\nGbPitCommon=ExpandedPose::Pointer\n'+''.join('.export '+n+'\n'for n in exports)+'.endif\n'
 (O/'entrypoint.s').write_text(entry)
 cfg=(P/'overlay/smb1base-mmc5-expanded.cfg').read_text()
 assert cfg.count('}\nSYMBOLS {')==1
 cfg=cfg.replace('}\nSYMBOLS {','    GB_PIT_RENDER: load=XG_PIT_MEM,type=ro,start=$dde6,optional=yes;\n    GB_PIT_CHR: load=TMNT_CHR_TAIL,type=ro,start=$ca000,optional=yes;\n}\nSYMBOLS {')
 line='    PN_MENU_HINT: load=X5_NEW_42,type=ro,optional=yes;'
 assert cfg.count(line)==1
 cfg=cfg.replace(line,line+'\n    GB_PIT_MENU: load=X5_NEW_42,type=ro,start=$b600,optional=yes;')
 # Append after original owners; never advance an existing automatic start.
 (O/'smb1base-mmc5-expanded.cfg').write_text(cfg)
 commands=[]
 common=parent['commands'][0]
 for kind,src,out in[('main',O/'entrypoint.s',O/'main.o'),('skin',P/'kamikaze_chr.s',O/'skin.o'),('gb',O/'component.s',O/'gb.o')]:
  cmd=common[:];cmd[cmd.index('-o')+1]=str(out);cmd[cmd.index('--create-full-dep')+1]=str(O/(kind+'.d'));cmd[-1]=str(src)
  j=cmd.index('-I');cmd[j:j]=['-I',str(O/'src')]
  z=subprocess.run(cmd,cwd=R,capture_output=True,text=True);assert not z.returncode,(kind,z.stdout,z.stderr)
  commands.append(cmd)
 link=parent['commands'][-1][:]
 # Reuse the genuine C runtime object and exact approved Kamikaze payload.
 for i,v in enumerate(link):
  for before,after in[(str(P/'overlay/smb1base-mmc5-expanded.cfg'),str(O/'smb1base-mmc5-expanded.cfg')),(str(P/'main-full.o'),str(O/'main.o')),(str(P/'skin-full.o'),str(O/'skin.o')),(str(P/'independent.nes'),str(O/'candidate.nes')),(str(P/'independent.dbg'),str(O/'candidate.dbg')),(str(P/'independent.lbl'),str(O/'candidate.lbl'))]:v=v.replace(before,after)
  link[i]=v
 link.append(str(O/'gb.o'))
 z=subprocess.run(link,cwd=R,capture_output=True,text=True);(O/'build.log').write_text(z.stdout+z.stderr);assert not z.returncode,z.stderr
 commands.append(link)
 from prepare_cv3_dmc_mirror import prepare
 prepare(R,O/'candidate.nes');new=scoped_load(O/'candidate.nes')
 changes={k:sum(a!=z for a,z in zip(b['raw'][16+k*8192:16+(k+1)*8192],new['raw'][16+k*8192:16+(k+1)*8192]))for k in range(128)};changes={k:v for k,v in changes.items()if v}
 assert set(changes)<={30,31,66},changes
 allowed={30:[(address(b,'ExpandedPose::Pit'),address(b,'ExpandedPose::Rygar'))],31:[(0xdde6,0xe000)],66:[(address(b,'CrossoverMenuInput::Navigation'),address(b,'CrossoverMenuInput::Navigation')+18),(address(b,'QueueSelectName'),address(b,'QueueSelectName')+18),(0xb600,0xb680)]}
 for bank,count in changes.items():
  base=0xc000 if bank==31 else 0xa000
  for offset,(v,z)in enumerate(zip(b['raw'][16+bank*8192:16+(bank+1)*8192],new['raw'][16+bank*8192:16+(bank+1)*8192])):
   if v!=z:assert any(lo<=base+offset<hi for lo,hi in allowed[bank]),('unexpected changed byte',bank,hex(base+offset))
 assert new['raw'][1048592+808*1024:1048592+813*1024]==pixels
 assert b['raw'][1048592:1048592+808*1024]==new['raw'][1048592:1048592+808*1024]
 assert b['raw'][1048592+813*1024:]==new['raw'][1048592+813*1024:]
 deps={}
 for name in['main','skin','gb']:
  for word in re.split(r'(?<!\\)\s+',(O/(name+'.d')).read_text().split(':\t',1)[1].strip().removesuffix(':')):
   p=Path(word.replace('\\ ',' '));p=(p if p.is_absolute()else R/p).resolve();assert p.is_file();deps[str(p)]=sha(p)
 ids={s.get('id')for n,s in b['syms'].items()if'::'in n};moves=[]
 for n,s in b['syms'].items():
  if n=='_FARCALL_COUNT'or'LOCAL-MACRO_SYMBOL-'in n or'$anon-SCOPE-'in n or('::'not in n and s.get('id')in ids):continue
  assert n in new['syms'],n
  if address(b,n)!=address(new,n):moves.append([n,hex(address(b,n)),hex(address(new,n))])
 assert not moves,moves
 (O/'pose-layout.json').write_text(json.dumps(dict(passed=True,all252=targets,changed_records_both_faces_bytes=154,source_basis='Retold IPS plus explicitly corroborated unchanged original bytes; existing host composites preserved'),indent=2)+'\n')
 (O/'source.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),expanded.splitlines(True),fromfile='parent/expanded.s',tofile='private/expanded.s'))+''.join(difflib.unified_diff((P/'overlay/src/character_select.s').read_text().splitlines(True),menu.splitlines(True),fromfile='parent/character_select.s',tofile='private/character_select.s')))
 proof=dict(assembled=True,native_run=False,candidate=sha(O/'candidate.nes'),DBG=sha(O/'candidate.dbg'),LBL=sha(O/'candidate.lbl'),parent=sha(P/'candidate.nes'),changes=changes,only_approved_actual_byte_ranges=allowed,old_public_PCs_exact=True,compiler_local_name_note='Two same-bank farcall macros become proper direct calls; compiler-generated LOCAL-MACRO_SYMBOL ordinal names regenerate, never aliased. All genuine named PCs and unrelated instruction bytes exact.',commands=commands,actual_dependencies=deps,render_end=hex(address(new,'GbPitRenderEnd')),menu_end=hex(address(new,'GbPitMenuEnd')))
 (O/'build-proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({k:v for k,v in proof.items()if k not in['commands','actual_dependencies']}))
if __name__=='__main__':main()
