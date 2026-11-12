"""Reduce distant impostor texture sources in the student copy only.

The instructor's originals, full meshes, close-view textures, LODs and material
slots remain intact. The native mip builder respects normal-map settings.
"""
import unreal as u
import json
from pathlib import Path

R=Path(u.Paths.project_dir()).resolve()
assert 'StudentMaterials' in R.parts and 'Week11-PCG' in R.parts
reg=u.AssetRegistryHelpers.get_asset_registry()
reg.search_all_assets(True)
rows=[]
for info in reg.get_assets_by_path('/Game/Northwood/DekogonContent/Textures/Impostors', recursive=True):
    if str(info.asset_class_path.asset_name)!='Texture2D':continue
    texture=info.get_asset()
    before=[texture.blueprint_get_size_x(),texture.blueprint_get_size_y()]
    assert u.TrailBiomeAuthoringLibrary.downsize_teaching_texture(texture,1024),str(info.package_name)
    assert u.EditorAssetLibrary.save_loaded_asset(texture,False)
    after=[texture.blueprint_get_size_x(),texture.blueprint_get_size_y()]
    assert max(after)<=1024
    rows.append({'asset':str(info.package_name),'before':before,'after':after})
assert len(rows)==26,len(rows)
(R.parents[1]/'Instructor/distant-foliage-conditioning.json').write_text(json.dumps({
    'status':'PASS','maximum_dimension':1024,'textures':rows,
    'method':'Native Unreal texture-aware downsampling of source data',
    'preserved':['Close-view textures','All meshes and LODs','Graph assets','Instructor originals']},indent=2))
u.SystemLibrary.quit_editor()
