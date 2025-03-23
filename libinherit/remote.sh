inherit(){
	_url="$1"
	_pkgbuild="$_url/PKGBUILD"
	_basepath=$(dirname $BASH_SOURCE)
	
	# source the remote PKGBUILD
	eval "$(curl -s -L $_pkgbuild)"
	
	# sync the localfiles
	_skip_prefix=("http://" "https://" "ftp://" "file://" "scp://" "rsync://" "git+" "bzr+" "fossil+" "hg+" "svn+")
	for _source in ${source[@]}; do
	  #TODO: detect filename tags ie: somefile::https://some/url
	  _skip=0
	  
	  # check if source is a local file
	  for _prefix in ${_skip_prefix[@]}; do
	    if [[ $_source == $_prefix* ]]; then
	      _skip=1
	    fi
	  done
	  
	  # skip non local files
	  if [ $_skip == 1 ]; then
	    continue
	  fi
	  
	  # sync the local file if there is a change
	  # TO-DO: only update when there is
	  curl -L -s $_url/$_source -o $_basepath/$_source
	done
	
	# list of functions to override while keeping the old
	_overrrides=("prepare" "build" "package")
	for _override in ${_overrrides[@]}; do
	  eval "`declare -f ${_override} | sed '1s/.*/old_&/'`"
	done
}