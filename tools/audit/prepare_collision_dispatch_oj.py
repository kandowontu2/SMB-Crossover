"""Isolate a shallow exact collision-leaf router from the accepted OG source."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[2]
PARENT=ROOT/'build/checkpoints/inventory-stack-og'
SOURCE='''; These collision queries receive the raw character ID in A. Preserve the
; original Roll selected-alternate override, and retain the old full router
; for mismatched/unsupported input. Actual native profile leaves stay intact.
.pushseg
.segment "HOT_COLLISION_GATE"
.macro HotCollision Name,OwnRoll,Kirby,Chip,Mac,Mike,Mario3,Vic,Turtle,Original
.proc Name
 php
 pha
 lda SelectedCharacter
 cmp #CHARACTER_BASS
 bne NotRoll
 lda RlVariant
 beq NotRoll
 pla
 plp
 farcall OwnRoll,jmp
NotRoll:
 pla
 pha
 cmp SelectedCharacter
 jne Fallback
 cmp #20
 jcs Fallback
 cmp #14
 bcc ToKirby
 beq ToChip
 cmp #15
 beq ToMac
 cmp #16
 beq ToMike
 cmp #17
 beq ToMario3
 cmp #18
 beq ToVic
 ; Only19 remains; its existing native leaf retains its exact flag contract.
 pla
 plp
 farcall Turtle,jmp
ToKirby:
 pla
 plp
 farcall Kirby,jmp
ToChip:
 pla
 plp
 farcall Chip,jmp
ToMac:
 pla
 plp
 ; Both exact-ID Mac leaves are LDY0 and return carry set by CMP15.
 ; Reuse that three-instruction result without another bank round trip.
 ldy #0
 sec
 rts
ToMike:
 pla
 plp
 farcall Mike,jmp
ToMario3:
 pla
 plp
 farcall Mario3,jmp
ToVic:
 pla
 plp
 farcall Vic,jmp
Fallback:
 pla
 plp
 farcall Original,jmp
.endproc
.endmacro
HotCollision HotCollisionAdder,RlAdder,KbAdderDispatch,CdAdderDispatch,LmAdderGate,JnAdderDispatch,M3AdderDispatch,VvAdderDispatch,TnAdderDispatch,RlAdderDispatch
HotCollision HotCollisionBox,RlBox,KbBoxDispatch,CdBoxDispatch,LmBoxGate,JnBoxDispatch,M3BoxDispatch,VvBoxDispatch,TnBoxDispatch,RlBoxDispatch
.popseg
'''


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    out=a.output.resolve();out.mkdir(parents=True,exist_ok=False);stage=out/'source'
    m=json.loads((PARENT/'manifest.json').read_text())
    assert sha(PARENT/'source.zip')==m['source_zip_sha256'] and sha(PARENT/'candidate.nes')==m['rom_sha256']
    with zipfile.ZipFile(PARENT/'source.zip') as z:
        assert z.testzip() is None
        assert all((stage/n).resolve().is_relative_to(stage.resolve()) for n in z.namelist())
        z.extractall(stage)
    assert all(sha(stage/n)==h for n,h in m['source_files'].items())
    changes={}
    edits={
      'src/expanded.s': [('farcall RlAdderDispatch,jmp','farcall HotCollisionAdder,jmp'),('farcall RlBoxDispatch,jmp','farcall HotCollisionBox,jmp')],
      'src/entrypoint.s': [('.include "inventory_legacy_leaf.s"','.include "inventory_legacy_leaf.s"\n.include "hot_collision_gate.s"')],
      'smb1base-mmc5-expanded.cfg': [('    INVENTORY_LEGACY_LEAF: load=X5_NEW_42,type=ro;','    INVENTORY_LEGACY_LEAF: load=X5_NEW_42,type=ro;\n    HOT_COLLISION_GATE: load=X5_NEW_42,type=ro;')],
    }
    for name,pairs in edits.items():
        f=stage/name;text=f.read_text();before=sha(f)
        for old,new in pairs:assert text.count(old)==1,(name,old);text=text.replace(old,new)
        f.write_text(text);changes[name]=dict(before=before,after=sha(f))
    f=stage/'src/hot_collision_gate.s';assert not f.exists();f.write_text(SOURCE)
    changes['src/hot_collision_gate.s']=dict(before=None,after=sha(f))
    z=subprocess.run([sys.executable,str(stage/'tools/build_mmc5_expanded.py'),'--workspace',str(stage),
        '--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(out/'candidate.nes')],cwd=stage,capture_output=True,text=True)
    (out/'build.log').write_text(z.stdout+z.stderr);assert z.returncode==0,(z.stdout+z.stderr)[-3000:]
    old=(PARENT/'candidate.nes').read_bytes();new=(out/'candidate.nes').read_bytes()
    assert len(old)==len(new) and old[:16]==new[:16] and old[16+1048576:]==new[16+1048576:]
    changed=[i for i in range(128) if old[16+i*8192:16+(i+1)*8192]!=new[16+i*8192:16+(i+1)*8192]]
    assert len(changed)==2 and 66 in changed
    def labels(p):return {q[2]:q[1] for line in p.read_text().splitlines() if len(q:=line.split())==3}
    before=labels(PARENT/'candidate.lbl');after=labels(out/'candidate.lbl')
    assert all(after[n]==v for n,v in before.items()),'A pre-existing linked address moved'
    proof=dict(prepared=True,accepted=False,parent_ROM_sha256=m['rom_sha256'],ROM_sha256=sha(out/'candidate.nes'),
        source_changes=changes,changed_PRG_banks=changed,CHR_unchanged=True,all_preexisting_labels_unchanged=True,
        scope='Isolated two-query router. Native collision leaves, RAM and movement are unchanged. Requires full actual-leaf CPU/IRQ differentials and matched native performance/contacts before adoption.')
    (out/'preparation.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2))


if __name__=='__main__':main()
