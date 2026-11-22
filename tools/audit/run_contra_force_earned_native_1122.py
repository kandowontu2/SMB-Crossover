"""Verify controller-earned Contra Force pickups in Mesen, with guarded delivery."""

import argparse
import json
import re

from capture_budget import preflight
from check_contra_force_combined_palette_1122 import comparison_base, compose
from check_contra_force_fast_route_1122 import build_controller, Frozen
import compose_rogue_hud_scene_dirty_cb95_1116 as Hud
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_contra_force_current_cadence_1122 import OUT
from run_stdout_mesen_1110 import run


PICKUP_OBSERVER = r'''
local itemOrder={0,3,1,2}
local itemBlocks={[0]=336,1248,1616,1024}
local function itemHook(pc, callback)
 emu.addMemoryCallback(guard(function()
  local mapped=emu.convertAddress(pc)
  if not mapped or mapped.memType~=emu.memType.nesWorkRam or mapped.address~=3*8192+(pc&8191) then return end
  if first then callback()end
 end),emu.callbackType.exec,pc)
end
itemHook(0xb876,function()
 local slot=emu.getState()['cpu.x']
 local kind=r('PowerUpType',slot)
 assert(slot<6 and kind==itemOrder[#earned+1] and births[kind],'Natural item in expected order')
 assert(r('Enemy_ID',slot)==0x2e and r('Enemy_State',slot)>=128,'Genuine mature actor')
 pendingItem={kind=kind,slot=slot,x=pos('Enemy_X_Position','Enemy_PageLoc',slot),
              y=r('Enemy_Y_Position',slot),tier=r('PlayerStatus'),birth=births[kind]}
end)
itemHook(0xb8cf,function()
 local item=pendingItem
 assert(item and (emu.getState()['cpu.ps']&1)==1,'Real successful collection return')
 local kind,slot=item.kind,item.slot
 local tier=r('PlayerStatus')
 local gear=emu.read(2*8192+0x7f+C.variant,emu.memType.nesWorkRam)
 local sound=r('Square2SoundQueue')
 assert(r('Enemy_Flag',slot)==0 and r('FloateyNum_Control',slot)==(kind==3 and 11 or 6),'Actor erased and credit queued')
 assert(tier==item.tier+(kind<2 and 1 or 0) and gear==(0x10|tier) and (sound&32)~=0,'Tier, gear and pickup sound')
 if kind==2 then
  assert(r('StarInvincibleTimer')==35 and r('AreaMusicQueue')==64,'Ordinary Star grant and music')
 end
 item.update=updates+1;item.tier_after=tier;item.gear=gear;item.sound=sound
 earned[#earned+1]=item;pendingItem=nil
end)
local function earnedTick()
 if not first then return end
 for slot=0,5 do
  local flag=r('Enemy_Flag',slot)
  if flag>0 and flag<128 and r('Enemy_ID',slot)==0x2e then
   local kind=r('PowerUpType',slot)
   if not births[kind] then
    local x=pos('Enemy_X_Position','Enemy_PageLoc',slot)
    local age=r('Enemy_State',slot)
    assert(x==itemBlocks[kind] and age<128,'Item born rising from its actual block')
    births[kind]={update=updates,x=x,y=r('Enemy_Y_Position',slot),state=age}
   end
  end
 end
 if #earned==4 then
  assert(identity()and active()and r('NumberofLives')==3 and r('PlayerStatus')==2
         and r('StarInvincibleTimer')>0,'Active powered player after all four items')
  earnedUpdates=updates-earned[4].update
  if earnedUpdates==25 then finish('contra-force-earned-four')end
 end
end
'''

WEAPON_ALLOCATE_OFFSET = 2006215
WEAPON_ALLOCATE_CODE = bytes.fromhex('9982c3c90af0034ce7a0a90099b2c34c')
WEAPON_KINDS = ((1, 2, 14), (1, 12, 4), (1, 3, 5), (1, 13, 7))
WEAPON_OBSERVER = r'''
emu.addMemoryCallback(guard(function()
 if not first or not active() or not identity() then return end
 local mapped=emu.convertAddress(0xa0ba)
 if not mapped or mapped.memType~=emu.memType.nesWorkRam or mapped.address~=0x20ba then return end
 local cpu=emu.getState()
 local slot,kind=cpu['cpu.y'],cpu['cpu.a']
 local tier=r('PlayerStatus')
 assert(slot>=10 and slot<=21 and kind==weaponKinds[tier+1],'Original weapon allocation for the earned tier')
 assert(emu.read(2*8192+0x382+slot,emu.memType.nesWorkRam)==kind,'Original weapon kind stored in its actual slot')
 assert(emu.read(2*8192+0x7f+C.variant,emu.memType.nesWorkRam)==(0x10|tier),'Actual class gear selects the shot')
 local key=tostring(tier)
 local existing=weaponShots[key]
 if existing then existing.allocations=existing.allocations+1
 else weaponShots[key]={kind=kind,slot=slot,update=updates+1,allocations=1}end
end),emu.callbackType.exec,0xa0ba)
'''

IMPACT_PREIMAGES = {
    0xB7F9: bytes.fromhex('20f59a'),
    0xB7FC: bytes.fromhex('aefcc22044a04c12b8'),
    0xB812: bytes.fromhex('68850da200689503e8e00890f868'),
}
IMPACT_OBSERVER = r'''
local function source(at)return emu.read(2*8192+at,emu.memType.nesWorkRam)end
local function impactRead(name)return emu.read(impactConfig.ram[name],emu.memType.nesDebug)end
local function nativeImpactHook(name,fn)
 local h=impactConfig.hooks[name]
 emu.addMemoryCallback(guard(function()
  if not first or not impactPending then return end
  local mapped=emu.convertAddress(h.pc)
  if not mapped or mapped.memType~=emu.memType.nesPrgRom or mapped.address~=h.offset then return end
  for i,v in ipairs(h.bytes)do assert(emu.read(h.pc+i-1,emu.memType.nesDebug)==v,'Exact native impact seam '..name)end
  fn(emu.getState())
 end),emu.callbackType.exec,h.pc)
end
emu.addMemoryCallback(guard(function()
 if not first or not active() or not identity() then return end
 local mapped=emu.convertAddress(0xa0ba)
 if not mapped or mapped.memType~=emu.memType.nesWorkRam or mapped.address~=0x20ba then return end
 local cpu=emu.getState();local slot=cpu['cpu.y']
 impactAllocations[slot]={tier=r('PlayerStatus'),kind=cpu['cpu.a'],Main=updates+1}
end),emu.callbackType.exec,0xa0ba)
itemHook(0xb7f9,function()
 if not active() or not identity() then return end
 assert(not impactPending,'Previous native contact must complete')
 local shot,foe=source(0x2fc),source(0x2fd)
 local tier=r('PlayerStatus')
 assert(shot>=10 and shot<=21 and foe<6 and tier>=0 and tier<=2,'Real source shot, enemy and tier')
 assert(source(0x7f+C.variant)==(0x10|tier),'Contact uses actual earned class gear')
 if tier>0 then
  local grant=earned[tier==1 and 1 or 3]
  assert(grant and grant.kind==tier-1 and grant.tier_after==tier,'Upgrade collected before powered contact')
 end
 local flag,kind,st=r('Enemy_Flag',foe),r('Enemy_ID',foe),r('Enemy_State',foe)
 assert(flag>0 and flag<128 and kind<21 and(st&32)==0,'Naturally live ordinary enemy before source hit')
 assert(impactRead('ObjectOffset')==foe,'Actual native defender origin')
 impactPending={Main=updates+1,frame=frame,tier=tier,shot_slot=shot,shot_kind=source(0x382+shot),
  radius=source(0x420+shot),shot_x=source(0x34e+shot)+pos('ScreenLeft_X_Pos','ScreenLeft_PageLoc'),
  shot_y=source(0x368+shot),enemy_slot=foe,enemy_id=kind,enemy_state_before=st,
  enemy_x=pos('Enemy_X_Position','Enemy_PageLoc',foe),enemy_y=r('Enemy_Y_Position',foe),
  last_allocation=impactAllocations[shot],native_calls=0,score_calls=0}
 assert(impactPending.shot_kind>0 and impactPending.radius>0,'Actual active source projectile')
 local row=weaponImpacts[tostring(tier)];row.contacts=row.contacts+1
end)
nativeImpactHook('ShellOrBlockDefeat',function(cpu)
 local q=impactPending
 assert(cpu['cpu.x']==q.enemy_slot and impactRead('ObjectOffset')==q.enemy_slot,'Native defeat receives real defender')
 q.native_calls=q.native_calls+1
end)
nativeImpactHook('SetupFloateyNumber',function(cpu)
 local q=impactPending
 assert(cpu['cpu.x']==q.enemy_slot,'Native score receives real defender')
 q.score_calls=q.score_calls+1;q.score_code=cpu['cpu.a']
end)
cfHook('CfSourceImpact',function()
 if not first or not active() or not identity() then return end
 local q=assert(impactPending,'Observed ordinary contact before source impact')
 assert(q.Main==updates+1 and source(0x2fc)==q.shot_slot and source(0x2fd)==q.enemy_slot,'Same contact at source impact')
 assert(q.native_calls==1 and q.score_calls>=1,'Real native defeat and score calls before source action')
 q.enemy_state_after=r('Enemy_State',q.enemy_slot)
 q.popup=r('FloateyNum_Control',q.enemy_slot);q.sound=impactRead('Square1SoundQueue')
 assert((q.enemy_state_after&32)~=0 and q.popup>0,'Actual native defeated state and score popup')
 if q.enemy_id==6 then
  assert(q.popup==1 and q.sound==impactConfig.defeat_sound,'Goomba native score and smack request')
 end
 assert(source(0x382+q.shot_slot)==q.shot_kind and source(0x420+q.shot_slot)==q.radius,'Source shot preserved until its own impact action')
 q.source_impact=true
end)
itemHook(0xb812,function()
 local q=impactPending
 if not q then return end
 assert(q.source_impact and q.Main==updates+1 and source(0x2fc)==q.shot_slot,'Same source action returns at authored seam')
 -- Kind6 is specific to the pistol. Other real weapons can retain or change
 -- kind differently; retain the actual post-action fields instead of guessing.
 q.post_kind=source(0x382+q.shot_slot);q.post_radius=source(0x420+q.shot_slot)
 q.post_frame=source(0x31a+q.shot_slot);q.post_PC=0xb812
 local row=weaponImpacts[tostring(q.tier)]
 row.defeats=row.defeats+1;row.source_actions=row.source_actions+1
 row.unreturned=row.unreturned+1
 if not row.first then row.first=q end
 impactPending=nil
end)
local function impactTick()
 assert(not impactPending,'Native contact and source action finish before Main returns')
 for _,row in pairs(weaponImpacts)do
  row.Main_returned=row.Main_returned+row.unreturned;row.unreturned=0
  if row.first and row.first.Main==updates then row.first.completed_Main=updates end
 end
end
'''


def controller(parent, candidate, identity, *, weapons=False, impacts=False):
    weapons = weapons or impacts
    text, _ = build_controller(parent, candidate, identity, 'all', native=True)

    def once(old, new):
        nonlocal text
        assert text.count(old) == 1, old
        text = text.replace(old, new, 1)

    once('local function finish(reason)',
         'local earned,births,pendingItem,earnedUpdates={},{},nil,0\nlocal function finish(reason)')
    text, count = re.subn(r'(?m)^ local ok=reason[^\n]*$',
                          " local ok=reason=='contra-force-earned-four'and#earned==4 and earnedUpdates==25",
                          text)
    assert count == 1
    once('game_state_writes=false,outputs=0',
         'earned=earned,updates_after_pickups=earnedUpdates,game_state_writes=false,outputs=0')
    observer = PICKUP_OBSERVER
    if weapons:
        at = WEAPON_ALLOCATE_OFFSET
        assert candidate[at:at+len(WEAPON_ALLOCATE_CODE)] == WEAPON_ALLOCATE_CODE
        kinds = WEAPON_KINDS[Frozen.IDENTITIES[identity][1]]
        # Declare the table before finish() so its receipt can include it.
        once('local function finish(reason)', 'local weaponShots={}\nlocal function finish(reason)')
        once('earned=earned,updates_after_pickups=', 'earned=earned,weapon_shots=weaponShots,updates_after_pickups=')
        observer += '\nlocal weaponKinds={' + ','.join(map(str, kinds)) + '}\n'
        observer += WEAPON_OBSERVER
    if impacts:
        from check_contra_force_fast_route_1122 import Current

        bundle = Current.bindings(Hud.inverse(parent))['bundle']
        base = Current.P.CHR + 951 * 1024
        for pc, code in IMPACT_PREIMAGES.items():
            assert candidate[base+(pc & 8191):base+(pc & 8191)+len(code)] == code
        native = {}
        for name in ('ShellOrBlockDefeat', 'SetupFloateyNumber'):
            pc, at = Current.W.address(bundle, name), Current.W.location(bundle, name)
            native[name] = dict(pc=pc, offset=at-16, bytes=list(candidate[at:at+8]))
        config = dict(hooks=native, ram={name: Current.W.address(bundle, name)
                      for name in ('ObjectOffset', 'Square1SoundQueue')},
                      defeat_sound=Current.W.address(bundle, 'Sfx_EnemySmack'))
        rows = {str(tier): dict(contacts=0, defeats=0, source_actions=0,
                              Main_returned=0, unreturned=0) for tier in range(3)}
        declarations = ('local weaponImpacts=' + Frozen.Frozen.lua(rows)
                        + '\nlocal impactPending,impactAllocations=nil,{}\n')
        once('local function finish(reason)', declarations + 'local function finish(reason)')
        once('earned=earned,weapon_shots=', 'earned=earned,weapon_impacts=weaponImpacts,weapon_shots=')
        observer += '\nlocal impactConfig=' + Frozen.Frozen.lua(config) + '\n' + IMPACT_OBSERVER
    once("hook('GameLoop',function()", observer + "\nhook('GameLoop',function()")
    once(' pendingReturn=nil;updates=updates+1\n cfOwner()',
         ' pendingReturn=nil;updates=updates+1\n cfOwner();'
         + ('impactTick();' if impacts else '') + 'earnedTick()')
    Frozen.Frozen.LuaRuntime().compile(text)
    return text


def verified_run(script, rom, candidate, identity, *, weapons=False, impacts=False):
    weapons = weapons or impacts
    expected = Hud.H(candidate)
    assert check(rom)['ROM_sha256'] == expected
    result = run(script, rom, OUT / 'capture', expected, 110, variant=Frozen.IDENTITIES[identity][1])
    receipt = result['receipt']
    if not result['passed']:
        print('FAILED ' + json.dumps(receipt), flush=True)
    assert result['passed'] and result['outputs_written'] == 0 and not result['images']
    assert receipt['updates_after_pickups'] == 25 and receipt['terminal']['lives'] == 3
    assert [item['kind'] for item in receipt['earned']] == [0, 3, 1, 2]
    assert receipt['terminal']['power'] == 2 and receipt['terminal']['star'] > 0
    assert check(rom)['ROM_sha256'] == expected
    weapon_report = {'weapons': receipt['weapon_shots']} if weapons else {}
    if impacts:
        rows = receipt['weapon_impacts']
        assert set(rows) == {'0', '1', '2'}
        for row in rows.values():
            assert row['contacts'] == row['defeats'] == row['source_actions'] == row['Main_returned']
            assert row['unreturned'] == 0
        weapon_report['impacts'] = rows
    print('NATIVE EARNED ' + json.dumps(dict(identity=identity, ROM=expected,
        location='downloads' if rom == Hud.ROM else 'private', script=result['script_SHA256'],
        receipt=result['receipt_SHA256'], earned=receipt['earned'], terminal=receipt['terminal'],
        **weapon_report)), flush=True)
    if weapons:
        shots = receipt['weapon_shots']
        expected_kinds = WEAPON_KINDS[Frozen.IDENTITIES[identity][1]]
        assert set(shots) == {'0', '1', '2'}, ('Actual firing coverage by tier', shots)
        assert [shots[str(i)]['kind'] for i in range(3)] == list(expected_kinds)


def main(identity, install, weapons=False, impacts=False):
    before = check(Hud.ROM)
    installed = Hud.ROM.read_bytes()
    parent = comparison_base(installed)
    target, script = OUT / 'candidate.nes', OUT / 'controller.lua'
    assert {entry.name for entry in OUT.iterdir()} == {target.name, script.name}
    assert target.read_bytes() == installed
    slot = check(target)
    preflight(OUT / 'capture', reserved_files=0)
    require_free_workspace(Hud.R, Hud.ROM, allow_interactive=True)
    _, candidate, _, _ = compose(parent, repair_pickup=True)
    assert comparison_base(candidate) == parent
    text = controller(parent, candidate, identity, weapons=weapons, impacts=impacts)
    old_script = script.read_bytes()
    try:
        script.write_bytes(text.encode())
        if installed == candidate:
            verified_run(script, Hud.ROM, candidate, identity, weapons=weapons, impacts=impacts)
        else:
            target.write_bytes(candidate)
            verified_run(script, target, candidate, identity, weapons=weapons, impacts=impacts)
        assert check(Hud.ROM) == before and Hud.ROM.read_bytes() == installed
        if install and installed != candidate:
            preflight(OUT / 'capture', reserved_files=0)
            require_free_workspace(Hud.R, Hud.ROM, allow_interactive=True)
            try:
                Hud.ROM.write_bytes(candidate)
                verified_run(script, Hud.ROM, candidate, identity, weapons=weapons, impacts=impacts)
                assert Hud.ROM.read_bytes() == candidate
            except BaseException:
                Hud.ROM.write_bytes(installed)
                assert check(Hud.ROM) == before
                raise
    finally:
        target.write_bytes(candidate if install and Hud.ROM.read_bytes() == candidate else installed)
        script.write_bytes(old_script)
        if not install:
            assert check(target) == slot and check(Hud.ROM) == before
    if install:
        assert check(target)['ROM_sha256'] == check(Hud.ROM)['ROM_sha256'] == Hud.H(candidate)


if __name__ == '__main__':
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument('--identity', default='burns', choices=Frozen.IDENTITIES)
    args.add_argument('--install', action='store_true', help='Install only after the private Mesen replay passes.')
    args.add_argument('--weapons', action='store_true', help='Also verify actual projectile births at each weapon tier.')
    args.add_argument('--impacts', action='store_true', help='Also observe real native defeats and source impact actions by earned tier; implies --weapons.')
    options = args.parse_args()
    main(options.identity, options.install, options.weapons, options.impacts)
