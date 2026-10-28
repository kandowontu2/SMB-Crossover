"""Add three enemy child spans to the existing current326 Bill replay profile.

No native launch, product writes, source/runtime/ROM copies or frame files.
"""
from pathlib import Path
from argparse import Namespace
import contextlib,csv,io,json,re,sys
import current_bill_passive_timing_prepare_v1 as timing
from current_bill_enemy_timing_prepare_v1 import decoded_direct_JSRs
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
import current_roster_compact_11_v1 as route
R=route.ROOT;B=R/'build';ROM=B/'zelda2_easy_glove.nes'
EXPECTED='32694243361bb1366f6fd64c054ea2451f86b2517fc020d9c2b5d66bbf07bfa0'
OLD='9ea11eab2fc5c373a3795b013f6ed9e0d5e9781891b2ae3bf40ad2556c27b85e'
ADDED=['EnemyGraphicsEngine','EnemyMovementSubs','ProcLoopCommand']
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')

def main():
 parent=B/'verification/bill-enemy-timing9ea-ready-v1';pr=json.loads((parent/'ready.json').read_text());old=json.loads((parent/'profile-config.json').read_text());result=json.loads((parent/'result.json').read_text())
 assert result['passed']and result['ROM_sha256']==OLD and result['frames']==6091
 assert route.sha(ROM)==EXPECTED and route.sha(B/'bill_early_cache.nes')==OLD
 inputs=parent/'inputs.csv';saved=list(csv.DictReader(inputs.open(newline='')));assert len(saved)==result['polls']==6090 and [int(r['poll'])for r in saved]==list(range(1,6091))
 observer=B/'bill_early_cache_timing_full.lua';observer_text=observer.read_text();assert route.sha(observer)==pr['bindings'][str(observer)]
 assert not re.search(r'emu\.(?:write\w*|setInput|setState|loadSavestate|reset|stop)\s*\(',observer_text)
 assert observer_text.count('emu.addMemoryCallback(')==6 and observer_text.count('emu.addEventCallback(')==1
 negative=B/'verification/bill-enemy-children326-ready-v1'
 out=B/'verification/bill-enemy-children326-ready-v2'
 if out.exists():
  # Continue only our unbound initial metadata preparation, after preserving
  # its exact format failure. Shared route.prepare is never overwritten or
  # called on a nonempty native/evidence folder.
  failure=json.loads((out/'preparation-mirror-order-negative.json').read_text())
  assert not(out/'prepare-controls.json').exists()and not(out/'launch.json').exists()and not(out/'result.json').exists()
  assert route.sha(out/'ready.json')==failure['generic_ready_sha256']and route.sha(out/'run.lua')==failure['generic_run_sha256']
 else:
  with contextlib.redirect_stdout(io.StringIO()):route.prepare(Namespace(identity='bill',mode='hard',rom=ROM,expected_sha256=EXPECTED,output=out,frames=8000,policy=R/'tools/playthroughs/roster_samus_contra.lua',replay=inputs))
 ready=json.loads((out/'ready.json').read_text());cfg=ready['config'];assert cfg['replay']==inputs.as_posix()and cfg['limit']==8000 and cfg['capture_bytes']==512*1024*1024
 b=scoped_load(ROM);baseline=scoped_load(B/'bill_early_cache.nes');raw=b['raw'];bank_proof={}
 for bank in[0,2,126]:
  a=raw[16+bank*8192:16+(bank+1)*8192];z=baseline['raw'][16+bank*8192:16+(bank+1)*8192];assert a==z
  bank_proof[str(bank)]=dict(all8192_bytes_equal=True,sha256=__import__('hashlib').sha256(a).hexdigest())
 def bound(name,symbol=None,banks=None):
  n=symbol or name;at=location(b,n);pc=address(b,n);owner=(at-16)//8192;owners=banks or[owner]
  for k in owners:assert list(raw[16+k*8192+(pc&8191):16+k*8192+(pc&8191)+3])==list(raw[at:at+3])
  return dict(name=name,symbol=n,pc=pc,banks=owners,bytes=list(raw[at:at+3]))
 profile=json.loads(json.dumps(old));profile.update(output=out.as_posix()+'/',ROM_sha256=EXPECTED)
 assert profile['first_frame']==3500 and profile['last_frame']==3560 and profile['row_cap']==200 and profile['byte_cap']==1048576
 entries=[bound(h['name'],h['symbol'],h['banks'])for h in old['functions']]+[bound(n)for n in ADDED]
 assert entries[:21]==old['functions'],'Current real entry metadata of original21 remains exact; only three new probes'
 assert [(h['pc'],h['banks'])for h in entries[-3:]]==[(0xbadf,[0]),(0xa4ba,[0]),(0xa5e6,[2])]
 assert len(entries)==24 and len({(h['pc'],tuple(h['banks']))for h in entries})==24
 # Fresh current compiled source closure, including stack-neutral tails and
 # real JumpEngine dispatch; never raw wildcard return-PC acceptance.
 callers,smc,closure=timing.source_call_closure(ROM,raw,entries,address(b,'JumpEngine'))
 direct=decoded_direct_JSRs(ROM,raw,entries);cross=[]
 for name,rets in direct.items():
  for ret,owners in rets.items():
   for owner in owners:
    if owner not in callers[name].get(ret,[]):callers[name].setdefault(ret,[]).append(owner);cross.append(dict(function=name,return_pc=int(ret),owner=owner))
 controls=0
 for h in entries:
  name=h['name'];assert '65535'not in callers[name]and '65535'not in smc[name]
  if not callers[name]:
   assert name in['RosterMovement','RosterWeapons','RemainingDraw']and old['source_callers'][name]=={}
   assert smc[name]==old['smc_targets'][name]=={str(h['pc']):True},'Inherited genuine SMC-only entry; no ROM caller or broad target allowance invented'
  for ret,owners in callers[name].items():
   for owner in owners:
    off=16+owner['bank']*8192+((int(ret)-3)&8191);assert list(raw[off:off+3])==owner['bytes']and owner['bytes'][0]==0x20
    accept=lambda k,code:any(q['bank']==k and q['bytes']==code for q in owners)
    assert accept(owner['bank'],owner['bytes'])and not accept(-1,owner['bytes'])and not accept(owner['bank'],[0x4c]+owner['bytes'][1:])
    bad=owner['bytes'][:];bad[1]^=1;assert not accept(owner['bank'],bad);controls+=1
  for bank in h['banks']:assert list(raw[16+bank*8192+(h['pc']&8191):16+bank*8192+(h['pc']&8191)+3])==h['bytes']
 returns={}
 for rets in callers.values():
  for ret,owners in rets.items():
   for owner in owners:
    if owner not in returns.get(ret,[]):returns.setdefault(ret,[]).append(owner)
 assert 0<len(returns)<2048
 profile.update(functions=entries,returns=returns,source_callers=callers,smc_targets=smc)
 # Original SP/depth checks and strict unknown/wrong-bank/JSR rejection are
 # literal observer code; all hooks/SMC/RAM/ISR copies are current metadata.
 _,_,_,_,hook=route.linked(ROM)
 for key,n,ck in[('NMI','NonMaskableInterrupt','nmi'),('IRQ','IrqScrollSplit','irq')]:
  actual_banks=cfg['hooks'][ck].get('banks',[cfg['hooks'][ck]['bank']]);banklist=old['interrupts'][key]['banks'];assert set(banklist)==set(actual_banks)
  entry=bound(n,n,banklist);tail=hook(n,tail=True);assert tail['bytes'][0]==0x40
  profile['interrupts'][key]=entry;profile['interrupts'][key+'_return']=dict(name=n+' preRTI',pc=tail['pc'],banks=banklist,bytes=[64])
  for k in banklist:assert raw[16+k*8192+(tail['pc']&8191)]==64
 assert profile['interrupts']==old['interrupts']and cfg['hooks']['dma_complete']==old['dma_complete']
 for n,v in old['ram'].items():assert address(b,n)==v
 profile['ram']={n:address(b,n)for n in old['ram']};profile['dma_complete']=cfg['hooks']['dma_complete']
 sy=b['syms']['FarcallJmpTarget_SMC'];segment=b['segs'][sy['seg']];start=int(segment['start'],0);size=int(segment['size'],0);assert segment['name']=='"SMCCODE"'and profile['smc_start']==start and profile['smc_end']==start+size-1
 prepared=(out/'run.lua').read_text();anchor='dofile('+route.lua(route.SCRIPT.as_posix())+')\n';insertion='BILL_PASSIVE_TIMING='+route.lua(profile)+'\n'+'dofile('+route.lua(observer.as_posix())+')\n';assert prepared.count(anchor)==1
 run=prepared.replace(anchor,insertion+anchor);assert run.replace(insertion,'',1)==prepared and not re.search(r'\\u[0-9a-fA-F]{4}',run);(out/'run.lua').write_text(run,newline='\n')
 put(out/'profile-config.json',profile);put(out/'command.json',ready['command'])
 prep=dict(passed=True,native_run=False,current_ROM_sha256=EXPECTED,baseline_actual_ROM_sha256=OLD,whole_relevant_banks_equal=bank_proof,new_functions=entries[-3:],old21_entry_and_ISR_metadata_exact=True,fresh_current_source_closure=closure,direct_cross_window_owners=cross,source_JSR_positive_wrongbank_wrongtarget_nonJSR_controls=controls,total_function_spans=24,return_PCs=len(returns),observer_body_unchanged_sha256=route.sha(observer),shared_route_body_unchanged_sha256=route.sha(route.SCRIPT),saved_input_sha256=route.sha(inputs),saved_polls=6090,
  limits='Actual old9ea profile remains historical. Fresh current326 source metadata only; native trace/input/PPU equality and hotspot attribution pending. SP/depth/bank/JSR/SMC/runtime checks unchanged. Normal61 timing rows are completion buckets; warmup/openMain/ISR nesting limits remain. No EnemyID/per-call shot state inference.',execution_scope='Same original8000 full1-1 to controlled1-2 saved-input replay; timing collection only3500..3560/61data rows. One compact512MiB container/2GB centralcap/64files; no native screenshot tree, no source/runtime/ROM copies.')
 put(out/'prepare-controls.json',prep)
 ready['passive_enemy_children_current326']=dict(ROM_sha256=EXPECTED,baseline_native_ROM_sha256=OLD,added_children=ADDED,total_spans=24,window=[3500,3560],expected_data_rows=61,CSV_max_rows=200,CSV_max_bytes=1048576,startup_static=True,observer_reused_literal=True,no_native_grant=True,no_emulated_writes=True,expected_result='Current actual route and hardware outcomes must be reviewed after ROOT launch; old9ea6091wall/5142updates is a reference, not an expected current result or FPS claim.',source_controls=str(out/'prepare-controls.json'),owned_new_file='tools/audit/current_bill_enemy_children326_prepare_v1.py')
 deps={Path(p)for p in ready['bindings']};deps.update({Path(__file__).resolve(),Path(timing.__file__).resolve(),R/'tools/audit/current_bill_enemy_timing_prepare_v1.py',observer,out/'profile-config.json',out/'prepare-controls.json',out/'command.json',parent/'ready.json',parent/'profile-config.json',parent/'result.json',parent/'bill-timing-summary.json',B/'bill_early_cache.nes',(B/'bill_early_cache.nes').with_suffix('.dbg'),Path('C:/Mesen2/Mesen.exe'),Path('C:/Mesen2/MesenCore.dll'),Path('C:/Mesen2/settings.json')})
 if(negative/'preparation-v1-negative.json').exists():deps.update(negative/n for n in['preparation-v1-negative.json','preparation-v1-negative-ready.json','preparation-v1-negative-run.lua','preparation-v2-fresh-directory-negative.json'])
 if(out/'preparation-mirror-order-negative.json').exists():deps.add(out/'preparation-mirror-order-negative.json')
 for module in list(sys.modules.values()):
  p=getattr(module,'__file__',None)
  if p and('py65'in str(p)or str(R/'tools/audit')in str(p))and Path(p).is_file():deps.add(Path(p))
 ready['bindings']={str(p):route.sha(p)for p in sorted(deps)};put(out/'ready.json',ready);assert all(route.sha(Path(p))==h for p,h in ready['bindings'].items())
 print(json.dumps(dict(prepared=True,native_run=False,ready=str(out/'ready.json'),ready_sha256=route.sha(out/'ready.json'),bindings=len(deps),positive_negative_controls=controls,source_closure_functions=len(closure['functions']),return_PCs=len(returns),command=ready['command']),indent=2),flush=True)
if __name__=='__main__':main()
