"""Private, same-PC Sophia triplet reservation proposal; never install it."""
from pathlib import Path
import argparse,difflib,hashlib,json,shutil,subprocess,sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import scoped_load


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--frozen-source',type=Path,required=True)
    p.add_argument('--baseline',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    overlay=a.output/'source';shutil.copytree(a.frozen_source,overlay)
    changes=[]
    def rewrite(name,old,new):
        q=overlay/name;before=q.read_bytes();s=before.decode()
        assert s.count(old)==1,(name,s.count(old))
        after=s.replace(old,new).encode();q.write_bytes(after)
        changes.append(''.join(difflib.unified_diff(before.decode().splitlines(True),after.decode().splitlines(True),fromfile='a/'+name,tofile='b/'+name)))
    rewrite('src/remaining_weapons.s',
        '  sta AvItem\r\n  jsr CountType\r\n  lda AvCount\r\n  jne Return\r\n  lda #1\r\n  ldy #3',
        '  sta AvItem\r\n  jsr SophiaTripletAdmission\r\n  lda AvCount\r\n  jne Return\r\n  lda #1\r\n  ldy #3')
    helper='''; Reserve all three shared projectile slots before spending one missile volley.
; Existing missile-type occupancy retains the native one-volley limit.
.pushseg
.segment "SPECIAL_EXTRA"
.proc SophiaTripletAdmission
 ldx #9
 ldy #3
Loop:
 lda RgShotType,x
 bne Next
 dey
 beq Enough
Next:
 dex
 bpl Loop
 sty AvCount ; positive missing-slot count refuses the volley before spending.
 rts
Enough:
 jmp RemainingWeapons::CountType
.endproc
.popseg
'''
    helper=helper.replace('\n','\r\n')
    (overlay/'src/audit_sophia_triplet_gate.s').write_bytes(helper.encode())
    ep=overlay/'src/entrypoint.s';s=ep.read_bytes()
    tail=b'\r\n.if ::ENABLE_CROSSOVER\r\n.include "audit_sophia_triplet_gate.s"\r\n.endif\r\n'
    ep.write_bytes(s+tail)
    changes.append(''.join(difflib.unified_diff(s.decode().splitlines(True),(s+tail).decode().splitlines(True),fromfile='a/src/entrypoint.s',tofile='b/src/entrypoint.s')))
    changes.append(''.join(difflib.unified_diff([],helper.splitlines(True),fromfile='/dev/null',tofile='b/src/audit_sophia_triplet_gate.s')))
    (a.output/'implementation.patch').write_bytes(''.join(changes).encode())
    candidate=a.output/'candidate.nes'
    subprocess.run([sys.executable,str(ROOT/'tools/build_mmc5_expanded.py'),'--source-overlay',str(overlay),'--output',str(candidate)],check=True)
    old,new=scoped_load(a.baseline),scoped_load(candidate)
    old_labels={q[2]:q[1] for line in a.baseline.with_suffix('.lbl').read_text().splitlines() if len(q:=line.split())==3}
    new_labels={q[2]:q[1] for line in candidate.with_suffix('.lbl').read_text().splitlines() if len(q:=line.split())==3}
    assert all(new_labels[n]==v for n,v in old_labels.items()),'Existing exported PC moved'
    oldram={n:int(s['val'],0) for n,s in old['syms'].items() if s.get('seg') and int(s['val'],0)<0x8000}
    assert all(n in new['syms'] and int(new['syms'][n]['val'],0)==v for n,v in oldram.items())
    assert old['raw'][16+1048576:]==new['raw'][16+1048576:]
    changed=[i for i,(x,y) in enumerate(zip(old['raw'],new['raw'])) if x!=y]
    receipt=dict(parent_sha256=digest(a.baseline),ROM_sha256=digest(candidate),
        implementation_patch_sha256=digest(a.output/'implementation.patch'),
        changed_bytes=len(changed),changed_PRG_banks=sorted({(i-16)//8192 for i in changed}),
        existing_exported_labels_exact=True,existing_RAM_labels_exact=True,all_CHR_exact=True,
        scope='Private assembled candidate. Native integration and controller-reachable crowded firing scene remain unrun.')
    (a.output/'build-proof.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))


if __name__=='__main__':main()
