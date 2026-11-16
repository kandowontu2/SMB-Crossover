"""Passive first-Koopa eligibility aggregates; exact frozen contact-policy inputs."""
from pathlib import Path
from functools import lru_cache
from unittest.mock import patch
import json
import replay_rogue_missile_contact_cb95_1116 as F
import inspect_rogue_missile_targets_cb95_1116 as Engine

PARENT_SHA='3138fe3939392064a80049dfeb87cbbc079842b90fc2c6f1d57d9502dbdd41c8'


@lru_cache(maxsize=1)
def controller(raw):
    assert F.H(Path(F.__file__).read_bytes())==PARENT_SHA
    old=F.controller(raw);assert F.H(old.encode())=='ff59ba978f0cb3567e0bea4e39845f28610e4693451c9586c83f48f5c2c7fbf3'
    observer='''if not impact.eligibility then impact.eligibility={samples=0,koopa=0,ready=0,vertical=0,gap=0,line=0,all=0,first={}}end
  local d=impact.eligibility;d.samples=d.samples+1
  for i=0,4 do local e=nativeEnemy(i);if e.flag==1 and e.id==0 and e.high==1 and e.state<32 and e.box then
   d.koopa=d.koopa+1
   local a,v,g=r('RdAction'),r('RdVY'),r('RdGravity');local ready=c.grounded and c.y>=168 and c.yHigh==1 and(a==0 or a==4 or(a==1 and g==0 and v<128))and(r('RdHeld')&128)==0
   local mx,my=pos('RdX','RdRoomHi')+8,r('RdY')-6;local gap=e.box[1]-mx;local vertical=my+2>=e.box[2]and my-2<e.box[4];local range=gap>=64 and gap<=144
   local clear=true;local obstruction
   for x=math.floor(mx/16)*16,e.box[1],16 do if solid(c,x,my)then clear=false;obstruction=obstruction or{x=x,y=my,tile=c.block(x,my)}end end
   local function first(n)if not d.first[n]then d.first[n]={player=state(),enemy=e,muzzle={mx,my},gap=gap,ready=ready,vertical=vertical,range=range,clear=clear,obstruction=obstruction,held=r('RdHeld'),gravity=g}end end
   first('koopa')
   if ready then d.ready=d.ready+1;first('ready');d.min_gap_ready=d.min_gap_ready and math.min(d.min_gap_ready,gap)or gap;d.max_gap_ready=d.max_gap_ready and math.max(d.max_gap_ready,gap)or gap end
   if vertical then d.vertical=d.vertical+1;first('vertical')end
   if range then d.gap=d.gap+1;first('range')end
   if clear then d.line=d.line+1 end
   if ready and vertical then first('ready_vertical')end
   if ready and vertical and range and clear then d.all=d.all+1;first('all')end
  end end
  '''
    assert old.count('local e=alignedTarget(c)')==1
    text=old.replace('local e=alignedTarget(c)',observer+'local e=alignedTarget(c)',1)
    assert text.replace(observer+'local e=alignedTarget(c)','local e=alignedTarget(c)',1)==old
    Engine.LuaRuntime().compile(text);return text


if __name__=='__main__':
    raw,provenance=Engine.Reader.load_current()
    def deny(*a,**kw):raise AssertionError('Passive alignment observer attempted outputs/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        text=controller(raw);q=Engine.run(raw,4000,text=text)
    d=q['receipt'].get('missile_contact',{}).get('eligibility')
    result=dict(diagnostic_complete=bool(d and d.get('koopa')and d.get('first')),original_gameplay_passed=q['passed'],input=provenance,
        factory_SHA256=F.H(Path(__file__).read_bytes()),controller_SHA256=F.H(text.encode()),parent_factory_SHA256=PARENT_SHA,
        exact_input_body_restoration=True,source_result=q,outputs=0,native=False)
    result['receipt_SHA256']=F.H(json.dumps(result,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(result,separators=(',',':')),flush=True)
