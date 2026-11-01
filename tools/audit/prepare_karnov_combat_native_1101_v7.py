"""Controller-earned first Goomba kill, mushroom and double-shot native run."""
from pathlib import Path
import sys
import prepare_karnov_pickup_final_native_1101_v5 as F
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address


def main():
    prepare=F.Q.P.prepare
    def combat(output,rom,t,refs,**kw):
        b=scoped_load(rom)
        t='L["HandleEnemyFBallCol"]='+str(address(b,'HandleEnemyFBallCol'))+'\n'+t
        t='local combatKills,nativeDamage,killSound=0,0,false\nlocal killed={}\n'+t
        t=F.Q.once(t,'local function route()', '''emu.addMemoryCallback(function()
 if raw(L.HandleEnemyFBallCol)==254 then nativeDamage=nativeDamage+1 end
end,emu.callbackType.exec,L.HandleEnemyFBallCol)
local function route()
 for i=0,5 do
  if r('Enemy_ID',i)==6 and r('Enemy_State',i)&32~=0 and not killed[i] then
   killed[i]=true;combatKills=combatKills+1
  end
 end
 if combatKills>0 and r('Square1SoundQueue')~=0 then killSound=true end''')
        t=F.Q.once(t,'pad={right=true,a=near and r(\'Player_State\')==0}',
                   'pad=near and{b=updates%24<4}or{right=true}')
        t=F.Q.once(t,'source_weapons=weaponTicks,',
                   'source_weapons=weaponTicks,native_enemy_damage=nativeDamage,goomba_kills=combatKills,kill_sfx=killSound,')
        t=F.Q.once(t,'maxShots==2 and not lastMain then finish(',
                   'maxShots==2 and nativeDamage>0 and combatKills>0 and killSound and not lastMain then finish(')
        kw['scope']='Controller-only actual cold Select/Start, stand and shoot the first real Goomba, require native defeat/SFX, head-hit the first real question block, collect the emerged mushroom and fire original double shots. No RAM/code/object injection. Four PNG cap; full1-1/equipment/source-audio remains separate.'
        return prepare(output,rom,t,[*refs,Path(__file__)],**kw)
    F.Q.P.prepare=combat
    if '--shots'not in sys.argv:sys.argv.append('--shots')
    F.main()


if __name__=='__main__':main()
