"""Separate ordinary Up-reach / mature1-UP pursuit on a bound Prince lift.

Root supplies the exact authenticated candidate overlay. No native emulator,
image writes, captures or state seeds. Existing lift replay stays unchanged.
"""
import argparse
import json
from pathlib import Path
from unittest.mock import patch

import replay_prince_oneup_lift_1123 as R
import run_prince_oneup_lift_native_1123 as Native

H,W,Engine=R.H,R.W,R.Engine
OBSERVER='4c48af6d3c1779f0de1491e8904b845f058bcab207d569e94e07d6a435390bf3'
FACTORY='921aa74cfb95e12e75aa00669446202bd05ed15bfc4758dbab410ee396bcf2fe'

OLD_ITEM=''' if item then
  if not stock.mature then pad=0;return true end
  local gap=item.x-s.x;pad=gap>5 and 1 or gap< -5 and 2 or 0
  if floor(s)and item.y<s.y-16 and stock.prince_returns-(stock.chase_jump or -100)>48 then
   stock.chase_jump=stock.prince_returns;pad=pad|STOCK.jump
  end
  return true
 end'''

ITEM=r''' if item then
  stock.item_pursuit=stock.item_pursuit or{samples={}}
  local p=stock.item_pursuit;local a=liftActor()
  p.born=p.born or{state=s,actor=item};p.lift=a
  local high=s.foot<176
  local left=stock.lift.placement.left+8
  local right=stock.lift.placement.left+stock.lift.placement.width-16
  local target
  if not stock.mature then
   -- This is platform safety, independent of the immature item's position.
   target=math.min(right,math.max(left,s.x))
   pad=s.x<left and 1 or s.x>right and 2 or 0
   p.waiting=p.waiting or{state=s,actor=item}
  else
   assert(item.flag==1 and item.id==46 and item.kind==3 and item.state>=128,
    'Pursuit begins only for the genuine mature1-UP')
   p.mature_start=p.mature_start or{state=s,actor=item}
   target=item.x-4
   if high then target=math.max(left,math.min(right,target))
   else target=math.max(left,math.min(1076,target))end
   pad=s.x<target-4 and 1 or s.x>target+4 and 2 or 0
  end
  if stock.prince_returns%8==0 and p.last~=stock.prince_returns and #p.samples<36 then
   p.last=stock.prince_returns
   p.samples[#p.samples+1]={state=s,actor=item,lift=a,high=high,target=target,pad=pad,
    left_material=tile(s.x+2,s.y+32),right_material=tile(s.x+13,s.y+32)}
  end
  return true
 end'''


def controller(image,overlay):
    assert H(Path(R.__file__).read_bytes())==OBSERVER,'Frozen lift observer'
    assert H(Path(Native.__file__).read_bytes())==FACTORY,'Frozen ordinary reach factory'
    parent,_,_=R.authenticate(image,overlay)
    text=Native.controller(parent,image,overlay,'pickup',centered=True,face_first=True,reach=True)
    once=R.P.G.First.once
    text=once(text,"strategy='centered cap departure'","strategy='ordinary Up / mature-only safe pursuit'")
    text=once(text,OLD_ITEM,ITEM)
    text=once(text,"assert(stock.lift.head.speed>=128 and stock.lift.admission,'Actual rising fresh-A head from lift')",
        """assert(stock.lift.head.speed>=128 and stock.lift.admission,'Actual rising native hidden hit from original Up reach')
 local admitted=stock.lift.admission.state
 assert(admitted.action==28 or admitted.pose==78,'Original Up action/reach pose, no substituted standing A')""")
    text=once(text,'  if s.pose==78 then l.reached_apex=s end', '''  if s.pose==78 then
   l.reached_apex=s
   if not stock.born and not l.head then
    l.no_head_at_apex=s;final=s
    finish(false,'Original Up reached apex without rising native head/birth; stopped before unsupported high fall')
    return true
   end
  end''')
    assert not any(token in text for token in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    R.P.Base.LuaRuntime().compile(text)
    return text


def source(image,overlay,limit=4200):
    text=controller(image,overlay)
    with patch.object(Engine.J,'cold',lambda raw:R.cold(raw,overlay)),patch.object(Engine.J,'PIN',H(image)):
        return Engine.run(image,limit,text=text)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',action='store_true');args=parser.parse_args()
    import compose_prince_oneup_lift_1123 as Compose
    import probe_prince_lift_swept_plane_1123 as Sweep
    raw=R.P.G.ROM.read_bytes();assert H(raw)==R.PIN
    image,overlay=Compose.compose(raw,Sweep.hold_plane_plan)
    def deny(*a,**k):raise AssertionError('Source-only Up replay attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        text=controller(image,overlay)
        info=dict(passed=True,ROM_SHA256=H(image),controller_SHA256=H(text.encode()),
                  observer_SHA256=OBSERVER,factory_SHA256=FACTORY,outputs=0,
                  compile_only=not args.source,native=False)
        if args.source:
            q=source(image,overlay);receipt=q.get('receipt',{});stock=receipt.get('natural_stock',{})
            info.update(passed=q['passed'],receipt_SHA256=q['receipt_SHA256'],passes=q['source_passes'],
                        reason=receipt.get('reason'),terminal=receipt.get('terminal'),
                        stock={name:stock[name]for name in('born','mature','collector','collected','credit',
                            'completed_at_main_return','lift','item_pursuit')if name in stock})
        print('PRINCE_UP_LIFE '+json.dumps(info,separators=(',',':')),flush=True)
    return int(not info['passed'])


if __name__=='__main__':raise SystemExit(main())
