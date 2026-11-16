"""Separate ordinary-control successor; original failed policy stays frozen."""
from pathlib import Path
from unittest.mock import patch
import argparse,json
import check_jay_natural_fsl_routes_1116 as Base

J=Base.J
OLD_SHA='4e7488dcd2674de3e22dffacf8eb83bc25af7840c60af980e36cd0a637143e7e'


def text():
    data=Base.POLICY.read_bytes();assert J.H(data)==OLD_SHA
    s=data.decode()
    edits=(
        ('local boarded=lift and lift.contact==lift.slot and y+32==lift.y and g',
         'local boarded=lift and lift.contact==lift.slot and y+32==lift.y and g and lift.y<208'),
        ('bits=(x<408 and 1 or 0)|shot','bits=(x<406 and 1 or 0)|shot'),
        ('if x>=408 and g then','if x>=406 and g then'),
        ("if boarded and lift.y<=168 then self:change('M-lift-face');bits=2|shot end",
         "if boarded and lift.y<=168 then self:change('M-lift-face');bits=2|shot\n   elseif not boarded and g and self.clock-self.at>4 then self:change('M-lift-wait')end"),
        (' self.lastA=bits&128~=0',r'''
 if self.phase:sub(1,2)=='M-'then
  local h=platform(actors,384)
  self.helper_witness=self.helper_witness or{}
  if #self.helper_witness==8 then table.remove(self.helper_witness,1)end
  self.helper_witness[#self.helper_witness+1]=string.format('%d:%s:x%d/y%d/f%d/c%d/A%s/req%d/p%s',self.clock,self.phase,x,y,s.source_flags,s.source_control,tostring(self.lastA),bits,
   h and string.format('%d/%d/%d/%d',h.slot,h.x,h.y,h.contact)or'none')
  assert(self.clock-self.at<512,'Bounded required M prefix; '..table.concat(self.helper_witness,';'))
 end
 self.lastA=bits&128~=0'''),
    )
    for old,new in edits:
        assert s.count(old)==1,(old,s.count(old));s=s.replace(old,new)
    return s


class Recipe:
    @staticmethod
    def read_text():return text()
    @staticmethod
    def read_bytes():return text().encode()


def run(raw,kind,limit):
    # Capture before the scoped replacement, avoiding recursive recipe reads.
    body=text()
    class CapturedRecipe:
        @staticmethod
        def read_text():return body
        @staticmethod
        def read_bytes():return body.encode()
    with patch.object(Base,'POLICY',CapturedRecipe):q=Base.run(raw,kind,limit)
    q.update(control_successor='v2 margin and genuine carry/retry',failed_policy_SHA256=OLD_SHA,
        control_module_SHA256=J.H(Path(__file__).read_bytes()))
    q['receipt_SHA256']=J.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--kind',choices=('flower','star','life'),required=True);p.add_argument('--limit',type=int,default=1800);a=p.parse_args()
    assert 100<=a.limit<=2600
    raw=J.load_current_image()
    def deny(*a,**kw):raise AssertionError('Jay v2 source controller attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(raw,a.kind,a.limit)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
