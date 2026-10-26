"""Prepare exactly one unchanged Hard1F strict pilot; no native launch."""
from pathlib import Path
import argparse,hashlib,json,shutil
from check_tmnt_render_oa import load,address,location
from check_tmnt_audio_fallback_oc import qualified
from observe_chip_committed_write import lua
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepared',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);parent=D/'cv3-remaining-lifecycle-native-v1/fixtures-v4/candidate/pressure-fireball-hard';rom=a.prepared/'candidate.nes';assert sha(rom)=='2cb5fca0757c3e347c264eab0bf3f22bd02d851787f38802a4af3cb0c3aa1fa5';b=load(rom);labels=qualified(rom);cfg=json.loads((parent/'configuration.json').read_text())
 def hook(n):
  if n=='NmiReturn':
   h=cfg['hooks'][n];off=16+h['physical_bank']*8192+(h['address']&8191);assert h['bytes']==[64]and list(b['raw'][off:off+1])==[64]and h['physical_bank']==127;return h
  proc,sep,leaf=n.partition('::');pc=labels[(proc,leaf)]if sep else address(b,n);off=location(b,proc)+pc-address(b,proc);return dict(address=pc,physical_bank=(off-16)//8192,bytes=list(b['raw'][off:off+3]),genuine_source_symbol=n)
 oldhooks=cfg['hooks'];cfg['hooks']={n:hook(n)for n in oldhooks};cfg['hooks']['Cv3FxNativeTick']=hook('Cv3FxNativeTick');cfg['native_tick_caller_return']=0xdcdf
 for n,at in cfg['ram'].items():assert address(b,n)==at,n
 text=(parent/'run.lua').read_text(encoding='utf-8').split('\n',1)[1];before=(ROOT/'tools/audit/cv3_remaining_sfx_lifecycle_common_v2.lua').read_text();after=(ROOT/'tools/audit/cv3_remaining_sfx_legacy_wrapper_native_v1.lua').read_text(encoding='utf-8');assert text.count(before)==1;text=text.replace(before,after,1)
 assert cfg['mode']==1 and cfg['cases'][0]['updates']==240 and cfg['cases'][0]['name']=='pressure-fireball-hard';assert text.endswith('installStaticReturns()\n');script=a.output/'run.lua';script.write_text('CV3_REMAINING_NATIVE_CONFIG='+lua(cfg)+'\n'+text,encoding='utf-8',newline='\n');shutil.copyfile(rom.with_suffix('.lbl'),a.output/'candidate.lbl');(a.output/'configuration.json').write_text(json.dumps(cfg,indent=2)+'\n')
 r=dict(prepared=True,native_executed=False,ROM=str(rom),ROM_sha256=sha(rom),script=str(script),script_sha256=sha(script),configuration_sha256=sha(a.output/'configuration.json'),parent_script= str(parent/'run.lua'),parent_script_sha256=sha(parent/'run.lua'),same_input_baseline=str(D/'cv3-remaining-lifecycle-native-v1/fixtures-v4/baseline/pressure-fireball-hard'),literal_original_workload_controller_RAM_seed_and_all_guards_retained=True,only_metadata_and_actual_native_tick_observer_changed=True,actual_native_tick=cfg['hooks']['Cv3FxNativeTick'],unused_public_Tick_asserted_not_gameplay=True,retained_held_parent_result=str(D/'cv3-remaining-lifecycle-native-v1/native-freeze-v1/qualification-native.json'),scope='Exactly one source-prepared Hard1F240 pilot, not granted/executed. Rebound genuine moved Continue and new actual NativeTick; original compatibility entry is observed as unused, not relabeled. Every original seed/controller/native guard literal retained. Need source/static readiness and explicit grant.',tool_sha256=sha(__file__));(a.output/'preparation.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
