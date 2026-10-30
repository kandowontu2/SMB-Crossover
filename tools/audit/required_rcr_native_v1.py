"""Cold controller-only Alex/Ryan smoke with both real menu Shadows settings."""
from pathlib import Path
import argparse
import copy
import json
import os
import sys

R = Path(__file__).resolve().parents[2]
O = R/'build/required-rcr-ink-shared-v3'
ROM = O/'candidate/candidate.nes'
sys.path[:0] = [str(R/'tools'), str(R/'tools/audit')]
from prepare_required_rcr_ink_v2 import sha
from current_roster_compact_11_v1 import linked, lua
from run_mesen import run
from capture_budget import capture_lease

POLICY = '''local age=0
return function(c)
 age=age+1
 return {right=age<40,left=age>=40 and age<48,a=age>=20 and age<34,b=age>=55 and age%12<6}
end
'''


def replace(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new)


def prepare(variant, off):
    out = O/f'native/v{variant}-off{off}'
    assert not out.exists()
    product = json.loads((O/'build-proof.json').read_text())
    for p, digest in product['bindings'].items():
        assert sha(p) == digest, p
    assert product['ROM_sha256'] == sha(ROM)
    parent_ready_path = R/'build/character-host-union-routes-v13-v4/goku-route-v1/ready.json'
    parent = json.loads(parent_ready_path.read_text())
    cfg = copy.deepcopy(parent['config'])
    raw, syms, address, location, hook = linked(ROM)
    cfg.update(name='alex' if variant == 0 else 'ryan', character=21, menu_index=20,
               variant_symbol='RcVariant', variant=variant, mode_value=0,
               expected_outlines_off=off, out=out.as_posix()+'/', prefix=out.as_posix()+'/',
               policy=(out/'policy.lua').as_posix(), extra_ram={}, limit=1400,
               ROM_sha256=sha(ROM), marker_names=['first-active','endpoint','failure'])
    edges = {k:list(raw[location('X5Menu'+k.title()):location('X5Menu'+k.title())+32])
             for k in ['left','right','up','down']}
    nav = []
    for start in range(32):
        queue, seen = [(start,[])], {start}
        for node, route in queue:
            if node == 20:
                nav.append(route[0] if route else '')
                break
            for key, table in edges.items():
                dest = table[node]
                assert 0 <= dest < 32
                if dest not in seen:
                    seen.add(dest)
                    queue.append((dest,route+[key]))
        else:
            raise AssertionError('Menu unreachable')
    cfg['navigation'] = nav
    for key, name, tail, offset in [
        ('loop','GameLoop',False,0), ('loop_return','GameLoop',True,0),
        ('nmi','NonMaskableInterrupt',False,0), ('nmi_return','NonMaskableInterrupt',True,0),
        ('irq','IrqScrollSplit',False,0), ('irq_return','IrqScrollSplit',True,0),
        ('dma_complete','PostDmaMaskEnable',False,3)]:
        h = hook(name, tail=tail, offset=offset)
        if key in ['nmi','nmi_return','dma_complete']:
            h['banks'] = [125,127]
            for bank in h['banks']:
                assert raw[16+bank*8192+(h['pc']&8191):16+bank*8192+(h['pc']&8191)+3] == bytes(h['bytes'])
        cfg['hooks'][key] = h
    cfg['dma_store_return'] = address('PostDmaMaskEnable')
    assert len(cfg['smc_fields']) == 33
    source_path = R/'tools/audit/roster_expansion_cold_capture_v3.lua'
    source = source_path.read_text()
    source = replace(source, 'local done,entered,failure=false,false,nil',
                     'local done,entered,failure=false,false,nil\nlocal smokeUpdates=0')
    source = replace(source, "local c=context();identity()",
                     "local c=context();identity();if entered then smokeUpdates=smokeUpdates+1 end")
    source = replace(source, "check(r('SelectedCharacter')==C.character,'Requested character readback')",
        "check(r('SelectedCharacter')==C.character,'Requested character readback')\n check(r('PlayerOutlinesOff')==C.expected_outlines_off,'Real menu Shadows setting retained')")
    source = replace(source, "local want=r('CrossoverBehaviorVersion')==C.mode_value and 0 or 1",
        "local want=(r('CrossoverBehaviorVersion')==C.mode_value and r('PlayerOutlinesOff')==C.expected_outlines_off) and 0 or 1")
    source = replace(source, "elseif state==4 then\n  if r('CrossoverOptionsFocus')~=1 then return pulse('down')end",
        "elseif state==4 then\n  if r('PlayerOutlinesOff')~=C.expected_outlines_off then\n   if r('CrossoverOptionsFocus')~=0 then return pulse('up')end\n   return pulse('a')\n  end\n  if r('CrossoverOptionsFocus')~=1 then return pulse('down')end")
    source = replace(source, 'local endpoint=entered and c.world==0 and c.level==1 and scope()and control12>=25 and c.x>first12X+5',
        'local endpoint=entered and c.world==0 and c.level==0 and scope()and smokeUpdates>=100')
    source = replace(source, 'real_1_2_control_updates=control12,',
        'real_1_2_control_updates=control12,smoke_active_Main_updates=smokeUpdates,')
    source = replace(source, 'Controller-only current 1-1 to controlled 1-2. Selected PPU review remains separate; no every-item/ability/source-fidelity/FPS claim.',
        'Controller-only cold menu/lives plus100active Main smoke in1-1. Not a levelclear or FPS qualification.')
    source = replace(source, "'cleared 1-1 and controlled 1-2'", "'completed100activeMain ink smoke'")
    source = source.replace("'ROSTER1-1 '", "'RCR_INK_SMOKE '")
    needle = "if endpoint then mark('endpoint',raw)end"
    hardware = '''if endpoint then
   mark('endpoint',raw)
   local ink=0;local hardwareOam={};local palette={};local pages={}
   for i=0,255 do hardwareOam[#hardwareOam+1]=emu.read(i,emu.memType.nesSpriteRam)end
   for i=0,31 do palette[#palette+1]=emu.read(0x3f00+i,emu.memType.nesPpuDebug)end
   for i=0,11 do pages[#pages+1]=assert(s['mapper.chrBanks'..i])end
   for i=1,256,4 do if hardwareOam[i]<240 and hardwareOam[i+2]&3==3 then ink=ink+1 end end
   check(ink>0,'Required intrinsic ink reaches actual hardware OAM')
   check(palette[30]==0x0f,'Required ink uses opaque native black3F1D')
   local hf=assert(io.open(C.prefix..'endpoint-hardware.json','w'))
   hf:write(json({OAM=hardwareOam,palette=palette,CHR=pages,ink_parts=ink,Shadows_off=r('PlayerOutlinesOff'),variant=r('RcVariant'),frame=frame}));hf:close()
  end'''
    source = replace(source, needle, hardware)
    # Resolve every extra fixture read to an actual compiled label/equate.
    import re
    labels = {}
    for line in ROM.with_suffix('.lbl').read_text().splitlines():
        m = re.fullmatch(r'al ([0-9A-Fa-f]+) \.([\w]+)',line)
        if m:
            labels[m[2]] = int(m[1],16)
    refs = set(re.findall(r'''\br\(['"]([^'"]+)['"]''',source))|{'RcVariant'}
    for name in refs:
        value=address(name)
        if name in labels:
            assert labels[name]==value
        else:
            assert syms[name]['type']=='equ' and (value<0x2000 or 0x5c00<=value<0x8000)
            cfg['extra_ram'][name]=value
    out.mkdir(parents=True)
    for name,text in [('source.lua',source),('policy.lua',POLICY)]:
        (out/name).write_text(text,newline='\n')
    (out/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
    (out/'run.lua').write_text('ROSTER_CONFIG='+lua(cfg)+'\n'+
        'for name,value in pairs(ROSTER_CONFIG.extra_ram)do assert(L[name]==nil or L[name]==value);L[name]=value end\n'+
        'dofile('+lua((out/'source.lua').as_posix())+')\n',newline='\n')
    bindings = {}
    paths = [Path(__file__).resolve(), O/'build-proof.json', source_path,
             R/'tools/audit/current_roster_compact_11_v1.py', R/'tools/audit/capture_budget.py',
             R/'tools/audit/final_inventory_compact_capture_v1.lua',
             R/'tools/audit/final_inventory_compact_capture_v1.py', R/'tools/run_mesen.py',
             ROM, ROM.with_suffix('.dbg'), ROM.with_suffix('.lbl'),
             *[out/n for n in ['source.lua','policy.lua','config.json','run.lua']]]
    for path in paths:
        bindings[str(path)] = sha(path)
    for path,digest in parent['bindings'].items():
        if 'kamikaze-private-emulator-v1' in path:
            assert sha(path)==digest
            bindings[path]=digest
    ready=dict(prepared=True,native_run=False,ROM_sha256=sha(ROM),config=cfg,
               emulator=parent['emulator'],bindings=bindings,normal_sprite_limit=True,
               controller_only=True,emulated_state_writes=False,frames_bound=1400,
               captured_PNGs_bound=8,container_bound=536870912,
               scope='Fresh separate100activeMain smoke, preserving all original PPU/CHR/IRQ/SMC/zero-death guards. Levelclear checker remains unchanged.')
    (out/'ready.json').write_text(json.dumps(ready,indent=2)+'\n')
    print(json.dumps(dict(prepared=str(out),ready_sha256=sha(out/'ready.json'))))


def launch(variant, off):
    out=O/f'native/v{variant}-off{off}'
    ready=json.loads((out/'ready.json').read_text())
    assert not(out/'capture-budget.json').exists()
    for path,digest in ready['bindings'].items():
        assert sha(path)==digest,path
    with capture_lease():
        pass
    os.environ['SMB_RUN_OUTPUT']=str(out)
    code=run(out/'run.lua',ROM,ready['emulator'],timeout=100,
             emulator_options=['--doNotSaveSettings','--nes.removeSpriteLimit=false',
                '--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false',
                '--nes.randomizeMapperPowerOnState=false'])
    for path,digest in ready['bindings'].items():
        assert sha(path)==digest,path
    (out/'binding.json').write_text(json.dumps(dict(exit_code=code,ROM_sha256=sha(ROM),
        ready_sha256=sha(out/'ready.json'),inputs=ready['bindings']),indent=2)+'\n')
    print(json.dumps(dict(exit_code=code,result=json.loads((out/'result.json').read_text())if(out/'result.json').exists()else None)))
    raise SystemExit(code)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('variant',type=int,choices=[0,1]);p.add_argument('off',type=int,choices=[0,1]);p.add_argument('--launch',action='store_true');a=p.parse_args()
    launch(a.variant,a.off)if a.launch else prepare(a.variant,a.off)
