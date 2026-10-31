"""Build actual CF graphics/early draw/portrait within existing A3/C2 leases."""
from pathlib import Path
import hashlib,json,re,subprocess,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
P=R/'build/contra-force-a2-router-v2';O=R/'build/contra-force-lifecycle-kernel-v6'
N=R/'build/cf-owner-retirement-v2/joint/candidate.nes'
S=R/'tools/reference/contra_force_host_render_v3.s';H=R/'tools/reference/contra_force_a2_router_v5.s'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not O.exists();O.mkdir();logs=[]
 try:
  d=json.loads((P/'build-proof.json').read_text())
  for p,h in d['bindings'].items():assert sha(p)==h,p
  commands=json.loads((P/'build-log.json').read_text());names=[Path(x['command'][-1]).stem for x in commands if Path(x['command'][0]).stem=='ca65']
  for n in names:(O/(n+'.s')).write_bytes((P/(n+'.s')).read_bytes())
  (O/'state.inc').write_bytes((P/'state.inc').read_bytes());(O/'runtime.cfg').write_bytes((P/'runtime.cfg').read_bytes())
  (O/'host-runtime.s').write_bytes((R/'tools/reference/contra_force_host_runtime_v9.s').read_bytes());
  cfg=(O/'runtime.cfg').read_text();at=cfg.rfind('}');assert at>0;cfg=cfg[:at]+' CF_HOST_LIFECYCLE_STATE:load=C2,type=rw;\n'+cfg[at:];(O/'runtime.cfg').write_text(cfg)
  (O/'render.s').write_bytes(S.read_bytes());(O/'a2-router.s').write_bytes(H.read_bytes())
  b=qualified(N);imports=['ObjectMetasprite','SmPosePtr','BlankPalette','RgOamRotation','GuestOamRotationActive','OperMode','InjuryTimer','MmDeathFlag','FrameCounter','CurrentPlayer','NumberofLives','JnResetDispatch','FarCallCommon','SafecallA_SMC','FarcallJmpTarget_SMC','OperMode','FamilyMainCommit','Mirror_PPUMASK','DisableScreenFlag','NmiDisable','GamePauseStatus']
  text=(O/'native-imports.s').read_text()
  for n in imports:
   if not re.search(r'^\.export '+n+r'$',text,re.M):text+='\n.export '+n+'\n'+n+'=$%04x\n'%address(b,n)
  resetbank=((location(b,'JnResetDispatch')-16)//8192)|128
  text+='\n; Actual current source DBG bank from JnResetDispatch; not .bank() of an absolute PC alias.\n.export CfNativeResetBank\nCfNativeResetBank=$%02x\n'%resetbank
  (O/'native-imports.s').write_text(text)
  zero=location(b,'BlankPalette')+7;assert b['raw'][zero]==0 and(address(b,'BlankPalette')+7)<0xa000
  assert address(b,'CfLoaderExpectedCookie')==0xcf86
  ca=R/'tools/Windows/cc65/bin/ca65.exe';ld=ca.with_name('ld65.exe')
  cmds=[[str(ca),'--cpu','6502x','-g','-I',str(R/'build/contra-force-reproduction-v2'),'--create-full-dep',str(O/(n+'.dep')),'-o',str(O/(n+'.o')),str(O/(n+'.s'))]for n in names]
  cmds+=[[str(ld),'-C',str(O/'runtime.cfg'),'-o',str(O/'unused.bin'),'--dbgfile',str(O/'runtime.dbg'),'-Ln',str(O/'runtime.lbl'),'-m',str(O/'runtime.map'),*[str(O/(n+'.o'))for n in names]]]
  for cmd in cmds:
   guard=validate(cmd,O,cwd=O);q=subprocess.run(cmd,cwd=O,capture_output=True,text=True);logs.append(dict(command=cmd,cwd=str(O),output_guard=guard,returncode=q.returncode,stdout=q.stdout,stderr=q.stderr));(O/'build-log.json').write_text(json.dumps(logs,indent=2)+'\n');assert q.returncode==0,logs[-1]
  labels={n:int(v,16)for v,n in re.findall(r'al ([0-9A-Fa-f]+) \.(\w+)',(O/'runtime.lbl').read_text())}
  assert labels['CfHostLastLife']==0xddb8
  assert labels['CfServiceVeneers']==0xbe00 and labels['CfServiceUnavailable']==0xbe6c
  out=dict(passed=True,source=True,native=False,ready=False,actual_cart_hooks=False,
   presentation_entries={n:labels[n]for n in['CfHostGraphics','CfHostDraw','CfHostPortrait','CfHostRenderBody','CfHostRenderShot']},
   resident_empty_header=dict(source='genuine BlankPalette+7 data terminator',PC=address(b,'BlankPalette')+7,physical_ROM=(zero-16)//8192,value=0),
   changes='Own source renderer honors actual native OAM rotation; early typedDraw2 emits body/shots and suppresses only nativebody using ObjectMetasprite0 and resident zero reservation. Portrait uses authenticated idle frames and temporary lives positioning, restoring source pose/nativeY.',
   open=['No natural cold/shared hook or readiness','P0/shotP1 commit and late lives packet still pending','Actual complete native DrawAll/sourcepixel controls not yet run'],
   bindings={str(p.resolve()):sha(p)for p in[Path(__file__),S,H,R/'build/contra-force-lifecycle-kernel-v1/negative.json',R/'build/contra-force-lifecycle-kernel-v2/negative.json',R/'tools/reference/contra_force_host_runtime_v9.s',P/'build-proof.json',N,N.with_suffix('.dbg'),ca,ld,R/'tools/audit/private_build_outputs_v1.py',*[p for p in O.iterdir()if p.is_file()]]})
  p=O/'build-proof.json';p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(path=str(p),sha256=sha(p),entries=out['presentation_entries'])),flush=True)
 except Exception as e:(O/'negative.json').write_text(json.dumps(dict(passed=False,error=repr(e),traceback=traceback.format_exc(),commands=logs),indent=2)+'\n');raise
if __name__=='__main__':main()
