"""Compose current Mac/TMNT repairs without installing or changing ROOT."""
from pathlib import Path
import argparse,difflib,hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
BASE='55bcfb8209b628062ce1f833a2ed386bd6f08426d34fed9fa8b5ba1f90694be7'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True)
 a=p.parse_args();out=a.packet.resolve();assert sha(out/'baseline.nes')==BASE
 frozen=out/'frozen';manifest=json.loads((out/'frozen-source.json').read_text())
 assert all(sha(frozen/n)==v for n,v in manifest.items())
 command=[sys.executable,str(ROOT/'tools/build_mmc5_expanded.py'),'--workspace',str(frozen),
          '--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe')]
 subprocess.run(command+['--output',str(out/'rebuilt-baseline.nes')],check=True)
 assert sha(out/'rebuilt-baseline.nes')==BASE
 source=out/'source';shutil.copytree(frozen,source)
 changes={}
 def replace(name,old,new):
  f=source/name;before=f.read_text();assert before.count(old)==1,(name,before.count(old))
  f.write_text(before.replace(old,new));changes[name]=before
 replace('src/tmnt_equipment.s',' lda Enemy_X_Position,x\n clc\n adc #4\n sta EnemyBoundingBoxCoord,y\n lda Enemy_X_Position,x\n clc\n adc #12\n sta EnemyBoundingBoxCoord+2,y',
         ' jsr TnPickupScreenBox\n .res 13,$ea ; retain the original sixteen-byte span')
 replace('src/little_mac_core.s',' lda LmLife\n cmp NumberofLives\n jne NewLife',
         ' jsr LmLifeAdvanced\n jcc NewLife\n .res 3,$ea ; retain the original life-test span')
 f=source/'src/mac_tmnt_lifecycle.s';changes['src/mac_tmnt_lifecycle.s']=''
 shutil.copyfile(ROOT/'tools/audit/mac_tmnt_native_helpers.candidate.s',f)
 f=source/'src/entrypoint.s';changes['src/entrypoint.s']=f.read_text()
 with f.open('a')as q:q.write('\n.if ::ENABLE_MMC5_EXPANDED\n.include "mac_tmnt_lifecycle.s"\n.endif\n')
 patch=''.join(''.join(difflib.unified_diff(old.splitlines(True),(source/name).read_text().splitlines(True),fromfile='a/'+name if old else'/dev/null',tofile='b/'+name))for name,old in changes.items())
 (out/'implementation.patch').write_text(patch)
 candidate_command=command[:];candidate_command[candidate_command.index('--workspace')+1]=str(source)
 subprocess.run(candidate_command+['--output',str(out/'candidate.nes')],check=True)
 sys.path.insert(0,str(ROOT/'tools/audit'))
 from check_tmnt_audio_fallback_oc import qualified
 oldq,newq=qualified(out/'baseline.nes'),qualified(out/'candidate.nes')
 assert all(newq.get(n)==v for n,v in oldq.items()),[(n,v,newq.get(n))for n,v in oldq.items()if newq.get(n)!=v][:10]
 old,new=(out/'baseline.nes').read_bytes(),(out/'candidate.nes').read_bytes()
 assert old[16+1048576:]==new[16+1048576:]
 touched=[i for i,(x,y)in enumerate(zip(old,new))if x!=y]
 ordinary={}
 for mapper in ['mmc3','mmc5']:
  paths=[]
  for label,cmd in [('baseline',command),('candidate',candidate_command)]:
   dest=out/f'ordinary-{label}-{mapper}.nes';subprocess.run(cmd+['--flag-off',mapper,'--output',str(dest)],check=True);paths.append(dest)
  assert paths[0].read_bytes()==paths[1].read_bytes(),mapper
  ordinary[mapper]=sha(paths[0])
 proof=dict(passed=True,adopted=False,baseline_sha256=BASE,ROM_sha256=sha(out/'candidate.nes'),
            changed_ROM_bytes=len(touched),changed_PRG_banks=sorted({(i-16)//8192 for i in touched}),
            qualified_old_symbols_exact=len(oldq),all_CHR_exact=True,new_RAM_bytes=0,
            ordinary_target_hashes=ordinary,ordinary_flagoff_byte_exact=True,
            source_files={n:sha(source/n)for n in changes},patch_sha256=sha(out/'implementation.patch'),
            scope='Private current55 composition plus exact ordinary mapper controls. Native qualification pending.')
 (out/'build-proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2))


if __name__=='__main__':main()
