"""
Deodex tool - Extract and convert .vdex files to .dex using vdexExtractor.

Reimplements the logic from vdexExtractor/tools/deodex/run.sh in Python
for cross-platform compatibility.
"""
import glob
import os
import platform
import shutil
import subprocess


def _get_vdex_extractor_bin():
    """Locate the vdexExtractor binary."""
    localdir = os.getcwd()
    system = platform.system()
    machine = platform.machine()

    # Check in bin/<OS>/<arch>/
    candidates = [
        os.path.join(localdir, "bin", system, machine, "vdexExtractor"),
        os.path.join(localdir, "bin", system, machine, "vdexExtractor.exe"),
        os.path.join(localdir, "vdexExtractor", "bin", "vdexExtractor"),
        os.path.join(localdir, "vdexExtractor", "bin", "vdexExtractor.exe"),
    ]

    for c in candidates:
        if os.path.isfile(c):
            return c

    # Check on PATH
    on_path = shutil.which("vdexExtractor")
    if on_path:
        return on_path

    return None


def _get_compact_dex_converter_bin():
    """Locate the compact_dex_converter binary."""
    localdir = os.getcwd()
    system = platform.system()
    machine = platform.machine()

    candidates = [
        os.path.join(localdir, "bin", system, machine, "compact_dex_converter"),
        os.path.join(localdir, "bin", system, machine, "compact_dex_converter.exe"),
    ]

    for c in candidates:
        if os.path.isfile(c):
            return c

    on_path = shutil.which("compact_dex_converter")
    if on_path:
        return on_path

    return None


def _run_cmd(cmd, log_func=None):
    """Run a command, streaming output to log_func if provided."""
    creationflags = 0
    if os.name != 'posix':
        creationflags = subprocess.CREATE_NO_WINDOW

    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        creationflags=creationflags
    )
    output_lines = []
    for line in iter(proc.stdout.readline, b""):
        try:
            text = line.decode("utf-8").rstrip()
        except UnicodeDecodeError:
            text = line.decode("latin-1", errors="replace").rstrip()
        output_lines.append(text)
        if log_func:
            log_func(text + "\n")
    proc.wait()
    return proc.returncode, output_lines


def find_vdex_files(input_dir):
    """Find all .vdex files in the given directory recursively."""
    results = []
    for root, dirs, files in os.walk(input_dir):
        for f in files:
            if f.lower().endswith('.vdex'):
                results.append(os.path.join(root, f))
    return sorted(results)


def deodex_files(vdex_files, output_dir, keep_tmp=False, log_func=None):
    """
    Deodex a list of .vdex file paths, writing .dex output to output_dir.

    Args:
        vdex_files: List of absolute paths to .vdex files
        output_dir: Directory to write deodexed .dex files
        keep_tmp: If True, keep intermediate decompiled files
        log_func: Callable(str) for logging output lines

    Returns:
        (success_count, error_count, messages)
    """
    if log_func is None:
        log_func = lambda x: None

    vdex_bin = _get_vdex_extractor_bin()
    if not vdex_bin:
        log_func("[ERROR] vdexExtractor binary not found.\n")
        log_func("Please place vdexExtractor in bin/<OS>/<arch>/ or on PATH.\n")
        return 0, 1, ["vdexExtractor binary not found"]

    if not vdex_files:
        log_func("No .vdex files to process.\n")
        return 0, 0, ["No .vdex files"]

    log_func(f"Processing {len(vdex_files)} .vdex file(s).\n")
    return _process_vdex_files(vdex_bin, vdex_files, output_dir, keep_tmp, log_func)


def deodex(input_dir, output_dir, keep_tmp=False, log_func=None):
    """
    Deodex .vdex files from input_dir, writing .dex output to output_dir.

    Args:
        input_dir: Directory containing .vdex files (searched recursively)
        output_dir: Directory to write deodexed .dex files
        keep_tmp: If True, keep intermediate decompiled files
        log_func: Callable(str) for logging output lines

    Returns:
        (success_count, error_count, messages)
    """
    if log_func is None:
        log_func = lambda x: None

    vdex_bin = _get_vdex_extractor_bin()
    if not vdex_bin:
        log_func("[ERROR] vdexExtractor binary not found.\n")
        log_func("Please place vdexExtractor in bin/<OS>/<arch>/ or on PATH.\n")
        return 0, 1, ["vdexExtractor binary not found"]

    vdex_files = find_vdex_files(input_dir)
    if not vdex_files:
        log_func("No .vdex files found in input directory.\n")
        return 0, 0, ["No .vdex files found"]

    log_func(f"Found {len(vdex_files)} .vdex file(s) to process.\n")
    return _process_vdex_files(vdex_bin, vdex_files, output_dir, keep_tmp, log_func)


def _process_vdex_files(vdex_bin, vdex_files, output_dir, keep_tmp, log_func):
    """Shared processing logic for deodex() and deodex_files()."""
    decompiled_dir = os.path.join(output_dir, "vdexExtractor_decompiled")
    deodexed_dir = os.path.join(output_dir, "vdexExtractor_deodexed")
    os.makedirs(decompiled_dir, exist_ok=True)
    os.makedirs(deodexed_dir, exist_ok=True)

    success_count = 0
    error_count = 0

    for vdex_file in vdex_files:
        bin_name = os.path.splitext(os.path.basename(vdex_file))[0]
        log_func(f"\nProcessing: {bin_name}.vdex\n")

        out_dec_base = os.path.join(decompiled_dir, bin_name)
        out_dec = os.path.join(out_dec_base, "decompiled")
        os.makedirs(out_dec, exist_ok=True)

        out_deodex_base = os.path.join(deodexed_dir, bin_name)
        os.makedirs(out_deodex_base, exist_ok=True)

        # Run vdexExtractor
        cmd = [vdex_bin, "-i", vdex_file, "-o", out_dec, "--ignore-crc-error"]
        ret, _ = _run_cmd(cmd, log_func)
        if ret != 0:
            log_func(f"[ERROR] vdexExtractor failed for {bin_name}.vdex\n")
            error_count += 1
            continue

        # Check for .dex files
        dex_files = glob.glob(os.path.join(out_dec, "*.dex"))
        cdex_files = glob.glob(os.path.join(out_dec, "*.cdex"))

        if dex_files:
            # Standard Dex - copy as-is
            for df in dex_files:
                shutil.copy2(df, out_deodex_base)
            log_func(f"  Extracted {len(dex_files)} .dex file(s) (standard)\n")
            success_count += 1

        elif cdex_files:
            # CompactDex - need conversion
            cdex_converter = _get_compact_dex_converter_bin()
            if not cdex_converter:
                log_func(f"  [WARN] CompactDex files found but compact_dex_converter not available.\n")
                log_func(f"  Copying .cdex files as-is. Use compact_dex_converter to convert them.\n")
                for cf in cdex_files:
                    shutil.copy2(cf, out_deodex_base)
                success_count += 1
            else:
                # Get API level
                api_cmd = [vdex_bin, "--get-api", "-i", vdex_file]
                api_ret, api_out = _run_cmd(api_cmd)
                api_level = ""
                for line in api_out:
                    if "API-" in line:
                        api_level = line.strip()
                        break

                log_func(f"  CompactDex detected ({api_level}), converting...\n")

                # Convert
                conv_cmd = [cdex_converter, "-w", out_deodex_base] + cdex_files
                conv_ret, _ = _run_cmd(conv_cmd, log_func)
                if conv_ret != 0:
                    log_func(f"  [ERROR] CompactDex conversion failed for {bin_name}\n")
                    error_count += 1
                    continue

                # Rename .cdex to .dex
                for f in os.listdir(out_deodex_base):
                    if f.endswith('.cdex'):
                        old = os.path.join(out_deodex_base, f)
                        new = os.path.join(out_deodex_base, f.rsplit('.cdex', 1)[0] + '.dex')
                        os.rename(old, new)

                log_func(f"  Converted {len(cdex_files)} CompactDex file(s)\n")
                success_count += 1
        else:
            log_func(f"  [WARN] No .dex or .cdex files produced for {bin_name}\n")
            # Clean empty dir
            if not os.listdir(out_deodex_base):
                os.rmdir(out_deodex_base)
            error_count += 1

    # Cleanup
    if not keep_tmp and os.path.isdir(decompiled_dir):
        shutil.rmtree(decompiled_dir, ignore_errors=True)

    log_func(f"\nDeodex complete: {success_count} succeeded, {error_count} failed.\n")
    log_func(f"Output: {deodexed_dir}\n")

    return success_count, error_count, []
