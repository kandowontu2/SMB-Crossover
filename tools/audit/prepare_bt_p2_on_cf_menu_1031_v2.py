"""Root-approved21B BT P2 status helper atop frozen CF menu source."""
from pathlib import Path
import hashlib,json,re,subprocess,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from prepare_cv3_dmc_mirror import prepare
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
P=R/'build/contra-force-menu-admission-1031-v2';O=R/'build/bt-p2-cf-menu-source-1031-v2';J=O/'joint'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')
def once(s,a,b):assert s.count(a)==1,(a,s.count(a));return s.replace(a,b,1)
def main():
 assert not O.exists();(J/'src').mkdir(parents=True)
 try:
  h=R/'docs/qa/checkpoints/2026-10-31/contra-force-menu-admission-v2/handoff.json';d=json.loads(h.read_text());assert sha(h)=='72811173c2ae5d571f15d50fa9e8d36f04be23da71ca2ca91a22220aade6ec56'
  for n,v in d['bindings'].items():assert sha(n)==v,n
  raw=(P/'joint/main.dep').read_text().split(':\t',1)[1].splitlines()[0];deps=[Path(v.replace('\\ ',' ')).resolve()for v in re.split(r'(?<!\\)[ \t]+',raw.strip())if v]
  src={n:next(p for p in deps if p.name==n)for n in['characters.s','screen_render.s']};assert len(src)==2
  a=src['characters.s'].read_text();replacement='''  ::BtStatusPlayerCount:
  php
  cpx #$ff
  bne BtNativePlayerCount
  lda SelectedCharacter
  cmp #33
  bne BtNativePlayerCount
  plp
  lda #0
  rts
BtNativePlayerCount:
  plp
  lda NumberOfPlayers
  rts
  .res 48-(*-::BtStatusPlayerCount),$ea'''
  a=once(a,'  .res 48,$ea',replacement)
  b=once(src['screen_render.s'].read_text(),'CheckPlayerName:\n  lda NumberOfPlayers','CheckPlayerName:\n  jsr BtStatusPlayerCount')
  (J/'src/characters.s').write_text(a);(J/'src/screen_render.s').write_text(b)
  (J/'entrypoint.s').write_bytes((P/'joint/entrypoint.s').read_bytes())
  old=qualified(P/'joint/candidate.nes');logs=[];pins={str(p):sha(p)for p in[*src.values(),h,P/'source-stage.json',P/'main-build.json',P/'candidate-link.json',P/'joint/candidate.nes',P/'joint/candidate.dbg']}
  def run(n,cmd):
   guard=validate(cmd,O,cwd=R);z=subprocess.run(cmd,cwd=R,capture_output=True,text=True);p=O/(n+'.json');save(p,dict(command=cmd,output_guard=guard,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr));logs.append(p);assert z.returncode==0,(n,z.stderr)
  cmd=json.loads((P/'main-build.json').read_text())['command'];oldmain=Path(cmd[cmd.index('-o')+1]).resolve();cmd[cmd.index('-o')+1]=str(J/'main.o');cmd[cmd.index('--create-full-dep')+1]=str(J/'main.dep');cmd=[str(J/'entrypoint.s')if Path(v).suffix=='.s'else v for v in cmd];cmd[1:1]=['-I',str(J),'-I',str(J/'src')];run('main-build',cmd)
  cmd=json.loads((P/'candidate-link.json').read_text())['command'];cfg=Path(cmd[cmd.index('-C')+1]);text=cfg.read_text();number=0
  def redir(m):
   nonlocal number
   if m[1]in['','%O']:return m[0]
   p=J/'sideoutputs'/('%03d-'%number+Path(m[1]).name);number+=1;p.parent.mkdir(parents=True,exist_ok=True);return 'file="'+p.as_posix()+'"'
  (J/'candidate.cfg').write_text(re.sub(r'file\s*=\s*"([^"]*)"',redir,text));cmd=[str(J/'main.o')if Path(v).suffix=='.o'and Path(v).resolve()==oldmain else v for v in cmd]
  for flag,value in[('-C',J/'candidate.cfg'),('-o',J/'candidate.nes'),('-Ln',J/'candidate.lbl'),('-m',J/'candidate.map')]:cmd[cmd.index(flag)+1]=str(value)
  cmd[cmd.index('--ld-args')+1]='--dbgfile,'+str(J/'candidate.dbg');run('candidate-link',cmd);prepare(R,J/'candidate.nes');new=qualified(J/'candidate.nes')
  start=location(new,'CrossoverPatchStatusName');consumer=location(new,'WriteGameText::CheckPlayerName');spans=[(start,66),(consumer,3)];diff=[i for i,(a,b)in enumerate(zip(old['raw'],new['raw']))if a!=b]
  assert all(any(lo<=i<lo+n for lo,n in spans)for i in diff)
  assert address(new,'BtStatusPlayerCount')==address(new,'CrossoverPatchStatusName')+18
  assert new['raw'][consumer]==0x20 and new['raw'][consumer+1]+256*new['raw'][consumer+2]==address(new,'BtStatusPlayerCount')
  count=0
  for n,s in old['syms'].items():assert n in new['syms']and int(s['val'],0)==address(new,n),n;count+=1
  for n,v in pins.items():assert sha(n)==v,n
  paths=[Path(__file__),*logs,J/'entrypoint.s',J/'src/characters.s',J/'src/screen_render.s',J/'main.dep',J/'main.o',J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',J/'candidate.cfg']
  q=dict(source=True,native=False,installed=False,admitted=False,candidate=sha(J/'candidate.nes'),parent=sha(P/'joint/candidate.nes'),changed_ROM_bytes=len(diff),allowed_envelopes=spans,actual21B_helper_inside_owned48B_padding=True,all_old_resolved_symbols_exact=count,all_CF_BT_payloads_cookies_CHR_menu_and59_67_exact=True,source_controls_pending=True,bindings={**pins,**{str(p):sha(p)for p in paths}});save(O/'source-stage.json',q);print(json.dumps(dict(path=str(O/'source-stage.json'),sha256=sha(O/'source-stage.json'),candidate=q['candidate'],changed=len(diff))),flush=True)
 except Exception as e:save(O/'negative.json',dict(passed=False,error=repr(e),traceback=traceback.format_exc()));raise
if __name__=='__main__':main()
