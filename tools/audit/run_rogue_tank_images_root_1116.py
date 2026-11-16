"""Two passive RAM screenshots over the native-qualified Rogue tank route."""
from hashlib import sha256
from pathlib import Path
import json
import replay_rogue_natural_tank_1327_1116 as F
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from mesen_session_guard_v1 import require_free_workspace
from run_stdout_mesen_1110 import run

OUT = F.R/'build/smb2-flag-native-1113'
BASE_FACTORY = 'd6366b1f77ee08e9a0edef33400ebc9c5548c24d517db4a3e2189454e2517fb6'
BASE_LUA = '0fe0bd5ee083207be58aa03346b54018ea3627e68dca3ff302b08ba3441cff4e'
NATIVE = 'c9f17c32b7be315890f05e61179e798b1d2386b047e6fa34e64dc4ec542d6ccb'

OBSERVER = r'''
local visualWait
local function visualBase64(bytes)
 local chars='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
 local out={}
 for i=1,#bytes,3 do
  local a,b,c=bytes:byte(i),bytes:byte(i+1),bytes:byte(i+2)
  local n=(a<<16)|((b or 0)<<8)|(c or 0)
  for _,shift in ipairs({18,12})do local j=(n>>shift)&63;out[#out+1]=chars:sub(j+1,j+1)end
  local j=(n>>6)&63;out[#out+1]=b and chars:sub(j+1,j+1)or'='
  j=n&63;out[#out+1]=c and chars:sub(j+1,j+1)or'='
 end
 return table.concat(out)
end
emu.addEventCallback(guard(function()
 if finished or not first or not active()or#visual.pictures>=2 then return end
 local tag
 if#visual.pictures==0 and mature and not collector then
  visualWait=visualWait or frame
  if frame-visualWait>=2 then tag='Mature Rogue energy tank'end
 elseif#visual.pictures==1 and credit then tag='Earned tank and resumed Rogue'end
 if not tag then return end
 local png=emu.takeScreenshot()
 assert(type(png)=='string'and png:sub(1,8)=='\137PNG\13\10\26\10'and#png<=65536,'Bounded actual RAM PNG')
 local palette={};for at=0x3f00,0x3f1f do palette[#palette+1]=emu.read(at,emu.memType.nesPpuDebug)end
 local oam={};for slot=0,63 do
  local at=slot*4;local y=emu.read(at,emu.memType.nesSpriteRam)
  if y<240 and#oam<32 then oam[#oam+1]={slot=slot,y=y,tile=emu.read(at+1,emu.memType.nesSpriteRam),attributes=emu.read(at+2,emu.memType.nesSpriteRam),x=emu.read(at+3,emu.memType.nesSpriteRam)}end
 end
 visual.pictures[#visual.pictures+1]={tag=tag,frame=frame,Main=updates,state=state(),PNG_bytes=#png,palette=palette,oam=oam}
 print('SMB_NATIVE_IMAGE '..visualBase64(png))
end),emu.eventType.endFrame)
'''


def controller(raw):
    assert F.H(Path(F.__file__).read_bytes()) == BASE_FACTORY
    source = F.controller(raw)
    assert F.H(source.encode()) == BASE_LUA
    old, new = 'ROGUE_STOCK_RECEIPT ', 'SMB_NATIVE_RECEIPT '
    assert source.count(old) == 1 and new not in source
    base = source.replace(old, new, 1)
    edits = [
        ('if finished then return end;finished=true',
         "if finished then return end;if reason=='natural-tank-credit-and25workers'then assert(#visual.pictures==2,'Both actual pictures')end;finished=true"),
        ('Mesen_images=0}', 'Mesen_images=2,visual=visual}'),
    ]
    text = base
    for a, b in edits:
        assert text.count(a) == 1
        text = text.replace(a, b, 1)
    restored = text
    for a, b in reversed(edits):
        restored = restored.replace(b, a, 1)
    assert restored == base
    text = 'local visual={pictures={}}\n'+text+'\n'+OBSERVER
    F.LuaRuntime().compile(text)
    return text


def main():
    raw = F.ROM.read_bytes()
    assert F.H(raw) == F.PIN
    before = check(F.ROM)
    assert not before['matching_patch_files']
    assert {p.name for p in OUT.iterdir() if p.is_file()} == {'candidate.nes', 'controller.lua'}
    assert (OUT/'candidate.nes').read_bytes() == raw
    text = controller(raw)
    Storage.preflight(private_root=OUT, fresh=True)
    require_free_workspace(F.R, F.ROM, allow_interactive=True)
    script = OUT/'controller.lua'
    script.write_bytes(text.encode())
    q = run(script, F.ROM, OUT/'capture', F.PIN, 180)
    assert F.ROM.read_bytes() == (OUT/'candidate.nes').read_bytes() == raw
    assert check(F.ROM) == before and q['outputs_written'] == 0
    functional = dict(q['receipt'])
    functional.pop('visual', None)
    functional['Mesen_images'] = 0
    digest = sha256(json.dumps(functional, sort_keys=True).encode()).hexdigest()
    report = {k: v for k, v in q.items() if k not in ('images', 'capture_preflight')}
    report.update(actual_Downloads=True, functional_receipt_SHA256=digest,
                  exact_functional_match=digest == NATIVE,
                  image_metadata=[{k: v for k, v in im.items() if k != 'base64'} for im in q['images']])
    for im in q['images']:
        assert im['bytes'] <= 65536
        print('IMAGE '+json.dumps(im, separators=(',', ':')), flush=True)
    print('RESULT '+json.dumps(report, separators=(',', ':')), flush=True)
    assert q['passed'] and len(q['images']) == 2 and digest == NATIVE


if __name__ == '__main__':
    main()
