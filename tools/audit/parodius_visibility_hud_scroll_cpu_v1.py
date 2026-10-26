"""Execute capture scroll policy and exact public ABI/intentional I/O delta."""
from pathlib import Path
import argparse,hashlib,itertools,json,shutil
from check_nmi_vram_fast_cpu_v1 import Bus,run,scoped_load,address
from check_tmnt_render_oa import location
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
class Ppu(Bus):
 def __init__(self,b,t=0,w=0):
  self.t=t;self.v=t;self.w=w;self.fineX=5;self.increment=1;self.io=[];super().__init__(b)
 def __getitem__(self,a):
  value=super().__getitem__(a)
  if a==0x2002:self.w=0;self.io.append(('r',a,value))
  if a==0x2007:self.v=(self.v+self.increment)&0x7fff;self.io.append(('r',a,value))
  return value
 def __setitem__(self,a,v):
  if isinstance(a,int)and 0x2000<=a<=0x2007:
   self.io.append(('w',a,v))
   if a==0x2000:self.t=(self.t&~0xc00)|((v&3)<<10);self.increment=32 if v&4 else 1
   if a==0x2005:
    if self.w:self.t=(self.t&~0x73e0)|((v&7)<<12)|((v&0xf8)<<2)
    else:self.t=(self.t&~31)|(v>>3);self.fineX=v&7
    self.w^=1
   if a==0x2006:
    self.t=((self.t&255)|((v&63)<<8))if not self.w else((self.t&0x7f00)|v);self.w^=1
    if not self.w:self.v=self.t
   if a==0x2007:self.v=(self.v+self.increment)&0x7fff
  return super().__setitem__(a,v)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);shutil.copy2(Path(__file__),a.output/Path(__file__).name);paths=[a.base/'baseline-rebuild-v2/candidate.nes',a.base/'hud-candidate-v11/candidate.nes',a.candidate];assert [sha(f)for f in paths]==['50b51c3c69f45ef137720c47f521574097f421056e3b73296d06ba70080d2363','64f454a248785ff4c53bd0d52158fd2cf5389de38e5c35a888c3e6a6ed982362','df5154bc035ba2c392bb8d34068897a2bccf7a78a6f4554bd6790d31a586c357'];bundles=[scoped_load(f)for f in paths];rows=[]
 def execute(b,whole,ctrl,variant,mirror,freeze,initial,flags):
  m=Ppu(b,0x5b3f if initial else 0,initial);m.page(2,88);m.palette=[(i*17+3)&63 for i in range(32)]
  values=dict(SelectedCharacter=18,OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,DisableScreenFlag=0,CurrentBankC=216,CurrentBank=215,NmiDisable=0,Sprite0HitDetectFlag=1,VvVariant=variant,PnBombCapturePending=1,PnBombPaletteReady=0,PnInitialized=0x50,SmFreezePalettePending=freeze,X5HudChrUpper=1,InvHudActive=0,Mirror_PPUCTRL=mirror,Mirror_PPUMASK=0x1e,VRAM_Buffer_AddrCtrl=ctrl,VRAM_Buffer1_Offset=0,VRAM_Buffer2_Offset=0,ReloadCHRBank=1,X5WideChrActive=1,SsChrActive=0,HorizontalScroll=117)
  for n,v in values.items():m.put(address(b,n),v)
  for i in range(12):m.put(address(b,'X5ChrMode')+i,0);m.put(address(b,'CurrentCHRBank')+i,i)
  for i,v in enumerate([0x20,0x22,3,0x13,0x27,0x31,0]):m.put(address(b,'VRAM_Buffer1')+i,v)
  for i,v in enumerate([0x21,0x10,0xc3,0x17,0]):m.put(address(b,'VRAM_Buffer2')+i,v)
  for i,v in enumerate([0x3f,0x15,3,1,17,33,0]):m.put(address(b,'SmFreezePalettePacket')+i,v)
  lo=m[address(b,'VRAM_AddrTable_Low')+ctrl];hi=m[address(b,'VRAM_AddrTable_High')+ctrl];pointer=lo+256*hi;m.put(address(b,'NmiR0'),lo);m.put(address(b,'NmiR1'),hi)
  if ctrl==19:
   seg=next(g for g in b['segs'].values()if g['name']=='"TITLE"');m.page(1,(int(seg['ooffs'],0)-16)//8192)
  m.put(0x2002,0x80);m.put(0x1fe,0xff);m.put(0x1ff,1);m.io=[]
  result=run(b,m,address(b,'NonMaskableInterrupt'if whole else'SamusFreezeUpdateScreen'),address(b,'OAMandReadJoypad')if whole else 0x0200,0x55,37,193,flags)
  return result,m,pointer
 def compare(whole,ctrl,variant,mirror,freeze,initial,flags,kind):
  out=[execute(b,whole,ctrl,variant,mirror,freeze,initial,flags)for b in bundles];base,old,new=[r[0]for r in out]
  for key in ['state','reads','ram','banks']:assert base[key]==old[key]==new[key],(kind,key,ctrl,variant,mirror,freeze,initial,flags)
  shadow=address(bundles[0],'PnBombPaletteShadow')+31
  at=next(i for i,pair in enumerate(old['writes'])if pair[0]==shadow)+1;expected=old['writes'][:at]+[(0x2005,0),(0x2005,0)]+old['writes'][at:];assert new['writes']==expected,('Only intentional two scroll writes',kind,ctrl,variant,mirror,freeze)
  assert base['writes']==old['writes'],'v11/source baseline no-marker I/O exact'
  io=out[1][1].io;at=next(i for i,e in enumerate(io)if e[0]=='r'and e[1]==0x2007 and sum(t[0]=='r'and t[1]==0x2007 for t in io[:i+1])==32)+1;assert out[2][1].io==io[:at]+[('w',0x2005,0),('w',0x2005,0)]+io[at:]
  assert new['cycles']-old['cycles']==13
  m=out[2][1];oldm=out[1][1]
  if whole:assert m.t==0 and m.w==0 and m.fineX==0 and oldm.t==(0 if freeze else 0x3300)
  else:assert m.t==((mirror&3)<<10)and m.w==0 and m.fineX==0,('gateway t/w/fineX',ctrl,mirror,freeze,initial,m.t,m.w,m.fineX,out[2][1].io)
  rows.append(dict(kind=kind,whole_regular_NMI_prefix=whole,ctrl=ctrl,actual_linked_initial_pointer=out[0][2],variant=variant,Mirror_PPUCTRL=mirror,freeze=freeze,initial_scroll_latch=initial,flags=flags,baseline_cycles=base['cycles'],v11_cycles=old['cycles'],after_cycles=new['cycles'],old_t=oldm.t,new_t=m.t))
 try:
  # Controls2/4 are actual linked fixed ROM palettes;6 is linked Buffer2.
  for spec in itertools.product([False,True],[0,2,4,6],[1,2,3],range(0xa0,0xa8),[0,128],[0,1],[0x30,0x75]):compare(*spec,'primary_capture_owners')
  for spec in itertools.product([False,True],range(20),[1,2,3],[0x81,0x86],[0,128]):compare(*spec,0,0xff,'all_native_ctrl_selectors')
 except Exception as e:
  (a.output/'failure.json').write_text(json.dumps(dict(passed=False,completed_cases=len(rows),error=repr(e),tool_sha256=sha(Path(__file__))),indent=2)+'\n');raise
 (a.output/'cases.json').write_text(json.dumps(rows,separators=(',',':'))+'\n');q=dict(passed=True,native_run=False,adopted=False,goal_complete=False,baseline_ROM_sha256=sha(paths[0]),v11_ROM_sha256=sha(paths[1]),candidate_ROM_sha256=sha(paths[2]),cases=len(rows),public_AXYP_SP_RAM_banks_exact=True,palette_reads_exact=True,only_intended_IO_delta='Two PPUSCROLL0 writes immediately after32nd capture read/shadow store; all other application writes and ordered I/O exact.',whole_NMI_before_OAM_t_fineX_w_zero=True,capture_only_extra_cycles=13,cases_sha256=sha(a.output/'cases.json'),tool_sha256=sha(Path(__file__)),limits='Actual assembled gateway and whole regular-NMI prefix with isolated legal linked ROM/RAM packet setups and modeled PPU t/v/w/fineX. PPU register semantics model is not a hardware raster/DMA/IRQ/DMC replay. OperMode1 is game flow, not difficulty. Native baseline/candidate images and final timing remain required.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))
if __name__=='__main__':main()
