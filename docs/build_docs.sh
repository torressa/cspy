#!/bin/bash
set -x
################################################################################
# From https://tech.michaelaltfield.net/2020/07/18/sphinx-rtd-github-pages-1/
################################################################################

###################
# INSTALL DEPENDS #
###################

apt-get update
apt-get -y install git rsync python3-sphinx python3-sphinx-rtd-theme \
  python3-git python3-pip python3-virtualenv python3-setuptools doxygen

#####################
# DECLARE VARIABLES #
#####################

pwd
ls -lah
export SOURCE_DATE_EPOCH=$(git log -1 --pretty=%ct)

##############
# BUILD DOCS #
##############

# Steps from RTD
python3 -m pip install --upgrade --no-cache-dir pip setuptools
python3 -m pip install --upgrade --no-cache-dir mock pillow \
  commonmark recommonmark sphinx sphinx-rtd-theme readthedocs-sphinx-ext
python3 -m pip install -r docs/requirements.txt
cd docs
python3 -m sphinx -T -E -b html -d _build/doctrees -D language=en . _build/html
cd ..

#######################
# Update GitHub Pages #
#######################

git config --global user.name "${GITHUB_ACTOR}"
git config --global user.email "${GITHUB_ACTOR}@users.noreply.github.com"

docroot=`mktemp -d`
rsync -av "docs/_build/html/" "${docroot}/"
cp -r docs/ ${docroot}/docs/

ls ${docroot}
ls ${docroot}/docs

pushd "${docroot}"

# don't bother maintaining history; just generate fresh
git init
git remote add deploy "https://token:${GITHUB_TOKEN}@github.com/${GITHUB_REPOSITORY}.git"
git checkout -b gh-pages

# add .nojekyll to the root so that github won't 404 on content added to dirs
# that start with an underscore (_), such as our "_content" dir..
touch .nojekyll

# TODO: fix issues with custom domain
# Add CNAME - this is required for GitHub to know what our custom domain is
# echo "cspy.docs" > CNAME

# Add README
cat > README.md <<EOF
# GitHub Pages Cache

Nothing to see here. The contents of this branch are essentially a cache that's not intended to be viewed on github.com.


If you're looking to update our documentation, check the relevant development branch's 'docs/' dir.
EOF

# copy the resulting html pages built from sphinx above to our new git repo
git add .

# commit all the new files
msg="Updating Docs for commit ${GITHUB_SHA} made on `date -d"@${SOURCE_DATE_EPOCH}" --iso-8601=seconds` from ${GITHUB_REF} by ${GITHUB_ACTOR}"
git commit -am "${msg}"

# overwrite the contents of the gh-pages branch on our github.com repo
git push deploy gh-pages --force

popd # return to main repo sandbox root

# exit cleanly
exit 0
