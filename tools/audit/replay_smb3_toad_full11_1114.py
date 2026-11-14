"""Independent strict421 SMB3 Toad full-stage factory."""
import replay_smb3_alts_full11_1114 as Base
LUA_SHA=Base.LUA_SHA['toad3']
def controller(raw):return Base.controller(raw,'toad3')
def metadata(raw):return Base.metadata(raw,'toad3')
