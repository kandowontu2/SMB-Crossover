"""Stage exact cold-linked Prince support and a controller-only native replay."""

import argparse
import json
from pathlib import Path
import re
import shutil
import sys

import check_prince_run_support_funded_irq_1110 as Qualification
from deliver_helper_camera_render_1110 import bindings
from observe_chip_committed_write import lua
from prepare_prince_full11_1110 import once
from prepare_selected_native_packet_v1 import prepare, sha


F,Current,P,R = Qualification.F,Qualification.Current,Qualification.P,Qualification.R
PIN = '50a66487c6e0e496e62e19b5b38ca0ee4da350163aece39c59d8e2be5a78cc21'
IRQ = Qualification.FUNDED.with_name('irq-linked.json')
IRQ_PIN = '6bfebbfab86e2080f16cc2691582b4cdd216d9c0043016447dfe1e70e135b40d'
DELIVERY = R/'build/mini-shared-game-loop-tail-delivery-1110/verified-delivery.json'
DELIVERY_PIN = 'ed3b32566d5ee1e9c39f146dd2f4e13099c7dd564a635b110d75bc68f866fe55'
OLD = R/'build/prince-full11-native-1110-v5'
OLD_READY_PIN = '5dff426fc9f24903cf8239ec622a7e7eca15ace59465121bac93f78139b16576'
SOURCE = OLD/'controller.lua'
LUA_DEPS = R/'build/smb2-final62-observer-lua-deps-v1'
RUNNER = R/'tools/audit/run_bounded_build_v1.py'
OLD_RUNNER_PIN = 'eb331ec122dd933d83eb2e0b217e0ca7be7ccf16e9c35d7e22231ce076d8b643'
RUNNER_PIN = 'e673791aac1dba6af0a6f896dc634b78bbe25387eca3ca247df276d455ccb32d'

WITNESS = r'''
route.third_support={}
local function writeThird(ok,why,cleared)
 if route.third_witness_written then return end
 writejson('third-pipe.json',{passed=ok,reason=why,controller_only=true,emulated_writes=false,
  ROM_sha256=Q.ROM_sha256,left=736,right=768,top=144,physical_support=route.on_top,
  original_hang=route.hang,source_support_publications=route.third_support,far_side=cleared,
  terminal=state(),Main=admitted,frame=frame,initial_lives=initialLives,final_lives=r('NumberofLives')})
 route.third_witness_written=true
end
'''

PUBLICATION = r'''
local supportPublicationPC,supportPublicationBytes=BOUND_SUPPORT_PUBLICATION
emu.addMemoryCallback(function()
 if part~='full11' or route.index~=2 or not sourceActive() or #route.third_support>=8 then return end
 local mapped=emu.convertAddress(supportPublicationPC)
 if not mapped or mapped.memType~=emu.memType.nesWorkRam or mapped.address~=2*8192+supportPublicationPC-0xc000 then return end
 local b=state()
 if b.world_x<720 or b.world_x>=768 then return end
 headers()
 for i,v in ipairs(supportPublicationBytes)do
  assert(ram(supportPublicationPC+i-1)==v,'Exact cold-backed D297 publication bytes')
 end
 local cpu=emu.getState();local sp=cpu['cpu.sp']
 -- The worker keeps one PHP byte on the stack until its matching PLP.
 local caller=(ram(0x100+(sp+2)%256)+256*ram(0x100+(sp+3)%256)+1)%65536
 assert(caller==0xa6f9,'Actual original D297 support caller')
 local qx=ram(0xb369)+256*ram(0xb36a);local roofY=ram(0xb36b)+256*ram(0xb36c)
 local atCap,tile=solid(qx,roofY+1)
 assert(cpu['cpu.a']==144 and roofY==143 and atCap and tile&0xfc==0x10 and not solid(qx,roofY),
  'Actual D297 publication reads a typed exposed 64px native pipe cap')
 assert(b.source_action==1 and (b.source_mode==1 or b.source_mode==255) and r('Player_State')==0
  and b.native_y_high==1 and b.native_y==112 and b.physical_foot==145
  and ps(0x86)+256*ps(0x87)==b.physical_foot and qx==b.world_x+(b.source_facing==0 and 2 or 13),
  'Original standing/running state retained on genuine native foot support')
 local q={Main=admitted,frame=frame,before=b,caller=caller,query_x=qx,roof_y=roofY,cap_tile=tile}
 route.third_support[#route.third_support+1]=q
 -- Install the matched return with the stack pointer expected after PLP.
 route.third_support_pending={observation=q,sp=(sp+3)%256}
end,emu.callbackType.exec,supportPublicationPC)
emu.addMemoryCallback(function()
 local p=route.third_support_pending
 if not p or emu.getState()['cpu.sp']~=p.sp then return end
 local mapped=emu.convertAddress(0xa6f9)
 if not mapped or mapped.memType~=emu.memType.nesWorkRam or mapped.address~=3*8192+0x6f9 then return end
 route.third_support_pending=nil
 local a=state();local b=p.observation.before
 local surface=ps(0x7f)+256*ps(0x80)
 assert(emu.getState()['cpu.a']==1 and surface==144 and a.source_x==b.source_x and a.source_y==b.source_y
  and a.physical_foot==b.physical_foot and a.native_y==b.native_y and a.world_x==b.world_x,
  'Actual original D297 return publishes support without changing source motion')
 p.observation.after=a;p.observation.surface=surface
end,emu.callbackType.exec,0xa6f9)
'''


def controller(old_pin,cookie,worker,address):
    source = SOURCE.read_text(encoding='utf-8')
    source = once(source,old_pin,PIN)
    old_cookie, = re.findall(r'(?m)^Q\.cookie=\{[\d,]+\}$',source)
    source = once(source,old_cookie,'Q.cookie='+lua(list(cookie)))
    publication = bytes.fromhex('8d7fc0a9008d80c028a90160')
    assert worker.count(publication)==1
    pc = address+worker.index(publication)
    source = once(source,'local function routeWrite(ok,why)',WITNESS+'\nlocal function routeWrite(ok,why)\n'
                  " if not route.third_witness_written then writeThird(false,why,nil) end")
    anchor = 'local function runReady(s)'
    witness = once(PUBLICATION,'BOUND_SUPPORT_PUBLICATION',f'{pc},{lua(list(publication))}')
    source = once(source,anchor,witness+'\n'+anchor)
    anchor = "  routeLog('supported-far-side')"
    source = once(source,anchor,'''  if o.kind=='pipe' and o.left==736 then
   local last=route.third_support[#route.third_support]
   if not last or not last.after or route.third_support_pending or not route.hang or s.native_y~=176 then
    routeFail('Third pipe lacks original ledge, D297 publication or grounded far-side witness')
   end
   writeThird(true,'Actual original ledge and D297 support crossed the 64px native pipe',route.clears[#route.clears])
  end
'''+anchor)
    assert 'emu.write(' not in source
    assert 'Native descent projection, donor landing and both hardware views were observed' in source
    sys.path.insert(0,str(LUA_DEPS))
    from lupa.lua54 import LuaRuntime

    assert LuaRuntime().eval('function(s) local f,e=load(s); assert(f,e); return true end')(source)
    return source,pc


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    out = cli.parse_args().output.resolve()
    assert out.is_relative_to(R/'build') and out!=R/'build'
    assert not out.exists() or not any(out.iterdir())
    assert sha(DELIVERY)==DELIVERY_PIN and sha(Qualification.FUNDED)==Qualification.FUNDED_PIN and sha(IRQ)==IRQ_PIN
    delivery,proof,irq = (Current.read(path) for path in (DELIVERY,Qualification.FUNDED,IRQ))
    assert delivery['Downloads_launch_verified'] and delivery['IPS_roundtrip'] and not delivery['backup_created']
    assert sha(Path(delivery['destination']))==delivery['ROM_SHA256']==proof['parent_SHA256']==Current.BASE_PIN
    assert proof['passed'] and irq['passed'] and proof['expected_memory_only_SHA256']==irq['expected_memory_only_SHA256']==PIN
    assert irq['bad_header_bytes_rejected']==32 and irq['cold_linked_route']['actual_linked_cold']
    for doc in (proof,irq):
        assert doc['ROM_written'] is False and doc['Mesen_run'] is False
        bindings(doc['bindings'])

    old_ready = OLD/'ready.json'
    assert sha(old_ready)==OLD_READY_PIN
    ready,negative,binding = (Current.read(path) for path in (old_ready,Current.NATIVE,OLD/'capture/binding.json'))
    assert ready['ROM_sha256']==negative['ROM_sha256']==binding['ROM_sha256']==sha(Path(ready['ROM']))
    assert not negative['passed'] and negative['route']['index']==2 and binding['exit_code']!=0
    assert binding['ready_sha256']==OLD_READY_PIN and ready['emulated_writes'] is False
    old_bindings = dict(ready['bindings'])
    assert old_bindings.pop(str(RUNNER.resolve()))==OLD_RUNNER_PIN and sha(RUNNER)==RUNNER_PIN
    bindings(old_bindings)

    out.mkdir(exist_ok=True)
    before,_,_ = Current.current()
    seed,_ = P.Q.C.C.cold(before,38)
    raw,patches,_,cookie,layout,worker = F.fit(out,before,seed)
    assert P.sha(raw)==PIN and patches==proof['patches'] and layout==proof['layout']
    assert cookie.hex()==proof['Prince_cookie'] and Current.apply(Current.BASE.read_bytes(),patches)==raw
    text,publication_pc = controller(ready['ROM_sha256'],cookie,worker,layout['support_half_open'][0])
    print('Exact existing carrier recompression, cookie and Lua syntax passed.',flush=True)

    rom = out/'prince-private.nes'
    rom.write_bytes(raw)
    assert sha(rom)==PIN
    metadata = set()
    for suffix in ('.lbl','.dbg'):
        parent,previous = Current.BASE.with_suffix(suffix),Path(ready['ROM']).with_suffix(suffix)
        assert parent.read_bytes()==previous.read_bytes()
        shutil.copyfile(parent,rom.with_suffix(suffix))
        metadata.update((parent,previous))
    manifest = out/'candidate.json'
    refs = {Path(__file__),DELIVERY,Qualification.FUNDED,IRQ,old_ready,Current.NATIVE,OLD/'capture/binding.json',
            *metadata,*map(Path,proof['bindings']),*map(Path,irq['bindings']),*map(Path,ready['bindings'])}
    receipt = dict(passed=True,private=True,ROM_written=True,Mesen_run=False,native_pending=True,
                   parent_SHA256=Current.BASE_PIN,candidate_SHA256=PIN,Prince_cookie=cookie.hex(),patches=patches,
                   compressed_layout=layout,source_support_publication_CPU=publication_pc,
                   controller_only=True,stage_goal='1-1 to active 1-2',third_pipe_receipt='third-pipe.json',
                   bounded_runner_rebound=dict(historical_SHA256=OLD_RUNNER_PIN,current_SHA256=RUNNER_PIN),
                   bindings={str(path.resolve()):sha(path) for path in sorted(refs)})
    manifest.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    prepare(out/'native',rom,text,refs|{manifest},expected=PIN,timeout=ready['timeout'],
            scope='Original Prince full 1-1 controller with separate real third-pipe support and crossing witness.',
            allow_interactive=ready['allow_interactive'])
    assert sum(path.is_file() for path in out.rglob('*'))==7


if __name__=='__main__':
    main()
