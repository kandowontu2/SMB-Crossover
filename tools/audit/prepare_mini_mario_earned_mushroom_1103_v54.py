"""Correct only52 observer hook-name metadata; keep its real negative immutable."""
from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import prepare_mini_mario_power_contract_1103_v51 as P
from prepare_selected_native_packet_v1 import prepare,sha
from observe_chip_committed_write import lua
R,O=P.R,P.O
def main():
 prior=O/'earned-mushroom';ready=json.loads((prior/'ready.json').read_text());rom=Path(ready['ROM']);assert sha(rom)==ready['ROM_sha256']==P.PIN
 negative=prior/'capture/result.json';n=json.loads(negative.read_text());assert n['passed']is False and 'name'in n['error'],n.get('error')
 text=(prior/'controller.lua').read_text();q=json.loads((P.HOST/'mini-host-v48.json').read_text());code=(P.HOST/'mini-host-v48.bin').read_bytes();pc=q['labels']['MiniHostHead'];prefix=list(code[pc-0xa000:pc-0xa000+4]);assert pc==45699 and prefix==[173,92,194,240]
 old=dict(pc=pc,physical=3*8192+pc-0xa000,memory='nesWorkRam',bytes=prefix)
 new=dict(name='MiniHostHead',**old);a='C.hooks.MiniHostHead='+lua(old);b='C.hooks.MiniHostHead='+lua(new);assert text.count(a)==1;text=text.replace(a,b)
 assert new['name']=='MiniHostHead'and new['physical']==29315
 raw=rom.read_bytes();assert list(raw[1048592+962*1024+pc-0xa000:1048592+962*1024+pc-0xa000+4])==prefix
 sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'))
 from lupa.lua54 import LuaRuntime
 assert LuaRuntime().eval('function(s)local f,e=load(s);assert(f,e);return true end')(text)
 report=O/'observer-hook-name-v54.json';report.write_text(json.dumps(dict(passed=True,observer_only=True,ROM_unchanged=True,ROM_SHA256=P.PIN,hook=new,physical_carrier=962+(pc-0xa000)//1024,negative=n['error'],negative_path=negative.relative_to(R).as_posix(),controller_inputs_unchanged=True,changed_exact_assignment=dict(old=a,new=b)),indent=2)+'\n')
 refs=[Path(p)for p in ready['bindings']]+[Path(__file__),negative,report]
 prepare(O/'earned-mushroom54',rom,text,refs,expected=P.PIN,timeout=180,allow_interactive=True,scope='Exact52earned-mushroom inputs/guards on unchangedca90. Observer-only correction adds required MiniHostHead name; PC B283/WRAMphysical29315/AD5CC2F0 bytes independently matched to current ROM carrier.52nil-name negative preserved. No ROM/source/RAM writes, no earned/timing/flower claim before root native result. TwoPNG/9000physical cap.')
if __name__=='__main__':main()
