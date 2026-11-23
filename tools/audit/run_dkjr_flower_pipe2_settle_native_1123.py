"""Wait out the native projection of DK Jr.'s verified floor state."""

from unittest.mock import patch

import run_dkjr_flower_pipe2_native_1123 as Pipe


BASE = Pipe.controller
OLD = "   assert(g.defense_hold,'Only an actual defensive jump leaves this waiting floor')"
NEW = """   if not g.defense_hold and read(0x1e)==2 and y==176
      and ram(2,0x6b)==1 and ram(2,0x6c)==1 and ram(2,0x210)==191 then
    return 0
   end
""" + OLD


def controller(raw, *, source_prefix=False):
    base = BASE(raw, source_prefix=source_prefix)
    result = Pipe.S.Check.Replay.one(base, OLD, NEW)
    assert Pipe.S.Check.Replay.one(result, NEW, OLD) == base
    Pipe.S.Check.LuaRuntime().compile(result)
    return result


if __name__ == '__main__':
    with patch.object(Pipe, 'controller', controller):
        raise SystemExit(Pipe.main())
