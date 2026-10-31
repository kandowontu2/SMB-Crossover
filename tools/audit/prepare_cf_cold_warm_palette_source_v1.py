"""Surgical own P0/name payload adoption after frozen pending cold/warm stage."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
from prepare_cv3_dmc_mirror import prepare
P=R/'build/cf-cold-warm-source-v3';O=R/'build/cf-cold-warm-palette-source-v1';J=O/'joint'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:Path(p).write_text(json.dumps(q,indent=2)+'\n')

def bound(p):
 q=json.loads(Path(p).read_text())
 for f,h in q['bindings'].items():assert sha(f)==h,('frozen input',f)
 return q

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--cf-handoff',required=True,type=Path);ap.add_argument('--cf-joint',required=True,type=Path);a=ap.parse_args();a.cf_handoff=a.cf_handoff.resolve();a.cf_joint=a.cf_joint.resolve()
 assert not O.exists();O.mkdir();logs=[]
 try:
  parent=bound(P/'handoff.json');own=bound(a.cf_handoff)
  assert parent['candidate']=='8f0a925be0f1845952583a28dac7b54dd716c35539cfd65a13df37a7f9cdb310'
  assert sha(a.cf_handoff)=='e82eafd5f921793c7eebde4cefde7ab2f46ffc223c027b45d7712b1394114547'
  for n in['cf-loader.s','cf-guard.s','cf-carrier.s','cf-retire.s','cf-stream.bin','cf-cookie.bin']:assert own['bindings'].get(str((a.cf_joint/n).resolve()))==sha(a.cf_joint/n),n
  shutil.copytree(P/'joint',J)
  # Main/shared/BW/BT producers stay the exact consumed parent objects.
  # Only own4 sources,2assets and link-output config paths are rewritten.
  for n in['cf-loader.s','cf-guard.s','cf-carrier.s','cf-retire.s']:
   s=(a.cf_joint/n).read_text().replace(str(a.cf_joint),str(J)).replace(a.cf_joint.as_posix(),J.as_posix());(J/n).write_text(s)
  for n in['cf-stream.bin','cf-cookie.bin']:shutil.copyfile(a.cf_joint/n,J/n)
  p=J/'private.cfg';s=p.read_text().replace(str(P/'joint'),str(J)).replace((P/'joint').as_posix(),J.as_posix());p.write_text(s)
  def run(n,cmd):
   guard=validate(cmd,O,cwd=R);z=subprocess.run(cmd,cwd=R,capture_output=True,text=True);q=dict(command=cmd,cwd=str(R),output_guard=guard,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr);logs.append(q);save(O/(n+'.json'),q);save(O/'commands.json',logs);assert z.returncode==0,(n,z.stderr)
  ca=R/'tools/Windows/cc65/bin/ca65.exe'
  for n in['cf-loader','cf-guard','cf-carrier','cf-retire']:
   obj=J/(n+'.o');run(n+'-build',[str(ca),'--cpu','6502x','-g','-I',str(J),'-I',str(J/'src'),'-I',str(R),'--create-full-dep',str(obj.with_suffix('.dep')),'-o',str(obj),str(J/(n+'.s'))])
  cmd=json.loads((P/'final-link.json').read_text())['command'][:];rebound={}
  for i,x in enumerate(cmd):
   p=Path(x)
   if p.suffix=='.o'and p.stem in['cf-loader','cf-guard','cf-carrier','cf-retire']:
    assert parent['bindings'].get(str(p.resolve()))==sha(p),p;cmd[i]=str(J/p.name);rebound[p.stem]=str(p)
  assert len(rebound)==4
  for flag in['-C','-Ln','-o','-m']:cmd[cmd.index(flag)+1]=str(J/Path(cmd[cmd.index(flag)+1]).name)
  cmd[cmd.index('--ld-args')+1]='--dbgfile,'+str(J/'candidate.dbg');run('final-link',cmd);prepare(R,J/'candidate.nes')
  old,b=map(qualified,[P/'joint/candidate.nes',J/'candidate.nes'])
  assert all(b['syms'].get(n,{}).get('val')==z['val']for n,z in old['syms'].items())
  for n,side in[('bowser.bin','04-bowser.bin'),('ram3.bin','01-ram3.bin'),('code.bin','02-code.bin'),('data.bin','03-data.bin')]:
   p=J/'sideoutputs/candidate'/side;assert sha(p)==sha(P/'joint'/n),n;shutil.copyfile(p,J/n)
  assert sha(J/'ff-cookie.bin')==sha(P/'joint/ff-cookie.bin')
  for n in['bowser/cold.s','bowser/router.s','bt/router.s','src/full_roster_menu.s','src/cf_menu_body.inc','entrypoint.s','cf-cold-warm.s']:
   assert (J/n).read_bytes()==(P/'joint'/n).read_bytes(),n
  spans=[(location(b,'CfExternalCookie'),16),(location(b,'CfLoaderExpectedCookie'),16),(16+128*8192+935*1024,24*1024)]
  changed=[i for i,(x,y)in enumerate(zip(old['raw'],b['raw']))if x!=y];assert changed and all(any(lo<=i<lo+size for lo,size in spans)for i in changed)
  assert old['raw'][:16]==b['raw'][:16]and b['raw'][16+128*8192+935*1024:16+128*8192+959*1024]==(J/'cf-stream.bin').read_bytes()
  owncart=qualified(a.cf_joint/'candidate.nes')
  assert b['raw'][16+128*8192+935*1024:16+128*8192+969*1024]==owncart['raw'][16+128*8192+935*1024:16+128*8192+969*1024]
  stage=dict(source=True,status='PENDING_CF_P0_NAMES_TARGETED_REBIND_REQUIRED',candidate=sha(J/'candidate.nes'),parent=parent['candidate'],own_CF_candidate=own['candidate'],joint=str(J),ready=66,CF_pending=True,BT_pending=True,native=False,installed=False,admitted=False,no_shared_Main_BW_BT_source_edits=True,no_new_PC_or_state_or_shared_P1_hooks=True,actual_rebound_four_objects=rebound,changed_bytes=len(changed),exact_changed_envelopes=spans,
   remaining=['Real pre-load ROM name18 fallback and future ready preview path','P1 yellow-shot fairness remains unadopted','CF/BT pending; no native/admission'],
   bindings={str(p.resolve()):sha(p)for p in[Path(__file__),P/'handoff.json',a.cf_handoff,J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',J/'private.cfg',J/'cf-stream.bin',J/'cf-cookie.bin',*[J/(n+ext)for n in['cf-loader','cf-guard','cf-carrier','cf-retire']for ext in['.s','.o','.dep']],O/'final-link.json']})
  save(O/'source-stage.json',stage);save(J/'source-stage.json',stage);bound(P/'handoff.json');bound(a.cf_handoff);print(json.dumps({k:v for k,v in stage.items()if k!='bindings'}))
 except Exception as e:save(O/'negative.json',dict(passed=False,error=repr(e),traceback=traceback.format_exc()));raise
if __name__=='__main__':main()
