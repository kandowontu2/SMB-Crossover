"""Prepare one small exact8487 Proto cold-Hard startup probe, never launch."""
from pathlib import Path
import argparse,hashlib,json,sys
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/audit'))
from current_roster_compact_11_v1 import prepare,lua
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--expected-sha256',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.rom=a.rom.resolve();a.output=a.output.resolve()
 assert sha(a.rom)==a.expected_sha256
 prepare(SimpleNamespace(rom=a.rom,expected_sha256=a.expected_sha256,output=a.output,identity='proto',mode='hard',frames=8000,policy=ROOT/'tools/playthroughs/megaman_bass_v34_policy.lua',replay=None))
 b=scoped_load(a.rom)
 def h(n,d=0,size=3):
  off=location(b,n)+d;pc=address(b,n)+d;bank=(off-16)//8192;bs=b['raw'][off:off+size];banks=[bank]
  if bank==127:
   rel=off-16-bank*8192;assert b['raw'][16+125*8192+rel:16+125*8192+rel+size]==bs;banks=[125,127]
  return dict(pc=pc,banks=banks,bytes=list(bs),source_symbol=n,source_delta=d)
 def tail(n,op):
  d=int(b['syms'][n]['size'],0)-1;assert b['raw'][location(b,n)+d]==op;return h(n,d,1)
 nmi=location(b,'NonMaskableInterrupt');nb=b['raw'][nmi:nmi+int(b['syms']['NonMaskableInterrupt']['size'],0)]
 target=address(b,'SamusFreezeUpdateScreen');call=bytes([0x20,target&255,target>>8]);assert nb.count(call)==1
 delta=nb.index(call)+3
 init=location(b,'InitScroll');assert b['raw'][init:init+7]==b'\x8d\x05\x20\x8d\x05\x20\x60'
 post=location(b,'PostDmaMaskEnable');mirror=address(b,'Mirror_PPUMASK');load=bytes([0xa5,mirror])if mirror<256 else bytes([0xad,mirror&255,mirror>>8])
 assert b['raw'][post-3:post+len(load)+3]==b'\x8d\x14\x40'+load+b'\x8d\x01\x20'
 hooks=dict(nmi=h('NonMaskableInterrupt'),nmi_return=tail('NonMaskableInterrupt',0x40),gateway=h('SamusFreezeUpdateScreen'),gateway_return=h('NonMaskableInterrupt',delta),update=h('UpdateScreen'),update_return=h('InitScroll',6,1),chr=h('BankSwitchCHR'),chr_return=tail('BankSwitchCHR',0x60),dma_complete=h('PostDmaMaskEnable',len(load)))
 names='NmiR0 NmiR1 OperMode OperMode_Task GameEngineSubroutine SelectedCharacter ProtoVariant NmiDisable NmiSkipped DisableScreenFlag Mirror_PPUMASK VRAM_Buffer_AddrCtrl VRAM_Buffer1_Offset VRAM_Buffer2_Offset ReloadCHRBank SmFreezePalettePending SmFreezeRenderState InvHudActive'.split()
 cfg=dict(ROM_sha256=a.expected_sha256,cutoff_frame=600,ram={n:address(b,n)for n in names},hooks=hooks,dma_store_return=address(b,'PostDmaMaskEnable'))
 module=ROOT/'tools/audit/proto_startup_vram_timing_v2.lua';assert 'emu.write'not in module.read_text()and 'setInput'not in module.read_text()and 'removeMemoryCallback'not in module.read_text()
 (a.output/'startup-config.json').write_text(json.dumps(cfg,indent=2)+'\n',newline='\n')
 append='PROTO_STARTUP_VRAM_TIMING='+lua(cfg)+'\nlocal previousClose=ROSTER_CONFIG.bass_close\nlocal startupClose=dofile('+lua(module.as_posix())+')\nROSTER_CONFIG.bass_close=function()local q=previousClose and previousClose()or{};q.startup_vram=startupClose();return q end\n'
 run=a.output/'run.lua';text=run.read_text();needle='dofile('+lua((ROOT/'tools/audit/current_roster_compact_11_v1.lua').as_posix())+')';assert text.count(needle)==1
 run.write_text(text.replace(needle,append+needle),newline='\n')
 ready=a.output/'ready.json';z=json.loads(ready.read_text());z['bindings'][str(run)]=sha(run)
 for f in [module,Path(__file__).resolve(),a.output/'startup-config.json']:z['bindings'][str(f)]=sha(f)
 z['startup_probe']=dict(read_only=True,static_exec_hooks=len(hooks),memory_hooks=3,CSV_files=1,scope='Cold ProtoHard original controller/strict shared guard full8000route; observer first600PPUframes; original292failure never waived. Sparse NMI/VRAM/gateway/CHR/DMA/mask stamps and actual source packet bytes only.',no_new_capture_format=True)
 z['max_total_frames']=8000;ready.write_text(json.dumps(z,indent=2)+'\n',newline='\n')
 for f,digest in z['bindings'].items():assert sha(f)==digest
 print(json.dumps(dict(status='PREPARED_DO_NOT_RUN',ready=str(ready),sha256=sha(ready),bindings=len(z['bindings']),command=z['command'])))
if __name__=='__main__':main()
