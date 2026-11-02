"""Observe bounded per-jump aggregates on the unchanged late-edge route."""
from pathlib import Path
import prepare_hogan_full11_1102_v2 as P
from prepare_hogan_full11_1102_v3 import ROM, PIN
from prepare_selected_native_packet_v1 import R, prepare, sha

O = R / 'build/hogan-gap-probe-1102-v4'


def main():
    O.mkdir(exist_ok=True)
    assert sha(ROM) == PIN
    s = P.CONTROLLER.replace('not solid(x+24,216)', 'not solid(x+8,216)')
    s = s.replace('local trace={}', 'local trace={}\nlocal flights={}\nlocal flight=nil')
    s = s.replace("local passed=reason=='active-1-2'", "if flight then flight.finishX=wx();flight.finishY=r('Player_Y_Position');flight.reason=reason;flights[#flights+1]=flight;flight=nil end\n local passed=reason=='active-1-2'")
    s = s.replace("out:close();emu.stop(passed and 0 or 1)", "out:close()\n local extra=assert(io.open(OUTPUT..'flights.json','w'));extra:write('[')\n for i,v in ipairs(flights)do\n  if i>1 then extra:write(',')end\n  extra:write(string.format('{\"x\":%d,\"y\":%d,\"minimum_y\":%d,\"finish_x\":%d,\"finish_y\":%d,\"reason\":%q}',v.x,v.y,v.minY,v.finishX,v.finishY,v.reason))\n end\n extra:write(']');extra:close();emu.stop(passed and 0 or 1)")
    s = s.replace('jumping=true;jumpAge=0;jumps=jumps+1', "jumping=true;jumpAge=0;jumps=jumps+1\n    assert(#flights<40);flight={x=x,y=y,minY=y}")
    s = s.replace('jumpAge=jumpAge+delta', "jumpAge=jumpAge+delta\n     if flight then flight.minY=math.min(flight.minY,r('Player_Y_Position'))end")
    s = s.replace('jumping=false;cooldown=16', "jumping=false;cooldown=16\n      if flight then flight.finishX=wx();flight.finishY=r('Player_Y_Position');flight.reason='land';flights[#flights+1]=flight;flight=nil end")
    prepare(O / 'native', ROM, s, [Path(__file__), Path(P.__file__),
            R / 'tools/audit/prepare_hogan_full11_1102_v3.py'], expected=PIN,
            timeout=180, allow_interactive=True,
            scope='Same x+8 controller inputs as v3, only aggregate launch/apex/landing observations '
                  'added to diagnose the second opening gap. No per-frame dump, writes, helper '
                  'or physics changes. Retain negative route if a life is lost. One PNG.')


if __name__ == '__main__':
    main()
