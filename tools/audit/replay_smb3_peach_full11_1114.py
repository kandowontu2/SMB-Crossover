"""Independent strict421 SMB3 Peach full-stage factory."""
import replay_smb3_alts_full11_1114 as Base
LUA_SHA=Base.LUA_SHA['peach3']
def controller(raw):return Base.controller(raw,'peach3')
def metadata(raw):return Base.metadata(raw,'peach3')
