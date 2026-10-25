"""Reaggregate exact frozen fade receipts and create actual-PPU review sheets."""
from pathlib import Path
import argparse,collections,csv,hashlib,json,statistics
import numpy as np
from PIL import Image,ImageDraw
BASE='9bac46e934d3301e378139783febf2d54c4fd5753a62e082f2d7e6580946d58c'
CANDIDATE='c32b70ed95f3a4031e9e8ff5696c9bd8f310bf11443748aa6377482d40b41f47'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p):return[json.loads(x)for x in p.read_text(encoding='utf-8').splitlines()]
def image(p):
    a=np.frombuffer(p.read_bytes(),dtype='<u4').reshape(240,256)
    return Image.fromarray(np.stack([(a>>16)&255,(a>>8)&255,a&255],axis=-1).astype('uint8'))
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--packet',type=Path,required=True);p.add_argument('--candidate-easy',type=Path,required=True);p.add_argument('--candidate-hard',type=Path,required=True)
    p.add_argument('--baseline-easy',type=Path,required=True);p.add_argument('--baseline-hard',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    prep=json.loads((a.packet/'preparation.json').read_text(encoding='utf-8'))
    summaries=[];selections=[];bindings={};cadences={}
    for role in ['candidate','baseline']:
      for mode in [0,1]:
        name=role+'-'+('hard'if mode else'easy');folder=getattr(a,name.replace('-','_'));proof=json.loads((folder/'proof.json').read_text(encoding='utf-8'));z=proof['native'];rom=CANDIDATE if role=='candidate'else BASE
        assert proof['dependencies_unchanged']and proof['emulator_exit']==0 and z['mechanics_passed']and z['actual_mode_readback']==mode
        assert z['ROM_sha256']==rom and z['fade_policy_passed']==(role=='candidate')and proof['passed']==(role=='candidate')
        assert sha(folder/'candidate.nes')==rom and proof['preparation_sha256']==sha(a.packet/'preparation.json')
        assert z['global_owner_calls']==z['updates']and z['real_pickups']==1 and z['natural_expiries']>=4
        assert z['four_actor_committed_renders']>0 and z['empty_committed_renders']>=120
        assert len(z['committed_fade_coverage'])==24
        for b in z['births']:
            assert b['rng'][0]&3==0 and b['kind']==(1 if b['rng'][1]<192 else 2)and b['meter']==(0 if b['rng'][2]&1==0 else 128)
            if 'expired'in b:assert b['expired']-b['born']==420
        rr=rows(folder/'renders.jsonl');seen=set();arts=set();visible=[]
        for r in rr:
            start=r['visible_start'];end=r['visible_end'];dma=start['dma'];pub=dma['publication']
            assert start['ppu']['scanline']==-1 and start['ppu']['cycle']==0 and end['scanline']==240 and end['cycle']==0
            assert start['ppu']['frame_count']==end['frame_count']==dma['ppu']['frame_count']
            assert 241<=dma['ppu']['scanline']<=260 and dma['render_id']==pub['render_id']==r['id']
            assert len(start['oam'])==256
            for q in r['admissions']:
                assert q['actual_a']==(q['kind']if role=='baseline'else q['expected_a'])
                assert q['emitted']==(q['kind']!=0 if role=='baseline'else q['expected_visible'])
                if q['emitted']:assert q['source_art_passed'];arts.add(q['art'])
                if q['kind']and 236<=q['age']<=247:
                    seen.add((q['age'],q['frame']&1));assert r.get('capture')
            if r.get('capture'):
                assert sha(folder/r['capture'])==proof['captures'][r['capture']]
        assert seen=={(age,parity)for age in range(236,248)for parity in [0,1]}
        sheet=Image.new('RGB',(4*256,6*270),'#202020');draw=ImageDraw.Draw(sheet)
        chosen=set()
        for cell,(age,parity)in enumerate((x,y)for x in range(236,248)for y in [0,1]):
            r=next(r for r in rr if r.get('capture')and any(q['kind']and q['age']==age and q['frame']&1==parity for q in r['admissions']))
            q=next(q for q in r['admissions']if q['kind']and q['age']==age and q['frame']&1==parity)
            raw=folder/r['capture'];im=image(raw);x=cell%4*256;y=cell//4*270;sheet.paste(im,(x,y+30))
            draw.text((x+3,y+2),f"{name} age{age} p{parity} emit{q['emitted']}",fill='white')
            draw.text((x+3,y+14),f"PPU{r['visible_end']['frame_count']} DMA{r['visible_start']['dma']['id']} render{r['id']}",fill='white')
            chosen.add(r['capture']);selections.append(dict(profile=name,age=age,parity=parity,slot=q['slot'],birth=q['birth'],emitted=q['emitted'],raw=str(raw),sha256=sha(raw),RGB_sha256=hashlib.sha256(im.tobytes()).hexdigest(),render_id=r['id'],visible_start=r['visible_start']['ppu'],visible_end=r['visible_end'],DMA=r['visible_start']['dma']))
        path=a.output/(name+'-ages236-247-both-parities.png');sheet.save(path);bindings[str(path)]=sha(path)
        cc=list(csv.DictReader((folder/'cadence.csv').open(encoding='utf-8')));cadences[name]=cc
        controls={}
        for phase in ['empty-before','empty-after','pool','pool-expiry','supplement','pickup']:
            group=[r for r in cc if r['phase']==phase]
            if group:controls[phase]=dict(completed_updates=len(group),unique_wall_frames=len({r['wall']for r in group}),draw_calls=sum(int(r['draw_calls'])for r in group),inclusive_cycles_min=min(int(r['inclusive_cycles'])for r in group),inclusive_cycles_max=max(int(r['inclusive_cycles'])for r in group),inclusive_cycles_mean=statistics.mean(int(r['inclusive_cycles'])for r in group))
        summaries.append(dict(profile=name,ROM_sha256=rom,proof_sha256=sha(folder/'proof.json'),native_sha256=sha(folder/'native-result.json'),mechanics_passed=True,fade_policy_passed=z['fade_policy_passed'],updates=z['updates'],wall=z['wall'],births=len(z['births']),kills=z['kills'],natural_expiries=z['natural_expiries'],pickups=z['real_pickups'],source_art_seen=sorted(arts),four_actor_committed_renders=z['four_actor_committed_renders'],empty_committed_renders=z['empty_committed_renders'],actual_PPU_counter_binding_checks=len(rr),selected_distinct_raw_frames=len(chosen),controls=controls,first_wrong_admission=z.get('first_wrong_native_admission'),first_wrong_oam_write=z.get('first_wrong_native_oam_write'),nmis=z['nmis'],irq_scroll_stores=z['irq_scroll_stores'],hardware_chr_checks=z['hardware_chr_checks'],complete_dma_checks=z['complete_dma_checks'],min_sampled_SP=z['minSP']))
        for file in ['proof.json','native-result.json','run.lua','config.json','events.jsonl','cadence.csv','renders.jsonl','apu.csv']:
            bindings[str(folder/file)]=sha(folder/file)
        for name2,digest in proof['captures'].items():bindings[str(folder/name2)]=digest
    comparisons=[]
    for mode in [0,1]:
        suffix='hard'if mode else'easy';old=[r for r in cadences['baseline-'+suffix]if r['phase']=='empty-before'];new=[r for r in cadences['candidate-'+suffix]if r['phase']=='empty-before']
        assert len(old)==len(new)==120
        assert all(int(x['drops'])==int(y['drops'])==0 and int(x['draw_calls'])==int(y['draw_calls'])==1 for x,y in zip(old,new))
        deltas=[int(y['inclusive_cycles'])-int(x['inclusive_cycles'])for x,y in zip(old,new)]
        comparisons.append(dict(mode_value=mode,scope='Identical cold idle arena/control before native target/RNG attempts;120 complete updates per ROM. Inclusive cycles include actual interrupts.',updates=120,baseline_unique_wall_frames=len({r['wall']for r in old}),candidate_unique_wall_frames=len({r['wall']for r in new}),baseline_draws=sum(int(r['draw_calls'])for r in old),candidate_draws=sum(int(r['draw_calls'])for r in new),inclusive_cycle_delta_min=min(deltas),inclusive_cycle_delta_max=max(deltas),inclusive_cycle_delta_mean=statistics.mean(deltas),no_constant60Hz_claim=True))
    result=dict(passed=True,candidate_native_fade_qualified=True,baseline_missing_fade_reproduced_both_modes=True,goal_complete=False,baseline=BASE,candidate=CANDIDATE,preparation_sha256=sha(a.packet/'preparation.json'),reporter_sha256=sha(Path(__file__)),profiles=summaries,matched_empty_cadence=comparisons,selected_cells=len(selections),selected_unique_raw_frames=len({s['raw']for s in selections}),selections=selections,bindings=bindings,visual_review_complete=False,limits=['All source admissions and supplied-art OAM records checked; selected actual PPU review is separate. Ordinary8-sprite scanline/rotation can partially hide admitted art under live fire/enemies.','No executable mobile gameplay oracle or audio-waveform fidelity.','Random pool contents/timing can differ between ROMs; full-pool timings are scenario matched, not a byte-identical scene comparison.','Native helper SP sampling and lower-stack guard are bounded observations, not a global maximum-stack proof.','Only exact9bac/c32b qualified; current installed5ec requires explicit later composition.'])
    (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,proof_sha256=sha(a.output/'proof.json'),profiles=len(summaries),selected_cells=len(selections),selected_unique_raw_frames=result['selected_unique_raw_frames'])))
if __name__=='__main__':main()
