"""Bind fresh529 numeric Hard progression/ability receipts; no emulator launch."""
from pathlib import Path
import argparse
from collections import Counter
import hashlib
import json
import math
from PIL import Image,ImageDraw
import numpy as np

ROM='52918588bab0eec3f3a1f857bf084d2d799e88a5c781c75233c098ccc5f54f3f'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    runs=[];unique={}
    for suite in ['progression','abilities']:
        for family,count in [('pit',10),('rygar',12),('scrooge',9)]:
            d=a.root/f'{family}-hard-{suite}-v1';z=json.loads((d/'proof.json').read_text());n=z['native']
            assert z['passed'] and z['emulator_exit']==0 and z['ROM_sha256']==ROM==sha(d/'candidate.nes')
            assert z['mode']=='hard' and z['numeric_mode_requested']==1 and n['actual_mode_readback']==1 and n['hard'] is True
            assert z['script_sha256']==sha(d/'run.lua')
            items=n['cases']if suite=='progression'else n['physical_collections']
            assert [(x['before'],x['after'],x['transformCalls'])for x in items]==[(0,1,60),(1,2,60)]+([(2,2,0)]if suite=='progression'else[])
            for q in items:
                assert q['headBlockObserved'] and q['revealed']<q['mature']<q['collisionPlaced']<=q['collected']
                assert q['ownerCalls']==q['beginCalls']==1
                if suite=='progression':assert q['attackObserved'] and q['cleanupObserved']
            if suite=='progression':assert n['mode_guard_executed']is True
            else:
                assert len(n['abilities'])==count
                assert all(q['tier']==q['q']['tier']and q['gameUpdates']==q['q']['limit']for q in n['abilities'])
            events=[json.loads(s)for s in (d/'events.jsonl').read_text().splitlines()]
            modes=[e for e in events if e['kind']=='actual-numeric-mode-readback']
            assert len(modes)==1 and modes[0]['data']==dict(actual=1,requested=1)
            frames=[]
            for f in sorted(d.glob('*.argb')):
                h=sha(f)
                if h not in unique:
                    raw=np.frombuffer(f.read_bytes(),dtype='<u4').reshape(240,256)
                    im=Image.fromarray(np.stack(((raw>>16)&255,(raw>>8)&255,raw&255),axis=2).astype(np.uint8))
                    unique[h]=dict(id=len(unique)+1,raw_sha256=h,image=im,aliases=[])
                u=unique[h];u['aliases'].append(dict(profile=d.name,name=f.stem))
                frames.append(dict(path=str(f),sha256=h,unique_id=u['id']))
            files=['proof.json','preparation.json','config.json','run.lua','events.jsonl','apu.csv','candidate.nes','candidate.dbg','candidate.lbl','candidate.map']
            if suite=='abilities':files.append('ability-updates.csv')
            runs.append(dict(family=family,suite=suite,folder=str(d),proof=z,
                             file_hashes={f:sha(d/f)for f in files},event_counts=dict(Counter(e['kind']for e in events)),mode_RAM_readback_events=modes,captures=frames))
    frames=list(unique.values());sheets=[]
    for start in range(0,len(frames),20):
        group=frames[start:start+20];sheet=Image.new('RGB',(1280,270*math.ceil(len(group)/5)),(20,25,32));draw=ImageDraw.Draw(sheet)
        for i,q in enumerate(group):
            x,y=i%5*256,i//5*270;sheet.paste(q['image'],(x,y+30));alias=q['aliases'][0]
            draw.text((x+2,y+1),str(q['id'])+' '+alias['profile'].replace('-hard-',' ').replace('-v1',''),fill='white');draw.text((x+2,y+15),alias['name'],fill='white')
        path=a.output/f'frames-{start//20+1:02}.png';sheet.save(path);sheets.append(dict(path=str(path),sha256=sha(path),first=start+1,last=start+len(group)))
    for q in frames:del q['image']
    totals={k:sum(q['proof']['native'][source]for q in runs)for k,source in [('updates','updates'),('nmis','nmis'),('irq_scroll_stores','irq_scroll_stores'),('hardware_chr_checks','hardware_chr_checks'),('complete_dma_checks','complete_dma_checks'),('apu_writes','apuWrites')]}
    result=dict(passed=True,goal_complete=False,ROM_sha256=ROM,native_runs=6,
                actual_mode='Hard',actual_numeric_mode=1,distinct_identities=3,distinct_mode_cells=3,
                ordinary_progression_cases=9,acquired_ability_cases=31,physical_collections=15,
                capped_collections=3,committed_transform_updates=720,**totals,
                minimum_sampled_sp=min(q['proof']['native']['minSP']for q in runs),
                raw_ppu_captures=sum(len(q['captures'])for q in runs),unique_ppu_frames=len(unique),
                runs=runs,unique_frames=frames,sheets=sheets,
                supersession='Fresh529 Hard evidence only. Does not relabel old220/84 duplicate Easy receipts, add identities or certify current529 Easy.',
                limits=['Visible/logical world and targets staged; actual head/reveal/full rise and explicit post-rise item contact placement retained.',
                        'Actual mode1 RAM readback, literal boolean and numeric guards, no tier/inventory/fuel/flight/reach/pogo injection.',
                        'Same bounded abilities/graphics/audio/terrain/priority limits as original separate report. No original waveform/pixel oracle, campaign/every-item/full-roster completion.'])
    f=a.output/'proof.json';f.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items()if k not in ['runs','unique_frames','sheets','limits']}))
    print(json.dumps(dict(path=str(f),sha256=sha(f),sheets=len(sheets))))


if __name__=='__main__':main()
