"""Attribute the frozen Octopus witness; no native run or game mutation."""
from pathlib import Path
import collections
import json
import struct
from current_roster_compact_11_v1 import ROOT, sha, png
from current326_route_visual_scan_v1 import frame_records

FOLDER=ROOT/'build/verification/compact-326942-octopus-visibility-v1'
BASE=ROOT/'build/verification/compact-326942-octopus-easy-v1'
ROM=ROOT/'build/zelda2_easy_glove.nes'


def pixels(hw,banks,palette,rom,chr_start):
    result=[];patterns={}
    for slot in range(64):
        yy,tile,attr,xx=hw[slot*4:slot*4+4]
        base=((tile&1)<<12)+((tile&254)<<4);p={}
        page=banks[base//1024]
        pair=rom[chr_start+page*1024+base%1024:chr_start+page*1024+base%1024+32]
        assert len(pair)==32;patterns[slot]=dict(page=page,pattern32=pair.hex(),tuple=[yy,tile,attr,xx])
        for dy in range(16):
            sy=15-dy if attr&128 else dy
            address=base+(sy//8)*16+sy%8
            offset=chr_start+banks[address//1024]*1024+address%1024
            assert 0<=offset<offset+8<len(rom)
            for dx in range(8):
                sx=7-dx if attr&64 else dx
                value=((rom[offset]>>(7-sx))&1)|(((rom[offset+8]>>(7-sx))&1)<<1)
                if value and xx+dx<256 and yy+1+dy<240:
                    p[xx+dx,yy+1+dy]=palette[16+(attr&3)*4+value]
        result.append(p)
    return result,patterns


def main():
    target=FOLDER/'body-attribution.json';assert not target.exists()
    ready=json.loads((FOLDER/'ready.json').read_text())
    assert all(sha(Path(p))==h for p,h in ready['bindings'].items())
    assert sha(ROM)==ready['ROM_sha256']=='32694243361bb1366f6fd64c054ea2451f86b2517fc020d9c2b5d66bbf07bfa0'
    rows=[json.loads(s) for s in (FOLDER/'octopus-visibility.jsonl').read_text().splitlines()]
    assert len(rows)==140 and (FOLDER/'octopus-visibility.jsonl').stat().st_size==337397
    native=json.loads((FOLDER/'result.json').read_text());review=json.loads((FOLDER/'review.json').read_text())
    assert native['passed'] and native['frames']==4801 and native['full_frames']==3984
    assert review['independent_replay']==dict(inputs_exact=True,trace_exact=True,PPU_stream_exact=True)
    for name in ['inputs.csv','trace.csv','events.jsonl']:assert (FOLDER/name).read_bytes()==(BASE/name).read_bytes()
    # Read every raw record, retaining only the TWO authorized new replay epochs.
    raw_frames={};frame_meta={}
    for meta,raw in frame_records(FOLDER):
        frame=meta['stamp']['ppu_frame']
        if frame in (3261,3263):raw_frames[frame]=raw;frame_meta[frame]=meta
    assert set(raw_frames)=={3261,3263}
    by=lambda kind:[q for q in rows if q['kind']==kind]
    body_returns={q['body_id']:q for q in by('body-caller-after-return')}
    renderers={q['body_id']:q for q in by('body-native-renderer')}
    publications={q['draw_id']:q for q in by('rotated-draw-rts-entry') if q['data']['matching_owner']}
    dmas={}
    for event in by('dma-complete-before-mask'):
        d=event['data'];transfer=d['dma'];source=bytes.fromhex(transfer['source256']);hw=bytes.fromhex(d['physical256'])
        assert transfer['page']==2 and len(source)==len(hw)==len(transfer['writes'])==256
        assert all(q==dict(oamaddr=i,value=source[i]) for i,q in enumerate(transfer['writes']))
        expected=bytes(v&0xe3 if i%4==2 else v for i,v in enumerate(source))
        assert hw==expected and d['current_source256']==transfer['source256']
        assert event['stamp']['pc']==0xe008 and event['stamp']['pc_bank'] in (125,127)
        assert d['state']['last_2001_bus_value']&24==0
        dmas[transfer['id']]=event
    assert len(dmas)==5
    rom=ROM.read_bytes();assert rom[9]&15==0
    chr_start=16+rom[4]*16384
    frame_results={};models={}
    for frame,dma_id in [(3261,3),(3263,4)]:
        start=next(q for q in by('start-frame') if q['stamp']['ppu_frame']==frame)
        end=next(q for q in by('end-frame-before-route-capture') if q['stamp']['ppu_frame']==frame)
        dma=dmas[dma_id];transfer=dma['data']['dma'];pub=transfer['publication']
        full_draw=publications[pub['draw_id']];body=body_returns[pub['body_id']];render=renderers[pub['body_id']]
        assert body['data']['matching_owner'] and full_draw['data']['matching_owner']
        assert pub['source256']==full_draw['data']['source256']==transfer['source256']==body['data']['source256_after']
        assert body['stamp']['cpu_cycle']<=pub['stamp']['cpu_cycle']<dma['stamp']['cpu_cycle']<start['stamp']['cpu_cycle']<end['stamp']['cpu_cycle']
        assert start['data']['last_dma']==end['data']['last_dma']
        assert start['data']['last_dma']['id']==dma_id
        assert start['data']['physical256']==end['data']['physical256']==dma['data']['physical256']
        assert start['data']['palette32']==end['data']['palette32']
        assert start['data']['state']['chr_banks'][:8]==end['data']['state']['chr_banks'][:8]==dma['data']['state']['chr_banks'][:8]
        assert start['data']['state']['last_2000_bus_value']&32  # Actual 8x16 mode.
        for q in [body,render,full_draw]:
            s=q['data']['state']
            assert all(s[n]==0 for n in ['VvHurt','InjuryTimer','GuestHurtKind','GuestHurtTicks','GuestInvulTicks','GuestHurtVisible','MmDeathFlag','PnBigStage','PnBigTimerHi','PnBigTimerLo','PnMissing','SmFreezeRenderState'])
            assert bytes.fromhex(s['PnFrame'])[0]==74 and s['PnPool']==0 and s['ObjectMetasprite']==233
        rec=render['data']['record'];record=bytes.fromhex(rec['mapped_record'])
        assert rec['pointer_bank']==76 and rec['pointer']==0xc89d and record[0]==28
        assert rom[16+76*8192+(0xc89d&8191):16+76*8192+(0xc89d&8191)+29]==record
        source=bytes.fromhex(body['data']['source256_after']);hw=bytes.fromhex(start['data']['physical256'])
        writes=body['data']['owner']['writes'];assert len(writes)==28
        assert all(w['value']==source[w['offset']] and w['bank']==4 and w['nmi_depth']==0 for w in writes)
        offsets=[w['offset'] for w in writes];assert len(set(offsets))==28
        slots=sorted({o//4 for o in offsets});assert len(slots)==7
        scratch=bytes.fromhex(rec['scratch']);x,y=scratch[4],scratch[6]
        expected=[]
        for i in range(1,len(record),4):
            tile,attr,dy,dx=record[i:i+4]
            expected.append([(y+(dy if dy<128 else dy-256))&255,tile,attr,(x+(dx if dx<128 else dx-256))&255])
        state=render['data']['state'];physical_start=(state['RgOamPlayerStart']+state['RgOamRotation'])&255
        ordered_slots=[((physical_start+i*4)&255)//4 for i in range(7)]
        assert [list(hw[s*4:s*4+4]) for s in ordered_slots]==list(reversed(expected))
        sprite_pixels,patterns=pixels(hw,start['data']['state']['chr_banks'],bytes.fromhex(start['data']['palette32']),rom,chr_start)
        first8={yy:[i for i in range(64) if hw[i*4]+1<=yy<=hw[i*4]+16][:8] for yy in range(240)}
        body_full={};ideal={};actual={}
        for i in slots:
            assert hw[i*4+2]&32==0
            for p,color in sprite_pixels[i].items():body_full.setdefault(p,(i,color))
        for i in range(64):
            for p,color in sprite_pixels[i].items():
                ideal.setdefault(p,(i,color))
                if i in first8[p[1]]:actual.setdefault(p,(i,color))
        visible={p:q for p,q in actual.items() if q[0] in slots}
        missing={p:q for p,q in ideal.items() if q[0] in slots and actual.get(p,(-1,))[0] not in slots}
        covered={p:actual[p] for p in body_full if p in actual and actual[p][0] not in slots}
        assert len(body_full)==218
        models[frame]=dict(visible=visible,missing=missing,actual=actual,ideal=ideal,body_full=body_full,slots=slots,
                           sprites=sprite_pixels,first8=first8,hw=hw,patterns=patterns)
        frame_results[frame]=dict(display_start=start['stamp'],display_end=end['stamp'],
            completed_dma_id=dma_id,completed_dma_stamp=dma['stamp'],source_draw_id=pub['draw_id'],source_draw_stamp=pub['stamp'],
            body_entry=body['data']['owner']['entry'],body_real_caller_return=body['stamp'],owner_matches=True,
            body_pose=74,incidental_last_actor_PnDrawFrame=state['PnDrawFrame'],pool=0,pointer=rec['pointer'],record=record.hex(),
            hurt_injury_invulnerability_Big_missing_freeze_all_zero=True,body_written_parts=7,body_writes=28,physical_body_slots=slots,
            logical_body_start=state['RgOamPlayerStart'],physical_rotation=state['RgOamRotation'],physical_start=physical_start,
            body_span_wraps=physical_start+28>256,body_patterns={i:patterns[i] for i in slots},
            palette32=start['data']['palette32'],sprite_chr_pages=start['data']['state']['chr_banks'][:8],
            complete_body_opaque_positions=len(body_full),body_winners_after_first8=len(visible),
            otherwise_visible_body_positions_excluded_by_first8=len(missing),other_sprite_occluded_body_positions=len(covered),
            per_body_part=[dict(slot=i,opaque=len(sprite_pixels[i]),opaque_admitted_by_first8=sum(i in first8[p[1]] for p in sprite_pixels[i])) for i in slots],
            scanline_first8=[dict(y=yy,eligible=[i for i in range(64) if hw[i*4]+1<=yy<=hw[i*4]+16],first8=first8[yy]) for yy in range(51,86)],
            raw_PPU_record=frame_meta[frame])
    # Derive the actual Mesen RGB colors only from normally displayed,
    # authenticated front-priority BODY pixels in the comparison frame.
    colors={}
    for (x,y),(_,color) in models[3263]['visible'].items():
        rgb=struct.unpack_from('<I',raw_frames[3263],(y*256+x)*4)[0]
        assert color not in colors or colors[color]==rgb;colors[color]=rgb
    assert len(colors)==5
    for frame in [3261,3263]:
        for (x,y),(_,color) in models[frame]['visible'].items():
            assert struct.unpack_from('<I',raw_frames[frame],(y*256+x)*4)[0]==colors[color]
    missing=models[3261]['missing'];different=equal=0
    for (x,y),(_,color) in missing.items():
        expected=colors[color]
        assert struct.unpack_from('<I',raw_frames[3263],(y*256+x)*4)[0]==expected
        if struct.unpack_from('<I',raw_frames[3261],(y*256+x)*4)[0]==expected:equal+=1
        else:different+=1
    assert (len(missing),different,equal)==(153,145,8)
    assert frame_results[3261]['body_span_wraps'] is False
    assert frame_results[3263]['body_winners_after_first8']==218
    assert frame_results[3261]['body_winners_after_first8']==45
    assert frame_results[3261]['other_sprite_occluded_body_positions']==20
    projectile_slots=list(range(50,56));m=models[3261]
    projectile_details=[]
    for group in [projectile_slots[:3],projectile_slots[3:]]:
        p={}
        for slot in group:
            for coord,color in m['sprites'][slot].items():p.setdefault(coord,(slot,color))
        assert len(p)==24
        projectile_details.append(dict(slots=group,patterns={i:m['patterns'][i] for i in group},
            composite_opaque_pixels=len(p),visible_NES_colors=sorted({v[1] for v in p.values()})))
    palette=bytes.fromhex(frame_results[3261]['palette32']);sprpal=[list(palette[17+i*4:20+i*4]) for i in range(4)]
    assert all(not {15,33,48}.issubset(p) for p in sprpal)
    sheet=FOLDER/'body-3261-3263-whole-frames.png';assert not sheet.exists()
    png(sheet,[raw_frames[3261],raw_frames[3263]])
    placements=dict(sheet=str(sheet),sha256=sha(sheet),placements=[dict(frame=f,row=0,column=i,record=frame_meta[f]) for i,f in enumerate([3261,3263])],
        distinct_new_epochs_extracted=2,maximum_with_six_original_route_markers=8)
    place_path=FOLDER/'body-placements.json';place_path.write_text(json.dumps(placements,indent=2)+'\n')
    deps=[FOLDER/n for n in ['ready.json','source-controls.json','run.lua','launch.json','result.json','review.json',
          'inputs.csv','trace.csv','events.jsonl','captures.nesppuv1','captures-index.jsonl','octopus-visibility.jsonl']]
    deps += [BASE/n for n in ['ready.json','result.json','review.json','inputs.csv','trace.csv','events.jsonl']]
    deps += [ROM,ROM.with_suffix('.dbg'),ROM.with_suffix('.lbl'),Path(__file__).resolve(),
        ROOT/'tools/audit/current326_route_visual_scan_v1.py',ROOT/'tools/audit/current_roster_compact_11_v1.py',
        ROOT/'tools/audit/final_inventory_compact_capture_v1.py',ROOT/'src/metasprite_engine.s',ROOT/'src/parodius_render.s',
        ROOT/'src/parodius_adapter.s',sheet,place_path]
    proof=dict(passed=True,attribution='Actual first-eight hardware sprite exclusion of an emitted nonwrapped body; not hurt flash/source hiding/stale pool or missing CHR.',
        ROM_sha256=sha(ROM),original_and_replay_native_pass=True,exact_inputs_trace_events_full3984PPU=True,
        journal_rows=len(rows),journal_bytes=337397,all_five_DMA_epochs_full256_source_write_destination_E3_exact=True,
        all_five_observed_body_and_rotated_draw_owners_match=True,
        initial_truncated_owner_excluded='The first3256 RTS/return has no entry in the bounded window; it is deliberately not a qualified full owner.',
        frames=frame_results,actual_Mesen_body_NES_color_to_RGB=colors,
        missing_body_pixels=153,actual_RGB_confirms_different=145,equal_RGB_ambiguous=8,
        six_earlier_sprites=projectile_details,active_sprite_palettes_visible_colors=sprpal,
        projectile_composite_limit='Each three-part projectile contributes24 source opaque pixels but3 full16px-high hardware entries. Its three visible colors0F/21/30 are not together in any current sprite palette; a one-sprite exact composite is not a data-only change under these palettes.',
        narrow_followup='Prioritize cold source-art/palette consolidation of frame118 projectile, preserving its pixels/actors/state. Two one-part shots would reduce this witnessed maximum12 rectangles/row to8. Palette ownership is a required unresolved design constraint; no patch is qualified here. Reordering the body alone merely reallocates the same hardware loss and repeats held e11/2dc tradeoffs.',
        agent_visual_review=False,placements=placements,bindings={str(p):sha(p) for p in deps},
        limits=['This is one exact pose/scene/epoch pair, not all modes/ships/poses or universal visibility.',
                'Patterns use actual mapper readbacks and exact bound ROM bytes; there is no per-dot pattern-fetch/background trace.',
                'The8 equal-RGB omitted positions are explicitly ambiguous in pixels despite proven physical first-eight exclusion.',
                'No native launch, ROM/source/default/settings edit or additional actor hiding/priority policy was performed.'])
    target.write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(dict(proof=str(target),sha256=sha(target),bindings=len(deps),body_pixels_lost=153,RGB_differences=145,equal_RGB_ambiguous=8,sheet=str(sheet)),indent=2))


if __name__=='__main__':main()
