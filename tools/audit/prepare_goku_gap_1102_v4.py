"""Current Goku natural route with original verified wide-gap takeoff window."""
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha
from observe_chip_committed_write import lua
O=R/'build/goku-gap-1102-v4'
ROM=R/'build/menu-family-root-candidate-1102-v1/mr-gimmick-family.nes'
def main():
    O.mkdir(exist_ok=True)
    prior=R/'build/goku-source-route-1102-v3';source=prior/'native/controller.lua'
    policy=O/'policy.lua'
    policy.write_text('local prior=assert(dofile('+lua((prior/'policy.lua').as_posix())+'''))
local launched=false
return function(c)
 local b=prior(c)
 if c.world==0 and c.level==0 and c.x>=1320 and c.x<1440 then
  b={right=true}
  if not launched then
   if c.x>=1360 and c.grounded and c.r('DpAction')==1 and not c.lastA then
    b.a=true;launched=true
   end
  else b.a=true end
 end
 return b
end
''')
    text=source.read_text();old='local POLICY='+lua((prior/'policy.lua').as_posix());assert old in text
    text=text.replace(old,'local POLICY='+lua(policy.as_posix()))
    text=text.replace('d0b445a71d6c539804d7c559fafc2c328ebf97ab4e35e8f3273f94ff8a25d01d',sha(ROM))
    anchor=' if wall%120==0 then'
    assert anchor in text;text=text.replace(anchor," if wall%120==0 or (entered and world()>=1320 and world()<1450 and wall%4==0) then")
    deps=[prior/'policy.lua',*[R/'tools/playthroughs'/('dragon_power_11_v'+str(i)+'.lua')for i in range(3,8)],R/'tools/playthroughs/full_roster_policy_og.lua']
    prepare(O/'native',ROM,text,[Path(__file__),source,policy,*deps],expected=sha(ROM),timeout=240,scope='Controller-only Goku Hard route: hold original jump from native grounded x>=1360 at wide1376..1424 gap; no attack/no state writes/no new platforms. Compact4frame gap diagnostics and120frame other telemetry.',allow_interactive=True)
if __name__=='__main__':main()
