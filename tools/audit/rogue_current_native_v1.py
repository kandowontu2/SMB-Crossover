"""Bounded controller-only menu or Rogue1-1 verification of composed ROM."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import sys

R=Path(__file__).resolve().parents[2]
O=R/'build/rogue-current-menu-v5'
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from run_mesen import run


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def lua(value):
    if isinstance(value,dict):return '{'+','.join('['+lua(k)+']='+lua(v)for k,v in value.items())+'}'
    if isinstance(value,list):return '{'+','.join(lua(v)for v in value)+'}'
    if value is None:return 'nil'
    if isinstance(value,bool):return 'true'if value else'false'
    return json.dumps(value)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('test',choices=['menu','route'])
    a=ap.parse_args();out=O/'native'/a.test;assert not out.exists()
    build=json.loads((O/'build-proof.json').read_text());controls=json.loads((O/'controls.json').read_text())
    rom=O/'candidate.nes';expected=sha(rom)
    assert expected==build['ROM_sha256']==controls['ROM_sha256']and controls['passed']
    for path,h in controls['source_bindings'].items():assert sha(path)==h,path
    inputs={};out.mkdir(parents=True)
    if a.test=='menu':
        template=R/'tools/audit/full_roster_menu_native_v1.lua';code=template.read_text()
        old='(s==2 or s==7 or s==11)and v==1'
        assert code.count(old)==1;code=code.replace(old,'(s==7 or s==11)and v==1')
        # Record ROM identity in the actual terminal receipt as well.
        old="f:write(string.format('{\"passed\":true,\"frames\":%d"
        assert code.count(old)==1
        code=code.replace(old,"f:write(string.format('{\"ROM_sha256\":\""+expected+"\",\"passed\":true,\"frames\":%d")
        inputs[str(template)]=sha(template)
    else:
        ready=R/'build/verification/rogue-dawn-victory-native-easy-v1/ready.json'
        config=json.loads(ready.read_text())['config']
        old=scoped_load(R/'build/rogue-dawn-victory-pose-v4/candidate.nes');b=scoped_load(rom)
        for h in config['hooks'].values():
            offset=h['pc']-address(old,h['name'])
            assert old['raw'][location(old,h['name'])+offset:location(old,h['name'])+offset+3]==bytes(h['bytes'])
            h['pc']=address(b,h['name'])+offset
            h['bytes']=list(b['raw'][location(b,h['name'])+offset:location(b,h['name'])+offset+3])
            g=b['segs'][b['syms'][h['name']]['seg']];h['bank']=(int(g['ooffs'],0)-16)//8192
        config.update(out=out.as_posix()+'/',prefix=out.as_posix()+'/',ROM_sha256=expected)
        config['navigation']=['up'if i//8 else'right'if i<2 else'left'for i in range(32)]
        config['dma_store_return']=address(b,'PostDmaMaskEnable')-3 if'PostDmaMaskEnable'in b['syms']else address(b,'PostDmaMaskEnable')
        # Use the actual configured hook label; older source calls it
        # PostDmaMaskEnable in metadata only on some branches.
        config['dma_store_return']=config['hooks']['dma_complete']['pc']-3
        runner=R/'tools/audit/roster_expansion_cold_capture_v3.lua'
        code='ROSTER_CONFIG='+lua(config)+'\n'
        code+='for name,value in pairs(ROSTER_CONFIG.extra_ram)do assert(L[name]==nil or L[name]==value,"RAM alias conflict: "..name);L[name]=value end\n'
        code+='dofile('+lua(runner.as_posix())+')\n'
        inputs[str(ready)]=sha(ready);inputs[str(runner)]=sha(runner)
        for p in (R/'tools/playthroughs').glob('rogue_dawn_11_v*.lua'):inputs[str(p)]=sha(p)
        inputs[str(R/'tools/audit/final_inventory_compact_capture_v1.lua')]=sha(R/'tools/audit/final_inventory_compact_capture_v1.lua')
        (out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    controller=out/'controller.lua';controller.write_text(code,newline='\n')
    os.environ['SMB_RUN_OUTPUT']=str(out)
    result=run(controller,rom,timeout=180,emulator_options=['--doNotSaveSettings','--nes.removeSpriteLimit=false',
        '--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
    assert sha(rom)==expected
    inputs[str(controller)]=sha(controller);inputs[str(Path(__file__).resolve())]=sha(__file__)
    inputs[str(O/'controls.json')]=sha(O/'controls.json')
    (out/'binding.json').write_text(json.dumps(dict(ROM_sha256=expected,exit_code=result,
        no_native_RAM_writes=True,normal_sprite_limit=True,inputs=inputs),indent=2)+'\n')
    print(json.dumps(dict(test=a.test,ROM_sha256=expected,exit_code=result)))
    raise SystemExit(result)


if __name__=='__main__':main()
