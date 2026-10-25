"""Freeze failed broad qualification and its genuine cold/settled packet costs."""
from pathlib import Path
import argparse,hashlib,json
from PIL import Image
from parodius_visibility_trace_report import commands
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def lines(p):return [json.loads(s)for s in p.read_text(encoding='utf-8').splitlines()]
def brief(x):return {k:v for k,v in x.items()if k not in ['state','hardware','source','ram','packet']}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 modes=read(a.root/'candidate-modes-v1/proof.json');diag=read(a.root/'candidate-failure-diagnostic-v1/proof.json');assert not modes['passed']and sum(x['passed']for x in modes['profiles'])==4 and not diag['passed'];failures=[]
 for name,frame in [('pentarou-easy',479),('octopus-hard',612)]:
  run=a.root/'candidate-failure-diagnostic-v1'/name/'baseline-early';bus=lines(run/'oam-bus.jsonl');epochs=lines(run/'epochs.jsonl');complete=next(x for x in bus if x['kind']=='4014-complete-after-next-LDX'and not x['exact_source']);ident=complete['dma_id'];start=next(x for x in bus if x['kind']=='4014-start'and x['dma_id']==ident);writes=[x for x in bus if x['kind']=='dma-2004'and x['dma_id']==ident];wrong=[x for x in writes if x['actual_hardware_address']!=(x['byte']-1)%256];assert len(writes)==256 and all(x['value']==complete['source'][i]for i,x in enumerate(writes))
  entries=[x for x in bus if x['kind']=='routine-entry'and x['ppu']['frame']==frame];wrapper=next(x for x in entries if x['name']=='SamusFreezeUpdateScreen');updates=[x for x in entries if x['name']=='UpdateScreen'];memory={}
  for entry in updates:
   packet=entry['packet']
   for i,v in enumerate(packet['bytes']):at=(packet['pointer']+i)%65536;assert at not in memory or memory[at]==v;memory[at]=v
  first=updates[0]['packet']['pointer'];packet={'pointer':first,'bytes':[memory.get(first+i,0)for i in range(100)]};decoded=commands(packet);assert decoded['terminated'];data=[x for x in bus if x['kind']=='2007-data'and x['ppu']['frame']==frame];assert decoded['PPUDATA_writes']==len(data)
  native=read(run/'native-result.json');owners=[x for x in bus if x['kind']=='UpdateScreen-owner'];assert len(owners)==native['all_boot_UpdateScreen_C116_owner_checks']and all(x['actual_bankC']==116 and x['nmi_depth']==1 for x in owners)
  strict=a.root/'candidate-modes-v1'/name/'baseline-early';old_inputs=(strict/'inputs.csv').read_bytes().splitlines();new_inputs=(run/'inputs.csv').read_bytes().splitlines();assert new_inputs[:len(old_inputs)]==old_inputs
  public=next(x['dma']['publication']for x in epochs if x['dma']['id']==ident)if frame>=500 else read(run/'first-hardware-mismatch.json')['last_DMA']['publication'];idx=set(public['body']['indices']);diffs=[dict(offset=i,source=v,hardware=complete['hardware'][i],body=i//4 in idx)for i,v in enumerate(complete['source'])if v!=complete['hardware'][i]]
  ret=lambda entry:next(x for x in bus if x['kind']=='routine-return'and x['id']==entry['id'])
  fail=dict(profile=name,frame=frame,mode=native['actual_mode'],variant=native['actual_variant'],native=native,strict_proof_sha256=sha(strict/'proof.json'),diagnostic_proof_sha256=sha(run/'proof.json'),strict_input_prefix_exact_lines=len(old_inputs),recorded_diagnostic_input_sha256=sha(run/'inputs.csv'),source_packet=packet,decoded=decoded,PPUDATA_render_on_writes=sum(bool(x['mask']&24)for x in data),wrapper_entry=brief(wrapper),wrapper_return=brief(ret(wrapper)),wrapper_RAM=wrapper['ram'],outer_UpdateScreen_cycles=ret(updates[0])['inclusive_CPU_cycles'],DMA_start=start,DMA_complete=brief(complete),first_wrong_destination=wrong[0],wrong_destination_writes=len(wrong),all_256_source_values_exact=True,hardware_differences=diffs,body_bad_bytes=sum(x['body']for x in diffs),source_body=public['body']['source']['label'],all_cold_boot_UpdateScreen_C116_checks=len(owners),actual_UpdateScreen_return_words=sorted({x['return_word']for x in owners}),IRQ_lines=sorted({x['ppu']['scanline']for x in bus if x['kind']=='IRQ-entry'}))
  failures.append(fail)
  if frame>=570:
   for f in [frame-1,frame,frame+1,frame+2]:
    raw=run/f'frame-{f:06}.argb';dest=a.output/f'{name}-actual-PPU-{f:06}.png';Image.frombytes('RGBA',(256,240),raw.read_bytes(),'raw','BGRA').convert('RGB').save(dest)
 (a.output/'genuine-failing-packets.json').write_text(json.dumps(failures,indent=2)+'\n',encoding='utf-8')
 q=dict(passed=False,analysis_complete=True,goal_complete=False,ROM_sha256=modes['ROM_sha256'],script_sha256=sha(Path(__file__)),six_mode_variant_aggregate_sha256=sha(a.root/'candidate-modes-v1/proof.json'),diagnostic_continuations_sha256=sha(a.root/'candidate-failure-diagnostic-v1/proof.json'),profiles=modes['profiles'],first_wrong_destinations=[x['first_wrong_destination']for x in failures],root_independent_CPU={n:dict(proof_sha256=sha(a.root/n/'proof.json'),cases=read(a.root/n/'proof.json')['cases'],passed=read(a.root/n/'proof.json')['passed'])for n in ['root-fast-cpu-v1','root-gateway-cpu-v1']},scope='Privatecf0f remains UNQUALIFIED:4/6 cold-menu640 controls pass; PentarouEasy cold40-data/capture packet and OctopusHard settled52-data/seven-command packet still corrupt completed OAM. Strict failures and non-green diagnostic continuations retained; all actual menu/input progress legal and numeric mode readback confirmed. Current helper has functional CPU parity but insufficient native vblank budget. Hard612/613 actual PPU exported; cold479 rawPPU was outside frozen570..620 capture window, hardware bus proof retained. No native stage clear/global-budget/body-priority closure.',bindings={p.name:sha(p)for p in sorted(a.output.iterdir())if p.is_file()})
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(passed=False,analysis_complete=True,proof_sha256=sha(a.output/'proof.json'))))
if __name__=='__main__':main()
