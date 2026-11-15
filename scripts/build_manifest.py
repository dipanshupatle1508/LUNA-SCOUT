"""Record hashes without changing input data."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
rows=[]
for folder in ['kernels','terrain']:
    for p in sorted((ROOT/'data'/folder).iterdir()):
        if not p.is_file(): continue
        digest=hashlib.sha256()
        with p.open('rb') as stream:
            for block in iter(lambda:stream.read(1024*1024),b''): digest.update(block)
        rows.append({'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':digest.hexdigest()})
(ROOT/'data'/'manifest.json').write_text(json.dumps({'files':rows,'reference_radius_m':1737400,'active_position_kernel':'de440s.bsp','orientation_kernel':'moon_pa_de440_200625.bpc'},indent=2)+'\n')
print(f'Manifest written: {len(rows)} inputs')
