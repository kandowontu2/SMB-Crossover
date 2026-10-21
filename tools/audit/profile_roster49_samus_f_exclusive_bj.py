"""Passive actual-bank CPU scopes on the exact retained Samus F input prefix."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-current-f-samus-exclusive-profile-bj'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    assert not H.exists();H.mkdir()
    cp=R/'build/checkpoints/roster-audit-v49-freeze-render-fast-f/manifest.json';c=json.loads(cp.read_text());assert sha(cp)=='c0f31e09027aad704fc539e95adc0a53abb035fef647206b61bb10d94c8068e2'
    helper=V/'agent49g-samus-crouch-fix-proposal-b/image.py';sp=importlib.util.spec_from_file_location('actual_samus_f_profile',helper);im=importlib.util.module_from_spec(sp);sp.loader.exec_module(im)
    image=im.Image(cp.parent/'smb-crossover-mmc3.nes')
    hooks={n:image.hook(n)for n in ['GameLoop','GameCoreRoutine','EnemiesAndLoopsCore','PlayerGfxHandler','DrawAllMetasprites','AreaParserTaskHandler','BlockObjectsCore','MiscObjectsCore','GuestPostEnemyCollision','InventoryUiTick','PlayerCtrlRoutine','SamusMovement','SamusWeapons','SamusDrawShots','SamusGraphics','SamusHeadProbe','SamusCanStand','SamusAfterBGCollision','RemainingWeapons','AudioUpdate','SamusAudioUpdate','SamusFreezeRenderFinish']}
    hooks.update(NMI=image.hook('NonMaskableInterrupt'),IRQ=image.hook('IrqScrollSplit'))
    hooks.update(NMI_END=image.hook('NonMaskableInterrupt',delta='last'),IRQ_END=image.hook('IrqScrollSplit',delta='last'))
    assert hooks['NMI_END']['bytes'][0]==hooks['IRQ_END']['bytes'][0]==0x40
    source=R/'build/roster-through-2-2/root49-f-samus-route-s-2-v0-mmc3';m=json.loads((source/'manifest.json').read_text());assert m['rom_sha256']==sha(image.path)
    # Actual F farcalls execute their JSR in linked RAM at FarcallJmpTarget_SMC.
    # Admit only that exact assembled continuation, retaining its eight bytes.
    ram_pc=image.ram['FarcallJmpTarget_SMC']+3
    ram_return=image.hook('FarCallCommon',delta=ram_pc-image.ram['FarCallCommon'])
    assert ram_return['bytes'][0]==0x8d
    helper_body=(R/'tools/audit/ordinary_roster_profile49.lua').read_text()
    anchor=" assert(q.bank>=0,'Only actual ROM callers are timed')";assert helper_body.count(anchor)==1
    helper_body=helper_body.replace(anchor,""" if q.bank<0 then
  assert(pc==C.ram_return.address,'Only actual ROM or the exact compiled FarCallCommon RAM continuation '..n..' pc='..pc)
  for j,v in ipairs(C.ram_return.bytes)do assert(guard[j]==v,'Exact assembled farcall RAM continuation8 '..n)end
 end""")
    helper_body=helper_body.replace('local calls,returns={},{}','local calls,returns={},{}\nlocal isrDepth,spent,starts=0,{},{}')
    helper_body=helper_body.replace("state=r('Player_State'),engine=r('GameEngineSubroutine'),skip=r('ShouldSkipDrawSprites')}","state=r('Player_State'),engine=r('GameEngineSubroutine'),skip=r('ShouldSkipDrawSprites'),isrDepth=isrDepth,isrSpent=spent[isrDepth+1]or 0}")
    helper_body=helper_body.replace('cycles=z.cycle-q.entry.cycle,frame_delta=', 'cycles=z.cycle-q.entry.cycle,interrupted_cycles=z.isrSpent-q.entry.isrSpent,exclusive_cycles=z.cycle-q.entry.cycle-z.isrSpent+q.entry.isrSpent,entry_ISR_depth=q.entry.isrDepth,frame_delta=')
    helper_body=helper_body.replace('c.bank==physical(pc)then','c.bank==physical(pc)and c.entry.isrDepth==z.isrDepth then')
    old="""hook('NMI',function()nmi=nmi+1 end)
hook('IRQ',function()irq=irq+1 end)
for n in pairs(H)do if n~='NMI'and n~='IRQ'then hook(n,function()begin(n)end)end end"""
    new="""local function enterISR()
 isrDepth=isrDepth+1;starts[isrDepth]=emu.getState()['cpu.cycleCount']-7
end
local function leaveISR()
 assert(isrDepth>0,'Actual profile interrupt stack balances')
 spent[isrDepth]=(spent[isrDepth]or 0)+emu.getState()['cpu.cycleCount']+6-starts[isrDepth]
 starts[isrDepth]=nil;isrDepth=isrDepth-1
end
hook('NMI',function()nmi=nmi+1;enterISR()end)
hook('IRQ',function()irq=irq+1;enterISR()end)
hook('NMI_END',leaveISR);hook('IRQ_END',leaveISR)
for n in pairs(H)do if n~='NMI'and n~='IRQ'and n~='NMI_END'and n~='IRQ_END'then hook(n,function()begin(n)end)end end"""
    assert helper_body.count(old)==1;helper_body=helper_body.replace(old,new)
    assert 'exclusive_cycles='in helper_body and 'isrDepth=isrDepth'in helper_body
    scoped=H/'profile-actual-ram-return.lua';scoped.write_text(helper_body)
    policy=H/'policy.lua';policy.write_text('ORDINARY_PROFILE='+im.lua(dict(hooks=hooks,ram=image.ram,ram_return=ram_return,start_frame=12500,stop_frame=14800,base_policy=(V/'root49-current-c-transfers-a/identity.lua').as_posix()))+'\nreturn dofile('+im.lua(scoped.as_posix())+')\n')
    sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
    size=workspace_bytes(R);assert size+100000000<70000000000
    deps=[Path(__file__),helper,R/'tools/audit/ordinary_roster_profile49.lua',V/'root49-current-c-transfers-a/identity.lua',source/'inputs.csv',source/'manifest.json']
    preparation=dict(checkpoint_sha256=sha(cp),dependencies={str(p.relative_to(R)):sha(p)for p in deps},policy_sha256=sha(policy),private_helper_sha256=sha(scoped),hooks=hooks,ram_return=ram_return,
      exclusive_method='Actual8-byte mapped NMI/IRQ entry/RTI scope stack. Completed inclusive interrupt costs per nesting depth; each measured call subtracts completed child interruptions at entry_depth+1, counting nested IRQ/NMI once. Same-depth return required. Hardware entry7/RTI6 cycles included.',
      predecessor_negative='BF assumed ROM-only callers, but actual assembled MMC3 FarCallCommon executes its JSR in linked RAM. Preserve BF failure. BH admits only compiled FarcallJmpTarget_SMC+3 with exact assembled8 bytes and unchanged dynamic SP/entry/return guards; unknown callers still fail.',
      phase_cap=120000000,phase_reserve=20000000,workspace_before=size,global_cap=70000000000,scope='Unchanged F power-on replay. Pure passive calls/return8-byte+physical-bank or exact RAM+SP guards, no seeded state.12500..14800 sample; expected partial route stops14850.')
    (H/'preparation.json').write_text(json.dumps(preparation,indent=2)+'\n')
    for n,h in c['source_hashes'].items():assert sha(R/n)==h,n
    args=[sys.executable,str(R/'tools/playthroughs/roster_run.py'),'--character','2','--mapper','mmc3','--rom',str(image.path),'--tag','root49-f-samus-exclusive-bj','--policy',str(policy),'--replay',str(source/'inputs.csv'),'--frames','14850','--timeout','900','--workspace-cap-gb','70']
    (H/'command.json').write_text(json.dumps(args,indent=2)+'\n')
    with (H/'native.log').open('wb')as f:q=subprocess.run(args,cwd=R,stdout=f,stderr=subprocess.STDOUT)
    p=R/'build/roster-through-2-2/root49-f-samus-exclusive-bj-2-v0-mmc3';manifest=json.loads((p/'manifest.json').read_text())
    for n,h in c['source_hashes'].items():assert sha(R/n)==h,n
    report=dict(exit=q.returncode,manifest_sha256=sha(p/'manifest.json'),result=manifest.get('result'),native_log_sha256=sha(H/'native.log'),preparation_sha256=sha(H/'preparation.json'),expected_partial=True,profile_analysis_pending=True,goal_complete=False)
    (H/'native-result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
if __name__=='__main__':main()
