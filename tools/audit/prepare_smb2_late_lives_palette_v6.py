"""Own late lives text/palette lifecycle source successor, preserving current union."""
from pathlib import Path
import difflib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_ff_joint_source_v1 as B
from private_build_outputs_v1 import validate
from prepare_cv3_dmc_mirror import prepare
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
P=R/'build/arthur-goku-smb2-palette-v1';O=R/'build/smb2-late-lives-palette-v6';J=O/'joint';S=J/'smb2'
def write(p,s):p.write_text(s,encoding='utf-8',newline='\n')
def save(p,x):write(p,json.dumps(x,indent=2)+'\n')
def run(c,n):
 g=validate(c,O,cwd=R);z=subprocess.run(c,cwd=R,capture_output=True,text=True);save(O/(n+'.json'),dict(command=c,guard=g,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr));assert not z.returncode,z.stderr
WORKER='''.proc S2TextStatusC
S2LivesOwnStart:
 ; Near-called only with genuine C80 mapped by the source A74 wrapper.
 ; Y carries priorC, originalY is on the CPU stack below our JSR+PHY.
 phy
 txa                           ; wrapper X retains original sourceA.
 cmp #0
 beq S2TextName
 cmp #1
 jne S2TextDone
 tsx
 lda $0104,x
 cmp #30
 bne S2TextRejectLives
 ; Native WriteGameText has completed its30B lives commands. Its remaining
 ; number patches address only bytes12/23/25, below this appended palette.
 ldx #3
S2TextSaveScratch:
 lda R0,x
 pha
 dex
 bpl S2TextSaveScratch
 lda BackgroundColorCtrl
 pha
 lda #2
 sta BackgroundColorCtrl
 lda #30
 sta VRAM_Buffer1_Offset
 lda #$ff
 sta S2PaletteAck
 ; Preserve the caller-owned five actually mutable SFC operands.
 lda NextBank_SMC+1
 pha
 lda SafecallA_SMC+1
 pha
 lda FarcallJmpTarget_SMC+1
 pha
 lda FarcallJmpTarget_SMC+2
 pha
 lda SafereturnA_SMC+1
 pha
 farcall S2MainPalette
 pla
 sta SafereturnA_SMC+1
 pla
 sta FarcallJmpTarget_SMC+2
 pla
 sta FarcallJmpTarget_SMC+1
 pla
 sta SafecallA_SMC+1
 pla
 sta NextBank_SMC+1
 pla
 sta BackgroundColorCtrl
 ldx #0
S2TextRestoreScratch:
 pla
 sta R0,x
 inx
 cpx #4
 bne S2TextRestoreScratch
S2TextRejectLives:
 lda #1
 bne S2TextDone
S2TextName:
 ; Match original A0 child-call/SFC output exactly. Old PHY set its sourceA
 ; to originalY, found below this helper JSR+saved priorC.
 tsx
 lda $0104,x
 farcall S2GraphicsBank
 ldx #11
 lda #7
 sta R0
 jsr S2MenuCopyC
 ply
 ldy #80|$80                   ; original successful A0 status leaves C80.
 lda #0
 rts
S2TextDone:
 ply                           ; other inputs retain genuine priorC.
 rts
 .assert *-S2LivesOwnStart<=219,error,"Existing C80 source padding only"
 .res 219-(*-S2LivesOwnStart),$ff
.endproc'''
STATUS='''.proc S2MenuStatus
S2LivesOwnStart:
 php
 pha
 lda SelectedCharacter
 cmp #25
 beq Own
 pla
 plp
 farcall JnStatusName,jmp
Own:
 ; SourceA remains in the entry stack while originalX/Y are pushed.
 phx
 phy
 tsx
 lda $0103,x
 tax
 ldy CurrentBankC
 ; Exact selected path from source S2GraphicsBank, A74 remains mapped.
 lda #80|$80
 sta CurrentBankC
 sta $5116
 jsr S2TextStatusC
 sty CurrentBankC              ; A74 stays mapped while C is restored.
 sty $5116
 ply
 plx
 pla                           ; original sourceA0/1/other contract.
 plp
 rts
 .assert *-S2LivesOwnStart<=71,error,"Existing71B public Status envelope"
 .res 71-(*-S2LivesOwnStart),$ea
.endproc'''
def main():
 assert not O.exists();S.mkdir(parents=True);B.validate(P/'handoff.json','93cf798479a206ea7ee1e08d503c8357fbee211b85d468d1b471313ab5592482')
 a=scoped_load(P/'joint/candidate.nes');before=a['raw'];at=16+80*8192+0xd25;assert before[at:at+219]==b'\xff'*219
 # All existing actual parent object consumers of the data-only C80 filler
 # are bound. No symbol resolves into the interior of the219B padding.
 entrants=[n for n,s in a['syms'].items()if 'seg'in s and 'ooffs'in a['segs'][s['seg']] and (16+80*8192+0xd25)<=location(a,n)<(16+80*8192+0xe00)];assert not entrants,entrants
 for f in(P/'joint/smb2').iterdir():
  if f.is_file()and f.suffix in['.s','.inc']:(S/f.name).write_bytes(f.read_bytes())
 (J/'component.s').write_bytes((P/'joint/component.s').read_bytes());patch=''
 p=S/'smb2_roster_host_v5.s';old=p.read_text();start=old.index('.proc S2MenuStatus');end=old.index('.endproc',start)+len('.endproc');s=old[:start]+STATUS+old[end:];write(p,s);patch+=''.join(difflib.unified_diff(old.splitlines(True),s.splitlines(True),fromfile='parent/host.s',tofile='new/host.s'))
 p=S/'smb2_roster.s';old=p.read_text();assert old.count(' .res 219,$ff')==1;s=old.replace(' .res 219,$ff',WORKER);write(p,s);patch+=''.join(difflib.unified_diff(old.splitlines(True),s.splitlines(True),fromfile='parent/component.s',tofile='new/component.s'))
 cfg=(P/'joint/private.cfg').read_text().replace(str(P/'joint'),str(J)).replace((P/'joint').as_posix(),J.as_posix());write(J/'private.cfg',cfg)
 c=json.loads((P/'component-build.json').read_text())['command'][:];c[1:1]=['-I',str(J),'-I',str(S)]
 for flag in['-o','--create-full-dep','--create-dep']:
  if flag in c:c[c.index(flag)+1]=str(J/Path(c[c.index(flag)+1]).name)
 c[-1]=str(J/'component.s');run(c,'component-build')
 c=json.loads((P/'final-link.json').read_text())['command'][:]
 for i,x in enumerate(c):
  if x==str(P/'joint/component.o'):c[i]=str(J/'component.o')
  elif x in[str(P/'joint'/n)for n in['private.cfg','candidate.nes','candidate.lbl','candidate.map']]:c[i]=str(J/Path(x).name)
  elif x.startswith('--dbgfile,'):c[i]='--dbgfile,'+str(J/'candidate.dbg')
 run(c,'final-link');prepare(R,J/'candidate.nes');b=scoped_load(J/'candidate.nes');after=b['raw'];diff=[i for i,(u,v)in enumerate(zip(before,after))if u!=v]
 spans=[(location(a,'S2MenuStatus'),location(a,'S2MenuStatus')+71),(at,at+219)];assert all(any(lo<=i<hi for lo,hi in spans)for i in diff)
 # Native public PCs and every existing scoped public producer remain exact.
 moved={n:[address(a,n),address(b,n)]for n in a['syms']if'::'not in n and n in b['syms']and address(a,n)!=address(b,n)};assert not moved,moved
 assert before[:16]==after[:16]and before[1048592:]==after[1048592:]and before[16+125*8192:16+126*8192]==after[16+125*8192:16+126*8192]
 write(O/'source.patch',patch);save(O/'source-proof.json',dict(passed=True,parent=B.sha(P/'joint/candidate.nes'),candidate=B.sha(J/'candidate.nes'),exact_diff=diff,changed_bytes=len(diff),own71B_and219B_only=True,header_CHR_all_other_PRG_public_PCs_final125_exact=True,own_C80_FF_preimage_no_existing_symbol_entries=True,new_code_used=len(after[at:at+219].rstrip(b'\xff')),native=False,source_controls_pending=True))
 print(json.dumps(dict(candidate=B.sha(J/'candidate.nes'),output=str(O),changed_bytes=len(diff))),flush=True)
if __name__=='__main__':main()
