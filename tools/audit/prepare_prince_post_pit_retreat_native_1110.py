"""Bind Prince's original reverse and forward jumps around the native Goomba pair."""

import argparse
from hashlib import sha256
from pathlib import Path
import sys

import check_prince_post_pit_retreat_1110 as Retreat
from deliver_helper_camera_render_1110 import bindings
from prepare_prince_full11_1110 import once
from prepare_selected_native_packet_v1 import prepare, sha


R, ROOT, Route = Retreat.R, Retreat.ROOT, Retreat.Route
PREVIOUS = ROOT/'native'
PROOF = ROOT/'retreat/proof.json'
PINS = {
    PREVIOUS/'ready.json':'59b2426f9096629c524838a1a433ad1020d6db68a374cc3d5b629969687e4ee7',
    PREVIOUS/'controller.lua':'3e420297594d234219daa844399a124abb2db898bd64f83571cbb9c9d69f2707',
    PROOF:'f8a9d12978037bbd2b2d10f869db44d988b50159c502d801e92c75168bf3920b',
}


PADS = r'''local postPitPads={['reverse-run']={'left'},['reverse-A']={'left','a'},['reverse-air']={'left'},
 ['wait-fall']={},['forward-run']={'right'},['forward-A']={'right','a'},['forward-air']={'right'}}
local postPitBounds={['reverse-run']=150,['reverse-A']=28,['reverse-air']=120,
 ['wait-fall']=330,['forward-run']=150,['forward-A']=28,['forward-air']=120}
'''


ALIGNMENT_COMPLETE = r'''  elseif stage=='extra-settle-right' and idle then
   if x<1480 or x>1501 or s.native_y~=176 or #postPit.births~=2 then
    routeFail('Reverse approach lacks a supported position and the actual native pair')
   end
   local a,b=groupActor(postPit.births[1].slot),groupActor(postPit.births[2].slot)
   if a.flag~=1 or b.flag~=1 or a.id~=6 or b.id~=6 or a.direction~=2 or b.direction~=2
       or math.min(a.x,b.x)-x<45 then
    routeFail('Original turn lacks room from both actual left-moving Goombas')
   end
   p.turn_actors={a,b};advance=true
'''


RETREAT = r''' route.pad=postPitPads[stage]
 local a,b=groupActor(postPit.births[1].slot),groupActor(postPit.births[2].slot)
 if stage=='reverse-run' then
  local gap=math.min(a.x,b.x)-x
  if x>=1442 and x<=1478 and gap>=34 and (s.phase&3)<=1 and support and runReady(s) and s.source_facing==0 then
   if not solid(1360,208) or solid(1376,208) or solid(1392,208) or solid(1408,208) or not solid(1424,208) then
    routeFail('Reverse original running A lacks the actual three-tile pit')
   end
   p.reverse_request={state=s,actors={a,b},gap=gap};change('reverse-A')
  elseif x<1432 or gap<34 then routeFail('Reverse run reached the lip or lost genuine enemy clearance')end
 elseif stage=='reverse-A' and s.source_action==4 then
  p.reverse_admission=s;change('reverse-air')
 elseif stage=='reverse-air' then
  if x<=1363 and s.native_y==176 and support and solid(x+2,208) then
   p.reverse_ground=s;p.falls={};p.cleared={};change('wait-fall')
  elseif s.native_y>=215 then routeFail('Original left running A did not reach the near bank')end
 elseif stage=='wait-fall' then
  if x<left+8 or x>=1370 then routeFail('Prince left the supported waiting bank')end
  for _,actor in ipairs({a,b})do
   local slot=tostring(actor.slot)
   if actor.flag==1 and actor.id==6 and actor.x>=1376 and actor.x<1424 and actor.y>=204
       and not p.falls[slot] then p.falls[slot]={actor=actor,Main=admitted,frame=frame}end
   if actor.flag==0 and p.falls[slot] and not p.cleared[slot] then
    p.cleared[slot]={Main=admitted,frame=frame,state=s}
   end
  end
  if p.cleared[tostring(a.slot)] and p.cleared[tostring(b.slot)] and support and idleReady(s) then
   change('forward-run')
  end
 elseif stage=='forward-run' then
  if x>=1335 and x<=1358 and (s.phase&3)<=1 and support and runReady(s) and s.source_facing==255 then
   p.forward_request=s;change('forward-A')
  elseif x>1362 then routeFail('Forward run reached the lip without an original supported A')end
 elseif stage=='forward-A' and s.source_action==4 then
  p.forward_admission=s;change('forward-air')
 elseif stage=='forward-air' then
  if x>=1440 and s.native_y==176 and support and solid(x+2,208) then
   if a.flag~=0 or b.flag~=0 then routeFail('The actual fallen Goomba slots did not stay cleared')end
   postPit.clear={Main=admitted,frame=frame,player=s,cleared=p.cleared,falls=p.falls}
   writePostPit(true,'Original reverse and forward running jumps let both live Goombas fall into the native second pit')
   routeLog('post-pit-pair-naturally-cleared')
   return false
  elseif s.native_y>=215 then routeFail('Original right running A did not re-cross the second pit')end
 end
 return true
end

'''


def controller():
    text = (PREVIOUS/'controller.lua').read_text(encoding='utf-8')
    start = text.index('local postPitAlignment={')
    stop = text.index('local function fullTick(finish)',start)
    block = text[start:stop]
    block = once(block,"['extra-settle-right']={pad={},next='up'}",
                 "['extra-settle-right']={pad={},next='reverse-run'}")
    first = block.index('local postPitPads=')
    after = block.index('local function postPitTick(',first)
    block = block[:first]+PADS+block[after:]
    block = once(block,"route.post_pit={stage='initial',Main=admitted,events={}}",
                 "route.post_pit={stage='initial',Main=admitted,events={},HP=s.HP}")
    block = once(block,' local stage=p.stage',' if s.HP~=p.HP then routeFail(\'Original Goomba retreat lost source HP\')end\n local stage=p.stage')
    before = block.index("  elseif stage=='extra-settle-right' and idle then")
    after = block.index('  else advance=idle end',before)
    block = block[:before]+ALIGNMENT_COMPLETE+block[after:]
    marker = ' route.pad=postPitPads[stage]\n'
    assert block.count(marker)==1
    text = text[:start]+block[:block.index(marker)]+RETREAT+text[stop:]
    assert text.count(Route.PIN)==1 and 'emu.write(' not in text
    sys.path.insert(0,str(Route.Seam.Stage.LUA_DEPS))
    from lupa.lua54 import LuaRuntime
    assert LuaRuntime().eval('function(s) local f,e=load(s); assert(f,e); return true end')(text)
    return text


def prior_bindings(ready):
    expected = dict(ready['bindings'])
    preparer = Path(prepare.__code__.co_filename).resolve()
    old = expected.pop(str(preparer))
    raw = preparer.read_bytes()
    if sha256(raw).hexdigest()!=old:
        # The current preparer accepts optional metadata paths. Prove the
        # default path still reproduces the exact previously bound source.
        text = raw.decode('utf-8')
        text = once(text,'allow_interactive=False,\n            rom_symbols=None):','allow_interactive=False):')
        text = once(text,"    if rom_symbols is None:\n        rom_symbols = (rom.with_suffix('.lbl'), rom.with_suffix('.dbg'))\n"
                    '    paths = {Path(__file__), rom, *rom_symbols,',
                    "    paths = {Path(__file__), rom, rom.with_suffix('.lbl'), rom.with_suffix('.dbg'),")
        assert sha256(text.encode('utf-8')).hexdigest()==old
    bindings(expected)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    out = parser.parse_args().output.resolve()
    assert out==ROOT/'retreat/native' and not out.exists()
    for p,digest in PINS.items():
        assert sha(p)==digest,p
    ready,proof = (Retreat.Pair.Second.First.Pit.Current.read(p) for p in (PREVIOUS/'ready.json',PROOF))
    assert ready['ROM_sha256']==proof['ROM_SHA256']==Route.PIN and not ready['emulated_writes']
    prior_bindings(ready)
    for p,digest in proof['bindings'].items():
        assert sha(R/p)==digest,p
    rev,forward,wait = proof['reverse'][-1],proof['forward'][-1],proof['waiting'][-1]
    assert rev['face']==0 and forward['face']==255 and rev['admission']['action']==forward['admission']['action']==4
    assert rev['terminal']==forward['terminal']=='far-ground' and wait['passed']
    assert (rev['end']['x'],wait['end']['x'],forward['end']['x'],forward['end']['hp'],forward['end']['lives'])==(1340,1313,1454,4,2)
    assert [(x['actor']['x'],x['actor']['y']) for x in wait['falls'].values()]==[(1408,206),(1408,206)]
    refs = {Path(__file__),*PINS,*map(Path,ready['bindings']),*(R/p for p in proof['bindings'])}
    prepare(out,Route.ROM,controller(),refs,expected=Route.PIN,timeout=ready['timeout'],
            allow_interactive=ready['allow_interactive'],
            scope='Live actor clearance gates an original reverse running A. Both actual Goombas fall into the authored '
                  'second pit and clear their slots before original supported running A re-crosses. Prior witnesses retained.')
    assert sum(p.is_file() for p in out.rglob('*'))==3


if __name__=='__main__':
    main()
