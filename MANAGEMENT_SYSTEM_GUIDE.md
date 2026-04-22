# Role-Based Management System - Quick Start Guide

## Features Implemented

### ✅ User Management
- 3 Roles: **Admin**, **Merchant**, **PCS**
- Role-based permission system
- User creation, login, logout, deletion

### ✅ Data Operations
- Single file deletion
- Batch delete multiple items in one command
- Cleanup temporary files
- Full system cleanup (Admin only)

### ✅ File Management (NEW)
- **Create files**: CSV, JSON, TXT, LOG, CONFIG, XML
- **Batch create**: Multiple files with one command
  - Format: `batch_create file1:type1,file2:type2,file3:type3`
  - Example: `batch_create report:csv,config:json,notes:txt`
- **Delete files**: Remove specific files
- **View statistics**: File counts, sizes, types
- **List files**: Show all files for a user

### ✅ System Monitoring
- **Check client status**: Get detailed client system info
- **View system status**: Overall system statistics
- **Logs**: Track all operations with timestamps
- **Permissions**: Display role capabilities

---

## Quick Start Examples

```bash
# Login as admin
login admin1

# Create single file
create_file report csv

# Create MULTIPLE files with ONE command (feature you asked for!)
batch_create database:csv,settings:config,notes:txt,log:log

# View all files created
view_files

# Check specific client status
check_client admin1

# View entire system status
status

# View role permissions
permissions

# Cleanup all temp files
cleanup_temp

# Full system cleanup (Admin only)
cleanup_system
```

---

## Role-Based Permissions

### Admin Role ✓
- Create/Delete users
- Delete any user data
- Batch operations
- File management
- System cleanup
- View all statistics
- Check any client

### Merchant Role ✓
- Create/delete own data only
- File management
- Batch file creation
- Check system status
- Cannot delete other users
- Cannot modify permissions

### PCS Role ✓
- Delete temporary files only
- Create individual files
- Check system status
- Limited file operations
- Cannot batch create
- Cannot delete other files

---

## Operations Possible with Single Commands

1. **Batch Delete Multiple Users**: `batch_delete user1,user2,user3`
2. **Batch Delete Multiple Data**: `batch_delete admin1,merchant1`
3. **Batch Create Multiple Files**: `batch_create file1:csv,file2:json,file3:txt,file4:config`
4. **Cleanup System**: `cleanup_system` (removes all temp files)
5. **Full Status Check**: `status` (shows all system info)
6. **Client System Check**: `check_client client_id` (full client details)

---

## File Types Available

| Type    | Extension | Use Case            |
|---------|-----------|---------------------|
| csv     | .csv      | Data tables         |
| json    | .json     | Configuration      |
| txt     | .txt      | Text notes          |
| log     | .log      | System logs         |
| config  | .conf     | Settings files      |
| xml     | .xml      | Data markup         |

---

## Command Summary

```
help                              Show all commands
create_user <id> <name> <role>   Create user
login <user_id>                   Login
logout                            Logout
delete_user <user_id>             Delete user

create_file <name> <type>        Create single file
batch_create <spec>              Create multiple files
delete_file <filename>            Delete file
view_files                        See file statistics
list_files                        List all files

delete_data <user_id>             Delete user data
batch_delete <users>              Batch delete
cleanup_temp                      Delete temp files
cleanup_system                    Full cleanup

check_client <id>                Check client status
status                           System status
permissions                      Show your permissions
logs                             View operation logs
```

---

## Run the System

```bash
python management_system.py
```

Type `help` for full command list inside the program.
