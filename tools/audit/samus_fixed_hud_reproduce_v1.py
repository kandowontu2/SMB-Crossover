"""Rebuild held2082-based prototype after4a adoption, using five sparse Git leaves."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];B=R/'build';P='samus_fixed_hud'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 z=json.loads((B/(P+'_build.json')).read_text());ref=subprocess.check_output(['git','rev-parse','ccbe677^'],cwd=R,text=True).strip()
 files=['characters.s','level_variants.s','megaman_weapons.s','metasprite_engine.s','sprite_render.s'];paths={}
 for name in files:
  blob=subprocess.check_output(['git','show',ref+':src/'+name],cwd=R)
  path=B/(P+'_2082_'+name)
  if path.exists():assert path.read_bytes()==blob
  else:path.write_bytes(blob)
  paths[name]=path
 ep=B/(P+'_reproduce_entrypoint.s');data=(B/(P+'_entrypoint.s')).read_bytes()
 for name,path in paths.items():
  token=b'.include "'+name.encode()+b'"';assert data.count(token)==1;data=data.replace(token,b'.include "'+path.name.encode()+b'"')
 if ep.exists():assert ep.read_bytes()==data
 else:ep.write_bytes(data)
 cfg=B/'proto_palette_ack_smb1base-mmc5-expanded.cfg'
 assert sha(cfg)=='81d61613a76f4e3032ead6d6afcb9a96c6457044c88753430c189aa29729bca5'
 old=z['command'];cmd=[];i=0;out=B/(P+'_reproduced_v3.nes');assert not out.exists()
 while i<len(old):
  arg=old[i]
  if arg=='-m':i+=2;continue
  if arg=='--ld-args':cmd.extend([arg,'--dbgfile,'+str(out.with_suffix('.dbg'))]);i+=2;continue
  if arg=='-Ln':cmd.extend([arg,str(out.with_suffix('.lbl'))]);i+=2;continue
  if arg=='-C':cmd.extend([arg,str(cfg)]);i+=2;continue
  if arg=='-o':cmd.extend([arg,str(out)]);i+=2;continue
  if arg==str(B/(P+'_entrypoint.s')):arg=str(ep)
  cmd.append(arg);i+=1
 result=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
 log=B/(P+'_reproduce.log');log.write_text(result.stdout+result.stderr);assert result.returncode==0,result.stdout+result.stderr
 sys.path.insert(0,str(R/'tools'));from prepare_cv3_dmc_mirror import prepare;prepare(R,out)
 assert out.read_bytes()==(B/(P+'.nes')).read_bytes()
 proof=dict(passed=True,source_only=True,native_run=False,candidate_sha256=sha(out),source_git_ref=ref,source_scope='Five changed direct leaves pinned to the2082 Git parent; sparse prototype leaves and unchanged other includes reused. Not a source/runtime clone.',existing_cfg=str(cfg),command=cmd,exact_reproduction=True,prior_host_setup_error='First two links succeeded but omitted respectively genuineLBL/DBG needed by standard mirrorpostprocessor. Unmirrored linker outputs retained as samus_fixed_hud_reproduced.nes and _reproduced_v2.nes. Third compile emits both genuine files; no ROM/game test failed.',bindings={str(p):sha(p)for p in [Path(__file__),B/(P+'_build.json'),B/(P+'.nes'),out,out.with_suffix('.lbl'),out.with_suffix('.dbg'),ep,cfg,log,*paths.values()]})
 p=B/(P+'_reproduction.json');assert not p.exists();p.write_text(json.dumps(proof,indent=2)+'\n',newline='\n');print(json.dumps(dict(passed=True,ROM_sha256=sha(out),proof_sha256=sha(p))))
if __name__=='__main__':main()
