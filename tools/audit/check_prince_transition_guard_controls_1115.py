"""Ordinary late sword controls using the actual imported opponent's slot."""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import json
import check_prince_transition_model_1115 as Model


def controller(text):
    old='        and(not target or math.abs(x-s.x)<math.abs(target.x-s.x))then target={slot=slot,x=x,y=y}end'
    new='        and(s.x<1800 or slot==(s.guard_uid&127))\n'+old
    assert text.count(old)==1;text=text.replace(old,new,1)
    Model.Frozen.LuaRuntime().compile(text)
    return text


def run(raw):
    samples=[];last=None;count=0;minimum=255
    def observe(m,tick):
        nonlocal last,count,minimum
        s=Model.state(m);minimum=min(minimum,s['hp'])
        if s['x']<1680:return False
        actors=[]
        for slot in range(6):
            flag=Model.N.get(m,'Enemy_Flag',slot)
            if flag:
                actors.append(dict(slot=slot,flag=flag,id=Model.N.get(m,'Enemy_ID',slot),
                    state=Model.N.get(m,'Enemy_State',slot),direction=Model.N.get(m,'Enemy_MovingDir',slot),
                    x=Model.N.get(m,'Enemy_X_Position',slot)+256*Model.N.get(m,'Enemy_PageLoc',slot),
                    y=Model.N.get(m,'Enemy_Y_Position',slot)))
        extra=dict(source_guard_x=int.from_bytes(m.ram[2][0x61d:0x61f],'little'),
            source_player_x=int.from_bytes(m.ram[2][0x60f:0x611],'little'),guard_hp=m.ram[2][0x6d0],
            source_pad=m.ram[2][0x40a],requested_pad=m.controller_pad,actors=actors)
        key=tuple(s.values())+(extra['guard_hp'],extra['source_pad'],extra['requested_pad'])
        if key!=last:
            count+=1;samples.append(dict(Main=tick,**s,**extra));last=key
            if len(samples)>80:samples.pop(16)
        return False
    q=Model.run(raw,full=True,limit=5500,controller_transform=controller,frame_observer=observe)
    q.update(ordinary_control_change='Only x>=1800 target selection: use actual imported guard UID slot, preserve original parry/approach/A attack',
        capped_actual_state_samples=samples,total_changed_state_samples=count,minimum_HP=minimum,
        no_gameplay_seeds=True,no_new_game_bytes=True,native_qualified=False)
    q['guard_control_receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q


if __name__=='__main__':
    def deny(*args,**kwargs):raise AssertionError('Guard control source proof attempted output or launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not q['passed']:raise SystemExit(1)
