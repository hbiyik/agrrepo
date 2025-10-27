import os
import subprocess
import requests
import re
import urllib3
from packaging.version import Version

REPOPATH = os.path.join(os.environ["GITHUB_WORKSPACE"], os.environ["REPOPATH"])
OWNER, REPO = os.environ["REPOSITORY"].split("/")
TAG = os.environ["TAG"]
TOKEN = os.environ["TOKEN"]
REPONAME = os.environ["REPONAME"]
PKGEXT = os.environ["PKGEXT"]

SERVER = "github.com"
APIVER = "2022-11-28"

VERSION_SEPS = [":", "+", "_", "@"]
urllib3.disable_warnings()


def runprocess(*args, **kwargs):
    proc = subprocess.Popen(*args, **kwargs)
    proc.wait()
    if not proc.returncode == 0:
        cmd = " ".join(args)
        raise RuntimeError(f"{cmd} returned {proc.returncode}")


def querygithub(method, path, subdomain="api", data=None, json=True, headers=None):
    u = f"https://{subdomain}.{SERVER}/repos/{OWNER}/{REPO}/{path}" if not path.startswith("https://") else path
    h = {"Accept": "application/vnd.github+json",
         "Authorization": f"Bearer {TOKEN}",
         "X-GitHub-Api-Version": APIVER}
    if headers:
        for k, v in headers.items():
            h[k] = v
    resp = requests.request(method, u, headers=h, data=data, json=json)
    next = None
    for substr in resp.headers.get("link", "").split(","):
        next = re.search(r'<(.+?)>; rel="next"', substr)
        if next:
            next = next.group(1)
            break
    if not resp.status_code >= 200 or not resp.status_code < 300:
        raise RuntimeError(f"{resp.status_code}:{u}:{resp.content}")
    ret = resp.json() if method not in ["DELETE"] else resp
    return next, ret


RELID = querygithub("GET", f"releases/tags/{TAG}")[1]["id"]


def iterassets():
    cache = []
    next = f"releases/{RELID}/assets"
    while next:
        next, assets = querygithub("GET", next)
        for asset in assets:
            if asset["name"] not in cache:
                yield asset
                cache.append(asset["name"])


def delasset(assetid):
    return querygithub("DELETE",  f"releases/assets/{assetid}", json=None)[1]


def uploadasset(name, path):
    # using curl here due to Python bug: https://github.com/python/cpython/issues/115627
    runprocess(["curl", "-L", "-s", "-X" "POST", "-o", "/dev/null",
                "-H", "Accept: application/vnd.github+json",
                "-H", f"Authorization: Bearer {TOKEN}",
                "-H", f"X-GitHub-Api-Version: {APIVER}",
                "-H", "Content-Type: application/octet-stream",
                f"https://uploads.{SERVER}/repos/{OWNER}/{REPO}/releases/{RELID}/assets?name={name}",
                "--data-binary", f"@{path}"], cwd=REPOPATH)


def updaterelease(name, body, draft=False, prerelease=False):
    return querygithub("PATCH", f"releases/{RELID}", json={"name": name,
                                                           "body": body,
                                                           "draft": draft,
                                                           "prerelease": prerelease})[1]


def getlocalpackages():
    local_packages = {}
    for found_filename in os.listdir(REPOPATH):
        if ".pkg." in found_filename:
            found_pkgpath = os.path.join(REPOPATH, found_filename)
            filename = found_filename.replace(":", ".")
            pkgpath = os.path.join(REPOPATH, filename)
            if not found_pkgpath == pkgpath:
                print(f"Renaming {found_pkgpath} -> {pkgpath}")
                os.replace(found_pkgpath, pkgpath)
            if "-debug-" in filename:
                print(f"Removing debug package {pkgpath}")
                os.remove(pkgpath)
                continue
            prename, _pkgext = filename.split(".pkg.")
            splits = prename.split("-")
            _arch = splits.pop(-1)
            pkgrel = splits.pop(-1)
            pkgver = splits.pop(-1)
            pkgname = "-".join(splits)
            pkgsize = os.stat(pkgpath).st_size
            # make version compatible with packaging
            versions = [pkgver, pkgrel]
            for i in range(len(versions)):
                for c in VERSION_SEPS:
                    versions[i] = versions[i].replace(c, ".")
                versions[i] = Version(''.join(c if c.isdigit() or c == "." else "0" for c in versions[i]))
            pkgver, pkgrel = versions
            if pkgname not in local_packages:
                local_packages[pkgname] = pkgver, pkgrel, filename, pkgpath, pkgsize
            elif local_packages[pkgname][0] > pkgver or (local_packages[pkgname][0] == pkgver and local_packages[pkgname][1] > pkgrel):
                print(f"Deleting local file {filename} in favor of {local_packages[pkgname][2]} because {local_packages[pkgname][0]}-{local_packages[pkgname][1]} >= {pkgver}-{pkgrel}")
                os.remove(pkgpath)
            else:
                print(f"Deleting local file {local_packages[pkgname][2]} in favor of {filename} because {pkgver}-{pkgrel} > {local_packages[pkgname][0]}-{local_packages[pkgname][1]}")
                os.remove(local_packages[pkgname][3])
                local_packages[pkgname] = pkgver, pkgrel, filename, pkgpath, pkgsize
    packages = {}
    for _pkgname, [pkgver, pkgrel, filename, pkgpath, pkgsize] in local_packages.items():
        packages[filename] = pkgsize
    return packages


def genrepo(*args):
    print(f"Generating Repo {REPONAME}")
    runprocess(["repo-add", "-R", f"{REPONAME}.db.{PKGEXT}", *args], cwd=REPOPATH)
    return [f"{REPONAME}.db",
            f"{REPONAME}.db.{PKGEXT}",
            f"{REPONAME}.files",
            f"{REPONAME}.files.{PKGEXT}"]


def syncassets(**localfiles):
    assets = list(iterassets())
    for asset in assets:
        if asset["name"] not in localfiles:
            print(f'Deleting remote asset {asset["name"]} with size {asset["size"]} because no such local file exists')
            delasset(asset["id"])
            continue
        if localfiles[asset["name"]] != asset["size"]:
            print(f'Replace remote asset {asset["name"]} with size {asset["size"]} with local file having size {localfiles[asset["name"]]}')
            delasset(asset["id"])
            uploadasset(asset["name"], os.path.join(REPOPATH, asset["name"]))
        else:
            print(f'Keep remote asset {asset["name"]} with size {asset["size"]} nothing changed')
        localfiles.pop(asset["name"])
    for localfile, localsize in localfiles.items():
        print(f"Uploading new asset {localfile} with size {localsize}")
        uploadasset(localfile, os.path.join(REPOPATH, localfile))
    print(f"Updating the release")
    updaterelease(TAG, "release")


if __name__ == "__main__":
    os.makedirs(REPOPATH, exist_ok=True)
    localfiles = getlocalpackages()
    dbfiles = genrepo(*list(localfiles))
    for f in dbfiles:
        localfiles[f] = -1 # force update db files
    syncassets(**localfiles)
