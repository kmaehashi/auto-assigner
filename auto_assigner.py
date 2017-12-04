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
    parser.add_argument('--issue', type=int, required=True)
    parser.add_argument('--token', type=str, default=None)
    params = parser.parse_args(args)

    if params.token is None:
        params.token = os.environ.get('GITHUB_ACCESS_TOKEN')
        if params.token is None:
            raise RuntimeError(
                '--token option or GITHUB_ACCESS_TOKEN environment'
                'variable must be specified')

    return params


def get_team_by_name(org, name):
    for team in org.get_teams():
        if team.name == name:
            return org.get_team(team.id)
    raise RuntimeError('no team named {} found'.format(name))


def main(args=sys.argv[1:]):
    params = parse_args(args)

    g = github.Github(params.token)
    org = g.get_organization(params.organization)
    repo = org.get_repo(params.repo)

    issue = repo.get_issue(params.issue)
    if 0 < len(issue.assignees):
        # Assignee(s) are already set.
        print('Warning: Issue/Pull-Request #{} already assigned to {}'.format(
            params.issue, [user.login for user in issue.assignees]))
        return

    team = get_team_by_name(org, params.team)
    candidates = [member.login for member in team.get_members()]
    assignee = random.choice(candidates)

    issue.edit(assignees=[assignee])
    print('Issue/Pull-Request #{} assigned to {}'.format(
        params.issue, assignee))


if __name__ == '__main__':
    main()
