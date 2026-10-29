"""One capture-free exact saved-input fb28 NMI diagnostic, preparation only."""
from pathlib import Path
import copy,csv,difflib,hashlib,json,re,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
import current_roster_compact_11_v1 as B
sha=B.sha
P=R/'build/verification/dragon-power-admission-native-easy-v4'
OUT=R/'build/verification/dragon-power-admission-nmi-diagnostic-v1'

def main():
 assert not OUT.exists();OUT.mkdir()
 parent=json.loads((P/'ready.json').read_text());launch=json.loads((P/'launch.json').read_text())
 assert all(sha(p)==v for p,v in parent['bindings'].items())
 cfg=copy.deepcopy(parent['config']);rom=R/'build/dragon-power-admission-v1/candidate.nes'
 assert sha(rom)==cfg['ROM_sha256']=='fb28a741937ad5fb18d7f76f272874118c291dc0a575f69e15a2573436df500e'
 inp=P/'inputs.csv';rows=list(csv.DictReader(inp.open()));assert len(rows)==2653
 assert all(int(z['poll'])==i and int(z['frame'])==i for i,z in enumerate(rows,1))
 raw,syms,addr,loc,hook=B.linked(rom)
 hooks={k:copy.deepcopy(cfg['hooks'][k])for k in['nmi','nmi_return','dma_complete']}
 for key,name in [('normal','ContinueNMI'),('update','UpdateScreen'),('command','WriteBufferToScreen'),('screen_done','InitScroll'),('chr','BankSwitchCHR'),('publish','X5PublishChr'),('pre_dma','OAMandReadJoypad'),('hud','DpAdmissionHud'),('palette','DpAdmissionPalette')]:hooks[key]=hook(name)
 hooks['chr_return']=hook('BankSwitchCHR',tail=True)
 # Real common HUD Done RTS precedes Decimal helper/template, not proc end.
 data=raw[loc('DpAdmissionHud'):loc('DpAdmissionHud')+int(syms['DpAdmissionHud']['size'],0)]
 vbo=addr('VRAM_Buffer1_Offset');vb=addr('VRAM_Buffer1')
 pattern=bytes([0x8e,vbo&255,vbo>>8,0xa9,0,0x9d,vb&255,vb>>8,0x60])
 matches=[i for i in range(len(data))if data[i:i+len(pattern)]==pattern];assert len(matches)==1,matches
 delta=matches[0]+8;hooks['hud_return']=hook('DpAdmissionHud',offset=delta)
 assert raw[loc('ContinueNMI'):loc('ContinueNMI')+3]==bytes([0xce,addr('NmiDisable')&255,addr('NmiDisable')>>8])
 for key in['normal','pre_dma']:
  h=hooks[key];assert h['bank']==127
  clone=16+125*8192+(h['pc']&8191);assert raw[clone:clone+3]==bytes(h['bytes']);h['banks']=[125,127]
 fields='VRAM_Buffer_AddrCtrl VRAM_Buffer1_Offset VRAM_Buffer2_Offset VRAM_Buffer1 VRAM_Buffer2 NmiR0 NmiR1 NmiDisable NmiSkipped ReloadCHRBank X5WideChrActive X5ChrMode SmFreezePalettePacket SmFreezePalettePending SmFreezePaletteControl SmFreezeRenderState DpClock DpPaletteAck DpHP DpPole DpWaves DpAction DpPower TimerControl FrameCounter GameEngineSubroutine CurrentBank CurrentBankC AreaType BackgroundColorCtrl Mirror_PPUMASK Mirror_PPUCTRL'.split()
 assert set(fields)<=syms.keys(),sorted(set(fields)-syms.keys())
 cfg.update(out=OUT.as_posix()+'/',prefix=OUT.as_posix()+'/',replay=inp.as_posix(),limit=2654,capture_bytes=0)
 cfg['diagnostic']=dict(first=2635,last=2654,row_cap=2048,byte_cap=2*1024*1024,hooks=hooks,fields=fields,ram={n:addr(n)for n in fields},pointer_low=addr('VRAM_AddrTable_Low'),pointer_high=addr('VRAM_AddrTable_High'))
 original=R/'tools/audit/roster_expansion_cold_capture_v3.lua';old=original.read_text();s=old;changes=[]
 def replace(a,b):
  nonlocal s
  assert s.count(a)==1,a[:100];s=s.replace(a,b);changes.append([a,b])
 begin=old.index("local codec=dofile(");end=old.index('local markers={}',begin)
 replace(old[begin:end],"-- Diagnostic explicitly disables all screen/media capture. Hardware guards below are unchanged.\nlocal capture={close=function()end,stats=function()return{capture_free=true,records=0,container_bytes=0}end}\nlocal full={close=function()end}\n")
 begin=old.index('local function mark(');end=old.index('local function scope()',begin)
 replace(old[begin:end],'')
 begin=old.index(' if coldMenu or coldLivesAge>=5');end=old.index(' lastPower=c.status',begin)
 replace(old[begin:end],' -- No getScreenBuffer, screenshots, ARGB, video or container in this diagnostic.\n')
 fragment=R/'tools/audit/dragon_power_nmi_queue_observer_v1.lua'
 injected='local diagnostic_install=dofile('+B.lua(fragment.as_posix())+')\ndiagnostic_install(C,L,{clock=function()return frame,polls,loops end,json=json})\n'
 replace('local lastPower\n',injected+'local lastPower\n')
 replace(' full:close();capture.close()',' local diagnostic=C.diagnostic_close and C.diagnostic_close()or nil\n full:close();capture.close()')
 replace('adapter=capture.stats(),bass_collision=bass,','adapter=capture.stats(),bass_collision=bass,diagnostic=diagnostic,')
 replace("scope='Controller-only current 1-1 to controlled 1-2. Selected PPU review remains separate; no every-item/ability/source-fidelity/FPS claim.'","scope='Capture-free exact saved-v4-input diagnostic through2654; expected strict render FALSE, no route-pass claim.'")
 back=s
 for a,b in reversed(changes):
  if b:assert back.count(b)==1;back=back.replace(b,a)
  else:
   # Deleted only standalone mark function; reconstruct at its unique next
   # function boundary for exact reverse normalization.
   assert a.startswith('local function mark(');back=back.replace('local function scope()',a+'local function scope()',1)
 assert back==old,'Exact derivative reverse normalization'
 assert 'emu.getScreenBuffer'in old and 'emu.getScreenBuffer'not in s
 assert not re.search(r'emu\.(?:write\w*|setState|loadSavestate|reset)\s*\(',s+fragment.read_text())
 assert fragment.read_text().count('emu.addMemoryCallback')==5 # one static helper + four fixed writes
 (OUT/'observer.lua').write_text(s)
 (OUT/'observer-only.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),s.splitlines(True),fromfile=str(original.relative_to(R)),tofile='private/observer.lua')))
 run=OUT/'run.lua';run.write_text('ROSTER_CONFIG='+B.lua(cfg)+'\nfor name,value in pairs(ROSTER_CONFIG.extra_ram)do assert(L[name]==nil or L[name]==value,"RAM alias conflict: "..name);L[name]=value end\ndofile('+B.lua((OUT/'observer.lua').as_posix())+')\n')
 command=launch['actual_argv'][:]
 command[command.index('--output')+1]=str(OUT);command[command.index(str(P/'run.lua'))]=str(run)
 assert command[command.index('--emulator')+1]==str(R/'build/verification/kamikaze-private-emulator-v1/Mesen.exe')
 (OUT/'command.json').write_text(json.dumps(command,indent=2)+'\n')
 metadata=dict(actual_hooks=hooks,ram=cfg['diagnostic']['ram'],full_parent_hook_copy_owners=parent['hook_copy_owners'],real_hud_done_RTS_offset=delta,
  all_callback_addresses_resolve=True,all_startup_static=True,reverse_normalized_original_exact=True,literal_hardware_guard_bodies_unchanged=True,
  original_input_polls=2653,original_input_frame_alignment='poll==frame1..2653 exactly; original assert(q.frame==frame) retained',
  native_attempt=False,Lua_VM_executed=False,scope='No capture and no producer/controller/ROM modifications. Same strict all256DMA/attributesE3/render/CHR/IRQ/NMI/5SMC/lowerstack/motion/death guards. Expected2654FALSE remainsFALSE; finite diagnostic only.')
 (OUT/'metadata-proof.json').write_text(json.dumps(metadata,indent=2)+'\n')
 dependencies={Path(p)for p in parent['bindings']}|{Path(__file__),Path(B.__file__),fragment,original,P/'ready.json',P/'launch.json',P/'result.json',P/'trace.csv',P/'events.jsonl',inp,R/'build/dragon-power-admission-v1/handoff.json',OUT/'observer.lua',OUT/'observer-only.patch',run,OUT/'command.json',OUT/'metadata-proof.json'}
 ready=dict(prepared=True,native_run=False,config=cfg,command=command,ROM_sha256=cfg['ROM_sha256'],bindings={str(p.resolve()):sha(p)for p in sorted(dependencies)},
  maximum_native_launches=1,maximum_owned_workers=1,capture_free=True,focus_ppu_frames=[2635,2654],diagnostic_log_cap_bytes=2*1024*1024,
  frame_bound=2654,host_seconds=600,expected_original_first_failure='Active render enable precedes pre-render vertical reload at2654; do not reinterpret as PASS',
  changed_scope=metadata['scope'],original_negative_result_sha256=sha(P/'result.json'))
 (OUT/'ready.json').write_text(json.dumps(ready,indent=2)+'\n')
 print(json.dumps(dict(ready=str(OUT/'ready.json'),sha256=sha(OUT/'ready.json'),bindings=len(ready['bindings']),command=str(OUT/'command.json'))))

if __name__=='__main__':main()
