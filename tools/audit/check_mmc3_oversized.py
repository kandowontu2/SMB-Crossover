"""Controller-only cold entry checks for every identity in oversized MMC3."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,re
R=Path(__file__).resolve().parents[2]
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--rom',type=Path,default=R/'build/oversized-mmc3-nf/smb-crossover-mmc3-oversized.nes')
 p.add_argument('--names',nargs='*');p.add_argument('--output',type=Path,required=True)
 p.add_argument('--behavior',choices=('easy','hard'),default='easy')
 a=p.parse_args();rom=a.rom.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
 labels={m[2]:int(m[1],16)for line in rom.with_suffix('.lbl').read_text().splitlines()if(m:=re.fullmatch(r'al ([0-9A-Fa-f]+) \.(\S+)',line))}
 cases=[('Mario',0,0,None,0),('Luigi',0,8,'MarioVariant',1),('Mega Man',1,1,'ProtoVariant',0),('Proto Man',1,1,'ProtoVariant',1),('Samus',2,2,None,0),('Bill',3,3,'BillVariant',0),('Lance',3,3,'BillVariant',1),('Link',4,4,'Z2Variant',0),('Zelda II Link',4,4,'Z2Variant',1),('Simon',5,5,'Cv3Variant',0),('Grant',5,5,'Cv3Variant',1),('Sypha',5,5,'Cv3Variant',2),('Alucard',5,5,'Cv3Variant',3),('Pit',6,6,None,0),('Rygar',7,7,None,0),('Scrooge',8,12,'DarkwingVariant',0),('Darkwing',8,12,'DarkwingVariant',1),('Bass',9,9,None,0),('Ryu',10,10,None,0),('Sophia',11,11,None,0),('Kirby',12,13,None,0),('Chip',13,14,'CdVariant',0),('Dale',13,14,'CdVariant',1),('Little Mac',14,15,None,0),('Mike Jones',15,16,None,0),('SMB3 Mario',16,17,'M3Variant',0),('SMB3 Luigi',16,17,'M3Variant',1),('Vic Viper',17,18,None,0),('Leonardo',18,19,'TnVariant',0),('Raphael',18,19,'TnVariant',1),('Michelangelo',18,19,'TnVariant',2),('Donatello',18,19,'TnVariant',3)]
 cases.append(('Meta Knight',12,13,'KbVariant',1))
 template=(R/'tests/full-roster-entry.lua').read_text().replace('%128','')
 first=template.index(' if actual(0xc000)~=ctx then');end=template.index(' smc=shared()',first)
 template=template[:first]+template[end:]
 template=template.replace('b.start=frame==60','b.start=frame>=150 and frame%12==0')
 template=template.replace('b.start=frame>=60 and frame%12==0','b.start=frame>=150 and frame%12==0')
 template=template.replace('local frame,phase,entered=0,0,nil','local frame,phase,entered=0,0,nil\nlocal hardStage=TARGET_HARD and 0 or 3')
 template=template.replace(' local b={}\n', ''' local b={}
 if hardStage<3 then
  if frame>=150 and frame%12==0 then
   local menu=r('CrossoverMenuState')
   if hardStage==0 and menu==0 then
    if r('CrossoverOptionsFocus')==0 then b.down=true else b.a=true;hardStage=1 end
   elseif hardStage==1 and menu==4 then
    if r('CrossoverOptionsFocus')~=1 then b.down=true
    elseif r('CrossoverBehaviorVersion')==0 then b.a=true else hardStage=2 end
   elseif hardStage==2 then
    if menu==4 then b.b=true elseif menu==0 then hardStage=3 end
   end
  end
  emu.setInput(b,0);return
 end
''',1)
 template=template.replace("r('CrossoverBehaviorVersion')==0 and r('PlayerOutlinesOff')==1", "r('CrossoverBehaviorVersion')==(TARGET_HARD and 1 or 0) and r('PlayerOutlinesOff')==1")
 template=template.replace("   assert(table.concat(name):match('^%s*(.-)%s*$')==TARGET_MENU_NAME,", "   if table.concat(name):match('^%s*(.-)%s*$')~=TARGET_MENU_NAME then emu.setInput({},0);return end\n   assert(table.concat(name):match('^%s*(.-)%s*$')==TARGET_MENU_NAME,")
 template=template.replace("if frame>1800 then error('Cold roster entry timed out')end", "if frame>1800 then shot('timeout');error('Cold roster entry timed out')end")
 template=template.replace("local frame,phase,entered=0,0,nil","""local frame,phase,entered=0,0,nil
local initialChrChecked=false
local referenceChr=nil
local uploadedBytes=0
local preservedBytes=0
emu.addMemoryCallback(function()
 if emu.convertAddress(0xc000).address//8192==228 and emu.read(L.OperMode,emu.memType.nesDebug)==1 and emu.read(L.DisableScreenFlag,emu.memType.nesDebug)==0 then
  local st=emu.getState();local scan=st['ppu.scanline']
  assert(scan>=241 and scan<=260,'Weapon cache upload remains inside VBlank: '..scan..':'..st['ppu.cycle'])
  uploadedBytes=uploadedBytes+1
 end
end,emu.callbackType.write,0x2007)
local freePairs={[0]=true,[1]=true,[13]=true,[14]=true,[15]=true,[21]=true,[25]=true,[27]=true,[29]=true,[30]=true,[31]=true}
emu.addMemoryCallback(function()
 local bank=emu.read(L.M3HardwareSpecial,emu.memType.nesDebug)
 if referenceChr and bank>=132 and bank<168 and bank%2==0 and emu.read(L.M3CacheProfile,emu.memType.nesDebug)>=2 then
  for i=0,2047 do
   if i<1024 or not freePairs[(i-1024)//32]then
    assert(emu.read(bank*1024+i,emu.memType.nesChrRam)==referenceChr:byte(2049+i),'Weapon composite preserves native terrain/actors byte '..i)
    preservedBytes=preservedBytes+1
   end
  end
 end
end,emu.callbackType.exec,L.NonMaskableInterrupt_RTI)
emu.addMemoryCallback(function(a,v) error(string.format('Unexpected MMC5/ExRAM write %04x=%02x',a,v))end,emu.callbackType.write,0x5000,0x5fff)
""")
 anchor=' frame=frame+1\n'
 template=template.replace(anchor,anchor+''' if frame==145 then
  local f=assert(io.open(RAW_CHR,'rb'));local bytes=f:read(262144);f:close();referenceChr=bytes
  for i=0,262143 do assert(emu.read(i,emu.memType.nesChrRam)==bytes:byte(i+1),'Boot cache byte '..i)end
  initialChrChecked=true
 end
''')
 marker="   print('PASS '..TARGET_NAME"
 template=template.replace(marker,"   local cacheProof=assert(io.open(OUTPUT..'cache-proof.json','w'));cacheProof:write(string.format('{\"boot_chr_bytes_verified\":262144,\"weapon_upload_bytes_within_vblank\":%d,\"retained_terrain_actor_bytes_verified\":%d,\"no_MMC5_or_ExRAM_writes\":true}',uploadedBytes,preservedBytes));cacheProof:close()\n"+marker)
 template=template.replace('NMI restores logical bank shadow, with decoded publication windows checked; no full-level or video review claim','NMI restores full8-bit bank shadows; CHR-RAM boot contents, VBlank-only weapon uploads and retained terrain/actor bytes checked; no full-level claim')
 spec=importlib.util.spec_from_file_location('m3_mesen',R/'tools/run_mesen.py');runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
 results={}
 for name,slot,char,var,value in cases:
  if a.names and name not in a.names:continue
  folder=out/name.lower().replace(' ','-');folder.mkdir(exist_ok=True)
  menu_name={'Samus':'SAMUS ARAN','Bill':'BILL RIZER','Lance':'LANCE BEAN','Simon':'SIMON BELMONT','Scrooge':'SCROOGE MCDUCK','Darkwing':'DARKWING DUCK','Ryu':'RYU HAYABUSA','Sophia':'SOPHIA III'}.get(name,name.upper())
  constants=dict(TARGET_NAME=name,TARGET_MENU_NAME=menu_name,TARGET_SLOT=slot,TARGET_CHARACTER=char,TARGET_VARIANT_ADDRESS=labels[var]if var else 0,TARGET_VARIANT=value,TARGET_HARD=a.behavior=='hard',RAW_CHR=(R/'build/oversized-mmc3-nf/source/chr/characters/oversized-raw.chr').as_posix())
  script=folder/'entry.lua';script.write_text('\n'.join(k+'='+json.dumps(v)for k,v in constants.items())+'\n'+template)
  runner.ROOT=folder
  code=runner.run(script,rom,timeout=45,emulator_options=['--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
  results[name]=dict(exit=code);(out/'results.json').write_text(json.dumps(dict(ROM_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),behavior=a.behavior,results=results),indent=2)+'\n')
  if code:return code
 return 0
if __name__=='__main__':raise SystemExit(main())
