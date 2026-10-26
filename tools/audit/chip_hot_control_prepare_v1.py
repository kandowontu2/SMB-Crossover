"""Prepare one private Chip movement/side-admission optimization against frozen8b4."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def edit(path,old,new):
 raw=path.read_bytes();eol=b'\r\n'if b'\r\n'in raw else b'\n';old=old.replace('\n',eol.decode()).encode();new=new.replace('\n',eol.decode()).encode();assert raw.count(old)==1,(path,raw.count(old));path.write_bytes(raw.replace(old,new))
def build(src,out):
 cmd=[sys.executable,str(ROOT/'tools/build_mmc5_expanded.py'),'--workspace',str(src),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(out)];q=subprocess.run(cmd,capture_output=True,text=True,cwd=ROOT);out.with_suffix('.host.log').write_text(q.stdout+q.stderr);assert q.returncode==0,q.stdout[-3000:]+q.stderr[-3000:]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);src=a.output/'source';shutil.copytree(D/'cv3-remaining-current50b-v1/baseline-source',src)
 for f in(D/'root-chip-native-adapter-v6/source').rglob('*'):
  if f.is_file():q=src/f.relative_to(D/'root-chip-native-adapter-v6/source');q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,q)
 build(src,a.output/'parent-rebuild.nes');assert sha(a.output/'parent-rebuild.nes')=='8b4accd2672b4b85508a365f81f499fb786f25e5572932aafc21837d5e591824'
 old='''::X5OwnMovementCall:
  jsr X5OwnMovement
  .res 15,$ea
  php'''
 new='''::X5OwnMovementCall:
  jsr X5OwnMovement
 .if ::MAPPER_MMC5
  jmp CameraResult
  .res 12,$ea
CameraResult:
 .else
  .res 15,$ea
 .endif
  php''';edit(src/'src/x5_bounce.s',old,new)
 old='''.proc X5OwnMovement
  php
  pha
  lda SelectedCharacter
  cmp #19
  bne Legacy
  pla
  plp
  farcall TnMovement,jmp
Legacy:
  pla
  plp
  farcall LmMovementGate,jmp
.endproc'''
 new='''.proc X5OwnMovement
 .if ::MAPPER_MMC5
  jmp CdCameraMovementAdmission
  .res 46,$ea
 .else
  php
  pha
  lda SelectedCharacter
  cmp #19
  bne Legacy
  pla
  plp
  farcall TnMovement,jmp
Legacy:
  pla
  plp
  farcall LmMovementGate,jmp
 .endif
.endproc''';edit(src/'src/x5_bounce.s',old,new)
 f=src/'src/x5_bounce.s';raw=f.read_bytes();eol=b'\r\n'if b'\r\n'in raw else b'\n';helper='''
; Exact Chip admission retains X5NewMovementFinish's pre-step camera sample.
; Other owners retain their real movement leaf. Skipped old camera padding
; pays for this admission on every foreign new-profile path.
.if ::MAPPER_MMC5
.pushseg
.segment "X5_BOUNCE"
.proc CdCameraMovementAdmission
  php
  pha
  lda SelectedCharacter
  cmp #14
  beq Chip
  cmp #19
  bne Legacy
  pla
  plp
  farcall TnMovement,jmp
Legacy:
  pla
  plp
  farcall LmMovementGate,jmp
Chip:
  pla
  plp
  farcall CdMovement,jmp
.endproc
.popseg
.endif
''';f.write_bytes(raw+helper.replace('\n',eol.decode()).encode())
 old='''::Z2NativeSideSelector:
   cmp #CHARACTER_LINK
   beq OwnZ2Side
   cmp #CHARACTER_SOPHIA
   rts
OwnZ2Side:sec
   rts
   .res 3,$ea'''
 new='''::MmSideDispatchPrefix:
   ; Former solecaller selector span: first ordered half of ordinary farcall.
   ; A/P have been restored before this genuine JMP-only helper entry.
   SMC_StoreValue SafecallA,a
   lda #<TnFastSideGate
   SMC_StoreLowByte FarcallJmpTarget,a
   jmp MmSideDispatchTail
   nop''';edit(src/'src/characters.s',old,new)
 old='''   php
   pha
   lda SelectedCharacter
   jsr Z2NativeSideSelector
   bcs OtherSide
   pla
   plp
   jmp BlockBufferColli_Side
OtherSide:
   pla
   plp
   farcall TnFastSideGate,jmp
   .res 2,$ea'''
 new='''   php
   pha
   lda SelectedCharacter
   cmp #CHARACTER_LINK
   beq OtherSide
   cmp #14
   beq NativeSide
   cmp #CHARACTER_SOPHIA
   bcs OtherSide
NativeSide:
   pla
   plp
   jmp BlockBufferColli_Side
OtherSide:
   pla
   plp
   jmp MmSideDispatchPrefix
::MmSideDispatchTail:
   lda #>TnFastSideGate
   SMC_StoreHighByte FarcallJmpTarget,a
   lda #.bank(TnFastSideGate)|MMC5_PRG_ROM
   jmp FarCallCommon''';edit(src/'src/megaman_weapons.s',old,new)
 build(src,a.output/'candidate.nes');parent=(a.output/'parent-rebuild.nes').read_bytes();candidate=(a.output/'candidate.nes').read_bytes();banks={str(k):sum(x!=y for x,y in zip(parent[16+k*8192:16+(k+1)*8192],candidate[16+k*8192:16+(k+1)*8192]))for k in range(128)};banks={k:v for k,v in banks.items()if v};assert parent[:16]==candidate[:16]and parent[16+128*8192:]==candidate[16+128*8192:];assert set(banks)=={'86','126','127'}
 files=[]
 for name in ['x5_bounce.s','characters.s','megaman_weapons.s']:
  f=src/'src'/name;files.append(dict(path=str(f),sha256=sha(f)))
 proof=dict(prepared=True,accepted=False,native_run=False,parent_ROM_sha256=sha(a.output/'parent-rebuild.nes'),candidate_ROM_sha256=sha(a.output/'candidate.nes'),changed_PRG_banks=banks,all_header_CHR_and_other_banks_exact=True,source_files=files,tool_sha256=sha(__file__),scope='Unqualified source-only Chip hot-control proposal; complete caller/IRQ/SMC/foreign controls still required. No source audio or RAM allocation changed.')
 (a.output/'preparation.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2))
if __name__=='__main__':main()
