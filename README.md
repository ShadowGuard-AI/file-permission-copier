![Banner](banner.png)

# file-permission-copier
Copies file permissions (owner, group, and mode only) from a source file to a target file. ACLs are not copied. Prevents permission drift during deployment or transfer. Uses 'os' and 'stat' modules. - Focused on File operations and analysis

Only mode and ownership (owner and group) are copied. ACLs are not copied.

Symbolic links are followed on both the source and the target: a symlink source contributes the permissions of the file it points at, and a symlink target passes the change through to the file it points at, which may be a file not named on the command line.

Ownership is applied first and mode last, so setuid, setgid, and sticky bits from the source are kept on the target.

Exit status: 0 only on a full copy of ownership and mode. If nothing was copied, or if any part (mode or ownership) failed, the run exits 1 and no full success line is printed.

## Install
`git clone https://github.com/ShadowStrikeHQ/file-permission-copier`

## Usage
`python3 main.py source target`

## Parameters
- `source`: The source file whose permissions will be copied (positional, required). Links are followed.
- `target`: The target file that will receive the permissions (positional, required). Links are followed.
- `-h`: Show help message and exit

## License
Copyright (c) ShadowStrikeHQ
