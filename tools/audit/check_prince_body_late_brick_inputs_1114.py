"""Bounded ordinary inputs from an actually earned late-brick CPU checkpoint."""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import argparse,json
import current_prince_body_research_f11_1114 as Current
import check_prince_body_earned_stage_1114 as Base
import replay_prince_body_earned_wait_stage_1114 as Factory

P,N=Base.P,Base.N


def play(model,raw,text,limit):
    receipts=[];loads=json.loads
    def capture(*args,**kwargs):
        value=loads(*args,**kwargs)
        if isinstance(value,dict)and'later_route'in value:receipts.append(value)
        return value
    def frame(m,*args,**kwargs):return Base.Frames.frame(m,whole_pass=True)
    with patch.object(P,'controller',lambda image:text),patch.object(P.Frames,'frame',frame),patch.object(P.json,'loads',capture):
        proof=P.route(model,raw,limit)
    assert len(receipts)==1
    proof.pop('events',None);proof.pop('sword_trace',None)
    if isinstance(proof.get('flower'),dict):proof['flower']={k:v for k,v in proof['flower'].items()if k!='trace'}
    return proof,receipts[0]


def component(text,mode):
    marker='local route=coroutine.create(function()\n';begin=text.index(marker)
    lo=text.index('  initial=state()\n',begin)
    tail='  while not stopped do tick();coroutine.yield() end'
    hi=text.index(tail,lo)+len(tail)
    body=r'''
  initial=state()
  local c={mode=@MODE@,start=combatState(),samples={}}
  late.latebrick_component=c
  local first,last=commits,-1
  local nextleft
  for x=((initial.x&~15)+48),((initial.x&~15)+192),16 do
    if solid(x,initial.y+32)then nextleft=x;break end
  end
  assert(nextleft and nextleft>initial.x+24,'Real separate next authored brick')
  c.next_platform_left=nextleft
  local held=@MODE@=='held-A-up'
  local phase=@MODE@=='walk-up'and'flight'or(@MODE@=='running-up'or held)and'runup'or'request'
  pad=phase=='request'and 128 or 1
  while not stopped do
    if commits~=last then
      last=commits
      local s=combatState()
      assert(s.lives==2 and s.hp>0,'Living genuine late-brick component')
      if phase=='runup'and running(s)and support(s)then phase='request';pad=129
      elseif phase=='request'and(s.action==3 or s.action==4)then phase='flight';pad=held and 129 or 1
      elseif phase=='flight'and s.x+16>=nextleft then phase='up';pad=held and 136 or 8 end
      if held and(s.mode==2 or s.mode==6)then pad=8 end
      if #c.samples==0 or c.samples[#c.samples].phase~=phase or c.samples[#c.samples].state.action~=s.action or commits%12==0 then
        c.samples[#c.samples+1]={phase=phase,state=s,actors=lateWalkers(s),tiles=finishGeometry(s)}
        if #c.samples>64 then table.remove(c.samples,2)end
      end
      c.hang=c.hang or s.mode==2 or s.mode==6
      c.top=c.top or(c.hang and support(s)and idle(s)and s.y<=initial.y+1 and s.x+13>=nextleft)
      if c.top or commits-first>=420 then
        c.terminal=s;final=s;finish(true,'Bounded ordinary late-brick input observation');break
      end
    end
    coroutine.yield()
  end
'''.replace('@MODE@',json.dumps(mode))
    result=text[:lo]+body+text[hi:]
    Factory.LuaRuntime().compile(result)
    return result


def run(*,current_score571=False):
    attempts=[]
    def deny(*args,**kwargs):attempts.append(str(args[:1]));raise AssertionError('No output or launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        if current_score571:import current_prince_body_research_571_1114 as Input
        else:Input=Current
        current=Input.load(Base.Game.Factory.ROM);raw,_=Base.C.proposal(current.reference1daca)
        assert Base.C.inverse(raw)==current.reference1daca
        text=Factory.controller(raw,brick_runup=True)
        checkpoint=text.replace("          switch('late-finish-brick-runup',1)","          final=s;finish(true,'Actual latebrick returned-source checkpoint');return",1)
        assert checkpoint!=text
        model,opening=Base.Game.cold(raw);prefix,receipt=play(model,raw,checkpoint,4600)
        assert prefix['passed']and prefix['terminal']['hp']==4 and prefix['terminal']['x']==1587
        assert model.ram[2][0x6ee]==1
        print(json.dumps(dict(event='actual-earned-late-brick',terminal=prefix['terminal'],Main=prefix['logical_updates']),separators=(',',':')),flush=True)
        cases=[]
        for mode in('standing-up','running-up','walk-up','held-A-up'):
            branch=N.fork(model);script=component(text,mode)
            proof,result=play(branch,raw,script,500)
            observed=result.get('later_route',{}).get('latebrick_component')
            trace_digest=sha256(json.dumps(observed,sort_keys=True,separators=(',',':')).encode()).hexdigest()
            if observed:
                observed['samples']=observed.get('samples',[])[-6:]
                for row in observed['samples']:row.pop('tiles',None)
            cases.append(dict(mode=mode,proof=proof,component=observed,full_component_SHA256=trace_digest,
                Main_entries=result.get('Main_entries'),Main_returns=result.get('Main_returns'),Main_pending=result.get('Main_pending'),
                Lua_SHA256=sha256(script.encode()).hexdigest()))
        assert not attempts
    q=dict(ROM_SHA256=Factory.PIN,opening=opening,prefix=prefix,cases=cases,
        checkpoint='Actual cold/UI/pickup/combat/late-brick state; only ordinary controls differ in forks',
        gameplay_seeds=0,outputs=0,Mesen=False,write_or_launch_attempts=attempts)
    q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--current-score-571',action='store_true');args=parser.parse_args()
    print(json.dumps(run(current_score571=args.current_score_571),separators=(',',':')),flush=True)
