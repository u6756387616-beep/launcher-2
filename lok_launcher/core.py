from pathlib import Path
import minecraft_launcher_lib as mll

LOADERS = ("Vanilla", "Fabric", "Forge", "NeoForge", "Quilt")

def list_versions():
    # Oficjalny manifest Mojang: release + snapshot + stare wersje.
    return mll.utils.get_version_list()

def installed_versions(game_dir):
    return mll.utils.get_installed_versions(str(game_dir))

def install_version(version_id, loader_name, game_dir, loader_version="", callback=None):
    game_dir = str(Path(game_dir))
    if loader_name == "Vanilla":
        return mll.install.install_minecraft_version(version_id, game_dir, callback=callback)
    loader = mll.mod_loader.get_mod_loader(loader_name.lower())
    if not loader.is_minecraft_version_supported(version_id):
        raise ValueError(f"{loader_name} nie obsługuje Minecrafta {version_id}.")
    if loader_version.strip():
        return loader.install(version_id, game_dir, loader_version=loader_version.strip(), callback=callback)
    return loader.install(version_id, game_dir, callback=callback)

def build_launch_command(version_id, game_dir, account):
    """Przyjmuje wyłącznie dane legalnego profilu Microsoft."""
    required = ("name", "id", "access_token")
    if not all(account.get(k) for k in required):
        raise RuntimeError("Brak zalogowanego konta Microsoft. Moduł OAuth zostanie dodany w kolejnym etapie.")
    options = {
        "username": account["name"],
        "uuid": account["id"],
        "token": account["access_token"],
    }
    return mll.command.get_minecraft_command(version_id, str(game_dir), options)
