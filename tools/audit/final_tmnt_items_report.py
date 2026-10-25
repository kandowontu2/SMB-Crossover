"""Aggregate eight exact529 turtle lifecycles and preserve all capture hashes."""
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
NAMES=['leonardo','raphael','michelangelo','donatello']


def image(path):
    v=np.frombuffer(path.read_bytes(),dtype='<u4').reshape(240,256)
    return Image.fromarray(np.stack(((v>>16)&255,(v>>8)&255,v&255),axis=2).astype(np.uint8))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    runs=[];compact=[]
    for variant,name in enumerate(NAMES):
        for mode in ['easy','hard']:
            d=a.root/f'{name}-{mode}-native-v5';z=json.loads((d/'proof.json').read_text());n=z['native']
            assert z['passed'] and z['emulator_exit']==0 and ROM==z['ROM_sha256']==sha(d/'candidate.nes')
            assert z['variant']==n['variant']==variant and z['mode']==mode
            assert n['actual_mode_readback']==int(mode=='hard') and n['hard']is(mode=='hard')
            steps=n['steps'];assert len(steps)==37 and n['eligible_defeats']==475 and n['drop_generations']==19
            assert(sum(q['heals']for q in steps),sum(q['grants']for q in steps),sum(q['injuries']for q in steps))==(5,25,8)
            assert [q['q']['action']for q in steps].count('block')==11
            assert steps[1]['riseCalls']==48 and steps[1]['healthAtReveal']==128 and steps[1]['injuries']==1 and steps[1]['after'][variant]['hp']==112
            assert all(q['riseCalls']==48 for q in steps if q['q'].get('gear')==4 and q['q']['action']=='block')
            for q in steps:
                for i,r in enumerate(q['before']):
                    if i!=variant:assert q['after'][i]==r
            assert steps[-1]['refunds']==[100,101,102]and steps[-1]['throws']==3 and steps[-1]['grants']==1
            assert steps[-1]['after'][variant]==dict(hp=128,gear=3,ammo=102)
            events=[json.loads(s)for s in (d/'events.jsonl').read_text().splitlines()]
            count=Counter(e['kind']for e in events)
            cold=[e for e in events if e['kind']=='actual-cold-selection']
            assert len(cold)==1 and cold[0]['data']==dict(character=19,variant=variant,mode=int(mode=='hard'),requested_mode=int(mode=='hard'))
            drops=[e for e in events if e['kind']=='native-drop-generated']
            assert len(drops)==19 and [q['data']['eligibleDefeats']for q in drops]==list(range(25,476,25))
            assert count['actual-native-defeat']==475 and count['actual-native-injury']==8 and count['actual-native-equipment-grant']==25 and count['actual-native-food-heal']==5
            paths=sorted(d.glob('*.argb'));captures=[dict(path=str(f),sha256=sha(f))for f in paths]
            files=['proof.json','native-result.json','config.json','run.lua','events.jsonl','updates.csv','apu.csv','final_tmnt_items_native.lua','candidate.nes','candidate.dbg','candidate.lbl','candidate.map']
            hashes={f:sha(d/f)for f in files}
            assert hashes['run.lua']==z['script_sha256'] and hashes['final_tmnt_items_native.lua']==z['fixture_sha256']
            chosen=[f'{i:02d}-complete'for i in range(1,38)]
            chosen += [f'{i:02d}-mature'for i in [1,2,4,6,8,9]]
            chosen += [f'{i:02d}-drop-generated'for i in [15,22,29,36]]
            chosen += [f'{i:02d}-throw-1'for i in [3,16,23,30]]
            chosen += ['37-throw-1','37-throw-2','37-throw-3','37-equipment-granted','37-catch-1','37-catch-2','37-catch-3']
            assert len(chosen)==58 and len(set(chosen))==58
            sheets=[]
            for start in range(0,len(chosen),20):
                group=chosen[start:start+20];sheet=Image.new('RGB',(1280,270*math.ceil(len(group)/5)),(20,25,32));draw=ImageDraw.Draw(sheet)
                for i,label in enumerate(group):
                    raw=d/(label+'.argb');assert raw.is_file(),raw
                    x,y=i%5*256,i//5*270;sheet.paste(image(raw),(x,y+30));draw.text((x+2,y+1),name+' '+mode,fill='white');draw.text((x+2,y+15),label,fill='white')
                f=a.output/f'{name}-{mode}-overview-{start//20+1}.png';sheet.save(f);sheets.append(dict(path=str(f),sha256=sha(f),capture_names=group))
            row=dict(identity=name,variant=variant,mode=mode,actual_mode=n['actual_mode_readback'],folder=str(d),proof_sha256=hashes['proof.json'],fixture_sha256=z['fixture_sha256'],script_sha256=z['script_sha256'],updates=n['updates'],wall=n['wall'],nmis=n['nmis'],irq_scroll_stores=n['irq_scroll_stores'],hardware_chr_checks=n['hardware_chr_checks'],complete_dma_checks=n['complete_dma_checks'],apu_writes=n['apuWrites'],minimum_sampled_sp=n['minSP'],physical_collections=30,food_collections=5,gear_collections=25,eligible_defeats=475,source_generated_drop_actors=19,actual_injuries=8,boomerang_returns=steps[-1]['refunds'],raw_ppu_captures=len(paths),source_selected_record_final=steps[-1]['after'][variant])
            compact.append(row)
            runs.append(dict(**row,native=n,event_counts=dict(count),file_hashes=hashes,captures=captures,overview_sheets=sheets,cold_mode_readback_event=cold[0],native_drop_generation_events=drops))
    assert len({q['fixture_sha256']for q in compact})==1
    totals={k:sum(r[k]for r in compact)for k in ['updates','wall','nmis','irq_scroll_stores','hardware_chr_checks','complete_dma_checks','apu_writes','physical_collections','food_collections','gear_collections','eligible_defeats','source_generated_drop_actors','actual_injuries','raw_ppu_captures']}
    summary=dict(passed=True,goal_complete=False,ROM_sha256=ROM,native_runs=8,identities=4,mode_cells=8,**totals,minimum_sampled_sp=min(q['minimum_sampled_sp']for q in compact),runs=compact,scope='All4 turtle cold identities x Easy/Hard;30 physical collections and475 native counted arranged-enemy defeats per run. No health/food/gear/ammo/counter/RNG/drop-actor writes. Question blocks, world/player motion/default-health stationary targets and per-step clock are staged; mature block actor is explicitly placed for actual contact after full native rise. Desired native random roll is timed by eligible target introduction. No actor clones or natural unarranged campaign/drop-route claim.',remaining=['Native star/1up, death/area reset, every stance/facing, pool-full/last-ammo/in-flight replacement/durable-target details remain separate.', 'Automatic actual CHR/OAM/NMI/IRQ guards and saved event frames are not exhaustive original-pixel/waveform/performance/campaign certification.', 'Only exact529; later accepted8ff is not relabeled as this tested ROM.'] )
    (a.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    full=dict(summary,full_runs=runs)
    (a.output/'proof.json').write_text(json.dumps(full,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items()if k not in ['runs','remaining']}))
    print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),summary_sha256=sha(a.output/'summary.json'),selected_review_captures=464)))


if __name__=='__main__':main()
