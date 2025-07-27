import winreg
import os
from pathlib import Path

def get_installed_programs_from_registry():
    """
    Get installed programs from Windows registry.
    """
    programs = []
    
    # Registry paths where installed programs are listed
    registry_paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
    ]
    
    for hkey, subkey_path in registry_paths:
        try:
            with winreg.OpenKey(hkey, subkey_path) as key:
                for i in range(winreg.QueryInfoKey(key)[0]):  # Number of subkeys
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, subkey_name) as subkey:
                            program_info = extract_program_info(subkey)
                            if program_info:
                                programs.append(program_info)
                    except (OSError, PermissionError):
                        continue
        except (OSError, PermissionError):
            continue
    
    return programs

def extract_program_info(registry_key):
    """
    Extract program information from a registry key.
    """
    try:
        # Get display name
        display_name, _ = winreg.QueryValueEx(registry_key, "DisplayName")
        
        # Get install location
        install_location = None
        try:
            install_location, _ = winreg.QueryValueEx(registry_key, "InstallLocation")
        except FileNotFoundError:
            try:
                # Try alternative location fields
                install_location, _ = winreg.QueryValueEx(registry_key, "UninstallString")
                if install_location:
                    # Extract directory from uninstall string
                    install_location = os.path.dirname(install_location.strip('"'))
            except FileNotFoundError:
                pass
        
        # Get publisher
        publisher = None
        try:
            publisher, _ = winreg.QueryValueEx(registry_key, "Publisher")
        except FileNotFoundError:
            pass
        
        return {
            'name': display_name,
            'install_location': install_location,
            'publisher': publisher
        }
    
    except FileNotFoundError:
        # Skip entries without display name
        return None

def get_steam_games():
    """
    Get Steam games from registry.
    """
    steam_games = []
    
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam") as steam_key:
            try:
                install_path, _ = winreg.QueryValueEx(steam_key, "InstallPath")
                
                # Look for Steam apps in registry
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam\Apps") as apps_key:
                        for i in range(winreg.QueryInfoKey(apps_key)[0]):
                            try:
                                app_id = winreg.EnumKey(apps_key, i)
                                with winreg.OpenKey(apps_key, app_id) as app_key:
                                    try:
                                        name, _ = winreg.QueryValueEx(app_key, "Name")
                                        installed, _ = winreg.QueryValueEx(app_key, "Installed")
                                        
                                        if installed == 1:
                                            steam_games.append({
                                                'name': name,
                                                'install_location': install_path,
                                                'publisher': 'Steam',
                                                'app_id': app_id
                                            })
                                    except FileNotFoundError:
                                        continue
                            except (OSError, PermissionError):
                                continue
                except FileNotFoundError:
                    pass
            except FileNotFoundError:
                pass
    except FileNotFoundError:
        pass
    
    return steam_games

def is_likely_game(program):
    """
    Determine if a program is likely a game based on various criteria.
    """
    if not program['name']:
        return False
    
    name_lower = program['name'].lower()
    publisher_lower = (program['publisher'] or '').lower()
    
    # Game publishers and platforms
    game_publishers = [
        'steam', 'valve', 'epic games', 'electronic arts', 'ea', 'ubisoft',
        'activision', 'blizzard', 'bethesda', 'cd projekt', 'rockstar',
        'square enix', 'capcom', 'konami', 'sega', 'nintendo', 'sony',
        'microsoft studios', 'xbox game studios', 'riot games', 'epic',
        'gog', 'origin', 'battle.net'
    ]
    
    # Game-related keywords
    game_keywords = [
        'game', 'games', 'simulator', 'racing', 'adventure', 'rpg',
        'strategy', 'action', 'shooter', 'warfare', 'battle', 'combat',
        'quest', 'fantasy', 'online', 'multiplayer', 'edition'
    ]
    
    # Non-game keywords (to exclude)
    non_game_keywords = [
        'microsoft', 'adobe', 'driver', 'update', 'runtime', 'framework',
        'redistributable', 'tool', 'utility', 'browser', 'antivirus',
        'office', 'visual studio', 'windows'
    ]
    
    # Check publisher
    for publisher in game_publishers:
        if publisher in publisher_lower:
            return True
    
    # Check for non-game keywords first
    for keyword in non_game_keywords:
        if keyword in name_lower:
            return False
    
    # Check for game keywords
    for keyword in game_keywords:
        if keyword in name_lower:
            return True
    
    return False

def filter_games_on_d_drive(programs):
    """
    Filter programs that are installed on D: drive.
    """
    d_drive_games = []
    
    for program in programs:
        if program['install_location']:
            install_path = Path(program['install_location'])
            # Check if the program is installed on D: drive
            if str(install_path).upper().startswith('D:'):
                d_drive_games.append(program)
    
    return d_drive_games

def find_game_executables(install_location):
    """
    Find game executables in the installation directory.
    """
    if not install_location or not os.path.exists(install_location):
        return []
    
    executables = []
    install_path = Path(install_location)
    
    try:
        # Look for .exe files in the main directory and subdirectories (limited depth)
        for exe_file in install_path.rglob("*.exe"):
            if exe_file.is_file():
                # Skip obvious non-game executables
                exe_name = exe_file.name.lower()
                skip_files = ['unins', 'setup', 'install', 'update', 'redist', 'crash']
                
                if not any(skip in exe_name for skip in skip_files):
                    executables.append(str(exe_file))
                    
                    # Don't go too deep - limit to reasonable number of executables
                    if len(executables) >= 5:
                        break
    except (PermissionError, OSError):
        pass
    
    return executables

def main():
    """
    Main function to find and display games on D: drive using registry.
    """
    print("Game Detector - Finding games on D: drive using Windows Registry\n")
    print("=" * 70)
    
    print("Scanning Windows Registry for installed programs...")
    
    # Get all installed programs
    all_programs = get_installed_programs_from_registry()
    
    # Get Steam games separately
    steam_games = get_steam_games()
    print(f"Found {len(steam_games)} Steam games in registry.\n{steam_games}")
    all_programs.extend(steam_games)
    
    print(f"Found {len(all_programs)} total installed programs.")
    
    # Filter for likely games
    likely_games = [program for program in all_programs if is_likely_game(program)]
    print(f"Identified {len(likely_games)} potential games.")
    
    # Filter for games on D: drive
    d_drive_games = filter_games_on_d_drive(likely_games)
    
    if not d_drive_games:
        print("\nNo games found on D: drive.")
        return
    
    print(f"\nFound {len(d_drive_games)} games on D: drive:\n")
    
    for i, game in enumerate(d_drive_games, 1):
        print(f"{i:2d}. {game['name']}")
        if game['publisher']:
            print(f"    Publisher: {game['publisher']}")
        print(f"    Install Location: {game['install_location']}")
        
        # Try to find game executables
        executables = find_game_executables(game['install_location'])
        if executables:
            print(f"    Executables found:")
            for exe in executables[:3]:  # Show up to 3 executables
                print(f"      - {exe}")
            if len(executables) > 3:
                print(f"      ... and {len(executables) - 3} more")
        
        print()
    
    print("=" * 70)
    print(f"Registry scan complete! Found {len(d_drive_games)} games on D: drive.")

if __name__ == "__main__":
    main()