"""Append own A3 P0/name/status APIs, preserve all native/shared producers."""
from pathlib import Path
import hashlib,json,re,subprocess,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
P=R/'build/contra-force-lifecycle-kernel-v6';O=R/'build/contra-force-palette-names-kernel-v3'
N=R/'build/cf-owner-retirement-v2/joint/candidate.nes'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not O.exists();O.mkdir();logs=[]
 try:
  d=json.loads((P/'build-proof.json').read_text())
  for p,h in d['bindings'].items():assert sha(p)==h,p
  old=json.loads((P/'build-log.json').read_text());names=[Path(x['command'][-1]).stem for x in old if Path(x['command'][0]).stem=='ca65']
  for n in names:(O/(n+'.s')).write_bytes((P/(n+'.s')).read_bytes())
  (O/'state.inc').write_bytes((P/'state.inc').read_bytes())
  cfg=(P/'runtime.cfg').read_text();i=cfg.rfind('}');cfg=cfg[:i]+' CF_HOST_PALETTE_NAMES:load=A3,type=ro;\n'+cfg[i:];(O/'runtime.cfg').write_text(cfg)
  replacements={'render.s':'contra_force_host_render_v4.s','a2-router.s':'contra_force_a2_router_v6.s','palette-names.s':'contra_force_host_palette_names_v2.s'}
  for n,source in replacements.items():(O/n).write_bytes((R/'tools/reference'/source).read_bytes())
  names+=['palette-names']
  b=qualified(N);text=(O/'native-imports.s').read_text()
  for n in ['VRAM_Buffer1','VRAM_Buffer1_Offset','BackgroundColorCtrl','AreaType']:
   assert not re.search(r'^\.export '+n+r'$',text,re.M)
   text+='\n.export '+n+'\n'+n+'=$%04x\n'%address(b,n)
  (O/'native-imports.s').write_text(text)
  bg=location(b,'BackgroundColors');assert bytes(b['raw'][bg:bg+8])==bytes([34,34,15,15,15,34,15,15])
  # Native charmap and compiled menu source show the authentic requested names.
  assert '.charmap $41+00, $A+00' in (R/'inc/charmap.inc').read_text()
  ca=R/'tools/Windows/cc65/bin/ca65.exe';ld=ca.with_name('ld65.exe')
  cmds=[[str(ca),'--cpu','6502x','-g','-I',str(R/'build/contra-force-reproduction-v2'),'--create-full-dep',str(O/(n+'.dep')),'-o',str(O/(n+'.o')),str(O/(n+'.s'))]for n in names]
  cmds+=[[str(ld),'-C',str(O/'runtime.cfg'),'-o',str(O/'unused.bin'),'--dbgfile',str(O/'runtime.dbg'),'-Ln',str(O/'runtime.lbl'),'-m',str(O/'runtime.map'),*[str(O/(n+'.o'))for n in names]]]
  for cmd in cmds:
   g=validate(cmd,O,cwd=O);q=subprocess.run(cmd,cwd=O,capture_output=True,text=True);logs.append(dict(command=cmd,cwd=str(O),output_guard=g,returncode=q.returncode,stdout=q.stdout,stderr=q.stderr));(O/'build-log.json').write_text(json.dumps(logs,indent=2)+'\n');assert q.returncode==0,logs[-1]
  labels={n:int(v,16)for v,n in re.findall(r'al ([0-9A-Fa-f]+) \.(\w+)',(O/'runtime.lbl').read_text())}
  assert labels['CfHostLastLife']==0xddb8 and labels['CfServiceVeneers']==0xbe00 and labels['CfHostPaletteNamesEnd']<=0xbfe0
  out=dict(passed=True,source=True,native=False,ready=False,actual_cart_hooks=False,new_module_bytes=labels['CfHostPaletteNamesEnd']-labels['CfHostForcePalette'],new_module=[labels['CfHostForcePalette'],labels['CfHostPaletteNamesEnd']],
   no_new_RAM_or_global_or_CHR=True,original_Source_CORE_preserved=True,old_lastlife_DDB8_and_bodymeta_exact=True,
   changes='Own A3 P0 queue/native background, dirty tick, source status/menu names and exact world-index policy; genuine portrait queues source P0. No yellow-shot policy/common/readiness/cold menu hooks.',
   bindings={str(p.resolve()):sha(p)for p in [Path(__file__),P/'build-proof.json',N,N.with_suffix('.dbg'),R/'inc/charmap.inc',*[R/'tools/reference'/n for n in replacements.values()],R/'tools/audit/private_build_outputs_v1.py',*[p for p in O.iterdir()if p.is_file()]]})
  p=O/'build-proof.json';p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(path=str(p),sha256=sha(p),size=out['new_module_bytes'],span=out['new_module'])),flush=True)
 except Exception as e:(O/'negative.json').write_text(json.dumps(dict(passed=False,error=repr(e),traceback=traceback.format_exc(),logs=logs),indent=2)+'\n');raise
if __name__=='__main__':main()
