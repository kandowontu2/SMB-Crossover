"""Capture genuine earned M/F once; inspect ordinary Flower-tier bubble motion."""
from hashlib import sha256
import json
from unittest.mock import patch
import replay_bub_star_174fa_1115 as S

B,W,N=S.B,S.W,S.N

def state(m,identity=0):
    q=B.state(m);actor=0x42 if identity else 0x2e;oy=8 if identity else 0
    q.update(flags=m.ram[2][actor+2],selector=m.ram[2][actor+3],held=m.ram[2][0x301],cooldown=m.ram[2][actor+8])
    q['bubbles']=[]
    for i in range(15):
        off=0x88+4*i;bo=0x188+8*i
        if not m.ram[2][off]:continue
        dx=((m.ram[2][bo+3]-m.ram[2][0x103+oy]+128)%256)-128
        dy=((m.ram[2][bo]-m.ram[2][0x100+oy]+128)%256)-128
        q['bubbles'].append(dict(slot=i,kind=m.ram[2][off],dx=dx,dy=dy,source=list(m.ram[2][off:off+4])))
    return q

def capture(raw,identity=0):
    saved=[];old=B.cold
    def cold(image,who):
        result=old(image,who);saved.append(result[0]);return result
    with patch.object(B,'cold',cold):q=S.Previous.source_check(raw,identity,stock='flower')
    assert q['passed']and len(saved)==1
    return saved[0],dict(controller_SHA256=q['controller_SHA256'],moves=q['receipt']['source_updates'],terminal=q['receipt']['terminal'])

if __name__=='__main__':
    raw,actual=S.load_current();m,prefix=capture(raw)
    for ticks in range(300):
        s=state(m)
        if s['x']>=1318 and s['Player_Y_Position']==176 and s['selector']in(0,1):break
        assert s['x']<1350 and s['GameEngineSubroutine']==8 and s['NumberofLives']==2
        m.controller_pad=1;B.frame(m,whole_pass=True)
    else:raise AssertionError('Safe ordinary1318 run-up bound')
    for _ in range(2):m.controller_pad=0;B.frame(m,whole_pass=True)
    opening=state(m);rows=[]
    for tick in range(56):
        m.controller_pad=64 if tick<4 else 0
        B.frame(m,whole_pass=True);s=state(m);s['tick']=tick+1;rows.append(s)
        assert s['x']<1350 and s['GameEngineSubroutine']==8 and s['NumberofLives']==2
    result=dict(input_SHA256=actual,executed_SHA256=S.PIN,prefix=prefix,opening=opening,rows=rows[:8]+rows[-24:],ordinary_inputs_only=True,output_files=0)
    text=json.dumps(result,sort_keys=True,separators=(',',':'))
    print('RESULT '+text,flush=True);print('RECEIPT '+sha256(text.encode()).hexdigest(),flush=True)
