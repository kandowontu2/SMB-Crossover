"""Own-cache genuine world32 tail; resident router and all other images fixed."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
from prepare_cv3_dmc_mirror import prepare
P=R/'build/bt-jmp-row-cold-source-v1';O=R/'build/bt-native-world-source-v2';J=O/'joint'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:Path(p).write_text(json.dumps(q,indent=2)+'\n')

def main():
 assert not O.exists();O.mkdir();logs=[]
 try:
  stage=json.loads((P/'source-stage.json').read_text());assert stage['candidate']==sha(P/'joint/candidate.nes')=='7247fa87d1b03100af449bd3bb05868915205f187b3c25947565a32c6253770b'
  for f,h in stage['bindings'].items():assert sha(f)==h,f
  receipts=[R/'build/bt-jmp-row-cold-controls-v3/controls.json',R/'build/bt-jmp-row-scene-controls-v1/controls.json',R/'build/bt-jmp-cold-retirement-controls-v3/controls.json']
  for p in receipts:
   q=json.loads(p.read_text());assert q['passed'],p
   for f,h in q['bindings'].items():assert sha(f)==h,f
  shutil.copytree(P/'joint',J)
  # Rebind the actual ancestor-owned incbins, not merely the immediate parent.
  ancestor=R/'build/bt-current-cf-component-v2/joint'
  for n in['loader.s','stream.s']:
   p=J/'bt'/n;p.write_text(p.read_text().replace(str(ancestor),str(J)).replace(ancestor.as_posix(),J.as_posix()))
  assert str(J/'bt/cookie.bin').replace('\\','/') in (J/'bt/loader.s').read_text().replace('\\','/')
  assert str(J/'bt/stream.bin').replace('\\','/') in (J/'bt/stream.s').read_text().replace('\\','/')
  cfg=J/'private.cfg';cfg.write_text(cfg.read_text().replace(str(P/'joint'),str(J)).replace((P/'joint').as_posix(),J.as_posix()))
  src=J/'bt/api.s';s=src.read_text();s='.import HuNativeWorldPalette\n.export BtNativeWorldPalette\n'+s
  old=' jmp BtUnavailable    ;32 ROM world-palette bridge pending';assert s.count(old)==1;s=s.replace(old,' jmp BtNativeWorldPalette ;32 genuine native area palette query')
  at=s.index('.segment "BT_CACHE_STATE"');s=s[:at]+'; Full-cookie row32 only. Genuine native callback, no state alias.\nBtNativeWorldPalette:\n BtFar HuNativeWorldPalette,jmp\n'+s[at:];src.write_text(s)
  def run(n,cmd):
   guard=validate(cmd,O,cwd=R);z=subprocess.run(cmd,cwd=R,capture_output=True,text=True);q=dict(command=cmd,cwd=str(R),output_guard=guard,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr);logs.append(q);save(O/(n+'.json'),q);save(O/'commands.json',logs);assert z.returncode==0,(n,z.stderr)
  def assemble(n):
   src=J/'bt'/(n+'.s');run(n+'-build',[str(R/'tools/Windows/cc65/bin/ca65.exe'),'--cpu','6502x','-g','-D','MAPPER_MMC5=1','-I',str(J/'bt'),'-I',str(J),'-I',str(R),'--create-full-dep',str(src.with_suffix('.dep')),'-o',str(src.with_suffix('.o')),str(src)])
  assemble('api');cmd=json.loads((P/'final-link.json').read_text())['command'][:];rebound={}
  for i,x in enumerate(cmd):
   p=Path(x)
   if p.suffix=='.o'and p.parent.name=='bt'and p.stem in['api','loader','stream']:rebound[p.stem]=str(p);cmd[i]=str(J/'bt'/p.name)
  assert set(rebound)=={'api','loader','stream'}
  for flag in['-C','-Ln','-o','-m']:cmd[cmd.index(flag)+1]=str(J/Path(cmd[cmd.index(flag)+1]).name)
  cmd[cmd.index('--ld-args')+1]='--dbgfile,'+str(J/'candidate.dbg');run('initial-link',cmd)
  cache=(J/'sideoutputs/candidate/00-cache.bin').read_bytes();assert len(cache)==8192 and cache[0x1fe0:0x1ff0]==bytes(16)
  cookie=bytes([167,33,1,117])+hashlib.sha256(cache).digest()[:12]
  (J/'bt/cache.bin').write_bytes(cache);(J/'bt/stream.bin').write_bytes(cache);(J/'bt/cookie.bin').write_bytes(cookie)
  assemble('loader');assemble('stream');run('final-link',cmd);prepare(R,J/'candidate.nes')
  old,b=map(qualified,[P/'joint/candidate.nes',J/'candidate.nes'])
  for n in['BtServiceVeneers','BtServiceUnavailable','BtRouter','BtCheck','BtLoad','BtRetire','BtAcquire','BtColdPortrait','BtColdColors','BtCacheServices','BtHostState','BtFresh','BtScene','BtEnsure','BwBtResolve','BwScene','CfLoadIfCold','CfOrBtCheck','CfRetire','BmFresh','BmColors','FmPending','FmStartFlags']:
   assert(address(old,n),location(old,n))==(address(b,n),location(b,n)),n
  at=location(b,'BtServiceVeneers');assert old['raw'][at:at+224]==b['raw'][at:at+224]
  changed=[i for i,(x,y)in enumerate(zip(old['raw'],b['raw']))if x!=y];allowed=[(16+93*8192+0xdc0,487),(16+128*8192+919*1024,8192)]
  assert changed and all(any(lo<=i<lo+size for lo,size in allowed)for i in changed)
  for n in['cf-stream.bin','cf-cookie.bin','bowser.bin','ram3.bin','ff-cookie.bin','code.bin','data.bin']:assert sha(J/n)==sha(P/'joint'/n),n
  assert old['raw'][:16]==b['raw'][:16]
  host=next(s for s in b['segs'].values()if s['name']=='"BT_CACHE_HOST"');helper=address(b,'BtNativeWorldPalette')
  assert int(host['start'],0)<=helper<helper+18<=int(host['start'],0)+int(host['size'],0)
  files=[R/'tools/audit/prepare_bt_native_world_source_v1.py',R/'build/bt-native-world-source-v1/negative.json',Path(__file__),P/'source-stage.json',*receipts,*[J/'bt'/n for n in['api.s','api.o','api.dep','loader.s','loader.o','loader.dep','stream.s','stream.o','stream.dep','cache.bin','stream.bin','cookie.bin']],J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',J/'private.cfg',O/'final-link.json',O/'commands.json']
  q=dict(source=True,status='PENDING_BT_NATIVE_WORLD32_OWN_SOURCE',candidate=sha(J/'candidate.nes'),parent=stage['candidate'],joint=str(J),ready=66,CF_pending=True,BT_pending=True,native=False,installed=False,changed_bytes=len(changed),owned_helper_bytes=18,owned_helper_address=helper,BT_cookie=cookie.hex(),BT_cache=sha(J/'bt/cache.bin'),actual_rebuilt_objects=rebound,resident_router_all_publicPCs_other_images_exact=True,no_new_resident_state_common_span=True,remaining=['Actual QueueMegaManFacePalette flags/ordered VRAM query controls across area/background contexts','Real full cold-parser order and unready/corrupt direct32 rejection','BT pending readiness/native/M3current68 composition remain separate'],bindings={str(p.resolve()):sha(p)for p in files})
  save(O/'source-stage.json',q);save(J/'source-stage.json',q);print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))
 except Exception as e:save(O/'negative.json',dict(passed=False,error=repr(e),traceback=traceback.format_exc()));raise
if __name__=='__main__':main()
