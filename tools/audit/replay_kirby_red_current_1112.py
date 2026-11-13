"""Re-run retained natural red-shell encounter without captures or log files."""
import json
import argparse
from hashlib import sha256
from pathlib import Path
from run_stdout_mesen_1110 import R, run


def controller(return_flight=False, expect_catch=False):
    assert not expect_catch or return_flight
    source=R/'build/kirby-red-shell-1110-v3/controller.lua'
    assert sha256(source.read_bytes()).hexdigest()=='15d360ea10e46543d869b39363dd2bf2718f4f210a3aff7db5a9987d8fb4a14c'
    text=source.read_text()
    first,body=text.split('\n',1)
    body=body.replace(" local f=assert(io.open(OUTPUT..'result.json','w'))\n",'')
    body=body.replace(' f:write(json({',' print(\'SMB_NATIVE_RECEIPT \'..json({')
    body=body.replace('ROM_sha256=C.sha','ROM_SHA256=C.sha')
    begin=body.index(' f:close()\n')
    end=body.index(' emu.stop(passed and 0 or 1)',begin)
    body=body[:begin]+body[end:]
    assert 'io.open' not in body and 'emu.takeScreenshot' not in body
    if return_flight:
        body=body.replace('local probes,contactAttempts={},{}','local probes,contactAttempts={},{}\nlocal returnShots={}\nlocal returned=false')
        body=body.replace("reason=='natural-red-shell-hit'", "reason=='natural-red-shell-return' and returned")
        body=body.replace('controller_only=true,','controller_only=true,return_shots=returnShots,returned=returned,')
        body=body.replace(' if hit then return {} end', " if hit then return {b=frame-hit.player.frame>=60 and frame-hit.player.frame<66} end")
        start=body.index("  if hit and r('KbShotType',hit.shell.slot)==0 then")
        end=body.index("  if not capture and x()>=544",start)
        body=body[:start]+'''  if hit then
   for slot=0,2 do
    local p=shot(slot)
    if p.type==3 and p.kind==3 and frame>hit.player.frame+18 then
     local prev=returnShots[#returnShots]
     if not prev or prev.age~=p.age then
      assert(#returnShots<100,'Bounded return trace')
      p.frame=frame;p.player_x=x();returnShots[#returnShots+1]=p
      if prev and p.vx_hi==253 and p.x<prev.x and p.x<=p.player_x+20 then returned=true end
     end
    end
   end
   if returned and r('KbShotType',hit.shell.slot)==0 then finish('natural-red-shell-return');return end
   if frame-hit.player.frame>180 then finish('bounded-return-flight-timeout');return end
  elseif shotInput and frame-shotInput.player.frame>35 then finish('ground-shell-did-not-hit');return end
'''+body[end:]
    if expect_catch:
        old="   if returned and r('KbShotType',hit.shell.slot)==0 then finish('natural-red-shell-return');return end"
        assert body.count(old)==1
        body=body.replace(old,'''   if returned and r('KbShotType',hit.shell.slot)==0 then
    local firstNear=nil
    for _,p in ipairs(returnShots) do
     if p.age>=32 and math.abs(p.x-p.player_x)<=3 then firstNear=firstNear or p.age end
    end
    local last=returnShots[#returnShots]
    if not firstNear or last.age-firstNear>2 or last.age>=89 or math.abs(last.x-last.player_x)>3 then
     finish('return-shell-not-caught');return
    end
    finish('natural-red-shell-return');return
   end''')
        body=body.replace('controller_only=true,','controller_only=true,catch_verified=passed,')
    return first+"\nC.sha=assert(os.getenv('SMB_STDOUT_ROM_SHA'))\n"+body


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--return-flight',action='store_true')
    parser.add_argument('--expect-catch',action='store_true')
    parser.add_argument('--rom',type=Path,default=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes'))
    args=parser.parse_args()
    rom=args.rom
    output=R/'build/kirby-red-current-1112'
    output.mkdir(exist_ok=True)
    script=output/'controller.lua'
    script.write_text(controller(args.return_flight or args.expect_catch,args.expect_catch),encoding='utf-8',newline='\n')
    result=run(script,rom,output/'capture',sha256(rom.read_bytes()).hexdigest(),90)
    summary={k:result[k] for k in ('passed','receipt_SHA256','script_SHA256')}
    summary['receipt']={k:v for k,v in result['receipt'].items() if k in ('reason','returned','return_shots','terminal','actual_ground_copy_attack','native_defeat_return')}
    shots=summary['receipt'].get('return_shots',[])
    if shots:
        summary['return_trace_count']=len(shots)
        summary['receipt']['return_shots']=[p for i,p in enumerate(shots)
            if i<3 or i>=len(shots)-3 or 30<=p['age']<=33 or 65<=p['age']<=70]
    print(json.dumps(summary),flush=True)
    assert result['passed']


if __name__=='__main__':
    main()
