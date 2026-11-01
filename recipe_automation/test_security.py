"""Offline regression checks for Git credentials and safe push failures."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from git import Repo
from github_ops import _auth_env, clone_repository, commit_and_push_changes


class GitSecurityTests(unittest.TestCase):
    def test_clone_keeps_token_out_of_url(self):
        with patch('github_ops.Repo.clone_from') as clone:
            path, _ = clone_repository('https://github.com/example/recipes', 'secret-token')
            try:
                self.assertEqual(clone.call_args.args[0], 'https://github.com/example/recipes')
                self.assertIn('GIT_CONFIG_VALUE_0', clone.call_args.kwargs['env'])
                self.assertNotIn('secret-token', str(clone.call_args))
            finally:
                Path(path).rmdir()

    def test_credentials_restricted_to_github(self):
        for url in ('http://github.com/a/b', 'https://example.com/a/b', 'https://token@github.com/a/b'):
            with self.assertRaises(ValueError):
                _auth_env(url, 'secret-token')

    def test_existing_branch_and_failed_push(self):
        for failure in (False, True):
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as root:
                repo = Repo.init(root)
                with repo.config_writer() as config:
                    config.set_value('user', 'name', 'Test')
                    config.set_value('user', 'email', 'test@example.com')
                Path(root, 'recipe.md').write_text('# Recipe')
                repo.index.add(['recipe.md'])
                repo.index.commit('Initial')
                repo.create_head('add-recipe').checkout()
                repo.create_remote('origin', 'https://github.com/example/recipes')
                remote = MagicMock()
                if failure:
                    remote.push.return_value.raise_if_error.side_effect = RuntimeError('rejected')
                with patch.object(repo, 'remote', return_value=remote):
                    result = commit_and_push_changes(root, repo, 'recipe.md', 'add-recipe',
                                                     'https://github.com/example/recipes', 'token', cleanup=False)
                self.assertEqual(result, not failure)
                remote.push.assert_called_once_with(refspec='add-recipe:add-recipe')
                remote.set_url.assert_called_once_with('https://github.com/example/recipes')


class RetrySafetyTests(unittest.TestCase):
    def test_failed_push_preserves_timestamp_and_skips_pr(self):
        import main
        recipe = {"Recipe Name": "Test"}
        with patch.dict('os.environ', {"GITHUB_TOKEN": "token"}), \
                patch.object(main, 'get_new_recipes', return_value=[recipe]), \
                patch.object(main, 'clone_repository', return_value=('unused', MagicMock())), \
                patch.object(main, 'create_markdown', return_value=('recipe.md', 'test', [])), \
                patch.object(main, 'commit_and_push_changes', return_value=False), \
                patch.object(main, 'create_pull_request') as create_pr, \
                patch('builtins.open') as open_file:
            main.main()
        create_pr.assert_not_called()
        open_file.assert_not_called()


if __name__ == '__main__':
    unittest.main()
