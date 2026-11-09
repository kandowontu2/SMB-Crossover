"""Bind the passing Mini injury route through the first corrected source update."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

import prepare_mini_injury_helper_native_1110 as V1


R = V1.R
V4 = R/'build/mini-injury-helper-v4-native-1110'
WITNESS = V4/'capture/result.json'
BINDING = V4/'capture/binding.json'
FIX = R/'build/mini-native-injury-status-fix-1110/proof.json'
OBSERVER = R/'tools/reference/mini_injury_status_native_1110.lua'
COOKIE = 16+65*8192+0x1003
STORE = 0x97a4


def kernel_hook(kernel, labels, name):
    pc = labels[name]
    code = kernel[pc-0xa000:pc-0xa000+4]
    assert len(code)==4
    return V1.lua(dict(name=name,pc=pc,physical=pc-0x4000,memory='nesWorkRam',bytes=list(code)))


def validate_cartridge(raw, kernel, labels):
    code = V1.CODE_OFFSET
    assert raw[:5]==b'NES\x1a\x40' and not raw[6]&4
    assert len(kernel)==5120 and raw[code:code+5120]==kernel
    payload_digest = hashlib.sha256(raw[code:code+7168]).digest()[:13]
    assert raw[COOKIE:COOKIE+16]==bytes((167,41,1))+payload_digest
    leaf = labels['MiniHostInjury']
    assert kernel[15:18]==b'\x4c'+leaf.to_bytes(2,'little')
    assert kernel[leaf-0xa000:leaf-0xa000+4]==bytes.fromhex('a9001860')
    store = V1.prg_hook(raw,'Native small tier store',126,STORE)
    assert store['bytes']==[0x8d,0x5b,0x07,0xa9]
    return store


def controller(text, raw, kernel, labels, old_rom, old_kernel, new_rom, new_kernel):
    store = validate_cartridge(raw,kernel,labels)
    text = V1.unique(text,f'["ROM_sha256"]="{old_rom}"',f'["ROM_sha256"]="{new_rom}"')
    text = V1.unique(text,f'["kernel_SHA256"]="{old_kernel}"',f'["kernel_SHA256"]="{new_kernel}"')
    text = V1.rebind_kernel(text,kernel,labels)
    for physical, values in V1.PRG_HOOK.findall(text):
        at = 16+int(physical)
        want = bytes(map(int,values.split(',')))
        assert raw[at:at+len(want)]==want,(hex(at),want.hex())
    text = V1.unique(text,"observe_return('MiniHostBox',",
                     "local injuryBoxReturn,injuryDrawReturn,injuryDma\nobserve_return('MiniHostBox',")
    text = V1.unique(text,"'Native GuestFullBox consumes original bounds')\nend)",
                     "'Native GuestFullBox consumes original bounds')\n injuryBoxReturn(p,b)\nend)")
    text = V1.unique(text,' if ram(0xc315)==1 then latestDraw=p end',
                     ' if ram(0xc315)==1 then latestDraw=p end\n injuryDrawReturn(p)')
    text = V1.unique(text,"'Actual Mini original-derived opaque RGB')end\n end",
                     "'Actual Mini original-derived opaque RGB')end\n  injuryDma(p,a,tile,attr)\n end")
    text = V1.unique(text,'  if not power.completed then return earned_route(s) end', '''  if not power.completed then return earned_route(s) end
  if injury.visible then
   check(injury.first_source_step and injury.first_source_box and injury.first_source_draw,
    'First resumed Main executes the small source step, box and draw')
   if not injury.first_source_update then
    local q=injury.first_source_step
    check(updates==q.source+1 and r('FrameCounter')==q.counter,
     'The observed small body belongs to the first completed source update')
    check(r('PlayerStatus')==0 and s.pose==injury.first_source_draw.pose and s.lives==startLives,
     'First resumed source update retains the small pose and both lives')
    injury.first_source_update={frame=frame,source=updates,counter=r('FrameCounter'),
     pose=s.pose,tier=ram(0xc244),top=ram(0xc256),lives=s.lives}
   end
   route_pad={}
   return
  end''')
    text = V1.unique(text,'   injury.start=snapshot_native()', '''   injury.start=snapshot_native()
   check(injury.fallback and injury.status_store and injury.start.status==0,
    'Native injury begins at the written small status')''')
    text = V1.unique(text,'  injury.native_steps[#injury.native_steps+1]=snapshot_native()', '''  local q=snapshot_native()
  q.source_tier=ram(0xc244);q.source_top=ram(0xc256)
  check(q.status==0 and q.source_tier==1 and q.source_top==0xf9,
   'Native injury keeps the frozen powered source body while host tier is already small')
  injury.native_steps[#injury.native_steps+1]=q''')
    text = V1.unique(text,'''  if q.right>=864 then
   check(q.status==41,'Preserve the separately tracked native PlayerStatus=41 injury defect')
   check(injury.jump_ack and injury.airborne,'Native jump and injury scroll are both witnessed')
   injury.native_status_anomaly={before=injury.force.status,during=q.status,expected=0}''', '''  if q.right>=864 and not injury.visible then
   check(q.status==0 and injury.jump_ack and injury.airborne,
    'Native small status, actual jump and injury scroll are all witnessed')
   injury.native_status_transition={before=injury.force.status,during=q.status}''')
    text = V1.unique(text,'''  if injury.visible then
   check(r('NumberofLives')==startLives,'Powered injury retains the life')
   injury.visible.sprite_chr4=emu.getState()['mapper.chrBanks4']
   injury.completed=true
   transition('finish')
  end''', '''  if injury.visible then
   check(r('NumberofLives')==startLives and r('PlayerStatus')==0,
    'Injury retains the life at small native status')
   if not injury.visible.sprite_chr4 then
    injury.visible.sprite_chr4=emu.getState()['mapper.chrBanks4']
    check(injury.visible.sprite_chr4==C.expected_chr4,'Mapped Mini CHR at visible lift entry')
   end
   check(frame-injury.visible.frame<32,'Bounded return to first source draw and DMA')
   if engine==8 then
    check(#injury.native_steps==39,'All 39 native injury movement updates elapsed')
    route_pad={}
    if injury.first_source_update and injury.first_small_dma then
     injury.completed=true
     transition('finish')
    end
   end
  end''')
    text = V1.unique(text,"print('PASS Mini helper scrolls in during native powered injury')",
                     "print('PASS Mini helper scroll and small source body after native injury')")
    hooks = ("\nlocal injuryFallback="+kernel_hook(kernel,labels,'MiniHostInjury')+
             "\nlocal injuryStatusStore="+V1.lua(store)+'\n')
    return text+hooks+OBSERVER.read_text(encoding='utf-8')


def bound_baseline():
    text,ready_path,ready = V1.bound_template(V4/'controller.lua')
    binding = json.loads(BINDING.read_text(encoding='utf-8'))
    result = json.loads(WITNESS.read_text(encoding='utf-8'))
    assert binding==dict(ROM_sha256=ready['ROM_sha256'],ready_sha256=V1.sha(ready_path),exit_code=0)
    assert result['passed'] and result['controller_only'] and not result['script_RAM_writes']
    injury = result['injury_helper']
    assert injury['completed'] and injury['visible']['right']==864 and injury['visible']['timer']==201
    assert injury['native_status_anomaly']==dict(before=1,during=41,expected=0)
    fix = json.loads(FIX.read_text(encoding='utf-8'))
    assert fix['passed'] and fix['parent_SHA256']==ready['ROM_sha256']
    return text,ready_path,ready


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    for field in ('rom','kernel','output'):
        cli.add_argument('--'+field,type=Path,required=True)
    cli.add_argument('--validate-only',action='store_true')
    args = cli.parse_args()
    rom,kernel = args.rom.resolve(),args.kernel.resolve()
    raw,code = rom.read_bytes(),kernel.read_bytes()
    metadata = rom.with_suffix('.json')
    info = json.loads(metadata.read_text(encoding='utf-8'))
    rom_hash,kernel_hash = V1.sha(rom),V1.sha(kernel)
    assert (rom_hash,kernel_hash)==(info['candidate_SHA256'],info['kernel_SHA256'])
    kernel_labels = kernel.with_suffix('.lbl')
    labels = {name:int(pc,16) for pc,name in re.findall(
        r'^al ([0-9A-F]+) \.(\w+)$',kernel_labels.read_text(),re.M)}
    text,ready_path,ready = bound_baseline()
    old_metadata = json.loads(Path(ready['ROM']).with_suffix('.json').read_text(encoding='utf-8'))
    text = controller(text,raw,code,labels,ready['ROM_sha256'],old_metadata['kernel_SHA256'],rom_hash,kernel_hash)
    assert not any(token in text for token in ('emu.write(', 'emu.reset(', 'emu.loadSavestate('))
    sys.path.insert(0,str(V1.LUA))
    from lupa.lua54 import LuaRuntime

    assert LuaRuntime().eval('function(s) local f,e=load(s); assert(f,e); return true end')(text)
    if args.validate_only:
        print(json.dumps(dict(validated=True,ROM_sha256=rom_hash,kernel_SHA256=kernel_hash,
                              controller_bytes=len(text.encode()))))
        return
    refs = {Path(__file__),Path(V1.__file__),OBSERVER,V4/'controller.lua',ready_path,WITNESS,BINDING,
            FIX,metadata,kernel,kernel_labels}
    V1.prepare(args.output,rom,text,refs,expected=rom_hash,timeout=180,
               allow_interactive=ready['allow_interactive'],
               scope='Controller-only earned mushroom and side injury. Verifies native status zero, '
                     'the X864 lift’s same-injury offscreen birth and visible entry, then the first '
                     'resumed small source body, pose and actual DMA with both lives retained.')


if __name__=='__main__':
    main()
