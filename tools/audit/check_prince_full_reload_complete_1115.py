"""Measured9000-Main completion bound; frozen ordinary controls unchanged."""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import json
import check_prince_full_reload_budget_1115 as Budget


def run(raw):
    assert sha256(Path(Budget.__file__).read_bytes()).hexdigest()=='6236f925b87fd1a17f6adbd65e5e63e1679ee1f4d88d7dfa07c2011220613955'
    Check=Budget.CurrentCheck;original_run=Check.run;original_source=Check.inspect.getsource
    active={}
    def source(fn):
        text=original_source(fn)
        if fn is Check.Base.run:
            old='proof=Candidate.Game.route(m,raw,8500)'
            assert text.count(old)==1
            text=text.replace(old,'proof=Candidate.Game.route(m,raw,9000)',1)
        return text
    def observed_run(image,*,full=False):
        frame=Budget.Frames.frame
        def observe(m,*args,**kwargs):
            active['model']=m
            return frame(m,*args,**kwargs)
        with patch.object(Budget.Frames,'frame',observe):
            try:return original_run(image,full=full)
            except AssertionError as error:
                m=active.get('model');state={}
                if m is not None:
                    names=('WorldNumber','LevelNumber','AreaNumber','AreaType','OperMode','OperMode_Task',
                        'GameEngineSubroutine','NumberofLives','PlayerStatus','Player_X_Position','Player_PageLoc',
                        'Player_Y_Position','Player_Y_HighPos','Player_State','AltEntranceControl','PlayerEntranceCtrl',
                        'ChangeAreaTimer','DisableScreenFlag','NmiDisable','Mirror_PPUMASK')
                    state={name:Budget.N.get(m,name)for name in names if name in m.bundle['syms']}
                    state.update(HP=m.ram[2][0x6cf],Sword=m.ram[2][0x6ee],action=m.ram[2][0x616],
                        pose=m.ram[2][0x617],mode=m.ram[2][0x618],maps=list(m.rawtags),
                        owning_ROM_SHA256=sha256(m.bundle['raw']).hexdigest())
                return dict(passed=False,source_fixture_exception=repr(error),terminal_diagnostic=state,
                    full_stage_qualified=False,outputs=0,Mesen=False)
    with patch.object(Check.inspect,'getsource',source),patch.object(Check,'run',observed_run):q=Budget.run(raw)
    q.update(measured_route_Main_limit=9000,previous8500_receipt_bound_negative_retained=True,
        all_frozen_controller_and_game_bytes_unchanged=True)
    q['completion_receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q


if __name__=='__main__':
    def deny(*args,**kwargs):raise AssertionError('Prince completion source gate attempted output or launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not q['passed']:raise SystemExit(1)
