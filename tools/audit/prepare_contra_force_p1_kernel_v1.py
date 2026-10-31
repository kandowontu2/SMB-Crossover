"""Build granted selected31 P1 private kernel; no shared source cart here."""
from pathlib import Path
import hashlib,json,re,subprocess,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address
P=R/'build/contra-force-palette-names-kernel-v3';O=R/'build/contra-force-p1-kernel-v1'
N=R/'build/cf-cold-warm-palette-source-v1/joint/candidate.nes'
G=R/'docs/qa/checkpoints/2026-10-31/contra-force-p1-experimental-resources/root-review-and-reservations.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not O.exists();O.mkdir();logs=[]
 try:
  d=json.loads((P/'build-proof.json').read_text());grant=json.loads(G.read_text())
  for p,h in {**d['bindings'],**grant['bindings']}.items():assert sha(p)==h,p
  assert sha(G)=='4dc474df018af488a3464e31a2ab1261c99ba3b07870fc402b0e40957a9dba90'
  old=json.loads((P/'build-log.json').read_text());names=[Path(x['command'][-1]).stem for x in old if Path(x['command'][0]).stem=='ca65']
  for n in names:(O/(n+'.s')).write_bytes((P/(n+'.s')).read_bytes())
  (O/'state.inc').write_bytes((P/'state.inc').read_bytes())
  cfg=(P/'runtime.cfg').read_text();i=cfg.rfind('}');cfg=cfg[:i]+''.join(' '+n+':load='+bank+',type='+kind+';\n'for n,bank,kind in [('CF_P1_STATE','C2','bss'),('CF_P1_TAG','A3','ro'),('CF_P1_LATE','A3','ro'),('CF_P1_PACKET','A1','ro'),('CF_P1_HEARTBEAT','A3','ro'),('CF_P1_ACQUIRE','A3','ro'),('CF_P1_GATE','A3','ro'),('CF_P1_NATIVE_MASK','A3','ro')])+cfg[i:];(O/'runtime.cfg').write_text(cfg)
  sources={'host-runtime.s':'contra_force_host_runtime_v10.s','render.s':'contra_force_host_render_v5.s','a2-router.s':'contra_force_a2_router_v7.s','palette-names.s':'contra_force_host_palette_names_v3.s','p1-runtime.s':'contra_force_p1_runtime_v1.s'}
  for n,p in sources.items():(O/n).write_bytes((R/'tools/reference'/p).read_bytes())
  oldmask=(R/'build/contra-force-p1-epoch-proposal-v2/native-mask-table.s').read_text();assert 'CF_P1_MASK_PROPOSAL' in oldmask
  (O/'native-mask.s').write_text(oldmask.replace('CF_P1_MASK_PROPOSAL','CF_P1_NATIVE_MASK'));names+=['p1-runtime','native-mask']
  b=qualified(N);t=(O/'native-imports.s').read_text()
  for n in ['SprObject_SprAttrib','ObjectMetasprite','SmFreezePalettePacket','SmFreezePalettePending','SmFreezeLastBlue','SmFreezeTurn','SmFreezePaletteControl']:
   if not re.search(r'^\.export '+n+'$',t,re.M):t+='\n.export '+n+'\n'+n+'=$%04x\n'%address(b,n)
  (O/'native-imports.s').write_text(t)
  ca=R/'tools/Windows/cc65/bin/ca65.exe';ld=ca.with_name('ld65.exe')
  cmds=[[str(ca),'--cpu','6502x','-g','-I',str(R/'build/contra-force-reproduction-v2'),'--create-full-dep',str(O/(n+'.dep')),'-o',str(O/(n+'.o')),str(O/(n+'.s'))]for n in names]
  cmds+=[[str(ld),'-C',str(O/'runtime.cfg'),'-o',str(O/'unused.bin'),'--dbgfile',str(O/'runtime.dbg'),'-Ln',str(O/'runtime.lbl'),'-m',str(O/'runtime.map'),*[str(O/(n+'.o'))for n in names]]]
  for cmd in cmds:
   g=validate(cmd,O,cwd=O);q=subprocess.run(cmd,cwd=O,capture_output=True,text=True);logs.append(dict(command=cmd,cwd=str(O),output_guard=g,returncode=q.returncode,stdout=q.stdout,stderr=q.stderr));(O/'build-log.json').write_text(json.dumps(logs,indent=2)+'\n');assert q.returncode==0,logs[-1]
  l={n:int(v,16)for v,n in re.findall(r'al ([0-9A-Fa-f]+) \.(\w+)',(O/'runtime.lbl').read_text())}
  assert l['CfHostLastLife']==0xddb8 and l['CfP1SavedAttributes']==0xddb9 and l['CfP1NativeC']==0xddd1
  assert l['CfServiceVeneers']==0xbe00 and l['CfA2RouterEnd']<=0xbfe0
  # Native-mask is last appended A3 segment; preserve approved cookie tail.
  assert l['CfNativeP1Mask']+145<=0xbfe0
  out=dict(passed=True,source=True,native=False,ready=False,shared_hook_installed=False,own_C2=[l['CfP1SavedAttributes'],l['CfP1NativeC']+1],A1_packet=l['CfP1Packet'],A3_end=l['CfNativeP1Mask']+145,A2_end=l['CfA2RouterEnd'],
   limitations=['No executed scheduler/pixel/lifecycle/IRQ proof yet','Invalid priorC1 cache palette cleanup still explicit pending','Public6 injury-status protected by phasebit7 ofexisting rendererTag02DF; new source caller proof pending'],
   bindings={str(p.resolve()):sha(p)for p in[Path(__file__),P/'build-proof.json',G,N,N.with_suffix('.dbg'),R/'build/contra-force-p1-epoch-proposal-v2/proposal.json',*[R/'tools/reference'/p for p in sources.values()],R/'tools/audit/private_build_outputs_v1.py',*[p for p in O.iterdir()if p.is_file()]]})
  p=O/'build-proof.json';p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(path=str(p),sha256=sha(p),ownC2=out['own_C2'],A3end=out['A3_end'],A2end=out['A2_end'],A1packet=out['A1_packet'])),flush=True)
 except Exception as e:(O/'negative.json').write_text(json.dumps(dict(passed=False,error=repr(e),traceback=traceback.format_exc(),logs=logs),indent=2)+'\n');raise
if __name__=='__main__':main()
