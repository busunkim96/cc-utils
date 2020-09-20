# SPDX-FileCopyrightText: 2019 SAP SE or an SAP affiliate company and Gardener contributors
#
# SPDX-License-Identifier: Apache-2.0

import urllib

from ci.util import (
    CliHint,
    ctx,
)
from gitutil import GitHelper
from github.util import (
    GitHubRepositoryHelper,
    GitHubRepoBranch,
    _add_user_to_team,
    _add_all_repos_to_team,
    _create_team,
    find_greatest_github_release_version,
    outdated_draft_releases,

)
from github.release_notes.util import (
    ReleaseNotes,
)
import ccc.github

import github3


def assign_github_team_to_repo(
    github_cfg_name: str,
    github_org_name: str,
    auth_token: CliHint(help="Token from an org admin user. Token must have 'admin:org' scope"),
    team_name: str='ci'
):
    '''
    Assign team 'team_name' to all repositories in organization 'github_org_name' and
    give the team admin rights on those repositories. The team will be created if it does not exist
    and the technical github user (from github_cfg_name) will be assigned to the team.
    The token of the technical github user must have the privilege to create webhooks
    (scope admin:repo_hook)
    'auth_token'  must grant 'admin:org' privileges.
    '''
    cfg_factory = ctx().cfg_factory()
    github_cfg = cfg_factory.github(github_cfg_name)
    github_username = github_cfg.credentials().username()

    # overwrite auth_token
    github_cfg.credentials().set_auth_token(auth_token=auth_token)

    github = ccc.github.github_api(
        github_cfg=github_cfg,
    )

    _create_team(
        github=github,
        organization_name=github_org_name,
        team_name=team_name
    )

    _add_user_to_team(
        github=github,
        organization_name=github_org_name,
        team_name=team_name,
        user_name=github_username
    )

    _add_all_repos_to_team(
        github=github,
        organization_name=github_org_name,
        team_name=team_name
    )


def generate_release_notes_cli(
    repo_dir: str,
    github_cfg_name: str,
    github_repository_owner: str,
    github_repository_name: str,
    repository_branch: str,
    commit_range: str=None
):
    github_cfg = ctx().cfg_factory().github(github_cfg_name)

    githubrepobranch = GitHubRepoBranch(
        github_config=github_cfg,
        repo_owner=github_repository_owner,
        repo_name=github_repository_name,
        branch=repository_branch,
    )

    helper = GitHubRepositoryHelper.from_githubrepobranch(
        githubrepobranch=githubrepobranch,
    )
    git_helper = GitHelper.from_githubrepobranch(
        repo_path=repo_dir,
        githubrepobranch=githubrepobranch,
    )

    ReleaseNotes.create(
        github_helper=helper,
        git_helper=git_helper,
        repository_branch=repository_branch,
        commit_range=commit_range
    ).to_markdown()


def release_note_blocks_cli(
    repo_dir: str,
    github_cfg_name: str,
    github_repository_owner: str,
    github_repository_name: str,
    repository_branch: str=None,
    commit_range: str=None
):
    github_cfg = ctx().cfg_factory().github(github_cfg_name)

    githubrepobranch = GitHubRepoBranch(
        github_config=github_cfg,
        repo_owner=github_repository_owner,
        repo_name=github_repository_name,
        branch=repository_branch,
    )

    helper = GitHubRepositoryHelper.from_githubrepobranch(
        githubrepobranch=githubrepobranch,
    )
    git_helper = GitHelper.from_githubrepobranch(
        repo_path=repo_dir,
        githubrepobranch=githubrepobranch,
    )

    ReleaseNotes.create(
        github_helper=helper,
        git_helper=git_helper,
        repository_branch=repository_branch,
        commit_range=commit_range
    ).release_note_blocks()


def list_draft_releases(
    github_cfg_name: str,
    github_repository_owner: str,
    github_repository_name: str,
    only_outdated: bool = False,
):
    '''List all draft releases in a GitHub repository. If the `--only-outdated` flag is set,
    only outdated draft releases are printed. A draft release is considered outdated iff:
        1: its version is smaller than the greatest release version (according to semver) AND
            2a: it is NOT a hotfix draft release AND
            2b: there are no hotfix draft releases with the same major and minor version
            OR
            3a: it is a hotfix draft release AND
            3b: there is a hotfix draft release of greater version (according to semver)
                with the same major and minor version

    Hotfix draft release in this context are draft releases with a semver patch version that is
    not equal to 0.
    '''
    github_cfg = ctx().cfg_factory().github(github_cfg_name)
    github_helper = GitHubRepositoryHelper(
        owner=github_repository_owner,
        name=github_repository_name,
        github_cfg=github_cfg,
    )
    if only_outdated:
        releases = [release for release in github_helper.repository.releases()]
        non_draft_releases = [release for release in releases if not release.draft]
        greatest_release_version = find_greatest_github_release_version(non_draft_releases)
    else:
        releases = github_helper.repository.releases()

    draft_releases = [release for release in releases if release.draft]

    if only_outdated:
        draft_releases = outdated_draft_releases(
            draft_releases=draft_releases,
            greatest_release_version=greatest_release_version,
        )
    for draft_release in draft_releases:
        print(draft_release.name)


def delete_releases(
    github_cfg_name: str,
    github_repository_owner: str,
    github_repository_name: str,
    release_name: [str],
):
    github_cfg = ctx().cfg_factory().github(github_cfg_name)
    github_helper = GitHubRepositoryHelper(
        owner=github_repository_owner,
        name=github_repository_name,
        github_cfg=github_cfg,
    )
    github_helper.delete_releases(release_names=release_name)


def greatest_release_version(
    github_repository_url: CliHint(help='e.g.: https://github.com/gardener/cc-utils'),
    anonymous: CliHint(
        typehint=bool,
        help='Use anonymous access. Unauthenticated access is only possible on github.com.',
    ) = False,
):
    '''Find the release with the greatest name (according to semver) and print its semver-version.

    Note:
    - This will only consider releases whose names are either immediately parseable as semver-
    versions, or prefixed with a single character ('v').
    - The 'v'-prefix (if present) will be not be present in the output.
    - If a release has no name, its tag will be used instead of its name.

    For more details on the ordering of semantic versioning, see 'https://www.semver.org'.
    '''
    parse_result = urllib.parse.urlparse(github_repository_url)

    if not parse_result.netloc:
        raise ValueError(f'Could not determine host for github-url {github_repository_url}')
    host = parse_result.netloc

    try:
        path = parse_result.path.strip('/')
        org, repo = path.split('/')
    except ValueError as e:
        raise ValueError(f"Could not extract org- and repo-name. Error: {e}")

    if anonymous:
        if 'github.com' not in host:
            raise ValueError("Anonymous access is only possible for github.com")
        github_api = github3.GitHub()
        repo_helper = GitHubRepositoryHelper(owner=org, name=repo, github_api=github_api)

    else:
        repo_helper = ccc.github.repo_helper(host=host, org=org, repo=repo)

    print(
        find_greatest_github_release_version(
            releases=repo_helper.repository.releases(),
            warn_for_unparseable_releases=False,
        )
    )
