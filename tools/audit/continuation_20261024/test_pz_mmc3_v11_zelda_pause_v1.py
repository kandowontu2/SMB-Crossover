from pathlib import Path
import importlib.util,json,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;rom=D/'ryu-head-oversized-mmc3-v11/candidate.nes';O=D/'ryu-head-oversized-mmc3-v11/zelda-pause-v1'
def once(t,a,b):
 assert t.count(a)==1,(a,t.count(a));return t.replace(a,b)
f=R/'tools/audit/fixtures/zelda2_pause_native_pq.lua';t=f.read_text();t=once(t,'oldchr=r(\'CurrentCHRBank\',11);oldmode=r(\'X5ChrMode\',11)',"oldchr=chrSnapshot();oldmode=r('X5ChrMode')")
t=once(t," assert(r('CurrentCHRBank',11)==oldchr and r('X5ChrMode',11)==oldmode,'Original background CHR ownership restored')"," assert(chrSnapshot()==oldchr and r('X5ChrMode')==oldmode,'Original physical CHR page3 and resident body-mode ownership restored')")
t=once(t,"   for i=0,127 do otherRecords[i]=(i*37+19)%256;emu.write(0x5e80+i,otherRecords[i],emu.memType.nesDebug)end","   for i=0,95 do otherRecords[i]=emu.read(L.MmAudioRamStart+i,emu.memType.nesDebug)end")
t=once(t,"   for i=0,127 do assert(emu.read(0x5e80+i,emu.memType.nesDebug)==otherRecords[i],'Pause leaves other character records untouched at '..i)end","   for i=0,95 do assert(emu.read(L.MmAudioRamStart+i,emu.memType.nesDebug)==otherRecords[i],'Pause leaves inactive character-state overlay untouched at '..i)end")
a='local function image(tag)';t=once(t,a,"local function chrSnapshot() local t={}for i=0,1023 do t[#t+1]=string.char(emu.read(3072+i,emu.memType.nesChrRam))end;return table.concat(t)end\n"+a)
# Keep the actual physical bank/SMC restoration assertions. MMC3 publication
# has a different decoded hardware store, so the MMC5-only pre-tail clause
# is not imported; the entry guard uses full8-bit bank shadows below.
e=(R/'tests/full-roster-entry.lua').read_text();a=e.index("emu.addMemoryCallback(function()\n assert(not ctx,'NMI nesting')");b=e.index('emu.addEventCallback(function()',a);g=e[a:b]
a=g.index(' if actual(0xc000)~=ctx then');b=g.index(' smc=shared()',a);g=g[:a]+g[b:];g=g.replace('%128','')
prefix="local ctx,smc;local nmis,irqs,publicationWindows=0,0,0\nlocal function actual(a)return emu.convertAddress(a).address//8192 end\nlocal function shared()local t={}for a=L.__SMCCODE_RUN__,L.__SMCCODE_RUN__+32 do t[#t+1]=emu.read(a,emu.memType.nesDebug)end;return table.concat(t,',')end\n"
a='emu.addMemoryCallback(function()\n if emu.convertAddress(L.Z2PanelTick)';t=once(t,a,prefix+g+a)
t += "\nemu.addMemoryCallback(function(a,v)error(string.format('Unexpected MMC5 register/ExRAM write %04x=%02x',a,v))end,emu.callbackType.write,0x5000,0x5fff)\n"
syms={}
for line in rom.with_suffix('.dbg').read_text().splitlines():
 if line.startswith('sym\t'):
  z=dict(v.split('=',1)for v in line[4:].split(',')if '='in v)
  if 'val'in z and z.get('scope')=='1':syms[z['name'].strip('"')]=int(z['val'],0)
aliases=''.join('L['+json.dumps(n)+']='+str(v)+'\n'for n,v in syms.items()if n.startswith('Z2')or n in('X5ChrMode','MmAudioRamStart'))
O.mkdir(exist_ok=False);script=O/'run.lua';script.write_text(aliases+t)
s=importlib.util.spec_from_file_location('runner',R/'tools/run_mesen.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.ROOT=O
raise SystemExit(m.run(script,rom,timeout=90,emulator_options=['--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false']))

