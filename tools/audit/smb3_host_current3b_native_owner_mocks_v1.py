"""Synthetic source-return/physical-clone/DMC observer controls; no native launch."""
from pathlib import Path
import argparse,json,sys,traceback
from smb3_host_current3b_cpu_v1 import D,R,sha,put
from observe_chip_committed_write import lua
from mario_powerups_current3cee_static_v2 import runtime

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);cfg=json.loads((a.packet/'configuration.json').read_text());sys.path.insert(0,str(D/'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1'));from lupa.lua54 import LuaRuntime
 module=R/'tools/audit/smb3_host_current3b_native_v1.lua';checks=[]
 def fixture():
  rt=runtime(LuaRuntime,{},{});rt.execute('ROSTER_CONFIG='+lua(cfg['roster'])+'\nSMB3_MUSIC_NATIVE_CONFIG='+lua(cfg['music']))
  rt.execute("""
state['cpu.a']=3;state['cpu.x']=4;state['cpu.y']=5;state['cpu.ps']=32
mockBanks={126,86,38,127}
emu.convertAddress=function(a)if a<32768 then return nil end;return{address=mockBanks[(a-32768)//8192+1]*8192+a%8192}end
emu.read=function(a,t)if t==emu.memType.nesPrgRom then return 0 end;return mem[a]or 0 end
""")
  rt.execute(module.read_text());rt.execute('SMB3_MUSIC_INSTALL_RETURN_DISPATCHER();count=#callbacks;emu.addMemoryCallback=function()error("runtime registration")end;emu.removeMemoryCallback=function()error("runtime removal")end')
  for h in cfg['music']['hooks'].values():
   for i,v in enumerate(h['bytes']):rt.globals().mem[h['pc']+i]=v
  return rt
 def fire(rt,kind,at,value=0):rt.execute(f"state['cpu.pc']={at};dispatch({kind},{at},{value})")
 def events(rt):
  text=rt.eval('table.concat(texts[ROSTER_CONFIG.out.."smb3-music-native.jsonl"])');return[json.loads(s)for s in text.splitlines()]
 try:
  rt=fixture();h=cfg['music']['hooks']['SourceInit'];rt.execute("state['cpu.sp']=250;mem[507]=127;mem[508]=169;mockBanks[2]=85")
  fire(rt,2,h['pc']);assert not events(rt),'Wrong source bank ignored'
  rt.execute('mockBanks[2]=86');fire(rt,2,h['pc']);fire(rt,1,cfg['music']['ram']['GuestNativeApu'],17)
  rt.execute("state['cpu.sp']=251");fire(rt,2,0xa980);assert not events(rt),'Wrong stack return ignored'
  rt.execute("state['cpu.sp']=252");fire(rt,2,0xa981);assert not events(rt),'Unrelated return ignored'
  fire(rt,2,0xa980);rows=events(rt);assert len(rows)==1 and rows[0]['kind']=='original-source-call'and rows[0]['call']['logical']==[[0x4000,17]] and rows[0]['call']['return_bank']==86
  assert rt.eval('#callbacks==count');checks.append('Source physical owner/stack/unrelatedPC reject, actual slot return and ordered logical image capture')
  rt=fixture();h=cfg['music']['hooks']['AudioUpdate'];rt.execute("state['cpu.sp']=250;mem[507]=255;mem[508]=224;mockBanks[4]=127")
  fire(rt,2,h['pc']);rt.execute("state['cpu.sp']=252;mockBanks[4]=125");fire(rt,2,0xe100);assert not events(rt),'Unknown E return must not consume slot'
  rt.execute('mockBanks[4]=70');fire(rt,2,0xe100);rows=events(rt);assert rows[0]['kind']=='whole-audio-return'and rows[0]['return_bank']==70
  assert rt.eval('#callbacks==count');checks.append('Genuine127 entry->70 return accepted after bytes/SP; unpermitted125 cannot consume slot')
  rt=fixture();h=cfg['music']['hooks']['AudioUpdate'];rt.execute('mockBanks[4]=125')
  try:fire(rt,2,h['pc'])
  except Exception as e:assert'Unexpected resident physical owner'in str(e)
  else:raise AssertionError('Wrong resident entry must reject')
  checks.append('Wrong physical resident entry125 rejects rather than silently losing AudioUpdate observation')
  for e in [70,97]:
   rt=fixture();m=cfg['music']['ram'];rt.globals().mem[m['BassDmcActive']]=4;rt.globals().mem[m['B3Source4012']]=230;rt.globals().mem[m['B3VirtualMaps']+7]=3;rt.execute(f'mockBanks[4]={e}')
   for at,v in [(0x4012,197),(0x4013,0),(0x4015,31)]:fire(rt,1,at,v)
   fire(rt,0,0xf140,0);rows=events(rt);assert len([x for x in rows if x['kind']=='DMC-start'])==1 and len([x for x in rows if x['kind']=='DMC-fetch-complete'])==1
   assert rt.eval('#callbacks==count');checks.append(f'Physical E{e} original virtualpage sample binding + actual sequential read/completion observer')
  rt=fixture();m=cfg['music']['ram'];rt.globals().mem[m['BassDmcActive']]=4;rt.globals().mem[m['B3Source4012']]=230;rt.globals().mem[m['B3VirtualMaps']+7]=3;rt.execute('mockBanks[4]=70')
  for at,v in [(0x4012,197),(0x4013,0),(0x4015,31)]:fire(rt,1,at,v)
  try:fire(rt,0,0xf140,1)
  except Exception as e:assert'Actual sequential DMC fetch/value'in str(e)
  else:raise AssertionError('Wrong actual sample value must reject')
  checks.append('Incorrect actual fetched sample value rejects; no masking or payload substitution')
  put(a.output/'proof.json',dict(passed=True,native_run=False,checks=checks,module_sha256=sha(module),readiness_sha256=sha(a.packet/'readiness.json'),configuration_sha256=sha(a.packet/'configuration.json'),checker_sha256=sha(__file__),limit='Deterministic API/state examples execute the actual new music observer only; no6502 emulation/native PPU/DMC/waveform/cadence or whole actual hardware result. All prior source proofs remain separate.'))
  print(json.dumps(dict(passed=True,checks=len(checks))))
 except Exception as e:put(a.output/'failure.json',dict(passed=False,error=str(e),traceback=traceback.format_exc(),checks_done=checks));raise
if __name__=='__main__':main()
