"""
Create Windows desktop shortcut and taskbar pin for OpenCalc
"""
import os
import sys
from pathlib import Path

def create_ico_file():
    """Create a proper .ico file from the logo"""
    try:
        from PIL import Image, ImageDraw

        # Create multiple sizes for .ico
        sizes = [16, 32, 48, 64, 128, 256]
        images = []

        for size in sizes:
            # Create image
            img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            # Blue circle background
            margin = int(size * 0.05)
            draw.ellipse(
                [margin, margin, size - margin, size - margin],
                fill='#0ea5e9'
            )

            # Building silhouette (simplified for small sizes)
            center = size // 2

            if size >= 32:
                # Main building
                bw = int(size * 0.35)
                bh = int(size * 0.45)
                bx = center - bw // 2
                by = int(size * 0.35)
                draw.rectangle([bx, by, bx + bw, by + bh], fill='white')

                # Roof
                roof_points = [
                    (bx - int(size * 0.05), by),
                    (center, by - int(size * 0.15)),
                    (bx + bw + int(size * 0.05), by)
                ]
                draw.polygon(roof_points, fill='white')

                # Windows
                if size >= 48:
                    ww = int(size * 0.08)
                    wh = int(size * 0.1)
                    gap = int(size * 0.05)

                    # Row 1
                    for col in range(2):
                        wx = bx + int(size * 0.06) + col * (ww + gap)
                        wy = by + int(size * 0.06)
                        draw.rectangle([wx, wy, wx + ww, wy + wh], fill='#0ea5e9')

                    # Row 2
                    for col in range(2):
                        wx = bx + int(size * 0.06) + col * (ww + gap)
                        wy = by + int(size * 0.2)
                        draw.rectangle([wx, wy, wx + ww, wy + wh], fill='#0ea5e9')

                # Euro symbol
                if size >= 48:
                    euro_size = int(size * 0.2)
                    ex = center + int(size * 0.15)
                    ey = int(size * 0.65)

                    # Circle part of euro
                    draw.arc(
                        [ex, ey, ex + euro_size, ey + euro_size],
                        start=45, end=315,
                        fill='#fbbf24',
                        width=max(2, size // 20)
                    )
                    # Horizontal lines
                    draw.line(
                        [ex - 2, ey + euro_size // 3, ex + euro_size // 2, ey + euro_size // 3],
                        fill='#fbbf24',
                        width=max(1, size // 25)
                    )
                    draw.line(
                        [ex - 2, ey + euro_size * 2 // 3, ex + euro_size // 2, ey + euro_size * 2 // 3],
                        fill='#fbbf24',
                        width=max(1, size // 25)
                    )
            else:
                # Simplified for 16px - just a building shape
                draw.rectangle(
                    [int(size * 0.25), int(size * 0.35), int(size * 0.75), int(size * 0.85)],
                    fill='white'
                )

            images.append(img)

        # Save as .ico
        assets_dir = Path(__file__).parent / "assets"
        assets_dir.mkdir(exist_ok=True)
        ico_path = assets_dir / "opencalc.ico"

        # Save with all sizes
        images[0].save(
            ico_path,
            format='ICO',
            sizes=[(img.width, img.height) for img in images],
            append_images=images[1:]
        )

        print(f"ICO bestand gemaakt: {ico_path}")
        return str(ico_path)

    except ImportError:
        print("PIL/Pillow niet gevonden. Installeer met: pip install Pillow")
        return None

def create_windows_shortcut(ico_path: str = None):
    """Create a Windows desktop shortcut"""
    if sys.platform != 'win32':
        print("Deze functie werkt alleen op Windows")
        return False

    try:
        import winshell
        from win32com.client import Dispatch
    except ImportError:
        print("pywin32 en winshell niet gevonden.")
        print("Installeer met: pip install pywin32 winshell")

        # Alternative: create a .bat file as shortcut
        create_batch_launcher()
        return False

    # Paths
    desktop = winshell.desktop()
    python_exe = sys.executable
    script_dir = Path(__file__).parent
    main_py = script_dir / "main.py"

    # Create shortcut
    shortcut_path = Path(desktop) / "OpenCalc.lnk"

    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(str(shortcut_path))
    shortcut.TargetPath = python_exe
    shortcut.Arguments = f'"{main_py}"'
    shortcut.WorkingDirectory = str(script_dir)
    shortcut.Description = "OpenCalc - Open Source Kostenbegrotingsprogramma"

    if ico_path and Path(ico_path).exists():
        shortcut.IconLocation = ico_path

    shortcut.save()

    print(f"Snelkoppeling gemaakt op: {shortcut_path}")
    return True

def create_batch_launcher():
    """Create a batch file launcher as alternative"""
    script_dir = Path(__file__).parent
    bat_path = script_dir / "OpenCalc.bat"

    # Get the virtual environment python if available
    venv_python = script_dir / ".venv" / "Scripts" / "python.exe"
    if venv_python.exists():
        python_path = str(venv_python)
    else:
        python_path = "python"

    bat_content = f'''@echo off
cd /d "{script_dir}"
"{python_path}" main.py
pause
'''

    with open(bat_path, 'w') as f:
        f.write(bat_content)

    print(f"Batch launcher gemaakt: {bat_path}")
    print("Je kunt dit bestand naar je bureaublad kopieren als snelkoppeling.")

    # Also create a VBS launcher for no console window
    vbs_path = script_dir / "OpenCalc.vbs"
    vbs_content = f'''Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "{script_dir}"
WshShell.Run """{python_path}"" main.py", 0, False
'''

    with open(vbs_path, 'w') as f:
        f.write(vbs_content)

    print(f"VBS launcher (zonder console) gemaakt: {vbs_path}")

    return str(bat_path)

def create_start_menu_shortcut(ico_path: str = None):
    """Create a Start Menu shortcut"""
    if sys.platform != 'win32':
        return False

    try:
        import winshell
        from win32com.client import Dispatch

        # Start menu programs folder
        start_menu = Path(winshell.start_menu()) / "Programs"

        python_exe = sys.executable
        script_dir = Path(__file__).parent
        main_py = script_dir / "main.py"

        shortcut_path = start_menu / "OpenCalc.lnk"

        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(str(shortcut_path))
        shortcut.TargetPath = python_exe
        shortcut.Arguments = f'"{main_py}"'
        shortcut.WorkingDirectory = str(script_dir)
        shortcut.Description = "OpenCalc - Open Source Kostenbegrotingsprogramma"

        if ico_path and Path(ico_path).exists():
            shortcut.IconLocation = ico_path

        shortcut.save()

        print(f"Start Menu snelkoppeling gemaakt: {shortcut_path}")
        return True

    except ImportError:
        return False

def main():
    print("=" * 50)
    print("OpenCalc Shortcut Creator")
    print("=" * 50)
    print()

    # Create icon
    print("1. Icoon maken...")
    ico_path = create_ico_file()
    print()

    # Create desktop shortcut
    print("2. Bureaublad snelkoppeling maken...")
    create_windows_shortcut(ico_path)
    print()

    # Create start menu shortcut
    print("3. Start Menu snelkoppeling maken...")
    create_start_menu_shortcut(ico_path)
    print()

    print("=" * 50)
    print("Klaar!")
    print()
    print("Tips voor taskbar:")
    print("1. Start OpenCalc via de snelkoppeling")
    print("2. Klik met rechts op het icoon in de taakbalk")
    print("3. Kies 'Aan taakbalk vastmaken'")
    print("=" * 50)

if __name__ == "__main__":
    main()
