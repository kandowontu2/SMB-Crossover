"""Compose only two frozen lives fixes through actual source compilation."""
from pathlib import Path
import difflib,json,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_functional_roster_visuals58_v1 as B
from private_build_outputs_v1 import validate
from check_tmnt_render_oa import load
P=R/'build/arthur-goku-smb2-palette-v1';F=R/'build/ff-lives-body-palette-v1';S=R/'build/smb2-late-lives-palette-v6'
O=R/'build/coherent62-lives-fixes-v1';J=O/'joint'
def main():
 assert not O.exists()
 roots=[(F/'handoff.json','5aa9827298535cb2ac5bc88d276ce5f37076a1283b3143140b1e113023247667'),(S/'handoff-qualified-v2.json','cdaecb1a19548d1fa5de26885a9d5b636228d3d2ecfc1bb599a63f1c9b3d8c69')]
 for p,h in roots:assert B.sha(p)==h;B.bound(json.loads(B.read(p)))
 shutil.copytree(F/'joint',J)
 def rt(t):return t.replace(str(F/'joint'),str(J)).replace((F/'joint').as_posix(),J.as_posix())
 for p in J.rglob('*'):
  if p.is_file()and p.suffix in ['.s','.inc','.cfg']:B.write(p,rt(B.read(p)))
 patch=[]
 for rel in ['smb2/smb2_roster.s','smb2/smb2_roster_host_v5.s']:
  p=J/rel;old=B.read(p);t=B.read(S/'joint'/rel);B.write(p,t);patch.extend(difflib.unified_diff(old.splitlines(True),t.splitlines(True),fromfile='frozenFFlives/'+rel,tofile='combinedlives/'+rel))
 c=json.loads(B.read(S/'component-build.json'))['command'][:];c[1:1]=['-I',str(J),'-I',str(J/'smb2')]
 for flag in ['-o','--create-full-dep','--create-dep']:
  if flag in c:c[c.index(flag)+1]=str(J/Path(c[c.index(flag)+1]).name)
 c[-1]=str(J/'component.s')
 link=json.loads(B.read(F/'final-link.json'))['command'][:];old=str(P/'joint/component.o');assert link.count(old)==1;link[link.index(old)]=str(J/'component.o')
 for flag in ['-o','-Ln','-m','--dbgfile','--mapfile','-C']:
  if flag in link:link[link.index(flag)+1]=str(J/Path(link[link.index(flag)+1]).name)
 k=link.index('--ld-args')+1;v=link[k].split(',')
 for i in range(1,len(v),2):v[i]=str(J/Path(v[i]).name)
 link[k]=','.join(v);recipes=[('component-build',c),('final-link',link)]
 B.write(O/'output-preflight.json',json.dumps([dict(step=n,validation=validate(cmd,J,cwd=R))for n,cmd in recipes],indent=2)+'\n')
 for n,cmd in recipes:
  validate(cmd,J,cwd=R);z=subprocess.run(cmd,cwd=R,text=True,capture_output=True);B.write(O/(n+'.json'),json.dumps(dict(command=cmd,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr),indent=2)+'\n');assert z.returncode==0,(n,z.stderr)
 from prepare_cv3_dmc_mirror import prepare
 prepare(R,J/'candidate.nes')
 base,ff,s2,out=[load(k/'joint/candidate.nes')for k in [P,F,S,O]];fd=[i for i,(a,b)in enumerate(zip(base['raw'],ff['raw']))if a!=b];sd=[i for i,(a,b)in enumerate(zip(base['raw'],s2['raw']))if a!=b];assert len(fd)==21 and len(sd)==206 and not set(fd)&set(sd)
 expected=bytearray(ff['raw'])
 for i in sd:assert expected[i]==base['raw'][i];expected[i]=s2['raw'][i]
 assert out['raw']==bytes(expected),'Source-linked candidate differs from exact disjoint leaf composition'
 assert all(int(v['val'],0)==int(out['syms'][n]['val'],0)for n,v in ff['syms'].items()if n in out['syms']), 'old public PCs moved'
 for n in ['ram3.bin','ff-cookie.bin','code.bin','data.bin']:assert B.sha(J/n)==B.sha(F/'joint'/n)==B.sha(P/'joint'/n)
 B.write(O/'source.patch',''.join(patch))
 d=dict(status='SOURCE_COMPOSED62_BOTH_LIVES_FIXES_TARGETED_CONTROLS_PENDING',source=True,candidate=B.sha(J/'candidate.nes'),joint=str(J.resolve()),native=False,installed=False,parent=B.sha(P/'joint/candidate.nes'),FF_leaf=B.sha(F/'handoff.json'),S2_leaf=B.sha(S/'handoff-qualified-v2.json'),changed_bytes=227,FF_changed_bytes=21,S2_changed_bytes=206,disjoint_actual_source_composition=True,header_CHR_public_PCs_payloads_cookies_exact=True,ready=62,no_new_lease=True,FF_gameplay_deadline419_fixed=False,bindings={str(p.resolve()):B.sha(p)for p in [Path(__file__),F/'handoff.json',S/'handoff-qualified-v2.json',J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',J/'ram3.bin',J/'ff-cookie.bin',O/'source.patch',O/'output-preflight.json']})
 B.write(O/'source-stage.json',json.dumps(d,indent=2)+'\n');B.write(J/'source-stage.json',json.dumps(d,indent=2)+'\n')
 for p,h in roots:assert B.sha(p)==h;B.bound(json.loads(B.read(p)))
 print(json.dumps({k:v for k,v in d.items()if k!='bindings'}),flush=True)
if __name__=='__main__':main()
