"""Run the existing90-identity native menu observer against current owning ROM."""
from pathlib import Path
import prepare_doki_menu_native_1101_v1 as D

def main():
    original=D.V.V.prepare
    def prepare(output,rom,controller,refs,**kw):
        output.parent.mkdir(parents=True,exist_ok=True)
        refs=[p.with_name('owner-link.json') if p.name=='graphics-assembly.json' else p for p in refs]
        return original(output,rom,controller,[*refs,Path(__file__)],**kw)
    D.V.V.prepare=prepare
    D.main()

if __name__=='__main__':main()
