"""Bind six progressive native results and lossless PPU captures; never launches Mesen."""
from pathlib import Path
import argparse,hashlib,json
from PIL import Image,ImageDraw
import numpy as np

sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--prefix',default='current220');p.add_argument('--version',default='v3');p.add_argument('--expected-sha256',default='220be8247baf877785c91244876038354442e68502b3f837920f39a674a1fa3e');p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 runs=[]
 for family in ['pit','rygar','scrooge']:
  for mode in ['easy','hard']:
   folder=a.root/f'{a.prefix}-{family}-{mode}-native-{a.version}';proof=folder/'proof.json';z=json.loads(proof.read_text());n=z['native']
   assert z['passed'] and z['emulator_exit']==0 and len(n['cases'])==3
   assert z['ROM_sha256']==a.expected_sha256 and z['family']==family and z['mode']==mode
   assert [(x['before'],x['after'],x['transformCalls'])for x in n['cases']]==[(0,1,60),(1,2,60),(2,2,0)]
   for x in n['cases']:
    assert x['headBlockObserved'] and x['revealed']<x['mature']<x['collisionPlaced']<=x['collected']
    assert x['ownerCalls']==x['beginCalls']==1 and x['attackObserved'] and x['cleanupObserved']
   captures=[];names=[]
   for i in [1,2,3]:
    names.extend(f'{stage}-{i}'for stage in ['block','reveal','mature'])
    if i<3:names.extend([f'transform-{i}-6',f'transform-{i}-30'])
    names.extend(f'{stage}-{i}'for stage in ['collected','attack-first','attack-live','used'])
   assert len(names)==25
   sheet=Image.new('RGB',(256*5,260*5),(20,25,32));draw=ImageDraw.Draw(sheet)
   for index,name in enumerate(names):
    path=folder/(name+'.argb');raw=path.read_bytes();assert len(raw)==240*256*4
    v=np.frombuffer(raw,dtype='<u4').reshape(240,256);rgb=np.stack(((v>>16)&255,(v>>8)&255,v&255),axis=2).astype(np.uint8)
    image=Image.fromarray(rgb);image.save(path.with_suffix('.png'));sheet.paste(image,((index%5)*256,(index//5)*260+20));draw.text(((index%5)*256+3,(index//5)*260+2),name,fill='white')
    captures.append(dict(path=str(path),sha256=sha(path),png_sha256=sha(path.with_suffix('.png'))))
   contact=a.output/f'{family}-{mode}-overview.png';sheet.save(contact)
   runs.append(dict(family=family,mode=mode,proof=str(proof),proof_sha256=sha(proof),fixture_sha256=z['fixture_sha256'],runner_sha256=z['runner_sha256'],script_sha256=z['script_sha256'],native=n,captures=captures,overview=str(contact),overview_sha256=sha(contact),apu_trace_sha256=sha(folder/'apu.csv'),events_sha256=sha(folder/'events.jsonl')))
 assert len({z['fixture_sha256']for z in runs})==1 and len({z['runner_sha256']for z in runs})==1
 summary=dict(passed=True,goal_complete=False,ROM_sha256=a.expected_sha256,native_runs=6,physical_block_cases=18,committed_transform_updates=720,game_updates=sum(r['native']['updates']for r in runs),nmis=sum(r['native']['nmis']for r in runs),irq_scroll_stores=sum(r['native']['irq_scroll_stores']for r in runs),hardware_chr_checks=sum(r['native']['hardware_chr_checks']for r in runs),complete_dma_checks=sum(r['native']['complete_dma_checks']for r in runs),apu_writes=sum(r['native']['apuWrites']for r in runs),minimum_sampled_sp=min(r['native']['minSP']for r in runs),raw_ppu_captures=sum(len(r['captures'])for r in runs),runs=runs,limits=['Visible/logical world blocks explicitly staged','Actor contact explicitly aligned only after actual head/reveal/full native rise, matching the historical physical fixture policy','Hardware CHR-latch/DMA/IRQ guards are not an exhaustive original-pixel or audio-waveform oracle','Pit hammer/flight/recharge and enemy hits, Rygar exact reach/hit/catch and Scrooge pogo remain separate','No star/1up/damage/refill/all-item/campaign/full-goal claim'])
 (a.output/'proof.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items()if k not in ['runs','limits']}))

if __name__=='__main__':main()
