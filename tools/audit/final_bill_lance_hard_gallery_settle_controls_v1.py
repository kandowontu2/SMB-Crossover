"""Literal cold-entry/30-settle/seed/postseed observer state-machine models."""
from pathlib import Path
import argparse,json,sys
from final_bill_lance_hard_gallery_source_v1 import ROOT,D,PARENT,SHA,sha,put
from parodius_visibility_hud_static_startup_v1 import MOCK


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ready',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 ready=json.loads((a.ready/'proof.json').read_text());assert ready['ROM_sha256']==SHA and ready['observer_version']==3 and not ready['native_run']
 sys.path.insert(0,str(D/'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1'));from lupa.lua54 import LuaRuntime
 raw=(PARENT/'candidate.nes').read_bytes();models=[]
 for profile in ready['profiles']:
  path=Path(profile['output']);script=(path/'run.lua').read_text();assert sha(path/'run.lua')==profile['script_sha256']
  anchor='local function hook(n,fn)\n';assert script.count(anchor)==1
  altered=script.replace(anchor,anchor+' if TEST_HOOKS then TEST_HOOKS[n]=fn end\n');assert altered.replace(anchor+' if TEST_HOOKS then TEST_HOOKS[n]=fn end\n',anchor)==script
  for fault in ['none','same-seed-finish-status0','same-seed-finish-transform1','run-status0','run-transform1']:
   rt=LuaRuntime(unpack_returned_tuples=True)
   pre=MOCK+'''\nL={};OUTPUT='mock/';TEST_HOOKS={};mem={};ppu={};writes={};emu.memType.nesPrgRom=6
emu.read=function(a,k)if k==6 then return PY_ROM(a)elseif k==2 then return ppu[a]or 0x24 else return mem[a]or 0 end end
emu.write=function(a,v,k)writes[#writes+1]={address=a,value=v,kind=k};if k==2 then ppu[a]=v else mem[a]=v end end
emu.getScreenBuffer=function()local z={};for i=1,256*240 do z[i]=0xff000000 end;return z end
'''
   rt.globals().PY_ROM=lambda i:raw[16+i]
   initialise="""
mem[L.OperMode]=1;mem[L.OperMode_Task]=3;mem[L.GameEngineSubroutine]=8
mem[L.SelectedCharacter]=3;mem[L.BillVariant]=C.variant;mem[L.CrossoverBehaviorVersion]=1
mem[L.PlayerStatus]=0;mem[L.GuestPowerupActive]=0;mem[L.InvSelected+3]=0
for i,v in ipairs(C.cases[1].hud_name)do ppu[0x2023+i-1]=v end
function advance()TEST_HOOKS.GameLoop();TEST_HOOKS.finish()end
for i=1,29 do
 advance();assert(phase=='settle'and age==i and updates==i,'All genuine pre-seed settle updates remain cold')
 assert(mem[L.PlayerStatus]==0 and(mem[L.InvOwnedLo+3]or 0)==0 and #writes==0,'Cold settle never writes the later powered state')
end
TEST_HOOKS.GameLoop()
assert(phase=='next'and age==0 and updates==30,'Age30 seed changes to next at the same entry')
assert(mem[L.PlayerStatus]==1 and mem[L.InvOwnedLo+3]==1 and mem[L.InvOwnedHi+3]==0 and mem[L.InvDirty]==1,'Exact actual boundary seed')
assert(#writes==4 and writes[1].address==L.PlayerStatus and writes[2].address==L.InvOwnedLo+3 and writes[3].address==L.InvOwnedHi+3 and writes[4].address==L.InvDirty,'Only the four declared seed writes')
assert(mem[L.InvSelected+3]==0 and mem[L.CrossoverBehaviorVersion]==1,'No selection or mode seed')
"""
   code=pre+altered+initialise
   if fault=='same-seed-finish-status0':code+='\nmem[L.PlayerStatus]=0\n'
   if fault=='same-seed-finish-transform1':code+='\nmem[L.GuestPowerupActive]=1\n'
   if fault.startswith('same-seed'):
    code+='\nMODEL_OK,MODEL_ERROR=pcall(TEST_HOOKS.finish)\n'
   else:
    code+="""
TEST_HOOKS.finish()
advance();assert(phase=='grant-setup'and current.q.case==1,'Next enters the real first case')
advance();assert(phase=='hud'and #current.grants==0,'Normal uses no invented grant')
for i=1,24 do advance()end
assert(phase=='setup','Original HUD finalizer reaches original setup')
TEST_HOOKS.GameLoop()
assert(phase=='run'and current.stage.kind=='free'and current.stage.face==1,'Full original native-boundary setup executes')
assert(mem[L.PlayerStatus]==1 and mem[L.InvOwnedLo+3]==1 and mem[L.InvSelected+3]==0,'Setup preserves carried inventory/form')
"""
    if fault=='run-status0':code+='\nmem[L.PlayerStatus]=0\n'
    if fault=='run-transform1':code+='\nmem[L.GuestPowerupActive]=1\n'
    code+='\nMODEL_OK,MODEL_ERROR=pcall(TEST_HOOKS.finish)\n'
   rt.execute(code)
   ok=bool(rt.globals().MODEL_OK);assert ok==(fault=='none'),(profile['profile'],fault,rt.globals().MODEL_ERROR)
   if not ok:assert 'Weapon upgrade remains the seeded mushroom form' in str(rt.globals().MODEL_ERROR)
   models.append(dict(profile=profile['profile'],case=fault,passed=True,expected='accept'if fault=='none'else'reject',accepted=ok,
       first_29_cold_finishes_accepted=True,seed_at30_exact4writes=True,same_finish_phase_next_is_strict=True,
       full_boundary_flow_executed=not fault.startswith('same-seed'),synthetic_not_native=True))
 put(a.output/'proof.json',dict(passed=True,source_only=True,native_run=False,synthetic_observer_state_machine=True,models=models,
  complete_generated_script_used=True,only_hook_export_reverse_exact=True,no_game_driver_or_NMI_PPU_execution_claim=True,
  scope='Literal observer callback/control/arena bodies execute against explicit cold/source setup RAM and mocked HUD PPU fields; actual pinned ROM is read for tile definitions. This validates observer chronology, not a new native attempt.',
  bindings={str(f):sha(f)for f in [Path(__file__),a.ready/'proof.json',a.ready/'manifest.json',ROOT/'tools/audit/final_bill_lance_hard_gallery_native_v2.lua',ROOT/'tools/audit/final_bill_lance_hard_gallery_native_v3.lua']+sum([[Path(z['output'])/'run.lua',Path(z['output'])/'config.json']for z in ready['profiles']],[])}))
 print(json.dumps(dict(passed=True,models=len(models),proof_sha256=sha(a.output/'proof.json'))))


if __name__=='__main__':main()
