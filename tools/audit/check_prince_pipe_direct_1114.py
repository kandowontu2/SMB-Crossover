"""Source replay of held Up+Right / jump+Right on real first-pipe approach."""
import argparse,json
from unittest.mock import patch
import check_prince_pipe_usability_1114 as Base
import replay_prince_pipe_direct_1114 as Factory


def run(raw,*,pad=9,hold=240):
    with patch.object(Base,'Factory',Factory):
        return Base.run(raw,target=1,pad=pad,hold=hold,approach='direct')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--pad',type=int,choices=(9,129,137),default=9)
    p.add_argument('--hold',type=int,default=240);p.add_argument('--metadata',action='store_true')
    a=p.parse_args();raw=Factory.ROM.read_bytes()
    if a.metadata:q=Factory.metadata(raw,pad=a.pad,hold=a.hold)
    else:
        q,_=run(raw,pad=a.pad,hold=a.hold)
        samples=q['observation'].get('samples',[])
        q['observation']['samples']=samples[::8]if isinstance(samples,list)else[]
        q.pop('events',None)
    print(json.dumps(q,separators=(',',':')),flush=True)
