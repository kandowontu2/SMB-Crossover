"""Route actual FF front-end service2 to its prepared native body renderer."""
from pathlib import Path
import difflib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from prepare_cv3_dmc_mirror import prepare
import prepare_ff_joint_source_v1 as B
P=R/'build/ff-current-names-v3';O=R/'build/ff-cold-preview-v1';J=O/'joint'
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8',newline='\n')
def save(p,x):write(p,json.dumps(x,indent=2)+'\n')
def main():
 assert not O.exists();J.mkdir(parents=True)
 B.validate(P/'handoff-source-v1.json','75f7baac5f70763aea759780620c48185db938775c36408b2c9efc9175826887')
 b=scoped_load(P/'joint/candidate.nes');retired=['FwAdder','FwHead'];link=json.loads((P/'joint/final-link.json').read_text())['command'];inputs={}
 for v in link:
  if v.endswith('.o'):
   txt=subprocess.check_output([str(R/'tools/Windows/cc65/bin/od65.exe'),'--dump-imports',v],text=True)
   assert not any('"'+n+'"'in txt for n in retired),v;inputs[v]=B.sha(v)
 for f in(P/'joint').rglob('*'):
  if f.is_file()and f.suffix in['.s','.inc','.cfg','.chr','.bin']:
   q=J/f.relative_to(P/'joint');q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(f.read_bytes())
 p=J/'loader.s';old=p.read_text();s=old
 needle='FW_GATE FwAdder,FfAdder\nFW_GATE FwHead,FfHead'
 code='''.import OperMode_Task,FwHostDrawShots,FwPreviewPublish,DrawMetasprite
.export FwDrawDispatch
; OWN obsolete FwAdder/FwHead explicitly retired. Real typed callbacks use
; host adapters. Upstream GmMenuDrawGate is service2 for both title AND lives.
FwDrawDispatch:
 php
 pha
 lda OperMode
 cmp #1
 bne FwDrawFrontEnd
 lda OperMode_Task
 cmp #3
 bne FwDrawFrontEnd
 pla
 plp
 jmp FwHostDrawShots
FwDrawFrontEnd:
 txa
 pha
 tya
 pha
 jsr FwPreviewPublish
 pla
 tay
 pla
 tax
 pla
 plp
 sta SafecallA_SMC+1
 lda #<DrawMetasprite
 sta FarcallJmpTarget_SMC+1
 lda #>DrawMetasprite
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(DrawMetasprite)|$80)
 jmp FarCallCommon
 .assert *-FwDrawDispatch<=52,error,"OWN retired FF two-gate span"
 .res 52-(*-FwDrawDispatch),$ea'''
 assert s.count(needle)==1;s=s.replace(needle,code);write(p,s)
 patch=list(difflib.unified_diff(old.splitlines(True),s.splitlines(True),fromfile='parent/loader.s',tofile='new/loader.s'))
 p=J/'veneers.s';old=p.read_text();s=old.replace('.import FwHostDrawShots','.import FwDrawDispatch')
 assert s.count(' jmp FwHostDrawShots')==1;s=s.replace(' jmp FwHostDrawShots',' jmp FwDrawDispatch');write(p,s)
 patch+=list(difflib.unified_diff(old.splitlines(True),s.splitlines(True),fromfile='parent/veneers.s',tofile='new/veneers.s'))
 cfg=(P/'joint/private.cfg').read_text().replace(str(P/'joint'),str(J)).replace((P/'joint').as_posix(),J.as_posix());write(J/'private.cfg',cfg)
 recipes=[]
 for n in['loader','veneers']:
  cmd=json.loads((P/'joint'/(n+'-build.json')).read_text())['command'];cmd=[v.replace(str(P/'joint'),str(J))for v in cmd];recipes.append((n+'-build',cmd))
 for i,v in enumerate(link):
  if v in[str(P/'joint'/n)for n in['loader.o','veneers.o','private.cfg','candidate.nes','candidate.lbl','candidate.map']]:link[i]=str(J/Path(v).name)
  elif v.startswith('--dbgfile,'):link[i]='--dbgfile,'+str(J/'candidate.dbg')
 for name,cmd in recipes+[('final-link',link)]:save(J/(name+'-guard.json'),validate(cmd,O,cwd=R))
 for name,cmd in recipes+[('final-link',link)]:
  p=subprocess.run(cmd,cwd=R,capture_output=True,text=True);save(J/(name+'.json'),dict(command=cmd,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr));assert p.returncode==0,p.stderr
 prepare(R,J/'candidate.nes');new=scoped_load(J/'candidate.nes')
 assert address(new,'FwDrawDispatch')==address(b,'FwAdder') and address(new,'FwSide')==address(b,'FwSide')
 for n in retired:assert n not in new['syms']
 shifts={n:(address(b,n),address(new,n))for n in b['syms']if n not in retired and n in new['syms']and address(b,n)!=address(new,n)};assert not shifts,shifts
 a=(P/'joint/candidate.nes').read_bytes();v=(J/'candidate.nes').read_bytes();ranges=[(location(b,'FwAdder'),location(b,'FwAdder')+52),(location(b,'FwServiceVeneers')+6,location(b,'FwServiceVeneers')+9)]
 diff=[i for i,(x,y)in enumerate(zip(a,v))if x!=y];assert all(any(lo<=i<hi for lo,hi in ranges)for i in diff)
 assert(J/'ram3.bin').read_bytes()==(P/'joint/ram3.bin').read_bytes()
 write(O/'source.patch',''.join(patch));save(O/'source-proof.json',dict(passed=True,candidate=B.sha(J/'candidate.nes'),parent=B.sha(P/'joint/candidate.nes'),
  retired_own_ABI=retired,zero_final_object_imports=inputs,all_live_public_PCs_header_CHR_payload_cookie_exact=True,
  own_dispatcher_size=int(new['syms']['FwDrawDispatch']['size'],0) if 'size' in new['syms']['FwDrawDispatch'] else 52,
  only52B_owned_alias_and_service2_operands=True,changed_bytes=len(diff),native=False,admitted=False))
 print(B.sha(J/'candidate.nes'))
if __name__=='__main__':main()
