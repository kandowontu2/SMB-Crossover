"""Passive late-opponent trace on frozen e418 ordinary controls, no overlay."""
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import json
import current_prince_body_research_ae66_1114 as Current
import check_prince_body_earned_stage_1114 as Base
import replay_prince_body_earned_wait_stage_1114 as Factory


def run():
    raw=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
    current=Current.normalize(raw,kind='bt-service-ae66');frames=Base.Frames.frame
    samples=[];last=None;ticks=0;terminal={}
    def state(m):
        return dict(x=Base.N.get(m,'Player_X_Position')+256*Base.N.get(m,'Player_PageLoc'),
            y=Base.N.get(m,'Player_Y_Position'),hp=m.ram[2][0x6cf],
            sword=m.ram[2][0x6ee],sheath_request=m.ram[2][0x6de],guard_active=m.ram[2][0x6e0],
            guard_uid=m.ram[2][0x61c],player_facing=m.ram[2][0x615],guard_facing=m.ram[2][0x623],
            source_player_y=m.ram[2][0x611]+256*m.ram[2][0x612],
            source_guard_y=m.ram[2][0x61f]+256*m.ram[2][0x620],pose=m.ram[2][0x617],
            action=m.ram[2][0x616],source_pad=m.ram[2][0x76])
    def frame(m,*args,**kwargs):
        nonlocal last,ticks,terminal
        result=frames(m,whole_pass=True);ticks+=1;terminal=state(m)
        key=tuple(terminal[k]for k in('sword','sheath_request','guard_active','guard_uid','pose','player_facing','guard_facing'))
        if ticks>=3900 and key!=last:
            samples.append(dict(Main_pass=ticks,**terminal));last=key
            if len(samples)>40:samples.pop(1)
        return result
    proxy=SimpleNamespace(controller=lambda raw:Factory.controller(raw,brick_runup=True,combat=True),
        metadata=lambda raw:Factory.metadata(raw,brick_runup=True,combat=True),Full=Factory.Frozen.Full)
    with patch.object(Base,'Factory',proxy),patch.object(Base.Frames,'frame',frame):q=Base.run(current,source=True)
    q.update(passive_lost_opponent_trace=samples,actual_terminal_source_fields=terminal,
        scope='Unchanged e418 ordinary controls and game bytes; source CPU negative retained; no importer overlay')
    q['passive_receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q


if __name__=='__main__':print(json.dumps(run(),separators=(',',':')),flush=True)
