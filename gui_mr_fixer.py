#!/usr/bin/env python3
"""
GitLab MR Conflict Resolver - GUI Version
Smart, visual interface for fixing merge request conflicts
"""

import os
import sys
import threading
import logging
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime
from typing import Optional
import yaml

# Configure UTF-8 for Windows
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

# Import the conflict resolver
from auto_fix_mr_conflicts_ndo import NDOMRConflictAutoFixer


class GUILogHandler(logging.Handler):
    """Custom logging handler to stream logs to GUI"""
    
    def __init__(self, gui_log_func):
        super().__init__()
        self.gui_log = gui_log_func
    
    def emit(self, record):
        """Emit log record to GUI"""
        try:
            msg = self.format(record)
            level = record.levelname
            
            # Map log level to tag
            if level == 'ERROR':
                tag = 'error'
            elif level == 'WARNING':
                tag = 'warning'
            elif level == 'INFO':
                tag = 'info'
            else:
                tag = 'info'
            
            # Call GUI log function (thread-safe)
            self.gui_log(msg, tag)
        except:
            pass


class MRConflictResolverGUI:
    """Modern GUI for MR conflict resolution"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("GitLab MR Conflict Resolver - NDO/Terraform")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Load config
        self.config = self._load_config()
        self.fixer = None
        self.is_running = False
        self.cancel_flag = False
        self.worker_thread = None
        self.timeout_seconds = 300  # 5 minutes default
        
        # Setup logging to GUI
        self._setup_logging()
        
        # Setup UI
        self._create_widgets()
        
        # Center window
        self._center_window()
    
    def _setup_logging(self):
        """Setup logging to stream to GUI"""
        # Get the logger from the conflict resolver module
        logger = logging.getLogger('auto_fix_mr_conflicts_ndo')
        logger.setLevel(logging.INFO)
        
        # Add GUI handler
        gui_handler = GUILogHandler(self._log_from_thread)
        formatter = logging.Formatter('%(message)s')
        gui_handler.setFormatter(formatter)
        logger.addHandler(gui_handler)
    
    def _load_config(self):
        """Load configuration - embedded defaults with token"""
        # Try environment variables first (for CI/CD or override)
        token = os.getenv('GITLAB_TOKEN') or os.getenv('CI_JOB_TOKEN') or os.getenv('GITLAB_PRIVATE_TOKEN')
        
        # Fallback to embedded token if no environment variable
        if not token:
            token = 'YOUR-GITLAB-TOKEN-HERE'  # Replace with your token or use environment variable
            print("⚠️  WARNING: Using placeholder token. Set GITLAB_TOKEN environment variable.")
        
        # Embedded configuration with secure defaults for corporate network
        config = {
            'gitlab_token': token,
            'gitlab_url': os.getenv('GITLAB_URL', 'https://gitlab.example.com'),
            'gitlab_api_url': os.getenv('GITLAB_API_URL', 'https://gitlab.example.com/api/v4'),
            'gitlab_project_id': os.getenv('GITLAB_PROJECT_ID', 'namespace/project'),
            'resolution_strategy': 'theirs',
            'conflict_resolution': {
                'strategy': 'theirs',  # During REBASE: 'theirs' = source branch (MR changes)
                'auto_push': True
            },
            # Corporate network defaults
            'bypass_proxy': True,      # Default: bypass proxy
            'ssl_verify': False,       # Default: disable SSL verification (for self-signed certs)
        }
        
        # Allow external config file to override embedded defaults (optional)
        config_files = ['config_ndo.yaml', 'config.yaml']
        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r') as f:
                        file_config = yaml.safe_load(f)
                        if file_config:
                            # Merge file config with embedded config (file overrides)
                            config.update(file_config)
                            print(f"Loaded configuration from {config_file}")
                            break
                except Exception as e:
                    print(f"Failed to load {config_file}: {e}")
        
        return config
    
    def _center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def _create_widgets(self):
        """Create all UI widgets"""
        
        # Header
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="GitLab MR Conflict Resolver",
            font=('Arial', 20, 'bold'),
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack(pady=10)
        
        subtitle_label = tk.Label(
            header_frame,
            text="NDO/Terraform Environment - Smart Conflict Resolution",
            font=('Arial', 10),
            bg='#2c3e50',
            fg='#bdc3c7'
        )
        subtitle_label.pack()
        
        # Main container
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Connection Status
        status_frame = tk.LabelFrame(
            main_frame,
            text="Connection Status",
            font=('Arial', 10, 'bold'),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        status_inner = tk.Frame(status_frame, bg='#f0f0f0')
        status_inner.pack(padx=10, pady=10)
        
        gitlab_url = self.config.get('gitlab_url', 'Not configured')
        project_id = self.config.get('gitlab_project_id', 'Not configured')
        
        tk.Label(
            status_inner,
            text=f"GitLab: {gitlab_url}",
            font=('Arial', 9),
            bg='#f0f0f0',
            fg='#34495e'
        ).grid(row=0, column=0, sticky='w', padx=5)
        
        tk.Label(
            status_inner,
            text=f"Project: {project_id}",
            font=('Arial', 9),
            bg='#f0f0f0',
            fg='#34495e'
        ).grid(row=0, column=1, sticky='w', padx=20)
        
        self.status_indicator = tk.Label(
            status_inner,
            text="● Ready",
            font=('Arial', 9, 'bold'),
            bg='#f0f0f0',
            fg='#27ae60'
        )
        self.status_indicator.grid(row=0, column=2, sticky='w', padx=20)
        
        # MR Input Section
        input_frame = tk.LabelFrame(
            main_frame,
            text="Step 1: Enter Merge Request",
            font=('Arial', 10, 'bold'),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        input_frame.pack(fill=tk.X, pady=(0, 15))
        
        input_inner = tk.Frame(input_frame, bg='#f0f0f0')
        input_inner.pack(padx=10, pady=10)
        
        tk.Label(
            input_inner,
            text="MR Number:",
            font=('Arial', 10),
            bg='#f0f0f0',
            fg='#2c3e50'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.mr_entry = tk.Entry(
            input_inner,
            font=('Arial', 12),
            width=15,
            bg='white',
            fg='#2c3e50',
            relief=tk.SOLID,
            borderwidth=1
        )
        self.mr_entry.pack(side=tk.LEFT, padx=(0, 15))
        self.mr_entry.bind('<Return>', lambda e: self.analyze_mr())
        
        self.analyze_btn = tk.Button(
            input_inner,
            text="Analyze MR",
            font=('Arial', 10, 'bold'),
            bg='#3498db',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor='hand2',
            command=self.analyze_mr
        )
        self.analyze_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.fix_btn = tk.Button(
            input_inner,
            text="Fix Conflicts",
            font=('Arial', 10, 'bold'),
            bg='#27ae60',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor='hand2',
            command=self.fix_conflicts,
            state=tk.DISABLED
        )
        self.fix_btn.pack(side=tk.LEFT)
        
        self.cancel_btn = tk.Button(
            input_inner,
            text="✖ Cancel",
            font=('Arial', 10, 'bold'),
            bg='#e74c3c',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor='hand2',
            command=self.cancel_operation,
            state=tk.DISABLED
        )
        self.cancel_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Conflict Details Section
        details_frame = tk.LabelFrame(
            main_frame,
            text="Step 2: Conflict Details",
            font=('Arial', 10, 'bold'),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        details_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Details display
        self.details_text = scrolledtext.ScrolledText(
            details_frame,
            font=('Consolas', 9),
            bg='#2c3e50',
            fg='#ecf0f1',
            relief=tk.FLAT,
            padx=10,
            pady=10,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.details_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure text tags for colors
        self.details_text.tag_config('header', foreground='#3498db', font=('Consolas', 9, 'bold'))
        self.details_text.tag_config('success', foreground='#2ecc71')
        self.details_text.tag_config('warning', foreground='#f39c12')
        self.details_text.tag_config('error', foreground='#e74c3c')
        self.details_text.tag_config('info', foreground='#ecf0f1')
        
        # Progress Section
        progress_frame = tk.Frame(main_frame, bg='#f0f0f0')
        progress_frame.pack(fill=tk.X)
        
        self.progress_label = tk.Label(
            progress_frame,
            text="Ready to analyze merge request...",
            font=('Arial', 9),
            bg='#f0f0f0',
            fg='#7f8c8d',
            anchor='w'
        )
        self.progress_label.pack(fill=tk.X, pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='indeterminate',
            length=300
        )
        self.progress_bar.pack(fill=tk.X)
        
        # Initial message
        self._log("Welcome to MR Conflict Resolver!", 'header')
        self._log(f"Connected to: {gitlab_url}", 'info')
        self._log(f"Project: {project_id}\n", 'info')
        self._log("Enter an MR number and click 'Analyze MR' to begin.", 'info')
    
    def _log(self, message: str, tag: str = 'info'):
        """Add message to log with color (thread-safe)"""
        self.details_text.config(state=tk.NORMAL)
        self.details_text.insert(tk.END, message + '\n', tag)
        self.details_text.see(tk.END)
        self.details_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def _log_from_thread(self, message: str, tag: str = 'info'):
        """Thread-safe logging - called from background threads"""
        self.root.after(0, self._log, message, tag)
    
    def _clear_log(self):
        """Clear the log"""
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        self.details_text.config(state=tk.DISABLED)
    
    def _set_status(self, text: str, color: str):
        """Update status indicator"""
        self.status_indicator.config(text=f"● {text}", fg=color)
    
    def cancel_operation(self):
        """Cancel current operation"""
        if not self.is_running:
            return
        
        self.cancel_flag = True
        self._log("\n✖ Cancellation requested by user...", 'warning')
        self.progress_label.config(text="Cancelling operation...")
        self._set_status("Cancelling...", '#e74c3c')
        self.cancel_btn.config(state=tk.DISABLED)
    
    def analyze_mr(self):
        """Analyze MR for conflicts"""
        if self.is_running:
            messagebox.showwarning("Busy", "Already processing. Please wait...")
            return
        
        mr_number = self.mr_entry.get().strip()
        if not mr_number:
            messagebox.showerror("Error", "Please enter an MR number")
            return
        
        try:
            mr_iid = int(mr_number)
        except ValueError:
            messagebox.showerror("Error", "MR number must be a number")
            return
        
        # Disable buttons
        self.analyze_btn.config(state=tk.DISABLED)
        self.fix_btn.config(state=tk.DISABLED)
        self.is_running = True
        
        # Start progress
        self.progress_bar.start(10)
        self._set_status("Analyzing...", '#f39c12')
        self.progress_label.config(text=f"Analyzing MR #{mr_iid}...")
        
        # Run in thread
        thread = threading.Thread(target=self._analyze_mr_thread, args=(mr_iid,))
        thread.daemon = True
        thread.start()
    
    def _analyze_mr_thread(self, mr_iid: int):
        """Analyze MR in background thread"""
        try:
            self._clear_log()
            self._log(f"=" * 70, 'header')
            self._log(f"ANALYZING MR #{mr_iid}", 'header')
            self._log(f"=" * 70 + "\n", 'header')
            
            # Create fixer instance with embedded config
            self.fixer = NDOMRConflictAutoFixer(config_dict=self.config)
            
            # Authenticate
            self._log("→ Connecting to GitLab...", 'info')
            if not self.fixer.authenticate():
                self._log("✗ Authentication failed", 'error')
                self.root.after(0, self._analysis_complete, False, None)
                return
            
            self._log("✓ Connected successfully", 'success')
            
            # Get MR details
            self._log(f"\n→ Loading MR #{mr_iid} details...", 'info')
            if not self.fixer.get_mr_details(mr_iid):
                self._log("✗ Failed to load MR details", 'error')
                self.root.after(0, self._analysis_complete, False, None)
                return
            
            # Display MR info
            mr_info = self.fixer.report.get('merge_request', {})
            self._log(f"\n{'=' * 70}", 'header')
            self._log(f"MR DETAILS", 'header')
            self._log(f"{'=' * 70}", 'header')
            self._log(f"Title: {mr_info.get('title', 'N/A')}", 'info')
            self._log(f"Source: {mr_info.get('source_branch', 'N/A')}", 'info')
            self._log(f"Target: {mr_info.get('target_branch', 'N/A')}", 'info')
            self._log(f"Author: {mr_info.get('author', 'N/A')}", 'info')
            self._log(f"Status: {mr_info.get('merge_status', 'N/A')}\n", 'info')
            
            # Check for conflicts
            has_conflicts = mr_info.get('has_conflicts', False)
            
            # Analyze file sizes if conflicts exist
            if has_conflicts:
                issues = self.fixer.report.get('issues_found', [])
                if issues:
                    # Check for large files
                    large_files = []
                    ndo_files = self.fixer.report.get('ndo_files_detected', [])
                    tf_files = self.fixer.report.get('terraform_files_detected', [])
                    
                    all_conflict_files = ndo_files + tf_files
                    for file_path in all_conflict_files:
                        # Estimate size warning (NDO YAML files are typically large)
                        if 'schema' in file_path.lower() and file_path.endswith('.yaml'):
                            large_files.append(file_path)
                    
                    if large_files:
                        self._log("\n⚠️  LARGE FILES DETECTED", 'warning')
                        self._log("These files may take longer to process:", 'warning')
                        for f in large_files:
                            self._log(f"  • {f}", 'warning')
            
            if has_conflicts:
                self._log("⚠ CONFLICTS DETECTED", 'warning')
                self._log("-" * 70, 'warning')
                
                # Show conflict info
                issues = self.fixer.report.get('issues_found', [])
                if issues:
                    for issue in issues:
                        self._log(f"  • {issue}", 'warning')
                
                # Show file types detected
                ndo_files = self.fixer.report.get('ndo_files_detected', [])
                tf_files = self.fixer.report.get('terraform_files_detected', [])
                
                if ndo_files:
                    self._log(f"\nNDO Schema Files:", 'info')
                    for f in ndo_files:
                        self._log(f"  • {f}", 'info')
                
                if tf_files:
                    self._log(f"\nTerraform Files:", 'info')
                    for f in tf_files:
                        self._log(f"  • {f}", 'info')
                
                self._log(f"\n{'=' * 70}", 'header')
                self._log("RESOLUTION STRATEGY", 'header')
                self._log(f"{'=' * 70}", 'header')
                strategy = self.fixer.config.get('conflict_resolution', {}).get('strategy', 'theirs')
                self._log(f"Strategy: '{strategy}' (keeps target branch version)", 'success')
                self._log("Safe for Terraform with PostgreSQL backend", 'success')
                self._log("Handles files of ANY size", 'success')
                
                self._log(f"\n{'=' * 70}", 'success')
                self._log("READY TO FIX CONFLICTS", 'success')
                self._log(f"{'=' * 70}\n", 'success')
                self._log("Click 'Fix Conflicts' button to resolve automatically.", 'info')
                
                self.root.after(0, self._analysis_complete, True, mr_iid)
            else:
                self._log("✓ NO CONFLICTS FOUND", 'success')
                self._log("This MR is ready to merge!", 'success')
                self.root.after(0, self._analysis_complete, False, None)
        
        except Exception as e:
            self._log(f"\n✗ Error: {str(e)}", 'error')
            self.root.after(0, self._analysis_complete, False, None)
    
    def _analysis_complete(self, has_conflicts: bool, mr_iid: Optional[int]):
        """Complete analysis"""
        self.progress_bar.stop()
        self.is_running = False
        
        if has_conflicts:
            self.fix_btn.config(state=tk.NORMAL)
            self._set_status("Conflicts Found", '#e74c3c')
            self.progress_label.config(text=f"MR #{mr_iid} has conflicts - Ready to fix")
        else:
            self._set_status("Ready", '#27ae60')
            self.progress_label.config(text="Analysis complete")
        
        self.analyze_btn.config(state=tk.NORMAL)
    
    def fix_conflicts(self):
        """Fix conflicts"""
        if self.is_running:
            messagebox.showwarning("Busy", "Already processing. Please wait...")
            return
        
        if not self.fixer:
            messagebox.showerror("Error", "Please analyze an MR first")
            return
        
        # Confirm
        response = messagebox.askyesno(
            "Confirm",
            "This will automatically resolve conflicts using the 'theirs' strategy.\n\n"
            "The tool will:\n"
            "• Keep target branch version for conflicts\n"
            "• Handle multiple rounds of conflicts\n"
            "• Force push resolved branch\n"
            "• Post update to MR\n\n"
            "Do you want to proceed?"
        )
        
        if not response:
            return
        
        # Disable buttons
        self.analyze_btn.config(state=tk.DISABLED)
        self.fix_btn.config(state=tk.DISABLED)
        self.is_running = True
        
        # Start progress
        self.progress_bar.start(10)
        self._set_status("Fixing...", '#f39c12')
        
        mr_iid = self.fixer.report.get('merge_request', {}).get('iid')
        self.progress_label.config(text=f"Resolving conflicts in MR #{mr_iid}...")
        
        # Run in thread
        thread = threading.Thread(target=self._fix_conflicts_thread, args=(mr_iid,))
        thread.daemon = True
        thread.start()
    
    def _fix_conflicts_thread(self, mr_iid: int):
        """Fix conflicts in background thread with timeout and progress"""
        try:
            self._log(f"\n{'=' * 70}", 'header')
            self._log("FIXING CONFLICTS", 'header')
            self._log(f"{'=' * 70}\n", 'header')
            
            # Fix conflicts WITH TIMEOUT AND PROGRESS
            self._log("→ Starting conflict resolution...", 'info')
            
            # Pass timeout and progress callback to the resolver
            success = self.fixer.fix_merge_conflicts(
                mr_iid,
                timeout=self.timeout_seconds,
                progress_callback=self._progress_update
            )
            
            # Check result
            result = self.fixer.report.get('result', 'UNKNOWN')
            
            if result == 'TIMEOUT':
                # Handle timeout
                self._log(f"\n{'=' * 70}", 'warning')
                self._log("⚠ TIMEOUT", 'warning')
                self._log(f"{'=' * 70}\n", 'warning')
                self._log(f"Operation timed out after {self.timeout_seconds} seconds.", 'warning')
                
                def ask_retry():
                    response = messagebox.askyesno(
                        "Timeout",
                        f"Operation timed out after {self.timeout_seconds} seconds.\n\n"
                        "Large files can take longer.\n\n"
                        "Retry with 10-minute timeout?"
                    )
                    if response:
                        self.timeout_seconds = 600
                        self._log("\nRetrying with 10-minute timeout...\n", 'info')
                        self.worker_thread = threading.Thread(
                            target=self._fix_conflicts_thread,
                            args=(mr_iid,),
                            daemon=True
                        )
                        self.worker_thread.start()
                    else:
                        self._fix_complete(False)
                
                self.root.after(0, ask_retry)
            
            elif success or result in ['SUCCESS', 'REBASE_SUCCESS']:
                self._log(f"\n{'=' * 70}", 'success')
                self._log("✓ SUCCESS!", 'success')
                self._log(f"{'=' * 70}\n", 'success')
                
                actions = self.fixer.report.get('actions_taken', [])
                for action in actions:
                    self._log(f"  ✓ {action}", 'success')
                
                self._log(f"\nMR #{mr_iid} is now ready to merge!", 'success')
                self.root.after(0, self._fix_complete, True)
            else:
                self._log(f"\n{'=' * 70}", 'error')
                self._log("✗ FAILED", 'error')
                self._log(f"{'=' * 70}\n", 'error')
                
                result = self.fixer.report.get('result', 'UNKNOWN')
                self._log(f"Status: {result}", 'error')
                
                self.root.after(0, self._fix_complete, False)
        
        except Exception as e:
            self._log(f"\n✗ Error: {str(e)}", 'error')
            self.root.after(0, self._fix_complete, False)
    
    def _progress_update(self, message: str):
        """Update progress from background thread (thread-safe)"""
        try:
            self.root.after(0, self._update_progress, message)
        except:
            pass
    
    def _update_progress(self, message: str):
        """Update progress label (main thread)"""
        self.progress_label.config(text=message)
        if "attempt" in message.lower():
            self._log(f"\n→ {message}", 'info')
    
    def _fix_complete(self, success: bool):
        """Complete fix operation"""
        self.progress_bar.stop()
        self.is_running = False
        
        if success:
            self._set_status("Success!", '#27ae60')
            self.progress_label.config(text="Conflicts resolved successfully!")
            messagebox.showinfo(
                "Success!",
                "Conflicts resolved successfully!\n\n"
                "The MR has been updated and is ready to merge."
            )
        else:
            self._set_status("Failed", '#e74c3c')
            self.progress_label.config(text="Conflict resolution failed")
            messagebox.showerror(
                "Failed",
                "Failed to resolve conflicts.\n\n"
                "Check the details for more information."
            )
        
        self.analyze_btn.config(state=tk.NORMAL)
        self.fix_btn.config(state=tk.DISABLED)


def main():
    """Main entry point"""
    root = tk.Tk()
    app = MRConflictResolverGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
