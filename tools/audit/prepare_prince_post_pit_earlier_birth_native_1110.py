"""Stage the source-qualified careful steps and earlier natural Goomba birth."""

import argparse
from pathlib import Path
import sys

import check_prince_post_pit_landing_writer_1110 as Writer
import prepare_prince_post_pit_native_1110 as Prior
from deliver_helper_camera_render_1110 import bindings
from prepare_prince_full11_1110 import once
from prepare_selected_native_packet_v1 import prepare, sha


R, Route = Writer.R, Writer.Route
PREVIOUS = R/'build/prince-post-pit-goombas-1110/native'
PROOF = R/'build/prince-post-pit-landing-writer-1110/writer.json'
PINS = {
    PREVIOUS/'ready.json':'b3bd14baff47c4dbb7b1e716b7316261a63a626c8e606afba462cefa81039944',
    PREVIOUS/'controller.lua':'646ced85cd5c400b82b05640b58cb8ce7b2dc2a6a6aec940b263200ee164adc7',
    PROOF:'b02298eaf32bc8763f39691972d958c877f7f7b4e2f961cca284b8594ca91fa3',
}


ALIGN = r'''
local postPitAlignment={
 initial={pad={'right'},next='brake'},brake={pad={},next='face-left'},
 ['face-left']={pad={'left'},next='settle-left'},['settle-left']={pad={},next='step-left'},
 ['step-left']={pad={'b'},next='stop-left'},['stop-left']={pad={},next='face-right'},
 ['face-right']={pad={'right'},next='settle-right'},['settle-right']={pad={},next='step-right'},
 ['step-right']={pad={'b'},next='finish-step'},['finish-step']={pad={},next='extra-left'},
 ['extra-left']={pad={'left'},next='extra-settle-left'},['extra-settle-left']={pad={},next='extra-right'},
 ['extra-right']={pad={'right'},next='extra-settle-right'},['extra-settle-right']={pad={},next='up'}
}
local postPitPads={up={'up'},climb={'up'},['cap-A']={'a'},leap={'right'}}
local postPitBounds={up=110,climb=100,['cap-A']=28,leap=145}
'''


PREPARE = r'''
 if admitted-p.Main>(postPitBounds[stage] or 140) then routeFail('Post-pit original '..stage..' exceeded its finite bound')end
 local align=postPitAlignment[stage]
 if align then
  if x<1435 or x>1510 then routeFail('Post-pit alignment left its supported bank')end
  local idle=idleReady(s) and support
  route.pad=align.pad
  local advance=false
  if stage=='initial' then advance=x>=1467
  elseif stage=='face-left' or stage=='extra-left' then advance=s.source_facing==0
  elseif stage=='face-right' or stage=='extra-right' then advance=s.source_facing==255
  elseif stage=='step-left' or stage=='step-right' then advance=s.source_action==42 and s.source_frame==127
  elseif stage=='extra-settle-right' and idle then
   local solidBlock,tile=solid(1504,144)
   if not solidBlock or tile~=88 or x<1480 or x>1501 or s.native_y~=176 then
    routeFail('Post-pit careful alignment lacks the authored high brick or supported original Up scan')
   end
   if #postPit.births~=2 or right<1552 then routeFail('Earlier post-pit group did not actually spawn before Up')end
   local a,b=groupActor(postPit.births[1].slot),groupActor(postPit.births[2].slot)
   if a.flag~=1 or b.flag~=1 or a.id~=6 or b.id~=6 or math.min(a.x,b.x)-x<45 then
    routeFail('Post-pit Up lacks room from both actual live Goombas')
   end
   p.up_actors={a,b};advance=true
  else advance=idle end
  if advance then change(align.next)end
  return true
 end
 route.pad=postPitPads[stage]
 if stage=='up' and (s.source_mode==2 or s.source_mode==6 or s.source_action==10) then
'''


def controller():
    text = (PREVIOUS/'controller.lua').read_text(encoding='utf-8')
    old = Prior.CONTROL
    begin = 'local function postPitTick(s,o,support)'
    replacement = ALIGN+old[old.index(begin):]
    replacement = once(replacement,'route.pad=postPitPads[name]',
                       'route.pad=postPitAlignment[name] and postPitAlignment[name].pad or postPitPads[name]')
    start = replacement.index(' if admitted-p.Main>postPitBounds[stage]')
    stop = replacement.index("  p.hang=s;change('climb')",start)
    replacement = replacement[:start]+PREPARE+replacement[stop:]
    text = once(text,old,replacement)
    assert text.count(Route.PIN)==1 and 'emu.write(' not in text
    sys.path.insert(0,str(Route.Seam.Stage.LUA_DEPS))
    from lupa.lua54 import LuaRuntime
    assert LuaRuntime().eval('function(s) local f,e=load(s); assert(f,e); return true end')(text)
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    out = parser.parse_args().output.resolve()
    assert out.is_relative_to(PROOF.parent) and out!=PROOF.parent and not out.exists()
    for p,digest in PINS.items():
        assert sha(p)==digest,p
    ready, proof = (Writer.Pair.Second.First.Pit.Current.read(p) for p in (PREVIOUS/'ready.json',PROOF))
    assert ready['ROM_sha256']==proof['ROM_SHA256']==Route.PIN and not ready['emulated_writes']
    bindings(ready['bindings'])
    for p,digest in proof['bindings'].items():
        assert sha(R/p)==digest,p
    timing = proof['timing']
    assert (timing['arrived']['x'],timing['arrived']['camera_right'])==(1482,1555)
    end = timing['replay']['end']
    assert timing['replay']['terminal']=='pair-behind' and not timing['replay']['contacts']
    assert (end['x'],end['y'],end['hp'],end['lives'])==(1546,176,4,2)
    refs = {Path(__file__),*PINS,*map(Path,ready['bindings']),*(R/p for p in proof['bindings'])}
    prepare(out,Route.ROM,controller(),refs,expected=Route.PIN,timeout=ready['timeout'],
            allow_interactive=ready['allow_interactive'],
            scope='Original careful steps and turns establish a naturally born Goomba pair and safe supported Up. '
                  'Existing authored high brick, original standing A and all prior crossing witnesses retained.')
    assert sum(p.is_file() for p in out.rglob('*'))==3


if __name__=='__main__':
    main()
