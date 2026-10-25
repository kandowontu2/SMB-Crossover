"""Assert actual calm-orb PPU RGB against the baseline art and adjacent stage."""
from pathlib import Path
import argparse,hashlib,json
import numpy as np
from PIL import Image,ImageDraw
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True)
    for n in ['candidate-easy','candidate-hard','baseline-easy','baseline-hard']:p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    summaries=[];bindings={};reference={};selections=[]
    for role in ['baseline','candidate']:
      for mode in [0,1]:
        name=role+'-'+('hard'if mode else'easy');folder=getattr(a,name.replace('-','_'));proof=json.loads((folder/'proof.json').read_text(encoding='utf-8'));z=proof['native']
        assert proof['dependencies_unchanged']and proof['emulator_exit']==0 and z['mechanics_passed']and z['actual_mode_readback']==mode and z['calm_complete']
        assert proof['preparation_sha256']==sha(a.packet/'preparation.json')and z['fade_policy_passed']==(role=='candidate')and proof['passed']==(role=='candidate')
        assert z['calm_max_scanline_sprites']<=8 and len(z['calm_committed_ages'])==12 and z['calm_admitted']>0 and z['calm_hidden']>0
        rr=[json.loads(x)for x in (folder/'renders.jsonl').read_text(encoding='utf-8').splitlines()];selected=[]
        for age in range(236,248):
            r=next(r for r in rr if r.get('capture')and any(q.get('birth')==z['calm_serial']and q['age']==age for q in r['admissions']))
            q=next(q for q in r['admissions']if q.get('birth')==z['calm_serial']and q['age']==age)
            assert r['calm']['desired']and r['calm']['enemies']==r['calm']['shots']==0 and r['calm']['player_y']+32<200
            assert r['visible_start']['ppu']['frame_count']==r['visible_end']['frame_count']and r['visible_start']['ppu']['scanline']==-1 and r['visible_end']['scanline']==240
            assert r['visible_start']['dma']['render_id']==r['id']and len(r['visible_start']['oam'])==256
            raw=folder/r['capture'];assert sha(raw)==proof['captures'][r['capture']]
            argb=np.frombuffer(raw.read_bytes(),dtype='<u4').reshape(240,256);rgb=np.stack([(argb>>16)&255,(argb>>8)&255,argb&255],axis=-1).astype('uint8');im=Image.fromarray(rgb)
            actor=next(x for x in r['actors']if x['slot']==q['slot']);x,y=actor['x'],actor['y'];assert x==200 and y==208
            crop=rgb[y-8:y+10,x-8:x+8,:];background=rgb[y-8:y+10,x+24:x+40,:]
            different=int(np.any(crop!=background,axis=-1).sum())
            expected=q['expected_visible']if role=='candidate'else True
            if role=='baseline':
                if mode not in reference:reference[mode]=crop.copy()
                assert np.array_equal(crop,reference[mode])and different>0,'Baseline calm source art must be full and stable at all12 ages'
            elif expected:assert np.array_equal(crop,reference[mode])and different>0,'Admitted candidate actual PPU pixels exactly equal original supplied-art baseline'
            else:assert np.array_equal(crop,background)and different==0,'Odd fading actor has no actual PPU pixels; exact adjacent repeated-stage background'
            selected.append((r,q,im));selections.append(dict(profile=name,age=age,parity=q['frame']&1,expected_visible=expected,actual_changed_pixels_against_adjacent_stage=different,crop_RGB_sha256=hashlib.sha256(crop.tobytes()).hexdigest(),reference_RGB_sha256=hashlib.sha256(reference[mode].tobytes()).hexdigest(),raw=str(raw),raw_sha256=sha(raw),RGB_sha256=hashlib.sha256(rgb.tobytes()).hexdigest(),rect=[x-8,y-8,x+8,y+10],background_rect=[x+24,y-8,x+40,y+10],render_id=r['id'],visible_start=r['visible_start']['ppu'],visible_end=r['visible_end'],DMA=r['visible_start']['dma'],player_y=r['calm']['player_y']))
        sheet=Image.new('RGB',(1024,810),'#202020');draw=ImageDraw.Draw(sheet)
        for i,(r,q,im)in enumerate(selected):
            x=i%4*256;y=i//4*270;sheet.paste(im,(x,y+30));draw.text((x+2,y+2),f"{name} age{q['age']} p{q['frame']&1} emit{q['emitted']}",fill='white');draw.text((x+2,y+14),f"PPU{r['visible_end']['frame_count']} DMA{r['visible_start']['dma']['id']} bodyY{r['calm']['player_y']}",fill='white')
        path=a.output/(name+'-calm-ages236-247.png');sheet.save(path);bindings[str(path)]=sha(path)
        for file in ['proof.json','native-result.json','run.lua','config.json','events.jsonl','cadence.csv','renders.jsonl','apu.csv']:bindings[str(folder/file)]=sha(folder/file)
        for file,digest in proof['captures'].items():bindings[str(folder/file)]=digest
        summaries.append(dict(profile=name,ROM_sha256=z['ROM_sha256'],actual_mode=mode,updates=z['updates'],wall=z['wall'],births=len(z['births']),kills=z['kills'],calm_serial=z['calm_serial'],calm_max_scanline_sprites=z['calm_max_scanline_sprites'],calm_admitted=z['calm_admitted'],calm_hidden=z['calm_hidden'],natural_expiries=z['natural_expiries'],real_pickups=z['real_pickups'],nmis=z['nmis'],irq_scroll_stores=z['irq_scroll_stores'],hardware_chr_checks=z['hardware_chr_checks'],complete_dma_checks=z['complete_dma_checks'],min_sampled_SP=z['minSP'],first_wrong_admission=z.get('first_wrong_native_admission'),first_wrong_oam_write=z.get('first_wrong_native_oam_write')))
    result=dict(passed=True,goal_complete=False,actual_PPU_RGB_controls_passed=True,preparation_sha256=sha(a.packet/'preparation.json'),reporter_sha256=sha(Path(__file__)),profiles=summaries,selected_distinct_raw_frames=len(selections),selections=selections,bindings=bindings,visual_review_complete=False,scope='Separate calm real-earned small health orb component. Exact full16x18 RGB art crop is constant across all12 baseline source ages; every admitted candidate crop equals it pixel-for-pixel. Every odd fading candidate crop equals the unobstructed stage32px to its right, exploiting the disclosed uniform16px repeated staged floor. No mobile executable art/timing oracle. Actual native jump moves body clear; no shots/enemies and maximum4 orb-row sprites measured. Pool stress and its partial visibility remain separate.')
    (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(passed=True,proof_sha256=sha(a.output/'proof.json'),actual_PPU_frames=len(selections))))
if __name__=='__main__':main()
