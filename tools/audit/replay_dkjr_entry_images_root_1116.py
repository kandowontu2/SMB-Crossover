"""Two passive in-memory entry pictures over the frozen strong DK Jr route."""
from hashlib import sha256
from pathlib import Path

import replay_dkjr_forced_entry_current_1116 as Base
from check_ff_stdout_controller_source_1110 import LuaRuntime

C = Base.C
H = lambda value: sha256(value).hexdigest()
BASE_SHA = '1caa3929abf8ff82d53e735d2c5e5620230abcc81f17aa2515cdbf3fa40c3a73'

DECL = '''local entryImages={}
local function entryPNG64(bytes)
 local alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
 local out={}
 for i=1,#bytes,3 do
  local a,b,c=bytes:byte(i),bytes:byte(i+1),bytes:byte(i+2)
  local n=(a<<16)|((b or 0)<<8)|(c or 0)
  for _,shift in ipairs({18,12})do local j=(n>>shift)&63;out[#out+1]=alphabet:sub(j+1,j+1)end
  local j=(n>>6)&63;out[#out+1]=b and alphabet:sub(j+1,j+1)or'='
  j=n&63;out[#out+1]=c and alphabet:sub(j+1,j+1)or'='
 end
 return table.concat(out)
end
'''

OBSERVER = '''emu.addEventCallback(guarded('entry pictures',function()
 if read(0x764)~=0 or read(0x761)~=1 or read(0x753)~=2 or read(0x6002)~=40 or
  read(0x771)~=1 or read(0x773)~=3 or read(0x0f)~=8 then return end
 local ready,y=ram(2,0x8fe),read(0xbd)
 local tag
 if #entryImages==0 and ready==1 and read(0x1e)==2 and y>=88 and y<=144 then tag='native pending fall'
 elseif #entryImages==1 and ready==2 and originalWorkGrounded>=8 then tag='grounded original work' end
 if not tag then return end
 assert(#entryImages<2,'At most two in-memory PNGs')
 local png=emu.takeScreenshot()
 assert(type(png)=='string'and png:sub(1,8)=='\\137PNG\\13\\10\\26\\10'and#png<=65536,'Actual bounded PNG')
 entryImages[#entryImages+1]={tag=tag,ready=ready,x=x(),y=y,sourceY=ram(2,0x210),
  originalGrounded=originalWorkGrounded,PNG_bytes=#png}
 print('SMB_NATIVE_IMAGE '..entryPNG64(png))
end),emu.eventType.endFrame)
'''


def controller(raw):
    assert H(Path(Base.__file__).read_bytes()) == BASE_SHA
    base = Base.controller(raw)
    marker = "emu.addEventCallback(guarded('frame',function()"
    edits = [
        ('local function finish(ok,why)\n if done then return end\n',
         'local function finish(ok,why)\n if done then return end\n'
         " if ok then assert(#entryImages==2,'Both actual pending and grounded images')end\n"),
        ('events=events,', 'entry_images=entryImages,events=events,'),
        (marker, OBSERVER+marker),
    ]
    text = DECL+base
    for before, after in edits:
        assert text.count(before) == 1, before
        text = text.replace(before, after, 1)
    restored = text[len(DECL):]
    for before, after in reversed(edits):
        assert restored.count(after) == 1
        restored = restored.replace(after, before, 1)
    assert restored == base, 'Passive observer removal recovers exact strong-route controls'
    assert not any(token in text for token in ('emu.write', 'emu.setState', 'io.open', 'loadState', 'saveState'))
    LuaRuntime().compile(text)
    return text
