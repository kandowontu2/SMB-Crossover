"""Corrected old-ROM peripheral fixture; original v1 missing-B3-symbol failure retained."""
from check_tmnt_render_oa import Memory
import smb3_host_current3b_owners_v1 as checked

class PeripheralMemory(Memory):
 def __init__(self,b):
  self.hw=[0]*24;self.hwdmc=False
  super().__init__(b)
 def __getitem__(self,at):
  if at==0x4015:return(self.hw[21]&15)|(16 if self.hwdmc else 0)
  return super().__getitem__(at)
 def __setitem__(self,at,v):
  if isinstance(at,int)and 0x4000<=at<=0x4017:
   self.hw[at-0x4000]=v
   if at==0x4015:self.hwdmc=bool(v&16)
  super().__setitem__(at,v)

if __name__=='__main__':
 checked.HostMemory=PeripheralMemory
 checked.sha_old=checked.sha
 # The underlying finite assertions/input states are unchanged; receipt names
 # both v1 and this fixture correction through the final qualification catalog.
 checked.main()
