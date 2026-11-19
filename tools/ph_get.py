"""Download Poly Haven assets (CC0) into assets/ph/<id>/: textures (2k jpg diff/nor_gl/rough) or models (blend/gltf with textures)."""
import json, os, sys, urllib.request
UA = {'User-Agent': 'Mozilla/5.0 (3d_visual floorplan renderer)'}
def _open(u): return urllib.request.urlopen(urllib.request.Request(u, headers=UA))
D = '/mnt/c/Projects/3d_visual/assets/ph/'
def get(url, path):
    if os.path.exists(path): return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'wb').write(_open(url).read())
def texture(aid, res='2k'):
    f = json.load(_open(f'https://api.polyhaven.com/files/{aid}'))
    out = {}
    for k in ('Diffuse', 'nor_gl', 'Rough', 'arm'):
        if k in f and res in f[k] and 'jpg' in f[k][res]:
            u = f[k][res]['jpg']['url']; p = D + aid + '/' + os.path.basename(u); get(u, p); out[k] = p
    return out
def model(aid, res='1k'):
    f = json.load(_open(f'https://api.polyhaven.com/files/{aid}'))
    b = f['blend'][res]['blend']; p = D + aid + '/' + os.path.basename(b['url']); get(b['url'], p)
    for rel, inc in b.get('include', {}).items(): get(inc['url'], D + aid + '/' + rel)
    return p
if __name__ == '__main__':
    kind = sys.argv[1]
    for a in sys.argv[2:]: print(a, texture(a) if kind == 't' else model(a))
