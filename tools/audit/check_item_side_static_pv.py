"""Pin every original symbol and exact patch/append footprint for PV."""
from pathlib import Path
import argparse,hashlib,json
from check_tmnt_render_oa import load,address,location
from check_tmnt_audio_fallback_oc import qualified
def main():
 p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--native-ui',action='store_true');a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);old,new=load(a.baseline),load(a.rom);before,after=old['raw'],new['raw'];ob,nb=qualified(a.baseline),qualified(a.rom)
 if a.native_ui:assert nb[('_FARCALL_COUNT',)]==ob[('_FARCALL_COUNT',)]-1
 changed={str(n):[v,nb.get(n)]for n,v in ob.items()if nb.get(n)!=v and not(a.native_ui and n==('_FARCALL_COUNT',))};assert not changed,list(changed.items())[:10]
 allowed={i:set()for i in [29,59,66,86,89]}
 def call(bank,pos,oldop,oldtarget,newop,newtarget):
  assert (pos-16)//8192==bank
  assert before[pos:pos+3]==bytes([oldop,oldtarget&255,oldtarget>>8])
  assert after[pos:pos+3]==bytes([newop,newtarget&255,newtarget>>8]);allowed[bank]|=set(range(pos,pos+3))
 def append(bank,segment,entry):
  bg=next(g for g in old['segs'].values()if g['name']==json.dumps(segment));ng=next(g for g in new['segs'].values()if g['name']==json.dumps(segment));start=int(bg['ooffs'],0);prior=int(bg['size'],0);size=int(ng['size'],0)
  assert (start-16)//8192==bank and start==int(ng['ooffs'],0)and int(bg['start'],0)+prior==address(new,entry)
  assert before[start+prior:start+size]==bytes([255])*(size-prior);allowed[bank]|=set(range(start+prior,start+size))
 def new_segment_after(bank,segment,prior_segment,entry):
  bg=next(g for g in old['segs'].values()if g['name']==json.dumps(prior_segment));ng=next(g for g in new['segs'].values()if g['name']==json.dumps(segment));start=int(ng['ooffs'],0);size=int(ng['size'],0)
  assert start==int(bg['ooffs'],0)+int(bg['size'],0)and int(ng['start'],0)==address(new,entry)and (start-16)//8192==bank
  assert before[start:start+size]==bytes([255])*size;allowed[bank]|=set(range(start,start+size))
 pos=location(new,'X5NativeNoiseSpan');call(29,pos,0x0d,address(old,'GuestMixChanged'),0x20,address(new,'X5NativeNoiseMask'));new_segment_after(29,'X5_AUDIO_MIX','CHAR_SELECT','X5NativeNoiseMask')
 pos=location(new,'TnMiddleProbeSpan');call(89,pos,0x20,address(old,'BlockBufferColli_Side'),0x20,address(new,'TnSideMiddleProbe'));append(89,'TMNT_COMBAT','TnSideMiddleProbe')
 # The existing18-byte mode wrapper keeps all opcodes; only the target
 # immediate operand changes, with its bank already identical.
 pos=location(old,'InventoryLegacyClassic');oldtarget=address(old,'InventoryLegacyLeaf');newtarget=address(new,'InventoryLegacyItemLeaf')
 x,y=before[pos:pos+18],after[pos:pos+18]
 assert x[0]==y[0]==0x8d and x[3]==y[3]==0xa9 and x[4]==oldtarget&255 and y[4]==newtarget&255 and x[8]==y[8]==0xa9 and x[9]==oldtarget>>8 and y[9]==newtarget>>8
 assert x[:4]==y[:4]and x[5:9]==y[5:9]and x[10:]==y[10:]
 allowed[59]|={pos+4,pos+9};new_segment_after(66,'INVENTORY_ITEM_RETURN','HOT_RENDER_GATE','InventoryLegacyItemLeaf')
 if a.native_ui:
  pos=16+86*8192+nb[('X5OwnInventoryUi','Legacy')]-18-0xa000;target=address(new,'X5NativeInventoryUiLeaf')
  assert after[pos:pos+18]==bytes([0x4c,target&255,target>>8])+bytes([0xea])*15
  allowed[86]|=set(range(pos,pos+18));append(86,'X5_BOUNCE','X5NativeInventoryUiLeaf')
 assert before[:16]==after[:16]and before[16+128*8192:]==after[16+128*8192:]
 counts={}
 for bank in range(128):
  changes={i for i in range(16+bank*8192,16+(bank+1)*8192)if before[i]!=after[i]}
  assert changes<=allowed.get(bank,set()),(bank,sorted(changes-allowed.get(bank,set()))[:10]);
  if changes:counts[bank]=len(changes)
 q=dict(passed=True,ROM_sha256=hashlib.sha256(after).hexdigest(),baseline_ROM_sha256=hashlib.sha256(before).hexdigest(),all_preexisting_qualified_symbols=len(ob),changed_PRG_banks=counts,header_and_all_CHR_exact=True,build_only_farcall_counter_delta=-1 if a.native_ui else 0,exact_patch_and_append_ownership=True)
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q),flush=True)
if __name__=='__main__':main()
