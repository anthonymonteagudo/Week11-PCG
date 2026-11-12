"""Editor-only museum navigation. All content and PCG nodes are native assets."""
import unreal as u,time
_ready_handle=None
_requested_station=1
MAP='/Game/Trail/Museum/Maps/PCG_Museum'
TITLES=['Create points','Vary transforms','Subtract a closed spline','Project and filter slope','Reuse a graph with asset sets','Prune nearby points','Assemble a modular building (optional)']
def _actors():return list(u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors())
def _ensure_map():
 world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
 if not world or world.get_name()!='PCG_Museum':
  # Never discard unsaved work when navigating from another map.
  if not u.EditorLoadingAndSavingUtils.save_dirty_packages_with_dialog(True,True):return False
  loaded=u.get_editor_subsystem(u.LevelEditorSubsystem).load_level(MAP)
  if loaded:ensure_ready()
  return loaded
 return True
def show_all():
 global _requested_station
 _requested_station=0
 if not _ensure_map():return
 for a in _actors():
  if a.get_actor_label().startswith('M') and a.get_actor_label()[1:3].isdigit():a.set_is_temporarily_hidden_in_editor(False);a.set_actor_hidden_in_game(False)
 u.log('PCG_MUSEUM_ALL_STATIONS')
def focus(number):
 global _requested_station
 assert 1<=number<=7
 _requested_station=number
 if not _ensure_map():return
 prefix='M%02d_'%number;cam=None;selection=[]
 for a in _actors():
  label=a.get_actor_label()
  if len(label)>=4 and label[0]=='M' and label[1:3].isdigit() and label[3]=='_':
   hide=not label.startswith(prefix);a.set_is_temporarily_hidden_in_editor(hide);a.set_actor_hidden_in_game(hide)
   if label==prefix+'Camera':cam=a
   if label.startswith(prefix+'PCG'):selection.append(a)
 if cam:u.get_editor_subsystem(u.UnrealEditorSubsystem).set_level_viewport_camera_info(cam.get_actor_location(),cam.get_actor_rotation())
 if selection:u.get_editor_subsystem(u.EditorActorSubsystem).set_selected_level_actors(selection)
 u.log('PCG_MUSEUM_STATION '+str(number)+' '+TITLES[number-1])
def ensure_ready():
 """Generate absent editor outputs automatically after the map has loaded."""
 global _ready_handle
 if _ready_handle:u.unregister_slate_post_tick_callback(_ready_handle)
 started=time.monotonic()
 def ready(dt):
  global _ready_handle
  if time.monotonic()-started<3:return
  world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
  if not world or not world.get_path_name().startswith('/Game/Trail/'):
   if time.monotonic()-started<30:return
  else:
   for a in _actors():
    c=a.get_component_by_class(u.PCGComponent)
    if c and not c.get_editor_property('generation_in_progress'):c.generate_local(False)
   if world.get_name()=='PCG_Museum':
    if _requested_station:focus(_requested_station)
    else:show_all()
  u.unregister_slate_post_tick_callback(_ready_handle);_ready_handle=None
 _ready_handle=u.register_slate_post_tick_callback(ready)
def generate(number):
 if not _ensure_map():return
 for a in _actors():
  if a.get_actor_label().startswith('M%02d_PCG'%number):
   c=a.get_component_by_class(u.PCGComponent)
   if c:c.generate_local(True)
def open_example(kind):
 maps={'trail':'/Game/Trail/Maps/Trail_Student','forest':'/Game/Trail/Maps/Biome_Forest','snow':'/Game/Trail/Maps/Biome_Snow','building':'/Game/Trail/Building/Maps/Building_Examples'}
 if not u.EditorLoadingAndSavingUtils.save_dirty_packages_with_dialog(True,True):return
 if u.get_editor_subsystem(u.LevelEditorSubsystem).load_level(maps[kind]):ensure_ready()
def open_graph():
 for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_selected_level_actors():
  c=a.get_component_by_class(u.PCGComponent)
  if not c:continue
  g=c.graph_instance
  while isinstance(g,u.PCGGraphInstance):g=g.get_editor_property('graph')
  u.get_editor_subsystem(u.AssetEditorSubsystem).open_editor_for_assets([g]);return
 u.log_warning('Select a station PCG actor first, then choose Open selected station graph. The numbered museum menu selects the correct actor for you.')
def register_menu():
 menus=u.ToolMenus.get();tools=menus.extend_menu('LevelEditor.MainMenu.Tools');name='LevelEditor.MainMenu.Tools.Week11PCGMuseum'
 menu=menus.find_menu(name)
 if not menu:menu=tools.add_sub_menu('Week11PCG','Week11PCG','Week11PCGMuseum','Week 11 PCG Museum')
 for k,title in enumerate(TITLES,1):
  entry=u.ToolMenuEntry(name='Week11Station%02d'%k,type=u.MultiBlockType.MENU_ENTRY);entry.set_label('%02d  %s'%(k,title));entry.set_string_command(u.ToolMenuStringCommandType.PYTHON,'','import museum; museum.focus(%d)'%k);menu.add_menu_entry('Stations',entry)
 entry=u.ToolMenuEntry(name='Week11ShowAll',type=u.MultiBlockType.MENU_ENTRY);entry.set_label('Show all stations');entry.set_string_command(u.ToolMenuStringCommandType.PYTHON,'','import museum; museum.show_all()');menu.add_menu_entry('Navigation',entry);menus.refresh_all_widgets()
 for key,label,command in [('OpenGraph','Open selected station graph','museum.open_graph()'),('Trail','Full trail exercise',"museum.open_example('trail')"),('Forest','Forest region',"museum.open_example('forest')"),('Snow','Snow region',"museum.open_example('snow')"),('Building','Building examples',"museum.open_example('building')")]:
  entry=u.ToolMenuEntry(name='Week11'+key,type=u.MultiBlockType.MENU_ENTRY);entry.set_label(label);entry.set_string_command(u.ToolMenuStringCommandType.PYTHON,'','import museum; '+command);menu.add_menu_entry('Navigation',entry)
 menus.refresh_all_widgets()
 levels=u.get_editor_subsystem(u.LevelEditorSubsystem);levels.on_map_opened.remove_callable(_map_opened);levels.on_map_opened.add_callable(_map_opened)
def _map_opened(filename,as_template):ensure_ready()
