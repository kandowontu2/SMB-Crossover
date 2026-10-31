"""Source-link CF bootstrap/guard plus granted36B retirement on9529.

No common resolver, lifecycle, frontend or readiness producer is modified.
"""
from pathlib import Path
import hashlib,json,re,subprocess,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from prepare_ff_current_component_v2 import qualified
from prepare_cv3_dmc_mirror import prepare as mirror
P=R/'build/cf-owner-retirement-v2';K=R/'build/contra-force-palette-names-kernel-v3'
O=R/'build/contra-force-palette-names-cart-v2';J=O/'joint'
G0=R/'docs/qa/checkpoints/2026-10-31/contra-force-loader-resources/root-review-and-reservations.json'
G1=R/'docs/qa/checkpoints/2026-10-31/contra-force-rom-guard-resources/root-review-and-reservations.json'
G2=R/'docs/qa/checkpoints/2026-10-31/contra-force-retire-resources/root-review-and-reservations.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def bound(d):
 for p,h in d['bindings'].items():assert sha(p)==h,p
def put(p,d):p.write_text(json.dumps(d,indent=2)+'\n')

def main():
 assert not O.exists();J.mkdir(parents=True);logs=[]
 try:
  parent=json.loads((P/'handoff.json').read_text());bound(parent)
  assert parent['candidate']=='f5231061660c6b898554a86c429db8357bd80da71b8aa38525b09636a6eb8e5e'
  kernel=json.loads((K/'build-proof.json').read_text());bound(kernel)
  g0,g1,g2=(json.loads(p.read_text())for p in[G0,G1,G2]);bound(g0);bound(g1);bound(g2)
  assert sha(G1)=='3bb5b3e3c0c2f9d30d424c5523f4bcf084af00bf57a6c504d0a3385b95135956'
  recipe=json.loads((P/'final-link.json').read_text())['command'];objects=[v for v in recipe if Path(v).suffix.lower()=='.o']
  for p in objects:assert parent['bindings'].get(str(Path(p).resolve()))==sha(p),p
  cl=R/'tools/Windows/cc65/bin/cl65.exe';ca=cl.with_name('ca65.exe')
  def run(cmd):
   guard=validate(cmd,O,cwd=R);p=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
   logs.append(dict(command=cmd,cwd=str(R),output_guard=guard,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr));put(O/'commands.json',logs);assert p.returncode==0,logs[-1]
  def side_files(text,prefix):
   count=0
   def rename(m):
    nonlocal count
    if m[1]in['','%O']:return m[0]
    p=J/'sideoutputs'/prefix/('%02d-'%count+Path(m[1]).name);count+=1;p.parent.mkdir(parents=True,exist_ok=True)
    return 'file="'+p.as_posix()+'"'
   return re.sub(r'file\s*=\s*"([^"]*)"',rename,text)
  def link(cfg,name,objs):
   run([str(cl),'--cpu','6502x','-t','nes','-C',str(cfg),'-Ln',str(J/(name+'.lbl')),'--ld-args','--dbgfile,'+str(J/(name+'.dbg')),'-o',str(J/(name+'.nes')),*objs,'-m',str(J/(name+'.map'))]);mirror(R,J/(name+'.nes'))
  original=(P/'joint/private.cfg').read_text();(J/'baseline.cfg').write_text(side_files(original,'baseline'));link(J/'baseline.cfg','baseline',objects)
  assert sha(J/'baseline.nes')==parent['candidate']
  banks=[]
  for bank in[1,2,3]:
   data=bytearray((K/f'ram{bank}.bin').read_bytes());data.extend([0]*(8192-len(data)));assert len(data)==8192
   if bank in[2,3]:data[0x1fe0:]=bytes(32)
   (J/f'cf-ram{bank}.bin').write_bytes(data);banks.append(data)
  payload=b''.join(banks);(J/'cf-stream.bin').write_bytes(payload)
  cookie=bytes([0xa7,31,0,1])+hashlib.sha256(payload).digest()[:12];(J/'cf-cookie.bin').write_bytes(cookie)
  loader=(R/'tools/reference/contra_force_loader_checkpoint_v1.s').read_text();needle=' .byte $a7,$1f,0,1\n .res 12,0                    ; MEASUREMENT ONLY, final payload SHA required';assert loader.count(needle)==1
  (J/'cf-loader.s').write_text(loader.replace(needle,'.incbin "'+(J/'cf-cookie.bin').as_posix()+'"'))
  (J/'cf-guard.s').write_bytes((R/'tools/reference/contra_force_rom_guard_v1.s').read_bytes())
  (J/'cf-retire.s').write_bytes((R/'tools/reference/contra_force_retire_proposal_v2.s').read_bytes())
  body=R/'build/contra-force-body-pack-v3/atlas.chr';shots=R/'build/contra-force-shot-pack-v1/atlas.chr'
  (J/'cf-carrier.s').write_text('.segment "CF_CARRIER"\n.incbin "'+(J/'cf-stream.bin').as_posix()+'"\n.segment "CF_BODY_CHR"\n.incbin "'+body.as_posix()+'"\n.segment "CF_SHOT_CHR"\n.incbin "'+shots.as_posix()+'"\n')
  cfg=side_files(original,'candidate')
  assert cfg.count('CF_RETIRE_MEM:start=$bfbd,size=$24')==1 and cfg.count('CF_RETIRE_PROPOSAL:load=CF_RETIRE_MEM')==1
  (J/'private.cfg').write_text(cfg);extras=[]
  for n in['cf-loader','cf-guard','cf-retire','cf-carrier']:
   extras.append(str(J/(n+'.o')));run([str(ca),'--cpu','6502x','-g','-I',str(J),'--create-full-dep',str(J/(n+'.dep')),'-o',str(J/(n+'.o')),str(J/(n+'.s'))])
  link(J/'private.cfg','candidate',[q for q in objects if Path(q).name not in['cf-loader.o','cf-guard.o','cf-carrier.o','cf-retire.o']]+extras)
  a,b=qualified(P/'joint/candidate.nes'),qualified(J/'candidate.nes')
  assert len(a['raw'])==len(b['raw'])and a['raw'][:16]==b['raw'][:16]
  moved={n:[v['val'],b['syms'].get(n,{}).get('val')]for n,v in a['syms'].items()if b['syms'].get(n,{}).get('val')!=v['val']}
  assert all(n.startswith('Cf')and 0xce68<=int(x[0],0)<0xcf86 for n,x in moved.items()),moved
  for n in ['CfLoaderProposal','CfLoaderCoreProposal','CfLoaderExpectedCookie','CfOrBtCheck']:assert a['syms'][n]['val']==b['syms'][n]['val'],n
  ranges=[[16+row['physical_bank']*8192+row['first_offset'],16+row['physical_bank']*8192+row['end_offset_exclusive']]for row in g0['ROM']+[g1['ROM'],g2['ROM']]]
  ranges.append([16+1048576+935*1024,16+1048576+969*1024])
  delta=[i for i,(x,y)in enumerate(zip(a['raw'],b['raw']))if x!=y];assert all(any(lo<=i<hi for lo,hi in ranges)for i in delta)
  for pc,bank,n in[(0xbf47,69,'CfOrBtCheck'),(0xadc0,93,'BtCheck'),(0xbfbd,69,'CfRetire')]:
   from check_tmnt_render_oa import address,location
   assert address(b,n)==pc and(location(b,n)-16)//8192==bank,(n,address(b,n))
  bound(parent);bound(kernel);bound(g0);bound(g1);bound(g2)
  prior=R/'build/contra-force-guarded-cart-v2/joint/candidate.nes'
  prior_raw=prior.read_bytes();changed=[i for i,(x,y)in enumerate(zip(prior_raw,b['raw']))if x!=y]
  oldret=P/'joint/candidate.nes';oldraw=oldret.read_bytes()
  cold_delta=[i for i,(x,y)in enumerate(zip(oldraw,b['raw']))if x!=y]
  changed_allowed=[(16+69*8192+0x1fad,16+69*8192+0x1fbd),(16+78*8192+0xe68,16+78*8192+0xf96),(16+69*8192+0x1fbd,16+69*8192+0x1fe1),(16+1048576+935*1024,16+1048576+959*1024)]
  assert cold_delta and all(any(lo<=i<hi for lo,hi in changed_allowed)for i in cold_delta),cold_delta[:16]
  assert address(b,'CfLoaderExpectedCookie')==0xcf86
  out=dict(previous_shared_cart=sha(oldret),only_owned_loader_retire_carrier_and_cookie_records_change=True,changed_from_shared=len(cold_delta),moved_own_CF_internal_labels=moved,checkpoint='Actual native X5PublishChr internal before borrowedPPU copy; priorowners must still be retired bycaller',passed=True,source=True,native=False,ready=False,installed=False,status='CF_SOURCE_WARM_LIFE_PLAYER_POLICY_PENDING_COLD_HOOKS_AND_PALETTE',parent=parent['candidate'],candidate=sha(J/'candidate.nes'),actual_parent_source_reproduction=sha(J/'baseline.nes'),all_nonCF_native_symbol_PCs_exact=len(a['syms'])-len(moved),public_CF_entries_exact=True,changed_bytes=len(delta),allowed_ranges=ranges,payload_sha256=hashlib.sha256(payload).hexdigest(),cookie=cookie.hex(),shared_resolver_and_lifecycle_and_frontend_unchanged=True,
    bindings={**parent['bindings'],str((P/'handoff.json').resolve()):sha(P/'handoff.json'),str((K/'build-proof.json').resolve()):sha(K/'build-proof.json'),str(G0.resolve()):sha(G0),str(G1.resolve()):sha(G1),str(G2.resolve()):sha(G2),str(prior.resolve()):sha(prior),str(oldret.resolve()):sha(oldret),str((R/'tools/reference/contra_force_loader_checkpoint_v1.s').resolve()):sha(R/'tools/reference/contra_force_loader_checkpoint_v1.s'),str(Path(__file__).resolve()):sha(__file__),str((R/'tools/audit/private_build_outputs_v1.py').resolve()):sha(R/'tools/audit/private_build_outputs_v1.py'),**{str(p.resolve()):sha(p)for p in O.rglob('*')if p.is_file()}})
  path=O/'source-stage.json';put(path,out);print(json.dumps(dict(path=str(path),sha256=sha(path),candidate=out['candidate'],symbols=out['all_nonCF_native_symbol_PCs_exact'],changed=len(delta))),flush=True)
 except Exception as e:put(O/'negative.json',dict(passed=False,error=repr(e),traceback=traceback.format_exc()));raise

if __name__=='__main__':main()

