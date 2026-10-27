"""Compact expanded-only recipe/union/CPU reuse qualification; no emulator."""
from pathlib import Path
from unittest.mock import patch
import ast,difflib,hashlib,json,sys
R=Path(__file__).resolve().parents[2];B=R/'build';P='samus_fixed_hud_current4a'
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools/reference')]
import patch_samus_fixed_hud_v2 as recipe
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location,Memory
from samus_hud_icon_controls_v1 import setup,execute
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 z=json.loads((B/(P+'_build.json')).read_text());assert sha(B/(P+'.nes'))==z['candidate_sha256']
 historical=json.loads((B/'samus_fixed_hud_handoff.json').read_text())
 assert all(sha(q['path'])==q['sha256']for q in historical['bindings'])
 root=(B/'smb-crossover-mmc5-expanded.nes');old=scoped_load(root);new=scoped_load(B/(P+'.nes'));prior=scoped_load(B/'samus_fixed_hud.nes')
 ordinary=R/'chr/mmc5/sprites_enemies.chr';ordinary_assets=[ordinary,R/'chr/characters/packed-mmc3.chr',R/'chr/characters/packed-mmc5.chr']
 before={str(p):sha(p)for p in ordinary_assets}
 pairs=recipe.source_pairs(R);native=ordinary.read_bytes();variant=recipe.make_variant(native,pairs)
 packed=(R/'chr/characters/packed-mmc5-expanded.chr').read_bytes();out=recipe.expanded_only(packed,native,variant,pairs)
 assert out==(B/(P+'_packed-mmc5-expanded.chr')).read_bytes()
 assert recipe.expanded_only(out,native,variant,pairs)==out
 assert variant[:3072+192]==native[:3072+192]and variant[3072+256:]==native[3072+256:]
 rejects=[]
 def reject(name,fn):
  try:fn()
  except AssertionError:rejects.append(name)
  else:raise AssertionError('Invalid overlay accepted:'+name)
 corrupt=bytearray(native);corrupt[3072+192]=1
 reject('ordinary_gap_nonzero',lambda:recipe.make_variant(bytes(corrupt),pairs))
 bad=bytearray(variant);bad[3072]^=1;reject('mouse_pair_changed',lambda:recipe.expanded_only(packed,native,bytes(bad),pairs))
 bad=bytearray(variant);bad[3072+192]^=1;reject('wrong_missile_pair',lambda:recipe.expanded_only(packed,native,bytes(bad),pairs))
 bad=bytearray(packed);bad[20*1024+192]=1;reject('unexpected_expanded_owner',lambda:recipe.expanded_only(bytes(bad),native,variant,pairs))
 # Execute the actual optional hook with virtual writes. No directory/tree or
 # ordinary asset is created. Only the expanded packed path may be a sink.
 target=R/'chr/characters/packed-mmc5-expanded.chr';vp=R/'chr/characters'/recipe.VARIANT
 real_read=Path.read_bytes;real_exists=Path.exists;calls=[]
 for enabled in [False,True]:
  mem={vp:variant,target:packed};writes=[]
  def exists(p):return enabled if p==vp else real_exists(p)
  def read(p):return mem[p]if p in mem else real_read(p)
  def write(p,data):
   assert p==target,'Expanded hook wrote a non-expanded path';writes.append(str(p));mem[p]=bytes(data);return len(data)
  with patch.object(Path,'exists',exists),patch.object(Path,'read_bytes',read),patch.object(Path,'write_bytes',write):
   value=recipe.apply_expanded_assets(R/'chr/characters')
  assert value==enabled and len(writes)==int(enabled)
  assert mem[target]==(out if enabled else packed)
  calls.append(dict(variant_present=enabled,return_value=value,write_paths=writes))
 # The private pack_chr proposal has exactly three additional source lines;
 # ordinary producers and their two outputs are otherwise text-exact.
 baseline=(R/'tools/reference/pack_chr.py').read_text();proposed=(B/(P+'_pack_chr.py')).read_text()
 hook="    # Optional expanded-only overlay; both ordinary outputs/assets stay exact.\n    from patch_samus_fixed_hud_v2 import apply_expanded_assets\n    apply_expanded_assets(folder)\n"
 assert proposed.count(hook)==1 and proposed.replace(hook,'')==baseline
 ast.parse(proposed)
 # Reuse the old finite tests only where actual linked instructions/tables
 # and RAM aliases are exact. Do not retag old native evidence to this ROM.
 reused={}
 for name in ['RemainingDraw','MetaspriteRenderLoop','SamusFixedMissileHud','SamusDrawShots','SamusFreezeRenderFinish','X5PublishChr','CrossoverGraphicsBank','IrqScrollSplit']:
  code=[]
  for b in [prior,new]:
   pos=location(b,name);length=(address(b,'X5SetPhysicalChr')-address(b,name))if name=='X5PublishChr'else int(b['syms'][name]['size'],0);code.append(b['raw'][pos:pos+length])
  assert code[0]==code[1],name;reused[name]=dict(bytes=len(code[0]),sha256=hashlib.sha256(code[0]).hexdigest())
 for name in ['R0','R1','R3','R4','R5','R6','R7','CurrentBank','CurrentBankC','AvDrawIndex','InvSelected','SsChrActive','SsChrPhysical','CurrentCHRBank']:
  assert address(prior,name)==address(new,name)
 outer=[]
 for char,item,mixed,freeze in [(2,2,False,0),(2,2,False,1),(2,2,True,0),(2,2,True,1),(2,1,False,0),(2,7,False,0),(3,2,False,0),(9,1,False,0)]:
  values=[]
  for b in [old,new]:
   q=setup(b,char,item,0,False,mixed);q.put(SmFreezeRenderState=freeze)
   if freeze:q.set('AvFrozen',180,0)
   cpu,_=q.invoke('SamusFreezeDrawAll');values.append(dict(cycles=cpu.processorCycles,AXYP_SP=[cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp],banks=q.m.banks[:],oam=list(q.m[512:768])))
  assert values[0]['AXYP_SP']==values[1]['AXYP_SP']and values[0]['banks']==values[1]['banks']
  if not(char==2 and item==2):assert values[0]['oam']==values[1]['oam']
  outer.append(dict(char=char,item=item,mixed=mixed,freeze=freeze,cycles=[v['cycles']for v in values],delta=values[1]['cycles']-values[0]['cycles']))
 # Fresh current linked IRQ replay at the same thirteen helper boundaries.
 q=setup(new);q.m.page(1,61);q.set('CurrentBank',189);image=list(q.m);banks=q.m.banks[:]
 def fresh():
  m=Memory(new);list.__setitem__(m,slice(None),image);m.banks=banks[:];return m
 def flat(m):return bytes(m[:0x1c0]+m[0x200:0x800]+m[0x6000:0x8000])
 def bus(m):return[w for i,w in enumerate(m.writes)if i not in m.irq_write_indices and not 256<=w[0]<512]
 old_controls=json.loads((B/'samus_fixed_hud_controls.json').read_text());keys=old_controls['actual_IRQ_instruction_boundaries']
 m=fresh();cpu,_=execute(new,m,'RemainingDraw');expected=(cpu.a,cpu.x,cpu.y,cpu.p&207,cpu.sp,flat(m),m.banks,bus(m))
 for pc,k in keys:
  m=fresh();cpu,_=execute(new,m,'RemainingDraw',inject=(pc,k));assert(cpu.a,cpu.x,cpu.y,cpu.p&207,cpu.sp,flat(m),m.banks,bus(m))==expected
 assert before=={str(p):sha(p)for p in ordinary_assets}
 # Additive normalized review diff, leaving the raw build receipt/patch intact.
 review=[]
 for name,s in z['source_overlay'].items():
  if name.endswith('.chr'):continue
  beforetext=(R/name).read_text().splitlines(True)if(R/name).exists()else[]
  aftertext=Path(s['path']).read_text().splitlines(True)
  # Sparse include aliases are build plumbing; the actual proposed entrypoint
  # uses canonical names and one new genuine include.
  if name=='src/entrypoint.s':
   text=''.join(aftertext)
   for leaf in ['remaining_weapons.s','samus_fixed_hud.s']:text=text.replace(P+'_'+leaf,leaf)
   text=text.replace('build/'+P+'_packed-mmc5-expanded.chr','chr/characters/packed-mmc5-expanded.chr');aftertext=text.splitlines(True)
  review+=difflib.unified_diff(beforetext,aftertext,fromfile='a/'+name,tofile='b/'+name)
 diff=B/(P+'_normalized.patch');assert not diff.exists();diff.write_text(''.join(review),newline='\n')
 proof=dict(passed=True,source_only=True,native_run=False,ROM_sha256=z['candidate_sha256'],original9d1_packet_unchanged=True,recipe_negative_controls=rejects,actual_conditional_hook_calls=calls,ordinary_assets_exact=before,ordinary_source_generation_exact=True,expanded_only_variant_bytes=4096,recipe_idempotent=True,reused_source_controls=dict(proof=str(B/'samus_fixed_hud_controls.json'),sha256=sha(B/'samus_fixed_hud_controls.json'),RemainingDraw_frame_scan_cases=80,SamusDrawShots_family_cases=10,window5_cases=6,scope='Reused source conclusions only, backed by the actual linked body hashes below; never native retagging.'),actual_linked_code_exact=reused,fresh_current_complete_outer_cases=outer,fresh_actual_IRQ_cases=len(keys),IRQ_scope=old_controls['IRQ_scope'],ordinary_byte_equivalence_plan='No packer main was run. Actual optional hook virtual writes only the expanded output and leaves all ordinary producers text-exact. For adoption ROOT should compile sparse candidate entrypoint with ENABLE_MMC5_EXPANDED=0 for MMC3/MMC5 using smb1base.cfg and compare d444cac8/f4ffd248; the guarded helper is excluded and ordinary packed files remain original. No ordinary binary build is claimed here.',limits='Current composition source-only. Prior9d1 native seven42pixel samples and2090/1716/2027counts keep their old hash. Native current4a epochs/cadence/crowding/highjump remain separate; foreignHUD+15 and nearfull positive costs remain disclosed.',bindings={str(p):sha(p)for p in [Path(__file__),R/'tools/reference/patch_samus_fixed_hud_v2.py',B/(P+'_build.json'),B/(P+'.nes'),B/(P+'.dbg'),B/'samus_fixed_hud_controls.json',B/'samus_fixed_hud_handoff.json',diff]})
 p=B/(P+'_controls.json');assert not p.exists();p.write_text(json.dumps(proof,indent=2)+'\n',newline='\n');print(json.dumps(dict(passed=True,proof_sha256=sha(p),cases=len(outer),IRQ=len(keys),normalized_patch_sha256=sha(diff))))
if __name__=='__main__':main()
