"""Change only dynamic return/DMA callback registration, leaving the whole observer intact."""
from pathlib import Path
import argparse,hashlib,json
ROOT=Path(__file__).resolve().parents[2]
CORE=(Path(__file__).with_name('cv3_remaining_sfx_static_core_v1.lua')).read_text()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def transform(s):
 first=s.index('local pendingReturns,installedReturns={},{}');last=s.index("emu.addMemoryCallback(function()\n if not entered or done or not valid('AudioUpdate')",first);oldcore=s[first:last]
 # queueReturnSlot must be lexically declared before the DMA callback captures
 # it, while install remains the last startup call. Move only the core text.
 original=s;prefix='local strictDMA=0;local strictDmaPending=nil;local strictDmaHooks={};local ppuMask=0';assert s.count(prefix)==1
 s=s[:first]+s[last:];s=s.replace(prefix,CORE+'\n'+prefix,1)
 old='''  emu.addMemoryCallback(function()
   if not strictDmaPending or bank(finish)~=owner then return end''';new='''  queueReturnSlot(finish,function()
   if not strictDmaPending or bank(finish)~=owner then return end'''
 assert s.count(old)==1;s=s.replace(old,new,1);end='''  end,emu.callbackType.exec,finish)
 end
end,emu.callbackType.write,0x4014)''';assert s.count(end)==1;s=s.replace(end,'''  end)
 end
end,emu.callbackType.write,0x4014)''',1)
 s+='\n-- Final startup registration follows every original observer/controller hook.\ninstallStaticReturns()\n'
 edits=[dict(kind='replace-and-relocate-core',original_sha256=hashlib.sha256(oldcore.encode()).hexdigest(),new_sha256=hashlib.sha256(CORE.encode()).hexdigest()),dict(kind='DMA completion to Lua-only slot'),dict(kind='last startup dispatcher installation')]
 assert s.count('installStaticReturns()')==2 and s.count('queueReturnSlot(finish,function()')==1
 return s,edits,oldcore
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--original',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);before=a.original.read_text();after,edits,oldcore=transform(before);script=a.output/'run.lua';script.write_text(after,newline='\n');(a.output/'original-run.lua').write_bytes(a.original.read_bytes());(a.output/'original-return-core.lua').write_text(oldcore,newline='\n')
 result=dict(prepared=True,executed=False,original=dict(path=str(a.original),sha256=sha(a.original)),static_script=str(script),static_sha256=sha(script),core_sha256=sha(Path(__file__).with_name('cv3_remaining_sfx_static_core_v1.lua')),transforms=edits,all_other_generated_script_bytes_retained=True,all_original_output_guards_controller_mode_state_and_raw_APU_logic_retained=True,native_observation_equivalence_required=True,tool_sha256=sha(__file__));(a.output/'preparation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
