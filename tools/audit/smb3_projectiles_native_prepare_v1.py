"""Freeze current build inputs and compose the private SMB3 projectile repair."""
from pathlib import Path
import argparse,difflib,hashlib,json,shutil,subprocess,sys
from check_tmnt_render_oa import load,address,location
ROOT=Path(__file__).resolve().parents[2]


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


HELPER='''; SMB3 projectiles retain source weapon admission/lifetime against SMB foes.
; Bowser damage uses the host's existing HP and native defeat progression.
.pushseg
.segment "M3_LOGIC"
.proc M3ProjectileAdmission
 lda Enemy_ID,y
 cmp #Bowser
 beq Allowed
 cmp #BuzzyBeetle
 bne Ordinary
 ldx M3SavedSlot
 lda M3ShotKind,x
 cmp #2
 bne BeetleFire
 lda #0 ; Only the following temporary ID filters see this value.
Allowed:clc
 rts
BeetleFire:lda #BuzzyBeetle
Ordinary:cmp #$15
 rts
.endproc
.proc M3ProjectileDamage
 lda Enemy_ID,x
 cmp #Bowser
 beq Boss
 jmp M3DefeatEnemy
Boss:stx R1
 jmp HandleEnemyFBallCol
.endproc
.popseg
'''


def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--parent',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False)
 frozen=out/'baseline-source';frozen.mkdir()
 for name in ['src','inc','chr','audio']:shutil.copytree(ROOT/name,frozen/name)
 shutil.copytree(ROOT/'build/generated',frozen/'build/generated')
 for path in [ROOT/'build_options.ini',*ROOT.glob('*.cfg')]:shutil.copy2(path,frozen/path.name)
 before={str(q.relative_to(frozen)):sha(q)for q in frozen.rglob('*')if q.is_file()}
 (out/'frozen-inputs.json').write_text(json.dumps(before,indent=2)+'\n')
 compiler=ROOT/'tools/Windows/cc65/bin/cl65.exe';builder=ROOT/'tools/build_mmc5_expanded.py'
 def build(source,name):
  with(out/(name+'.host.log')).open('w')as log:
   result=subprocess.run([sys.executable,str(builder),'--workspace',str(source),'--compiler',str(compiler),'--output',str(out/(name+'.nes'))],cwd=source,stdout=log,stderr=subprocess.STDOUT)
  assert result.returncode==0,(out/(name+'.host.log')).read_text()[-5000:]
 build(frozen,'baseline')
 assert sha(out/'baseline.nes')==sha(a.parent),'Frozen baseline does not reproduce supplied parent'
 stage=out/'source';shutil.copytree(frozen,stage)
 target=stage/'src/smb3_mario_combat.s';old=target.read_text()
 token=' lda Enemy_ID,y\n cmp #$15\n jcs Next\n cmp #Podoboo\n'
 assert old.count(token)==1
 new=old.replace(token,' jsr M3ProjectileAdmission\n nop\n nop\n jcs Next\n cmp #Podoboo\n')
 at=new.index('.proc M3ShotEnemies');head,tail=new[:at],new[at:]
 assert tail.count(' jsr M3DefeatEnemy\n')==1
 new=head+tail.replace(' jsr M3DefeatEnemy\n',' jsr M3ProjectileDamage\n')
 target.write_text(new)
 entry=stage/'src/entrypoint.s';entry_old=entry.read_text()
 entry_new=entry_old+'\n.if ::ENABLE_MMC5_EXPANDED\n.include "smb3_projectile_damage.s"\n.endif\n'
 entry.write_text(entry_new);(stage/'src/smb3_projectile_damage.s').write_text(HELPER)
 patch=''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/src/smb3_mario_combat.s',tofile='b/src/smb3_mario_combat.s'))
 patch+=''.join(difflib.unified_diff(entry_old.splitlines(True),entry_new.splitlines(True),fromfile='a/src/entrypoint.s',tofile='b/src/entrypoint.s'))
 patch+=''.join(difflib.unified_diff([],HELPER.splitlines(True),fromfile='/dev/null',tofile='b/src/smb3_projectile_damage.s'))
 (out/'implementation.patch').write_text(patch)
 build(stage,'candidate')
 oldb,newb=load(out/'baseline.nes'),load(out/'candidate.nes')
 assert len(oldb['raw'])==len(newb['raw'])
 changes=[i for i,(x,y)in enumerate(zip(oldb['raw'],newb['raw']))if x!=y]
 assert len(changes)==51 and {(i-16)//8192 for i in changes}=={90}
 oldlabels={q[2]:q[1]for line in(out/'baseline.lbl').read_text().splitlines()if len(q:=line.split())==3}
 newlabels={q[2]:q[1]for line in(out/'candidate.lbl').read_text().splitlines()if len(q:=line.split())==3}
 assert all(newlabels[n]==v for n,v in oldlabels.items()),'Existing exported code/RAM label moved'
 assert oldb['raw'][16+1048576:]==newb['raw'][16+1048576:]
 assert all(sha(frozen/n)==h for n,h in before.items()),'Frozen baseline inputs mutated'
 report=dict(prepared=True,accepted=False,parent_sha256=sha(a.parent),fresh_frozen_baseline_sha256=sha(out/'baseline.nes'),candidate_sha256=sha(out/'candidate.nes'),changed_bytes=len(changes),changed_PRG_banks=[90],all_existing_exported_PC_RAM_labels_unchanged=True,all_CHR_unchanged=True,production_helper_guarded_by_ENABLE_MMC5_EXPANDED=True,frozen_build_input_count=len(before),frozen_input_manifest_sha256=sha(out/'frozen-inputs.json'),driver_sha256=sha(Path(__file__)),source_changes={n:sha(stage/n)for n in ['src/entrypoint.s','src/smb3_mario_combat.s','src/smb3_projectile_damage.s']},limits='Private pending final-hash native/CPU qualification and root adoption. Native SMB1 five-HP balance; source SMB3 hammer contact persists per overlap update and source boss requires35hits.')
 (out/'prepare.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))


if __name__=='__main__':main()
