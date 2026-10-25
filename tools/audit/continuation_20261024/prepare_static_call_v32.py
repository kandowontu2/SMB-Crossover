from pathlib import Path
D=Path(__file__).resolve().parent;t=(D/'build_mmc3_static_call_v31.py').read_text();t=t.replace("O=D/'mmc3-static-call-v31'","O=D/'mmc3-static-call-v32'")
t=t.replace("if parent[16+bank*8192:16+(bank+1)*8192]!=bytes([255])*8192:continue","if parent[16+bank*8192:16+(bank+1)*8192]not in(bytes([255])*8192,bytes(8192)):continue")
t=t.replace("if z:empty.append((bank,z[1]))","if z and not re.search(r'\\bload\\s*=\\s*'+re.escape(z[1])+r'\\b',cfg):empty.append((bank,z[1]))")
(D/'build_mmc3_static_call_v32.py').write_text(t)
