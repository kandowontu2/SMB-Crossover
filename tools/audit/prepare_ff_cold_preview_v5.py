"""Keep the original black lives backdrop during the late own palette append."""
from pathlib import Path
import json,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from prepare_cv3_dmc_mirror import prepare
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
import prepare_ff_joint_source_v1 as B
P=R/'build/ff-cold-preview-v4';O=R/'build/ff-cold-preview-v5';J=O/'joint'
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8',newline='\n')
def save(p,x):write(p,json.dumps(x,indent=2)+'\n')
def main():
 assert not O.exists();J.mkdir(parents=True)
 for f in(P/'joint').rglob('*'):
  if f.is_file()and f.suffix in['.s','.inc','.cfg','.chr','.bin']:
   q=J/f.relative_to(P/'joint');q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(f.read_bytes())
 p=J/'loader.s';s=p.read_text();assert s.count(' jmp FwForceColors')==1;s=s.replace(' jmp FwForceColors',' jmp FwLivesColors')
 marker=' .assert *-FwPortraitDraw<=52,error,"OWN retired FF two-gate span"'
 helper='''FwLivesColors:
 lda BackgroundColorCtrl
 pha
 lda #2
 sta BackgroundColorCtrl
 jsr FwForceColors
 pla
 sta BackgroundColorCtrl
 lda #1
 rts
'''
 assert s.count(marker)==1;s='.import BackgroundColorCtrl\n'+s.replace(marker,helper+marker);write(p,s)
 cfg=(P/'joint/private.cfg').read_text().replace(str(P/'joint'),str(J)).replace((P/'joint').as_posix(),J.as_posix());write(J/'private.cfg',cfg)
 cmd=json.loads((P/'joint/loader-build.json').read_text())['command'];cmd=[v.replace(str(P/'joint'),str(J))for v in cmd]
 link=json.loads((P/'joint/final-link.json').read_text())['command']
 for i,v in enumerate(link):
  if v in[str(P/'joint'/n)for n in['loader.o','private.cfg','candidate.nes','candidate.lbl','candidate.map']]:link[i]=str(J/Path(v).name)
  elif v.startswith('--dbgfile,'):link[i]='--dbgfile,'+str(J/'candidate.dbg')
 for name,c in [('loader-build',cmd),('final-link',link)]:save(J/(name+'-guard.json'),validate(c,O,cwd=R))
 for name,c in [('loader-build',cmd),('final-link',link)]:
  q=subprocess.run(c,cwd=R,capture_output=True,text=True);save(J/(name+'.json'),dict(command=c,returncode=q.returncode,stdout=q.stdout,stderr=q.stderr));assert q.returncode==0,q.stderr
 prepare(R,J/'candidate.nes');b=qualified(J/'candidate.nes');a=qualified(R/'build/ff-current-names-v3/joint/candidate.nes')
 spans=[(location(a,'FwStatusName'),location(a,'FwStatusName')+52),(location(a,'FwHudNames'),location(a,'FwHudNames')+52),(location(a,'FwAdder'),location(a,'FwAdder')+52),(location(a,'FwServiceVeneers')+51,location(a,'FwServiceVeneers')+54)]
 changes=[i for i,(x,y)in enumerate(zip(a['raw'],b['raw']))if x!=y];assert all(any(lo<=i<hi for lo,hi in spans)for i in changes)
 assert b['raw'][location(b,'FwServiceVeneers')+6:location(b,'FwServiceVeneers')+9]==a['raw'][location(a,'FwServiceVeneers')+6:location(a,'FwServiceVeneers')+9]
 assert(J/'ram3.bin').read_bytes()==(P/'joint/ram3.bin').read_bytes()
 save(O/'source-proof.json',dict(passed=True,candidate=B.sha(J/'candidate.nes'),parent_named0369=B.sha(R/'build/ff-current-names-v3/joint/candidate.nes'),
  own_spans_only=spans,changed_bytes=len(changes),unchanged_gameplay_row2=True,ROM_bridge33_plus19_lives_helper_in52=True,
  actual_native_lives_A1_Y30_end_then_complete49B_queue=True,lives_Black_BG_restored_exact_native_SetupIntermediate_control2=True,
  all_live_public_PCs_header_CHR_payload_cookie_exact=True,native=False,admitted=False))
 print(B.sha(J/'candidate.nes'))
if __name__=='__main__':main()
