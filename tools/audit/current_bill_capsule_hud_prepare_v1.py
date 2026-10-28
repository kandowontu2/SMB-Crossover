"""One fresh BillHard earned-gallery readiness for the private HUD union.

No emulator invocation, game writes beyond the inherited disclosed fixture,
settings changes, copies or old-evidence retagging.
"""
from pathlib import Path
import argparse,json
import current_bill_inert_pool_items_prepare_v1 as parent
from current_bill_capsule_hud_candidate_v1 import R,B,P,BASE,EXPECTED,sha,put
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location

OUT=B/'current-85af-bill-hard-earned-hud-v1'
PRIOR=B/'current-44204-bill-hard-earned-v1'

ADDON=r'''
-- Read-only capsule provenance/sampling. All callbacks register at startup.
local capsuleGate,capsulePointer=nil,nil
local capsuleCounts,capsuleFirst,capsuleImages={},{},{}
local capsuleGateCalls,capsulePointerOK,capsuleRejected=0,0,0
local function capsuleExpected()
 if not entered or not current or done or r('SelectedCharacter')~=3 then return nil end
 local selected=r('InvSelected',3)
 if selected==0 then return nil end
 return C.capsules[tostring(selected)],selected
end
hook('CapsuleGate',function()
 capsuleGate=nil
 local q,selected=capsuleExpected();if not q then return end
 assert(r('AvDrawIndex')==20 and r('AvDrawArt')==q.art,'Genuine Bill selected capsule reaches appended gate')
 local s=emu.getState()
 capsuleGate={selected=selected,art=q.art,sp=s['cpu.sp'],case=index}
 capsuleGateCalls=capsuleGateCalls+1
end)
hook('RemainingDraw::ArtPointer',function()
 local gate=capsuleGate;capsuleGate=nil;capsulePointer=nil
 if not gate then return end
 local q,selected=capsuleExpected();local s=emu.getState();local sp=s['cpu.sp']
 local ret=(emu.read(256+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(256+(sp+2)%256,emu.memType.nesDebug)+1)%65536
 assert(q and selected==gate.selected and r('AvDrawIndex')==20 and r('AvDrawArt')==q.art and s['cpu.a']==q.art,'Only immediate selected capsule consumes gate')
 assert(sp==(gate.sp-2)%256 and ret==C.capsule_pointer_return and bank(ret)==61,'Real Draw JSR/stack/bank owns capsule pointer')
 assert(r('R4')==120 and r('R5')==0 and r('R6')==16 and r('R7')==1 and r('AvDrawDirection')==1,'Actual complete capsule anchor/direction')
 onReturn('new-capsule-pointer-v1',function()
  local s=emu.getState();local flags=s['cpu.ps']or s['cpu.p']
  assert(flags,'Actual flags available')
  if flags&1==0 then capsuleRejected=capsuleRejected+1;return end
  assert(r('R0')+256*r('R1')==q.pointer and bank(0xc000)==q.bank,'Actual successful immutable capsule pointer/C bank')
  capsulePointerOK=capsulePointerOK+1
  capsulePointer={case=gate.case,selected=selected}
 end)
end)
hook('CapsuleDmaComplete',function()
 local q,selected=capsuleExpected();if not q or index<2 or index>7 then return end
 if phase~='hud'and phase~='setup'and phase~='run'then return end
 local complete=assert(dmaCompleted,'Original complete256 DMA observer already ran')
 local count=0
 for i=0,63 do
  local at=i*4;local y=emu.read(at,emu.memType.nesSpriteRam);local t=emu.read(at+1,emu.memType.nesSpriteRam)
  local attr=emu.read(at+2,emu.memType.nesSpriteRam);local x=emu.read(at+3,emu.memType.nesSpriteRam)
  for _,p in ipairs(q.parts)do if y==p[1]and t==p[2]and attr==p[3]and x==p[4]then count=count+1 end end
 end
 if count~=3 then return end -- Original mixed-family rejection remains explicit.
 assert(r('InvOwnedLo',3)==current.q.expected_owned and selected==current.q.expected_selected,'Real preceding physical grant owns HUD sample')
 capsuleCounts[index]=(capsuleCounts[index]or 0)+1
 if not capsuleFirst[index]then capsuleFirst[index]=complete.id end
 if not capsuleImages[index]and complete.id>=capsuleFirst[index]+2 then
  capsuleImages[index]={case=index,selected=selected,first_dma=capsuleFirst[index],sample_dma=complete.id,wall=wall,update=updates}
  capture(current.q.name..'-actual-capsule-HUD');event('new-capsule-three-part-DMA',capsuleImages[index])
 end
end)
emu.addEventCallback(function()
 if not done then return end
 assert(capsuleGateCalls>0 and capsulePointerOK>0,'Actual new helper/pointer owner observed')
 local imageRows,countRows={},{}
 for i=2,7 do
  assert(capsuleImages[i]and capsuleCounts[i]>2,'Every acquired gun/passive case has complete three-part actual HUD and delayed image')
  imageRows[#imageRows+1]=capsuleImages[i];countRows[#countRows+1]=capsuleCounts[i]
 end
 local f=assert(io.open(OUTPUT..'capsule-hud-native.json','w'))
 f:write(json({passed=true,ROM_sha256=C.ROM_sha256,mode=r('CrossoverBehaviorVersion'),variant=r('BillVariant'),gate_calls=capsuleGateCalls,
  successful_pointer_returns=capsulePointerOK,mixed_family_rejections=capsuleRejected,actual_complete_three_part_counts=countRows,
  image_records=imageRows,anchor={120,16},OAM_bounds={108,1,131,16},limits='Read-only actual source/genuine pointer and complete OAM evidence. Root must review selected full PPU; source-family alternation remains, no continuous advanced HUD assertion.'}));f:close()
end,emu.eventType.endFrame)
'''


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--collect',type=Path);a=ap.parse_args()
    if a.collect:
        result=parent.collect(a.collect)
        try:
            hud=json.loads((a.collect/'capsule-hud-native.json').read_text())
            assert hud['passed']and hud['mode']==1 and hud['variant']==0 and hud['anchor']==[120,16]
            assert len(hud['image_records'])==6
            result['components']['new_capsule_HUD']=hud
        except Exception as e:result['passed']=False;result['errors'].append('New actual capsule HUD: '+str(e))
        put(a.collect/'component-review.json',result);print(json.dumps(dict(passed=result['passed'],errors=result['errors'])));return
    if OUT.exists():
        draft=OUT/'prepared-not-run.json'
        assert sha(draft)=='11191266e17db69a5594519948fb4c4c43e31e32a5723784cc5533e80e267bb0'
        assert not any((OUT/'native').iterdir())
        put(OUT/'unsubmitted-observer-draft.json',dict(ready_sha256=sha(draft),native_run=False,
            fixes=['Post-grant-only DMA sampling admission; prior selected gun during pickup is valid, so cannot compare it to the future expected acquisition.','Serialize six image/count records as genuine dense arrays; internal case-index2..7 maps are not sent through the inherited array/object heuristic.'],
            previous_code_delta='DMA callback had no hud/setup/run admission; terminal JSON serialized sparse capsuleCounts/capsuleImages directly. Corrected before ROOT submission.'))
    else:OUT.mkdir();(OUT/'native').mkdir()
    prior_path=PRIOR/'prepared-not-run.json';assert sha(prior_path)=='b3530700636d8013e5ec9634ee95fb38420f242ff45bb6e1e9b2e54bc484713f'
    prior=json.loads(prior_path.read_text())
    for q in prior['bindings']:assert sha(q['path'])==q['sha256'],q['path']
    build_path=B/(P+'_build.json');controls_path=B/(P+'_controls.json')
    build=json.loads(build_path.read_text());controls=json.loads(controls_path.read_text())
    assert build['passed']and controls['passed']and build['parent_sha256']==EXPECTED
    rom=B/(P+'.nes');assert sha(rom)==build['candidate_sha256']==controls['candidate_sha256']
    b=scoped_load(rom);cfg=parent.metadata(b)
    assert cfg==json.loads((PRIOR/'config.json').read_text()),'All inherited actual metadata exact; new gate only'
    cfg['ROM_sha256']=sha(rom);cfg['capsules']={}
    for selected in [2,3,4,5]:
        art=b['raw'][location(b,'RemainingDraw::PickupArts')+8+selected]
        ptr=b['raw'][location(b,'AvArtRightLo')+art]+256*b['raw'][location(b,'AvArtRightHi')+art]
        bank=b['raw'][location(b,'AvArtBanks')+art]&127;at=16+bank*8192+ptr%8192;rec=b['raw'][at:at+b['raw'][at]+1]
        assert rec[0]==12
        parts=[]
        for i in range(1,len(rec),4):
            t,attr,y,x=rec[i:i+4]
            parts.append([16+(y-256 if y>=128 else y),t,attr&0xe3,120+(x-256 if x>=128 else x)])
        cfg['capsules'][str(selected)]=dict(art=art,pointer=ptr,bank=bank,bytes=list(rec),parts=parts)
    for key,name,delta in [('CapsuleGate','BillCapsuleHudAnchor',0),('CapsuleDmaComplete','PostDmaMaskEnable',3)]:
        at=location(b,name)+delta
        cfg['hooks'][key]=dict(address=address(b,name)+delta,physical_bank=(at-16)//8192,bytes=list(b['raw'][at:at+3]))
    cfg['hooks']['CapsuleDmaComplete']['physical_banks']=[127,125]
    cfg['capsule_pointer_return']=address(b,'RemainingDraw::Draw')+6
    parent.advanced.B=b;script,guards,adaptations=parent.adapt(cfg)
    marker='emu.addEventCallback(function()\n wall=wall+1';assert script.count(marker)==1
    script=script.replace(marker,ADDON+'\n'+marker,1)
    assert (R/'tools/audit/final_bill_lance_hard_gallery_native_v3.lua').read_text()in script
    assert script.count('FINAL_ITEM_ABILITIES_STATIC_INSTALL_RETURNS()')==1 and'emu.removeMemoryCallback'not in script
    assert 'emu.write('not in ADDON and 'emu.setInput('not in ADDON
    put(OUT/'config.json',cfg);(OUT/'run.lua').write_text(script,encoding='utf-8',newline='\n')
    command=[str(OUT/'native')if s==str(PRIOR/'native')else str(OUT/'run.lua')if s==str(PRIOR/'run.lua')else str(rom)if s==str(BASE)else s for s in prior['command']]
    assert str(BASE)not in command and str(rom)in command
    put(OUT/'command.json',dict(argv=command,maximum_launches=1,retries=0,ROOT_only=True))
    deps={Path(q['path'])for q in prior['bindings']}|{Path(__file__).resolve(),rom,rom.with_suffix('.dbg'),rom.with_suffix('.lbl'),prior_path,
        build_path,controls_path,B/(P+'_controls_negatives.json'),B/(P+'_samus_fixed_hud.s'),B/(P+'_entrypoint.s'),B/(P+'.patch'),
        R/'tools/audit/current_bill_capsule_hud_candidate_v1.py',R/'tools/audit/current_bill_capsule_hud_controls_v1.py',
        OUT/'config.json',OUT/'run.lua',OUT/'command.json'}
    if(OUT/'unsubmitted-observer-draft.json').exists():deps.add(OUT/'unsubmitted-observer-draft.json')
    ready=dict(prepared=True,native_run=False,native_granted=False,ROM=str(rom),ROM_sha256=sha(rom),profile='BillHard earned7/newHUD',
        command=command,maximum_launches=1,retries=0,maximum_owned_workers=1,ROOT_only_native=True,
        inherited_actual_mechanics='Literal seven cases/28 stages, initial mushroom state disclosed; later physical mature grants/autoequip, exclusive guns, Rapid, actual free/contact/terrain/second-edge/machine cadence/source art/SFX/cleanup. All original guards/controller/caps unchanged.',
        guard_scope=prior['hardware'],source_controls=str(controls_path),
        source_mechanism_reuse='Previous fresh44204 weapon CPU controls are reused only because all inherited metadata/body/tables are byte-exact; new fullRemainingDraw/OAM/foreign/Samus/IRQ controls are fresh85af. No old native pass transferred.',
        new_readonly_observer='Actual appended gate -> genuine Draw JSR ArtPointer PC/SP/bank -> success immutable C pointer; all3 compiled OAM parts at genuine E008, six committed images after2 later DMAs. No emulated writes/input or runtime callback registration added.',
        visual_limit='Laser/Flare HUD still shares alternate family turns; no continuously visible-HUD assertion. Root must review actual full images; maximum8 selected PNGs.',
        Easy_scope='Classic Easy rejects2.02 guns. All no-HUD Easy behavior and synthetic mode0 capsule renderer geometry were source checked; no Easy gun acquisition claim.',
        storage=prior['storage'],host_seconds=1800,wall_frame_cap=12000,
        collector=['python','-B',str(Path(__file__).resolve()),'--collect',str(OUT/'native')],Lua_VM_executed=False,
        owned_files=[str(R/'tools/audit'/n)for n in ['current_bill_capsule_hud_candidate_v1.py','current_bill_capsule_hud_controls_v1.py','current_bill_capsule_hud_prepare_v1.py']],
        bindings=[dict(path=str(p.resolve()),sha256=sha(p),bytes=p.stat().st_size)for p in sorted(deps)])
    put(OUT/'prepared-not-run.json',ready)
    print(json.dumps(dict(prepared=True,native_run=False,ready=str(OUT/'prepared-not-run.json'),sha256=sha(OUT/'prepared-not-run.json'),bindings=len(deps),command=str(OUT/'command.json'))))


if __name__=='__main__':main()
