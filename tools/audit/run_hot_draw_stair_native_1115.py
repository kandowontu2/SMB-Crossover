"""Root private full-stage test with the source-qualified stair control successor."""
from pathlib import Path
import argparse,json
import replay_battletoads_stair_progress_1115 as F
import run_hot_draw_private_stage_1115 as Root

Root.F=F
Root.GRANT=F.R/'docs/qa/allocations/hot-draw-bt118-stair-native-1115.json'

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--identity',nargs='+',choices=('rash','zitz'),default=['zitz','rash'])
    p.add_argument('--downloads',action='store_true')
    a=p.parse_args()
    for identity in a.identity:
        q=Root.execute(identity,a.downloads);r=q['receipt']
        out={k:v for k,v in q.items()if k not in('receipt','images','capture_preflight')}
        keep=('passed','reason','Main_entries','Main_returned','physical_frames','full_nonshortcut1_1',
              'next_area_updates','Bt_1_2_steps','Bt_source_steps','minimum_source_HP','terminal',
              'game_state_writes','first_active','menu_events','input_polls','max_x')
        out['receipt']={k:r[k]for k in keep if k in r}
        out['receipt']['checkpoint_tail']=r.get('checkpoints',[])[-12:]
        out.update(identity=identity,actual_Downloads_repeat=a.downloads,new_stair_control=True)
        print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)
        assert q['passed']and r['Main_entries']==r['Main_returned']and not r['game_state_writes']
        assert r['full_nonshortcut1_1']and r['next_area_updates']>=25
        s=r['terminal'];assert s['world']==0 and s['level']==1 and s['engine']==8 and s['state']==0
        assert s['y']==176 and s['source_HP']>0 and s['lives']==2
