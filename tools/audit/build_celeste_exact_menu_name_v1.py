"""Two label-only source successors, released52 and frozenArthur53 separate."""
from pathlib import Path
import difflib,hashlib,json,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools'))
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from prepare_cv3_dmc_mirror import prepare
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
CASES=[('celeste-menu-name-current-v1','expanded-playable-roster-1030-v1',52,'main-build.json','link-build.json'),('celeste-menu-name-arthur-v1','arthur-expanded-ready-v2',53,'main-build-v3.json','final-link-v3.json')]
def build(name,parent,ready,main,link):
 P=R/'build'/parent/'joint';O=R/'build'/name;N=O/'joint';assert not O.exists()
 if ready==52:bound=json.loads((P/'source-closure.json').read_text())['bindings']
 else:bound=json.loads((P.parent/'handoff.json').read_text())['bindings']
 for p,v in bound.items():assert sha(p)==v,p
 assert sha(P/'candidate.nes')==('18de015564c61cd07d0d52ec26300661627278880d4226f7c589ac95028a0976'if ready==52 else'd8f18f65d50458fe01f7c2488d7dcefcb8a2a1b1d877655d1a8e94de729e753f')
 assert N.resolve().is_relative_to((R/'build'/name).resolve());O.mkdir();shutil.copytree(P,N)
 def rewrite(s):return s.replace(str(P),str(N)).replace(P.as_posix(),N.as_posix())
 for p in N.rglob('*'):
  if p.is_file()and p.suffix in ['.s','.inc','.cfg']:
   s=p.read_text();z=rewrite(s)
   if s!=z:p.write_text(z,newline='\n')
 p=N/'src/kamikaze_mario.s';s=p.read_text();old=' cmp #3\n bne Foreign\n pla\n plp';assert s.count(old)==1
 s=s.replace(old,old.replace('bne Foreign','bne KmMarioName'),1)
 old='Name:.byte " KAMIKAZE MARIO "\n.endproc';assert s.count(old)==1
 s=s.replace(old,'''Name:.byte " KAMIKAZE MARIO "
KmMarioName:
 ; Cold exactvariant4 name only, reusing authentic original Names44.
 cmp #4
 bne Foreign
 pla
 plp
 lda #44
 farcall NrQueueSelectName::NameIndex,jmp
.endproc''',1);p.write_text(s,newline='\n')
 def run(cmd,phase):
  for flag in ['-o','-Ln','-m','--create-full-dep']:
   if flag in cmd:assert Path(cmd[cmd.index(flag)+1]).resolve().is_relative_to(N.resolve()),cmd
  for x in cmd:
   if x.startswith('--dbgfile,'):assert Path(x.split(',',1)[1]).resolve().is_relative_to(N.resolve())
  t=subprocess.run(cmd,cwd=R,capture_output=True,text=True);(N/(phase+'.json')).write_text(json.dumps(dict(command=cmd,returncode=t.returncode,stdout=t.stdout,stderr=t.stderr),indent=2)+'\n');assert not t.returncode,t.stderr
 run([rewrite(x)for x in json.loads((P/main).read_text())['command']],'label-main-build')
 run([rewrite(x)for x in json.loads((P/link).read_text())['command']],'label-link');prepare(R,N/'candidate.nes')
 old,b=[scoped_load(t/'candidate.nes')for t in [P,N]];diff=[i for i,(a,z)in enumerate(zip(old['raw'],b['raw']))if a!=z]
 assert len(diff)==27 and all((x-16)//8192==81 for x in diff),diff
 assert b['raw'][:16]==old['raw'][:16]and b['raw'][1048592:]==old['raw'][1048592:]
 assert address(old,'KmMenuEnd')==0xbfad and address(b,'KmMenuEnd')==0xbfc7
 stable=[]
 for name,sym in old['syms'].items():
  if sym.get('type')=='lab'and 'seg'in sym and 'val'in sym and name in b['syms']and name!='KmMenuEnd':
   assert address(old,name)==address(b,name),(name,address(old,name),address(b,name));stable.append(name)
 patch=''.join(difflib.unified_diff((P/'src/kamikaze_mario.s').read_text().splitlines(True),p.read_text().splitlines(True),fromfile='parent/src/kamikaze_mario.s',tofile='private/src/kamikaze_mario.s'))
 (O/'source.patch').write_text(patch,newline='\n')
 for q,v in bound.items():assert sha(q)==v,q
 d=dict(passed=True,native=False,ready=ready,ROM_sha256=sha(N/'candidate.nes'),parent=sha(P/'candidate.nes'),changed_bytes=len(diff),physical_PRG_bank=81,header_CHR_exact=True,all_existing_label_PCs_except_nonentry_end_exact=len(stable),own_existing_KmMenu_tail=[0xbfad,0xbfc7],shared_common_unchanged=True,byte_changes=[dict(offset=i,old=old['raw'][i],new=b['raw'][i])for i in diff],bindings={str(q.resolve()):sha(q)for q in list(N.rglob('*'))+[Path(__file__),P/'candidate.nes',P/'candidate.dbg']if q.is_file()})
 (O/'source-proof.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({k:v for k,v in d.items()if k not in ['bindings','byte_changes']}),flush=True)
def main():
 for args in CASES:build(*args)
if __name__=='__main__':main()
