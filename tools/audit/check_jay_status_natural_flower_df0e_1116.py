"""Same ordinary V3 heart-to-Flower controls on the leased owningdf0e."""
from pathlib import Path
from unittest.mock import patch
import argparse,inspect,json
import current_jay_status_publication_00bb_1116 as J
import check_jay_natural_fsl_routes_1116 as Base
import jay_natural_fsl_controls_v3_1116 as V3

C=J.C
COMPOSER_SHA='48fe2b7f1b9dd704f04f6118e333aca89f963cc0012bacd7c761ecf886bc2bca'
FACADE_SHA='c7cf5ec1f238fb0d4b0001fb1c43d1507165052bf695776a37101f8da22f607c'
OLD_CHECK_SHA='407f51f1a089a12e31c418af919ae9fb620e790bc2efdb42e6e8b5e5353010f0'
V3_SHA='6746cbe6239e67c08ee6d5cdd9207902bd3b83f86c4d4e1c3fd1be5ef2e58704'


def run(raw,limit=1400):
    for module,pin in((C,COMPOSER_SHA),(J,FACADE_SHA),(Base,OLD_CHECK_SHA),(V3,V3_SHA)):
        assert J.H(Path(module.__file__).read_bytes())==pin
    C.lease();J.bindings(raw);body=V3.text();source=inspect.getsource(Base.run)
    edits=(
        ('metadata91dc_only=J.Frozen.PIN','metadata00bb_only=J.Previous.PIN'),
        ('collected=[];births=[];head=[];attack=[];life=[];sound=Counter();',
         'score_writes=[];collected=[];births=[];head=[];attack=[];life=[];sound=Counter();'),
        ("status=r('PlayerStatus'),star=r('StarInvincibleTimer'),engine=r('GameEngineSubroutine'),",
         "status=r('PlayerStatus'),upgrade_parity=r('JnStars'),effective_tier=r('JnTier'),original_pad=m.ram[2][0x2a],original_previous=m.ram[2][0x2b],source_vy=m.ram[2][0x0f],star=r('StarInvincibleTimer'),engine=r('GameEngineSubroutine'),"),
        ("if kind!='life'or(s['lives']==3 and life and sound[64]):",
         "if kind=='flower'and score_writes and s['score']>=target['before']['score']+1000:"),
        ('credit=dict(Main=counts[\'Main_returns\'],motor=counts[\'motor_returns\'],state=s)',
         "credit=dict(Main=counts['Main_returns'],motor=counts['motor_returns'],state=s,writer=score_writes[0])"),
        ("if kind=='flower':assert a['private']==130 and s['tier']==2 and s['maximum']==4 and 6 in popups and 32 in sound",
         "if kind=='flower':assert a['private']==130 and s['tier']==2 and s['maximum']==4 and N.get(m,'FloateyNum_Control',a['slot'])==6 and 32 in sound and s['weapon']==p['before']['weapon']and s['ammo']==p['before']['ammo']"),
        ("ctx.update(inside=True,PC=self.pc,tag=tag(self.pc),opcode=m[self.pc])",
         "ctx.update(inside=True,PC=self.pc,tag=tag(self.pc),opcode=m[self.pc],X=self.x,SP=self.sp)"),
        ('        return old_write(bus,at,value)',
         """        result=old_write(bus,at,value)
        if bus is m and ctx['inside']and target and score_at<=at<score_at+6 and not score_writes:
            s=state()
            if s['score']>=target['before']['score']+1000:
                i=target['item']['slot']
                score_writes.append(dict(PC=ctx['PC'],tag=ctx['tag'],opcode=ctx['opcode'],X=ctx['X'],SP=ctx['SP'],address=at,value=value,
                    Main=counts['Main_returns'],motor=counts['motor_returns'],actual_score=s['score'],popup=N.get(m,'FloateyNum_Control',i),
                    timer=N.get(m,'FloateyNum_Timer',i),state=s))
        return result"""),
        ('collected=collected,births=births,head=head,attack=attack,life=life,sound=sound,popups=popups,',
         'collected=collected,births=births,head=head,attack=attack,life=life,sound=sound,popups=popups,score_writes=score_writes,'),
    )
    for old,new in edits:assert source.count(old)==1,(old,source.count(old));source=source.replace(old,new)
    class Recipe:
        @staticmethod
        def read_text():return body
        @staticmethod
        def read_bytes():return body.encode()
    namespace=dict(Base.__dict__,J=J,N=J.N,W=J.W,Frames=J.Frames,POLICY=Recipe)
    exec(compile(source,'<actualdf0e Flower credit observer>','exec'),namespace)
    q=namespace['run'](raw,'flower',limit)
    q.update(metadata00bb_only_SHA256=C.PIN,composer_SHA256=COMPOSER_SHA,candidate_facade_SHA256=FACADE_SHA,
        same_frozen_V3_controls=True,V3_module_SHA256=V3_SHA,derived_observer_SHA256=J.H(source.encode()),
        reward_scope='Inherited Mike ownedtier2/health policy; donor Jay weapon/ammo unchanged by Flower. Postpickup original pistol remains usable; no newgun grant.',
        credit_then25_actual_returned_workers_required=True,observer_source_SHA256=J.H(Path(__file__).read_bytes()))
    q['receipt_SHA256']=J.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--limit',type=int,default=1400);a=p.parse_args();assert 100<=a.limit<=2400
    raw=J.load_current_image()
    def deny(*a,**kw):raise AssertionError('Jaydf0e naturalFlower source attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(raw,a.limit)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
