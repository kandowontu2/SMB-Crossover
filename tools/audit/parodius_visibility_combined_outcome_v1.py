"""Freeze the actual e11 cold-control negative; never launches an emulator."""
from pathlib import Path
from collections import Counter, defaultdict
import argparse, hashlib, json
import numpy as np
from PIL import Image, ImageDraw
from parodius_visibility_combined_pixels_v2 import model

sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
lines = lambda p: [json.loads(s) for s in p.read_text().splitlines()]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for n in ['baseline', 'candidate', 'pixels', 'source', 'output']:
        ap.add_argument('--' + n, type=Path, required=True)
    a = ap.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    ds = [a.baseline, a.candidate]
    es = [{e['start']['frame']: e for e in lines(d/'epochs.jsonl')} for d in ds]
    chrraw = (ds[0]/'candidate.nes').read_bytes()[1048592:]
    pixel_proof = read(a.pixels/'proof.json')
    assert not pixel_proof['passed'] and pixel_proof['source_model_actual_RGB_mismatches'] == 0
    colors = pixel_proof['uncontested_color_calibration']
    changes, first = [], {}
    for f in sorted(es[0]):
        ms = [model(e[f], chrraw)[0] for e in es]
        ims = [np.fromfile(d/f'frame-{f:06}.argb', dtype='<u4').reshape(240,256)&0xffffff for d in ds]
        other = [{pt:v for pt,v in m.items() if not v[0]} for m in ms]
        loss, gain = set(other[0])-set(other[1]), set(other[1])-set(other[0])
        visible = [[], []]
        for side, points in enumerate([loss, gain]):
            for x,y in sorted(points, key=lambda p:(p[1],p[0])):
                v = other[side][x,y]
                nes = es[side][f]['palette'][16+v[1]*4+v[2]]&63
                if v[3]&32 or x<8 or str(nes) not in colors:
                    continue
                rgb = colors[str(nes)]['RGB24']
                if int(ims[side][y,x]) == rgb and int(ims[1-side][y,x]) != rgb:
                    visible[side].append([x,y])
                    key = ['loss', 'gain'][side]
                    if key not in first:
                        oi = v[4]
                        first[key] = dict(frame=f, x=x, y=y, DMA=es[side][f]['dma']['id'], publication=es[side][f]['dma']['publication']['id'], hardware_OAM_index=oi, unchanged_part=es[side][f]['start_hardware'][oi*4:oi*4+4], other_part=es[1-side][f]['start_hardware'][oi*4:oi*4+4], RGB24=[int(im[y,x]) for im in ims], actual_start=es[side][f]['start'], attr=v[3], NEScolor=nes)
                        assert first[key]['unchanged_part'] == first[key]['other_part']
        if loss or gain:
            changes.append(dict(frame=f, modeled_other_losses=len(loss), modeled_other_gains=len(gain), actual_front_RGB_losses=visible[0], actual_front_RGB_gains=visible[1]))
    (a.output/'other-sprite-loss-gain.json').write_text(json.dumps(dict(first=first,frames=changes),indent=2)+'\n')
    # Actual body owner/write sequence for the first visibility regression and
    # the originally reported crowded frame. Keep PPU and DMA IDs distinct.
    owner = []
    writes = [lines(d/'body-writes.jsonl') for d in ds]
    for f in [461,480,586]:
        pair = []
        for side,e in enumerate(es):
            ep = e[f];pub = ep['dma']['publication'];b = pub['body'];tr = pub['transaction'];dm = ep['dma']
            pair.append(dict(actual_start=ep['start'], body_row=ep['body_row']['ppu'], body={k:v for k,v in b.items() if k not in ['world_prefill']}, transaction={k:v for k,v in tr.items() if k!='prefill'}, prefill={k:v for k,v in tr['prefill'].items() if k!='oam'}, publication={k:v for k,v in pub.items() if k not in ['oam','transaction','body']}, DMA={k:dm[k] for k in ['id','ppu','oam_address','mask','writer_bank','writer_callback_pc','writer_instruction','data_writes']}, DMA_complete={k:dm['complete'][k] for k in ['ppu','completed_2004_writes','exact_source','mask']}, body_writes=[w for w in writes[side] if w['transaction']==pub['id']]))
        owner.append(dict(frame=f,baseline=pair[0],candidate=pair[1]))
    (a.output/'actual-owner-traces.json').write_text(json.dumps(owner,indent=2)+'\n')
    # Profile only real paired entry/return records. Do not sum nested costs.
    bus = [lines(d/'oam-bus.jsonl') for d in ds]
    profile = []
    for side,records in enumerate(bus):
        entries = {}; durations = defaultdict(list)
        for r in records:
            if r['kind']=='routine-entry': entries[r['id']]=r
            elif r['kind']=='routine-return':
                en=entries.pop(r['id'])
                assert r['name']==en['name']
                duration=r['ppu']['cpu']-en['ppu']['cpu']
                assert duration==r['inclusive_CPU_cycles']
                durations[r['name']].append(duration)
        profile.append(dict(event_counts=dict(Counter(r['kind'] for r in records)), routine_inclusive_durations=dict(durations)))
    assert profile[0]['event_counts'] == profile[1]['event_counts']
    diffs = {}
    for key,old in profile[0]['routine_inclusive_durations'].items():
        new=profile[1]['routine_inclusive_durations'][key]
        assert len(old)==len(new)
        delta=[y-x for x,y in zip(old,new)]
        diffs[key]=dict(calls=len(delta),min=min(delta),max=max(delta),sum=sum(delta),note='Inclusive measured callback interval; nested intervals must not be added together.')
    (a.output/'cadence-profile.json').write_text(json.dumps(dict(baseline=profile[0],candidate=profile[1],paired_inclusive_deltas=diffs),indent=2)+'\n')
    chosen=[458,459,461,469,480,584,585,586,587,588,589]
    sheet=Image.new('RGB',(768,260*len(chosen)),'#202020');draw=ImageDraw.Draw(sheet)
    for row,f in enumerate(chosen):
        ims=[]
        for side,d in enumerate(ds):
            raw=np.fromfile(d/f'frame-{f:06}.argb',dtype='<u4').reshape(240,256);ims.append(raw)
            im=Image.frombytes('RGBA',(256,240),raw.tobytes(),'raw','BGRA').convert('RGB')
            im.save(a.output/f'{"baseline" if side==0 else "candidate"}-actual-PPU-{f:06}.png')
            sheet.paste(im,(side*256,row*260+20));draw.text((side*256,row*260),f'{"df515" if side==0 else "e11"} actual PPU {f}',fill='white')
        diff=Image.fromarray(np.where((ims[0]!=ims[1])[:,:,None],np.array([255,0,255],dtype=np.uint8),np.array([0,0,0],dtype=np.uint8)))
        sheet.paste(diff,(512,row*260+20));draw.text((512,row*260),'actual RGB change',fill='white')
    sheet.save(a.output/'actual-PPU-selected-wholeframes.png')
    source_bindings={}
    for name in ['metasprite_engine.s','meta_knight.s','parodius_render.s']:
        file=a.source/'src'/name;source_bindings[str(file.resolve())]=sha(file)
    q=dict(passed=False,analysis_complete=True,native_control_passed=True,visibility_proposal_accepted=False,native_worker_released=True,no_native_launch_in_analysis=True,baseline_ROM_sha256=sha(ds[0]/'candidate.nes'),candidate_ROM_sha256=sha(ds[1]/'candidate.nes'),native_receipt_sha256=sha(ds[1]/'cold-proof.json'),pixel_analysis_sha256=sha(a.pixels/'proof.json'),actual_mode=0,actual_variant=1,wall=640,updates=168,publications=130,DMAs=130,matched_actual_PPU_epochs=185,raw_fullframes_per_side=201,other_sprite_actual_loss_frames=sum(bool(r['actual_front_RGB_losses'])for r in changes),other_sprite_actual_gain_frames=sum(bool(r['actual_front_RGB_gains'])for r in changes),other_sprite_actual_lost_pixels=sum(len(r['actual_front_RGB_losses'])for r in changes),other_sprite_actual_gained_pixels=sum(len(r['actual_front_RGB_gains'])for r in changes),first_other_changes=first,cadence_event_counts_exact=True,source_bindings=source_bindings,tool_sha256=sha(Path(__file__)),limits='One exact cold Octopus Easy640 only; hardware8sprites retained. Actual RGB/model has calibrated front-sprite coverage, not exhaustive background/behind-background composition. Other sprite identity beyond native prefill/OAM record is not inferred. Body order is intentionally different, not CHR corruption. No lifecycle/death/area/Buffer2/heavy/DMC or other-mode verdict; no production edits/adoption. Existing negative analyses and native receipts remain immutable.')
    bindings={}
    for root in [*ds,a.pixels,a.output]:
        for file in root.iterdir():
            if file.is_file():bindings[str(file.resolve())]=sha(file)
    bindings.update(source_bindings)
    bindings[str(Path(__file__).resolve())]=sha(Path(__file__))
    manifest=a.output/'manifest.json';manifest.write_text(json.dumps(bindings,indent=2)+'\n')
    q['manifest_sha256']=sha(manifest);q['binding_count']=len(bindings)
    (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:v for k,v in q.items() if k not in ['source_bindings','first_other_changes']},indent=2))


if __name__=='__main__':main()
