Changelog
=========


(unreleased)
------------

Fix
~~~
- Report unreadable DOI file as a usage error. [Claude Opus 5.5,
  eriktks]

  `doi-downloader -f missing.txt` crashed with a FileNotFoundError
  traceback. Catch OSError when reading the DOI file and report it via
  parser.error(), so a missing file, a directory or an unreadable file
  gives a one-line message and exit code 2.
- Use ASCII status markers in CLI output. [Claude Sonnet 5, eriktks]

  Windows CI's default cp1252 console encoding can't encode the
  ✓/✗ Unicode symbols, so print() raised UnicodeEncodeError and
  failed 6 of the new CLI tests on tests_win. Swap them for plain
  ASCII "OK"/"FAIL" markers, which work under any console encoding.

Other
~~~~~
- [pre-commit.ci] auto fixes from pre-commit.com hooks. [pre-commit-
  ci[bot]]

  for more information, see https://pre-commit.ci
- Feat: register doi-downloader as an installable console script.
  [Claude Sonnet 5, eriktks]

  Adds a [project.scripts] entry so `pip install .` (or -e .) puts
  a doi-downloader command on PATH, wrapping doi_downloader.cli:main.
- Feat: add CLI entry point for downloading PDFs by DOI. [Claude Sonnet
  5, eriktks]

  Adds an argparse-based `doi-downloader` command that wraps
  download() for everyday single- or few-DOI use, accepting DOIs
  directly or via a --file list, distinct from the benchmark CSV
  batch runner.


1.1.2 (2026-09-22)
------------------
- Release: version 1.1.2 🚀 [eriktks]
- Merge pull request #73 from escience-tmsr/rename-pypi-package. [Erik
  Tjong Kim Sang]

  publish to PyPI as tmsr-doi-downloader
- [pre-commit.ci] auto fixes from pre-commit.com hooks. [pre-commit-
  ci[bot]]

  for more information, see https://pre-commit.ci
- Publish to PyPI as tmsr-doi-downloader. [eriktks]

  PyPI rejects doi_downloader/doi-downloader outright: 'The name is too
  similar to an existing project' - an unrelated existing PyPI project,
  doidownloader, is close enough (PyPI normalizes away - and _) to trip
  this on every upload attempt, regardless of anything else in the repo.

  Only the [project].name (the PyPI distribution name) changes; the
  importable module stays doi_downloader, confirmed by rebuilding locally:
  the wheel still ships doi_downloader/ with all its submodules, just
  renamed to tmsr_doi_downloader-*.whl / tmsr_doi_downloader-*.tar.gz.
  twine check passes on both artifacts.


1.1.1 (2026-09-22)
------------------
- Release: version 1.1.1 🚀 [eriktks]
- Merge pull request #72 from escience-tmsr/fix-pypi-packaging. [Erik
  Tjong Kim Sang]

  fix package discovery so the wheel actually ships doi_downloader
- [pre-commit.ci] auto fixes from pre-commit.com hooks. [pre-commit-
  ci[bot]]

  for more information, see https://pre-commit.ci
- Fix package discovery so the wheel actually ships doi_downloader.
  [eriktks]

  where = ["doi_downloader"] told setuptools the source root was inside
  doi_downloader/, so the built wheel only contained the plugins/ and
  extra_plugins/ subdirectories and never the doi_downloader package itself
  (confirmed by inspecting the built wheel: top_level.txt listed only
  extra_plugins and plugins). Verified the fix locally: the wheel now
  contains doi_downloader/__init__.py and every submodule.

  Also add --verbose to the twine upload step in release.yml, since the
  Upload Python Package workflow has failed on every tag push so far with
  a bare 'HTTPError: 400 Bad Request from https://upload.pypi.org/legacy/'
  and no further detail; twine only prints PyPI's actual rejection reason
  in verbose mode.
- Release: stage version-bump files and create the tag in make release.
  [eriktks]

  Fixes two bugs found while debugging a failed 1.1.0 release: the bump-my-version
  changes to doi_downloader/VERSION and pyproject.toml were never staged (only
  HISTORY.md was), so the release commit never actually contained the version
  bump; and no local tag was ever created before git push origin $(cat VERSION),
  so that push failed with 'src refspec ... does not match any'.


1.1.0 (2026-09-22)
------------------
- Release: bump version to 1.1.0 (files omitted from df3a82b) [eriktks]
- Release: version 1.1.0 🚀 [eriktks]
- Updated Makefile for releases. [eriktks]
- Updated Makefile for releases. [eriktks]
- Updated Makefile for releases. [eriktks]
- Updated Makefile for releases. [eriktks]
- Bump to version 1.0.0. [eriktks]
- Merge pull request #70 from escience-tmsr/sjvrijn-patch-1. [Sander van
  Rijn]

  Add pre-commit.ci badge to README
- Add pre-commit.ci badge to README. [Sander van Rijn]

  Added pre-commit.ci status badge to README
- Merge pull request #68 from escience-tmsr/54-apply-formatting. [Sander
  van Rijn]

  apply ruff/pre-commit formatting
- Apply pre-commit run --all. [Sander van Rijn]
- Ignore pycharm .idea folder. [Sander van Rijn]
- Apply ruff check --fix . and fix remainder. [Sander van Rijn]
- Apply ruff format . [Sander van Rijn]
- Merge pull request #66 from escience-tmsr/pyproject-toml-to-claude-md.
  [Sander van Rijn]

  Incorporate switch to using pyproject.toml in CLAUDE.md
- Added pre-commit to CLAUDE.md. [Claude, eriktks]
- Removed references to poetry. [Claude, eriktks]


1.0.0 (2026-07-31)
------------------
- Claude Code solution. [Claude, eriktks]
- Pyproject.toml switch to CLAUDE.md. [Claude, eriktks]
- Merge pull request #62 from escience-tmsr/53-pyproject-toml. [Sander
  van Rijn]

  Update repository to use pyproject.toml
- [CI]: update installation step for windows. [Sander van Rijn]
- Fix ruff check complaints (manually ignore a few for now) [Sander van
  Rijn]
- Update (dev) README. [Sander van Rijn]
- Update installation command in Makefile. [Sander van Rijn]
- Remove obsolete files. [Sander van Rijn]
- Add pyproject.toml file. [Sander van Rijn]
- Simplify ArticleDataObject imports. [Sander van Rijn]
- Merge pull request #47 from escience-tmsr/google_scholar_plugin. [Erik
  Tjong Kim Sang]

  Upgrading Google Scholar plugin, thanks for the reviews!
- Simplify link verification: just accept a list. [Sander van Rijn]
- Fixed review comments. [eriktks, s.vanrijn@esciencecenter.nl]
- Apply suggestions from code review. [Sander van Rijn]
- Processed review comments. [Claude, eriktks]
- Fix Github test errors. [eriktks]
- Fix Github test errors. [eriktks]
- Processed review comments. [eriktks]
- Fix review comment 3. [Claude, eriktks]
- Processed reviewer comments. [Claude, eriktks]
- Processing review comments. [eriktks]
- Fixed review comments. [eriktks]
- Solved linter problems. [eriktks]
- Shorter error messages. [eriktks]
- Testing and reacting. [eriktks]
- Fixed review comments. [Claude, eriktks]
- Claude tests for googlescholar. [eriktks]
- Harmoning, fixing tests bug. [eriktks]
- Get_page_with_requests. [eriktks]
- Harmonize plugin operation. [eriktks]
- Harmonize plugin operation. [eriktks]
- Retrieve metadata. [eriktks]
- Refactored code. [eriktks]
- Refactoring code. [eriktks]
- Refactored code. [eriktks]
- Refactored. [eriktks]
- Refactored code. [eriktks]
- Checking robots.txt. [eriktks]
- Counted validations. [eriktks]
- Check multiple links. [eriktks]
- Plugin results checks. [eriktks]
- Tests. [eriktks]
- More testing. [eriktks]
- Fixing linter complaint. [eriktks]
- Fixing linter complaint. [eriktks]
- Verifying the DOI. [eriktks]
- Merge pull request #60 from escience-tmsr/57-cleanup-github-folder.
  [Sander van Rijn]

  remove files in .github folder related to project creation
- Restore HISTORY.md; remove init.sh reference from makefile. [Sander
  van Rijn]
- Remove files in .github folder related to project creation. [Sander
  van Rijn]
- Merge pull request #61 from escience-tmsr/56-add-precommit. [Erik
  Tjong Kim Sang]

  Add pre-commit configuration
- Add dev readme. [Sander van Rijn]
- Add pre-commit configuration. [Sander van Rijn]
- Merge pull request #59 from escience-tmsr/58-cff-convert. [Sander van
  Rijn]

  add cffconvert.yml action file
- Add cffconvert.yml action file. [Sander van Rijn]
- Merge pull request #51 from escience-tmsr/CITATION.cff. [Erik Tjong
  Kim Sang]

  Added citation file. Thanks for the reviews!
- Fixed YAML syntax issues. [eriktks]
- Update CITATION.cff. [Erik Tjong Kim Sang, Sander van Rijn]
- Update CITATION.cff. [Erik Tjong Kim Sang, Sander van Rijn]
- Update CITATION.cff. [Erik Tjong Kim Sang, Sander van Rijn]
- Add citation file. [eriktks]
- Merge pull request #50 from escience-
  tmsr/dependabot/github_actions/actions/setup-python-7. [Erik Tjong Kim
  Sang]

  Bump actions/setup-python from 6 to 7
- Bump actions/setup-python from 6 to 7. [dependabot[bot]]

  Bumps [actions/setup-python](https://github.com/actions/setup-python) from 6 to 7.
  - [Release notes](https://github.com/actions/setup-python/releases)
  - [Commits](https://github.com/actions/setup-python/compare/v6...v7)

  ---
  updated-dependencies:
  - dependency-name: actions/setup-python
    dependency-version: '7'
    dependency-type: direct:production
    update-type: version-update:semver-major
  ...
- Merge pull request #49 from escience-
  tmsr/dependabot/github_actions/actions/checkout-7. [Erik Tjong Kim
  Sang]

  Bump actions/checkout from 6 to 7
- Bump actions/checkout from 6 to 7. [dependabot[bot]]

  Bumps [actions/checkout](https://github.com/actions/checkout) from 6 to 7.
  - [Release notes](https://github.com/actions/checkout/releases)
  - [Changelog](https://github.com/actions/checkout/blob/main/CHANGELOG.md)
  - [Commits](https://github.com/actions/checkout/compare/v6...v7)

  ---
  updated-dependencies:
  - dependency-name: actions/checkout
    dependency-version: '7'
    dependency-type: direct:production
    update-type: version-update:semver-major
  ...
- Merge pull request #48 from escience-
  tmsr/dependabot/github_actions/codecov/codecov-action-7. [Erik Tjong
  Kim Sang]

  Bump codecov/codecov-action from 6 to 7
- Bump codecov/codecov-action from 6 to 7. [dependabot[bot]]

  Bumps [codecov/codecov-action](https://github.com/codecov/codecov-action) from 6 to 7.
  - [Release notes](https://github.com/codecov/codecov-action/releases)
  - [Changelog](https://github.com/codecov/codecov-action/blob/main/CHANGELOG.md)
  - [Commits](https://github.com/codecov/codecov-action/compare/v6...v7)

  ---
  updated-dependencies:
  - dependency-name: codecov/codecov-action
    dependency-version: '7'
    dependency-type: direct:production
    update-type: version-update:semver-major
  ...
- Removed subdirectory, moved to separate repository browser-plugins.
  [eriktks]
- Added UnpaywallPDFDownloader evaluation. [eriktks]
- Merge pull request #39 from escience-tmsr/doi.org_plugin. [Erik Tjong
  Kim Sang]

  Merging doi.org plugin PR. Thanks for all the review comments
- Adapted towards review comment. [eriktks]
- Adapted towards review comment. [eriktks]
- Update doi_downloader/plugins/doiorg.py. [Erik Tjong Kim Sang, Sander
  van Rijn]
- Incorporated review comments. [eriktks]
- Added test summary. [eriktks]
- Fixed linter complaint. [eriktks]
- Fixed linter complaint. [eriktks]
- Fixed bug. [eriktks]
- Incorporated review comments. [eriktks]
- Update doi_downloader/plugins/doiorg.py. [Erik Tjong Kim Sang, Sander
  van Rijn]
- Update doi_downloader/plugins/doiorg.py. [Erik Tjong Kim Sang, Sander
  van Rijn]
- Update tests/test_doiorg.py. [Erik Tjong Kim Sang, Sander van Rijn]
- Update tests/test_doiorg.py. [Erik Tjong Kim Sang, Sander van Rijn]
- Updated requirements.txt. [eriktks]
- Updated requirements.txt. [eriktks]
- Fixed typo. [eriktks]
- Prepared tests for review. [eriktks]
- Refactored code. [eriktks]
- Refactored code. [eriktks]
- Added test. [eriktks]
- Initial version. [eriktks]
- Merge pull request #40 from escience-
  tmsr/dependabot/github_actions/softprops/action-gh-release-3. [Erik
  Tjong Kim Sang]

  Bump softprops/action-gh-release from 2 to 3
- Bump softprops/action-gh-release from 2 to 3. [dependabot[bot]]

  Bumps [softprops/action-gh-release](https://github.com/softprops/action-gh-release) from 2 to 3.
  - [Release notes](https://github.com/softprops/action-gh-release/releases)
  - [Changelog](https://github.com/softprops/action-gh-release/blob/master/CHANGELOG.md)
  - [Commits](https://github.com/softprops/action-gh-release/compare/v2...v3)

  ---
  updated-dependencies:
  - dependency-name: softprops/action-gh-release
    dependency-version: '3'
    dependency-type: direct:production
    update-type: version-update:semver-major
  ...
- Update README.md. [Erik Tjong Kim Sang]

  included doi-downloader performance
- Merge pull request #38 from escience-
  tmsr/dependabot/github_actions/codecov/codecov-action-6. [Erik Tjong
  Kim Sang]

  Bump codecov/codecov-action from 5 to 6
- Bump codecov/codecov-action from 5 to 6. [dependabot[bot]]

  Bumps [codecov/codecov-action](https://github.com/codecov/codecov-action) from 5 to 6.
  - [Release notes](https://github.com/codecov/codecov-action/releases)
  - [Changelog](https://github.com/codecov/codecov-action/blob/main/CHANGELOG.md)
  - [Commits](https://github.com/codecov/codecov-action/compare/v5...v6)

  ---
  updated-dependencies:
  - dependency-name: codecov/codecov-action
    dependency-version: '6'
    dependency-type: direct:production
    update-type: version-update:semver-major
  ...
- Merge pull request #35 from escience-tmsr/browser_plugins. [Erik Tjong
  Kim Sang]

  Browser plugins
- Extended usage instructions. [eriktks]
- Extended usage instructions. [eriktks]
- Moved listener outside function. [eriktks]
- Added puzzle icon image. [eriktks]
- Refactored tests. [eriktks]
- Refactoring tests. [eriktks]
- Added tests. [eriktks]
- Added tests. [eriktks]
- Added tests. [eriktks]
- Added tests. [eriktks]
- Added tests. [eriktks]
- Reported test in README. [eriktks]
- Added tests. [eriktks]
- Removed debugging code. [eriktks]
- Added tests. [eriktks]
- Added tests. [eriktks]
- Added tests. [eriktks]
- Added tests. [eriktks]
- Added tests. [eriktks]
- Added tests. [eriktks]
- Testing. [eriktks]
- Testing. [eriktks]
- Background.js. [eriktks]
- Refactoring and testing. [eriktks]
- Refactoring. [eriktks]
- Refactoring. [eriktks]
- Refactoring. [eriktks]
- Refactoring. [eriktks]
- Refactoring. [eriktks]
- Refactoring. [eriktks]
- Fixed log saving. [eriktks]
- Steps towards download logging. [eriktks]
- Removed bugs. [eriktks]
- Added more tests. [eriktks]
- Added tests. [eriktks]
- Added icon. [eriktks]
- Improved error messages. [eriktks]
- Improved error messages. [eriktks]
- Adding automatic download. [eriktks]
- Initial version. [eriktks]
- Merge pull request #37 from escience-
  tmsr/dependabot/github_actions/actions/checkout-6. [Erik Tjong Kim
  Sang]

  Bump actions/checkout from 4 to 6
- Bump actions/checkout from 4 to 6. [dependabot[bot]]

  Bumps [actions/checkout](https://github.com/actions/checkout) from 4 to 6.
  - [Release notes](https://github.com/actions/checkout/releases)
  - [Changelog](https://github.com/actions/checkout/blob/main/CHANGELOG.md)
  - [Commits](https://github.com/actions/checkout/compare/v4...v6)

  ---
  updated-dependencies:
  - dependency-name: actions/checkout
    dependency-version: '6'
    dependency-type: direct:production
    update-type: version-update:semver-major
  ...
- Merge pull request #36 from escience-
  tmsr/dependabot/github_actions/actions/setup-python-6. [Erik Tjong Kim
  Sang]

  Bump actions/setup-python from 5 to 6
- Bump actions/setup-python from 5 to 6. [dependabot[bot]]

  Bumps [actions/setup-python](https://github.com/actions/setup-python) from 5 to 6.
  - [Release notes](https://github.com/actions/setup-python/releases)
  - [Commits](https://github.com/actions/setup-python/compare/v5...v6)

  ---
  updated-dependencies:
  - dependency-name: actions/setup-python
    dependency-version: '6'
    dependency-type: direct:production
    update-type: version-update:semver-major
  ...
- Enable manual run. [Erik Tjong Kim Sang]
- Write access for docs. [Erik Tjong Kim Sang]
- Removed readthedocs installation. [Erik Tjong Kim Sang]
- Create docs.yml. [Erik Tjong Kim Sang]
- Merge pull request #32 from escience-tmsr/docs_update. [Erik Tjong Kim
  Sang]

  docs update
- Added docs/README.md. [eriktks]
- Merge branch 'main' into docs_update. [Erik Tjong Kim Sang]
- Merged with recent version. [eriktks]
- Fixed claude review comments. [eriktks]
- Removed examples. [eriktks]
- Described benchmarking. [eriktks]
- Rewritten docs phase 2. [eriktks]
- Checked and rewritten. [eriktks]
- Merge pull request #31 from escience-
  tmsr/dependabot/github_actions/stefanzweifel/git-auto-commit-action-7.
  [Erik Tjong Kim Sang]

  Bump stefanzweifel/git-auto-commit-action from 6 to 7
- Bump stefanzweifel/git-auto-commit-action from 6 to 7.
  [dependabot[bot]]

  Bumps [stefanzweifel/git-auto-commit-action](https://github.com/stefanzweifel/git-auto-commit-action) from 6 to 7.
  - [Release notes](https://github.com/stefanzweifel/git-auto-commit-action/releases)
  - [Changelog](https://github.com/stefanzweifel/git-auto-commit-action/blob/master/CHANGELOG.md)
  - [Commits](https://github.com/stefanzweifel/git-auto-commit-action/compare/v6...v7)

  ---
  updated-dependencies:
  - dependency-name: stefanzweifel/git-auto-commit-action
    dependency-version: '7'
    dependency-type: direct:production
    update-type: version-update:semver-major
  ...
- Merge pull request #30 from escience-
  tmsr/dependabot/github_actions/actions/setup-python-6. [Erik Tjong Kim
  Sang]

  Bump actions/setup-python from 5 to 6
- Merge branch 'main' into dependabot/github_actions/actions/setup-
  python-6. [Erik Tjong Kim Sang]
- Merge pull request #34 from escience-
  tmsr/dependabot/github_actions/actions/checkout-6. [Erik Tjong Kim
  Sang]

  Bump actions/checkout from 4 to 6
- Bump actions/checkout from 4 to 6. [dependabot[bot]]

  Bumps [actions/checkout](https://github.com/actions/checkout) from 4 to 6.
  - [Release notes](https://github.com/actions/checkout/releases)
  - [Changelog](https://github.com/actions/checkout/blob/main/CHANGELOG.md)
  - [Commits](https://github.com/actions/checkout/compare/v4...v6)

  ---
  updated-dependencies:
  - dependency-name: actions/checkout
    dependency-version: '6'
    dependency-type: direct:production
    update-type: version-update:semver-major
  ...
- Merge pull request #33 from escience-tmsr/benchmarking. [Erik Tjong
  Kim Sang]

  adds plugin benchmarking feature
- Simplifies logging system; removes context manager; integrates top
  performers analysis; updates benchmark docs. [kody.moodley@gmail.com]
- Adds plugin benchmarking feature. [kody.moodley@gmail.com]
- Bump actions/setup-python from 5 to 6. [dependabot[bot]]

  Bumps [actions/setup-python](https://github.com/actions/setup-python) from 5 to 6.
  - [Release notes](https://github.com/actions/setup-python/releases)
  - [Commits](https://github.com/actions/setup-python/compare/v5...v6)

  ---
  updated-dependencies:
  - dependency-name: actions/setup-python
    dependency-version: '6'
    dependency-type: direct:production
    update-type: version-update:semver-major
  ...
- Merge pull request #28 from escience-tmsr/feature/server_docs_locally.
  [R. Cushing]

  Added Makefile target for serving documentation locally
- Added `.PHONY` directive and `docs-deploy` target to Makefile for
  deploying documentation to GitHub Pages. [Reggie Cushing]
- Fixed `xdg-open` command usage and added new functionality for serving
  and deploying documentation locally and to GitHub Pages branch.
  [Reggie Cushing]
- Added configuration details for Unpaywall and Google Scholar plugins,
  including required environment variables. [Reggie Cushing]
- Merge pull request #27 from escience-tmsr/feature/serpAPI-plugin. [R.
  Cushing]

  Feature/serp api plugin
- Added configuration documentation for plugins requiring environment
  variables, including Unpaywall and Google Scholar. [Reggie Cushing]
- Added SerpApi as a new plugin for retrieving metadata and content
  associated with DOIs. [Reggie Cushing]
- Adding Google Scholar API. [Reggie Cushing]
- Trigger mkdocs rebuild. [Reggie Cushing]
- Merge pull request #26 from escience-tmsr/feature/fill_documentation.
  [R. Cushing]

  mkdocs documentation
- Added example documentation and usage instructions in `docs/usage.md`.
  [Reggie Cushing]
- Added support for loading environment variables from a `.env` file
  using the `dotenv` library, allowing plugins to access configuration
  settings such as API keys. [Reggie Cushing]
- Added configuration and contributing documentation with links to
  external resources. [Reggie Cushing]
- Adding documentation for caching functionality. [Reggie Cushing]
- Added a new navigation item for "Developing new plugins" in the
  mkdocs.yml file. [Reggie Cushing]
- Added examples for using Unpaywall plugin to fetch PDF URLs and
  download DOIs. [Reggie Cushing]
- Added support for multiple plugins to download PDFs from DOIs,
  including Crossref, Unpaywall, and CORE. [Reggie Cushing]
- Added documentation link to README.md and updated plugin class
  methods. [Reggie Cushing]
- Merge pull request #25 from escience-tmsr/fix/fix_template. [R.
  Cushing]

  Remove file
- Added navigation menu to mkdocs.yml with links to various pages.
  [Reggie Cushing]
- Remove file. [Reggie Cushing]
- Merge pull request #24 from escience-tmsr/feature/abstract-download-
  function. [R. Cushing]

  Feature/abstract download function
- Added retry mechanism with limited attempts to improve plugin
  reliability. [Reggie Cushing]
- Added documentation for simple example usage of the doi_downloader
  library. [Reggie Cushing]
- Added logging for plugin output to improve user experience. [Reggie
  Cushing]
- Added functionality to validate downloaded PDF files by checking their
  header, ensuring only valid PDFs are kept. [Reggie Cushing]
- Added a check to exit the loop early when a PDF is successfully
  downloaded. [Reggie Cushing]
- Added downloads directory to .gitignore and updated loader.py to use
  the correct folder path for plugin modules. [Reggie Cushing]
- Merge pull request #22 from escience-
  tmsr/dependabot/github_actions/stefanzweifel/git-auto-commit-action-6.
  [R. Cushing]

  Bump stefanzweifel/git-auto-commit-action from 5 to 6
- Bump stefanzweifel/git-auto-commit-action from 5 to 6.
  [dependabot[bot]]

  Bumps [stefanzweifel/git-auto-commit-action](https://github.com/stefanzweifel/git-auto-commit-action) from 5 to 6.
  - [Release notes](https://github.com/stefanzweifel/git-auto-commit-action/releases)
  - [Changelog](https://github.com/stefanzweifel/git-auto-commit-action/blob/master/CHANGELOG.md)
  - [Commits](https://github.com/stefanzweifel/git-auto-commit-action/compare/v5...v6)

  ---
  updated-dependencies:
  - dependency-name: stefanzweifel/git-auto-commit-action
    dependency-version: '6'
    dependency-type: direct:production
    update-type: version-update:semver-major
  ...
- Merge pull request #23 from escience-tmsr/fix/check-for-plugin-
  folders. [R. Cushing]

  Added a check to ensure the plugin folder is a directory before attem…
- Added a check to ensure the plugin folder is a directory before
  attempting to load its contents. [Reggie Cushing]
- Load plugins from extra_plugin folder also. [Reggie Cushing]
- Update README. [Reggie Cushing]
- Merge pull request #21 from escience-
  tmsr/tests/write_code_coverage_tests. [R. Cushing]

  Tests/write code coverage tests
- Adding pytest.ini file. [Reggie Cushing]
- Adding python-dotenv to test req. [Reggie Cushing]
- Mocking dotenv. [Reggie Cushing]
- Adding test env variable. [Reggie Cushing]
- Adding core_ac_uk api test. [Reggie Cushing]
- Adding test files. [Reggie Cushing]
- Adding crossref test. [Reggie Cushing]
- Adding unpaywall test and plugin loader test. [Reggie Cushing]
- Merge pull request #20 from escience-
  tmsr/fix/coreapi_schema_validation. [R. Cushing]

  fix setting title to string instead of list
- Fix setting title to string instead of list. [Reggie Cushing]
- Merge pull request #19 from escience-
  tmsr/feature/add_version_to_json_db. [R. Cushing]

  adding version tag in json object in db
- Adding version tag in json object in db. [Reggie Cushing]
- Merge pull request #18 from escience-tmsr/feature/core_api. [R.
  Cushing]

  Feature/core api
- Adding core api. [Reggie Cushing]
- Adding core.ac.uk api. [Reggie Cushing]
- Adding core.ac.uk api. [Reggie Cushing]
- Merge pull request #17 from escience-tmsr/feature/plugin_framework.
  [R. Cushing]

  Feature/plugin framework
- Update examples. [Reggie Cushing]
- Remove commented code. [Reggie Cushing]
- Refactor to plugin framework. [Reggie Cushing]
- Refactor to plugin framework. [Reggie Cushing]
- Merge pull request #16 from escience-tmsr/feature/json-schema. [R.
  Cushing]

  Feature/json schema
- Linting. [Reggie Cushing]
- Updated schema and adaptors. [Reggie Cushing]
- Lint. [Reggie Cushing]
- Update requirements.txt. [Reggie Cushing]
- Using duckdb. [Reggie Cushing]
- Using single json schema for artciles. [Reggie Cushing]
- Testing crossref schema. [Reggie Cushing]
- Adding data object methods. [Reggie Cushing]
- Adding article json data object and schema validator. [Reggie Cushing]
- Merge pull request #13 from escience-tmsr/feature/crossref_api. [R.
  Cushing]

  Feature/crossref api
- Linting. [Reggie Cushing]
- Adding crossref. [Reggie Cushing]
- Upgrade jinja2. [Reggie Cushing]
- Adding crossref api. [Reggie Cushing]
- Merge pull request #12 from escience-tmsr/feature/8-cache-responses.
  [R. Cushing]

  testing cache content
- Adding examples README. [Reggie Cushing]
- Adding examples README. [Reggie Cushing]
- Testing cache content. [Reggie Cushing]
- Merge pull request #10 from escience-tmsr/feature/7-implement-
  unpaywall-api. [R. Cushing]

  implement module for unpaywall API
- Update test. [Reggie Cushing]
- Adding module pdf_download. [Reggie Cushing]
- Adding scripts to check cache for doi to pdf mapping. [Reggie Cushing]
- Adding cache object. [Reggie Cushing]
- Adding example. [Reggie Cushing]
- Merge remote-tracking branch 'origin/main' into feature/7-implement-
  unpaywall-api. [Reggie Cushing]
- Merge pull request #11 from escience-
  tmsr/dependabot/github_actions/codecov/codecov-action-5. [R. Cushing]

  Bump codecov/codecov-action from 4 to 5
- Bump codecov/codecov-action from 4 to 5. [dependabot[bot]]

  Bumps [codecov/codecov-action](https://github.com/codecov/codecov-action) from 4 to 5.
  - [Release notes](https://github.com/codecov/codecov-action/releases)
  - [Changelog](https://github.com/codecov/codecov-action/blob/main/CHANGELOG.md)
  - [Commits](https://github.com/codecov/codecov-action/compare/v4...v5)

  ---
  updated-dependencies:
  - dependency-name: codecov/codecov-action
    dependency-type: direct:production
    update-type: version-update:semver-major
  ...
- Merge main. [Reggie Cushing]
- Merge pull request #5 from escience-
  tmsr/dependabot/github_actions/codecov/codecov-action-4. [R. Cushing]

  Bump codecov/codecov-action from 3 to 4
- Bump codecov/codecov-action from 3 to 4. [dependabot[bot]]

  Bumps [codecov/codecov-action](https://github.com/codecov/codecov-action) from 3 to 4.
  - [Release notes](https://github.com/codecov/codecov-action/releases)
  - [Changelog](https://github.com/codecov/codecov-action/blob/main/CHANGELOG.md)
  - [Commits](https://github.com/codecov/codecov-action/compare/v3...v4)

  ---
  updated-dependencies:
  - dependency-name: codecov/codecov-action
    dependency-type: direct:production
    update-type: version-update:semver-major
  ...
- Merge pull request #4 from escience-
  tmsr/dependabot/github_actions/actions/setup-python-5. [R. Cushing]

  Bump actions/setup-python from 4 to 5
- Merge branch 'main' into dependabot/github_actions/actions/setup-
  python-5. [R. Cushing]
- Merge pull request #3 from escience-
  tmsr/dependabot/github_actions/softprops/action-gh-release-2. [R.
  Cushing]

  Bump softprops/action-gh-release from 1 to 2
- Bump softprops/action-gh-release from 1 to 2. [dependabot[bot]]

  Bumps [softprops/action-gh-release](https://github.com/softprops/action-gh-release) from 1 to 2.
  - [Release notes](https://github.com/softprops/action-gh-release/releases)
  - [Changelog](https://github.com/softprops/action-gh-release/blob/master/CHANGELOG.md)
  - [Commits](https://github.com/softprops/action-gh-release/compare/v1...v2)

  ---
  updated-dependencies:
  - dependency-name: softprops/action-gh-release
    dependency-type: direct:production
    update-type: version-update:semver-major
  ...
- Merge pull request #2 from escience-
  tmsr/dependabot/github_actions/stefanzweifel/git-auto-commit-action-5.
  [R. Cushing]

  Bump stefanzweifel/git-auto-commit-action from 4 to 5
- Bump stefanzweifel/git-auto-commit-action from 4 to 5.
  [dependabot[bot]]

  Bumps [stefanzweifel/git-auto-commit-action](https://github.com/stefanzweifel/git-auto-commit-action) from 4 to 5.
  - [Release notes](https://github.com/stefanzweifel/git-auto-commit-action/releases)
  - [Changelog](https://github.com/stefanzweifel/git-auto-commit-action/blob/master/CHANGELOG.md)
  - [Commits](https://github.com/stefanzweifel/git-auto-commit-action/compare/v4...v5)

  ---
  updated-dependencies:
  - dependency-name: stefanzweifel/git-auto-commit-action
    dependency-type: direct:production
    update-type: version-update:semver-major
  ...
- Merge pull request #1 from escience-
  tmsr/dependabot/github_actions/actions/checkout-4. [R. Cushing]

  Bump actions/checkout from 3 to 4
- Bump actions/checkout from 3 to 4. [dependabot[bot]]

  Bumps [actions/checkout](https://github.com/actions/checkout) from 3 to 4.
  - [Release notes](https://github.com/actions/checkout/releases)
  - [Changelog](https://github.com/actions/checkout/blob/main/CHANGELOG.md)
  - [Commits](https://github.com/actions/checkout/compare/v3...v4)

  ---
  updated-dependencies:
  - dependency-name: actions/checkout
    dependency-type: direct:production
    update-type: version-update:semver-major
  ...
- Merge pull request #6 from escience-tmsr/feature/convert_to_package.
  [R. Cushing]

  Feature/convert to package
- Disable pip install on windows due to error. [Reggie Cushing]
- Mock API requests in unit tests. [Reggie Cushing]
- Update setup.py. [Reggie Cushing]
- Update readme. [Reggie Cushing]
- Update test with smaller file to download. [Reggie Cushing]
- Update unit test for unpaywall. [Reggie Cushing]
- Adding unpaywall module. [Reggie Cushing]
- Update readme. [Reggie Cushing]
- Fix typo. [Reggie Cushing]
- Update README. [Reggie Cushing]
- Pass csv file with dois. [Reggie Cushing]
- Add requirments.txt. [Reggie Cushing]
- Linting. [Reggie Cushing]
- Remove unecessary print. [Reggie Cushing]
- Remove dois from code. [Reggie Cushing]
- First script attempt to access unpaywall API. [Reggie Cushing]
- Remove doc. [Reggie Cushing]
- Create LICENSE. [recap]
- Remove lic. [Reggie Cushing]
- Bump actions/setup-python from 4 to 5. [dependabot[bot]]

  Bumps [actions/setup-python](https://github.com/actions/setup-python) from 4 to 5.
  - [Release notes](https://github.com/actions/setup-python/releases)
  - [Commits](https://github.com/actions/setup-python/compare/v4...v5)

  ---
  updated-dependencies:
  - dependency-name: actions/setup-python
    dependency-type: direct:production
    update-type: version-update:semver-major
  ...
- ✅ Ready to clone and code. [recap]
- Initial commit. [recap]
