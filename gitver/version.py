import _version as rel

# get the release by default
gitver_version = rel.gitver_version
gitver_buildid = rel.gitver_buildid

try:
    # if dev is present, that's the most recent build
    import _version_next as next
    gitver_version = next.gitver_version
    gitver_buildid = next.gitver_buildid
except ImportError:
    pass
