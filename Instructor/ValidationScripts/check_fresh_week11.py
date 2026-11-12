"""Observe a real cloned/extracted kit. Does not install or configure anything."""
import unreal as u
import os,json,time,traceback,hashlib
from pathlib import Path
R=Path(u.Paths.project_dir()).resolve()
assert (R.parents[1]/'README.md').exists()
O=Path(os.environ['WEEK11_VALIDATION_DIR']);O.mkdir(parents=True,exist_ok=True)
manifest=json.loads((R.parents[1]/'Instructor/project-manifest.json').read_text())
L=u.get_editor_subsystem(u.LevelEditorSubsystem);E=u.get_editor_subsystem(u.EditorActorSubsystem)
state={'index':0,'step':'startup','start':time.monotonic()};rows=[]
u.EditorPythonScripting.set_keep_python_script_alive(True)

def actors():return list(E.get_all_level_actors())
def outputs():
    out={}
    for a in actors():
        c=a.get_component_by_class(u.PCGComponent)
        if not c:continue
        if c.get_editor_property('generation_in_progress'):return None
        records=[]
        for ism in a.get_components_by_class(u.InstancedStaticMeshComponent):
            assert ism.static_mesh
            for k in range(ism.get_instance_count()):
                t=ism.get_instance_transform(k,True)
                records.append([ism.static_mesh.get_path_name(),
                    *[round(getattr(t.translation,d),4) for d in ['x','y','z']],
                    *[round(getattr(t.scale3d,d),4) for d in ['x','y','z']],
                    *[round(getattr(t.rotation,d),6) for d in ['x','y','z','w']]])
        if not records:return None
        out[a.get_actor_label()]={'count':len(records),'signature':hashlib.sha256(json.dumps(sorted(records)).encode()).hexdigest()}
    assert out,'No PCG actors'
    return out

def finish(error=None):
    state['step']='done'
    (O/'fresh-check.json').write_text(json.dumps({'status':'FAIL' if error else 'PASS','error':error,
        'engine':u.SystemLibrary.get_engine_version(),'startup':state.get('startup'),
        'manual_setup_performed':False,'custom_authoring_plugin_loaded':hasattr(u,'TrailBiomeAuthoringLibrary'),
        'maps':rows,'scope':'Fresh checkout on this Windows machine; UE is preinstalled. No second physical machine claim.'},indent=2))
    u.unregister_slate_post_tick_callback(handle);u.EditorPythonScripting.set_keep_python_script_alive(False)
    if not error and os.environ.get('WEEK11_THEN_CAPTURE'):
        script=Path(os.environ['WEEK11_THEN_CAPTURE'])
        exec(compile(script.read_text(encoding='utf8'),str(script),'exec'),{'__name__':'__main__'})
        return
    u.SystemLibrary.quit_editor()

def tick(dt):
    try:
        if state['step'] in ['done','loading']:return
        if state['step']=='startup':
            if time.monotonic()-state['start']<10:return
            world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
            assert world.get_name()=='PCG_Museum',world.get_path_name()
            assert not hasattr(u,'TrailBiomeAuthoringLibrary')
            menu=u.ToolMenus.get().find_menu('LevelEditor.MainMenu.Tools.Week11PCGMuseum');assert menu,'Museum menu missing'
            data=outputs()
            if data is None:
                assert time.monotonic()-state['start']<180,'Startup auto-generation failed'
                return
            counts=[sum(v['count'] for k,v in data.items() if k.startswith('M%02d_'%n)) for n in range(1,8)]
            assert counts==[12,12,6,6,8,31,36],counts
            # All referenced native content must resolve without source project paths.
            for file in manifest['files']:
                name='/Game/'+file['file'][8:].rsplit('.',1)[0]
                assert u.load_asset(name),('Missing bundled package',name)
            assert len(u.load_asset('/Game/Trail/Biome/PCG_BiomeScatter').nodes)==43
            assert len(u.load_asset('/Game/Trail/Building/PCG_ModularBuilding').nodes)==59
            import museum
            museum.focus(6)
            selected=E.get_selected_level_actors();assert selected and all(a.get_actor_label().startswith('M06_') for a in selected)
            museum.focus(1)
            state['startup']={'map':world.get_name(),'menu':'PASS','all_packages_loaded':len(manifest['files']),'station_counts':counts,'region_menu_navigation':[],'dirty_content_before_navigation':[p.get_name() for p in u.EditorLoadingAndSavingUtils.get_dirty_content_packages()],'dirty_maps_before_navigation':[p.get_name() for p in u.EditorLoadingAndSavingUtils.get_dirty_map_packages()]}
            museum.open_example('forest');state.update(step='menuforest',start=time.monotonic());return
        if state['step'] in ['menuforest','menusnow']:
            if time.monotonic()-state['start']<8:return
            expected='Biome_Forest' if state['step']=='menuforest' else 'Biome_Snow'
            world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world();assert world.get_name()==expected,world.get_name()
            data=outputs()
            if data is None:
                assert time.monotonic()-state['start']<180,'Region menu failed to generate'
                return
            state['startup']['region_menu_navigation'].append({'map':expected,'actors':len(data),'PASS':True})
            if state['step']=='menuforest':
                import museum
                museum.open_example('snow');state.update(step='menusnow',start=time.monotonic());return
            state.update(step='load');return
        if state['step']=='load':
            if state['index']==len(manifest['root_maps']):finish();return
            state['step']='loading';assert L.load_level(manifest['root_maps'][state['index']]);state.update(step='wait',start=time.monotonic());return
        if state['step']=='wait':
            if time.monotonic()-state['start']<8:return
            data=outputs()
            if data is None:
                assert time.monotonic()-state['start']<180,'Map auto-generation failed'
                return
            rows.append({'map':manifest['root_maps'][state['index']],'actors':data})
            (O/'progress.json').write_text(json.dumps(rows,indent=2))
            state.update(index=state['index']+1,step='load')
    except Exception:finish(traceback.format_exc())
handle=u.register_slate_post_tick_callback(tick)
