"""Exactf11 ordinary DK source; optional genuine-input delayed-poll fixture."""
import argparse
import json
from pathlib import Path
from unittest.mock import patch

import replay_dk_full11_latched_current_1114 as Factory
import check_smb1_alts_full11_1114 as Runner
import check_shared_world_sprite_images_1114 as Cold


def run(raw,*,delayed_polls=False,baseline=False):
    selected=Factory.Previous if baseline else Factory
    N=Factory.N;arena=[];injection=dict(started=False,remaining=0,skipped=[],poll_events=0)
    def cold(image,key):
        with patch.object(Cold,'Factory',selected):m=Cold.cold(image,key)
        arena.append(m);return m
    original_runtime=Runner.LuaRuntime
    class Runtime:
        def __init__(self,*args,**kwargs):self.inner=original_runtime(*args,**kwargs)
        def __getattr__(self,name):return getattr(self.inner,name)
        def execute(self,text):
            api=self.inner.globals().emu;register=api.addEventCallback
            def add(fn,kind):
                if kind!=0:return register(fn,kind)
                def poll():
                    injection['poll_events']+=1;m=arena[0]
                    x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc')
                    if not injection['started']and 1437<=x<=1458 and N.get(m,'Player_Y_Position')==176 and N.get(m,'Player_State')==0:
                        injection['started']=True;injection['remaining']=2
                    if injection['remaining']:
                        injection['remaining']-=1
                        injection['skipped'].append(dict(event=injection['poll_events'],x=x,
                            y=N.get(m,'Player_Y_Position'),state=N.get(m,'Player_State'),
                            SavedJoypadBits=N.get(m,'SavedJoypadBits'),A_B_Buttons=N.get(m,'A_B_Buttons'),
                            PreviousA_B_Buttons=N.get(m,'PreviousA_B_Buttons'),DkPrevious=N.get(m,'DkPrevious')))
                        return
                    fn()
                return register(poll,kind)
            api.addEventCallback=add
            return self.inner.execute(text)
    with patch.object(Runner,'Factory',selected),patch.object(Runner,'cold',cold):
        if delayed_polls:
            with patch.object(Runner,'LuaRuntime',Runtime):q=Runner.run(raw,'donkey_kong',9000)
        else:q=Runner.run(raw,'donkey_kong',9000)
    q['delayed_input_poll_fixture']=dict(enabled=delayed_polls,**injection,
        scope='Two normal controller delivery callbacks omitted at actual grounded launch; all CPU/NMI scheduler and game state remain unseeded')
    if delayed_polls:assert injection['started']and len(injection['skipped'])==2
    return q


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--delayed-polls',action='store_true');p.add_argument('--baseline',action='store_true');a=p.parse_args()
    raw=Factory.ROM.read_bytes()
    def forbid(*args,**kwargs):raise RuntimeError('DK latched checker attempted files/Mesen')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Runner.Native,'run',forbid):
        q=run(raw,delayed_polls=a.delayed_polls,baseline=a.baseline)
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not a.baseline:assert q['passed'],'DK actual admission latch remains source-unqualified'
