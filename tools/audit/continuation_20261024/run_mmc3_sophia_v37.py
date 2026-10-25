from pathlib import Path
D=Path(__file__).resolve().parent
s=(D/'run_mmc3_sophia_v27.py').read_text(encoding='utf-8')
s=s.replace("V=D/'mmc3-sophia-stack-v27'", "V=D/'mmc3-static-call-v37'")
s=s.replace("V/'predicate-cpu-v1/proof.json'", "V/'abi-cpu-v1/proof.json'")
s=s.replace("cfg=dict(raw_chr=", "fields=[address(bundle,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(bundle,'FarcallJmpTarget_SMC')+2]\ncfg=dict(smc_fields=fields,raw_chr=")
old="guard=O/'native-guard.lua';guard.write_text('FULL_SMC_GUARD='+im.lua(dict(start=start,bytes=list(bundle['raw'][pos:pos+size]),mutable=mutable))+'\\n'+(D/'mmc3_full_smc_guard_v1.lua').read_text()+'\\nMMC3_ROUTE_GUARD='+im.lua(cfg)+'\\n'+(D/'mmc3_full_route_cache_guard_v3.lua').read_text())"
new="""assert start==0x155 and size==6
native_guard=(D/'mmc3_full_route_cache_guard_v3.lua').read_text()
old_shared="local function shared()local q={}for a=C.smc_start,C.smc_start+32 do q[#q+1]=debug(a)end;return table.concat(q,',')end"
new_shared="local function shared()local q={}for _,a in ipairs(C.smc_fields)do q[#q+1]=debug(a)end;return table.concat(q,',')end"
assert native_guard.count(old_shared)==1
native_guard=native_guard.replace(old_shared,new_shared)
tiny=dict(start=start,bytes=list(bundle['raw'][pos:pos+size]),mutable=mutable,common=image.hook('FarCallCommon'),stack_floor=start+size-0x100)
guard=O/'native-guard.lua';guard.write_text('TINY_CALL_GUARD='+im.lua(tiny)+'\\n'+(D/'mmc3_tiny_call_guard_v1.lua').read_text()+'\\nMMC3_ROUTE_GUARD='+im.lua(cfg)+'\\n'+native_guard)"""
assert s.count(old)==1
s=s.replace(old,new)
s=s.replace("for kind in['prefix','fresh']:","for kind in['fresh','prefix']:")
s=s.replace("else:passed=passed and m.get('result',{}).get('cleared')and m['result']['deaths']==0", "else:passed=passed and m.get('result',{}).get('cleared')and m['result']['deaths']==0")
exec(compile(s,str(D/'run_mmc3_sophia_v27.py'),'exec'),globals())
