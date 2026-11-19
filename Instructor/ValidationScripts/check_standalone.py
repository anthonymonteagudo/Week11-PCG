"""Audit every packaged asset and dependency after removing cross-week paths."""
import unreal as u
import os, json, re, traceback
from pathlib import Path

root = Path(u.Paths.project_dir()).resolve()
output = Path(os.environ['WEEK11_VALIDATION_DIR'])
output.mkdir(parents=True, exist_ok=True)
try:
    registry = u.AssetRegistryHelpers.get_asset_registry()
    registry.search_all_assets(True)
    assets = registry.get_assets_by_path('/Game', recursive=True)
    options = u.AssetRegistryDependencyOptions(include_soft_package_references=True, include_hard_package_references=True)
    previous_week = re.compile(r'/Week(?:0?[1-9]|10)(?:/|$)', re.I)
    missing, stale, redirectors = [], [], []
    dependencies = set()
    for asset in assets:
        name = str(asset.package_name)
        if previous_week.search(name):
            stale.append(name)
        if str(asset.asset_class_path.asset_name) == 'ObjectRedirector':
            redirectors.append(name)
        if not u.load_asset(name):
            missing.append(name)
        for dependency in registry.get_dependencies(name, options):
            dep = str(dependency)
            dependencies.add(dep)
            if previous_week.search(dep):
                stale.append(dep)
            if dep.startswith('/Game/') and not u.EditorAssetLibrary.does_asset_exist(dep):
                missing.append(dep)
    assert not missing, ('Missing assets', missing)
    assert not stale, ('Previous-week paths', stale)
    assert not redirectors, ('Redirectors remain', redirectors)
    manifest = json.loads((root.parents[1] / 'Instructor/project-manifest.json').read_text(encoding='utf-8-sig'))
    reachable = set()
    pending = list(manifest['root_maps'])
    while pending:
        name = pending.pop()
        if name in reachable or not name.startswith('/Game/'):
            continue
        reachable.add(name)
        pending.extend(str(x) for x in registry.get_dependencies(name, options))
    unused = sorted(set(str(a.package_name) for a in assets) - reachable)
    assert not unused, ('Assets unrelated to the Week 11 maps', unused)
    surface_materials = {}
    for material_name, texture_folder in [('M_Ground_Forest', 'Mossy_Forest_Floor_vfylbge'), ('M_Ground_Snow', 'Melting_Snow_uepnbikfw')]:
        material = u.load_asset('/Game/Trail/Regions/Materials/' + material_name)
        textures = u.MaterialEditingLibrary.get_used_textures(material)
        paths = sorted(t.get_path_name() for t in textures)
        moved_textures = [p for p in paths if '/Game/Trail/Textures/Surfaces/' + texture_folder + '/' in p]
        assert len(moved_textures) == 2, (material_name, paths)
        surface_materials[material_name] = paths
    result = {'status': 'PASS', 'native_packages': len(assets), 'dependency_count': len(dependencies),
              'missing_assets': missing, 'previous_week_paths': stale, 'redirectors': redirectors,
              'unrelated_packages': unused, 'reachable_project_packages': len(reachable),
              'surface_material_textures': surface_materials,
              'engine': u.SystemLibrary.get_engine_version()}
except Exception:
    result = {'status': 'FAIL', 'error': traceback.format_exc()}
(output / 'standalone-audit.json').write_text(json.dumps(result, indent=2))
u.SystemLibrary.quit_editor()
