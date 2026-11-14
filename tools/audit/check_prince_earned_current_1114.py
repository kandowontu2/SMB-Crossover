"""Current421 genuine earned-mushroom/flower/sword CPU prefix, no overlay."""
import argparse,json
from unittest.mock import patch
import replay_prince_earned_current_1114 as Factory
import check_prince_pipe_usability_1114 as Current


def run(raw):
    text=Factory.controller(raw);model,opening=Current.cold(raw)
    with patch.object(Current.P,'recovery_controller',lambda image:text):
        q=Current.P.route(model,raw,4600,recover=True)
    return dict(metadata=Factory.metadata(raw),opening=opening,proof=q,
        earned_sword=model.ram[2][0x6ee],outputs=0,Mesen=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--metadata',action='store_true');a=p.parse_args()
    raw=Factory.ROM.read_bytes();q=Factory.metadata(raw)if a.metadata else run(raw)
    if not a.metadata:
        q['proof']['events']=(q['proof'].get('events')or[])[-6:]
        q['proof']['flower']={k:v for k,v in(q['proof'].get('flower')or{}).items()if k!='trace'}
    print(json.dumps(q,separators=(',',':')),flush=True)
