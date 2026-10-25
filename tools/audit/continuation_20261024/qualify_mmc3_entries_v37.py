from pathlib import Path
D=Path(__file__).resolve().parent
s=(D/'qualify_mmc3_entries_v27.py').read_text(encoding='utf-8')
s=s.replace("O=D/'mmc3-sophia-stack-v27'","O=D/'mmc3-static-call-v37'")
start=s.index("full='ROSTER_CONFIG=")
end=s.index('\nreport=dict(',start)
replacement="""assert start==0x155 and size==6
fields=[address(bundle,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(bundle,'FarcallJmpTarget_SMC')+2]
tiny=dict(start=start,bytes=list(bundle['raw'][pos:pos+size]),mutable=mutable,common=image.hook('FarCallCommon'),stack_floor=start+size-0x100)
full='ROSTER_CONFIG={out=OUTPUT}\\nTINY_CALL_GUARD='+im.lua(tiny)+'\\n'+(D/'mmc3_tiny_call_guard_v2.lua').read_text()+'\\n'
"""
s=s[:start]+replacement+s[end:]
anchor="script=out/'entry.lua';script.write_text(full+text);runner.ROOT=out"
new="""old_shared="local function shared()local t={}for a=L.__SMCCODE_RUN__,L.__SMCCODE_RUN__+32 do t[#t+1]=emu.read(a,emu.memType.nesDebug)end;return table.concat(t,',')end"
 new_shared='local function shared()local t={}for _,a in ipairs('+im.lua(fields)+")do t[#t+1]=emu.read(a,emu.memType.nesDebug)end;return table.concat(t,',')end"
 assert text.count(old_shared)==1
 text=text.replace(old_shared,new_shared)
 script=out/'entry.lua';script.write_text(full+text);runner.ROOT=out"""
assert s.count(anchor)==1
s=s.replace(anchor,new)
s=s.replace('on the private flag fix','on the private six-byte tiny-call candidate')
exec(compile(s,str(D/'qualify_mmc3_entries_v27.py'),'exec'),globals())
