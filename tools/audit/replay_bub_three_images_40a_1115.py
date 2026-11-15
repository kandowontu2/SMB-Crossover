"""Three RAM PNGs: actual opening Goomba plus the two frozen item scenes."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import replay_bub_flower_images_40a_1115 as Previous

R,ROM,W,N,B,PIN=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.B,Previous.PIN
PARENT='c1616cddfc30edae8cecdaec3d6e5ac567409c0ed8930fcc8273f91590c0a562'
GOOMBA=r'''
local visualGoombaReady=nil
local function visualGoombaObserve()
 if done or not visualLast or visualSeen.G then return end
 local camera=r('ScreenLeft_PageLoc')*256+r('ScreenLeft_X_Pos')
 for _,a in ipairs(visualLast.enemies)do
  if a.id==6 and a.state&96==0 and a.x>=camera and a.x<camera+240 and a.y>=16 and a.y<224 then
   if not visualGoombaReady or visualGoombaReady.slot~=a.slot then visualGoombaReady={slot=a.slot,Main=updates}end
   if updates-visualGoombaReady.Main>=2 then
    assert(#visualQueue+#visualRows<3,'Maximum three actual scene requests')
    visualSeen.G=true;visualQueue[#visualQueue+1]={tag='G',snapshot=visualLast,goomba=a,camera=camera}
   end
   return
  end
 end
 visualGoombaReady=nil
end
'''
ACK=r'''
 if request.tag=='G'then
  local a=request.goomba;local sx=a.x-request.camera;local selected={}
  for _,p in ipairs(oam)do
   if p.x>=sx-4 and p.x<=sx+20 and p.y>=a.y-16 and p.y<=a.y+24 then selected[#selected+1]=p end
  end
  assert(#selected>0,'Actual visible hardware OAM near the live opening Goomba')
  row.goomba=a;row.goomba_oam=selected
 end
'''

@lru_cache(maxsize=1)
def controller(raw,identity=0,mode='mushroom'):
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()==PARENT
    old=Previous.controller(raw,identity,mode);text=old;once=Previous.Previous.once
    text=once(text,'local function visualBase64(bytes)',GOOMBA+'\nlocal function visualBase64(bytes)')
    text=once(text,'tick();visualObserve()','tick();visualObserve();visualGoombaObserve()')
    bounds=[("#visualRows==2,'Both rendered item scenes captured'","#visualRows==3,'Three rendered Goomba and item scenes captured'"),
        ("#visualQueue+#visualRows<2,'Maximum two queued pictures'","#visualQueue+#visualRows<3,'Maximum three queued pictures'"),
        ("#visualRows<2,'Maximum two actual rendered PNGs'","#visualRows<3,'Maximum three actual rendered PNGs'")]
    for before,after in bounds:text=once(text,before,after)
    text=once(text,' visualRows[#visualRows+1]=row',ACK+'\n visualRows[#visualRows+1]=row')
    restored=text.replace(GOOMBA+'\n','',1).replace(ACK+'\n','',1).replace('tick();visualObserve();visualGoombaObserve()','tick();visualObserve()',1)
    for before,after in bounds:restored=restored.replace(after,before,1)
    assert restored==old,'Exact frozen two-scene controls and observations after removing only third-scene additions'
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    LuaRuntime().compile(text)
    return text

def metadata(raw,identity=0):
    text=controller(raw,identity);q=Previous.metadata(raw,identity)
    q.update(controller_SHA256=sha256(text.encode()).hexdigest(),parent_factory_SHA256=PARENT,
        parent_controller_SHA256=sha256(Previous.controller(raw,identity).encode()).hexdigest(),maximum_images=3,
        maximum_total_PNG_bytes=196608,existing_M_F_tags_exact=True,third_scene_requires_live_Goomba_and_visible_hardware_OAM=True,
        scope='Opening liveGoomba plus the two frozen matureM/hero and matureF/Mpoweredhero/freebubble scenes; no files/input/game changes')
    return q
