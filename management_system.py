#!/usr/bin/env python3
"""
Role-Based Management System
Supports Admin, Merchant/Client, and PCS roles with batch operations
"""

import os
import sys
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

# Role permissions
PERMISSIONS = {
    'Admin': {
        'delete_users': True,
        'delete_data': True,
        'delete_temp_files': True,
        'modify_permissions': True,
        'view_logs': True,
        'batch_delete': True,
        'cleanup_system': True,
        'create_files': True,
        'batch_create_files': True,
        'check_system': True,
        'view_file_stats': True,
        'delete_files': True
    },
    'Merchant': {
        'delete_users': False,
        'delete_data': True,  # Only own data
        'delete_temp_files': True,
        'modify_permissions': False,
        'view_logs': False,
        'batch_delete': True,
        'cleanup_system': False,
        'create_files': True,
        'batch_create_files': True,
        'check_system': True,
        'view_file_stats': True,
        'delete_files': True
    },
    'PCS': {
        'delete_users': False,
        'delete_data': False,
        'delete_temp_files': True,
        'modify_permissions': False,
        'view_logs': False,
        'batch_delete': False,
        'cleanup_system': False,
        'create_files': True,
        'batch_create_files': False,
        'check_system': True,
        'view_file_stats': False,
        'delete_files': False
    }
}

# File types that can be created
FILE_TYPES = {
    'csv': {'extension': '.csv', 'template': 'id,name,value\n1,sample,100\n'},
    'json': {'extension': '.json', 'template': '{\n  "data": [\n    {"id": 1, "name": "sample"}\n  ]\n}\n'},
    'txt': {'extension': '.txt', 'template': 'Sample Text File\nCreated: {timestamp}\n'},
    'log': {'extension': '.log', 'template': '[{timestamp}] System initialized\n'},
    'config': {'extension': '.conf', 'template': '[settings]\nversion=1.0\nenabled=true\n'},
    'xml': {'extension': '.xml', 'template': '<?xml version="1.0"?>\n<root>\n  <data>Sample</data>\n</root>\n'}
}

class User:
    def __init__(self, user_id: str, name: str, role: str):
        self.user_id = user_id
        self.name = name
        self.role = role
        self.created_at = datetime.now()

    def __repr__(self):
        return f"User({self.user_id}, {self.name}, {self.role})"


class ManagementSystem:
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.current_user: User = None
        self.temp_files_dir = Path("temp_files")
        self.data_dir = Path("user_data")
        self.logs: List[str] = []
        self.setup_directories()

    def setup_directories(self):
        """Create necessary directories"""
        self.temp_files_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)

    def log_action(self, action: str, status: str = "SUCCESS"):
        """Log system actions"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {self.current_user.role if self.current_user else 'SYSTEM'} - {action} - {status}"
        self.logs.append(log_entry)
        print(log_entry)

    def check_permission(self, action: str) -> bool:
        """Check if current user has permission for action"""
        if not self.current_user:
            print(f"{Colors.RED}[ERROR] No user logged in{Colors.RESET}")
            return False
        
        if action not in PERMISSIONS[self.current_user.role]:
            print(f"{Colors.RED}[ERROR] Unknown action: {action}{Colors.RESET}")
            return False
        
        if not PERMISSIONS[self.current_user.role][action]:
            print(f"{Colors.RED}[ERROR] Permission denied: {self.current_user.role} cannot {action}{Colors.RESET}")
            self.log_action(f"DENIED: {action}", "PERMISSION_DENIED")
            return False
        
        return True

    def create_user(self, user_id: str, name: str, role: str) -> bool:
        """Create a new user"""
        # Allow first admin user to be created without login
        if len(self.users) == 0 and role == 'Admin':
            if user_id in self.users:
                print(f"{Colors.RED}[ERROR] User already exists: {user_id}{Colors.RESET}")
                return False
            
            self.users[user_id] = User(user_id, name, role)
            print(f"{Colors.GREEN}[SUCCESS] User created: {user_id} ({role}){Colors.RESET}")
            self.log_action(f"CREATE_USER: {user_id} ({role})")
            return True
        
        if not self.current_user or not self.check_permission('modify_permissions'):
            return False
        
        if user_id in self.users:
            print(f"{Colors.RED}[ERROR] User already exists: {user_id}{Colors.RESET}")
            return False
        
        if role not in PERMISSIONS:
            print(f"{Colors.RED}[ERROR] Invalid role: {role}{Colors.RESET}")
            return False
        
        self.users[user_id] = User(user_id, name, role)
        print(f"{Colors.GREEN}[SUCCESS] User created: {user_id} ({role}){Colors.RESET}")
        self.log_action(f"CREATE_USER: {user_id} ({role})")
        return True

    def login(self, user_id: str) -> bool:
        """Login as a user"""
        if user_id not in self.users:
            print(f"{Colors.RED}[ERROR] User not found: {user_id}{Colors.RESET}")
            return False
        
        self.current_user = self.users[user_id]
        print(f"{Colors.GREEN}[SUCCESS] Logged in as: {self.current_user.name} ({self.current_user.role}){Colors.RESET}")
        self.log_action(f"LOGIN")
        return True

    def logout(self):
        """Logout current user"""
        if self.current_user:
            print(f"{Colors.GREEN}[SUCCESS] Logged out: {self.current_user.name}{Colors.RESET}")
            self.log_action("LOGOUT")
            self.current_user = None

    def delete_user(self, target_user_id: str) -> bool:
        """Delete a user (Admin only)"""
        if not self.check_permission('delete_users'):
            return False
        
        if target_user_id not in self.users:
            print(f"{Colors.RED}[ERROR] User not found: {target_user_id}{Colors.RESET}")
            return False
        
        user = self.users.pop(target_user_id)
        print(f"{Colors.GREEN}[SUCCESS] User deleted: {target_user_id}{Colors.RESET}")
        self.log_action(f"DELETE_USER: {target_user_id}")
        return True

    def delete_user_data(self, target_user_id: str) -> bool:
        """Delete user data"""
        if not self.check_permission('delete_data'):
            return False
        
        # Merchant can only delete own data
        if self.current_user.role == 'Merchant' and self.current_user.user_id != target_user_id:
            print(f"{Colors.RED}[ERROR] Merchants can only delete own data{Colors.RESET}")
            return False
        
        user_data_path = self.data_dir / target_user_id
        if user_data_path.exists():
            shutil.rmtree(user_data_path)
            print(f"{Colors.GREEN}[SUCCESS] User data deleted: {target_user_id}{Colors.RESET}")
            self.log_action(f"DELETE_USER_DATA: {target_user_id}")
            return True
        else:
            print(f"{Colors.YELLOW}[INFO] No data found for user: {target_user_id}{Colors.RESET}")
            return True

    def cleanup_temp_files(self) -> int:
        """Clean up temporary files"""
        if not self.check_permission('delete_temp_files'):
            return 0
        
        count = 0
        if self.temp_files_dir.exists():
            for item in self.temp_files_dir.iterdir():
                try:
                    if item.is_file():
                        item.unlink()
                    else:
                        shutil.rmtree(item)
                    count += 1
                except Exception as e:
                    print(f"{Colors.RED}[ERROR] Failed to delete {item}: {e}{Colors.RESET}")
        
        print(f"{Colors.GREEN}[SUCCESS] Removed {count} temporary files{Colors.RESET}")
        self.log_action(f"CLEANUP_TEMP_FILES: {count} items removed")
        return count

    def cleanup_system(self) -> bool:
        """Full system cleanup (Admin only)"""
        if not self.check_permission('cleanup_system'):
            return False
        
        print(f"{Colors.YELLOW}[INFO] Starting system cleanup...{Colors.RESET}")
        temp_count = self.cleanup_temp_files()
        print(f"{Colors.GREEN}[SUCCESS] System cleanup complete{Colors.RESET}")
        self.log_action("CLEANUP_SYSTEM: Full cleanup executed")
        return True

    def batch_delete(self, targets: List[str], target_type: str = "data") -> int:
        """Delete multiple items in one command"""
        if not self.check_permission('batch_delete'):
            return 0
        
        count = 0
        for target in targets:
            if target_type == "data":
                if self.delete_user_data(target):
                    count += 1
            elif target_type == "user":
                if self.delete_user(target):
                    count += 1
        
        print(f"{Colors.GREEN}[SUCCESS] Batch deleted {count} items{Colors.RESET}")
        self.log_action(f"BATCH_DELETE: {count} {target_type}s deleted")
        return count

    def create_file(self, filename: str, file_type: str, user_id: str = None) -> bool:
        """Create file with specified type"""
        if not self.check_permission('create_files'):
            return False
        
        if file_type not in FILE_TYPES:
            print(f"{Colors.RED}[ERROR] Unsupported file type: {file_type}{Colors.RESET}")
            print(f"Supported types: {', '.join(FILE_TYPES.keys())}")
            return False
        
        # Default to current user if not specified
        if user_id is None:
            user_id = self.current_user.user_id if self.current_user else 'system'
        
        user_files_dir = self.data_dir / user_id / 'files'
        user_files_dir.mkdir(parents=True, exist_ok=True)
        
        file_info = FILE_TYPES[file_type]
        file_path = user_files_dir / f"{filename}{file_info['extension']}"
        
        # Replace timestamp in template if needed
        content = file_info['template'].replace('{timestamp}', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        try:
            file_path.write_text(content)
            print(f"{Colors.GREEN}[SUCCESS] File created: {file_path}{Colors.RESET}")
            self.log_action(f"CREATE_FILE: {filename} ({file_type})")
            return True
        except Exception as e:
            print(f"{Colors.RED}[ERROR] Failed to create file: {e}{Colors.RESET}")
            return False

    def batch_create_files(self, file_spec: str, user_id: str = None) -> int:
        """Batch create multiple files"""
        if not self.check_permission('batch_create_files'):
            return 0
        
        """
        Format: filename1:type1,filename2:type2,filename3:type3
        Example: report:csv,config:json,notes:txt
        """
        count = 0
        try:
            files = file_spec.split(',')
            for file_entry in files:
                if ':' not in file_entry:
                    print(f"{Colors.YELLOW}[WARN] Invalid format: {file_entry} (use name:type){Colors.RESET}")
                    continue
                
                filename, file_type = file_entry.strip().split(':')
                if self.create_file(filename.strip(), file_type.strip(), user_id):
                    count += 1
            
            print(f"{Colors.GREEN}[SUCCESS] Batch created {count} files{Colors.RESET}")
            self.log_action(f"BATCH_CREATE_FILES: {count} files created")
            return count
        except Exception as e:
            print(f"{Colors.RED}[ERROR] Batch create failed: {e}{Colors.RESET}")
            return count

    def delete_file(self, file_path_str: str, user_id: str = None) -> bool:
        """Delete a specific file"""
        if not self.check_permission('delete_files'):
            return False
        
        if user_id is None:
            user_id = self.current_user.user_id if self.current_user else 'system'
        
        file_path = self.data_dir / user_id / 'files' / file_path_str
        
        try:
            if file_path.exists():
                file_path.unlink()
                print(f"{Colors.GREEN}[SUCCESS] File deleted: {file_path}{Colors.RESET}")
                self.log_action(f"DELETE_FILE: {file_path_str}")
                return True
            else:
                print(f"{Colors.YELLOW}[INFO] File not found: {file_path}{Colors.RESET}")
                return False
        except Exception as e:
            print(f"{Colors.RED}[ERROR] Failed to delete file: {e}{Colors.RESET}")
            return False

    def get_file_stats(self, user_id: str = None) -> Dict:
        """Get statistics about user files"""
        if not self.check_permission('view_file_stats'):
            return {}
        
        if user_id is None:
            user_id = self.current_user.user_id if self.current_user else 'system'
        
        user_files_dir = self.data_dir / user_id / 'files'
        stats = {
            'user_id': user_id,
            'total_files': 0,
            'total_size': 0,
            'files_by_type': {},
            'files': []
        }
        
        if user_files_dir.exists():
            for file in user_files_dir.iterdir():
                if file.is_file():
                    size = file.stat().st_size
                    ext = file.suffix
                    stats['total_files'] += 1
                    stats['total_size'] += size
                    stats['files_by_type'][ext] = stats['files_by_type'].get(ext, 0) + 1
                    stats['files'].append({
                        'name': file.name,
                        'size': size,
                        'created': datetime.fromtimestamp(file.stat().st_ctime).strftime("%Y-%m-%d %H:%M")
                    })
        
        self.log_action(f"VIEW_FILE_STATS: {user_id}")
        return stats

    def check_client_system(self, client_id: str = None) -> Dict:
        """Check client system status and information"""
        if not self.check_permission('check_system'):
            return {}
        
        if client_id is None:
            client_id = self.current_user.user_id if self.current_user else 'system'
        
        if client_id not in self.users:
            print(f"{Colors.YELLOW}[WARN] Client not found: {client_id}{Colors.RESET}")
            return {}
        
        user = self.users[client_id]
        user_dir = self.data_dir / client_id
        
        # Calculate directory size
        total_size = 0
        file_count = 0
        if user_dir.exists():
            for item in user_dir.rglob('*'):
                if item.is_file():
                    total_size += item.stat().st_size
                    file_count += 1
        
        system_info = {
            'client_id': client_id,
            'client_name': user.name,
            'role': user.role,
            'created': user.created_at.strftime("%Y-%m-%d %H:%M"),
            'total_files': file_count,
            'data_size_kb': round(total_size / 1024, 2),
            'temp_files': len(list(self.temp_files_dir.iterdir())) if self.temp_files_dir.exists() else 0,
            'is_active': client_id == self.current_user.user_id if self.current_user else False
        }
        
        self.log_action(f"CHECK_CLIENT_SYSTEM: {client_id}")
        return system_info

    def view_system_status(self):
        """Display comprehensive system status"""
        if not self.check_permission('check_system'):
            return
        
        print(f"\n{Colors.BOLD}=== System Status ==={Colors.RESET}")
        print(f"  Total Users: {len(self.users)}")
        print(f"  Current User: {self.current_user.name if self.current_user else 'NONE'}")
        print(f"  Total Logs: {len(self.logs)}")
        
        total_data_size = 0
        total_files = 0
        for item in self.data_dir.rglob('*'):
            if item.is_file():
                total_files += 1
                total_data_size += item.stat().st_size
        
        print(f"  Total Data Files: {total_files}")
        print(f"  Data Size: {round(total_data_size / 1024, 2)} KB")
        print(f"  Temp Files: {len(list(self.temp_files_dir.iterdir())) if self.temp_files_dir.exists() else 0}")
        print()
    
    def view_users(self):
        """List all users"""
        if not self.users:
            print(f"{Colors.YELLOW}[INFO] No users found{Colors.RESET}")
            return
        
        print(f"\n{Colors.BOLD}=== Users ==={Colors.RESET}")
        for user_id, user in self.users.items():
            print(f"  {Colors.BLUE}{user_id}{Colors.RESET}: {user.name} ({user.role}) - Created: {user.created_at.strftime('%Y-%m-%d %H:%M')}")
        print()

    def view_permissions(self):
        """Display current user's permissions"""
        if not self.current_user:
            print(f"{Colors.RED}[ERROR] No user logged in{Colors.RESET}")
            return
        
        perms = PERMISSIONS[self.current_user.role]
        print(f"\n{Colors.BOLD}=== Permissions for {self.current_user.role} ==={Colors.RESET}")
        for action, allowed in perms.items():
            status = f"{Colors.GREEN}[YES]{Colors.RESET}" if allowed else f"{Colors.RED}[NO]{Colors.RESET}"
            print(f"  {status} {action}")
        print()

    def view_logs(self):
        """View system logs"""
        if self.current_user and self.current_user.role != 'Admin':
            if not self.check_permission('view_logs'):
                return
        
        print(f"\n{Colors.BOLD}=== System Logs ==={Colors.RESET}")
        for log in self.logs[-20:]:  # Show last 20 logs
            print(f"  {log}")
        print()

    def show_help(self):
        """Display help menu"""
        print(f"""
{Colors.BOLD}=== Management System Commands ==={Colors.RESET}

{Colors.BLUE}User Management:{Colors.RESET}
  create_user <user_id> <name> <role>  - Create new user (Admin only)
  login <user_id>                       - Login as user
  logout                                - Logout current user
  delete_user <user_id>                 - Delete user (Admin only)
  view_users                            - List all users

{Colors.BLUE}Data & File Operations:{Colors.RESET}
  delete_data <user_id>                 - Delete user data
  batch_delete <user1,user2,...>        - Batch delete data
  cleanup_temp                          - Delete temporary files
  cleanup_system                        - Full system cleanup (Admin only)

{Colors.BLUE}File Management:{Colors.RESET}
  create_file <name> <type> [user_id]  - Create single file
    Types: csv, json, txt, log, config, xml
    Example: create_file report csv
  
  batch_create <spec> [user_id]        - Create multiple files
    Format: name1:type1,name2:type2
    Example: batch_create report:csv,config:json,notes:txt
  
  delete_file <filename> [user_id]     - Delete a file
  view_files [user_id]                 - View file statistics
  list_files [user_id]                 - List all files

{Colors.BLUE}System Monitoring:{Colors.RESET}
  check_client <client_id>             - Check client system status
  status                               - View system status
  permissions                          - View current user permissions
  logs                                 - View system logs

{Colors.BLUE}Other:{Colors.RESET}
  help                                 - Show this help
  exit                                 - Exit program

{Colors.BOLD}File Types Available: csv, json, txt, log, config, xml{Colors.RESET}
{Colors.BOLD}Roles: Admin, Merchant, PCS{Colors.RESET}
""")



def main():
    system = ManagementSystem()
    
    print(f"{Colors.BOLD}{Colors.BLUE}Welcome to Management System{Colors.RESET}\n")
    print("Type 'help' for commands or 'exit' to quit\n")
    
    # Demo: Create default users
    print("Setting up demo users...")
    system.create_user('admin1', 'Admin User', 'Admin')
    system.login('admin1')  # Auto-login after first admin creation
    system.create_user('merchant1', 'Merchant User', 'Merchant')
    system.create_user('pcs1', 'PCS User', 'PCS')
    system.logout()  # Logout after setup
    print()
    
    while True:
        try:
            user_prompt = f"{Colors.BOLD}{system.current_user.role if system.current_user else 'GUEST'}{Colors.RESET}> "
            command = input(user_prompt).strip()
            
            if not command:
                continue
            
            parts = command.split()
            cmd = parts[0].lower()
            
            if cmd == 'exit':
                print(f"{Colors.YELLOW}Exiting...{Colors.RESET}")
                break
            
            elif cmd == 'help':
                system.show_help()
            
            elif cmd == 'create_user' and len(parts) == 4:
                system.create_user(parts[1], parts[2], parts[3])
            
            elif cmd == 'login' and len(parts) == 2:
                system.login(parts[1])
            
            elif cmd == 'logout':
                system.logout()
            
            elif cmd == 'delete_user' and len(parts) == 2:
                system.delete_user(parts[1])
            
            elif cmd == 'delete_data' and len(parts) == 2:
                system.delete_user_data(parts[1])
            
            elif cmd == 'batch_delete' and len(parts) >= 2:
                targets = parts[1].split(',')
                target_type = parts[2] if len(parts) > 2 else 'data'
                system.batch_delete(targets, target_type)
            
            elif cmd == 'cleanup_temp':
                system.cleanup_temp_files()
            
            elif cmd == 'cleanup_system':
                system.cleanup_system()
            
            elif cmd == 'view_users':
                system.view_users()
            
            elif cmd == 'permissions':
                system.view_permissions()
            
            elif cmd == 'logs':
                system.view_logs()
            
            # File operations
            elif cmd == 'create_file' and len(parts) >= 3:
                file_type = parts[2]
                user_id = parts[3] if len(parts) > 3 else None
                system.create_file(parts[1], file_type, user_id)
            
            elif cmd == 'batch_create' and len(parts) >= 2:
                file_spec = parts[1]
                user_id = parts[2] if len(parts) > 2 else None
                system.batch_create_files(file_spec, user_id)
            
            elif cmd == 'delete_file' and len(parts) >= 2:
                filename = parts[1]
                user_id = parts[2] if len(parts) > 2 else None
                system.delete_file(filename, user_id)
            
            elif cmd == 'view_files':
                user_id = parts[1] if len(parts) > 1 else None
                stats = system.get_file_stats(user_id)
                if stats:
                    print(f"\n{Colors.BOLD}=== File Statistics for {stats['user_id']} ==={Colors.RESET}")
                    print(f"  Total Files: {stats['total_files']}")
                    print(f"  Total Size: {round(stats['total_size'] / 1024, 2)} KB")
                    print(f"  Files by Type: {stats['files_by_type']}")
                    if stats['files']:
                        print(f"\n  {Colors.BLUE}File List:{Colors.RESET}")
                        for file_info in stats['files']:
                            print(f"    - {file_info['name']} ({file_info['size']} bytes, {file_info['created']})")
                    print()
            
            elif cmd == 'list_files':
                user_id = parts[1] if len(parts) > 1 else None
                stats = system.get_file_stats(user_id)
                if stats and stats['files']:
                    print(f"\n{Colors.BOLD}=== Files for {stats['user_id']} ==={Colors.RESET}")
                    for file_info in stats['files']:
                        print(f"  {Colors.BLUE}{file_info['name']}{Colors.RESET} - {file_info['size']} bytes")
                    print()
            
            # System monitoring
            elif cmd == 'check_client' and len(parts) == 2:
                info = system.check_client_system(parts[1])
                if info:
                    print(f"\n{Colors.BOLD}=== Client System Status ==={Colors.RESET}")
                    print(f"  Client ID: {Colors.BLUE}{info['client_id']}{Colors.RESET}")
                    print(f"  Name: {info['client_name']}")
                    print(f"  Role: {info['role']}")
                    print(f"  Created: {info['created']}")
                    print(f"  Total Files: {info['total_files']}")
                    print(f"  Data Size: {info['data_size_kb']} KB")
                    print(f"  Temp Files: {info['temp_files']}")
                    print(f"  Active: {'Yes' if info['is_active'] else 'No'}")
                    print()
            
            elif cmd == 'status':
                system.view_system_status()
            
            else:
                print(f"{Colors.RED}[ERROR] Unknown command: {cmd}{Colors.RESET}")
                print("Type 'help' for available commands")
        
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Interrupted by user{Colors.RESET}")
            break
        except Exception as e:
            print(f"{Colors.RED}[ERROR] {e}{Colors.RESET}")


if __name__ == "__main__":
    main()
