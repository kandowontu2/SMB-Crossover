"""Sparse lifecycle successor to frozen f1ed39; no shared/native mutation."""
from pathlib import Path
import difflib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import rogue_dawn_map_v1 as ref
from prepare_cv3_dmc_mirror import prepare
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from check_tmnt_audio_fallback_oc import qualified
P=R/'build/rogue-dawn-host-body-v1';O=R/'build/rogue-dawn-host-lifecycle-v1'
EXPECTED='f1ed39c8dc5d801567d1f6a5b86e581ed61da19d67f04716daf3c7429391745d'
sha=lambda p:ref.digest(Path(p).read_bytes())

def once(s,a,b):
 assert s.count(a)==1,(a,s.count(a))
 return s.replace(a,b)
def inproc(s,name,old,new):
 start=s.index('.proc '+name+'\n');end=s.index('.endproc',start)
 return s[:start]+once(s[start:end],old,new)+s[end:]

def main():
 assert sha(P/'candidate.nes')==EXPECTED
 assert not(O/'build.json').exists(),'Frozen successor'
 parent=json.loads((P/'handoff.json').read_text())
 for x in parent['bindings']:assert ref.binding(x['path'])==x,x['path']
 art=R/'build/rogue-dawn-death-art-v1/handoff.json';assets=json.loads(art.read_text());assert assets['passed']
 for x in assets['outputs']+assets['bindings']:assert ref.binding(x['path'])==x,x['path']
 O.mkdir(exist_ok=True)
 files=['entrypoint.s','main.c','private.cfg','player.s','luigi_native.s','megaman_weapons.s','object.s','new_roster_dispatch.s','zelda2_link_platform.s','legacy-player-prg.s','control-include.s','services-include.s','art-include.inc','bridge-include.s','movement-flush.s']
 for n in files:(O/n).write_bytes((P/n).read_bytes())
 # All unchanged root source inputs are checked above against the actual
 # parent compiler closure. Only these new sparse caller leaves are staged.
 originals={}
 for n in ['game.s','guest_injury.s','guest_body_contact.s','collision.s','megaman_death.s']:
  text=(R/'src'/n).read_text();originals[n]=text;(O/n).write_text(text,newline='\n');files.append(n)
 changes={}
 def edit(n,fn):
  p=O/n;old=p.read_text();new=fn(old);assert old!=new,n
  p.write_text(new,newline='\n');changes[n]=(old,new)
 edit('player.s',lambda s:once(once(once(s,'farcall RdTxMovement','farcall RdLifeMovement'),'farcall RdBodyGraphics','farcall RdLifeGraphics'),'    farcall SamusDeathUpdate\n','.if ::ENABLE_MMC5_EXPANDED\n    farcall RdLifeDeathTick\n.else\n    farcall SamusDeathUpdate\n.endif\n'))
 edit('megaman_weapons.s',lambda s:once(s,'farcall RdBodyDynamicPrg','farcall RdLifeDynamicPrg'))
 edit('services-include.s',lambda s:once(s,'Case 3,RdHsDraw','Case 3,RdLifeDraw'))
 edit('game.s',lambda s:once(once(s,'farcall Z2ResetAreaGate','farcall RdLifeArea'),'farcall X5BounceUiDispatch','farcall RdLifeUi'))
 def injury(s):
  s=inproc(s,'GuestPlayerVisible','farcall RlVisibleDispatch','farcall RdLifeVisible')
  s=inproc(s,'GuestGameRoutinesBridge','farcall CheatsGameRoutinesGate','farcall RdLifeCheatRoutines')
  return inproc(s,'GuestGameRoutinesBridge','Run:\n  farcall GameRoutines,jmp\n  .byte $ea','Run:\n  farcall RdLifeGameRoutines,jmp\n  .byte $ea')
 edit('guest_injury.s',injury)
 def body(s):
  s=inproc(s,'GuestInjuryStatus','farcall RlInjuryStatusDispatch','farcall RdLifeStatus')
  return inproc(s,'GuestBodyContactBridge','farcall LmBodyGate','farcall RdLifeBody')
 edit('guest_body_contact.s',body)
 edit('collision.s',lambda s:once(s,'farcall RlInjuryDispatch','farcall RdLifeInjury'))
 edit('megaman_death.s',lambda s:once(s,'farcall Cv3FxDeathDispatch','farcall RdLifeDeathStart'))
 edit('new_roster_dispatch.s',lambda s:inproc(s,'NrFreshGameInit','farcall CmHostFresh','farcall RdLifeFresh'))
 edit('entrypoint.s',lambda s:once(once(s,'.include "rogue_dawn_host_body.s"','.include "rogue_dawn_host_body.s"\n.include "rogue_dawn_host_lifecycle.s"\n.include "rogue_dawn_death_art.inc"'),'.incbin "chr/characters/rogue-dawn.chr"','.incbin "chr/characters/rogue-dawn.chr",0,9*1024\n.incbin "chr/characters/rogue-dawn-death.chr"\n.incbin "chr/characters/rogue-dawn.chr",10*1024,6*1024'))
 d=json.loads((P/'build.json').read_text());cmd=[s.replace(str(P),str(O))for s in d['commands'][0]]
 out=O/'candidate.nes'
 if '--qualify-existing'not in sys.argv:
  z=subprocess.run(cmd,cwd=R,capture_output=True,text=True);(O/'build.log').write_text(z.stdout+z.stderr);assert z.returncode==0,(z.stdout+z.stderr)[-4000:]
  prepare(R,out)
 else:assert out.exists()
 a,b=scoped_load(P/'candidate.nes'),scoped_load(out)
 assert address(b,'RdLifeStart')==0xb803 and address(b,'RdLifeEnd')<=0xbf00
 assert address(b,'RdDeathRecordA')==0xbf00 and address(b,'RdDeathRecordLeftA')==0xbf19
 oldsym,newsym=qualified(P/'candidate.nes'),qualified(out)
 moved={str(k):[v,newsym.get(k)]for k,v in oldsym.items()if newsym.get(k)!=v and 'LOCAL-MACRO_SYMBOL-'not in str(k)}
 assert all('_FARCALL_COUNT'in k for k in moved),moved
 # Exact old farcall operand changes, derived from genuine linked target and
 # common SMC bytes. No whole-bank/shared-span waiver.
 raw=bytes(a['raw']);spans=[]
 def farpre(target,jmp=False):
  return bytes([0x8d])+(address(a,'SafecallA_SMC')+1).to_bytes(2,'little')+bytes([0xa9,address(a,target)&255,0x8d])+(address(a,'FarcallJmpTarget_SMC')+1).to_bytes(2,'little')+bytes([0xa9,address(a,target)>>8,0x8d])+(address(a,'FarcallJmpTarget_SMC')+2).to_bytes(2,'little')+bytes([0xa9,128|(location(a,target)-16)//8192,0x4c if jmp else 0x20])+address(a,'FarCallCommon').to_bytes(2,'little')
 for owner,target,jmp in [('PlayerMovementSubs','RdTxMovement',False),('PlayerGfxHandler','RdBodyGraphics',False),('PlayerDeath','SamusDeathUpdate',False),('MmDynamicPlayerPrgOwner','RdBodyDynamicPrg',False),('InitializeArea','Z2ResetAreaGate',False),('GameLoop','X5BounceUiDispatch',False),('GuestPlayerVisible','RlVisibleDispatch',True),('GuestInjuryStatus','RlInjuryStatusDispatch',True),('GuestBodyContactBridge','LmBodyGate',False),('ForceInjury','RlInjuryDispatch',False),('UnionDeathStartCore','Cv3FxDeathDispatch',False),('NrFreshGameInit','CmHostFresh',True),('GuestGameRoutinesBridge','CheatsGameRoutinesGate',True),('GuestGameRoutinesBridge','GameRoutines',True)]:
  at=raw.find(farpre(target,jmp),location(a,owner),location(a,owner)+400);assert at>=0,(owner,target)
  spans.append((at,at+18,owner+'->'+target))
 for x,y,name in list(spans):
  if (x-16)//8192==127:
   mx,my=x-2*8192,y-2*8192
   assert raw[mx:my]==raw[x:y],('actual original E125/E127 hook alias',name)
   spans.append((mx,my,name+' actualE125 copy'))
 seq=bytes([0x4c])+address(a,'RdHsDraw').to_bytes(2,'little');at=raw.find(seq,location(a,'RdHsFrozenDispatch'),location(a,'RdHsFrozenDispatch')+400);assert at>=0
 spans.append((at,at+3,'Actual sourceDraw callback vector'));vector_at=at
 diff=[i for i,(x,y)in enumerate(zip(a['raw'],b['raw']))if x!=y]
 for i in diff:
  if any(x<=i<y for x,y,_ in spans):continue
  bank=(i-16)//8192;off=(i-16)%8192
  if bank<128:assert bank==95 and 0x1803<=off<0x2000 and a['raw'][i]==255,(bank,hex(off),a['raw'][i])
  else:assert 16+1048576+689*1024<=i<16+1048576+690*1024 and a['raw'][i]==0,i
 literal=[]
 for bank,pc,n in[(124,0xb000,4090),(124,0xae00,508),(94,0xd300,3150),(94,0xdf50,175)]:
  at=16+bank*8192+(pc&8191);assert a['raw'][at:at+n]==b['raw'][at:at+n];literal.append(dict(bank=bank,start=hex(pc),bytes=n,sha256=ref.digest(b['raw'][at:at+n])))
 # Entire A95oldprefix is exact EXCEPT the single3B declared source vector.
 at0=16+95*8192+0x600;at1=16+95*8192+0x1803
 for i in range(at0,at1):assert a['raw'][i]==b['raw'][i]or vector_at<=i<vector_at+3,i
 patch=O/'source.patch';patch.write_text(''.join(''.join(difflib.unified_diff(x.splitlines(True),y.splitlines(True),fromfile='f1ed39/'+n,tofile='private/'+n))for n,(x,y)in changes.items()),newline='\n')
 dep=O/'assembler-full.dep';words=dep.read_text().split(':\t',1)[1].split('\n\n',1)[0].replace('\\\n',' ').strip();inputs=[]
 for w in re.split(r'(?<!\\)\s+',words):
  if not w:continue
  p=Path(w.replace('\\ ',' '));p=(p if p.is_absolute()else R/p).resolve();assert p.is_file(),str(p)
  if p not in inputs:inputs.append(p)
 assert len(inputs)>490
 extras=[Path(__file__),R/'src/rogue_dawn_host_lifecycle.s',P/'handoff.json',art,R/'src/rogue_dawn_death_art.inc',R/'chr/characters/rogue-dawn-death.chr',P/'candidate.nes',P/'candidate.dbg',P/'candidate.lbl',out,out.with_suffix('.dbg'),out.with_suffix('.lbl'),out.with_suffix('.map'),O/'private.cfg',O/'main.c',patch,dep,R/'build_options.ini',R/'tools/prepare_cv3_dmc_mirror.py',R/'tools/Windows/cc65/bin/cl65.exe',R/'tools/Windows/cc65/bin/ca65.exe',R/'tools/Windows/cc65/bin/ld65.exe']
 proof=dict(passed=True,source_only=True,native_run=False,playable_admission=False,ROM_sha256=sha(out),parent_sha256=EXPECTED,life_start=hex(address(b,'RdLifeStart')),life_end=hex(address(b,'RdLifeEnd')),life_bytes=address(b,'RdLifeEnd')-address(b,'RdLifeStart'),life_free_to_descriptor_tail=0xbf00-address(b,'RdLifeEnd'),descriptor_start='BF00',descriptor_end=hex(address(b,'RdDeathRecordEnd')),old_symbols_moved=moved,literal_frozen_spans=literal,old_hook_spans=[dict(start=x,end=y,name=n,parent_hex=raw[x:y].hex(),candidate_hex=bytes(b['raw'][x:y]).hex())for x,y,n in spans],changed_bytes=len(diff),actual_ASM_dependencies=len(inputs),commands=[cmd],bindings=[ref.binding(p)for p in dict.fromkeys(inputs+extras)],future_router_union='Frozen helperAD9B remains on actualf1ed39. B compactor independently reclaimsADA4..ADCD42B for future relocation; neither original is retagged.',open=['constructor and typed pickup/art ownership','weapon actor/effect consumers','hazard and boss contact mappings','authentic audio','menu/native admission'])
 (O/'build.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({k:proof[k]for k in ['ROM_sha256','life_bytes','life_end','life_free_to_descriptor_tail','actual_ASM_dependencies']}))
if __name__=='__main__':main()
