"""Separate explicit421 SMB1 Peach normal-control full1-1 factory."""
import replay_smb1_alts_full11_1114 as Base
LUA_SHA=Base.LUA_SHA['peach']
def controller(raw):return Base.controller(raw,'peach')
def metadata(raw):return Base.metadata(raw,'peach')
