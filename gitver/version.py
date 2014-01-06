import _version as rel

# get the release by default
gitver_version = rel.gitver_version
gitver_buildid = rel.gitver_buildid
gitver_pypi = rel.gitver_pypi

try:
    # if dev is present, that's the most recent build
    import _version_next as next
    gitver_version = next.gitver_version
    gitver_buildid = next.gitver_buildid
    gitver_pypi = next.gitver_pypi
except ImportError:
    pass
