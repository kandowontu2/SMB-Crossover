"""Source-compose exact BT7 onto genuine terminal CF-menu/P2 main producer."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from prepare_cv3_dmc_mirror import prepare
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
P=R/'build/bt-p2-cf-menu-source-1031-v2';B=R/'build/bt-lives-body-source-v7';V=R/'build/bt-lives-body-source-v5'
O=R/'build/bt-cf-coherent-source-1031-v1';J=O/'joint'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8',newline='\n')
def save(p,q):write(p,json.dumps(q,indent=2)+'\n')
def bound(p):
 d=json.loads(p.read_text())
 for n,h in d['bindings'].items():assert sha(n)==h,n
 return d
def rt(s):
 for p in [P/'joint',B/'joint']:s=s.replace(str(p),str(J)).replace(p.as_posix(),J.as_posix())
 return s
def run(n,cmd):
 guard=validate(cmd,J,cwd=R)
 for x in guard['outputs']:Path(x['path']).parent.mkdir(parents=True,exist_ok=True)
 z=subprocess.run(cmd,cwd=R,capture_output=True,text=True);save(O/(n+'.json'),dict(command=cmd,output_guard=guard,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr));assert z.returncode==0,(n,z.stderr)
def main():
 assert not O.exists();O.mkdir()
 try:
  pstage=bound(P/'source-stage.json');bstage=bound(B/'source-stage.json')
  assert pstage['candidate']==sha(P/'joint/candidate.nes')=='f428406a89b5d5d8fcf07db6bafe9955e0ba4059dfbd4267480484ce57f5d779'
  assert bstage['candidate']==sha(B/'joint/candidate.nes')=='b356ae88e13ff319dc863ddc59df02edca879aeafc923e0d815c641830b3de91'
  shutil.copytree(P/'joint',J);shutil.copytree(B/'joint/bt',J/'bt',dirs_exist_ok=True)
  for p in J.rglob('*'):
   if p.suffix.lower()in['.s','.inc','.cfg']:
    s=p.read_text(encoding='utf-8');t=rt(s)
    if t!=s:write(p,t)
  cmds={}
  for n in ['api','loader','stream']:
   cmds[n]=[rt(x)for x in json.loads((B/(n+'-build.json')).read_text())['command']];run(n+'-build',cmds[n])
  cmd=json.loads((P/'candidate-link.json').read_text())['command']
  cmd=[x if Path(x).suffix.lower()=='.o'else rt(x)for x in cmd]
  for i,x in enumerate(cmd):
   if Path(x).suffix.lower()=='.o'and Path(x).parent.name=='bt'and Path(x).stem in cmds:cmd[i]=str(J/'bt'/Path(x).name)
  cmd[cmd.index('-C')+1]=str(J/'candidate.cfg')
  run('initial-link',cmd)
  outputs=validate(cmd,J,cwd=R)['outputs'];paths=[Path(x['path'])for x in outputs if x['kind']=='MEMORY file'and x['path'].endswith('cache.bin')];assert len(paths)==1
  cache=paths[0].read_bytes();assert cache==(B/'joint/bt/cache.bin').read_bytes()
  cookie=bytes([167,33,1,117])+hashlib.sha256(cache).digest()[:12];assert cookie==(B/'joint/bt/cookie.bin').read_bytes()
  for n in ['cache.bin','stream.bin']:(J/'bt'/n).write_bytes(cache)
  (J/'bt/cookie.bin').write_bytes(cookie)
  for n in ['loader','stream']:run(n+'-final-build',cmds[n])
  run('final-link',cmd);prepare(R,J/'candidate.nes')
  raw=(J/'candidate.nes').read_bytes();parent=(P/'joint/candidate.nes').read_bytes();old=(V/'joint/candidate.nes').read_bytes();new=(B/'joint/candidate.nes').read_bytes()
  # Verification oracle only: the actual product above came from source link.
  expected=bytearray(parent);deltas=[]
  for i,(a,b)in enumerate(zip(old,new)):
   if a!=b:assert expected[i]==a,('overlap with current main/CF child',i);expected[i]=b;deltas.append(i)
  assert raw==expected,'Source output differs from the exact disjoint source delta oracle'
  prior,now=[scoped_load(p)for p in[P/'joint/candidate.nes',J/'candidate.nes']]
  for n in ['GameLoop','BtServiceVeneers','BtRouter','FmToggle','FmStartFlags','BtStatusPlayerCount','WriteGameText::CheckPlayerName','CfP1NativeRestore']:
   assert(address(prior,n),location(prior,n))==(address(now,n),location(now,n)),n
  assert raw[:16]==parent[:16]and raw[749223:749290]==parent[749223:749290]
  paths=[Path(__file__),P/'source-stage.json',P/'candidate-link.json',P/'main-build.json',B/'source-stage.json',V/'source-stage.json',
   J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',J/'candidate.cfg',*[J/'bt'/n for n in['api.s','api.o','api.dep','loader.s','loader.o','loader.dep','stream.s','stream.o','stream.dep','cache.bin','cookie.bin']],*O.glob('*-build.json'),O/'initial-link.json',O/'final-link.json']
  save(O/'source-stage.json',dict(source=True,native=False,installed=False,candidate=sha(J/'candidate.nes'),parent=pstage['candidate'],BT_component=bstage['candidate'],
   actual_source_delta_oracle_equal=True,main_object_genuine_parent_not_copied_from_old_BT=True,current_main_CF67_and_all_nonBT_ROM_exact=True,
   all_BTv7_cache_cookie_bytes_exact=True,BT_cookie=cookie.hex(),changed_ROM_bytes=len(deltas),ready_if_native_qualified=74,CF_menu_parent_preserved=True,
   bindings={str(p.resolve()):sha(p)for p in paths}))
  print(json.dumps(dict(source=True,native=False,candidate=sha(J/'candidate.nes'),changed=len(deltas),cookie=cookie.hex())),flush=True)
 except Exception as e:save(O/'negative.json',dict(passed=False,error=repr(e),traceback=traceback.format_exc()));raise
if __name__=='__main__':main()
