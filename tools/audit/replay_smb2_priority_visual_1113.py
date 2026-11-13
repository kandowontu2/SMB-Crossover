"""Two bounded in-memory views appended to unchanged ordinary SMB2 controls."""
from hashlib import sha256

import replay_smb2_pipe_priority_1113 as Parent


def controller(raw, variant=4):
    assert sha256(raw).hexdigest() == Parent.C.CANDIDATE
    text = Parent.controller(raw, variant)
    W = Parent.Parent.Flag.Root.Base.W
    bundle = dict(W.Symbols.bundle(), raw=raw)
    sprite_attribute = W.address(bundle, 'Player_SprAttrib')
    text = 'local priorityImages={}\n' + text
    needle = 'capture_files=0,runtime_state_writes=0'
    assert text.count(needle) == 1
    text = text.replace(needle, 'capture_files=0,image_tags=priorityImages,runtime_state_writes=0')
    source = (W.R / 'tools/reference/karnov_ladder_native_1113.lua').read_text(encoding='utf-8')
    encoder = source[source.index('local alphabet='):]
    encoder = encoder[:encoder.index('emu.addEventCallback')]
    text += '\n' + encoder.replace('alphabet', 'priorityAlphabet').replace('base64', 'priorityBase64')
    text += f'\nlocal priorityAttributeAddress={sprite_attribute}\n'
    text += r'''
local function priorityShot(tag)
 assert(not priorityImages[tag],'Each view is captured only once')
 local png=emu.takeScreenshot()
 assert(type(png)=='string'and png:sub(1,8)=='\137PNG\r\n\26\n'and #png<=4*1024*1024,'Bounded in-memory PNG')
 priorityImages[tag]={s=state(),attribute=read(priorityAttributeAddress),bytes=#png,next_area_updates=nextUpdates}
 print('SMB_NATIVE_IMAGE '..priorityBase64(png))
end
emu.addEventCallback(guard(function()
 if not game or done or r('WorldNumber')~=0 or r('LevelNumber')~=1 then return end
 if not priorityImages.side_pipe and r('AreaType')==1 and r('GameEngineSubroutine')==7
  and read(priorityAttributeAddress)&32~=0 and x()>=155 and x()<=170 then priorityShot('side_pipe')end
 if not priorityImages.underground_grounded and r('AreaType')==2 and active()
  and nextUpdates>=20 and nextUpdates<25 then priorityShot('underground_grounded')end
end),emu.eventType.endFrame)
'''
    Parent.Parent.Flag.Root.Base.LuaRuntime().compile(text)
    assert all(word not in text for word in ('emu.write', 'emu.setState', 'io.open', 'loadState', 'saveState'))
    return text
