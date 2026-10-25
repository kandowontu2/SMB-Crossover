"""Compose two existing bounded proposals on a frozen, reproducible49 input."""
from pathlib import Path
import argparse,difflib,hashlib,json,shutil,subprocess,sys
from check_tmnt_render_oa import load

ROOT=Path(__file__).resolve().parents[2]
BASE='49d980e564abfb8bfc71bf0c69d5f25c91afed0968d231f959252fa53552b174'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--frozen',type=Path,required=True)
 p.add_argument('--baseline',type=Path,required=True)
 p.add_argument('--output',type=Path,required=True)
 a=p.parse_args();assert sha(a.baseline)==BASE
 a.output.mkdir(exist_ok=False)
 source=a.output/'source';shutil.copytree(a.frozen,source)
 before={}
 def replace(name,old,new):
  q=source/name;s=q.read_text();assert s.count(old)==1,(name,s.count(old))
  before[name]=s;q.write_text(s.replace(old,new))
 replace('src/expanded_weapons.s','  lda XgWall\n  bne ExistingAttackDone\n  lda InvSelected+CHARACTER_RYU',
         ' .if ::ENABLE_MMC5_EXPANDED\n  jsr RyuPrimaryBlocked\n .else\n  lda XgWall\n .endif\n  bne ExistingAttackDone\n  lda InvSelected+CHARACTER_RYU')
 replace('src/remaining_weapons.s','  sta AvItem\n  jsr CountType\n  lda AvCount\n  jne Return\n  lda #1\n  ldy #3',
         '  sta AvItem\n .if ::ENABLE_MMC5_EXPANDED\n  jsr SophiaTripletAdmission\n .else\n  jsr CountType\n .endif\n  lda AvCount\n  jne Return\n  lda #1\n  ldy #3')
 helpers={
 'src/cv3_ryu_audit_sword_guard.s':'; Source2.02 Ryu.pressAtkBtn rejects primary while Jump Slash remains live.\n.pushseg\n.segment "EXPANDED_EX"\n.proc RyuPrimaryBlocked\n  lda XgWall\n  ora AvSlash\n  rts\n.endproc\n.popseg\n',
 'src/audit_sophia_triplet_gate.s':'; Reserve all three shared projectile slots before spending one missile volley.\n; Existing missile-type occupancy retains the native one-volley limit.\n.pushseg\n.segment "SPECIAL_EXTRA"\n.proc SophiaTripletAdmission\n ldx #9\n ldy #3\nLoop:\n lda RgShotType,x\n bne Next\n dey\n beq Enough\nNext:\n dex\n bpl Loop\n sty AvCount\n rts\nEnough:\n jmp RemainingWeapons::CountType\n.endproc\n.popseg\n'}
 for name,text in helpers.items():
  q=source/name;assert not q.exists();before[name]='';q.write_text(text)
 ep=source/'src/entrypoint.s';before['src/entrypoint.s']=ep.read_text()
 with ep.open('a')as f:f.write('\n.if ::ENABLE_MMC5_EXPANDED\n.include "cv3_ryu_audit_sword_guard.s"\n.include "audit_sophia_triplet_gate.s"\n.endif\n')
 patch=''.join(''.join(difflib.unified_diff(old.splitlines(True),(source/name).read_text().splitlines(True),fromfile='a/'+name if old else '/dev/null',tofile='b/'+name))for name,old in before.items())
 (a.output/'implementation.patch').write_text(patch)
 out=a.output/'candidate.nes'
 command=[sys.executable,str(ROOT/'tools/build_mmc5_expanded.py'),'--workspace',str(source),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(out)]
 with(a.output/'host-build.log').open('w')as f:subprocess.run(command,stdout=f,stderr=subprocess.STDOUT,check=True)
 old,new=load(a.baseline),load(out)
 labels=lambda path:{q[2]:q[1]for line in path.read_text().splitlines()if len(q:=line.split())==3}
 ol,nl=labels(a.baseline.with_suffix('.lbl')),labels(out.with_suffix('.lbl'))
 assert all(nl[n]==v for n,v in ol.items())
 ram={n:int(s['val'],0)for n,s in old['syms'].items()if s.get('seg')and int(s['val'],0)<0x8000}
 assert all(n in new['syms']and int(new['syms'][n]['val'],0)==v for n,v in ram.items())
 assert old['raw'][16+1048576:]==new['raw'][16+1048576:]
 changed=[i for i,(x,y)in enumerate(zip(old['raw'],new['raw']))if x!=y]
 proof=dict(passed=True,private=True,adopted=False,goal_complete=False,baseline_sha256=BASE,ROM_sha256=sha(out),patch_sha256=sha(a.output/'implementation.patch'),changed_bytes=len(changed),changed_PRG_banks=sorted({(i-16)//8192 for i in changed}),existing_exported_labels_exact=True,existing_RAM_labels_exact=True,all_CHR_exact=True,new_RAM_bytes=0,source_files={n:sha(source/n)for n in before},scope='Composition of the existing seven-byte Ryu slash guard and24-byte Sophia triplet gate. Native qualification pending.')
 (a.output/'build-proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))

if __name__=='__main__':main()
