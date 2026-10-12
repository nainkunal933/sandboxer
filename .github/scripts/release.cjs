const { execFileSync } = require('node:child_process');
const { statSync } = require('node:fs');
const { join } = require('node:path');

const STABLE_TAG = /^v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$/;
const ARCHIVES = [
  'sandboxer-linux-x86_64.tar.gz',
  'sandboxer-windows-x86_64.zip',
  'sandboxer-macos-arm64.tar.gz',
  'sandboxer-macos-x86_64.tar.gz',
];

function run(command, args) {
  return execFileSync(command, args, { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] }).trim();
}

function lines(value) {
  return value.split(/\r?\n/).filter(Boolean);
}

function stableTags(tags) {
  return tags.filter(tag => STABLE_TAG.test(tag)).sort((left, right) => {
    const a = STABLE_TAG.exec(left).slice(1).map(BigInt);
    const b = STABLE_TAG.exec(right).slice(1).map(BigInt);
    for (let index = 0; index < 3; index++) {
      if (a[index] !== b[index]) return a[index] > b[index] ? -1 : 1;
    }
    return 0;
  });
}

function selectBump(pullRequests) {
  const levels = ['patch', 'minor', 'major'];
  let level = 0;
  for (const pr of pullRequests) {
    for (const label of pr.labels) {
      const index = levels.findIndex(value => label.name === `release:${value}`);
      level = Math.max(level, index);
    }
  }
  return levels[level];
}

function isAncestor(ancestor, descendant, execute) {
  try {
    execute('git', ['merge-base', '--is-ancestor', ancestor, descendant]);
    return true;
  } catch (error) {
    if (error.status === 1) return false;
    throw error;
  }
}

async function getRelease(github, repo, tag) {
  try {
    return (await github.rest.repos.getReleaseByTag({ ...repo, tag })).data;
  } catch (error) {
    if (error.status === 404) return null;
    throw error;
  }
}

async function prepareRelease({ github, context, execute = run }) {
  const tags = stableTags(lines(execute('git', ['tag', '--list'])));
  const currentTags = stableTags(lines(execute('git', ['tag', '--points-at', context.sha])));
  const tag = currentTags[0];
  if (tag) {
    const release = await getRelease(github, context.repo, tag);
    return { publish: !release || release.draft, version: tag.slice(1), tag };
  }

  const previousTag = tags[0];
  if (previousTag && !isAncestor(previousTag, context.sha, execute)) {
    if (isAncestor(context.sha, previousTag, execute)) {
      return { publish: false, reason: `Commit is already covered by ${previousTag}.` };
    }
    throw new Error(`Release history diverges from ${previousTag}; refusing to choose a version.`);
  }

  const commits = lines(execute('git', ['rev-list', previousTag ? `${previousTag}..${context.sha}` : context.sha]));
  const commitSet = new Set(commits);
  const pullRequests = new Map();
  for (const commit_sha of commits) {
    const associated = await github.paginate(github.rest.repos.listPullRequestsAssociatedWithCommit, {
      ...context.repo, commit_sha, per_page: 100,
    });
    for (const pr of associated) {
      if (pr.merged_at && pr.base.ref === 'main' &&
          pr.base.repo.full_name.toLowerCase() === `${context.repo.owner}/${context.repo.repo}`.toLowerCase() &&
          commitSet.has(pr.merge_commit_sha)) {
        pullRequests.set(pr.number, pr);
      }
    }
  }

  const bump = selectBump(pullRequests.values());
  const baseline = previousTag ? previousTag.slice(1) : execute('uv', ['version', '--short']);
  if (!STABLE_TAG.test(`v${baseline}`)) throw new Error(`Expected a stable project version, got ${baseline}.`);
  execute('uv', ['version', baseline, '--frozen']);
  execute('uv', ['version', '--bump', bump, '--no-sync']);
  const version = execute('uv', ['version', '--short']);
  if (!STABLE_TAG.test(`v${version}`)) throw new Error(`uv returned an invalid release version: ${version}.`);
  return { publish: true, version, tag: `v${version}`, bump };
}

async function verifyTagTarget(github, repo, tag, sha) {
  let object;
  try {
    object = (await github.rest.git.getRef({ ...repo, ref: `tags/${tag}` })).data.object;
  } catch (error) {
    if (error.status === 404) return;
    throw error;
  }
  while (object.type === 'tag') {
    object = (await github.rest.git.getTag({ ...repo, tag_sha: object.sha })).data.object;
  }
  if (object.type !== 'commit' || object.sha !== sha) {
    throw new Error(`${tag} already points to another commit; refusing to publish.`);
  }
}

async function publishRelease({ github, context, tag, directory = 'artifacts', execute = run, inspect = statSync }) {
  if (!STABLE_TAG.test(tag)) throw new Error(`Invalid release tag: ${tag}.`);
  const assets = ARCHIVES.map(name => join(directory, name));
  for (const asset of assets) {
    const stat = inspect(asset);
    if (!stat.isFile() || stat.size === 0) throw new Error(`Missing or empty release archive: ${asset}.`);
  }
  await verifyTagTarget(github, context.repo, tag, context.sha);
  const release = await getRelease(github, context.repo, tag);
  if (release && !release.draft) return 'already published';
  if (release) {
    execute('gh', ['release', 'upload', tag, ...assets, '--clobber']);
    execute('gh', ['release', 'edit', tag, '--draft=false', '--latest']);
  } else {
    execute('gh', ['release', 'create', tag, ...assets, '--target', context.sha,
      '--title', `Sandboxer ${tag}`, '--generate-notes']);
  }
  return 'published';
}

module.exports = { prepareRelease, publishRelease, stableTags, selectBump };
