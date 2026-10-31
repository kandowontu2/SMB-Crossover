"""Freeze source-only pending-ROM/lives palette repair; no admission/native claim."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from prepare_ff_joint_source_v1 import validate
from finalize_ff_current_component_v3 import dependencies
O=R/'build/smb2-late-lives-palette-v6';J=O/'joint';P=R/'build/arthur-goku-smb2-palette-v1';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):assert not p.exists();p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8',newline='\n')
def main():
 assert not(O/'handoff.json').exists();files=validate(P/'handoff.json','93cf798479a206ea7ee1e08d503c8357fbee211b85d468d1b471313ab5592482')
 proofs=[O/'source-proof.json',R/'build/smb2-late-lives-controls-v3/controls.json',R/'build/smb2-late-lives-isr-v2/controls.json']
 for p in proofs:
  h=json.loads(p.read_text());assert h['passed'],p
  for n,v in h.get('bindings',{}).items():assert sha(n)==v,n;files.add(Path(n))
  files.add(p)
 files|=set(dependencies(J/'component.dep'));files|={p for p in O.rglob('*')if p.is_file()}
 for n in json.loads((O/'final-link.json').read_text())['command']:
  if n.endswith('.o'):files.add(Path(n))
 own=[J/'smb2/smb2_roster.s',J/'smb2/smb2_roster_host_v5.s'];files|=set(own)
 for stem,versions in [('prepare_smb2_late_lives_palette_',range(1,7)),('smb2_late_lives_controls_',range(1,4)),('smb2_late_lives_isr_',range(1,3))]:
  for v in versions:files.add(R/'tools/audit'/f'{stem}v{v}.py')
 files.add(Path(__file__))
 for d in['smb2-late-lives-palette-v1','smb2-late-lives-palette-v2','smb2-late-lives-palette-v3','smb2-late-lives-palette-v4','smb2-late-lives-palette-v5','smb2-late-lives-controls-v1','smb2-late-lives-controls-v2','smb2-late-lives-isr-v1']:
  files|={p for p in(R/'build'/d).glob('*.json')if p.is_file()}
 diag=R/'build/smb2-lives-palette-diagnostic-v1/class0';files|={diag/'ready.json',diag/'observer.diff'}|set((diag/'capture').glob('*'))
 st=dict(status='PRIVATE_SOURCE_LIVES_PENDING_ROM_ORDER_REPAIRED_NATIVE_PENDING',candidate=sha(J/'candidate.nes'),parent=sha(P/'joint/candidate.nes'),owned_sources=[str(p)for p in own],new_code166of219=True,wrapper71B_public_PC_exact=True,source_only=True,native=False)
 save(O/'source-stage.json',st);files.add(O/'source-stage.json')
 text='''Own SMB2 late lives palette successor of immutable combined37210891. Native not run; not installed.

Authoritative native negative: pending ROM palette3 caused SetupIntermediate's source palette to defer atframe193. Native bulk atframe194 set P0=162718. Portrait frame197 queued3f100422011627 atoffset7 andACK0, then actual WriteGameText::GameTextLoop STA VRAM_Buffer1,Y overwrote it frombyte0. Next normalNMI consumed text only; firstlives DMAframe198 had P0=162718,P2=163027,BG0F. No R0/R1 NMI-clobber evidence. The old source8cold tests used1Main/NMI, flushing ROM3 beforeSetupIntermediate, so they did not cover this legal native ordering. Those bounded CPU cases remain valid for their scheduled inputs; they are not general native lifecycle proof.

The new source regression calls actualInitScreen andSetupIntermediate before SAME normalNMI whileROM3pending, then realbulk,portrait,WriteGameText andactualNMI/DMA. Parent3721 faithfully reproduceswrongP0; all8new class/rule cohorts nowfirstDMAoriginalP0+blackBG, thenrealentrance+64controlledMainTOTAL retainblue22.

Repair stays in own S2MenuStatus71B and166B of existing219B CD25..<CE00 sourcealignment. Existing15B CD16..<CD25 renderer helper/publicPCs/allotherowners/header/CHR/final125 are exact. Selected wrapper retains originalA onstack, savesX/Y, mapsC80 using exact selected S2GraphicsBank stores, calls ownnearC80worker, restoresC before returning from A74. A0 name path retains originalnamecopy and actualgenuineGraphicsBank child-call/SFC outputs. OtherA values/invalidA1-Y remain unchanged. RealA1/Y30 posttext callback alone setsactualoffset30, invalidatesACK, temporarilyswitchesBGctrl2, queueswholeblack/nativeBG+originalP0, restoresBGctrl andR0..7, all5mutableSFCoperands andoriginalAXYP/C. NativeWriteGameText's remainingnumberpatches12/23/25 arebelow appendedpalette30..37. PublishedROM rejection retainsACKFF forretry; no fullqueue/canary corruption. No newRAM/CHR/PRGlease orcommonedit.

Qualification:1024 actual nonlives service30 old/new full64distinctflag pairs;512actual lateclass/flag/publishedqueue-reclaim/retry cases;128 real lagNMI/IRQcuts includingexactpendingCshadow/store intervals preserveAXYP/SP/livepage1/all33SMC/R0..7/maps and converge toactualnormalNMI/PPUcorrectpalette. All8actualpending-ROM cold/lives/entrance+64MainTOTAL pass. Nativehardware/visibleUI next; no60Hz/levelclear claim.

Retained preparation negatives: v1guard enumerated BSS symbol with no output offset;v2wrapper did not fit71B;v3generic local label collision aftersource link;v4name-return registers matched but oldgenuinechildSFCoutputs differed;v5longbranch requiredactualJNE;v6retainsgenuineA0call andpreservesnewA1borrowedoperands. Controls v2 stopped ownCPU process after discovering oldflags formula covered32uniquevectors in64rows and unnecessarilydeepcopiedimmutableROM/DBG; v3uses64distinctflags and sharesonlyreadonlyROM/DBG/labels whilecopyingallRAM/WRAM/PPU/mapper/stack state. ISR v1cut122cases excludedfinal4bytes dueoldhardcoded162;v2derivesactual166B andpasses128cuts. No frozenreceipt/source changed.

Adoption: copy ONLY actualowned smb2_roster.s andsmb2_roster_host_v5.s into CURRENT actualS2include precedence, preservingprevious BG/eye threeproducers+asset. Recompileactualcomponent andlinkgenuinecurrentowner objects, no oldmain/cfg/commoncopies. Config differsoutputpaths only, no segmentgrowth. Exact206ownROMbyte delta against3721. Guardeveryoutput/dep/cfg/DBG/mapbeforecompiler; finalizeactual125mirror source. No native grant or downloadinstall conferred.
'''
 p=O/'README.txt';assert not p.exists();p.write_text(text,encoding='utf-8',newline='\n');files.add(p)
 h=dict(passed=True,status=st['status'],candidate=st['candidate'],candidate_path=str(J/'candidate.nes'),parent=st['parent'],native=False,installed=False,owned_source_producers=st['owned_sources'],source_proof=str(O/'source-proof.json'),actual_controls=[str(p)for p in proofs[1:]],recipes=[str(O/n)for n in['component-build.json','final-link.json']],native_negative=str(diag/'capture/palette-write-order.csv'),bindings={str(p.resolve()):sha(p)for p in sorted(files)if p.is_file()})
 save(O/'handoff.json',h)
 for p,v in h['bindings'].items():assert sha(p)==v,p
 print(json.dumps(dict(handoff=str(O/'handoff.json'),sha256=sha(O/'handoff.json'),candidate=h['candidate'],bindings=len(h['bindings']))),flush=True)
if __name__=='__main__':main()
