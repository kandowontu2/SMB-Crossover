"""Ten actual award controls and a real mushroom on the private score candidate."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys
from unittest.mock import patch

import compose_native_floatey_score_1114 as C
import replay_gimmick_natural_mushroom_1114 as Previous
import check_mr_gimmick_full11_current_1114 as Original
import check_smb1_alts_full11_1114 as Runner

R,ROM,W,N,PIN=Previous.R,Previous.ROM,Previous.W,Previous.N,C.CANDIDATE
IDENTITIES=Previous.IDENTITIES


def normalize(raw):return Previous.normalize(C.inverse(raw))


class Frozen:
    LuaRuntime=Previous.Frozen.LuaRuntime
    normalize=staticmethod(normalize)


def bindings(raw,key='mr_gimmick'):
    parent=C.inverse(raw);q=deepcopy(Previous.bindings(parent,key));q['sha']=PIN
    for h in q['hooks'].values():
        at=16+h['offset'];assert raw[at:at+len(h['bytes'])]==bytes(h['bytes'])
        if 'bank'in h:
            at=16+h['bank']*8192;h['bank_SHA256']=sha256(raw[at:at+8192]).hexdigest()
    return q


def controller(raw,key='mr_gimmick'):
    parent=C.inverse(raw);old=Previous.controller(parent,key)
    assert sha256(old.encode()).hexdigest()=='41654ed1dac0e6aacf4905619fb68b18cf806c454e267cd6ae54fcae061671e4'
    prefix='local C='+Previous.Base.Stage.Frozen.lua(Previous.bindings(parent,key))+'\n'
    assert old.startswith(prefix)
    text='local C='+Previous.Base.Stage.Frozen.lua(bindings(raw,key))+'\n'+old[len(prefix):]
    Frozen.LuaRuntime().compile(text)
    return text


def metadata(raw,key='mr_gimmick'):
    q=Previous.metadata(C.inverse(raw),key)
    q.update(ROM_SHA256=PIN,controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        score_assertion_unchanged_1000=True,scope='Exact10-byte private native score table; original ordinary mushroom policy and score gate unchanged')
    return q


def cold(raw,key='mr_gimmick'):
    with patch.object(Original,'Factory',sys.modules[__name__]):return Original.cold(raw,key)


def digit_value(m):
    return int(''.join(str(N.get(m,'Player1ScoreDisplay',i))for i in range(6)))


def components(parent,raw):
    outcomes=[];awards=(100,200,400,500,800,1000,2000,4000,5000,8000)
    seeds=(0,90,990,9990,99990,999900,999990,123456,999999)
    for image,divisor in ((parent,10),(raw,1)):
        b=dict(W.Symbols.bundle(),raw=image);m=N.fresh(b);cases=0
        for seed in seeds:
            for control in range(13):
                for p in (0x20,0x31,0x69,0xe5):
                    N.put(m,OperMode=1,CurrentPlayer=0,SelectedCharacter=0,NumberofLives=2,
                        FloateyNum_Control=control,FloateyNum_Timer=0x2b,
                        VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0,Square2SoundQueue=0)
                    for i,digit in enumerate(f'{seed:06d}'):
                        m[W.address(b,'Player1ScoreDisplay')+i]=int(digit)
                        m[W.address(b,'DigitModifier')+i]=0
                    result=N.invoke(m,'FloateyNumbersCore',x=0,p=p)
                    amount=awards[control-1]//divisor if 1<=control<=10 else 0
                    assert digit_value(m)==(seed+amount)%1000000,(divisor,control,seed,digit_value(m),amount)
                    assert N.get(m,'NumberofLives')==(3 if control>=11 else 2)
                    if control>=11:assert N.get(m,'Square2SoundQueue')==0x40
                    assert N.get(m,'FloateyNum_Timer')==(0x2b if control==0 else 0x2a)
                    assert result['minimum_SP']>=128
                    cases+=1
        outcomes.append(dict(ROM_SHA256=sha256(image).hexdigest(),cases=cases,
            expected_award_divisor=divisor,all_ten_awards=True,six_digit_carry_and_wrap=True,
            no_popup_and_extra_life_unchanged=True,fixture='Declared component score/timer/actor inputs; not a gameplay seed'))
    return outcomes


def run(parent):
    raw,proposal=C.proposal(parent);component=components(parent,raw)
    with patch.object(Runner,'Factory',sys.modules[__name__]),patch.object(Runner,'cold',cold):
        natural=Runner.run(raw,'mr_gimmick',2400)
    return dict(passed=natural['passed'],proposal=proposal,components=component,natural_mushroom=natural,
        source_game_table_matches='ScoreUpdateDigit:\n  ; Six displayed digits: index3 is hundreds, index2 is thousands.'in(R/'src/game.s').read_text(),
        all_other_bytes_exact=True,outputs=0,Mesen_run=False)


if __name__=='__main__':
    parent=ROM.read_bytes()
    def forbid(*args,**kwargs):raise RuntimeError('Score source checker attempted file or Mesen output')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Runner.Native,'run',forbid):q=run(parent)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    assert q['passed']and q['source_game_table_matches'],'Private score correction remains unqualified'
