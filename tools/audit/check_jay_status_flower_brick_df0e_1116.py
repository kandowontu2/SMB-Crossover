"""Ordinary existing large-head brick clearing before the Flower hop."""
from pathlib import Path
from unittest.mock import patch
import argparse,json
import check_jay_status_flower_side_df0e_1116 as Side

J=Side.J
SIDE_SHA='0f57cc75711ac26ac0b83a2997f32c24a695a9f4b40e4f1e98db20ca775d7ca6'
OldText=Side.text


def text():
    assert J.H(Path(Side.__file__).read_bytes())==SIDE_SHA
    s=OldText()
    begin=s.index(" elseif self.phase=='F-side-left'then")
    end=s.index(" elseif self.phase=='target-collect'then",begin)
    s=s[:begin]+r''' elseif self.phase=='F-side-left'then
  bits=(x<1228 and 1 or x>1230 and 2 or 0)|shot
  if x>=1228 and x<=1230 and g then self:change('F-brick-park');bits=0 end
 elseif self.phase=='F-brick-park'then
  bits=shot
  if self.clock-self.at>=8 then self:change('F-brick-head');bits=128|shot end
 elseif self.phase=='F-brick-head'then
  bits=(self.clock-self.at<18 and 128 or 0)|shot
  if self.clock-self.at>=64 and g then self:change('F-brick-hop');self.hold=self.clock+18;bits=129|shot end
 elseif self.phase=='F-brick-hop'then
  bits=1|shot
  if self.clock<self.hold then bits=bits|128 end
  assert(self.clock-self.at<80,'One existing-ability brick hop did not collect Flower')
'''+s[end:]
    return s


def run(raw,limit=1800):
    body=text()
    with patch.object(Side,'text',lambda:body):q=Side.run(raw,limit)
    q.pop('ordinary_side_launch',None)
    q.update(ordinary_brick_route=dict(align_head_x=1228,head_A_updates=18,wait_for_native_brick_lifecycle=64,hop_Right_A_updates=18),
        existing_head_ability_only=True,no_helper_or_terrain_or_physics_edits=True,
        preserved_side_negative='efd26720466c28b72530d7e0fd32ad27feddcd4c6f43f1150e04a9b511d81bb4',
        policy_SHA256=J.H(body.encode()),observer_source_SHA256=J.H(Path(__file__).read_bytes()))
    q['receipt_SHA256']=J.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--limit',type=int,default=1800);a=p.parse_args();assert 100<=a.limit<=2400
    raw=J.load_current_image()
    def deny(*a,**kw):raise AssertionError('Ordinary brick Flower route attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(raw,a.limit)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
