"""Controller-only native Jay pickup through an existing vertical platform."""

from hashlib import sha256
import json
import compose_jay_pickup_helper_1113 as P
import replay_jay_powerups_1113 as Base


def controller(raw):
    parent=P.inverse(raw)
    script=Base.controller(parent,expect='earned').replace(P.Head.NEW_COOKIE.hex(),P.COOKIE.hex())
    bundle=P.B.Current.W.Symbols.bundle()
    address=lambda name:P.B.Current.W.address(bundle,name)
    contact=address('PlatformCollisionFlag')
    script=script.replace('local registered={}',"local registered={}\nlocal helpers,boards,departures={},{},{}")
    script=script.replace('source_flags=emu.read',f"camera=r({address('ScreenLeft_X_Pos')})+256*r({address('ScreenLeft_PageLoc')}),source_flags=emu.read")
    old='x=r(0x76+i)+256*r(0x5d+i),y=r(0xbe+i),private='
    assert script.count(old)==1
    script=script.replace(old,f'x=r(0x76+i)+256*r(0x5d+i),y=r(0xbe+i),contact=r({contact}+i),private=')
    script=script.replace('minimum_y=minimum,block=r(0x445),trace=trace}',
        'minimum_y=minimum,block=r(0x445),trace=trace,helpers=helpers,boards=boards,departures=departures}')
    script=script.replace('local item=nil;local near=false','local item=nil;local platform=nil;local near=false')
    script=script.replace('if a.flag~=0 then',"if a.flag~=0 then\n   if a.id==37 and a.x==384 then platform=a end")
    script=script.replace('local shot=near and epoch%12<2 and 64 or 0',
        '''local shot=near and epoch%12<2 and 64 or 0
 local boarded=platform and platform.contact==platform.slot and s.y+32==platform.y and s.motion==0
 if boarded and #boards==0 then boards[1]={actor=platform,player=s,epoch=epoch}end''')
    script=script.replace("assert(expected=='earned'and #heads>0 and #births>0,'Natural reveal and collection')",
        "assert(expected=='earned'and #heads>0 and #births>0,'Natural reveal and collection')\n  assert(#helpers==1 and #boards==1 and #departures==1,'Offscreen native platform birth, carry and fresh jump')")
    first=script.index(" if item and(phase=='approach'or phase=='park'or phase=='jump')")
    last=script.index(' epoch=epoch+1',first)
    script=script[:first]+''' if item and(phase=='approach'or phase=='park'or phase=='jump')then phaseTo('lift-approach')end
 if phase=='lift-approach'then
  pad=(s.x<408 and 1 or 0)+shot
  if s.x>=408 and s.motion==0 then phaseTo('lift-wait');pad=shot end
 elseif phase=='lift-wait'then
  pad=shot
  if boarded then phaseTo('lift-ride')
  elseif platform and s.motion==0 and platform.y>=176 then phaseTo('lift-board');pad=pad|128 end
 elseif phase=='lift-board'then
  pad=(epoch-phaseEpoch<18 and 128 or 0)+shot
  if boarded then phaseTo('lift-ride');pad=shot
  elseif s.motion==0 and epoch-phaseEpoch>20 then phaseTo('lift-wait')end
 elseif phase=='lift-ride'then
  pad=shot
  if boarded and platform.y<=168 then phaseTo('lift-face');pad=2+shot end
 elseif phase=='lift-face'then
  pad=shot
  if boarded and s.source_flags&2~=0 and s.source_control&0x38==0 then
   phaseTo('collect-jump');pad=130+shot;departures[1]={actor=platform,player=s,epoch=epoch}
  end
 elseif phase=='collect-jump'then
  pad=(item and s.x>item.x and 2 or 0)+shot
  if epoch-phaseEpoch<18 then pad=pad|128 end
 elseif phase=='approach'then pad=1+shot
 elseif phase=='park'then pad=shot
 elseif phase=='jump'then pad=((epoch-phaseEpoch)%64<18 and 128 or 0)+shot
 else pad=0 end
'''+script[last:]
    marker="exec(0x9ef5,'Head effect'"
    first=script.index(marker)
    hook='''exec(0xa74f,'Native helper constructor',function()
 if not game then return end
 local q=emu.convertAddress(0xa74f)
 if not q or q.memType~=emu.memType.nesPrgRom or q.address~=2*8192+(0xa74f&8191)then return end
 local a=actor(emu.getState()['cpu.x'])
 if a.id~=37 or a.x~=384 then return end
 local s=state();local relative=a.x-s.camera
 assert(#helpers==0 and a.flag==1 and a.y==192 and relative>=256 and relative<=287,'Native offscreen birth')
 helpers[1]={actor=a,player=s,relative=relative,camera_right=s.camera+255}
end)
'''
    script=script[:first]+hook+script[first:]
    return script


def stage_controller(raw):
    """Keep the qualified full-stage controls, authenticate the helper cache."""
    import replay_jay_stage_current_1113 as Stage
    text=Stage.controller(P.inverse(raw))
    assert text.count(P.Head.NEW_COOKIE.hex())==2
    return text.replace(P.Head.NEW_COOKIE.hex(),P.COOKIE.hex())


if __name__=='__main__':
    import check_ff_stdout_controller_source_1110 as Lua
    image,info=P.proposal(P.frozen_head())
    text=controller(image)
    assert Lua.LuaRuntime().eval('function(s)local f,e=load(s);assert(f,e);return true end')(text)
    print(json.dumps(dict(compiles=True,ROM_SHA256=P.PIN,script_SHA256=sha256(text.encode()).hexdigest(),
                          controller_only=True,output_files=0)),flush=True)
