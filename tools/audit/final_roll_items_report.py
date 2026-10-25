"""Aggregate two explicitly pinned Roll lifecycles; retain every raw capture hash."""
from pathlib import Path
import argparse,hashlib,json,math
from collections import Counter
import numpy as np
from PIL import Image,ImageDraw

TARGET='8ff245ae662059abbc77c5de517260032775b7ba881a5201b8b54686ccf08277'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def pixels(path):
    v=np.frombuffer(path.read_bytes(),dtype='<u4').reshape(240,256)
    return Image.fromarray(np.stack(((v>>16)&255,(v>>8)&255,v&255),axis=2).astype(np.uint8))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--easy',type=Path,required=True)
    p.add_argument('--hard',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--expected-sha256',default=TARGET)
    p.add_argument('--expected-easy-fixture-sha256')
    p.add_argument('--expected-hard-fixture-sha256')
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);runs=[];compact=[];plans=[]
    explicit_fixtures=dict(easy=a.expected_easy_fixture_sha256,hard=a.expected_hard_fixture_sha256)
    assert all(explicit_fixtures.values())or not any(explicit_fixtures.values()),'Supply both exact mode-fixture hashes or neither.'
    for mode,folder in [('easy',a.easy),('hard',a.hard)]:
        z=json.loads((folder/'proof.json').read_text(encoding='utf-8'));n=z['native']
        assert z['passed'] and z['emulator_exit']==0 and z['ROM_sha256']==sha(folder/'candidate.nes')==a.expected_sha256
        assert z['mode']==mode and n['actual_mode_readback']==int(mode=='hard') and n['hard']is(mode=='hard')
        if explicit_fixtures[mode]:assert z['fixture_sha256']==explicit_fixtures[mode]
        plans.append(json.loads((folder/'config.json').read_text(encoding='utf-8'))['plan'])
        steps=n['steps'];assert len(steps)==36 and n['committed_hud_checks']==36
        assert sum(q['injuries']for q in steps)==15 and sum(q['charges']for q in steps)==25
        assert sum(q['grants']for q in steps if q['q']['action']=='capsule')==13
        assert sum(q['grants']for q in steps if q['q']['action']=='block')==6
        assert steps[-1]['after']['hp']==steps[-1]['after']['energy']==28 and steps[-1]['after']['food']==0
        assert all(q['collided']>=q['mature']>=q['reveal']for q in steps if q['q']['action']=='block')
        assert all(q['pellets']>0 and q['charges']==0 for q in steps if q['q']['action']=='refuse')
        events=[json.loads(s)for s in(folder/'events.jsonl').read_text(encoding='utf-8').splitlines()];counts=Counter(e['kind']for e in events)
        cold=[e for e in events if e['kind']=='actual-cold-selection'];assert len(cold)==1 and cold[0]['data']==dict(character=9,variant=1,mode=int(mode=='hard'),requested_mode=int(mode=='hard'))
        assert counts['actual-food-grant']==4 and counts['actual-native-injury']==15 and counts['actual-acquired-charge']==25
        assert counts['committed-resource-hud']==36 and counts['actual-native-death-start']==1
        physical_caps=[e for e in events if e['kind']=='actual-physical-capsule'and e['phase']=='capsule'];assert len(physical_caps)==13
        draws=[e for e in events if e['kind']=='earned-capsule-native-draw-record']
        frames=sorted(folder.glob('*.argb'));capture_hashes=[dict(path=str(f),sha256=sha(f))for f in frames]
        chosen=[]
        for i,q in enumerate(steps,1):
            chosen += [f'{i:02d}-start',f'{i:02d}-committed-hud']
            action=q['q']['action']
            if action=='block':chosen += [f'{i:02d}-mature',f'{i:02d}-contact']
            if action in ['capsule','expiry','hold']:chosen += [f'{i:02d}-desired-drop']
            if action=='charge':chosen += [f'{i:02d}-charge-1',f'{i:02d}-charge-{q["q"]["count"]}']
            if action=='expiry':chosen += [f'{i:02d}-expiry-age-{age}'for age in range(236,248)]
            if action=='death':chosen += [f'{i:02d}-death-start',f'{i:02d}-respawn']
        chosen=list(dict.fromkeys(chosen));sheets=[]
        for start in range(0,len(chosen),20):
            labels=chosen[start:start+20];im=Image.new('RGB',(1280,270*math.ceil(len(labels)/5)),(20,25,32));d=ImageDraw.Draw(im)
            for i,label in enumerate(labels):
                path=folder/(label+'.argb');assert path.is_file(),path
                x,y=i%5*256,i//5*270;im.paste(pixels(path),(x,y+30));d.text((x+2,y+1),'Roll '+mode,fill='white');d.text((x+2,y+15),label,fill='white')
            path=a.output/f'roll-{mode}-overview-{start//20+1}.png';im.save(path);sheets.append(dict(path=str(path),sha256=sha(path),capture_names=labels))
        files=['proof.json','native-result.json','run.lua','config.json','final_roll_items_native.lua','events.jsonl','updates.csv','apu.csv','candidate.nes','candidate.dbg','candidate.lbl','candidate.map']
        hashes={f:sha(folder/f)for f in files};assert hashes['run.lua']==z['script_sha256']and hashes['final_roll_items_native.lua']==z['fixture_sha256']
        row=dict(mode=mode,actual_mode=n['actual_mode_readback'],folder=str(folder),proof_sha256=hashes['proof.json'],fixture_sha256=z['fixture_sha256'],script_sha256=z['script_sha256'],game_updates=n['updates'],wall_frames=n['wall'],nmis=n['nmis'],irq_stores=n['irq_scroll_stores'],chr_checks=n['hardware_chr_checks'],dma_checks=n['complete_dma_checks'],hud_checks=n['committed_hud_checks'],register_range_writes=n['register_range_writes'],minimum_sampled_sp=n['minSP'],planned_physical_food=4,planned_physical_capsules=13,planned_star=1,planned_oneup=1,actual_nonlethal_injuries=15,actual_charge_attacks=25,actual_defeats=counts['actual-native-defeat'],actual_drop_generations=counts['actual-native-drop-generated'],raw_event_captures=len(frames),selected_review_captures=len(chosen))
        compact.append(row);runs.append(dict(**row,native=n,event_counts=dict(counts),cold_readback=cold[0],draw_age_observations=draws,file_hashes=hashes,captures=capture_hashes,overview_sheets=sheets))
    assert plans[0]==plans[1], 'The exact36-step resource/lifecycle plan must agree.'
    if not any(explicit_fixtures.values()):assert len({r['fixture_sha256']for r in compact})==1
    keys=['game_updates','wall_frames','nmis','irq_stores','chr_checks','dma_checks','hud_checks','register_range_writes','planned_physical_food','planned_physical_capsules','planned_star','planned_oneup','actual_nonlethal_injuries','actual_charge_attacks','actual_defeats','actual_drop_generations','raw_event_captures','selected_review_captures']
    summary=dict(passed=True,goal_complete=False,ROM_sha256=a.expected_sha256,native_runs=2,identities=1,mode_cells=2,minimum_sampled_sp=min(r['minimum_sampled_sp']for r in compact),**{k:sum(r[k]for r in compact)for k in keys},runs=compact,scope='Two cold Roll modes; actual earned depletion, head/block/full rise/controller contact, actual natural-RNG default-health NPC drops/refill/caps/expiry, star/1up and real death/respawn cleanup. Flat-world/blocks/motion/NPC/clock staging explicit. No resource/RNG/outcome writes or pickup clones/mature placement.',rendering_limit='Age/fade observations and event frames are diagnostic; this aggregate does not declare mobile-original fidelity or a passed fade policy. Visual review and any first wrong render write remain separate.',remaining=['Original mobile executable/timing/audio unavailable; static asset fidelity is separate.','Natural campaign routes, native pool-full reachability, other stances/facings/Bowser/water/area/performance and exhaustive original PPU/audio remain open.'])
    summary['explicit_mode_fixture_bindings']=explicit_fixtures
    summary['identical36step_plans']=True
    (a.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    (a.output/'proof.json').write_text(json.dumps(dict(summary,full_runs=runs),indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items()if k not in ['runs','remaining','scope','rendering_limit']}))
    print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),summary_sha256=sha(a.output/'summary.json'))))


if __name__=='__main__':main()
