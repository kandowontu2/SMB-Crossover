"""Actual natural route with exact passive Pair picture callbacks, no PNG API."""
import argparse
from hashlib import sha256
import inspect,json
from types import SimpleNamespace
import replay_bub_selected_star_images_ace_1115 as Pictures

F,C=Pictures.F,Pictures.C


def controller(raw,identity=0,mode='mushroom'):
    plain=F.controller(raw,identity,mode)
    cfg=dict(entry=0xbdc9,offset=3*8192+0x1dc9,after=0xbd5f,after_offset=3*8192+0x1d5f)
    lua=F.Star.Previous.Witness.Base.Previous.lua
    prefix='local HeroDraw='+lua(cfg)+'\nlocal Pic='+lua(dict(Player_SprAttrib=0x587))+'\n'
    text=prefix+plain;once=F.Star.once
    text=once(text,'local function finish(',Pictures.DECL+'local function finish(')
    text=once(text,'local routeStarted=false',Pictures.OBSERVE+'\nlocal routeStarted=false')
    text=once(text,'natural_star=star','natural_star=star,selected_draw_tail=heroDrawRows')
    check="if done then return end;if ok then assert(#heroDrawRows==8 and heroLastDraw and heroLastDraw.star>0,'Actual passive selected Pair callbacks reached during natural Star')end;done=true"
    text=once(text,'if done then return end;done=true',check)
    restored=text[len(prefix):].replace(Pictures.DECL,'',1).replace(Pictures.OBSERVE+'\n','',1)
    restored=restored.replace('natural_star=star,selected_draw_tail=heroDrawRows','natural_star=star',1)
    restored=restored.replace(check,'if done then return end;done=true',1)
    assert restored==plain
    return text


def run(raw,identity):
    Witness=F.Items.Witness
    base=SimpleNamespace(reference=C.inverse,Previous=Witness.Base.Previous)
    ns=dict(Witness.__dict__,Base=base,PIN=C.CANDIDATE,controller=controller)
    exec(compile(inspect.getsource(Witness.source_check),__file__+':actual-picture-callbacks','exec'),ns)
    q=ns['source_check'](raw,identity)
    rows=q['receipt']['selected_draw_tail'];phases=sorted({p['native']&3 for p in rows})
    assert phases==[0,1,2,3]
    return dict(passed=True,identity=identity,Main=q['receipt']['Main_updates'],
        actual_natural_Star_and_all_selected_draw_callbacks=True,
        actual_last8_native_palette_phases=phases,actual_draw_tail=rows,
        source_receipt_SHA256=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        screenshot_API_called=False,output_files=0)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--identity',type=int,choices=(0,1),default=0);a=ap.parse_args()
    raw,_=C.proposal(C.load_current());q=run(raw,a.identity)
    print('RESULT '+json.dumps(q,sort_keys=True,separators=(',',':')),flush=True)
