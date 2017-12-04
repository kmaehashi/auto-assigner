#!/usr/bin/env python

import github

import argparse
import os
import random
import sys


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--organization', type=str, required=True)
    parser.add_argument('--repo', type=str, required=True)
    parser.add_argument('--team', type=str, required=True)
    parser.add_argument('--issue', type=int, default=None)
    parser.add_argument('--all-pull-requests', action='store_true',
                        default=False,
                        help='add assignee to all open Pull-Requests '
                             '(use with care!)')
    parser.add_argument('--token', type=str, default=None)
    params = parser.parse_args(args)

    if params.token is None:
        params.token = os.environ.get('GITHUB_ACCESS_TOKEN')
        if params.token is None:
            raise RuntimeError(
                '--token option or GITHUB_ACCESS_TOKEN environment'
                'variable must be specified')

    if params.issue is None and not params.all_pull_requests:
        raise RuntimeError(
            '--issue option or --all-pull-requests option must be specified')
    elif params.issue is not None and params.all_pull_requests:
        raise RuntimeError(
            '--issue option and --all-pull-requests option cannot be '
            'specified together')

    return params


def get_team_by_name(org, name):
    for team in org.get_teams():
        if team.name == name:
            return org.get_team(team.id)
    raise RuntimeError('no team named {} found'.format(name))


def set_assignee_to_issue(candidates, issue):
    if 0 < len(issue.assignees):
        print('Warning: Issue/Pull-Request #{} already assigned to {}'.format(
            params.issue, [user.login for user in issue.assignees]))
        return

    assignee = random.choice(candidates)
    issue.edit(assignees=[assignee])
    print('Issue/Pull-Request #{} assigned to {}'.format(
        issue.number, assignee))


def main(args=sys.argv[1:]):
    params = parse_args(args)

    g = github.Github(params.token)
    org = g.get_organization(params.organization)
    repo = org.get_repo(params.repo)

    team = get_team_by_name(org, params.team)
    candidates = [member.login for member in team.get_members()]

    if params.all_pull_requests:
        print('Getting all issues (this may take a while)...')
        issues = repo.get_issues(state='open', assignee='none')
        prs = [issue for issue in issues if issue.pull_request is not None]
        for pr in prs:
            set_assignee_to_issue(candidates, pr)
    else:
        issue = repo.get_issue(params.issue)
        set_assignee_to_issue(candidates, issue)


if __name__ == '__main__':
    main()
