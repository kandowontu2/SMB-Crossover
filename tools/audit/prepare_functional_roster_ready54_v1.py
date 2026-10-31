"""Source-compose qualified RCR/Chip repairs with native Quick+Arthur v13.

No ROM patching, shared edits, emulator, new leases, or installation.
"""
from pathlib import Path
import difflib,hashlib,json,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from check_tmnt_render_oa import load,address
P=R/'build/current-character-quick-ui-v13/joint'
O=R/'build/functional-roster-ready54-v1';N=O/'joint'
RC=R/'build/current-rcr-misc-chr-fix-1030-v1';CD=R/'build/current-chip-facing-fix-1030-v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def verify(p):
 d=json.loads(Path(p).read_text())
 for n,v in d.get('bindings',{}).items():assert sha(n)==v,n
 return d
def retarget(s):return s.replace(str(P),str(N)).replace(P.as_posix(),N.as_posix())
def run(q,name):
 z=subprocess.run(q,cwd=R,text=True,capture_output=True)
 (O/(name+'.json')).write_text(json.dumps(dict(command=q,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr),indent=2)+'\n')
 assert z.returncode==0,(name,z.stderr)
def main():
 assert not O.exists()
 parent=verify(P.parent/'handoff.json');verify(P.parent/'native-qualified/handoff.json')
 verify(R/'build/arthur-quick-functional-admission-v1/handoff.json')
 cr=verify(CD/'source-proof.json');rr=json.loads((R/'docs/qa/checkpoints/2026-10-30/current-rcr-native-misc-repair/receipt.json').read_text())
 assert rr['source_proof_sha256']==sha(RC/'source-proof.json')
 rp=verify(RC/'source-proof.json')
 assert parent['candidate']=='7a9e2cc1246d590bebe2acd5451267894f39cdac75cd528e20109de01753d760'
 assert cr['changed_ROM_bytes']==1 and rp['changed_ROM_bytes']==409
 O.mkdir();shutil.copytree(P,N)
 for p in N.rglob('*'):
  if p.is_file()and p.suffix in['.s','.inc','.cfg']:
   old=p.read_text();new=retarget(old)
   if old!=new:p.write_text(new,newline='\n')
 # Only genuine source files from the qualified root packets are adopted.
 files=['river_city_required_ink_v1.inc','river_city_shared_palette_art.inc','chip_dale_render.s']
 patches=[]
 for name in files:
  target=N/'src'/name;source=(CD if name.endswith('.s')else RC)/'src'/name
  original=target.read_text();updated=source.read_text()
  if name=='chip_dale_render.s':
   assert original.count(' cmp #2\n beq Left')==1 and updated.count(' cmp #2\n bne Left')==1
  else:
   # RCR source preimage is still the exact installed a7cc producer.
   old=R/'build/celeste-menu-name-current-v2/joint/src'/name
   assert sha(target)==sha(old)
  patches.extend(difflib.unified_diff(original.splitlines(True),updated.splitlines(True),fromfile='native-v13/src/'+name,tofile='ready54/src/'+name))
  target.write_text(updated,newline='\n')
 (O/'source.patch').write_text(''.join(patches),newline='\n')
 commands=[]
 for name,log in [('compile-main',P.parent/'compile-main.json'),('final-link',P.parent/'final-link.json')]:
  q=[retarget(x)for x in json.loads(log.read_text())['command']]
  commands.append((q,name))
 (O/'output-preflight.json').write_text(json.dumps([validate(q,N,cwd=R)for q,_ in commands],indent=2)+'\n')
 for q,name in commands:run(q,name)
 from prepare_cv3_dmc_mirror import prepare
 prepare(R,N/'candidate.nes')
 old,new=[load(x/'candidate.nes')for x in[P,N]]
 diffs=[i for i,(x,y)in enumerate(zip(old['raw'],new['raw']))if x!=y]
 expected=rp['changed_file_offsets']+[cr['changed_file_offset']]
 assert len(diffs)==410 and set(diffs)==set(expected),(len(diffs),set(diffs)^set(expected))
 qualified=(CD/'candidate.nes').read_bytes();assert all(new['raw'][i]==qualified[i]for i in diffs)
 assert old['raw'][:16]==new['raw'][:16]and old['raw'][16+128*8192:]==new['raw'][16+128*8192:]
 moved=[]
 for name in old['syms']:
  try:a=address(old,name);b=address(new,name)
  except(KeyError,TypeError,ValueError):continue
  if a!=b:moved.append([name,a,b])
 assert not moved,moved[:20]
 payloads=['code.bin','data.bin','ram3.bin','quick/cookie.bin','ff-cookie.bin']
 for name in payloads:assert(P/name).read_bytes()==(N/name).read_bytes(),name
 # Everything outside the two exact owner repairs is byte-exact: Quick,
 # Arthur, FF, frontend readiness/names/art, header and every CHR page.
 d=dict(passed=True,native=False,installed=False,candidate=sha(N/'candidate.nes'),parent=sha(P/'candidate.nes'),ready=54,pending=26,
  source_files=['src/'+n for n in files],changed_ROM_bytes=410,changed_file_offsets=diffs,
  all_prior_scoped_symbol_values_exact=True,header_CHR_exact=True,all_other_PRG_exact=True,all_code_data_cookies_exact=payloads,
  Quick_Arthur_ready_predicates_and_registry_unchanged=True,cv3_fixed125_regenerated_from_actual127=True,
  next='Root-controlled native Chip/Dale review. No native run or Downloads install is authorized by this source packet.',
  bindings={str(p.resolve()):sha(p)for p in[Path(__file__),P.parent/'handoff.json',P.parent/'native-qualified/handoff.json',R/'build/arthur-quick-functional-admission-v1/handoff.json',RC/'source-proof.json',CD/'source-proof.json',R/'docs/qa/checkpoints/2026-10-30/current-rcr-native-misc-repair/receipt.json',O/'source.patch',O/'output-preflight.json']})
 (O/'source-proof.json').write_text(json.dumps(d,indent=2)+'\n')
 verify(P.parent/'handoff.json');verify(P.parent/'native-qualified/handoff.json');verify(CD/'source-proof.json')
 print(json.dumps({k:v for k,v in d.items()if k not in['bindings','changed_file_offsets']}))
if __name__=='__main__':main()
