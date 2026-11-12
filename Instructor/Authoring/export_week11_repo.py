"""Stage the current complete project in its dedicated PRIVATE weekly repository.
Use the real asset registry dependency closure, not filename guesses or whole source packs.
"""
import unreal as u,json,shutil,hashlib
from pathlib import Path
R=Path(u.Paths.project_dir());W=R.parent;repo=W/'StudentMaterials/Week11-PCG';target=repo/'Unreal/Week11PCGTrail';target.mkdir(parents=True,exist_ok=True);reg=u.AssetRegistryHelpers.get_asset_registry();reg.search_all_assets(True)
assert not (repo/'Instructor/texture-conditioning.json').exists(), 'The teaching copy already has reduced texture sources. Sync changed class assets selectively; a full re-export would restore the full-resolution art.'
roots=['/Game/Trail/Maps/'+n for n in ['Trail_Student','Biome_OpenDesert','Biome_JuniperScrub','Biome_RockyWash','Biome_Forest','Biome_Snow']]
roots += [str(x.package_name) for x in reg.get_assets_by_path('/Game/Trail/Variations/Maps',recursive=True) if str(x.asset_class_path.asset_name)=='World']
roots += ['/Game/Trail/Building/Maps/Building_Examples','/Game/Trail/Museum/Maps/PCG_Museum']
options=u.AssetRegistryDependencyOptions(include_soft_package_references=True,include_hard_package_references=True,include_searchable_names=False,include_soft_management_references=False,include_hard_management_references=False);seen=set();todo=list(roots)
while todo:
 name=todo.pop()
 if name in seen or not name.startswith('/Game/'):continue
 assert not name.startswith('/Game/Trail/Portable/'),'Rejected asset experiment reached a current map.'
 seen.add(name);todo.extend(str(x) for x in reg.get_dependencies(name,options))
files=[];missing=[]
for name in sorted(seen):
 rel=Path('Content')/name[6:];source=next((R/(str(rel)+ext) for ext in ['.uasset','.umap'] if (R/(str(rel)+ext)).exists()),None)
 if not source:missing.append(name);continue
 for f in [source]+[source.with_suffix(ext) for ext in ['.uexp','.ubulk'] if source.with_suffix(ext).exists()]:
  q=target/f.relative_to(R);q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,q);files.append({'file':f.relative_to(R).as_posix(),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
assert not missing,missing
assert all(x['bytes']<95*1024*1024 for x in files),'Use a release asset for a file exceeding normal Git limits.'
config=json.loads((R/'Week11PCGTrail.uproject').read_text());config['Plugins']=[p for p in config['Plugins'] if p['Name']!='TrailBiomeAuthoring'];(target/'Week11PCGTrail.uproject').write_text(json.dumps(config,indent=2))
(target/'Config').mkdir(exist_ok=True);engine=(R/'Config/DefaultEngine.ini').read_text().split('[/Script/AndroidFileServerEditor.')[0].replace('EditorStartupMap=/Game/Trail/Maps/Trail_Student','EditorStartupMap=/Game/Trail/Museum/Maps/PCG_Museum').replace('GameDefaultMap=/Game/Trail/Maps/Trail_Student','GameDefaultMap=/Game/Trail/Museum/Maps/PCG_Museum');(target/'Config/DefaultEngine.ini').write_text(engine)
for f in (R/'Content/Python').glob('*.py'):
 q=target/'Content/Python'/f.name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,q)
for name in ['Check_Student_Setup.py']:
 q=target/'Tools'/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/'Tools'/name,q)
for name in ['SKY_SOURCE.md','BUILDING_EXAMPLE.md']:
 shutil.copyfile(R/name,target/name)
instructor=repo/'Instructor';instructor.mkdir(exist_ok=True)
for name in ['build_building_example.py','build_pcg_museum.py','clean_pcg_layouts.py','polish_museum.py','rehearse_museum.py','rehearse_building.py','capture_buildings.py','probe_hda_engine.py','export_week11_repo.py']:
 q=instructor/'Authoring'/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/'Tools'/name,q)
plugin=R/'Plugins/TrailBiomeAuthoring'
for f in [plugin/'TrailBiomeAuthoring.uplugin']+list((plugin/'Source').rglob('*')):
 if f.is_file():q=instructor/'AuthoringPlugin'/f.relative_to(plugin);q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,q)
manifest={'status':'STAGED','engine':u.SystemLibrary.get_engine_version(),'private_repository_required':True,'root_maps':roots,'reachable_project_packages':len(seen),'files':files,'missing_packages':missing,'dependencies_bundled':True,'native_project_setup':'Open the .uproject in installed UE 5.7.4. Bundled Python registers the menu and generates absent editor outputs automatically.','not_included':['Unreal Engine installation','Houdini Engine optional installation and free license','Udemy archives/graphs/Blueprints','unrelated source pack content','rejected CC0 experiment','caches and credentials'],'source_content_attribution':'Original class graphs and teaching content; Fab/source assets retain their licenses. Source resources are documented separately.'};(instructor/'project-manifest.json').write_text(json.dumps(manifest,indent=2));(R/'Validation/MuseumPass/repo-stage.json').write_text(json.dumps({k:v for k,v in manifest.items() if k!='files'},indent=2));print('WEEK11_REPO_STAGED',len(seen),'packages',round(sum(f['bytes'] for f in files)/1048576,1),'MiB')
u.SystemLibrary.quit_editor()
