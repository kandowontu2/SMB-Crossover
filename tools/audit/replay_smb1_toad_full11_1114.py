"""Separate explicit421 SMB1 Toad normal-control full1-1 factory."""
import replay_smb1_alts_full11_1114 as Base
LUA_SHA=Base.LUA_SHA['toad']
def controller(raw):return Base.controller(raw,'toad')
def metadata(raw):return Base.metadata(raw,'toad')
