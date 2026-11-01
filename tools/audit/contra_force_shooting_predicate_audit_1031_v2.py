"""Read-only exact terminal predicate diagnosis for frozen Burns shooting v2."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[2];O=R/'build/contra-force-shooting-predicate-audit-1031-v2'
N=R/'build/contra-force-shooting-native-1031-v2/burns';T=R/'tools/reference/contra_force_shooting_native_1031_v2.lua'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not O.exists();O.mkdir();q=json.loads((N/'capture/result.json').read_text());s=T.read_text();log=(N/'capture/candidate-controller.log').read_text()
 assert 'passed'not in q and 'CF_COLD nil 'in log and 'FAIL'not in log
 assert q['frames']==1047 and q['earned']['original_impact_verified']and q['earned']['post_kind']==6
 checks=dict(completed_Main=q['main_updates']>=200,source_Main=q['source_Main']==q['main_updates'],source_body=q['source_body_steps']==q['main_updates'],vectors=q['vector_guards']>60,construct=q['source_construct']==1,earned=bool(q['earned']),original_impact=q['earned']['original_impact_verified'],native_defeat=q['native_defeats']==1,native_score=q['native_score_calls']==1,source_impact=q['source_impact_calls']==1,source_commit=q['source_impact_commits']==1,ground_shot=q['ground_projectile_observations']>0,source_records=q['source_projectile_records']>0,earned_image=bool(q['rendered'].get('earned')),body_pixels=q['body_checks']>=20,native_enemy_DMA=q['native_enemy_DMAS']>=4,native_enemy_pixels=q['native_enemy_pixel_frames']>=4,stale_avoidance_jump_image=bool(q['rendered'].get('jump')),epochs=q['epochs']>0,authentication=q['auth_A2_entries']>0)
 assert [n for n,v in checks.items()if not v]==['stale_avoidance_jump_image']
 assert 'and renderedUI.jump and epochs>0'in s and "routePad.a"not in s
 assert 'updates=updates+1;sourceEnd=sourceEnd+1'in (N/'controller.lua').read_text()
 refs=[Path(__file__),T,N/'controller.lua',N/'ready.json']+[p for p in(N/'capture').iterdir()if p.is_file()]
 d=dict(passed=True,observer_only=True,native_pass=False,source_changed=False,ROM=q['ROM_sha256'],retained_native_exit_code=1,known_logged_predicates=checks,
  exact_unmet='renderedUI.jump=nil is an inherited avoidance-image gate. This independent shooting policy has no A input and uses renderedUI.earned.',
  why_terminal_nil='Lua and returns its first falsy operand. Earlier numeric/comparison predicates return booleans, earned and rendered.earned are present tables, and the only missing table value is renderedUI.jump. CF_COLD nil and the omitted passed key agree. No Lua assertion failed.',
  unlogged_prior_fields='sourceEnd and sourceAudio are not in v2 result.json. sourceEnd increments beside updates in the same callback; sourceAudio>0 must have evaluated true to reach a nil rather than false terminal value. No numerical native audio count is fabricated.',
  repair='A separate same-ROM v3 removes only the out-of-scope avoidance-image predicate and exports actual sourceEnd/sourceAudio counters. Original kind6/native score/SFX/body/world/enemy/DMA/cookie/SMC requirements and controller policy remain.',
  relevant_native_metrics={k:q[k]for k in ['main_updates','maximum_worldX','maximum_camera','body_checks','native_enemy_DMAS','native_enemy_pixel_frames','native_defeats','native_score_calls','source_impact_calls','source_impact_commits','vector_guards','earned']},bindings={str(p):sha(p)for p in refs})
 p=O/'diagnosis.json';p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf8',newline='\n');print(json.dumps(dict(path=str(p),sha256=sha(p),passed=True)))
if __name__=='__main__':main()
