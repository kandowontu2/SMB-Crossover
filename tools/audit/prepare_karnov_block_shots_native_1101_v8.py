"""Controller-fired projectiles trigger real brick/question block effects."""
from pathlib import Path
import prepare_karnov_combat_native_1101_v8 as V
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address


def main():
    prepare=V.V.F.Q.P.prepare;once=V.V.F.Q.once
    def blocks(output,rom,t,refs,**kw):
        b=scoped_load(rom)
        t=''.join('L["'+n+'"]='+str(address(b,n))+'\n'for n in ['NativeRarePlayerHeadCollisionCore','Block_State'])+t
        t='local combatBlocks,sawBrick=0,false\n'+t
        t=once(t,'local function route()', '''emu.addMemoryCallback(function()
 if raw(L.NativeRarePlayerHeadCollisionCore)==137 and r('Player_X_Position')~=kr(0x859) then combatBlocks=combatBlocks+1 end
end,emu.callbackType.exec,L.NativeRarePlayerHeadCollisionCore)
local function route()
 for i=0,1 do if r('Block_State',i)&15==2 then sawBrick=true end end''')
        t=once(t,'source_weapons=weaponTicks,','source_weapons=weaponTicks,combat_block_effects=combatBlocks,brick_animation=sawBrick,')
        t=once(t,' if updates<=20 then assert(x==startX,\'No idle drift\');pad={}', ''' if combatBlocks>0 and x<300 then pad={right=true}
 elseif combatKills>0 and x>=236 then
  if r('Player_State')==0 and updates-lastPulse>35 then lastPulse=updates;pulse=22 end
  if pulse>0 then pulse=pulse-1 end
  pad={a=pulse>0,b=updates%12<4}
 elseif updates<=20 then assert(x==startX,'No idle drift');pad={}''')
        lo=t.index('if pickupPrepares>0 and pickupContacts>0 and sawRising')
        hi=t.index(';return end',lo)+len(';return end')
        t=t[:lo]+"if combatBlocks>=3 and sawBrick and pickupPrepares>0 and not lastMain then finish(true,'Controller-fired brick break and question-block powerup spawn');return end"+t[hi:]
        kw['scope']='Controller-only cold Select/Start, crouch-fire Goomba kill, stand left of the first block row and jump/fire into bricks and a question block. Require native projectile block effects, brick animation and real powerup spawn. No player/object/code/RAM injection. Four PNG cap.'
        return prepare(output,rom,t,[*refs,Path(__file__)],**kw)
    V.V.F.Q.P.prepare=blocks;V.main()


if __name__=='__main__':main()
