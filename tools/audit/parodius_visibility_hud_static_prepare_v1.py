"""Clone a frozen df515 controller, changing only observer callback registration."""
from pathlib import Path
import argparse,hashlib,json,shutil,sys
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--parent',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--parser-root',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 z=json.loads((a.parent/'preparation.json').read_text());old=Path(z['script']).parent;assert z['ROM_sha256']=='df5154bc035ba2c392bb8d34068897a2bccf7a78a6f4554bd6790d31a586c357';assert sha(old/'run.lua')==z['script_sha256'];assert all(sha(Path(n))==v for n,v in z['dependencies'].items())
 out=a.output/'baseline-early';out.mkdir();controller=a.output/'controller';controller.mkdir();oldcontroller=a.parent/'controller'
 for f in oldcontroller.iterdir():
  if f.is_file():shutil.copy2(f,controller/f.name)
 policy=controller/'policy.lua';text=policy.read_text(encoding='utf-8');text=text.replace(oldcontroller.as_posix(),controller.as_posix());policy.write_text(text,encoding='utf-8')
 for ext in ['.nes','.dbg','.lbl','.map']:shutil.copy2(old/('candidate'+ext),out/('candidate'+ext))
 module=ROOT/'tools/audit/parodius_visibility_hud_static_observer_v1.lua';original=ROOT/'tools/audit/parodius_visibility_observer.lua'
 text=(old/'run.lua').read_text(encoding='utf-8');body=original.read_text(encoding='utf-8');assert text.count(body)==1;text=text.replace(body,module.read_text(encoding='utf-8')).replace(old.as_posix(),out.as_posix()).replace(oldcontroller.as_posix(),controller.as_posix());assert text.rstrip().endswith('dofile("'+(controller/'harness.lua').as_posix()+'")')or text.rstrip().endswith("dofile('"+(controller/'harness.lua').as_posix()+"')")
 text+='\n-- FINAL startup registration: all HUD/scroll/controller static hooks precede returns.\nPARODIUS_STATIC_INSTALL_RETURNS()\n';(out/'run.lua').write_text(text,encoding='utf-8')
 config=json.loads((old/'config.json').read_text());config['output']=out.as_posix()+'/';(out/'config.json').write_text(json.dumps(config,indent=2)+'\n',encoding='utf-8')
 sys.path.insert(0,str(a.parser_root));from luaparser import ast;ast.parse(text)
 deps=dict(z['dependencies']);deps.update({str(f.resolve()):sha(f)for f in [Path(__file__),module,ROOT/'tools/audit/parodius_visibility_hud_static_build_v1.py',ROOT/'tools/audit/parodius_visibility_hud_static_cpu_v1.py']})
 snapshots=a.output/'dependency-snapshots';snapshots.mkdir();bindings={}
 for n,digest in deps.items():dest=snapshots/Path(n).name;shutil.copy2(n,dest);assert sha(dest)==digest;bindings[n]=str(dest)
 q=dict(z,script=str(out/'run.lua'),script_sha256=sha(out/'run.lua'),observer_sha256=sha(module),dependencies=deps,dependency_snapshots=bindings,controller={f.name:sha(f)for f in controller.iterdir()if f.is_file()},parent_preparation_sha256=sha(a.parent/'preparation.json'),static_dispatcher=True,static_dispatcher_last=True,original_observer_sha256=sha(original),scope='Same exact df515 ROM, numeric mode, input stream/policy and all guard/output bodies; only callback registration is moved out of runtime. Raster gate retains original epoch. New single exec-range dispatcher is last after complete harness. No native result yet.')
 (a.output/'preparation.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(preparation_sha256=sha(a.output/'preparation.json'),script_sha256=q['script_sha256'],mode=q['mode'],variant=q['variant'],ROM_sha256=q['ROM_sha256'])))

if __name__=='__main__':main()
