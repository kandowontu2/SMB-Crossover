from pathlib import Path
R=Path(__file__).resolve().parents[2]
for mapper in ('mmc3','mmc5'):
 b=(R/'build'/f'smb-crossover-{mapper}.nes').read_bytes()
 print(mapper,[(hex(i),hex(8192-len(b[16+i*8192:16+(i+1)*8192].rstrip(bytes([255])))))for i in range(64)if 8192-len(b[16+i*8192:16+(i+1)*8192].rstrip(bytes([255])))>=512])
