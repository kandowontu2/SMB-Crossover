"""Private owner-local signed crate vertical-window repair; no Kirby change."""
from pathlib import Path
import argparse,difflib,hashlib,json,shutil,subprocess,sys
from check_tmnt_render_oa import load
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['frozen','baseline','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();assert sha(a.baseline)=='55bcfb8209b628062ce1f833a2ed386bd6f08426d34fed9fa8b5ba1f90694be7'
 a.output.mkdir(exist_ok=False);source=a.output/'source';shutil.copytree(a.frozen,source)
 name='src/chip_dale_boxes.s';q=source/name;s=q.read_text();before={name:s}
 old=' lda Enemy_Y_Position,x\n clc\n adc #8\n sec\n sbc CdRectY\n clc\n adc #16\n cmp #32\n bcs Next\n'
 assert s.count(old)==1
 new=' .if ::ENABLE_MMC5_EXPANDED\n jsr CdContactYWindow\n bcc Next\n clc\n adc #16\n cmp #32\n .res 6,$ea\n .else\n'+old+' .endif\n'
 q.write_text(s.replace(old,new))
 helper='''; Full visible-page center minus crateY; never admit an8-bit wrap.
.pushseg
.segment "CD_LOGIC"
.proc CdContactYWindow
 lda Enemy_Y_HighPos,x
 cmp #1
 bne No
 lda Enemy_Y_Position,x
 clc
 adc #8
 bcs No
 sec
 sbc CdRectY
 bcs Positive
 cmp #$f0
 bcc No
 sec
 rts
Positive:
 cmp #16
 bcs No
 sec
 rts
No:
 clc
 rts
.endproc
.popseg
'''
 h='src/cd_contact_y_window.s';before[h]='';(source/h).write_text(helper)
 ep=source/'src/entrypoint.s';before['src/entrypoint.s']=ep.read_text()
 with ep.open('a')as f:f.write('\n.if ::ENABLE_MMC5_EXPANDED\n.include "cd_contact_y_window.s"\n.endif\n')
 patch=''.join(''.join(difflib.unified_diff(v.splitlines(True),(source/n).read_text().splitlines(True),fromfile='a/'+n if v else '/dev/null',tofile='b/'+n))for n,v in before.items())
 (a.output/'implementation.patch').write_text(patch)
 out=a.output/'candidate.nes'
 with(a.output/'host-build.log').open('w')as f:subprocess.run([sys.executable,str(ROOT/'tools/build_mmc5_expanded.py'),'--workspace',str(source),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(out)],stdout=f,stderr=subprocess.STDOUT,check=True)
 old,new=load(a.baseline),load(out)
 labs=lambda p:{q[2]:q[1]for line in p.read_text().splitlines()if len(q:=line.split())==3}
 oldlabels,newlabels=labs(a.baseline.with_suffix('.lbl')),labs(out.with_suffix('.lbl'))
 assert all(newlabels[n]==v for n,v in oldlabels.items())
 assert old['raw'][16+1048576:]==new['raw'][16+1048576:]
 ram={n:int(s['val'],0)for n,s in old['syms'].items()if s.get('seg')and int(s['val'],0)<0x8000}
 assert all(n in new['syms']and int(new['syms'][n]['val'],0)==v for n,v in ram.items())
 changed=[i for i,(x,y)in enumerate(zip(old['raw'],new['raw']))if x!=y]
 proof=dict(passed=True,private=True,adopted=False,goal_complete=False,ROM_sha256=sha(out),baseline_sha256=sha(a.baseline),patch_sha256=sha(a.output/'implementation.patch'),changed_bytes=len(changed),changed_PRG_banks=sorted({(i-16)//8192 for i in changed}),existing_labels_and_RAM_exact=True,CHR_exact=True,new_RAM_bytes=0,scope='Private actual crate vertical-window owner repair. No Kirby change; native/CPU qualification pending.')
 (a.output/'build-proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
if __name__=='__main__':main()
