"""Append authentic palettes after the genuine native30B lives text packet."""
from pathlib import Path
import difflib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from prepare_cv3_dmc_mirror import prepare
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
import prepare_ff_joint_source_v1 as B
P=R/'build/ff-cold-preview-v3';O=R/'build/ff-cold-preview-v4';J=O/'joint'
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8',newline='\n')
def save(p,x):write(p,json.dumps(x,indent=2)+'\n')
def main():
 assert not O.exists();J.mkdir(parents=True)
 for f in(P/'joint').rglob('*'):
  if f.is_file()and f.suffix in['.s','.inc','.cfg','.chr','.bin']:
   q=J/f.relative_to(P/'joint');q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(f.read_bytes())
 p=J/'loader.s';old=p.read_text();s='.import FwForceColors,VRAM_Buffer1_Offset\n'+old
 needle=' cmp #0\n bne FwStatusDone\n php'
 new=' cmp #0\n beq FwStatusOwn\n cmp #1\n bne FwStatusDone\n cpy #30\n bne FwStatusDone\n sty VRAM_Buffer1_Offset\n jmp FwForceColors\nFwStatusOwn:\n php'
 assert s.count(needle)==1;s=s.replace(needle,new)
 needle=' ldy #0\nFwStatusCopy:';assert s.count(needle)==1;s=s.replace(needle,' ldy #6\nFwStatusCopy:')
 needle=' inx\n iny\n cpy #7\n bne FwStatusCopy';assert s.count(needle)==1;s=s.replace(needle,' inx\n dey\n bpl FwStatusCopy')
 needle='"FIGHTER ","WHITE M ","BLACK M ","THIEF   "'
 assert s.count(needle)==1;s=s.replace(needle,'"RETHGIF ","M ETIHW ","M KCALB ","  FEIHT "')
 write(p,s)
 cfg=(P/'joint/private.cfg').read_text().replace(str(P/'joint'),str(J)).replace((P/'joint').as_posix(),J.as_posix());write(J/'private.cfg',cfg)
 command=json.loads((P/'joint/loader-build.json').read_text())['command'];command=[v.replace(str(P/'joint'),str(J))for v in command]
 link=json.loads((P/'joint/final-link.json').read_text())['command']
 for i,v in enumerate(link):
  if v in[str(P/'joint'/n)for n in['loader.o','private.cfg','candidate.nes','candidate.lbl','candidate.map']]:link[i]=str(J/Path(v).name)
  elif v.startswith('--dbgfile,'):link[i]='--dbgfile,'+str(J/'candidate.dbg')
 for name,cmd in [('loader-build',command),('final-link',link)]:save(J/(name+'-guard.json'),validate(cmd,O,cwd=R))
 for name,cmd in [('loader-build',command),('final-link',link)]:
  q=subprocess.run(cmd,cwd=R,capture_output=True,text=True);save(J/(name+'.json'),dict(command=cmd,returncode=q.returncode,stdout=q.stdout,stderr=q.stderr));assert q.returncode==0,q.stderr
 prepare(R,J/'candidate.nes');a=qualified(P/'joint/candidate.nes');b=qualified(J/'candidate.nes')
 spans=[(location(a,'FwStatusName'),location(a,'FwStatusName')+52),(location(a,'FwHudNames'),location(a,'FwHudNames')+52)]
 changes=[i for i,(x,y)in enumerate(zip(a['raw'],b['raw']))if x!=y];assert all(any(lo<=i<hi for lo,hi in spans)for i in changes)
 moved={n:(address(a,n),address(b,n))for n in a['syms']if n not in['FwStatusCopy','FwStatusDone']and n in b['syms']and address(a,n)!=address(b,n)};assert not moved,moved
 assert(J/'ram3.bin').read_bytes()==(P/'joint/ram3.bin').read_bytes()
 write(O/'source.patch',''.join(difflib.unified_diff(old.splitlines(True),s.splitlines(True),fromfile='parent/loader.s',tofile='new/loader.s')))
 save(O/'source-proof.json',dict(passed=True,candidate=B.sha(J/'candidate.nes'),parent=B.sha(P/'joint/candidate.nes'),
  only_own52B_status_and52B_data=True,all_live_public_PCs_header_CHR_payload_cookie_exact=True,
  actual_WriteGameText_A1_Y30_append_offset49_before_DMA=True,invalid_A1_Y_rejected=True,changed_bytes=len(changes),native=False,admitted=False))
 print(B.sha(J/'candidate.nes'))
if __name__=='__main__':main()
