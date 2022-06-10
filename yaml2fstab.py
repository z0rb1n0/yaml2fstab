#!/usr/bin/python3 -uB


# Exercise for yaml-defined fstab source.

# Consumes a yaml file to generate a fstab file accordingly
# (The yaml schema is not documented but the default --meta-fstab is a good
# example)

# About root-reserve:
# I've always configured it/seen it configured at the FS superblock setting
# (with mk/tune2fs), never as a mount-time option, and couldn't find anything
# in the fstab/mount/ext4 documentation that would allow that.
# Is it an undocumented mount-time option or am I missing something?
# (I didn't scour the source code to deliver the test faster)


# I obviously cannot test the fstab unless I build a test stack for it


import sys, os, argparse, yaml


DEFAULT_META_FSTAB = "meta_fstab.yaml"


class MixedHelpFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawTextHelpFormatter):
    """ We need to preseve some formatting in the help string. Hence this """
    pass


def main():


    ap = argparse.ArgumentParser(
        description = "\n".join(map(str.strip, str("""

            Reads a meta-fstab yaml files and generates the fstab accordingly.

        """).split("\n"))),
        formatter_class = MixedHelpFormatter
    )

    ap.add_argument("--meta-fstab",
        dest = "meta_fstab",
        metavar = "PATH",
        type = str,
        required = False,
        default = DEFAULT_META_FSTAB,
        help = "The file containing the fstab-defining yaml"
    )

    ap.add_argument("--headers",
        dest = "headers",
        action = "store_true",
        required = False,
        default = argparse.SUPPRESS,
        help = """Print fstab comment line with headers"""
    )

    ap.add_argument("--debug",
        dest = "debug",
        action = "store_true",
        required = False,
        default = argparse.SUPPRESS,
        help = """Debug mode. Causes the resulting fstab lines to be """
            """preceded by the metadata from which they were generated"""
    )

    cmd_args = ap.parse_args()

    try:
        y_tree = yaml.safe_load(open(cmd_args.meta_fstab, "r"))
    except (
        FileNotFoundError,
        PermissionError,
        OSError,
        yaml.parser.ParserError
    ) as e_load:
        sys.stderr.write("Cannot open/load yaml file `%s`: %s(%s)\n" % (
            cmd_args.meta_fstab, e_load.__class__.__name__, e_load
        ))
        return 4

    # things are buffered up in a list
    fstab_lines = []


    if ("headers" in cmd_args):
        fstab_lines.append("#%-30s %-25s %-12s %-40s %-8s %-8s" % (
            "<file system>", "<mount point>", "<type>", "<options>", "<dump>", "<pass>"
        ))


    for m_dev, m_def in y_tree["fstab"].items():

        if ("debug" in cmd_args):
            fstab_lines.append("")
            fstab_lines.append("# from: %s %s" % (m_dev, m_def))

        # we use direct dictionary keys for required members,
        # get() defaulting to nothing for optionals
        m_p, fs_t, m_opts, nfs_export, root_reserve = (
            m_def["mount"],
            m_def["type"],
            m_def.get("options", {}),
            m_def.get("export", None),
            m_def.get("root-reserve", None)
        )


        fstab_lines.append("%-30s %-25s %-12s %-40s %-8d %-8d" % (
            m_dev +    ((":" + nfs_export) if nfs_export else ""),
            m_p,
            fs_t,
            ",".join(m_opts),
            0, # dump is here for padding
            (m_p != "/") # only / gets scanned earlier
        ))


    sys.stdout.write("\n".join(fstab_lines) + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
