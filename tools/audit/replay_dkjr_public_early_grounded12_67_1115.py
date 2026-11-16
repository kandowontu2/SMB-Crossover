"""Separate public67 earlier-hop route with25 completed grounded DK Main returns."""
from hashlib import sha256
from types import SimpleNamespace
import replay_dkjr_public_early_depart_67_1115 as Early
from check_ff_stdout_controller_source_1110 import LuaRuntime

SOURCE = 'tools/audit/replay_dkjr_oneway_grounded12_1114.py'
SOURCE_SHA = 'bb4537064cf39372e5786c49aed10b875f53b0518d8405ce44a39e07373407b0'
BASE = '48284d833c4abd9e160dc31ec35ca763190a6d9a13f86ad1cb21336c3063d255'


def one(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new, 1)


def controller(raw):
    base = Early.controller(raw)
    assert sha256(base.encode()).hexdigest() == BASE
    Early.Old.file_bytes(SOURCE, SOURCE_SHA)
    scope = dict(S=SimpleNamespace(P=SimpleNamespace(once=one)), LuaRuntime=LuaRuntime)
    strengthen = Early.Old.pure_function(SOURCE, 'strengthen', scope)
    text = strengthen(base)
    # A physical endFrame may occur after25 completed motors but during
    # the next motor. Wait for its return; retain the final no-pending and
    # living/grounded assertions rather than reading an incomplete update.
    text = one(text, '  if undergroundGrounded>=25 then\n',
               '  if undergroundGrounded>=25 and not undergroundPending then\n')
    # The reused pure transform proves exact restoration internally. Its
    # historical private/ROM APIs are never imported or invoked here.
    LuaRuntime().compile(text)
    return text
