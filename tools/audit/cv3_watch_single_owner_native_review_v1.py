"""Offline native watch witness reparse; no emulator, PNG generation or mutation."""
from pathlib import Path
import csv,hashlib,json
from check_tmnt_audio_fallback_oc import qualified
R=Path(__file__).resolve().parents[2];B=R/'build';P=B/'current-9a1b-grant-earned-hard-v2';N=P/'native'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 out=P/'watch-native-offline-reparse.json';assert not out.exists()
 ready=json.loads((P/'prepared-not-run.json').read_text());assert all(sha(x['path'])==x['sha256']for x in ready['bindings'])
 result=json.loads((N/'result.json').read_text());assert result['passed']and result['ROM_sha256']==ready['ROM_sha256']=='9a1b68c0a26ea86ff8c4712af66b8de8cd5ed2de13c74db1bfaf15eb9e2ba333'
 w=next(c for c in result['cases']if c['name']=='use-watch');rows=list(csv.DictReader((N/'earned-components.csv').open(newline='')));cfg=json.loads((P/'config.json').read_text())
 events=lambda name:[x for x in rows if x['event']==name]
 birth,ticks,old,zero=events('actual-watch-birth-180'),events('actual-watch-one-tick'),events('watch-rmw-old-value'),events('watch-zero-same-update-NPC-resume')
 assert len(birth)==len(zero)==1 and len(ticks)==len(old)==180
 assert[int(x['value'])for x in ticks]==list(range(179,-1,-1))and[int(x['value'])for x in old]==list(range(180,0,-1))
 assert[int(x['update'])for x in ticks]==list(range(w['watch_birth_update']+1,w['watch_birth_update']+181))
 for a,b in zip(old,ticks):assert int(a['cycle'])+1==int(b['cycle'])and a['update']==b['update'],'Real NMOS old-value/write1cycle pair retained'
 assert all(int(x['bank'])==cfg['watch_tick_store']['banks'][0]and int(x['pc'])==cfg['watch_tick_store']['pc']+3 for x in ticks+old)
 assert int(birth[0]['bank'])==cfg['watch_birth_store']['banks'][0]and int(birth[0]['pc'])==cfg['watch_birth_store']['pc']+3
 assert int(zero[0]['update'])==w['watch_zero_update']==w['watch_birth_update']+180
 update_rows=[x for x in rows if x['event']=='update'and x['phase']=='use'and x['case']=='8']
 assert len(update_rows)==321 and[int(x['age'])for x in update_rows]==list(range(321))
 assert w['watch_ticks']==180 and w['watch_npc']=='185:0:184:0:0'and w['watch_resumed_npc']=='184:0:184:128:0'and w['debits']==5 and w['heart_before']==23 and w['hearts_after']==18
 assert len(result['cases'])==12 and result['screenshots']==8 and result['updates']==1845 and result['wall']==2219 and result['complete256_DMAs']==2188
 qo,qn=qualified(B/'mega_proto_body_palette_9ea.nes'),qualified(B/'cv3_watch_single_owner.nes');moved={str(k):[v,qn.get(k)]for k,v in qo.items()if qn.get(k)!=v};assert not moved,moved
 imgs=list(N.glob('*.png'));assert len(imgs)==8
 summary=dict(passed=True,offline_reparse_only=True,native_ROM_sha256=result['ROM_sha256'],native_result=result,
 watch=dict(positive_end_states_including_birth=180,birth=birth[0],decrement_rows=180,ordered_values_exact_179_to0=True,old_value_RMW_rows=180,ordered_old_values_exact_180_to1=True,RMW_write_pairs_one_CPU_cycle_apart=True,one_decrement_per_actual_complete_update=True,decrement_owner=cfg['watch_tick_store'],first_decrement=ticks[0],last_decrement=ticks[-1],zero_resume=zero[0],birth_update=1043,zero_resume_update=1223,frozen_NPC_tuple=w['watch_npc'],resumed_NPC_tuple=w['watch_resumed_npc'],tuple_order=['X','page','Y','Xmovefraction','Ymovefraction']),
 genuine_qualified_labels=dict(old_count=len(qo),new_count=len(qn),all_previous_labels_equates_and_macro_symbols_exact=True,moved=moved,new_genuine_loop_label='Cv3FreezeTick::FrozenActors'),
 source_Gate_hardware_scope='Native unmodified4058B guard asserts each actual256-byte DMA/readback, real renderingoff/enable deadline, fixed-alias NMI/IRQ/SP/5SMC/banks and CHR hardware. Result counters attest native guard execution; raw256-byte DMA transfers are not individually serialized for independent offline reparse.',
 health_scope='D0 collected at full64HP and stayed64; no actual deficit healing claim. Newly requested deficit profiles will be separately versioned.',
 retained_offline_first_assertion='First unbound offline parser expected320 watch update CSVrows; actual321 include component age0 plus1..320. Corrected parser preserves all original CSV/result bytes and confirms exact0..320 sequence. This is observer-age accounting, not native/gameplay failure.',
 limits='NPC per-update/subpixel equality was asserted in native Lua. CSV independently serializes birth/ticks/zero-resume; result retains frozen/resumed tuples, not every per-update tuple. No waveform, natural emergence/drop lottery, Easy/facing2, full Hard route or canonical adoption claim.',
 bindings=[dict(path=str(q),bytes=q.stat().st_size,sha256=sha(q))for q in [Path(__file__),P/'prepared-not-run.json',P/'config.json',P/'fixture.lua',P/'run.lua',N/'result.json',N/'earned-components.csv',P/'launch.json',B/'mega_proto_body_palette_9ea.nes',B/'mega_proto_body_palette_9ea.dbg',B/'cv3_watch_single_owner.nes',B/'cv3_watch_single_owner.dbg',*imgs]])
 out.write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(dict(passed=True,path=str(out),sha256=sha(out),CSV_rows=len(rows),previous_qualified_symbols=len(qo),source_ticks=len(ticks))))
if __name__=='__main__':main()
