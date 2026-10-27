"""Prepare exact failed1939-poll Proto3e7 replay plus unchanged passive probe."""
from pathlib import Path
import argparse,csv,hashlib,json,sys
from proto_startup_vram_timing_prepare_v2 import main as startup_prepare
from current_roster_compact_11_v1 import ROOT,lua
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')
EXPECTED='3e7c53d82eb949b8527d837861d95ed6051966056ca3f336fafd66e514e055ea'

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve()
 rom=ROOT/'build/mm_body_current.nes';old=ROOT/'build/verification/mm-body-proto-current-hard-v1'
 assert sha(rom)==EXPECTED
 previous=json.loads((old/'ready.json').read_text());result=json.loads((old/'result.json').read_text())
 assert previous['ROM_sha256']==result['ROM_sha256']==EXPECTED and not result['passed']and result['frames']==1940 and result['polls']==1939
 assert result['reason']=='Active render enable precedes pre-render vertical reload'
 inputs=old/'inputs.csv';rows=list(csv.DictReader(inputs.open(newline='')))
 assert len(rows)==1939 and all(int(r['poll'])==i+1 and int(r['frame'])==i+1 for i,r in enumerate(rows))
 # The original strictly failed before poll1940: no fabricated tail input is
 # added. If the deadline unexpectedly passes, stream-exhaustion must fail.
 saved=sys.argv[:];sys.argv=[str(Path(__file__)),'--rom',str(rom),'--expected-sha256',EXPECTED,'--output',str(out)]
 try:startup_prepare()
 finally:sys.argv=saved
 ready=out/'ready.json';z=json.loads(ready.read_text());cfg=z['config'];cfg.update(replay=inputs.as_posix(),limit=2050)
 diagnostic=json.loads((out/'startup-config.json').read_text());diagnostic['cutoff_frame']=2050;put(out/'startup-config.json',diagnostic)
 # Retain the original body-owner observer byte-for-byte as well as all shared
 # route guards. Genuine current PCs/banks/bytes are rechecked before binding.
 body=previous['passive_body_observer']['metadata_fresh_from_actual_DBG']
 assert body['ROM_sha256']==EXPECTED
 b=scoped_load(rom)
 for h in body['hooks'].values():
  at=16+h['bank']*8192+h['pc']%8192;assert list(b['raw'][at:at+len(h['bytes'])])==h['bytes']
 body_module=ROOT/'tools/audit/mm_proto_body_reserve_passive_v1.lua';module=ROOT/'tools/audit/proto_startup_vram_timing_v2.lua';harness=ROOT/'tools/audit/current_roster_compact_11_v1.lua'
 assert sha(body_module)==previous['passive_body_observer']['module_sha256']
 for f in [body_module,module]:
  text=f.read_text();assert 'emu.write'not in text and 'setInput'not in text and 'removeMemoryCallback'not in text
 append='PROTO_STARTUP_VRAM_TIMING='+lua(diagnostic)+'\nlocal previousClose=ROSTER_CONFIG.bass_close\nlocal startupClose=dofile('+lua(module.as_posix())+')\nROSTER_CONFIG.bass_close=function()local q=previousClose and previousClose()or{};q.startup_vram=startupClose();return q end\n'
 run=out/'run.lua';run.write_text('ROSTER_CONFIG='+lua(cfg)+'\nfor name,value in pairs(ROSTER_CONFIG.extra_ram)do assert(L[name]==nil or L[name]==value,"RAM alias conflict: "..name);L[name]=value end\nMM_BODY_OBSERVATION_CONFIG='+lua(body)+'\nMM_BODY_OBSERVATION_CONFIG.output=ROSTER_CONFIG.prefix.."body-epochs.csv"\ndofile('+lua(body_module.as_posix())+')\n'+append+'dofile('+lua(harness.as_posix())+')\n',newline='\n')
 z['config']=cfg;z['max_total_frames']=2050;z['expected_outcome']='Original active-render deadline FALSE at1940/E00B; no assertion waived. This finite diagnostic is not a fullroute qualification.'
 z['startup_probe'].update(scope='Literal failed1939poll replay, exactProto3e7; observer2050PPU cutoff/30000rowcap; all original shared render/CHR/256DMA/E3/SMC/IRQ/SP guards and existing body-owner observer retained.',maximum_rows=30000)
 z['replay_provenance']=dict(input=str(inputs),input_sha256=sha(inputs),actual_polls=1939,no_tail_input_added=True,original_result_sha256=sha(old/'result.json'),original_first_failure=json.loads(next(line for line in(old/'events.jsonl').read_text().splitlines()if'"kind":"first-failure"'in line)))
 for f in [Path(__file__).resolve(),run,out/'startup-config.json',body_module,module,inputs,old/'ready.json',old/'result.json',old/'events.jsonl',old/'trace.csv',old/'run.lua']:z['bindings'][str(f)]=sha(f)
 for f,h in z['bindings'].items():assert sha(Path(f))==h,f
 put(out/'command.json',dict(PREPARED_DO_NOT_RUN=True,requires_ROOT_native_lease_and_grant=True,argv=z['command']))
 z['bindings'][str(out/'command.json')]=sha(out/'command.json');put(ready,z)
 print(json.dumps(dict(status='PREPARED_DO_NOT_RUN',ROM_sha256=EXPECTED,ready=str(ready),ready_sha256=sha(ready),bindings=len(z['bindings']),command=z['command'])))
if __name__=='__main__':main()
