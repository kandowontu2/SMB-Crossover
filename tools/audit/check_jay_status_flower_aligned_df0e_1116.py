"""Re-align after the measured original left carry before one Flower hop."""
from pathlib import Path
from unittest.mock import patch
import argparse,json
import check_jay_status_flower_brick_df0e_1116 as Brick

J,Side=Brick.J,Brick.Side
BRICK_SHA='8d35d98ec996f6b2fd3a8f18c3a9f43c8b7df96e1667b12d3f48c5571668add0'
OldText,OldSource=Brick.text,Side.OldSource


def text():
    assert J.H(Path(Brick.__file__).read_bytes())==BRICK_SHA
    s=OldText()
    a="  if self.clock-self.at>=64 and g then self:change('F-brick-hop');self.hold=self.clock+18;bits=129|shot end\n elseif self.phase=='F-brick-hop'then"
    b=r'''  if self.clock-self.at>=64 and g then self:change('F-brick-reset');bits=1|shot end
 elseif self.phase=='F-brick-reset'then
  bits=1|shot
  if x>=1228 and g and s.source_flags&2==0 and s.source_control&0x38==0 then self:change('F-brick-stable');bits=0 end
 elseif self.phase=='F-brick-stable'then
  bits=0
  if self.clock-self.at>=8 and g and s.source_control&0x38==0 then
   self:change('F-brick-hop');self.hold=self.clock+18;self.hop_minY=y;bits=129|shot
  end
 elseif self.phase=='F-brick-hop'then
  if y<self.hop_minY then self.hop_minY=y;self.hop_apex=s end'''
    assert s.count(a)==1;s=s.replace(a,b)
    return s


def run(raw,limit=1800):
    body=text()
    def source(obj):
        s=OldSource(obj)
        if obj is Side.Frozen.Base.run:
            a="original_motor_return_PC=q['motion_callsite_PC']+11,attack_capture_PC=attack_pc,"
            b="hop_minY=policy.hop_minY,hop_apex=({k:v for k,v in policy.hop_apex.items()}if policy.hop_apex is not None else None),"+a
            assert s.count(a)==1;s=s.replace(a,b)
            a="private=r('InvPickup'),owner=r('InvPickupOwner'),contact=r('PlatformCollisionFlag'))"
            b="box=[m[W.address(m.bundle,'EnemyBoundingBoxCoord')+4*i+k]for k in range(4)],"+a
            assert s.count(a)==1;s=s.replace(a,b)
        return s
    with patch.object(Brick,'text',lambda:body),patch.object(Side,'OldSource',source):q=Brick.run(raw,limit)
    q.update(ordinary_postbrick_alignment='WalkRight to1228 facingRight, wait8 releasedA, then existing18A hop',
        preserved_misaligned_brick_negative='4e5f3f0b1684da93c9e5455738ccf767ec46368dba27e9c43ce0775e41321431',
        policy_SHA256=J.H(body.encode()),observer_source_SHA256=J.H(Path(__file__).read_bytes()))
    q['receipt_SHA256']=J.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--limit',type=int,default=1800);a=p.parse_args();assert 100<=a.limit<=2400
    raw=J.load_current_image()
    def deny(*a,**kw):raise AssertionError('Aligned ordinary Flower route attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(raw,a.limit)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
