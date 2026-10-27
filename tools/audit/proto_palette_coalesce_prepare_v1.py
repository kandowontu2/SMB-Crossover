"""Prepare two ROOT-owned tests only: exact failed polls, then fresh fullroute.

No emulator launch, state/controller mutation, copied ROM/runtime/source tree or
tail input synthesis. All actual shared/body/VRAM guards remain unchanged.
"""
from pathlib import Path
import argparse,copy,csv,json,sys
from proto_palette_coalesce_candidate_v1 import R,B,SHA,sha,put
from proto_palette_coalesce_controls_v1 import NEW
from proto_startup_vram_timing_prepare_v2 import main as startup_prepare
from current_roster_compact_11_v1 import lua
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve()
 assert not out.exists();rom=B/'proto_palette_coalesce.nes';assert sha(rom)==NEW
 controls=B/'proto_palette_coalesce_controls.json';assert json.loads(controls.read_text())['passed']
 old=B/'verification/mm-body-proto-current-hard-v1';previous=json.loads((old/'ready.json').read_text());result=json.loads((old/'result.json').read_text());inputs=old/'inputs.csv'
 assert previous['ROM_sha256']==result['ROM_sha256']==SHA and result['passed']is False and result['frames']==1940 and result['polls']==1939
 assert result['reason']=='Active render enable precedes pre-render vertical reload'
 rows=list(csv.DictReader(inputs.open(newline='')));assert len(rows)==1939 and all(int(v['poll'])==i+1 and int(v['frame'])==i+1 for i,v in enumerate(rows))
 b=scoped_load(rom);original_body=previous['passive_body_observer']['metadata_fresh_from_actual_DBG'];body=copy.deepcopy(original_body);body['ROM_sha256']=NEW
 # Bind real current source addresses/banks/bytes, never fake hook aliases.
 for k,h in body['hooks'].items():
  name=h['name'];delta=0
  if k=='dma_complete':name='PostDmaMaskEnable';delta=3;assert b['raw'][location(b,name):location(b,name)+6]==bytes([0xad,address(b,'Mirror_PPUMASK')&255,address(b,'Mirror_PPUMASK')>>8,0x8d,1,0x20])
  pc=address(b,name)+delta;at=location(b,name)+delta;bank=(at-16)//8192;bs=list(b['raw'][at:at+len(h['bytes'])])
  assert(pc,bank,bs)==(h['pc'],h['bank'],h['bytes']),('Preserved genuine hook',k)
 for name,v in body['ram'].items():assert address(b,name)==v
 body_module=R/'tools/audit/mm_proto_body_reserve_passive_v1.lua';module=R/'tools/audit/proto_startup_vram_timing_v2.lua';harness=R/'tools/audit/current_roster_compact_11_v1.lua'
 assert sha(body_module)==previous['passive_body_observer']['module_sha256']
 for f in[body_module,module]:
  text=f.read_text();assert 'emu.write'not in text and'setInput'not in text and'removeMemoryCallback'not in text
 out.mkdir(parents=True);prepared=[]
 for kind in['diagnostic','fullroute']:
  d=out/kind;saved=sys.argv[:];sys.argv=[str(Path(__file__)),'--rom',str(rom),'--expected-sha256',NEW,'--output',str(d)]
  try:startup_prepare()
  finally:sys.argv=saved
  ready=d/'ready.json';z=json.loads(ready.read_text());cfg=z['config'];cfg['limit']=2050 if kind=='diagnostic'else 8000
  cfg['replay']=inputs.as_posix()if kind=='diagnostic'else None
  diagnostic=json.loads((d/'startup-config.json').read_text());diagnostic['cutoff_frame']=2050;put(d/'startup-config.json',diagnostic)
  run=d/'run.lua'
  startup='PROTO_STARTUP_VRAM_TIMING='+lua(diagnostic)+'\nlocal previousClose=ROSTER_CONFIG.bass_close\nlocal startupClose=dofile('+lua(module.as_posix())+')\nROSTER_CONFIG.bass_close=function()local q=previousClose and previousClose()or{};q.startup_vram=startupClose();return q end\n'
  run.write_text('ROSTER_CONFIG='+lua(cfg)+'\nfor name,value in pairs(ROSTER_CONFIG.extra_ram)do assert(L[name]==nil or L[name]==value,"RAM alias conflict: "..name);L[name]=value end\nMM_BODY_OBSERVATION_CONFIG='+lua(body)+'\nMM_BODY_OBSERVATION_CONFIG.output=ROSTER_CONFIG.prefix.."body-epochs.csv"\ndofile('+lua(body_module.as_posix())+')\n'+startup+'dofile('+lua(harness.as_posix())+')\n',newline='\n')
  z['config']=cfg;z['max_total_frames']=cfg['limit'];z['PREPARED_DO_NOT_RUN']=True
  z['expected_outcome']=('Original strict1940 render deadline must pass; exhausted original1939poll input must stop. Diagnostic only: no invented input tail and no fullroute PASS expected.'if kind=='diagnostic'else'Fresh original qualified adaptive ProtoHard controller,8000frame bound, full1-1 clear→controlled1-2, zero deaths, unchanged strict render/256DMA/E3/CHR/IRQ/bank/5SMC/SP/PPU guards. Independent route evidence, not old3e7/2082 retag.')
  z['startup_probe'].update(scope='Read-only source queue/copy/CHR/DMA timing first2050PPU;30000CSV rowcap; actual helper/controller/strict hardware guard bodies unchanged.',maximum_rows=30000)
  z['passive_body_observer']=dict(metadata_fresh_from_actual_DBG=body,module_sha256=sha(body_module),only_source_metadata_ROM_hash_changed=True,all_hook_bytes_actual_and_unchanged=True)
  cost=json.loads(controls.read_text())['actual_observed_packet']
  z['private_candidate_source_scope']=dict(parent=SHA,candidate=NEW,controls=str(controls),controls_sha256=sha(controls),source_CPU_only=True,foreground_three_calls_delta=cost['total_foreground_delta'],recorded_UpdateScreen_saved=cost['NMI_component_saved'],native_not_yet_run=True)
  for f in[Path(__file__).resolve(),run,d/'startup-config.json',body_module,module,controls,B/'proto_palette_coalesce_build.json',B/'proto_palette_coalesce.patch',old/'ready.json',old/'result.json',old/'run.lua']:
   z['bindings'][str(f)]=sha(f)
  for v in json.loads((B/'proto_palette_coalesce_build.json').read_text())['bindings']:
   f=Path(v['path']);assert sha(f)==v['sha256'];z['bindings'][str(f)]=v['sha256']
  for rel in['tools/audit/proto_palette_coalesce_controls_v1.py','tools/audit/link_pit_rygar_sophia_audit_cpu.py','tools/audit/robots_weapon_cpu_v1.py','tools/audit/check_tmnt_render_oa.py','tools/audit/verify_native_relocation.py','src/game.s','src/bill_native_rare.s','src/protoman_cold.s','src/megaman_palette.s','src/mmc5.s','src/player.s','src/reset.s']:
   f=R/rel;z['bindings'][str(f)]=sha(f)
  if kind=='diagnostic':
   z['bindings'][str(inputs)]=sha(inputs);z['literal_replay']=dict(path=str(inputs),sha256=sha(inputs),polls=1939,no_appended_tail=True)
  for f,h in z['bindings'].items():assert sha(f)==h,f
  command=dict(PREPARED_DO_NOT_RUN=True,requires_fresh_ROOT_review_and_native_lease=True,argv=z['command'])
  put(d/'command.json',command);z['bindings'][str(d/'command.json')]=sha(d/'command.json');put(ready,z)
  prepared.append(dict(kind=kind,ready=str(ready),sha256=sha(ready),bindings=len(z['bindings']),frames=cfg['limit'],command=str(d/'command.json')))
 put(out/'index.json',dict(PREPARED_DO_NOT_RUN=True,native_launched=False,ROM_sha256=NEW,profiles=prepared,guard_scope='Unmodified shared harness, original controller, body and VRAM observer; candidate metadata/ROM and diagnostic replay pointer/cutoff only. ROOT alone owns launch/review.'))
 print(json.dumps(dict(status='PREPARED_DO_NOT_RUN',index=str(out/'index.json'),sha256=sha(out/'index.json'),profiles=prepared)))
if __name__=='__main__':main()
