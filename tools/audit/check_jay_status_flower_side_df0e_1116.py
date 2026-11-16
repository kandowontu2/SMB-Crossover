"""One ordinary side-launch successor after the preserved under-block negative."""
from pathlib import Path
from unittest.mock import patch
import argparse,inspect,json
import check_jay_status_natural_flower_df0e_1116 as Frozen

J,V3=Frozen.J,Frozen.V3
SOURCE_SHA='99c8ee8b336da8a441fc11c7c1de971419ed20792051803cbc2737e48300e874'
OldText,OldSource=V3.text,inspect.getsource


def text():
    s=OldText()
    edits=(
        (' local shot=enemy and self.clock%12<2 and 64 or 0',
         " local shot=enemy and self.clock%12<2 and 64 or 0\n if self.kind=='flower'and self.phase=='target-collect'and item and item.state>=128 then self:change('F-side-left')end"),
        (" elseif self.phase=='target-collect'then",r""" elseif self.phase=='F-side-left'then
  bits=(x>1184 and 2 or 0)|shot
  if x<=1184 and g then self:change('F-side-turn');bits=0 end
 elseif self.phase=='F-side-turn'then
  bits=1|shot
  if g and s.source_flags&2==0 and s.source_control&0x38==0 then self:change('F-side-approach')end
 elseif self.phase=='F-side-approach'then
  bits=1|shot
  if x>=1200 and g and s.source_control&0x38==0 then
   self:change('F-side-jump');self.hold=self.clock+18;self.side_minY=y;bits=bits|128
  end
 elseif self.phase=='F-side-jump'then
  bits=1|shot
  if self.clock<self.hold then bits=bits|128 end
  self.side_minY=math.min(self.side_minY,y)
  if g and self.clock-self.at>40 then error('One ordinary side jump completed without Flower; minY='..self.side_minY..',x='..x..',box='..table.concat(s.player_box,','))end
  assert(self.clock-self.at<96,'Bounded ordinary Flower side jump minY='..self.side_minY)
 elseif self.phase=='target-collect'then"""),
        ("  if self.clock%12<2 then bits=bits|64 end\n elseif self.phase=='credited'",r"""  if self.clock%12<2 then bits=bits|64 end
  self.attackGapHold=self.attackGapHold or 0
  if x>=1358 and x<1370 and g and not self.lastA then self.attackGapHold=self.clock+14 end
  if self.clock<self.attackGapHold then bits=bits|128 end
 elseif self.phase=='credited'"""),
    )
    for a,b in edits:assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b)
    return s


def run(raw,limit=1800):
    assert J.H(Path(Frozen.__file__).read_bytes())==SOURCE_SHA
    body=text()
    def source(obj):
        s=OldSource(obj)
        if obj is Frozen.Base.run:
            old="weapon=m.ram[2][0x20],ammo=m.ram[2][0xbe],Main=counts['Main_returns'],motor=counts['motor_returns'])"
            new="player_box=[m[W.address(m.bundle,'BoundingBox_UL_Corner')+i]for i in range(4)],weapon=m.ram[2][0x20],ammo=m.ram[2][0xbe],Main=counts['Main_returns'],motor=counts['motor_returns'])"
            assert s.count(old)==1;s=s.replace(old,new)
        return s
    with patch.object(V3,'text',lambda:body),patch.object(inspect,'getsource',source):q=Frozen.run(raw,limit)
    q.update(same_frozen_V3_controls=False,unchanged_V3_prefix_until_mature_Flower=True,
        ordinary_side_launch=dict(left_turn=1184,right_launch=1200,held_A_updates=18),
        postpickup_second_gap='Existing14-update ordinary jump at1358..1370 only if needed to reach a real enemy',
        policy_SHA256=J.H(body.encode()),observer_source_SHA256=J.H(Path(__file__).read_bytes()),preserved_underblock_negative='c05e8231f9c55b058fb93b32b79dc148c7ba38b531b38302d67b21957fa0491f')
    q['receipt_SHA256']=J.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--limit',type=int,default=1800);a=p.parse_args();assert 100<=a.limit<=2400
    raw=J.load_current_image()
    def deny(*a,**kw):raise AssertionError('Ordinary Flower side launch attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(raw,a.limit)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
