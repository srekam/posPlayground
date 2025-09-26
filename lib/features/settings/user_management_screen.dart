import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/models/server_config.dart';
import '../../core/services/server_config_service.dart';

class UserManagementScreen extends ConsumerStatefulWidget {
  const UserManagementScreen({super.key});

  @override
  ConsumerState<UserManagementScreen> createState() =>
      _UserManagementScreenState();
}

class _UserManagementScreenState extends ConsumerState<UserManagementScreen> {
  List<UserInfo> _users = [];
  List<RoleInfo> _roles = [];
  bool _isLoading = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadUsers();
    _loadRoles();
  }

  Future<void> _loadUsers() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final config = await ServerConfigService.getCurrentConfig();
      final apiKey = await ServerConfigService.getCurrentApiKey();

      if (apiKey == null) {
        setState(() {
          _error =
              'No API key configured. Please configure server settings first.';
          _isLoading = false;
        });
        return;
      }

      // TODO: Implement actual API call to fetch users
      // For now, show mock data
      setState(() {
        _users = _getMockUsers();
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _loadRoles() async {
    try {
      // TODO: Implement actual API call to fetch roles
      // For now, show mock data
      setState(() {
        _roles = _getMockRoles();
      });
    } catch (e) {
      // Handle error silently for roles
    }
  }

  List<UserInfo> _getMockUsers() {
    return [
      UserInfo(
        id: '1',
        email: 'owner@playpark.com',
        name: 'Park Owner',
        roles: ['Owner'],
        permissions: ['admin', 'can_manage_users', 'can_sell', 'can_redeem'],
        isActive: true,
        isOwner: true,
        lastLogin: DateTime.now().subtract(const Duration(hours: 2)),
      ),
      UserInfo(
        id: '2',
        email: 'manager@playpark.com',
        name: 'Store Manager',
        roles: ['Manager'],
        permissions: ['can_sell', 'can_redeem', 'can_access_reports'],
        isActive: true,
        isOwner: false,
        lastLogin: DateTime.now().subtract(const Duration(minutes: 30)),
      ),
      UserInfo(
        id: '3',
        email: 'cashier1@playpark.com',
        name: 'Cashier 1',
        roles: ['Cashier'],
        permissions: ['can_sell'],
        isActive: true,
        isOwner: false,
        lastLogin: DateTime.now().subtract(const Duration(minutes: 5)),
      ),
      UserInfo(
        id: '4',
        email: 'gate@playpark.com',
        name: 'Gate Operator',
        roles: ['Gate Operator'],
        permissions: ['can_redeem'],
        isActive: true,
        isOwner: false,
        lastLogin: DateTime.now().subtract(const Duration(hours: 1)),
      ),
    ];
  }

  List<RoleInfo> _getMockRoles() {
    return [
      const RoleInfo(
        id: '1',
        name: 'owner',
        displayName: 'Owner',
        description: 'Full system access and control',
        permissions: [
          'admin',
          'can_manage_users',
          'can_sell',
          'can_redeem',
          'can_access_reports'
        ],
        level: 10,
        color: '#d32f2f',
        isSystemRole: true,
      ),
      const RoleInfo(
        id: '2',
        name: 'manager',
        displayName: 'Manager',
        description: 'Store management and reporting access',
        permissions: ['can_sell', 'can_redeem', 'can_access_reports'],
        level: 7,
        color: '#1976d2',
        isSystemRole: true,
      ),
      const RoleInfo(
        id: '3',
        name: 'cashier',
        displayName: 'Cashier',
        description: 'Basic POS operations',
        permissions: ['can_sell'],
        level: 3,
        color: '#388e3c',
        isSystemRole: true,
      ),
      const RoleInfo(
        id: '4',
        name: 'gate_operator',
        displayName: 'Gate Operator',
        description: 'Ticket redemption and gate control',
        permissions: ['can_redeem'],
        level: 2,
        color: '#f57c00',
        isSystemRole: true,
      ),
    ];
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('User Management'),
        actions: [
          IconButton(
            onPressed: _isLoading ? null : _loadUsers,
            icon: const Icon(Icons.refresh),
            tooltip: 'Refresh',
          ),
          IconButton(
            onPressed: _showAddUserDialog,
            icon: const Icon(Icons.person_add),
            tooltip: 'Add User',
          ),
        ],
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 16),
            Text('Loading users...'),
          ],
        ),
      );
    }

    if (_error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.error_outline,
              size: 64,
              color: Colors.red,
            ),
            const SizedBox(height: 16),
            Text(
              'Error loading users',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 8),
            Text(
              _error!,
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Colors.red,
                  ),
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: _loadUsers,
              icon: const Icon(Icons.refresh),
              label: const Text('Retry'),
            ),
          ],
        ),
      );
    }

    return Column(
      children: [
        // Role Overview
        Container(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Roles & Permissions',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
              ),
              const SizedBox(height: 8),
              SizedBox(
                height: 120,
                child: ListView.builder(
                  scrollDirection: Axis.horizontal,
                  itemCount: _roles.length,
                  itemBuilder: (context, index) {
                    final role = _roles[index];
                    return _buildRoleCard(role);
                  },
                ),
              ),
            ],
          ),
        ),

        // Users List
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: _users.length,
            itemBuilder: (context, index) {
              final user = _users[index];
              return _buildUserCard(user);
            },
          ),
        ),
      ],
    );
  }

  Widget _buildRoleCard(RoleInfo role) {
    return Container(
      width: 200,
      margin: const EdgeInsets.only(right: 12),
      child: Card(
        color: Color(int.parse(role.color.replaceFirst('#', '0xFF')))
            .withOpacity(0.1),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    _getRoleIcon(role.name),
                    color:
                        Color(int.parse(role.color.replaceFirst('#', '0xFF'))),
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      role.displayName,
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: Color(
                            int.parse(role.color.replaceFirst('#', '0xFF'))),
                      ),
                    ),
                  ),
                  if (role.isSystemRole)
                    Icon(
                      Icons.security,
                      size: 16,
                      color: Color(
                          int.parse(role.color.replaceFirst('#', '0xFF'))),
                    ),
                ],
              ),
              const SizedBox(height: 4),
              Text(
                role.description,
                style: Theme.of(context).textTheme.bodySmall,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 4,
                runSpacing: 4,
                children: role.permissions.take(3).map((permission) {
                  return Chip(
                    label: Text(
                      permission,
                      style: const TextStyle(fontSize: 10),
                    ),
                    backgroundColor:
                        Color(int.parse(role.color.replaceFirst('#', '0xFF')))
                            .withOpacity(0.2),
                    materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                  );
                }).toList(),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildUserCard(UserInfo user) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  backgroundColor: user.isActive ? Colors.green : Colors.red,
                  radius: 20,
                  child: Text(
                    user.name[0].toUpperCase(),
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Text(
                            user.name,
                            style: Theme.of(context)
                                .textTheme
                                .titleMedium
                                ?.copyWith(
                                  fontWeight: FontWeight.bold,
                                ),
                          ),
                          const SizedBox(width: 8),
                          if (user.isOwner)
                            Chip(
                              label: const Text('OWNER'),
                              backgroundColor: Colors.red.withOpacity(0.2),
                              materialTapTargetSize:
                                  MaterialTapTargetSize.shrinkWrap,
                            ),
                        ],
                      ),
                      Text(
                        user.email,
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: Colors.grey[600],
                            ),
                      ),
                    ],
                  ),
                ),
                PopupMenuButton<String>(
                  onSelected: (value) => _handleUserAction(value, user),
                  itemBuilder: (context) => [
                    const PopupMenuItem(
                      value: 'edit',
                      child: Row(
                        children: [
                          Icon(Icons.edit),
                          SizedBox(width: 8),
                          Text('Edit'),
                        ],
                      ),
                    ),
                    const PopupMenuItem(
                      value: 'permissions',
                      child: Row(
                        children: [
                          Icon(Icons.security),
                          SizedBox(width: 8),
                          Text('Permissions'),
                        ],
                      ),
                    ),
                    PopupMenuItem(
                      value: user.isActive ? 'deactivate' : 'activate',
                      child: Row(
                        children: [
                          Icon(
                              user.isActive ? Icons.block : Icons.check_circle),
                          const SizedBox(width: 8),
                          Text(user.isActive ? 'Deactivate' : 'Activate'),
                        ],
                      ),
                    ),
                    const PopupMenuItem(
                      value: 'delete',
                      child: Row(
                        children: [
                          Icon(Icons.delete, color: Colors.red),
                          SizedBox(width: 8),
                          Text('Delete', style: TextStyle(color: Colors.red)),
                        ],
                      ),
                    ),
                  ],
                  child: const Icon(Icons.more_vert),
                ),
              ],
            ),

            const SizedBox(height: 12),

            // Roles
            Wrap(
              spacing: 4,
              runSpacing: 4,
              children: user.roles.map((role) {
                final roleInfo = _roles.firstWhere(
                  (r) => r.displayName == role,
                  orElse: () => RoleInfo(
                    id: '',
                    name: role.toLowerCase(),
                    displayName: role,
                    description: '',
                    permissions: [],
                    level: 1,
                    color: '#757575',
                    isSystemRole: false,
                  ),
                );

                return Chip(
                  label: Text(role),
                  backgroundColor:
                      Color(int.parse(roleInfo.color.replaceFirst('#', '0xFF')))
                          .withOpacity(0.2),
                  materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                );
              }).toList(),
            ),

            const SizedBox(height: 8),

            // Status and last login
            Row(
              children: [
                Icon(
                  user.isActive ? Icons.check_circle : Icons.block,
                  size: 16,
                  color: user.isActive ? Colors.green : Colors.red,
                ),
                const SizedBox(width: 8),
                Text(
                  user.isActive ? 'Active' : 'Inactive',
                  style: TextStyle(
                    color: user.isActive ? Colors.green : Colors.red,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                Icon(
                  Icons.access_time,
                  size: 16,
                  color: Colors.grey[600],
                ),
                const SizedBox(width: 8),
                Text(
                  'Last login: ${_formatLastLogin(user.lastLogin)}',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Colors.grey[600],
                      ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  IconData _getRoleIcon(String roleName) {
    switch (roleName.toLowerCase()) {
      case 'owner':
        return Icons.admin_panel_settings;
      case 'manager':
        return Icons.supervisor_account;
      case 'cashier':
        return Icons.point_of_sale;
      case 'gate_operator':
        return Icons.admin_panel_settings;
      default:
        return Icons.person;
    }
  }

  String _formatLastLogin(DateTime lastLogin) {
    final now = DateTime.now();
    final difference = now.difference(lastLogin);

    if (difference.inMinutes < 1) {
      return 'Just now';
    } else if (difference.inMinutes < 60) {
      return '${difference.inMinutes}m ago';
    } else if (difference.inHours < 24) {
      return '${difference.inHours}h ago';
    } else {
      return '${difference.inDays}d ago';
    }
  }

  void _handleUserAction(String action, UserInfo user) {
    switch (action) {
      case 'edit':
        _showEditUserDialog(user);
        break;
      case 'permissions':
        _showPermissionsDialog(user);
        break;
      case 'activate':
      case 'deactivate':
        _toggleUserStatus(user);
        break;
      case 'delete':
        _showDeleteUserDialog(user);
        break;
    }
  }

  void _showAddUserDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Add New User'),
        content: const Text(
            'User creation functionality will be implemented with full backend integration.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  void _showEditUserDialog(UserInfo user) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Edit User'),
        content: Text(
            'Edit functionality for ${user.name} will be implemented with full backend integration.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  void _showPermissionsDialog(UserInfo user) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('${user.name} - Permissions'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Current Permissions:',
                style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            ...user.permissions.map((permission) => Padding(
                  padding: const EdgeInsets.symmetric(vertical: 2),
                  child: Row(
                    children: [
                      const Icon(Icons.check_circle,
                          color: Colors.green, size: 16),
                      const SizedBox(width: 8),
                      Text(permission),
                    ],
                  ),
                )),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  void _toggleUserStatus(UserInfo user) {
    // TODO: Implement actual API call
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
            '${user.isActive ? 'Deactivating' : 'Activating'} ${user.name}...'),
      ),
    );
  }

  void _showDeleteUserDialog(UserInfo user) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete User'),
        content: Text(
            'Are you sure you want to delete ${user.name}? This action cannot be undone.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).pop();
              // TODO: Implement actual deletion
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text('Deleting ${user.name}...')),
              );
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Delete'),
          ),
        ],
      ),
    );
  }
}

class UserInfo {
  final String id;
  final String email;
  final String name;
  final List<String> roles;
  final List<String> permissions;
  final bool isActive;
  final bool isOwner;
  final DateTime lastLogin;

  const UserInfo({
    required this.id,
    required this.email,
    required this.name,
    required this.roles,
    required this.permissions,
    required this.isActive,
    required this.isOwner,
    required this.lastLogin,
  });
}

class RoleInfo {
  final String id;
  final String name;
  final String displayName;
  final String description;
  final List<String> permissions;
  final int level;
  final String color;
  final bool isSystemRole;

  const RoleInfo({
    required this.id,
    required this.name,
    required this.displayName,
    required this.description,
    required this.permissions,
    required this.level,
    required this.color,
    required this.isSystemRole,
  });
}
