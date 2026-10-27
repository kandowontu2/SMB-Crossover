"""Compose frozen877d Bass leaves onto fb2a, using flat files only.

No original generator, frozen-file overwrite, tree clone, native or primary
mutation. The complete build and targeted controls share one compact receipt.
"""
from pathlib import Path
import configparser,difflib,hashlib,itertools,json,re,subprocess,sys,traceback,zipfile
from check_tmnt_audio_fallback_oc import qualified
from check_tmnt_render_oa import address
from link_pit_rygar_sophia_audit_cpu import scoped_load
from bass_corner_source_cpu_v1 import setup,run,fixed,block,app,reg

R=Path(__file__).resolve().parents[2];B=R/'build'
BASE=B/'smb-crossover-mmc5-expanded.nes'
EXPECTED='fb2a608e4670788c0a170d6a17e7802b226e9e6933cd44103cb1b9212db54eed'
DONOR='877d0b5e33810568af2dc6410b4f081cc3e5badc2ee9128e283c859ba08395c9'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,q:Path(p).write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')

class DebugText:
 def __init__(self,text):self.text=text
 def with_suffix(self,_):return self
 def exists(self):return True
 def read_text(self):return self.text

def main():
 proof=dict(passed=False,native_run=False,installed=False,new_directories=0,source_tree_copies=0,
  baseline_ROM=EXPECTED,frozen_donor_ROM=DONOR,counts={})
 try:
  assert sha(BASE)==EXPECTED
  frozen=json.loads((B/'bass_corner_final_source.json').read_text())
  before_bound={f:h for f,h in frozen['bindings'].items()if Path(f).exists()}
  for f,h in before_bound.items():assert sha(f)==h,('Frozen input changed',f)
  assert sha(B/'bass_corner_private.nes')==DONOR
  current=scoped_load(BASE);raw=current['raw']
  leaves={'src/kirby_legacy.s':B/'bass_corner_kirby_legacy.s',
   'src/tmnt_probe_gates.s':B/'bass_corner_tmnt_probe_gates.s',
   'src/zelda2_link_platform.s':B/'bass_corner_zelda2_link_platform.s'}
  primary={rel:sha(R/rel)for rel in[*leaves,'src/entrypoint.s','smb1base-mmc5-expanded.cfg','src/kirby.s','src/tmnt.s','src/main.c','build_options.ini']}
  for rel in leaves:assert primary[rel]==frozen['primary_changed_file_base_hashes'][rel],('Current leaf changed; no blind overwrite',rel)
  for parent,child,flat_parent,flat_child in[
   ('src/kirby.s','kirby_legacy.s','bass_corner_kirby.s','bass_corner_kirby_legacy.s'),
   ('src/tmnt.s','tmnt_probe_gates.s','bass_corner_tmnt.s','bass_corner_tmnt_probe_gates.s')]:
   assert(R/parent).read_text()==(B/flat_parent).read_text().replace('"'+flat_child+'"','"'+child+'"'),parent
  working=json.loads((B/'bass_corner_working_result.json').read_text())
  pool_checks=[]
  for q in working['declared_pools']:
   at=16+q['bank']*8192+(q['start']&8191);end=at+q['maximum_bytes']
   assert raw[at:end]==b'\xff'*q['maximum_bytes'],('Current pool not FF',q)
   for seg in current['segs'].values():
    if 'ooffs'in seg:
     pos,n=int(seg['ooffs'],0),int(seg['size'],0)
     assert not(n and pos<end and at<pos+n),('Declared owner overlaps',q,seg)
   pool_checks.append(q)
  # The new declarations are appended after ALL current segments. They never
  # advance a current segment's start or replace menu/music declarations.
  cfg=(R/'smb1base-mmc5-expanded.cfg').read_text()
  additions=['    '+line+'\n'for line in re.findall(r'\bBASS_(?:PROFILE|HEAD_GATE|CEILING|POST):[^;]+;',(B/'bass_corner.cfg').read_text())]
  assert len(additions)==4 and not any(line.strip().split(':')[0]+':'in cfg for line in additions)
  at=cfg.index('\n}\nSYMBOLS');merged_cfg=cfg[:at]+'\n'+''.join(additions)+cfg[at:]
  entry=(R/'src/entrypoint.s').read_text();include='\n.if ::ENABLE_MMC5_EXPANDED\n.include "bass_corner_profile.inc"\n.endif\n'
  assert 'bass_corner_profile.inc'not in entry
  merged_entry=entry+include
  asm_text=merged_entry
  for old,new in [('kirby.s','bass_corner_kirby.s'),('tmnt.s','bass_corner_tmnt.s'),('zelda2_link_platform.s','bass_corner_zelda2_link_platform.s')]:
   token='.include "'+old+'"';assert asm_text.count(token)==1
   asm_text=asm_text.replace(token,'.include "'+new+'"')
  conf=B/'bass_corner_current.cfg';conf.write_text(merged_cfg)
  asm=B/'bass_corner_current_entrypoint.s';asm.write_text(asm_text)
  mainc=B/'bass_corner_current_main.c';mainc.write_bytes((R/'src/main.c').read_bytes())
  output=B/'bass_corner_current.nes'
  # Reuse only the exact frozen compiler flags, with new flat output names.
  cmd=working['command'][:]
  names={'bass_corner.cfg':conf.name,'bass_corner_private.':output.stem+'.',
   'bass_corner_main.c':mainc.name,'bass_corner_entrypoint.s':asm.name}
  for a,z in names.items():cmd=[s.replace(a,z)for s in cmd]
  # Current authoritative build settings, not stale donor-only definitions.
  options=configparser.ConfigParser();options.optionxform=str;options.read(R/'build_options.ini')
  defs={k:v for section in options.values()for k,v in section.items()}
  defs.update(MAPPER_MMC3='0',MAPPER_MMC5='1',ENABLE_CROSSOVER='1',ENABLE_MMC5_EXPANDED='1')
  clean=[];i=0
  while i<len(cmd):
   if cmd[i]in['--asm-define','-D']:i+=2;continue
   clean.append(cmd[i]);i+=1
  inputs=clean[-2:];cmd=clean[:-2]
  for k,v in defs.items():cmd+=['--asm-define',k+'='+v,'-D',k+'='+v]
  cmd+=inputs
  p=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
  (B/'bass_corner_current_build.log').write_text(p.stdout+p.stderr)
  proof['build_command']=cmd;proof['build_exit']=p.returncode
  assert p.returncode==0,p.stderr
  sys.path.insert(0,str(R/'tools'))
  from prepare_cv3_dmc_mirror import prepare
  prepare(R,output)
  new=scoped_load(output);after=new['raw'];proof['candidate_ROM']=sha(output)
  # Read the one bounded old-baseline ZIP in memory; never extract a tree.
  with zipfile.ZipFile(B/'stable-3b112-baseline.zip')as z:
   ns=[n for n in z.namelist()if n.endswith('.nes')];ds=[n for n in z.namelist()if n.endswith('.dbg')]
   assert len(ns)==len(ds)==1
   old_raw=z.read(ns[0]);old_debug=z.read(ds[0]).decode()
  assert hashlib.sha256(old_raw).hexdigest()==frozen['baseline_ROM']
  donor=(B/'bass_corner_private.nes').read_bytes()
  delta=[i for i,(a,z)in enumerate(zip(old_raw,donor))if a!=z]
  assert len(old_raw)==len(donor)==len(raw)==len(after)
  expected=bytearray(raw)
  for i in delta:
   assert raw[i]==old_raw[i],('Current changed an actual Bass patch byte',i,raw[i],old_raw[i])
   expected[i]=donor[i]
  assert after==expected,'Fresh link is not the exact frozen Bass/current union'
  banks={i:sum(a!=z for a,z in zip(raw[16+i*8192:16+(i+1)*8192],after[16+i*8192:16+(i+1)*8192]))for i in range(128)}
  banks={i:n for i,n in banks.items()if n};assert banks=={int(k):v for k,v in frozen['actual_changed_banks'].items()}
  proof['changed_banks']=banks;proof['changed_bytes']=len(delta)
  proof['exact_current_plus_frozen_donor_byte_union']=True
  proof['CHR_header_all_other_PRG_exact']=raw[:16]==after[:16]and raw[16+128*8192:]==after[16+128*8192:]
  oq,nq=qualified(BASE),qualified(output)
  moved={'::'.join(n):[v,nq.get(n)]for n,v in oq.items()if nq.get(n)!=v}
  assert set(moved)==set(frozen['genuine_private_symbol_changes']),moved
  proof['current_qualified_symbol_exceptions']=moved;proof['unchanged_current_qualified_symbols']=len(oq)-len(moved)
  oldq=qualified(DebugText(old_debug))
  hooks=['PlayerBGCollision','PlayerCtrlRoutine','MegaMan202AfterBG','BillBGHeadConsumer','BlockBufferColli_Head',
   'SamusAfterBGCollisionBridge','SamusStopAtWallBanked','KbLegacyExpandedCollisionAdder',
   'KbLegacyExpandedCollisionBox','TnFastHeadGate','Z2PostBGBodyBridge','RosterOamReady']
  proof['actual_current_hook_addresses']={n:dict(old3b=oldq.get((n,)),current=oq.get((n,)),composed=nq.get((n,)))for n in hooks}
  # Current-parent controls, not inherited donor results.
  for b in[current,new]:
   q=setup(b,Player_X_Position=89,Player_PageLoc=1)
   fixed(q,'MmXFraction',16384,2);fixed(q,'MmYFraction',8187,2);fixed(q,'MmVX',90112,3);fixed(q,'MmVY',-226647,3)
   cell=block(q,352,80,196);run(q,'PlayerBGCollision')
   if b is current:
    assert q.get('Player_Y_Position')==88 and q.get('SmCeilingHit')==0
   else:
    assert q.get('SmCeilingHit')==2 and q.get('SmTempY')==91
    run(q,'SamusAfterBGCollisionBridge')
    assert q.get('Player_Y_Position')==91 and q.get('MmYFraction')+256*q.get('MmYFraction',1)==0x8050
    assert[q.get('MmVY',i)for i in range(3)]==[0x55,0xd5,0]and q.get('Player_Y_Speed')==0
  proof['first_contact_pipeline']=dict(reconstructed_source_scene=True,current_misses=True,candidate_separates=True,cell=cell,target_anchor_Q16=91*65536+0x8050,exported_velocity_Q16=0xd555)
  n=0
  for state,face,mode,status in itertools.product([0,1,2],[1,2],[0,1],range(3)):
   q=setup(new,Player_State=state,PlayerFacingDir=face,CrossoverBehaviorVersion=mode,PlayerStatus=status)
   c,_,_=run(q,'MegaManCollisionBox');q.set('Player_BoundBoxCtrl',c.y)
   assert c.y==(12 if state==0 else 13)
   c,_,_=run(q,'PlayerBGCollision',stop='BillBGHeadConsumer');assert c.y==(30 if state==0 else 37);n+=1
  proof['counts']['actual_body_to_BG_prefixes']=n
  n=0;cost=[]
  for char,variant,mode in itertools.product(range(20),[0,1],[0,1]):
   if char==9 and variant==0:continue
   qs=[setup(b,char,RlVariant=variant,CrossoverBehaviorVersion=mode)for b in[current,new]]
   cs=[run(q,'PlayerBGCollision',flags=0xef)[0]for q in qs]
   assert reg(cs[0])==reg(cs[1])and app(qs[0])==app(qs[1]),('foreign BG',char,variant,mode)
   cost.append(cs[1].processorCycles-cs[0].processorCycles);n+=1
  proof['counts']['foreign_full_empty_BG']=n;proof['foreign_BG_cycle_delta']=[min(cost),max(cost)]
  n=0
  for char,face,x,page,flags in itertools.product([1,2,3,4,7,9,10,11],[1,2],[1,94,250],[0,1],[0x20,0xef]):
   qs=[setup(b,char,PlayerFacingDir=face,Player_X_Position=x,Player_PageLoc=page,R0=face,Player_X_Speed=22 if face==1 else 234)for b in[current,new]]
   for q in qs:fixed(q,'MmVX',65536 if face==1 else -65536,3)
   cs=[run(q,'SamusStopAtWallBanked',a=char,flags=flags)[0]for q in qs]
   assert reg(cs[0])==reg(cs[1])and app(qs[0])==app(qs[1]);n+=1
  proof['counts']['unchanged_valid_wall_calls']=n
  changes={**{rel:p.read_text()for rel,p in leaves.items()},'src/bass_corner_profile.inc':(B/'bass_corner_profile.inc').read_text(),
   'src/entrypoint.s':merged_entry,'smb1base-mmc5-expanded.cfg':merged_cfg}
  patch=[]
  for rel,text in changes.items():
   before=(R/rel).read_text().splitlines(True)if(R/rel).exists()else[]
   patch+=difflib.unified_diff(before,text.splitlines(True),fromfile='current-fb2a/'+rel,tofile='private/'+rel)
  (B/'bass_corner_current_source.patch').write_text(''.join(patch))
  assert primary=={rel:sha(R/rel)for rel in primary}and sha(BASE)==EXPECTED
  for f,h in before_bound.items():assert sha(f)==h,('Frozen input overwritten',f)
  proof.update(passed=True,verified_FF_unowned_pools=pool_checks,current_primary_source_hashes=primary,
   final_source_leaves={rel:dict(path=str(path),sha256=sha(path))for rel,path in leaves.items()},
   new_helper=dict(path=str(B/'bass_corner_profile.inc'),sha256=sha(B/'bass_corner_profile.inc')),
   current_cfg_overlay=dict(path=str(conf),sha256=sha(conf)),current_entry_overlay=dict(path=str(asm),sha256=sha(asm)),
   current_source_patch=dict(path=str(B/'bass_corner_current_source.patch'),sha256=sha(B/'bass_corner_current_source.patch')),
   no_original_generator_executed=True,all_frozen_donor_bindings_unchanged=True,
   install_after_native_acceptance='Copy the three named src leaves and new helper; apply ONLY the four BASS segment additions to current cfg and the guarded helper include to current entrypoint. Build-time flat include substitutions must NOT be copied into production entrypoint. Preserve menu/music source and native acceptance remains ROOT-owned.',
   limits='Targeted fresh source/CPU composition only. Original source-safe/cost/diagonal/hurt/slide/HUD-cutoff limits persist; no native/cadence acceptance. Original877d full qualification is referenced without retagging it as current.',
   frozen_donor_receipt=dict(path=str(B/'bass_corner_final_source.json'),sha256=sha(B/'bass_corner_final_source.json')))
 except BaseException as ex:
  proof['error']=repr(ex);proof['traceback']=traceback.format_exc();raise
 finally:
  proof['tool_sha256']=sha(__file__);put(B/'bass_corner_current_result.json',proof)
  print(json.dumps({k:v for k,v in proof.items()if k in['passed','error','candidate_ROM','changed_banks','changed_bytes','counts','foreign_BG_cycle_delta']},indent=2))
if __name__=='__main__':main()
