"""Prepare one passive61-frame HUD timeline over frozen Bass Hard inputs."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/audit'))
from observe_chip_committed_write import lua
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')
def main():
 old=ROOT/'build/current-6be-bass-missing-effects-hard-v1';out=ROOT/'build/current-6be-bass-hud-timeline-hard-v1';assert not out.exists()
 manifest=json.loads((old/'prepared-not-run.json').read_text())
 for v in manifest['bindings']:assert sha(v['path'])==v['sha256'],v['path']
 cfg=json.loads((old/'config.json').read_text());assert cfg['ROM_sha256']=='6be48337ffee66a22b22de9ce134d5db323649fb4de620c43bad4ca98b80f193'and cfg['mode']==1 and cfg['character']==9
 rom=Path(next(v['path']for v in manifest['bindings']if Path(v['path']).suffix=='.nes'));b=scoped_load(rom)
 def hook(name,symbol,delta=0,size=3):
  off=location(b,symbol)+delta;pc=address(b,symbol)+delta;bank=(off-16)//8192;op=b['raw'][off:off+size];banks=[bank]
  if bank==127:
   assert b['raw'][16+125*8192+pc%8192:16+125*8192+pc%8192+size]==op;banks=[125,127]
  return dict(name=name,source_symbol=symbol,source_delta=delta,pc=pc,banks=banks,bytes=list(op))
 assert int(b['syms']['VRAM_Buffer1']['size'],0)==84
 names=['InvDirty','VRAM_Buffer1_Offset','VRAM_Buffer_AddrCtrl','InvSelected','InvAmmo','InvHudAmmo','NmiDisable','NmiSkipped','DisableScreenFlag','VRAM_Buffer1','NmiR0','NmiR1']
 hooks=dict(hud=hook('InventoryHud','InventoryHud'),hud_done=hook('InventoryHud::Done','InventoryHud::Done',size=1),hud_tail_done=hook('InventoryHudColdTail-return','InventoryHudColdTail',int(b['syms']['InventoryHudColdTail']['size'],0)-1,1),screen=hook('UpdateScreen-packet','UpdateScreen'))
 for name in ['hud_done','hud_tail_done']:assert hooks[name]['banks']==[59]and hooks[name]['bytes']==[96]
 h=cfg['hooks']['DmaComplete'];hooks['dma']=dict(name='DmaComplete',**h)
 for h in hooks.values():
  assert address(b,h['source_symbol'])+h['source_delta']==h['pc']
  for bank in h['banks']:
   off=16+bank*8192+h['pc']%8192
   assert list(b['raw'][off:off+len(h['bytes'])])==h['bytes'],h
 module=ROOT/'tools/audit/bass_hud_timeline_v1.lua';body=module.read_text()
 assert 'removeMemoryCallback'not in body and not any(s in body for s in ['emu.write(','emu.setInput(','emu.setState(','emu.loadSavestate('])
 assert body.count('originalScreenshot(...)')==1 and 'return png'in body and body.count('emu.addEventCallback(')==1
 assert 'emu.addMemoryCallback'not in body[body.index('emu.takeScreenshot=function'):],'No runtime registrations from screenshot/stop callbacks'
 out.mkdir(parents=True)
 observer=dict(ROM_sha256=cfg['ROM_sha256'],output=(out/'native').as_posix()+'/',first=980,last=1040,queue_bytes=84,ram={n:address(b,n)for n in names},hooks=hooks)
 original_run=(old/'run.lua').read_text();fixture=old/'current-bass-missing-effects.lua';loader='dofile([=['+fixture.as_posix()+']=])\n';assert original_run.count(loader)==1
 added='BASS_HUD_TIMELINE='+lua(observer)+'\ndofile([=['+module.as_posix()+']=])\n'
 run=original_run.replace(loader,added+loader,1);assert run.replace(added,'',1)==original_run
 (out/'run.lua').write_text(run,newline='\n');put(out/'observer-config.json',observer)
 command=json.loads((old/'command.json').read_text());argv=command['argv'];assert str(old/'native')in argv and str(old/'run.lua')in argv
 command['argv']=[str(out/'native')if x==str(old/'native')else str(out/'run.lua')if x==str(old/'run.lua')else x for x in argv];put(out/'command.json',command)
 proof=dict(PREPARED_DO_NOT_RUN=True,native_run=False,original_run_reverse_exact=True,original_fixture_path=str(fixture),original_fixture_sha256=sha(fixture),original_source_configuration_unchanged=True,source_order='InventorySpend writes ammo then INCInvDirty; next GameLoop UI can queue fresh digits only if screen enabled and buffer1 offset0. This observer does not assume which native cause occurs.',window=dict(first_actual_PPU_frame=980,last_actual_PPU_frame=1040,frames=61,rows_max=3000,CSV_bytes_max=1048576),static_callbacks_only=True,real_returns='InventoryHud A820 bank59 exits via native RTS A985 or relocated tail RTS BFFE; source metadata/opcodes freshly verified. Match actual bank59 and entry SP/caller word. Window-clipped returns recorded without claiming owner.',outputs='ONE bounded CSV +one small summary; original fixture still emits its existing eightPNGs/result/CSV only. No extra PNG/containers, RAM/input writes or guard wrappers.',screenshot_scope='Detailed before/after stamps and current committed HUD NT/actual mapped pattern reads only inside61-frame window. Outside screenshot calls only counted. Exact PNG object from original emu.takeScreenshot returned unchanged.',limitations='No per-scanline background-fetch callback; raw PPUADDR/PPUDATA callbacks and actualppu.videoRamAddr/state are serialized. Snapshot pattern/NT data are current state, not an invented raster epoch. Existing strict original hardware guards unchanged.',original_caps=manifest['caps'])
 put(out/'source-review.json',proof)
 paths={v['path']:v for v in manifest['bindings']}
 for p in [Path(__file__).resolve(),module,ROOT/'tools/audit/observe_chip_committed_write.py',old/'prepared-not-run.json',old/'native/result.json',old/'native/inventory.csv',old/'native/item-03.png']+[out/n for n in ['observer-config.json','run.lua','command.json','source-review.json']]:
  paths[str(p.resolve())]=dict(path=str(p.resolve()),sha256=sha(p),bytes=p.stat().st_size)
 for v in paths.values():assert sha(v['path'])==v['sha256'],v['path']
 put(out/'prepared-not-run.json',dict(status='PREPARED_DO_NOT_RUN',native_run=False,ROM_sha256=cfg['ROM_sha256'],original_fixture_byte_unchanged=True,original_controller_and_source_config_unchanged=True,observer_only=True,caps=manifest['caps'],additional_observer_caps=dict(window_frames=61,CSV_bytes=1048576,rows=3000,extra_PNGs=0),ROOT_native_lease_required=True,bindings=list(paths.values())))
 print(json.dumps(dict(status='PREPARED_DO_NOT_RUN',ready=str(out/'prepared-not-run.json'),sha256=sha(out/'prepared-not-run.json'),bindings=len(paths),source_review=sha(out/'source-review.json'),command=str(out/'command.json'))))
if __name__=='__main__':main()
