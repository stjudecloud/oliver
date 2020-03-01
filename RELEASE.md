# Releasing

You can do the following to create a release:

1. Run `poetry install` on the `master` branch to ensure you have the dev dependencies.
2. Run `semantic-release version` to look at the commits since the last release, determine the version bump needed (if any), and then update the version + add tags to the repo.
3. Run `git push --all` to push all commits and tags.
4. GitHub Actions should both
   1. Cut a release on the [release page](https://github.com/stjudecloud/oliver/releases) with the relevant release notes, and
   2. Upload a release to PyPI.
5. After a few hours, the conda-forge watcher will automatically make a PR on the [Oliver feedstock repo](https://github.com/conda-forge/oliver-feedstock). You'll need to review the PR and merge in to update conda-forge.