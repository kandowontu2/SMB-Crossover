"""Review one successful candidate discovery/direct replay; no emulator launch."""
from pathlib import Path
from collections import Counter,defaultdict
import argparse,csv,hashlib,json

sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def jsonlines(path):
    with path.open()as f:
        for line in f:yield json.loads(line)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in['route','rom','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();a.output.mkdir(exist_ok=False)
    direct=a.route.parent/(a.route.name+'-direct')
    manifest=json.loads((a.route/'manifest.json').read_text());observer=json.loads((a.route/'shot-observer.json').read_text())
    replay=json.loads((direct/'proof.json').read_text())
    assert manifest['exit']==0 and manifest['result']['cleared']and manifest['result']['deaths']==0 and observer['passed']and replay['passed']
    assert sha(a.rom)==manifest['ROM_sha256']=='b0c152fa0c588a7df28171e1c673a8db31e2769c5e9114768742e328f1134a99'
    raw=a.rom.read_bytes();chr_data=raw[16+128*8192:]
    constructions={};selected=defaultdict(list);event_counts=Counter();admission_types=Counter()
    for r in jsonlines(a.route/'shot-events.jsonl'):
        event_counts[r['kind']]+=1
        if r['kind']=='construction-start':constructions[r['construction']]=r
        elif r['kind']=='admission-finish'and r['selected']:
            selected[r['construction']].append(r);admission_types[r['source']['MmBulletType']]+=1
        elif r['kind']=='admission-finish':assert not r['parts']and not r['ordered_writes']
    assert all(len(v)<=1 for v in selected.values())
    publications={};exposures=Counter();dma_exact=0;releases=0;epochs=Counter();frame_rows=[];witness_count=Counter();top_body=[];source_age_deltas=Counter();slot_missing=[0]*4;max_slot_missing=[0]*4
    cache={}

    def opaque_pixels(tile,attr,row,height,banks,x,mask):
        if attr&128:row=height-1-row
        logical=(tile&1)*4096+(tile&254)*16+(row//8)*16+row%8 if height==16 else (4096 if frame_ctrl&8 else 0)+tile*16+row
        key=(tuple(banks[:8]),logical)
        if key not in cache:
            physical=banks[logical//1024]*1024+logical%1024
            assert 0<=physical and physical+8<len(chr_data),(physical,len(chr_data),banks,logical)
            lo,hi=chr_data[physical],chr_data[physical+8]
            cache[key]=[i for i in range(8)if((lo|hi)>>(7-i))&1]
        return sum(1 for bit in cache[key]if 0<=x+(7-bit if attr&64 else bit)<256 and(mask&4 or x+(7-bit if attr&64 else bit)>=8))

    reference=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py/root-megaman-lowbody-probe-v1/attribution.json')
    assert sha(reference)=='83049a3ea3a60ac33e87d0b27e397a9341976763552839fa495819fc4a953d53'
    original_rows=0
    for finding in json.loads(reference.read_text())['findings']:
        original_oam=bytes.fromhex(finding['actual_physical_OAM'])
        for witness in finding['body_pixel_omission_witnesses']:
            offset=witness['omitted_body_slot']*4
            sy,tile,attr,x=original_oam[offset:offset+4]
            assert opaque_pixels(tile,attr,witness['scanline']-sy-1,16,finding['actual_sprite_CHR_banks'],x,30)==witness['nontransparent_source_pixels']
            original_rows+=1
    assert original_rows==73

    with(a.output/'opaque-row-witnesses.jsonl').open('w')as witnesses,(a.output/'visible-shot-ages.jsonl').open('w')as ages:
        for r in jsonlines(a.route/'shot-epochs.jsonl'):
            epochs[r['kind']]+=1
            if r['kind']=='publication':publications[r['publication']['id']]=r['publication']
            elif r['kind']=='main-release':
                q=r['main'];assert q['release_writer_bank']==126 and q['release_writer_pc']==0x8355;releases+=1
            elif r['kind']=='dma-complete-before-equality':
                q=r['DMA'];assert q['transferred']==256 and len(q['source'])==len(q['hardware'])==256 and q['source']==q['hardware'];dma_exact+=1
            elif r['kind']=='visible-frame':
                frame=r['ppu']['frame'];q=publications.get(r['publication']);frame_ctrl=r['ctrl'];mask=r['mask'];height=16 if frame_ctrl&32 else 8
                assert len(r['hardware'])==256 and len(r['chr'])==12
                sprites=[r['hardware'][i:i+4]for i in range(0,256,4)]
                first8=[[i for i,s in enumerate(sprites)if s[0]+1<=y<=s[0]+height][:8]for y in range(240)]
                demand=max(sum(s[0]+1<=y<=s[0]+height for s in sprites)for y in range(240))
                cg=q.get('construction')if q else None
                if cg:exposures[cg['id']]+=1
                clean=bool(cg and not any(cg['state'][n]for n in['MmDeathFlag','MmSliding','GuestHurtTicks','GuestInvulTicks','InjuryTimer']))
                row_counts=Counter();body=q.get('body')if q else None;shot=cg.get('emitted',[])if cg else []
                emitted=shot[0]if shot else None
                for role,parts in [('body',body.get('parts',[])if body else []),('shot',emitted.get('parts',[])if emitted else [])]:
                    for part in parts:
                        slot=part['slot'];sy,tile,attr,x=part['bytes']
                        if sprites[slot]!=part['bytes']:
                            row_counts[role+'_overwritten_parts']+=1;continue
                        if not mask&16:continue
                        for scan in range(max(0,sy+1),min(240,sy+height+1)):
                            opaque=opaque_pixels(tile,attr,scan-sy-1,height,r['chr'],x,mask)
                            if not opaque:continue
                            if slot in first8[scan]:row_counts[role+'_admitted_opaque_rows']+=1
                            else:
                                row_counts[role+'_omitted_opaque_rows']+=1
                                w=dict(frame=frame,publication=r['publication'],construction=cg['id']if cg else-1,role=role,slot=slot,scanline=scan,tile=tile,x=x,opaque_source_pixels=opaque,first_eight=first8[scan],clean_body_state=clean)
                                witnesses.write(json.dumps(w,separators=(',',':'))+'\n')
                live=r['last_DMA_state']['slots'];encoded_slot=emitted['slot']if emitted else None;encoded_age=emitted['state']['slots'][encoded_slot]['MmBulletAge']if emitted else None
                visible_slot=encoded_slot if row_counts['shot_admitted_opaque_rows']else None
                for slot,s in enumerate(live):
                    slot_missing[slot]=slot_missing[slot]+1 if s['MmBulletType']and visible_slot!=slot else 0
                    max_slot_missing[slot]=max(max_slot_missing[slot],slot_missing[slot])
                if encoded_slot is not None:
                    now=live[encoded_slot];then=emitted['state']['slots'][encoded_slot]
                    if now['MmBulletType']==then['MmBulletType']and now['MmBulletAge']>=encoded_age:source_age_deltas[now['MmBulletAge']-encoded_age]+=1
                ages.write(json.dumps(dict(frame=frame,DMA=r['DMA'],publication=r['publication'],construction=r['construction'],encoded_slot=encoded_slot,encoded_age=encoded_age,opaque_row_admitted_slot=visible_slot,DMA_live_slots=live,rows=dict(row_counts)),separators=(',',':'))+'\n')
                witness_count.update(row_counts)
                if clean:witness_count['clean_body_omitted_opaque_rows']+=row_counts['body_omitted_opaque_rows']
                frame_rows.append(dict(frame=frame,construction=r['construction'],max_scanline_rectangle_demand=demand,clean=clean,**dict(row_counts)))
                if clean and row_counts['body_omitted_opaque_rows']:top_body.append(dict(frame=frame,omitted_rows=row_counts['body_omitted_opaque_rows'],construction=r['construction'],capture=str(direct/'frames'/f'{frame:06d}.png')))
    ordered=sorted(constructions.values(),key=lambda r:r['construction']);windows=0;violations=[];clock_bad=[]
    def key(r):return tuple(r['state'][n]for n in['SelectedCharacter','ProtoVariant','WorldNumber','LevelNumber','AreaPointer'])
    for left,right in zip(ordered,ordered[1:]):
        if key(left)==key(right)and not left['state']['MmDeathFlag']and not right['state']['MmDeathFlag']and right['state']['SsDrawFirst']!=(left['state']['SsDrawFirst']+1)%10:clock_bad.append([left['construction'],right['construction']])
    for i in range(len(ordered)-4):
        rr=ordered[i:i+5]
        if len({key(r)for r in rr})!=1 or any(r['state']['MmDeathFlag']for r in rr):continue
        for slot in range(4):
            if all(r['state']['slots'][slot]['MmBulletType']for r in rr):
                windows+=1
                if not any(any(v['slot']==slot for v in selected[r['construction']])for r in rr):violations.append(dict(start=rr[0]['construction'],slot=slot))
    # Deliberately report failures; no assertion discards physical visibility
    # gaps or source observations merely because the route itself passed.
    render=list(csv.DictReader((a.route/'render.csv').open()))
    live_constructions={r['construction']for r in ordered if any(s['MmBulletType']for s in r['state']['slots'])}
    summaries=dict(native_route_and_independent_replay_passed=True,ROM_sha256=sha(a.rom),route_result=manifest['result'],observer=observer,direct_replay_proof_sha256=sha(direct/'proof.json'),exact_raw256_DMAs=dma_exact,Main_releases=releases,event_counts=dict(event_counts),epoch_counts=dict(epochs),selected_types=dict(admission_types),continuous_live_source_five_construction_windows=windows,source_window_violations=violations,source_phase_discontinuities=clock_bad,source_constructions=len(constructions),source_constructions_without_observed_visible_exposure=sum(exposures[i]==0 for i in constructions),live_source_constructions_without_observed_visible_exposure=sum(exposures[i]==0 for i in live_constructions),visible_frames=len(frame_rows),visible_frames_rectangle_demand_over8=sum(r['max_scanline_rectangle_demand']>8 for r in frame_rows),opaque_row_totals=dict(witness_count),maximum_observed_consecutive_frames_live_slot_without_admitted_opaque_encoded_shot=max_slot_missing,matching_type_DMA_age_minus_encoded_age_histogram=dict(source_age_deltas),worst_clean_body_frames=sorted(top_body,key=lambda r:r['omitted_rows'],reverse=True)[:12],render_rows=len(render),render_rows_without_new_DMA=sum(int(r['dmaCount'])==0 for r in render),original_opaque_row_decoder_oracle_cases=original_rows,original_attribution_sha256=sha(reference),matched_baseline_no_harm_claim=False,physical_fairness_bound_claim=False,limits='Actual candidate-only route. Opaque rows mean nontransparent CHR source rows omitted/admitted by exact first8 sprite selection; admitted rows may still be occluded by background/earlier pixels. EndFrame CHR snapshots are used, no universal midscanline CHR proof. Live-slot frame gaps use literal latest-DMA states, not unique projectile identities; offscreen/clipped/reused/dead slots can contribute. No all-ability/charge/death/facings coverage or matched performance guarantee.',checker_sha256=sha(__file__))
    (a.output/'proof.json').write_text(json.dumps(summaries,indent=2)+'\n')
    (a.output/'frame-summary.json').write_text(json.dumps(frame_rows,separators=(',',':'))+'\n')
    print(json.dumps({k:summaries[k]for k in['native_route_and_independent_replay_passed','exact_raw256_DMAs','source_constructions','continuous_live_source_five_construction_windows','source_window_violations','visible_frames','opaque_row_totals','maximum_observed_consecutive_frames_live_slot_without_admitted_opaque_encoded_shot','worst_clean_body_frames']},indent=2))


if __name__=='__main__':main()
