import json
import os
import threading
from dune_weaver_flask.modules.core import pattern_manager

# Global state
PLAYLISTS_FILE = os.path.join(os.getcwd(), "playlists.json")

# Ensure the file exists and contains at least an empty JSON object
if not os.path.exists(PLAYLISTS_FILE):
    with open(PLAYLISTS_FILE, "w") as f:
        json.dump({}, f, indent=2)

def load_playlists():
    """Load the entire playlists dictionary from the JSON file."""
    with open(PLAYLISTS_FILE, "r") as f:
        return json.load(f)

def save_playlists(playlists_dict):
    """Save the entire playlists dictionary back to the JSON file."""
    with open(PLAYLISTS_FILE, "w") as f:
        json.dump(playlists_dict, f, indent=2)

def list_all_playlists():
    """Returns a list of all playlist names."""
    playlists_dict = load_playlists()
    return list(playlists_dict.keys())

def get_playlist(playlist_name):
    """Get a specific playlist by name."""
    playlists_dict = load_playlists()
    if playlist_name not in playlists_dict:
        return None
    return {
        "name": playlist_name,
        "files": playlists_dict[playlist_name]
    }

def create_playlist(playlist_name, files):
    """Create or update a playlist."""
    playlists_dict = load_playlists()
    playlists_dict[playlist_name] = files
    save_playlists(playlists_dict)
    return True

def modify_playlist(playlist_name, files):
    """Modify an existing playlist."""
    return create_playlist(playlist_name, files)

def delete_playlist(playlist_name):
    """Delete a playlist."""
    playlists_dict = load_playlists()
    if playlist_name not in playlists_dict:
        return False
    del playlists_dict[playlist_name]
    save_playlists(playlists_dict)
    return True

def add_to_playlist(playlist_name, pattern):
    """Add a pattern to an existing playlist."""
    playlists_dict = load_playlists()
    if playlist_name not in playlists_dict:
        return False
    playlists_dict[playlist_name].append(pattern)
    save_playlists(playlists_dict)
    return True

def run_playlist(playlist_name, pause_time=0, clear_pattern=None, run_mode="single", shuffle=False, schedule_hours=None):
    """Run a playlist with the given options."""
    playlists = load_playlists()
    if playlist_name not in playlists:
        return False, "Playlist not found"

    file_paths = playlists[playlist_name]
    file_paths = [os.path.join(pattern_manager.THETA_RHO_DIR, file) for file in file_paths]

    if not file_paths:
        return False, "Playlist is empty"

    try:
        threading.Thread(
            target=pattern_manager.run_theta_rho_files,
            args=(file_paths,),
            kwargs={
                'pause_time': pause_time,
                'clear_pattern': clear_pattern,
                'run_mode': run_mode,
                'shuffle': shuffle,
                'schedule_hours': schedule_hours
            },
            daemon=True
        ).start()
        return True, f"Playlist '{playlist_name}' is now running."
    except Exception as e:
        return False, str(e)
