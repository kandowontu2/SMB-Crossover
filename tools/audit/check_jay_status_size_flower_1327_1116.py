"""Ordinary retained Flower controls with actual brick/credit/worker evidence."""
from pathlib import Path
from unittest.mock import patch
import argparse,inspect,json
import current_jay_status_size_publication_00bb_1116 as J
import check_jay_status_natural_flower_df0e_1116 as Prior
import check_jay_status_flower_aligned_df0e_1116 as Aligned

C=J.C
COMPOSER_SHA='7f1c0eab5a08a7a7e3fbf922aaff1a1c2b8b7513c9c3bd11ed8eee50d01e8d0c'
FACADE_SHA='ffe06f7b53421b24a07da2918b846a67a3de28469ee7eed2d7e67d42816bf8f3'
PRIOR_SHA='99c8ee8b336da8a441fc11c7c1de971419ed20792051803cbc2737e48300e874'
ALIGNED_SHA='681664c956674a150805888ed55e71bcb7a3a6bb00d6f48a9d3fdcae28c4907b'


def text():
    assert J.H(Path(Aligned.__file__).read_bytes())==ALIGNED_SHA
    return Aligned.text()


def enhance(source):
    edits=[
        ('collected=[];births=[];head=[];attack=[];life=[];sound=Counter();',
         'brick=[];noise=[];brick_cells=[];collected=[];births=[];head=[];attack=[];life=[];sound=Counter();'),
        ("status=r('PlayerStatus'),star=r('StarInvincibleTimer')", "size=r('PlayerSize'),status=r('PlayerStatus'),star=r('StarInvincibleTimer')"),
        ("old_write=type(m).__setitem__;first_birth=set();private_returns=[];last_phase=None", """brick_hooks={}
    for name in('BrickShatter','SpawnBrickChunks'):
        pc=W.address(m.bundle,name);at=W.location(m.bundle,name);t=((at-16)//8192)|128
        points[t,pc]=name;brick_hooks[name]=dict(PC=pc,tag=t,file=at,first32=raw[at:at+32].hex())
    old_write=type(m).__setitem__;first_birth=set();private_returns=[];last_phase=None"""),
        ('s=state();aa=actors()', """s=state();aa=actors()
        for cell in brick_cells:
            if cell['erased_at_Main']is None and m[cell['address']]==0:cell['erased_at_Main']=counts['Main_returns']"""),
        ("elif name=='JnCollectPickup':private_returns.append", """elif name in('BrickShatter','SpawnBrickChunks'):
                    i=p['index'];r=lambda field,slot=i:N.get(m,field,slot)
                    brick.append(dict(name=name,PC=p['entry_PC'],tag=p['entry_tag'],SP=p['entry_SP'],index=i,
                        before=p['before'],after=state(),Main=counts['Main_returns'],
                        chunk=dict(state=r('Block_State'),replace=r('Block_RepFlag'),metasprite=r('BlockMetasprite'),
                            vx=r('Block_X_Speed'),vy=r('Block_Y_Speed'),vy2=r('Block_Y_Speed',i+2),
                            x=r('Block_X_Position')+256*r('Block_PageLoc'),y=r('Block_Y_Position'),y2=r('Block_Y_Position',i+2))))
                elif name=='JnCollectPickup':private_returns.append"""),
        ("if len(head)<8:head.append(dict(tile=self.a,player=state()))", """if len(head)<16:head.append(dict(tile=self.a,player=state()))
                    if self.a==0x51:
                        p6,p7,r2=(W.address(m.bundle,n)for n in('R6','R7','R2'))
                        address=(m[p6]+256*m[p7]+m[r2])&65535
                        if len(brick_cells)<8 and all(c['address']!=address for c in brick_cells):
                            brick_cells.append(dict(address=address,before=m[address],head_Main=counts['Main_returns'],player=state(),erased_at_Main=None))"""),
        ("if name=='HandlePowerUpCollision':p.update(actor=actor(self.x),before=state())", """if name=='HandlePowerUpCollision':p.update(actor=actor(self.x),before=state())
                    if name in('BrickShatter','SpawnBrickChunks'):
                        assert len(brick)<8,'Bounded actual brick observations'
                        p.update(index=self.x,before=state(),entry_PC=self.pc,entry_tag=tag(self.pc),entry_SP=self.sp)"""),
        ("if at==fields['Square2SoundQueue']and value in(32,64):sound[value]+=1", """if at==fields['Square2SoundQueue']and value in(32,64):sound[value]+=1
            if at==W.address(m.bundle,'NoiseSoundQueue')and value&1 and len(noise)<8:
                noise.append(dict(PC=ctx['PC'],tag=ctx['tag'],opcode=ctx['opcode'],value=value,Main=counts['Main_returns'],motor=counts['motor_returns']))"""),
        ("'JnCollectPickup','JayCaptureAmmoDefeat'):", "'JnCollectPickup','JayCaptureAmmoDefeat','BrickShatter','SpawnBrickChunks'):"),
        ('original_motor_return_PC=q[\'motion_callsite_PC\']+11,attack_capture_PC=attack_pc,',
         "actual_brick=brick,brick_noise=noise,brick_cells=brick_cells,brick_hooks=brick_hooks,original_motor_return_PC=q['motion_callsite_PC']+11,attack_capture_PC=attack_pc,"),
    ]
    for old,new in edits:
        assert source.count(old)==1,(old,source.count(old));source=source.replace(old,new)
    return source


def run(raw,limit=1800):
    assert J.H(raw)==J.PIN and J.H(Path(Prior.__file__).read_bytes())==PRIOR_SHA
    body=text();source=inspect.getsource(Prior.run)
    namespace=dict(Prior.__dict__,J=J,C=C,COMPOSER_SHA=COMPOSER_SHA,FACADE_SHA=FACADE_SHA)
    exec(compile(source,'<1327 existing Flower reward and credit gates>','exec'),namespace)
    original=inspect.getsource
    def observed(obj):return enhance(original(obj))if obj is Prior.Base.run else original(obj)
    with patch.object(Prior.V3,'text',lambda:body),patch.object(inspect,'getsource',observed):q=namespace['run'](raw,limit)
    if q['passed']:
        chunks=[r for r in q['actual_brick']if r['name']=='SpawnBrickChunks']
        assert chunks and any((r['chunk']['vx'],r['chunk']['vy'],r['chunk']['vy2'])==(240,250,252)for r in chunks)
        assert q['brick_noise']and any(c['before']==0x51 and c['erased_at_Main']is not None for c in q['brick_cells'])
        assert any(c['player']['size']==0 and c['player']['status']==1 for c in q['brick_cells'])
        assert q['credit']and q['motor']>=q['credit']['motor']+25 and q['score_writes']
    q.update(same_frozen_V3_controls=False,unchanged_V3_prefix_until_mature_Flower=True,
        retained_aligned_policy_SHA256=J.H(body.encode()),retained_aligned_module_SHA256=ALIGNED_SHA,
        inherited_reward_and_original_weapon_policy=True,brick_and_size_original_response_required=True,
        source_SHA256=J.H(Path(__file__).read_bytes()))
    q['receipt_SHA256']=J.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--limit',type=int,default=1800);a=p.parse_args();assert 100<=a.limit<=2400
    raw=J.load_current_image()
    def deny(*a,**kw):raise AssertionError('Jay1327 Flower attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(raw,a.limit)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
