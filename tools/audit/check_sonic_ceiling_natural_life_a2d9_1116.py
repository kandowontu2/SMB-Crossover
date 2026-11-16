"""Ordinary a2 Sonic/Super1UP and sustained original ceiling-stop witnesses."""
from pathlib import Path
from unittest.mock import patch
import argparse,inspect,json
import current_sonic_ceiling_complete_a2d9_1116 as F
import check_sonic_hidden_natural_life_f7c9_1116 as Previous

F_SHA='13b1050ecd45ad30d0f6f51f385d3eda6389d9e6d1bfdf11fa302557103571ff'
PREVIOUS_SHA='5250ef4b48e39111eeb169ee93c39666f94a876e1fe72239049a47732671b35e'


def run(raw,form='sonic',limit=1200):
    assert F.H(Path(F.__file__).read_bytes())==F_SHA and F.H(Path(Previous.__file__).read_bytes())==PREVIOUS_SHA
    code=inspect.getsource(Previous.run)
    edits=(
        ('heads=[];births=[];mature=[];collect=[];credit=[];', 'posthead=[];heads=[];births=[];mature=[];collect=[];credit=[];'),
        ("assert mature and collect and sounds[64]and not reset,'Mature physical1UP, realcredit/cue and no reset'",
         "assert collect and collect[0]['actor']['state']>=6 and sounds[64]and not reset,'Actual original admission/credit/cue without reset';assert len(posthead)==8;assert s['ringLives']==s['hurt']==s['sourceStar']==0"),
        ("if name=='OriginalFrame':counts['accepted_original'if self.p&1 else'rejected_original']+=1", """if name=='OriginalFrame':
                    counts['accepted_original'if self.p&1 else'rejected_original']+=1
                    if heads:
                        current=state()
                        if policy.lastJump==479:assert current['vy']>=0,'No held-impulse reassertion before actual later policy jump'
                        if len(posthead)<8:
                            row=dict(state=current,sourceY=list(m.ram[2][0x73:0x76]),JumpTimer=m.ram[2][0x58],
                                JumpVelocity=list(m.ram[2][0x59:0x5b]),HeadPending=m.ram[2][0x122],
                                policy=dict(lastJump=policy.lastJump,hold=policy.hold,clock=policy.clock,phase=policy.phase),C=self.p&1,PC=self.pc,SP=self.sp)
                            assert row['JumpTimer']==0 and current['vy']>=0 and not current['source_flags']&8,'Original Suppress clears08 after ceiling timer cancellation'
                            posthead.append(row)"""),
        ("p.update(actor=a,before=state(),cue32=sounds[32])", """p.update(actor=a,before=state(),cue32=sounds[32])
                        if a is not None:
                            bb=W.address(b,'BoundingBox_UL_Corner');off=(a['slot']+1)*4
                            player=list(m[bb:bb+4]);item=list(m[bb+off:bb+off+4])
                            assert max(player[0],item[0])<=min(player[2],item[2])and max(player[1],item[1])<=min(player[3],item[3]),'Actual native physical overlap'
                            p['boxes']=dict(player=player,item=item)"""),
        ("collect.append(dict(actor=a,before=p['before'],state=s,popup=11,cue32=sounds[32]-p['cue32']))",
         "collect.append(dict(actor=a,before=p['before'],state=s,popup=11,cue32=sounds[32]-p['cue32'],boxes=p['boxes']))"),
        ("assert self.pc!=0xd344,'No helper before fullcold readback'", "assert self.pc not in(0xd344,0xd371),'No new helper before complete cold readback'"),
        ('heads=heads,births=births,mature=mature,', 'first8_posthead_original_returns=posthead,heads=heads,births=births,mature=mature,'),
    )
    for old,new in edits:assert code.count(old)==1,(old,code.count(old));code=code.replace(old,new)
    ns=dict(Previous.__dict__,F=F,F_SHA=F_SHA,__file__=__file__);exec(compile(code,'<same ordinary controls complete native ceiling response>','exec'),ns)
    result=ns['run'](raw,form,limit)
    result.update(original_native_state6_admission=True,old_f7_held_ascent_receipt='902a4915f51f1ebcf78a49e1080cc9e3443baf14ee2c1a018d49aa80ebe2e3b4',
        original_motor5526_exact=True,no_direct_flag_edit=True,derived_source_SHA256=F.H(code.encode()))
    result['receipt_SHA256']=F.H(json.dumps(result,sort_keys=True,separators=(',',':')).encode());return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--form',choices=tuple(F.FORMS),default='sonic');a=p.parse_args()
    def deny(*a,**k):raise AssertionError('Complete ceiling source route attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):out=run(F.load_current_image(),a.form)
    print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)
