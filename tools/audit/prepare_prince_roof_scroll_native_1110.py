"""Rebind the qualified Prince right-edge repair to the exact c8bd image."""

import argparse
from collections import Counter
import json
from pathlib import Path
import shutil
import sys

import check_prince_roof_scroll_seam_1110 as Seam
from deliver_helper_camera_render_1110 import bindings
from observe_chip_committed_write import lua
from prepare_prince_full11_1110 import once
from prepare_selected_native_packet_v1 import prepare, sha


R, P, I, N, Current = Seam.R, Seam.P, Seam.I, Seam.N, Seam.Current
BASE = R/'build/mini-contact-platform-combo-native-1110/candidate.nes'
BASE_PIN = 'c8bd2e2c75015b84fe7bc3c4dba5b24b87e517620ef914ff229b5d4249acbe48'
BASE_MANIFEST = '7d3a9021a3612b5cfc4e10f98908a4882ca4d33d745f5b42ef394d1e620d38f6'
BASE_PROOF = '9bb145df9aff1a33107d5e49bfc4fad1935df8f29fea3cf01f5baddebf556916'
OLD = Seam.ROM.with_name('candidate.json')
OLD_PIN = '4bfac88e6736fc101e4c26cf981af006ee9a25bb34314b4b39be58bd047bc366'
EDGE = R/'build/prince-roof-scroll-seam-1110/proof.json'
EDGE_PIN = '443fbf3b7c882b9440c1bda2959573ba73a462d186a38e2ec15a0a9156cc1531'
MINUS_PIN = '639c8861cb8702cd49509b5c708922a82ffc6424a5ca674e32357065968f3d8b'
PIN = '4699c73befdd331b7e49a8b992a4f15f52d14eed81ac2d76f3b69c63ba3c846e'
V2 = Seam.NATIVE.parent
V2_PINS = {'ready.json':'31a64c632699335023bef6dc0c25bc44cb2845ed9f66abfe201c37956d6d7932',
           'controller.lua':'a81b0f8b9faeb8d5df81cb10664bda359aa03aa686f92bb2df0553271662f2ed',
           'capture/binding.json':'106a16532257f59cb7dd5b2bd0830e0f5e0309142b6cec0d155dff0b70ac408b'}


OBSERVER = r'''
local scrollTrace={raw_samples={},writes={},right_clamps={},pose40={}}
local pendingRaw,pendingStore,lastExport=nil,nil,nil
local function scrollSample()
 return part=='full11' and route.index==2 and route.third_jump and sourceActive()
  and r('GameEngineSubroutine')==8 and ps(0x616)==4
end
local function currentEdges()
 return ram(0x71f)+256*ram(0x71d),ram(0x720)+256*ram(0x71e)
end
local function scrollSnapshot(cpu)
 local left,right=currentEdges()
 return {Main=admitted,frame=frame,PC=cpu['cpu.pc'],A=cpu['cpu.a'],Y=cpu['cpu.y'],SP=cpu['cpu.sp'],
         native_x=wx(),native_y=r('Player_Y_Position'),source_x=ps(0x60f)+256*ps(0x610),
         source_pose=ps(0x617),source_sole=ps(0x84)+256*ps(0x85),camera_left=left,camera_right=right,
         scroll=ram(0x75a),raw_bits=ram(3)}
end
local scrollHooks=BOUND_SCROLL_HOOKS
local function scrollExec(name,callback)
 local h=scrollHooks[name]
 emu.addMemoryCallback(function()
  if not scrollSample() then return end
  local mapped=emu.convertAddress(h.pc)
  if not mapped or mapped.memType~=emu.memType[h.memory] or mapped.address~=h.physical then return end
  equal(bytes(h.pc,#h.bytes),h.bytes,'Exact physical Prince roof scroll opcode')
  callback(emu.getState())
 end,emu.callbackType.exec,h.pc)
end
scrollExec('raw',function(cpu)
 local q=scrollSnapshot(cpu)
 pendingRaw=q
 if #scrollTrace.raw_samples<80 then scrollTrace.raw_samples[#scrollTrace.raw_samples+1]=q end
 if q.source_pose==40 and #scrollTrace.pose40<12 then scrollTrace.pose40[#scrollTrace.pose40+1]=q end
 if q.A==255 and q.Y==1 and ((q.native_x-q.camera_right)&0xffff)>0
    and ((q.native_x-q.camera_right)&0xffff)<128 then
  q.expected_right=true
  if lastExport and lastExport.frame==q.frame and lastExport.Main==q.Main then q.source_export=lastExport end
 end
end)
local function expectStore(kind,cpu)
 local row=scrollSnapshot(cpu)
 row.kind=kind
 local clamp=kind=='clamp_x' or kind=='clamp_page'
 if clamp and pendingRaw and pendingRaw.Main==admitted and pendingRaw.frame==frame then
  if pendingRaw.expected_right then
   local expected=(pendingRaw.camera_right-16)&0xffff
   assert(row.Y==1 and row.A==(kind=='clamp_x' and expected%256 or expected//256),
    'Raw right-overflow selects the ordinary native right clamp and exact store byte')
  end
 end
 pendingStore=row
end
for _,kind in ipairs({'export_x','export_page','clamp_x','clamp_page'}) do
 scrollExec(kind,function(cpu)expectStore(kind,cpu)end)
end
local function scrollWrite(address,value)
 local q=pendingStore
 if not q then return end
 pendingStore=nil
 local writesX=q.kind=='export_x' or q.kind=='clamp_x'
 assert(address==(writesX and L.Player_X_Position or L.Player_PageLoc) and q.A==value,
        'Actual CPU bus write matches the bound native/source STA')
 q.address=address;q.value=value
 if #scrollTrace.writes<160 then scrollTrace.writes[#scrollTrace.writes+1]=q end
 if q.kind=='export_x' then lastExport={frame=frame,Main=admitted,x=q,source_x=q.source_x} end
 if q.kind=='export_page' and lastExport and lastExport.Main==admitted and lastExport.frame==frame then
  lastExport.page=q;lastExport.world_x=lastExport.x.value+256*value
 end
 if q.kind=='clamp_x' and pendingRaw and pendingRaw.Main==admitted and pendingRaw.frame==frame then pendingRaw.x_write=q end
 if q.kind=='clamp_page' and pendingRaw and pendingRaw.Main==admitted and pendingRaw.frame==frame then
  pendingRaw.page_write=q
  assert(pendingRaw.x_write,'Native clamp page write follows its position write')
  pendingRaw.committed_x=pendingRaw.x_write.value+256*value
  if pendingRaw.expected_right then
   assert(pendingRaw.committed_x==((pendingRaw.camera_right-16)&0xffff),'Actual right clamp committed to screen right−16')
   if #scrollTrace.right_clamps<24 then scrollTrace.right_clamps[#scrollTrace.right_clamps+1]=pendingRaw end
  end
  pendingRaw=nil
 end
end
emu.addMemoryCallback(scrollWrite,emu.callbackType.write,L.Player_X_Position)
emu.addMemoryCallback(scrollWrite,emu.callbackType.write,L.Player_PageLoc)
'''


def inputs():
    parent_meta, parent_proof = BASE.with_suffix('.json'), BASE.with_name('proof.json')
    expected = {BASE:BASE_PIN, parent_meta:BASE_MANIFEST, parent_proof:BASE_PROOF,
                OLD:OLD_PIN, EDGE:EDGE_PIN, **{V2/k:v for k,v in V2_PINS.items()}}
    for path,pin in expected.items():
        assert sha(path)==pin,path
    parent, mini, prince, edge, ready, failed = (Current.read(p) for p in (
        parent_meta,parent_proof,OLD,EDGE,V2/'ready.json',V2/'capture/binding.json'))
    assert parent['passed'] and mini['passed'] and prince['passed'] and edge['passed']
    assert parent['candidate_SHA256']==mini['candidate_SHA256']==BASE_PIN
    assert parent['composed_proof_SHA256']==BASE_PROOF
    assert edge['parent_SHA256']==prince['candidate_SHA256']==ready['ROM_sha256']==Seam.Stage.PIN
    assert failed['ROM_sha256']==Seam.Stage.PIN and failed['ready_sha256']==V2_PINS['ready.json']
    assert failed['exit_code']!=0 and ready['emulated_writes'] is False
    bindings(ready['bindings'])
    for file,pin in edge['bindings'].items():
        assert sha(R/file)==pin,file
    assert len(prince['patches'])==24 and len(edge['patches'])==1
    assert Current.apply(Current.BASE.read_bytes(),prince['patches'])==Seam.ROM.read_bytes()
    before = Current.apply(BASE.read_bytes(),prince['patches'])
    assert P.sha(before)==MINUS_PIN
    template,_,_ = Current.current()
    before = dict(template,raw=before)
    after, change = Seam.patch(before)
    assert change==edge['patches'][0] and P.sha(after['raw'])==PIN
    extents = [(p['offset'],p['offset']+len(bytes.fromhex(p['preimage'])))
               for p in prince['patches']+[change]]
    extents.sort()
    assert all(hi<=lo2 for (_,hi),(lo2,_) in zip(extents,extents[1:]))
    assert all(BASE.with_suffix(s).read_bytes()==Seam.ROM.with_suffix(s).read_bytes() for s in ('.dbg','.lbl'))
    return before,after,prince,edge,ready,set(expected)


def cleanup(model):
    for name in ('writes','ram_writes','ppu_log','blocked'):
        getattr(model,name).clear()


def state(model):
    # Bypass the model's side-effecting hardware reads for the RAM snapshot.
    return (bytes(list.__getitem__(model,slice(0,0x8000))),
            {key:value for key,value in model.__dict__.items() if key!='bundle'})


def paired_steps(before, after, seed):
    env, start, labels = P.Q.first8(before,seed)
    cleanup(start)
    report = {}
    for target, count in (('GameCoreRoutine',48),('GameLoop',64)):
        pair = [N.fork(start),N.fork(start)]
        pair[1].bundle = after
        for slot,tag in enumerate(pair[1].rawtags):
            if tag&128:
                pair[1].raw_page(slot,tag)
        deltas = Counter()
        for epoch in range(count):
            pad = 1 if epoch<32 else 0 if epoch<40 else 2
            rows = []
            for model in pair:
                cleanup(model)
                model.controller_pad = pad
                N.put(model,SavedJoypad1Bits=pad,SavedJoypadBits=pad)
                if target=='GameCoreRoutine':
                    N.put(model,FrameCounter=epoch)
                rows.append(env['run'](model,target,labels))
            assert rows[0]['regs']==rows[1]['regs'] and state(pair[0])==state(pair[1]),(target,epoch)
            deltas[rows[0]['CPU']-rows[1]['CPU']] += 1
        end = Current.row(pair[1],count)
        assert end['engine']==8 and end['hp']==5 and end['lives']==2 and end['source_x']>40
        report[target] = dict(steps=count,all_live_state_and_ordered_writes_exact=True,
                              cycle_deltas=sorted(deltas.items()),end=end)
    return report


def controller(final, seed):
    hooks = {}
    for key,pc,code in (('raw',0xaa44,Seam.NEW),('clamp_x',0xaa59,b'\x85\x75'),
                        ('clamp_page',0xaa60,b'\x85\x5c')):
        physical = 8192+pc-0xa000
        assert final[16+physical:16+physical+len(code)]==code
        hooks[key] = dict(pc=pc,memory='nesPrgRom',physical=physical,bytes=list(code))
    for key,pc,code in (('export_x',0xc3a9,b'\x85\x75'),('export_page',0xc3ae,b'\x85\x5c')):
        start = pc-0xc000
        assert seed.ram[2][start:start+len(code)]==code
        hooks[key] = dict(pc=pc,memory='nesWorkRam',physical=16384+start,bytes=list(code))
    old = (V2/'controller.lua').read_text(encoding='utf-8')
    text = once(old,Seam.Stage.PIN,PIN)
    anchor = 'route.third_support={}\n'
    observer = once(OBSERVER,'BOUND_SCROLL_HOOKS',lua(hooks))
    text = once(text,anchor,anchor+observer)
    field = '  roof_jump=route.third_jump,terminal=state(),'
    text = once(text,field,'  roof_jump=route.third_jump,scroll_writer=scrollTrace,terminal=state(),')
    assert text.replace(observer,'').replace('scroll_writer=scrollTrace,','').replace(PIN,Seam.Stage.PIN)==old
    assert 'emu.write(' not in text
    sys.path.insert(0,str(Seam.Stage.LUA_DEPS))
    from lupa.lua54 import LuaRuntime
    assert LuaRuntime().eval('function(s) local f,e=load(s); assert(f,e); return true end')(text)
    return text,hooks


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    out = cli.parse_args().output.resolve()
    assert out.is_relative_to(R/'build') and out!=R/'build'
    assert not out.exists() or not any(out.iterdir())
    before,after,prince,edge,ready,refs = inputs()
    seed,_ = P.Q.C.C.cold(before,38)
    final_seed,_ = P.Q.C.C.cold(after,38)
    cookie = bytes.fromhex(prince['Prince_cookie'])
    assert tuple(map(bytes,seed.ram))==tuple(map(bytes,final_seed.ram))
    assert all(bytes(seed.ram[k][0x1fe0:0x1ff0])==cookie for k in (2,3))
    cleanup(seed)
    text,hooks = controller(after['raw'],final_seed)
    route, stack, env, labels = Seam.trajectory(before,after,seed)
    exact = route['actual_GameLoop']
    assert exact['original']['result']['x']==533 and exact['proposed']['result']['x']==772
    end = exact['proposed']['continuation']
    assert (end['x'],end['y'],end['native_state'],end['hp'],end['lives'])==(795,176,0,5,2)
    print('Exact c8bd final-minus reproduces the old pose40 snap and restores grounded far-side support.',flush=True)
    paired = paired_steps(before,after,seed)
    print('Genuine Prince GameCoreRoutine and GameLoop agree on the unaffected input sequence.',flush=True)
    direct = Seam.direct(before,after)
    assert direct==edge['direct']
    cleanup(stack)
    vectors = Seam.vectors(stack,env,labels)
    assert vectors==edge['vectors']

    out.mkdir(exist_ok=True)
    rom = out/'prince-private.nes'
    rom.write_bytes(after['raw'])
    assert sha(rom)==PIN
    for suffix in ('.lbl','.dbg'):
        shutil.copyfile(BASE.with_suffix(suffix),rom.with_suffix(suffix))
        refs.add(BASE.with_suffix(suffix))
    refs.update({Path(__file__),*(R/p for p in edge['bindings']),*map(Path,ready['bindings'])})
    proof = out/'candidate.json'
    receipt = dict(passed=True,private=True,ROM_written=True,Mesen_run=False,native_pending=True,
                   parent_SHA256=BASE_PIN,candidate_SHA256=PIN,final_minus_camera_SHA256=MINUS_PIN,
                   Prince_cookie=cookie.hex(),patches=prince['patches']+edge['patches'],
                   genuine_cold_headers_exact=True,unaffected_Prince=paired,
                   direct=direct,vectors=vectors,camera_reconstruction=route,observer_hooks=hooks,
                   controller_only=True,unchanged_V2_controller_inputs=True,
                   third_pipe_receipt='third-pipe.json',full_stage_receipt='full11.json',
                   bindings={str(p.resolve()):sha(p) for p in sorted(refs)})
    proof.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    prepare(out/'native',rom,text,refs|{proof},expected=PIN,timeout=ready['timeout'],
            scope='Same V2 original controls with actual AA44/A,Y/camera and both coordinate bus writes. '
                  'Strict third far-side ground and actual full stage are separate receipts.',
            allow_interactive=ready['allow_interactive'])
    assert sum(p.is_file() for p in out.rglob('*'))==7


if __name__=='__main__':
    main()
