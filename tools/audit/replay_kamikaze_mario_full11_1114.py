"""Separate explicit421 Kamikaze Mario normal-control full1-1 factory."""
import replay_smb1_alts_full11_1114 as Base
LUA_SHA=Base.LUA_SHA['kamikaze']
def controller(raw):return Base.controller(raw,'kamikaze')
def metadata(raw):return Base.metadata(raw,'kamikaze')
