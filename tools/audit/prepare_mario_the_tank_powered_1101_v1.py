"""Explicit powered-state fixture for native boot rendering; not a pickup run."""
from pathlib import Path
import json
import prepare_mario_the_tank_native_1101_v1 as N
def main():
    original=N.prepare
    def prepare(output,rom,controller,refs,**kw):
        controller=controller.replace("shot('selected');",'')
        controller=controller.replace("shot('gameplay-entry');", "emu.write(L['PlayerStatus'],2,emu.memType.nesDebug);emu.write(L['PlayerSize'],0,emu.memType.nesDebug);")
        controller=controller.replace("elseif phase=='walk' and age>=36 then", "elseif phase=='walk' and (age==8 or age==24) then shot('boots-'..age)\n elseif phase=='walk' and age>=36 then")
        controller=controller.replace("local passed=x>40 and", "local passed=r('PlayerStatus')==2 and x>40 and")
        controller=controller.replace('"controller_only":true','"controller_only":false,"powered_fixture":true')
        kw['scope']='Native boot-render fixture after ordinary menu/Start: sets PlayerStatus2 and PlayerSize0 once. Three PNGs. Not natural pickup, growth or full-stage evidence.'
        target=output.with_name('native-powered-final')
        original(target,rom,controller,[*refs,Path(__file__)],**kw)
        ready=target/'ready.json';q=json.loads(ready.read_text());q['emulated_writes']=True;q['fixture']='PlayerStatus=2 and PlayerSize=0 once after normal gameplay entry'
        ready.write_text(json.dumps(q,indent=2)+'\n')
    N.prepare=prepare;N.main()
if __name__=='__main__':main()
