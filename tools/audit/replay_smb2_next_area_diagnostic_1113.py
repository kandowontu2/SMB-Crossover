"""Passive next-area phase observation for the frozen private flag controller."""
from hashlib import sha256
import json

import replay_smb2_flag_handoff_1113 as Replay

BASE = '09c0f838b1c8f592d7a470f51892cafe03227dbd898e5c1b61d317fc1873c453'


def controller(image, variant=4):
    text = Replay.controller(image, variant)
    if variant == 4:
        assert sha256(text.encode()).hexdigest() == BASE
    W = Replay.Root.Base.W
    b = dict(W.Symbols.bundle(), raw=image)
    names = ('OperMode', 'OperMode_Task', 'ScreenRoutineTask',
             'DisableScreenFlag', 'ScreenTimer', 'IntervalTimerControl',
             'GamePauseStatus', 'NmiDisable', 'CrossoverTitleDrawn',
             'GameEngineSubroutine', 'AreaType', 'AreaAddrsLOffset',
             'AltEntranceControl', 'AltEntranceControl2', 'PlayerEntranceCtrl',
             'Player_OffscreenBits', 'Player_CollisionBits', 'GameTimerCtrlTimer',
             'FrameCounter', 'ScrollLock', 'ChangeAreaTimer',
             'ScreenLeft_X_Pos', 'ScreenLeft_PageLoc', 'CurrentBank',
             'CurrentBankC', 'Player_State', 'Player_Y_HighPos',
             'S2Health', 'S2MaxHealth', 'S2Ready', 'S2Variant')
    fields, missing = {}, []
    for name in names:
        try:
            fields[name] = W.address(b, name)
        except (KeyError, AssertionError):
            missing.append(name)
    text = 'local nextPhase={changes={},samples={},missing=' + json.dumps(','.join(missing)) + '}\n' + text
    needle = 'idle=smb2Idle'
    assert text.count(needle) == 1
    text = text.replace(needle, needle + ',next_phase=nextPhase')
    # The original formatter only used string-keyed records.
    needle = "string.format('%q',k)"
    assert text.count(needle) == 1
    text = text.replace(needle, "string.format('%q',tostring(k))")
    encoder = (W.R / 'tools/reference/karnov_ladder_native_1113.lua').read_text(encoding='utf-8')
    encoder = encoder[encoder.index("local alphabet="):]
    encoder = encoder[:encoder.index('emu.addEventCallback')]
    text += '\n' + encoder.replace('alphabet', 'phaseAlphabet').replace('base64', 'phaseBase64')
    text += '\nlocal phaseFields={' + ','.join(f'{k}={v}' for k, v in fields.items()) + '}\n'
    text += r'''
local phasePrevious,phaseUpdates,phaseStill,phaseCount=nil,-1,0,0
emu.addEventCallback(guard(function()
 if not game or done or r('WorldNumber')~=0 or r('LevelNumber')~=1 then return end
 local s=state();local q={s=s,fields={},pad=pad,pending=#pending}
 for k,at in pairs(phaseFields)do q.fields[k]=read(at)end
 local c=emu.getState();q.pc=c['cpu.pc'];q.sp=c['cpu.sp']
 for _,k in ipairs({'ppu.control','ppu.mask','ppu.scanline','ppu.cycle','cpu.nmi','cpu.irq'})do
  if c[k]~=nil then q[k]=c[k]end
 end
 local fingerprint=table.concat({q.fields.OperMode or -1,q.fields.OperMode_Task or -1,
  q.fields.ScreenRoutineTask or -1,q.fields.GameEngineSubroutine or -1,
  q.fields.DisableScreenFlag or -1,q.fields.GamePauseStatus or -1,
  q.fields.NmiDisable or -1,s.area},':')
 if fingerprint~=phasePrevious then
  phaseCount=phaseCount+1;assert(phaseCount<=64,'Bounded phase changes')
  nextPhase.changes[tostring(phaseCount)]=q;phasePrevious=fingerprint
 end
 if frames%100==0 then
  nextPhase.samples[tostring(frames)]=q
  for k,_ in pairs(nextPhase.samples)do if tonumber(k)<frames-700 then nextPhase.samples[k]=nil end end
 end
 nextPhase.last=q
 if updates==phaseUpdates then phaseStill=phaseStill+1 else phaseStill=0;phaseUpdates=updates end
 if phaseStill>=600 then
  q.mapping={};q.stack={};q.pc_bytes={};q.cpu={}
  for _,at in ipairs({0x8000,0xa000,0xc000,0xe000,q.pc})do
   local mapped=emu.convertAddress(at)
   q.mapping[tostring(at)]=mapped and {address=mapped.address,memType=mapped.memType}or'none'
  end
  for at=0x100+q.sp+1,0x1ff do q.stack[tostring(at)]=read(at)end
  for at=q.pc-8,q.pc+15 do q.pc_bytes[tostring(at)]=read(at)end
  for k,v in pairs(c)do if k:sub(1,4)=='cpu.'then q.cpu[k]=v end end
  local png=emu.takeScreenshot()
  assert(type(png)=='string'and png:sub(1,8)=='\137PNG\r\n\26\n'and #png<=4*1024*1024,'One bounded in-memory phase PNG')
  nextPhase.image={frame=frames,bytes=#png};print('SMB_NATIVE_IMAGE '..phaseBase64(png))
  finish(false,'passive-next-area-no-returned-Main600')
 end
end),emu.eventType.endFrame)
'''
    Replay.Root.Base.LuaRuntime().compile(text)
    assert all(word not in text for word in ('emu.write', 'emu.setState', 'io.open', 'loadState', 'saveState'))
    return text
