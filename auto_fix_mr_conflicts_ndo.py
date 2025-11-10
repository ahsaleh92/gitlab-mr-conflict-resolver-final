#!/usr/bin/env python3
"""
Auto-fix GitLab MR conflicts - Customized for NDO/Terraform Environment
Handles terraform files, workspace-specific conflicts, NDO schema conflicts
"""

import os
import sys
import json
import yaml
import logging
import argparse
import tempfile
import shutil
import re
import subprocess
from subprocess import TimeoutExpired
from typing import Dict, List, Optional
from datetime import datetime

try:
    import git
    import gitlab
    import urllib3
except ImportError:
    print("ERROR: Install with: pip install gitpython python-gitlab pyyaml urllib3")
    sys.exit(1)

# Configure UTF-8 encoding for Windows compatibility
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    # Bypass proxy for corporate network
    os.environ['NO_PROXY'] = '*'
    os.environ['no_proxy'] = '*'
    # Disable SSL warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    if sys.version_info >= (3, 7):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except:
            pass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(
            f'mr_fix_ndo_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
            encoding='utf-8'
        ),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class NDOMRConflictAutoFixer:
    """Auto-fix MR conflicts in NDO/Terraform environment"""
    
    def __init__(self, config_file: str = 'config_ndo.yaml', config_dict: dict = None):
        """
        Initialize with either config file or embedded config dict
        
        Args:
            config_file: Path to YAML config file (default: 'config_ndo.yaml')
            config_dict: Direct config dictionary (overrides config_file if provided)
        """
        if config_dict:
            self.config = config_dict
            logger.info("Configuration loaded from embedded config")
        else:
            self.config = self._load_config(config_file)
        
        self.gl = None
        self.project = None
        self.temp_dir = None
        self.repo = None
        self.cancel_flag = False  # Add cancel flag support
        
        self.report = {
            'timestamp': datetime.now().isoformat(),
            'merge_request': {},
            'environment': 'NDO/Terraform',
            'status': 'PENDING',
            'issues_found': [],
            'actions_taken': [],
            'warnings': [],
            'terraform_files_detected': [],
            'ndo_files_detected': [],
            'result': 'UNKNOWN'
        }
    
    def _load_config(self, config_file: str) -> Dict:
        """Load configuration from YAML"""
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {config_file}")
            return config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            sys.exit(1)
    
    def authenticate(self) -> bool:
        """Authenticate to GitLab with detailed logging"""
        try:
            logger.info("Attempting authentication...")
            
            # Try environment variables first, then config file (with detailed logging)
            token = os.getenv('CI_JOB_TOKEN')
            if token:
                logger.info("  → Using CI_JOB_TOKEN")
            else:
                token = os.getenv('GITLAB_PRIVATE_TOKEN')
                if token:
                    logger.info("  → Using GITLAB_PRIVATE_TOKEN")
                else:
                    token = os.getenv('GITLAB_TOKEN')
                    if token:
                        logger.info("  → Using GITLAB_TOKEN")
                    else:
                        # Try to get from config
                        token = self.config.get('gitlab_token')
                        if token:
                            logger.info("  → Using config file token")
            
            if not token:
                logger.error("  ✗ No token found in any source!")
                logger.error("Set GITLAB_TOKEN, GITLAB_PRIVATE_TOKEN or use CI_JOB_TOKEN in pipeline")
                return False
            
            api_url = self.config.get('gitlab_api_url', 'https://gitlab.allianzcaf/api/v4')
            gitlab_url = self.config.get('gitlab_url', 'https://gitlab.allianzcaf')
            
            # SSL verification: Check config first, then environment variable
            # Default: disabled (ssl_verify=False) for corporate networks with self-signed certs
            ssl_verify = self.config.get('ssl_verify', False)
            if os.getenv('CORP_NETWORK', '').lower() == 'true':
                ssl_verify = False  # Environment variable override
            
            if not ssl_verify:
                logger.warning("  ⚠️  SSL verification disabled (corporate network mode)")
                # Disable SSL verification for self-signed certificates
                import urllib3
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            else:
                logger.info("  ✓ SSL verification enabled (secure mode)")
            
            # Proxy bypass: Check config first, then apply
            # Default: enabled (bypass_proxy=True) for corporate networks
            bypass_proxy = self.config.get('bypass_proxy', True)
            if bypass_proxy:
                os.environ['NO_PROXY'] = '*'
                logger.info("  → Proxy bypass enabled")
            
            self.gl = gitlab.Gitlab(gitlab_url, private_token=token, ssl_verify=ssl_verify)
            self.gl.auth()
            
            project_id = self.config.get('gitlab_project_id')
            self.project = self.gl.projects.get(project_id)
            
            logger.info(f"✓ Connected to GitLab project: {self.project.path_with_namespace}")
            return True
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    def get_mr_details(self, mr_iid: int) -> bool:
        """Get merge request details"""
        try:
            mr = self.project.mergerequests.get(mr_iid)
            
            self.report['merge_request'] = {
                'iid': mr.iid,
                'title': mr.title,
                'source_branch': mr.source_branch,
                'target_branch': mr.target_branch,
                'state': mr.state,
                'merge_status': mr.merge_status,
                'author': mr.author['username'] if mr.author else 'unknown',
                'web_url': mr.web_url
            }
            
            logger.info(f"\n{'='*70}")
            logger.info(f"MR #{mr.iid}: {mr.title}")
            logger.info(f"{'='*70}")
            logger.info(f"Source: {mr.source_branch} → Target: {mr.target_branch}")
            logger.info(f"Status: {mr.merge_status}")
            logger.info(f"Author: {mr.author['username'] if mr.author else 'unknown'}")
            
            # Check for conflicts
            if mr.merge_status == 'cannot_be_merged':
                self.report['issues_found'].append('Merge conflicts detected')
                self.report['merge_request']['has_conflicts'] = True
                logger.warning("⚠️  ISSUE: Merge conflicts")
            else:
                self.report['merge_request']['has_conflicts'] = False
            
            return True
        except Exception as e:
            logger.error(f"Failed to get MR: {e}")
            return False
    
    def detect_file_types(self, conflicting_files: List[str]):
        """Detect terraform and NDO files in conflicts"""
        for file_path in conflicting_files:
            if file_path.endswith('.tf') or '.terraform' in file_path:
                self.report['terraform_files_detected'].append(file_path)
                logger.warning(f"  ⚠️  Terraform file: {file_path}")
            
            if file_path.endswith('.yaml') or file_path.endswith('.yml'):
                if 'schema' in file_path.lower() or 'ndo' in file_path.lower():
                    self.report['ndo_files_detected'].append(file_path)
                    logger.warning(f"  ⚠️  NDO schema file: {file_path}")
    
    def fix_merge_conflicts(self, mr_iid: int, timeout=300, progress_callback=None) -> bool:
        """Fix merge conflicts with NDO/Terraform awareness and timeout support"""
        self.temp_dir = tempfile.mkdtemp(prefix='mr_ndo_')
        self.timeout = timeout
        self.progress_callback = progress_callback
        logger.info(f"\nWorking directory: {self.temp_dir}")
        
        try:
            mr = self.project.mergerequests.get(mr_iid)
            source_branch = mr.source_branch
            target_branch = mr.target_branch
            
            # Get MR author information for git commits
            mr_author_name = mr.author.get('name', 'MR Author')
            mr_author_email = mr.author.get('username', 'mrauthor') + '@gitlab.local'
            
            repo_url = self.config.get('gitlab_url', 'https://gitlab.allianzcaf')
            project_path = self.config.get('gitlab_project_id', 'nac/nac-eu-ndo')
            
            logger.info(f"Cloning repository (this may take a moment)...")
            
            # Get authentication token from multiple sources
            token = (os.getenv('CI_JOB_TOKEN') or 
                    os.getenv('GITLAB_PRIVATE_TOKEN') or 
                    os.getenv('GITLAB_TOKEN') or 
                    self.config.get('gitlab_token'))
            
            if not token:
                logger.error("No authentication token found!")
                return False
            
            # Build complete repository URL with authentication
            # Format: https://oauth2:TOKEN@gitlab.allianzcaf/nac/nac-eu-ndo.git
            if 'https://' in repo_url:
                base_url = repo_url.replace('https://', f'https://oauth2:{token}@')
            else:
                base_url = f'https://oauth2:{token}@{repo_url}'
            
            # Ensure we have the full path
            if not base_url.endswith('.git'):
                auth_url = f"{base_url}/{project_path}.git"
            else:
                auth_url = base_url
            
            # Disable SSL verification for git operations
            os.environ['GIT_SSL_NO_VERIFY'] = '1'
            
            # Set git to non-interactive mode (prevent hanging)
            os.environ['GIT_EDITOR'] = 'true'  # Use 'true' command (does nothing, exits immediately)
            os.environ['GIT_TERMINAL_PROMPT'] = '0'  # Disable prompts
            
            logger.info(f"Cloning from: {repo_url}/{project_path}.git")
            
            self.repo = git.Repo.clone_from(
                auth_url,
                self.temp_dir,
                branch=source_branch,
                no_single_branch=True
            )
            logger.info(f"✓ Repository cloned")
            
            # Configure git with MR author information
            self.repo.git.config('user.email', mr_author_email)
            self.repo.git.config('user.name', mr_author_name)
            logger.info(f"Git configured with author: {mr_author_name} <{mr_author_email}>")
            
            # Detect workspace
            logger.info(f"\nDetecting workspace...")
            workspace = self._detect_workspace()
            if workspace:
                logger.info(f"✓ Detected workspace: {workspace}")
                self.report['workspace'] = workspace
            
            # Fetch branches
            logger.info(f"Fetching branches...")
            self.repo.remotes.origin.fetch(source_branch)
            self.repo.remotes.origin.fetch(target_branch)
            logger.info(f"✓ Fetched")
            
            # Attempt rebase
            logger.info(f"\nAttempting rebase...")
            return self._rebase_and_resolve(source_branch, target_branch, self.progress_callback)
        
        except Exception as e:
            logger.error(f"Error fixing conflicts: {e}")
            self.report['result'] = 'FAILED'
            return False
        
        finally:
            if self.temp_dir and os.path.exists(self.temp_dir):
                try:
                    shutil.rmtree(self.temp_dir)
                    logger.info(f"Cleaned up temporary directory")
                except Exception as e:
                    logger.warning(f"Failed to clean up: {e}")
    
    def _detect_workspace(self) -> Optional[str]:
        """Detect which NDO workspace this MR is for"""
        try:
            # Check for terraform files in workspace structure
            workspaces = self.config.get('workspaces', [])
            
            for file in self.repo.index.commit().tree.traverse():
                if file.path.endswith('.tf'):
                    # Extract workspace from path like: terraform/schema_AAT/main.tf
                    parts = file.path.split('/')
                    for part in parts:
                        if part.startswith('schema_') and part in workspaces:
                            return part
        except:
            pass
        return None
    
    def _detect_conflicting_files(self) -> List[str]:
        """Detect all files currently in merge conflict state"""
        try:
            status_output = self.repo.git.status(porcelain=True)
            conflicting_files = []
            
            for line in status_output.split('\n'):
                if not line.strip():
                    continue
                
                # Merge conflict markers: 'UU', 'DD', 'AA', 'AU', 'UA', 'DU', 'UD', 'AD', 'DA'
                if line[:2] in ['UU', 'DD', 'AA', 'AU', 'UA', 'DU', 'UD', 'AD', 'DA']:
                    file_path = line[3:].strip()
                    conflicting_files.append(file_path)
            
            return conflicting_files
        
        except Exception as e:
            logger.error(f"Error detecting conflicts: {e}")
            return []

    def _rebase_and_resolve(self, source_branch: str, target_branch: str, progress_callback=None) -> bool:
        """
        Execute rebase with multi-round conflict resolution and progress support.
        Handles MRs with multiple commits that each have conflicts.
        Timeout is handled at the GUI thread level, not per-command.
        """
        try:
            self.repo.git.checkout(source_branch)
            logger.info(f"Checked out: {source_branch}")
            
            attempt = 0
            max_attempts = 10  # Safety limit to prevent infinite loops
            total_resolved = 0
            
            while attempt < max_attempts:
                attempt += 1
                
                # Check if cancellation was requested
                if self.cancel_flag:
                    logger.warning("⚠️  Cancellation requested - aborting rebase")
                    try:
                        self.repo.git.rebase('--abort')
                    except:
                        pass
                    self.report['result'] = 'CANCELLED'
                    return False
                
                # Send progress update to GUI
                progress_msg = f"Rebase attempt {attempt}/{max_attempts}"
                if progress_callback:
                    try:
                        progress_callback(progress_msg)
                    except Exception as e:
                        logger.debug(f"Progress callback error: {e}")
                
                try:
                    if attempt == 1:
                        # Initial rebase attempt
                        logger.info(f"\n{progress_msg}...")
                        logger.info(f"Rebasing {source_branch} onto origin/{target_branch}...")
                        self.repo.git.rebase(f'origin/{target_branch}')
                    else:
                        # Continue rebase after resolving conflicts
                        logger.info(f"\n{progress_msg}...")
                        logger.info(f"Continuing rebase...")
                        self.repo.git.rebase('--continue')
                    
                    # If we reach here, rebase succeeded
                    logger.info("✓ Rebase completed successfully!")
                    
                    # Force push the rebased branch
                    logger.info(f"\nForce pushing to {source_branch}...")
                    self.repo.remotes.origin.push(source_branch, force=True)
                    logger.info(f"✓ Force pushed")
                    
                    # Update report
                    if total_resolved > 0:
                        self.report['actions_taken'].append(f'Resolved {total_resolved} conflicting files across {attempt-1} conflict rounds')
                        self.report['result'] = 'SUCCESS'
                    else:
                        self.report['actions_taken'].append('Rebase successful without conflicts')
                        self.report['result'] = 'REBASE_SUCCESS'
                    
                    self.report['actions_taken'].append(f'Force pushed {source_branch}')
                    return True
                
                except git.exc.GitCommandError as e:
                    # Rebase hit conflicts - detect and resolve them
                    conflicting_files = self._detect_conflicting_files()
                    
                    if not conflicting_files:
                        # Error occurred but no conflicts - real error
                        error_str = str(e)
                        if 'No rebase in progress' in error_str or 'nothing to commit' in error_str:
                            # Edge case: rebase completed but git returned error
                            logger.info("Rebase already completed")
                            try:
                                self.repo.remotes.origin.push(source_branch, force=True)
                                self.report['actions_taken'].append(f'Resolved {total_resolved} conflicting files')
                                self.report['actions_taken'].append(f'Force pushed {source_branch}')
                                self.report['result'] = 'SUCCESS'
                                return True
                            except Exception as push_error:
                                logger.error(f"Failed to push: {push_error}")
                                return False
                        else:
                            logger.error(f"✗ Rebase failed without conflicts: {str(e)}")
                            self.repo.git.rebase('--abort')
                            return False
                    
                    # Log conflict detection
                    logger.warning(f"⚠️  Conflict round {attempt} detected with {len(conflicting_files)} file(s)")
                    for f in conflicting_files:
                        logger.info(f"   • {f}")
                    
                    # Detect file types
                    self.detect_file_types(conflicting_files)
                    
                    # Resolve conflicts
                    logger.info(f"\nResolving {len(conflicting_files)} conflicts...")
                    resolved_count = self._resolve_conflicts_in_round(conflicting_files, source_branch, target_branch)
                    
                    if resolved_count < 0:
                        # Resolution failed
                        logger.error("✗ Failed to resolve conflicts")
                        self.repo.git.rebase('--abort')
                        self.report['result'] = 'RESOLUTION_FAILED'
                        return False
                    
                    total_resolved += resolved_count
                    logger.info(f"✓ Resolved {resolved_count} file(s) in round {attempt}")
                    
                    # Loop continues to next iteration for 'rebase --continue'
            
            # Max attempts exceeded
            logger.error(f"✗ Rebase failed after {max_attempts} conflict rounds")
            self.report['result'] = 'MAX_ATTEMPTS_EXCEEDED'
            try:
                self.repo.git.rebase('--abort')
            except:
                pass
            return False
        
        except Exception as e:
            logger.error(f"Rebase error: {e}")
            try:
                self.repo.git.rebase('--abort')
            except:
                pass
            return False
    
    def _resolve_conflicts_in_round(self, conflicting_files: List[str], 
                                     source_branch: str, target_branch: str) -> int:
        """
        Resolve conflicts for one round of rebase.
        Returns: Number of files resolved, or -1 on failure
        """
        strategy = self.config.get('conflict_resolution', {}).get('strategy', 'theirs')
        ignore_patterns = self.config.get('conflict_resolution', {}).get('ignore_files', [])
        
        logger.info(f"Strategy: {strategy}")
        
        try:
            resolved = 0
            skipped = 0
            failed = 0
            
            for file_path in conflicting_files:
                # Check if file should be ignored
                should_ignore = False
                for pattern in ignore_patterns:
                    if pattern.replace('*', '') in file_path or pattern in file_path:
                        should_ignore = True
                        logger.warning(f"  ⊘ {file_path} - SKIPPED (matches ignore pattern)")
                        self.report['warnings'].append(f"Skipped {file_path} - requires manual review")
                        skipped += 1
                        break
                
                if should_ignore:
                    continue
                
                try:
                    if strategy == 'ours':
                        # During REBASE: 'ours' = target branch (base)
                        self.repo.git.checkout('--ours', file_path)
                        logger.info(f"  ✓ {file_path} - kept target (base)")
                    
                    elif strategy == 'theirs':
                        # During REBASE: 'theirs' = source branch (MR changes) ✓
                        self.repo.git.checkout('--theirs', file_path)
                        logger.info(f"  ✓ {file_path} - kept source (MR changes)")
                    
                    # Stage the file using git add (more reliable than index.add)
                    self.repo.git.add(file_path)
                    logger.info(f"  ✓ Staged: {file_path}")
                    resolved += 1
                
                except Exception as e:
                    logger.error(f"  ✗ Error resolving {file_path}: {e}")
                    failed += 1
            
            if failed > 0:
                logger.error(f"Failed to resolve {failed} files")
                return -1
            
            return resolved
        
        except Exception as e:
            logger.error(f"Conflict resolution error: {e}")
            return -1
    
    def post_update_to_mr(self, mr_iid: int) -> bool:
        """Post update comment to MR"""
        try:
            mr = self.project.mergerequests.get(mr_iid)
            
            if self.report['result'] == 'SUCCESS':
                comment = f"""## ✅ Merge Conflicts Resolved - NDO/Terraform Aware

**Environment:** NDO/Terraform Workspace
**Action Taken:** Automatic rebase and conflict resolution

**Changes Made:**
"""
                for action in self.report['actions_taken']:
                    comment += f"- {action}\n"
                
                if self.report.get('workspace'):
                    comment += f"\n**Workspace:** `{self.report['workspace']}`\n"
                
                if self.report['terraform_files_detected']:
                    comment += f"\n**Terraform Files Detected & Handled:**\n"
                    for file in self.report['terraform_files_detected']:
                        comment += f"- `{file}`\n"
                
                if self.report['ndo_files_detected']:
                    comment += f"\n**NDO Schema Files Handled:**\n"
                    for file in self.report['ndo_files_detected']:
                        comment += f"- `{file}`\n"
                
                if self.report['warnings']:
                    comment += f"\n**⚠️ Warnings (Manual Review Recommended):**\n"
                    for warning in self.report['warnings']:
                        comment += f"- {warning}\n"
                
                comment += f"""
**Strategy Used:** `{self.config.get('conflict_resolution', {}).get('strategy', 'theirs')}`

✅ Conflicts resolved
✅ Rebased onto `{self.report['merge_request']['target_branch']}`
✅ Ready to merge

**Next Steps:**
1. Review the changes in this MR
2. Run CI/CD pipeline tests
3. Merge when ready

*Auto-fixed by NDO/Terraform Conflict Resolver - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
            
            elif self.report['result'] == 'REBASE_SUCCESS':
                comment = f"""## ✅ No Conflicts - Ready to Merge

Your merge request is up-to-date with `{self.report['merge_request']['target_branch']}` and has no conflicts.

**You can merge this MR safely!**

*Auto-validated by NDO Conflict Resolver - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
            
            else:
                comment = f"""## ⚠️ Automatic Resolution Incomplete

**Status:** {self.report['result']}

**Issues Found:**
"""
                for issue in self.report['issues_found']:
                    comment += f"- {issue}\n"
                
                if self.report['warnings']:
                    comment += f"\n**Warnings:**\n"
                    for warning in self.report['warnings']:
                        comment += f"- {warning}\n"
                
                comment += f"""

**Manual Resolution Required:**
```bash
git fetch origin
git rebase origin/{self.report['merge_request']['target_branch']}
# Fix conflicts in your editor
git add .
git rebase --continue
git push origin {self.report['merge_request']['source_branch']} --force
```

**Important for Terraform:**
- Be careful with `.terraform` files
- `.tfstate` files should not be in git
- Use terraform workspace for state management

*Please resolve manually and push to update this MR*
"""
            
            mr.notes.create({'body': comment})
            logger.info(f"✓ Posted update to MR #{mr_iid}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to post update: {e}")
            return False
    
    def save_report(self, mr_iid: int):
        """Save detailed JSON report"""
        filename = f"mr_{mr_iid}_ndo_fix_report.json"
        try:
            with open(filename, 'w') as f:
                json.dump(self.report, f, indent=2)
            logger.info(f"Report saved: {filename}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
    
    def run(self, mr_url: str = None, mr_iid: int = None) -> int:
        """Main execution"""
        logger.info("\n" + "="*70)
        logger.info("NDO/TERRAFORM MERGE REQUEST AUTO-FIX")
        logger.info("="*70)
        
        # Extract MR ID from URL
        if mr_url and not mr_iid:
            match = re.search(r'/merge_requests/(\d+)', mr_url)
            if match:
                mr_iid = int(match.group(1))
                logger.info(f"Extracted MR ID: {mr_iid}")
        
        if not mr_iid:
            logger.error("No MR ID provided")
            return 1
        
        # Execute pipeline
        if not self.authenticate():
            return 1
        
        if not self.get_mr_details(mr_iid):
            return 1
        
        logger.info("\nAttempting to fix merge conflicts...")
        self.fix_merge_conflicts(mr_iid)
        
        # Post results
        self.post_update_to_mr(mr_iid)
        self.save_report(mr_iid)
        
        # Summary
        print("\n" + "="*70)
        print("NDO/TERRAFORM AUTO-FIX RESULT")
        print("="*70)
        print(f"MR: #{self.report['merge_request'].get('iid')}")
        print(f"Status: {self.report['result']}")
        print(f"Issues Found: {len(self.report['issues_found'])}")
        print(f"Actions Taken: {len(self.report['actions_taken'])}")
        for action in self.report['actions_taken']:
            print(f"  ✓ {action}")
        if self.report['warnings']:
            print(f"Warnings: {len(self.report['warnings'])}")
            for warning in self.report['warnings']:
                print(f"  ⚠️ {warning}")
        print("="*70 + "\n")
        
        return 0 if self.report['result'] in ['SUCCESS', 'REBASE_SUCCESS'] else 1


def main():
    parser = argparse.ArgumentParser(
        description='Auto-fix GitLab MR conflicts (NDO/Terraform optimized)'
    )
    parser.add_argument('--config', default='config.yaml', help='Config file')
    parser.add_argument('--mr-url', help='MR URL')
    parser.add_argument('--mr-iid', type=int, help='MR internal ID')
    
    args = parser.parse_args()
    
    fixer = NDOMRConflictAutoFixer(args.config)
    exit_code = fixer.run(args.mr_url, args.mr_iid)
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
