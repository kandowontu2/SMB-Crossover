"""Aggregate immutable late-DMA diagnostics without converting them to passes."""
from pathlib import Path
import argparse, hashlib, json
from collections import Counter
from PIL import Image

sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def lines(p):return [json.loads(s)for s in p.read_text(encoding='utf-8').splitlines()]
def compact(x):return {k:v for k,v in x.items()if k not in ['state','hardware','source']}
def commands(packet):
 data=packet['bytes'];i=0;out=[]
 while i<len(data)and data[i]:
  if i+3>len(data):break
  hi,lo,c=data[i:i+3];n=c&63;n=n or 256;repeat=bool(c&64);used=1 if repeat else n
  if i+3+used>len(data):break
  out.append(dict(buffer_offset=i,address=hi*256+lo,length=n,repeat=repeat,increment=32 if c&128 else 1,data=data[i+3:i+3+used]));i+=3+used
 return dict(commands=out,terminated=i<len(data)and data[i]==0,consumed_bytes=i,PPUDATA_writes=sum(x['length']for x in out))

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--packet',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 prep=read(a.packet/'preparation.json');run=Path(prep['script']).parent;native=read(run/'native-result.json');proof=read(run/'proof.json');assert not proof['passed']and not native['passed']and proof['emulator_exit']==0
 bus=lines(run/'oam-bus.jsonl');epochs=lines(run/'epochs.jsonl');starts={x['dma_id']:x for x in bus if x['kind']=='4014-start'};complete={x['dma_id']:x for x in bus if x['kind']=='4014-complete-after-next-LDX'}
 dma={x['dma']['id']:x['dma']for x in epochs};first=read(run/'first-hardware-mismatch.json');dma[first['last_DMA']['id']]=first['last_DMA']
 nmis=[];open_nmi=None
 for event in bus:
  if event['kind']=='NMI-entry':assert open_nmi is None;open_nmi={'entry':event,'events':[]}
  if open_nmi is not None:open_nmi['events'].append(event)
  if event['kind']=='NMI-return':
   assert open_nmi is not None;open_nmi['return']=event;nmis.append(open_nmi);open_nmi=None
 assert open_nmi is None
 summaries=[]
 for nmi in nmis:
  ev=nmi['events'];routine_returns=[x for x in ev if x['kind']=='routine-return'];routine_entries={x['id']:x for x in ev if x['kind']=='routine-entry'};spans=[]
  for ret in routine_returns:
   entry=routine_entries[ret['id']];span=compact(ret);span['input']=entry.get('ram',{});span['SP']=entry['sp']
   if entry.get('packet'):span['packet']=dict(entry['packet'],decoded=commands(entry['packet']))
   spans.append(span)
  ids=[x['dma_id']for x in ev if x['kind']=='4014-start'];data=[x for x in ev if x['kind']=='2007-data'];summary=dict(entry=compact(nmi['entry']),returned=compact(nmi['return']),inclusive_CPU_cycles=nmi['return']['ppu']['cpu']-nmi['entry']['ppu']['cpu'],DMA_ids=ids,mask_writes=[compact(x)for x in ev if x['kind']=='2001-mask'],routine_spans=spans,PPUDATA_writes=len(data),PPUDATA_rendering_enabled=sum(bool(x['mask']&24)for x in data),CHR_writes=[compact(x)for x in ev if x['kind']=='CHR-write'],IRQs=[compact(x)for x in ev if x['kind']=='IRQ-entry'])
  summaries.append(summary)
 bad=[]
 for ident,c in complete.items():
  writes=[x for x in bus if x['kind']=='dma-2004'and x['dma_id']==ident];assert len(writes)==256 and [x['byte']for x in writes]==list(range(1,257));assert all(x['value']==c['source'][i]for i,x in enumerate(writes))
  if c['exact_source']:continue
  pub=dma[ident]['publication'];body=pub['body'];idx=set(body['indices'])if body else set();wrong=[x for x in writes if x['actual_hardware_address']!=(x['byte']-1)%256]
  diffs=[dict(offset=i,source=v,hardware=c['hardware'][i],belongs_to_body=i//4 in idx)for i,v in enumerate(c['source'])if v!=c['hardware'][i]]
  nmi=next(x for x in summaries if ident in x['DMA_ids']);bad.append(dict(DMA_id=ident,start=starts[ident],completion=compact(c),first_wrong_destination=wrong[0],wrong_destination_writes=len(wrong),all_256_source_values_exact=True,hardware_differences=diffs,body_different_bytes=sum(x['belongs_to_body']for x in diffs),body_source=body['source']['label']if body else None,body_OAM_indices=body['indices']if body else [],publication=pub['ppu'],transaction=pub['transaction'],NMI=nmi,displayed_epochs=[dict(frame=e['start']['frame'],start=e['start'],finish=e['finished'],body_row={k:v for k,v in e.get('body_row',{}).items()if k not in ['hardware','state']})for e in epochs if e['dma']['id']==ident]))
 samples=[]
 for frame in [584,585,586,587,588,611,612,613,614,615,616]:
  raw=run/f'frame-{frame:06}.argb';im=Image.frombytes('RGBA',(256,240),raw.read_bytes(),'raw','BGRA').convert('RGB');dest=a.output/f'actual-PPU-{frame:06}.png';im.save(dest)
  e=next(x for x in epochs if x['start']['frame']==frame);samples.append(dict(frame=frame,raw=str(raw),raw_sha256=sha(raw),PNG=str(dest),PNG_sha256=sha(dest),DMA_id=e['dma']['id'],publication=e['dma']['publication']['ppu'],body_source=e['dma']['publication']['body']['source']['label'],start_hardware_exact_source=e['start_hardware_exact_source'],body_row=compact(e.get('body_row',{}))))
 (a.output/'NMI-timings.json').write_text(json.dumps(summaries,indent=2)+'\n',encoding='utf-8');(a.output/'bad-DMAs.json').write_text(json.dumps(bad,indent=2)+'\n',encoding='utf-8');(a.output/'sample-bindings.json').write_text(json.dumps(samples,indent=2)+'\n',encoding='utf-8')
 rebuild=read(a.root/'baseline-rebuild-v2/candidate.build.json');assert rebuild['sha256']==native['ROM_sha256']
 q=dict(analysis_complete=True,baseline_diagnostic_passed=False,goal_complete=False,ROM_sha256=native['ROM_sha256'],native=native,native_proof_sha256=sha(run/'proof.json'),preparation_sha256=sha(a.packet/'preparation.json'),rebuild_receipt_sha256=sha(a.root/'baseline-rebuild-v2/candidate.build.json'),rebuild_source_supplement_sha256=sha(a.root/'baseline-source-v2-proof.json'),script_sha256=sha(Path(__file__)),source_inputs=prep['controller'],emulator_sha256=proof['emulator_sha256'],first_wrong_DMA=bad[0]['first_wrong_destination'],bad_DMA_ids=[x['DMA_id']for x in bad],kind_counts=dict(Counter(x['kind']for x in bus)),all_128_DMAs_256_exact_source_bus_values=True,body_corruption_in_settled_DMA=next(x for x in bad if x['DMA_id']==109)['body_different_bytes'],scope='Exact frozen50b5 Octopus Easy fixed legal controller from cold boot through actual PPU640. Instrumentation only. Failed cold and settled DMA source-to-hardware assertions retained. 586/587 source/hardware exact; their crowded body visibility remains separate and open. UpdateScreen entry label revisits produce overlapping spans; use the outermost span, never sum overlaps. Actual PPU frame/scanline/cycle and CPU cycles are recorded directly. No art/fix/gameplay source changes; no stage clear, all-mode or other-character verdict.',bindings={p.name:sha(p)for p in sorted(a.output.iterdir())if p.is_file()},raw_bindings=proof['output_bindings'])
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(analysis_complete=True,baseline_passed=False,bad_DMAs=q['bad_DMA_ids'],proof_sha256=sha(a.output/'proof.json'))))
if __name__=='__main__':main()
