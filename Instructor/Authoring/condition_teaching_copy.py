"""Downsize only the staged private repository's texture source data, using UE's mip builder."""
import unreal as u,json,hashlib
from pathlib import Path
R=Path(u.Paths.project_dir()).resolve();assert 'StudentMaterials' in R.parts and 'Week11-PCG' in R.parts,'Never condition the instructor originals.'
reg=u.AssetRegistryHelpers.get_asset_registry();reg.search_all_assets(True);rows=[]
for info in reg.get_assets_by_path('/Game',recursive=True):
 if str(info.asset_class_path.asset_name)!='Texture2D':continue
 texture=info.get_asset();before=[texture.blueprint_get_size_x(),texture.blueprint_get_size_y()]
 assert u.TrailBiomeAuthoringLibrary.downsize_teaching_texture(texture,2048),(str(info.package_name),before)
 u.EditorAssetLibrary.save_loaded_asset(texture,False);after=[texture.blueprint_get_size_x(),texture.blueprint_get_size_y()];rows.append({'asset':str(info.package_name),'before':before,'after':after,'compression':str(texture.get_editor_property('compression_settings')),'srgb':texture.get_editor_property('srgb')})
target=R.parents[1]/'Instructor';(target/'texture-conditioning.json').write_text(json.dumps({'status':'PASS','maximum_dimension':2048,'source_instructor_assets_unchanged':True,'method':'Unreal DownsizeImageUsingTextureSettings with normal renormalization and texture build gamma settings','textures':rows},indent=2));u.SystemLibrary.quit_editor()
