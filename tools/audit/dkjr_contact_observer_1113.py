"""Read-only causal observer appended to the frozen9f943 controller."""
from hashlib import sha256
import json

import compose_dkjr_helper_retire_1113 as P
import check_dkjr_head_bridge_1113 as H


def controller(raw):
    assert sha256(raw).hexdigest()==P.PRINCE_PROPOSAL
    text=P.fourth_contact_ride_controller(raw)
    body=P.T.payload(raw)[:8160];labels=P.frozen_labels()
    bundle=H.W.Symbols.bundle();bundle['raw']=raw
    columns=['Main','event','phase','nativeX','nativeY','nativeDY','nativeYHigh',
        'sourceY','sourceState','sourcePriorState','direction','fallStart','fallLimit','jumpProgress',
        'carryTop','carryPhase','carryReason','worldKind','worldTop','worldBottom','worldCount',
        'sourceRect','playerBox','playerBoxCtrl','nativePad','sourceHeld','sourceSample',
        'slot944','flag944','top944','box944','DY944','force944',
        'slot880','flag880','top880','box880','PC','SP','A','X','Y','P','ObjectOffset','bankA','bankC']
    declaration='local dkContactCapture\nlocal dkContactTrace={columns='+json.dumps(columns)+',rows={},dropped=0}'
    # JSON arrays are not Lua table constructors.
    declaration=declaration.replace(json.dumps(columns),'{'+','.join(json.dumps(s)for s in columns)+'}')
    text=P.once(text,'local births,carries,visible,events,crossings={},{},{},{},{}',
        'local births,carries,visible,events,crossings={},{},{},{},{}\n'+declaration)
    text=P.once(text,'events=events,crossings=crossings,',
        'events=events,crossings=crossings,fourth_contact_trace=dkContactTrace,')
    text=P.once(text,'if playing then drive() else',
        "if playing then dkContactCapture('frame-before-control');drive() else")
    native={n:H.W.address(bundle,n)for n in('PlatformCollisionFlag','BoundingBox_UL_Corner',
        'Player_BoundBoxCtrl','Enemy_Y_Speed','Enemy_Y_MoveForce','CurrentBank','CurrentBankC')}
    functions={n:labels[n]for n in('DkjrNativeSourcePhase','DkjrMove','DkjrFallDistance',
        'DkjrLand','DkjrNativeCarryEvent','D_e89f')}
    def callers(target):
        pattern=bytes((0x20,target&255,target>>8))
        return [0xa000+i+3 for i in range(len(body)-2)if body[i:i+3]==pattern]
    points=[]
    for name,event in(('DkjrNativeSourcePhase','source-before'),('DkjrMove','move-before'),
        ('DkjrFallDistance','fall-before'),('DkjrLand','land-before'),
        ('DkjrNativeCarryEvent','source-carry-before'),('D_e89f','support-before')):
        points.append((functions[name],event))
    for name,event in(('DkjrNativeSourcePhase','source-after'),('DkjrFallDistance','fall-after'),
        ('D_e89f','support-after')):
        returns=callers(functions[name]);assert returns,(name,hex(functions[name]))
        points.extend((pc,event)for pc in returns)
    writers=[0xa000+i for i in range(len(body)-2)if body[i:i+3]==bytes.fromhex('8d6bc0')]
    position=H.W.address(bundle,'PositionPlayerOnVPlat')
    position_offset=H.W.location(bundle,'PositionPlayerOnVPlat')-16
    assert raw[16+71*8192+0xc29:16+71*8192+0xc2a]==b'\x60'
    assert raw[16+71*8192+0xc18:16+71*8192+0xc1f]==bytes.fromhex('85bd98e90085a4')
    tail='''
-- Exact e73 observational callbacks; no emu.write or controller changes.
local dkTraceLast={}
local function dkArray(at,count)
 local result={};for i=0,count-1 do result[#result+1]=read(at+i)end;return result
end
local function dkPlatform(left)
 for i=0,5 do
  if read(0x10+i)==1 and read(0x17+i)==0x25 and pos(0x76,0x5d,i)==left then
   return i,read(DK_FLAG+i),read(0xbe+i),dkArray(DK_BOX+4*(i+1),4),read(DK_DY+i),read(DK_FORCE+i)
  end
 end
 return -1,-1,-1,{},-1,-1
end
dkContactCapture=function(event)
 if not playing or not active()or updates<3338 or updates>3385 then return end
 local s=emu.getState()
 local a,af,ay,abox,ady,force=dkPlatform(944)
 local b,bf,by,bbox=dkPlatform(880)
 local rect={};for i=0,7 do rect[#rect+1]=ram(2,0x3e+i)end
 local row={updates,event,phase,x(),read(0xbd),read(0x8e),read(0xa4),
  ram(2,0x210),ram(2,0x6b),ram(2,0x6c),ram(2,0x54),ram(2,0x76),ram(2,0x7b),ram(2,0x7e),
  ram(2,0x8f5),ram(2,0x8f7),ram(2,0x8f6),ram(2,0x8db),ram(2,0x8ea),ram(2,0x8eb),ram(2,0x8dd),
  rect,dkArray(DK_BOX,4),read(DK_PLAYER_BOX),read(0x6fc),ram(2,0x14),ram(2,0x15),
  a,af,ay,abox,ady,force,b,bf,by,bbox,
  s['cpu.pc'],s['cpu.sp'],s['cpu.a'],s['cpu.x'],s['cpu.y'],s['cpu.ps']or s['cpu.p']or-1,
  read(8),read(DK_BANK_A),read(DK_BANK_C)}
 local signature=json(row);if dkTraceLast[event]==signature then return end;dkTraceLast[event]=signature
 local rows=dkContactTrace.rows
 if #rows>=512 then table.remove(rows,129);dkContactTrace.dropped=dkContactTrace.dropped+1 end
 rows[#rows+1]=row
end
local function dkSourceProbe(pc,event,only944)
 emu.addMemoryCallback(guarded('DK contact trace '..event,function()
  if not mapped(pc,'nesWorkRam',3*8192+pc-0xa000)then return end
  if only944 then local i=emu.getState()['cpu.x'];if i>5 or pos(0x76,0x5d,i)~=944 then return end end
  dkContactCapture(event)
 end),emu.callbackType.exec,pc)
end
'''
    definitions='\n'+''.join(f'local {key}=0x{native[name]:x}\n'for key,name in(
        ('DK_FLAG','PlatformCollisionFlag'),('DK_BOX','BoundingBox_UL_Corner'),
        ('DK_PLAYER_BOX','Player_BoundBoxCtrl'),('DK_DY','Enemy_Y_Speed'),
        ('DK_FORCE','Enemy_Y_MoveForce'),('DK_BANK_A','CurrentBank'),('DK_BANK_C','CurrentBankC')))
    tail=definitions+tail
    for pc,event in points:
        tail+=f'dkSourceProbe(0x{pc:x},{json.dumps(event)},{str(event=="source-carry-before").lower()})\n'
    for pc in writers:
        tail+=f'''emu.addMemoryCallback(guarded('DK source state store',function()
 if mapped(0x{pc:x},'nesWorkRam',3*8192+0x{pc-0xa000:x})and emu.getState()['cpu.a']~=ram(2,0x6b)then dkContactCapture('state-store')end
end),emu.callbackType.exec,0x{pc:x})
'''
    for pc,offset,event in((position,position_offset,'native-position-entry'),
        (0xac18,71*8192+0xc18,'native-before-Y-store'),
        (0xac26,71*8192+0xc26,'native-after-Y-before-source'),
        (0xac29,71*8192+0xc29,'native-position-after')):
        tail+=f'''emu.addMemoryCallback(guarded('DK contact {event}',function()
 if not mapped(0x{pc:x},'nesPrgRom',{offset})then return end
 local i=emu.getState()['cpu.x'];if i<=5 and pos(0x76,0x5d,i)==944 then dkContactCapture('{event}')end
end),emu.callbackType.exec,0x{pc:x})
'''
    for pc,event in((0xb5c8,'foot-plane-before'),(0xb61c,'foot-plane-appended')):
        tail+=f'''emu.addMemoryCallback(guarded('DK {event}',function()
 if mapped(0x{pc:x},'nesWorkRam',3*8192+0x{pc-0xa000:x})and ram(2,0x8db)==3 then
  local i=ram(2,0x8f0);if i<=5 and pos(0x76,0x5d,i)==944 then dkContactCapture('{event}')end
 end
end),emu.callbackType.exec,0x{pc:x})
'''
    result=text+tail
    assert 'emu.write'not in result.replace('-- Exact e73 observational callbacks; no emu.write or controller changes.','')
    return result


if __name__=='__main__':
    from compose_dkjr_platform_contact_1113 import load_parent
    raw=load_parent()
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    text=controller(raw);LuaRuntime().compile(text)
    print(json.dumps(dict(passed=True,ROM_SHA256=P.PRINCE_PROPOSAL,
        base_controller_SHA256=P.FOURTH_CONTACT_CONTROLLER,observer_controller_SHA256=sha256(text.encode()).hexdigest(),
        window_Main=[3338,3385],row_cap=512,game_memory_writes=False,controller_policy_unchanged=True,
        output_files=0),separators=(',',':')),flush=True)
