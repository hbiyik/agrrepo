import os
import subprocess
import requests
import re
import urllib3

REPOPATH = os.path.join(os.environ["GITHUB_WORKSPACE"], os.environ["REPOPATH"])
OWNER, REPO = os.environ["REPOSITORY"].split("/")
TAG = os.environ["TAG"]
TOKEN = os.environ["TOKEN"]
REPONAME = os.environ["REPONAME"]
# TO-DO: parse this from makepkg.conf
PKGEXT = os.environ["PKGEXT"]

SERVER = "github.com"
APIVER = "2022-11-28"

urllib3.disable_warnings()
PKG_FILTERCHARS = {":": "."}


def runprocess(*args, **kwargs):
    proc = subprocess.Popen(args, **kwargs)
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
    nextp = None
    for substr in resp.headers.get("link", "").split(","):
        nextp = re.search(r'<(.+?)>; rel="next"', substr)
        if nextp:
            nextp = nextp.group(1)
            break
    if not resp.status_code >= 200 or not resp.status_code < 300:
        raise RuntimeError(f"{resp.status_code}:{u}:{resp.content}")
    ret = resp.json() if method not in ["DELETE"] else resp
    return nextp, ret


RELID = querygithub("GET", f"releases/tags/{TAG}")[1]["id"]


def iterassets():
    cache = []
    nextp = f"releases/{RELID}/assets"
    while nextp:
        nextp, assets = querygithub("GET", nextp)
        for asset in assets:
            if asset["name"] not in cache:
                yield asset
                cache.append(asset["name"])


def delasset(assetid):
    return querygithub("DELETE", f"releases/assets/{assetid}", json=None)[1]


def uploadasset(name, path):
    # using curl here due to Python bug: https://github.com/python/cpython/issues/115627
    runprocess("curl", "-L", "-s", "-X" "POST", "-o", "/dev/null",
               "-H", "Accept: application/vnd.github+json",
               "-H", f"Authorization: Bearer {TOKEN}",
               "-H", f"X-GitHub-Api-Version: {APIVER}",
               "-H", "Content-Type: application/octet-stream",
               f"https://uploads.{SERVER}/repos/{OWNER}/{REPO}/releases/{RELID}/assets?name={name}",
               "--data-binary", f"@{path}", cwd=REPOPATH)


def updaterelease(name, body, draft=False, prerelease=False):
    return querygithub("PATCH", f"releases/{RELID}", json={"name": name,
                                                           "body": body,
                                                           "draft": draft,
                                                           "prerelease": prerelease})[1]


def fnameparse(fname):
    fname = os.path.basename(fname)
    parts = fname.split("-")
    for c1, c2 in PKG_FILTERCHARS.items():
        fname = fname.replace(c1, c2)
    if len(parts) < 4:
        return None, None, None
    # pgname-[epoch:]pkgver-pkgrel-arch.ext
    pkgrel = parts[-2]
    if not pkgrel.isdigit():
        return None, None, None
    pkgrel = int(pkgrel)
    pkgver = parts[-3]
    pkgname = "-".join(parts[:-3])
    return pkgname, f"{pkgver}.{pkgrel}"


def isnewer(version1, version2):
    stdout = subprocess.check_output(['vercmp', str(version1), str(version2)])
    return int(stdout.strip()) > 0


def getlocalpackages():
    local_packages = {}
    for filename in os.listdir(REPOPATH):
        if ".pkg." in filename:
            pkgpath = os.path.join(REPOPATH, filename)
            if "-debug-" in filename:
                print(f"Removing debug package {pkgpath}")
                os.remove(pkgpath)
                continue
            pkgname, pkgversion = fnameparse(filename)
            pkgsize = os.stat(pkgpath).st_size
            if pkgname not in local_packages:
                local_packages[pkgname] = pkgversion, filename, pkgpath, pkgsize
            elif isnewer(pkgversion, local_packages[pkgname][0]):
                print(f"Deleting local file {local_packages[pkgname][1]} in favor of {filename} because {pkgversion} > {local_packages[pkgname][0]}")
                print(f"::notice::Package update: {pkgname}: {local_packages[pkgname][0]} -> {pkgversion}")
                os.remove(local_packages[pkgname][2])
                local_packages[pkgname] = pkgversion, filename, pkgpath, pkgsize
            else:
                print(f"Deleting local file {filename} in favor of {local_packages[pkgname][1]} because {local_packages[pkgname][0]} >= {pkgversion}")
                print(f"::notice::Package update: {pkgname}: {pkgversion} -> {local_packages[pkgname][0]}")
                os.remove(pkgpath)
    packages = {}
    for _pkgname, [pkgversion, filename, pkgpath, pkgsize] in local_packages.items():
        packages[filename] = pkgsize
    return packages


def genrepo(*args):
    print(f"Generating Repo {REPONAME}")
    runprocess("repo-add", "-R", f"{REPONAME}.db.{PKGEXT}", *args, cwd=REPOPATH)
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
        print(f"::notice:: Updated release: {localfile}")
        uploadasset(localfile, os.path.join(REPOPATH, localfile))
    print(f"Updating the release")
    updaterelease(TAG, "release")


if __name__ == "__main__":
    os.makedirs(REPOPATH, exist_ok=True)
    localfiles = getlocalpackages()
    dbfiles = genrepo(*list(localfiles))
    for f in dbfiles:
        localfiles[f] = -1  # force update db files
    syncassets(**localfiles)
