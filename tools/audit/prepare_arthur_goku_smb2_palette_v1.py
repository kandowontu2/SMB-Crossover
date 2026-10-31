"""Surgical source adoption of frozen native-BG/red-eye producer on remap.

The exact205-byte source leaf commutes with the private remap's disjoint
menu/gate edits. Binary deltas are compared after genuine source linking;
they are never used to produce or patch a ROM.
"""
from pathlib import Path
import difflib,json,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_functional_roster_visuals58_v1 as B
from private_build_outputs_v1 import validate
from check_tmnt_render_oa import load,address
P=R/'build/arthur-goku-select-remap-v3';S=R/'build/smb2-eye-sky-v3';Q=R/'build/functional-roster-coherent62-v4'
O=R/'build/arthur-goku-smb2-palette-v1';J=O/'joint'

def main():
 assert not O.exists()
 inputs=[(P/'handoff.json','079d1e5c7da5dd0467ecfdb068aee1dc3c9b097f2b92852bdc31ca19dca4b58a'),(S/'handoff.json','ff49c753b8d323eea5ab4a342bd8dfaf79d9438522e0d9fca39a1a28b82bb850')]
 for p,h in inputs:assert B.sha(p)==h;B.bound(json.loads(B.read(p)))
 shutil.copytree(P/'joint',J)
 def rt(t):return t.replace(str(P/'joint'),str(J)).replace((P/'joint').as_posix(),J.as_posix())
 for p in J.rglob('*'):
  if p.is_file()and p.suffix in['.s','.inc','.cfg']:B.write(p,rt(B.read(p)))
 patch=[]
 for rel in['smb2/smb2_roster_palette_v2.s','smb2/smb2_roster_main_v2.s','smb2/smb2_roster_art.inc','asset.s','eye-red.chr']:
  p=J/rel;prior=p.read_bytes()if p.exists()else b'';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((S/'joint'/rel).read_bytes())
  if p.suffix in['.s','.inc']:patch.extend(difflib.unified_diff(prior.decode().splitlines(True),B.read(p).splitlines(True),fromfile='frozen-remap/'+rel,tofile='remap-native-BG-eye/'+rel))
 recipes=[]
 for name,source in[('component-build','component.s'),('asset-build','asset.s')]:
  c=json.loads(B.read(S/(name+'.json')))['command'][:];c[1:1]=['-I',str(J),'-I',str(J/'smb2')]
  for flag in['-o','--create-full-dep','--create-dep']:
   if flag in c:c[c.index(flag)+1]=str(J/Path(c[c.index(flag)+1]).name)
  c[-1]=str(J/source);recipes.append((name,c))
 link=json.loads(B.read(P/'final-link.json'))['command'][:]
 for old,new in[(Q/'joint/component.o',J/'component.o'),(R/'build/smb2-current-component-v1/asset.o',J/'asset.o')]:
  assert link.count(str(old))==1,str(old);link[link.index(str(old))]=str(new)
 for flag in['-o','-Ln','-m','--dbgfile','--mapfile','-C']:
  if flag in link:link[link.index(flag)+1]=str(J/Path(link[link.index(flag)+1]).name)
 if '--ld-args'in link:
  k=link.index('--ld-args')+1;v=link[k].split(',')
  for i in range(1,len(v),2):v[i]=str(J/Path(v[i]).name)
  link[k]=','.join(v)
 recipes.append(('final-link',link))
 B.write(O/'output-preflight.json',json.dumps([dict(step=n,validation=validate(c,J,cwd=R))for n,c in recipes],indent=2)+'\n')
 for n,c in recipes:
  validate(c,J,cwd=R);z=subprocess.run(c,cwd=R,text=True,capture_output=True);B.write(O/(n+'.json'),json.dumps(dict(command=c,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr),indent=2)+'\n');assert z.returncode==0,(n,z.stderr)
 from prepare_cv3_dmc_mirror import prepare
 prepare(R,J/'candidate.nes')
 old=load(P/'joint/candidate.nes');new=load(J/'candidate.nes')
 base=(Q/'joint/candidate.nes').read_bytes();leaf=(S/'joint/candidate.nes').read_bytes();expected=bytearray(old['raw']);diff=[i for i,(a,b)in enumerate(zip(base,leaf))if a!=b]
 assert len(diff)==205
 for i in diff:assert expected[i]==base[i],('overlapping remap/palette delta',i);expected[i]=leaf[i]
 assert new['raw']==bytes(expected),'Source-linked combined cart differs from exact disjoint205-byte composition'
 for n in['FmPending','FmResolve','FmToggle','FmQueueName','FmStartFlags','NrMenuCharacter','NrMenuAltTail','CrossoverMenuInput','MenuResolveCharacter','MaaFresh','HuEntryBase','HuEnd','GmCommonNmiStart','GmCommonNmiEnd','S2ServiceVeneers','QwService','DpAdmissionPortrait','S2MainPalette','S2MainSpawn']:assert address(old,n)==address(new,n),n
 for n in['ram3.bin','ff-cookie.bin','code.bin','data.bin']:assert B.sha(J/n)==B.sha(P/'joint'/n),n
 assert old['raw'][:16]==new['raw'][:16]
 B.write(O/'source.patch',''.join(patch))
 d=dict(status='SOURCE_LINKED_REMAP_S2_NATIVE_BG_RED_EYE_TARGETED_CONTROLS_PENDING',source=True,candidate=B.sha(J/'candidate.nes'),parent=B.sha(P/'joint/candidate.nes'),S2_palette_eye_leaf=B.sha(S/'handoff.json'),native=False,installed=False,ready=62,no_new_leases=True,exact205_owned_bytes_from_frozen_leaf=True,remap_all_other_bytes_exact=True,Quick_Arthur_FF_WRAM_cookie_exact=True,public_PCs_exact=True,native_negative_correction='Frozen oldremap note hypothesized fullP0header3F10. Authoritative negative is bulk native3F00=0F without subsequent nativeBackgroundColors restore; oldS2MainPalette already wrote3F11..13. Frozenleaf now supplies genuine BackgroundColorCtrl/AreaType-native header plus original3body shades and source-exact red eye P2.',bindings={str(p.resolve()):B.sha(p)for p in[Path(__file__),P/'handoff.json',S/'handoff.json',J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',J/'ram3.bin',J/'ff-cookie.bin',O/'output-preflight.json',O/'source.patch']})
 B.write(O/'source-stage.json',json.dumps(d,indent=2)+'\n');B.write(J/'source-stage.json',json.dumps(d,indent=2)+'\n')
 for p,h in inputs:assert B.sha(p)==h;B.bound(json.loads(B.read(p)))
 print(json.dumps({k:v for k,v in d.items()if k!='bindings'}))

if __name__=='__main__':main()
