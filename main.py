import os
import stat
import argparse
import logging
import pathlib
import shutil
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_argparse():
    """
    Sets up the argument parser for the file-permission-copier tool.
    """
    parser = argparse.ArgumentParser(description="Copies file permissions (owner, group, and mode only; ACLs are not copied) from a source file to a target file. Symbolic links are followed on both the source and the target. Exits 1 when nothing was copied or when any part (mode or ownership) failed; the success line prints only on a full copy.",
                                     epilog="Example Usage: python main.py source.txt target.txt")

    parser.add_argument("source", help="The source file whose permissions will be copied. A symlink source is followed to its target.")
    parser.add_argument("target", help="The target file that will receive the permissions. A symlink target is followed to the file it points at.")

    return parser

def copy_permissions(source_file, target_file):
    """
    Copies file permissions (owner, group, and mode only) from a source file to a target file.
    Symbolic links are followed on both the source and the target.
    Args:
        source_file (str): Path to the source file.
        target_file (str): Path to the target file.
    Returns:
        bool: True only on a full copy (ownership and mode), False otherwise.
    """
    try:
        # Validate input paths
        source_path = pathlib.Path(source_file)
        target_path = pathlib.Path(target_file)

        # exists() follows symlinks, so a broken symlink reports as not found
        # rather than as a link. That matches the stat below, which also
        # follows links on both sides, as the help text promises.
        if not source_path.exists():
            raise FileNotFoundError(f"Source file '{source_file}' not found.")

        if not target_path.exists():
            raise FileNotFoundError(f"Target file '{target_file}' not found.")
            
        # Get file statistics from source file (os.stat follows symlinks)
        source_stat = os.stat(source_file)

        # Both halves are always attempted, even when the first one fails. A
        # target can therefore end up half copied, new mode under old ownership
        # or the reverse, and the False return is the only record that the copy
        # is incomplete. The success line in main's terms prints only when both
        # halves landed.
        success = True

        # Copy ownership (UID and GID) first. A chown clears the setuid
        # and setgid bits, so ownership must run before the mode copy.
        try:
            os.chown(target_file, source_stat.st_uid, source_stat.st_gid)
            logging.info(f"Copied ownership from {source_file} to {target_file}.")
        except OSError as e:
            success = False
            logging.error(f"Failed to copy ownership: {e}.  This may be due to insufficient privileges.")

        # Copy file mode (permissions) last, so special bits survive.
        try:
            # The full st_mode goes to chmod, file type bits and all. Only the
            # permission and special bits take effect; the type bits are ignored,
            # so passing the whole value is simpler than masking it first.
            os.chmod(target_file, source_stat.st_mode)
            logging.info(f"Copied file mode from {source_file} to {target_file}.")
        except OSError as e:
            success = False
            logging.error(f"Failed to copy file mode: {e}")

        if success:
            logging.info(f"Successfully copied permissions from {source_file} to {target_file}.")
        else:
            logging.error(f"Permission copy from {source_file} to {target_file} was incomplete.")
        return success

    except FileNotFoundError as e:
        logging.error(e)
        return False
    except OSError as e:
        logging.error(f"Error copying permissions: {e}")
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return False


def main():
    """
    Main function to parse arguments and call the copy_permissions function.
    """
    parser = setup_argparse()
    args = parser.parse_args()

    source_file = args.source
    target_file = args.target

    # Call the core function
    if not copy_permissions(source_file, target_file):
        sys.exit(1)

if __name__ == "__main__":
    main()