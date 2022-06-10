#!/usr/bin/python3 -uB


# Exercise for yaml-defined fstab source.
# The code is not defensive and there are no exception handlers,
# but the data source is static, so that shouldn't be a problem.

# The generated fstab block contains no headers, but they obviously are
#<file system> <mount point>   <type>  <options>       <dump>  <pass>

# About root-reserve:
# I've always configured it/seen it configured at the FS superblock setting
# (with mk/tune2fs), never as a mount-time option, and couldn't find anything
# in the fstab/mount/ext4 documentation that would allow that.
# Is it an undocumented mount-time option or am I missing something?
# (I didn't scour the source code to deliver the test faster)


# I obviously cannot test the fstab unless I build a test stack for it


import sys, os, yaml

META_FSTAB = "meta_fstab.yaml"
EMIT_METADATA = True


def main():

    y_tree = yaml.safe_load(open(META_FSTAB, "r"))
    
    # things are buffered up in a list
    fstab_lines = []
    
    for m_dev, m_def in y_tree["fstab"].items():

        if (EMIT_METADATA):
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
        
        
        fstab_lines.append("%-30s %-25s %-12s %-40s 0 %d" % (
            m_dev +    ((":" + nfs_export) if nfs_export else ""),
            m_p,
            fs_t,
            ",".join(m_opts),
            (m_p != "/") # only / gets scanned earlier
        ))


    sys.stdout.write("\n".join(fstab_lines) + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
