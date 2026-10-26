"""Independently correlate the single731 ownership capture; never rerun it."""
from pathlib import Path
import argparse
import collections
import hashlib
import json

from check_tmnt_render_oa import address, location
from link_pit_rygar_sophia_audit_cpu import scoped_load

D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
PACKET=D/'mm-proto-publication-ownership-v1/prepare-v2'
BASELINE=D/'root-presentation450-731-v1'
GAME=D/'mm-proto-clean-menu-candidates-v1/clean-menu-irq'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def raw(z):
    return bytes(z[str(i)] for i in range(1,257))


def put(p,z):
    Path(p).write_text(json.dumps(z,indent=2)+'\n')


def active(s):
    return s['OperMode']==1 and s['OperMode_Task']==3 and s['GameEngineSubroutine']==8


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    receipt=json.loads((PACKET/'native-receipt.json').read_text())
    assert receipt['passed'] and receipt['launches']==1 and receipt['retries']==0 and receipt['worker_released']
    assert receipt['grant_sha256']=='0505ced393f3237203d96254737fba81c8b94560d6f43e6f0a5eb144bf3e2e28'
    exact={}
    for name in ['prefix.csv','direct-index.csv','direct.argb','timing.jsonl','result.json']:
        x,y=[p/name for p in [BASELINE,PACKET]]
        assert x.read_bytes()==y.read_bytes(),name
        exact[name]=dict(bytes=y.stat().st_size,sha256=sha(y),byte_exact=True)
    rows=[json.loads(s) for s in (PACKET/'ownership.jsonl').read_text().splitlines()]
    old=[json.loads(s) for s in (PACKET/'timing.jsonl').read_text().splitlines()]
    hardware=[q['DMA'] for q in old if q['kind']=='DMA-complete']
    b=scoped_load(GAME/'candidate.nes')
    counts=collections.Counter(q['kind'] for q in rows)
    assert counts['source-write']==6680 and counts['Main-release']==432
    assert counts['DrawAll-roster-ready']==51 and counts['DMA-source-owner']==402
    initial=rows[0];assert initial['kind']=='initial-source'
    image=bytearray(raw(initial['source']));owners={};source_epoch=0
    release_by_id={};roster_by_id={};main_begin={};live_main=None;live_draw=None
    nmi=None;pending=None;dm=[];nm=[];writers=collections.Counter();store_bindings={}
    outside=[];life=[];releases=[];rosters=[]
    for q in rows:
        kind=q['kind']
        if kind=='source-write':
            source_epoch+=1;assert q['id']==source_epoch
            at=q['address']-0x200;assert 0<=at<256
            image[at]=q['value'];owners[str(at+1)]=source_epoch
            assert q['main']==(live_main if live_main is not None else -1)
            assert q['construction']==(live_draw if live_draw is not None else -1)
            writers[(q['callback_bank'],q['callback_pc'],q['construction']!=-1)]+=1
            pc,bank=q['callback_pc'],q['callback_bank']
            # Bind the literal nextPC to an actual three-byte absolute/indexed
            # STA ending there. No claim about unobserved call stacks follows.
            assert pc>=0x8003 and (pc-3)//8192==pc//8192
            off=16+bank*8192+(pc-3)%8192
            code=b['raw'][off:off+3]
            assert code[0] in [0x8d,0x99,0x9d] and 0x200<=code[1]+256*code[2]<0x300,(q,code.hex())
            store_bindings[(bank,pc)]=dict(bank=bank,callback_nextPC=pc,instruction_start=pc-3,bytes=code.hex(),base_operand=code[1]+256*code[2],interpretation='Bound actual absolute/indexed STA ending at the literal callbackPC; addressing index/caller stack was not separately logged.')
            if q['construction']==-1:outside.append(q)
        elif kind=='Main-begin':
            x=q['main'];assert live_main is None
            live_main=x['id'];main_begin[x['id']]=q
        elif kind=='DrawAll-begin':
            x=q['construction'];assert live_draw is None and x['main']==live_main
            live_draw=x['id']
        elif kind=='DrawAll-roster-ready':
            x=q['construction'];assert x['id']==live_draw and raw(x['source'])==bytes(image) and x['last_write']==source_epoch
            assert x['main']==live_main
            roster_by_id[x['id']]=x;rosters.append(x);live_draw=None
        elif kind=='Main-release':
            x=q['main'];assert x['id']==live_main and raw(x['source'])==bytes(image) and x['mirror_exact']
            assert x['last_write']==source_epoch and x['writer_pc']==0x8355 and x['writer_bank']==126
            assert x['state']['NmiDisable']==255  # read callback observes pre-store image; write event records value0
            release_by_id[x['id']]=x;releases.append(x)
        elif kind=='Main-return':
            assert q['main']==live_main and q['last_release']==live_main
            live_main=None
        elif kind=='NMI-acceptance':
            assert nmi is None and q['depth']==1
            assert q['main']==(live_main if live_main is not None else -1)
            assert q['construction']==(live_draw if live_draw is not None else -1)
            nmi=q|dict(DMA_count=0)
            pc=q['interrupted']['stacked_pc']
            nmi['interrupted_execution_kind']='RAM/SMC; raw converter-bank field is not a PRG bank' if pc<0x8000 else 'ROM'
        elif kind=='DMA-source-owner':
            x=q['DMA'];assert nmi is not None and pending is None
            assert x['page']==2 and x['id']==len(dm)+1
            assert x['source_write']==source_epoch and raw(x['source'])==bytes(image) and x['mirror_exact']
            assert x['last_source_writer_per_byte']==owners
            assert x['callback_pc']==0xe005 and x['callback_bank']==127
            assert x['state']['NmiDisable']==255 and nmi['state']['NmiDisable']==0
            if x.get('last_release'):
                assert raw(x['last_release']['source'])==raw(x['source'])
                assert x['last_release']==release_by_id[x['last_release']['id']]
            if x.get('last_roster'):
                assert x['last_roster']==roster_by_id[x['last_roster']['id']]
            pending=x;nmi['DMA_count']+=1
        elif kind=='DMA-completed-owner':
            assert pending and q['id']==pending['id']
            h=hardware[q['id']-1]
            assert raw(q['hardware'])==raw(pending['source'])==raw(h['source'])==raw(h['hardware'])
            assert q['ppu']==h['complete'] and pending['start']==h['start']
            pending['complete']=q['ppu'];dm.append(pending);pending=None
        elif kind=='NMI-return':
            assert nmi is not None and not pending
            lag=nmi['state']['NmiDisable']>=128
            assert nmi['DMA_count']==(0 if lag else 1)
            nmi['return']=q['ppu'];nmi['lag']=lag;nm.append(nmi);nmi=None
        elif kind=='lifecycle-or-direct-replacement':life.append(q)
    assert nmi is None and pending is None and len(dm)==402 and len(nm)==442
    assert len(rosters)==51 and len(releases)==432 and live_main is None
    put(a.output/'original-observations-exact.json',exact)
    put(a.output/'compiled-source-store-bindings.json',list(store_bindings.values()))
    put(a.output/'outside-DrawAll-source-writers.json',outside)
    put(a.output/'actual-lifecycle-events.json',life)
    per_dma=[];seen_rosters=collections.Counter();post_roster=[];carried=[];stale=[]
    for i,x in enumerate(dm):
        rr=x.get('last_release');draw=x.get('last_roster')
        prior=dm[i-1] if i else None
        row=dict(DMA=x['id'],start=x['start'],complete=x['complete'],active_gameplay=active(x['state']),
                 full_source_sha256=hashlib.sha256(raw(x['source'])).hexdigest(),source_epoch=x['source_write'],
                 Main=rr['id'] if rr else None,Main_draw_count=rr['draws'] if rr else None,
                 Main_release=rr['release'] if rr else None,Roster=draw['id'] if draw else None,
                 Roster_Main=draw['main'] if draw else None,Roster_ready=draw['ppu'] if draw else None,
                 writes_after_Roster=x['source_write']-draw['last_write'] if draw else None,
                 full_latest_Main_source_exact=bool(rr and rr['source']==x['source']),
                 full_latest_Roster_source_exact=bool(draw and draw['source']==x['source']),
                 same_source_epoch_as_prior_DMA=bool(prior and prior['source_write']==x['source_write']),
                 same_full_source_as_prior_DMA=bool(prior and prior['source']==x['source']),
                 live_ordinary=x['state']['ordinary'],live_special=x['state']['special'],
                 Roster_ordinary=draw['state']['ordinary'] if draw else None,
                 Roster_special=draw['state']['special'] if draw else None)
        per_dma.append(row)
        if draw:
            seen_rosters[draw['id']]+=1
            if row['writes_after_Roster']:post_roster.append(row)
            if rr['draws']==0:carried.append(row)
        if row['same_source_epoch_as_prior_DMA'] and row['same_full_source_as_prior_DMA']:stale.append(row)
    put(a.output/'all402-source-Main-DMA-correlations.json',per_dma)
    put(a.output/'actual-no-draw-carry-images.json',carried)
    put(a.output/'all442-NMI-interrupted-owners.json',nm)
    # Observation-only counterfactual: the unimplemented one-byte protocol
    # tags/acks actual source epochs; it does not change any pixels or code.
    proposed=0;phase_for_draw={};phase_for_roster={};acks=[];pending_id=None;drops=[]
    for q in rows:
        kind=q['kind']
        if kind=='lifecycle-or-direct-replacement':proposed=0;pending_id=None
        elif kind=='DrawAll-begin':
            x=q['construction'];phase_for_draw[x['id']]=proposed&1;proposed&=1
        elif kind=='DrawAll-roster-ready':
            x=q['construction'];s=x['state']
            if active(s) and s['SelectedCharacter']==1 and not s['MmDeathFlag'] and s['ObjectMetasprite'] and not s['SprObject_SprAttrib']&128:
                if pending_id is not None:drops.append(pending_id)
                phase_for_roster[x['id']]=phase_for_draw[x['id']];proposed=phase_for_draw[x['id']]|128;pending_id=x['id']
            else:proposed&=1;pending_id=None
        elif kind=='DMA-completed-owner' and proposed&128:
            assert pending_id is not None
            acks.append(dict(DMA=q['id'],Roster=pending_id,phase=proposed&1,completion=q['ppu']))
            proposed^=129;pending_id=None
    assert len(acks)==49 and all(x['phase']!=y['phase'] for x,y in zip(acks,acks[1:]))
    assert pending_id==51 and not drops
    put(a.output/'counterfactual-protocol-source-epoch-only.json',dict(implemented=False,native_priority_changes=False,acknowledged=acks,unconsumed_at_end=pending_id,overwritten_pending_Rosters=drops,limits='Offline replay of a proposed lifecycle protocol on the actual fixed731 observer trace only. The original images did not alternate body/shot priority; no visibility or performance claim.'))
    active_nm=[q for q in nm if active(q['state'])]
    lag=[q for q in nm if q['lag']]
    post=[q for q in lag if q['construction']==-1 and q['main']!=-1 and q['last_roster']!=-1]
    selected=[q for q in nm if q['ppu']['frame'] in [372,384,385,386,387,437,438,444,445,446,448,449,450]]
    put(a.output/'selected-actual-lag-publication-epochs.json',selected)
    summary=dict(passed=True,review_complete=True,native_run=True,game_implementation=False,adopted=False,
                 ROM_sha256=receipt['ROM_sha256'],launches=1,retries=0,worker_released=True,
                 original_five_named_observations_byte_exact=True,all275_actual_PPU_frames_byte_exact=True,
                 original402_full256_hardware_DMA_source_and_destination_exact=True,
                 Main_entries=432,Main_releases=432,source_writes=6680,complete_Rosters=51,
                 source_initial_and_every_logged_write_reconstructed=True,actual_absolute_indexed_STA_sites=len(store_bindings),
                 DMA_with_exact_completed_Main_image=401,bootstrap_DMA_before_first_Main_release=1,
                 no_DrawAll_latest_Main_carry_images=len(carried),post_latest_Roster_source_edits=len(post_roster),
                 actual_stale_source_epoch_DMAs=len(stale),actual_active_gameplay_DMAs=sum(x['active_gameplay'] for x in per_dma),
                 actual_distinct_transferred_Rosters=len(seen_rosters),last_untransferred_Roster=51,
                 eligible_transferred_Rosters=49,first_Roster1_entrance_engine7_is_not_priority_mode=True,
                 Main_release_callback_state_is_pre_store_FF_write_value_is0=True,
                 repeated_Roster_transfers=sum(v-1 for v in seen_rosters.values()),
                 regular_NMI=len(nm)-len(lag),lag_NMI=len(lag),lag_inside_DrawAll=sum(q['construction']!=-1 for q in lag),
                 lag_after_Roster_during_Main=len(post),active_lag_after_Roster_frames=[q['ppu']['frame'] for q in post],
                 actual_lifecycle_events=len(life),direct_writer_outside_DrawAll=len(outside),
                 observed_native_Vine_or_Brick_postdraw_edits=False,
                 protocol_counterfactual_ack_phases_alternate=True,protocol_not_implemented=True,
                 raw_RAM_SMC_stacked_bank_caveat='For stackedPC<8000 the raw observer converter quotient0 is NOT PRGbank0. It is classified RAM/SMC in the additive review, without modifying or masking raw records.',
                 limits='One unchanged731450 MegaEasy menu/start/earlygame diagnostic. No new phase byte/code or body/shot scheduling was active. No death, later area, Proto gameplay, actual prior00fb Main-PC attribution or universal direct-writer closure. Source model/counterfactual demonstrates feasibility on this trace only. Raw pre-existing prototype failures remain held.',
                 checker_sha256=sha(__file__))
    deps={Path(__file__)}|{p for root in [PACKET,BASELINE] for p in root.iterdir() if p.is_file()}
    deps|={GAME/('candidate'+ext) for ext in ['.nes','.dbg','.lbl','.map']}
    deps|={Path(__file__).parent/n for n in ['check_tmnt_render_oa.py','link_pit_rygar_sophia_audit_cpu.py']}
    put(a.output/'bindings.json',{str(p.resolve()):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(deps)})
    put(a.output/'proof.json',summary)
    print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),**summary),indent=2))


if __name__=='__main__':main()
