# -*- coding: utf-8 -*-
"""
Collaborative Cybersecurity System for Sharingan OS
Multi-user sessions, shared workflows, team audit trail
"""

import os
import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger("collaborative_security")

class UserManager:
    """
    Multi-user authentication and permission management
    """

    def __init__(self):
        self.users: Dict[str, Dict[str, Any]] = {}
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.permissions = {
            'admin': ['read', 'write', 'delete', 'execute', 'manage_users'],
            'pentester': ['read', 'write', 'execute', 'audit'],
            'analyst': ['read', 'write', 'audit'],
            'viewer': ['read']
        }

    def authenticate_user(self, username: str, password: str) -> Optional[str]:
        """Authenticate user and return session token"""
        # Simple authentication (in production: use proper auth)
        if username in self.users and self.users[username]['password'] == password:
            session_token = f"session_{username}_{int(time.time())}"
            self.sessions[session_token] = {
                'username': username,
                'role': self.users[username]['role'],
                'created': time.time(),
                'last_activity': time.time()
            }
            return session_token
        return None

    def validate_session(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate session token"""
        if token in self.sessions:
            session = self.sessions[token]
            # Check expiration (24 hours)
            if time.time() - session['created'] < 86400:
                session['last_activity'] = time.time()
                return session
            else:
                del self.sessions[token]
        return None

    def add_user(self, username: str, password: str, role: str = 'viewer') -> bool:
        """Add new user"""
        if username not in self.users and role in self.permissions:
            self.users[username] = {
                'password': password,  # In production: hash this!
                'role': role,
                'created': time.time(),
                'last_login': None
            }
            return True
        return False

    def check_permission(self, token: str, action: str) -> bool:
        """Check if user has permission for action"""
        session = self.validate_session(token)
        if session:
            role = session['role']
            return action in self.permissions.get(role, [])
        return False

class CollaborativeSession:
    """
    Real-time collaborative session for cybersecurity tasks
    """

    def __init__(self, session_id: str, creator: str):
        self.session_id = session_id
        self.creator = creator
        self.participants: List[str] = [creator]
        self.workflow: Dict[str, Any] = {
            'id': session_id,
            'name': f'Session {session_id}',
            'status': 'active',
            'tasks': [],
            'created': time.time(),
            'last_activity': time.time()
        }
        self.audit_log: List[Dict[str, Any]] = []
        self.shared_data: Dict[str, Any] = {}

    def add_participant(self, username: str) -> bool:
        """Add participant to session"""
        if username not in self.participants:
            self.participants.append(username)
            self.log_action(username, 'joined_session', {'session': self.session_id})
            return True
        return False

    def remove_participant(self, username: str) -> bool:
        """Remove participant from session"""
        if username in self.participants and username != self.creator:
            self.participants.remove(username)
            self.log_action(username, 'left_session', {'session': self.session_id})
            return True
        return False

    def update_workflow(self, username: str, updates: Dict[str, Any]) -> bool:
        """Update shared workflow"""
        # Merge updates into workflow
        self.workflow.update(updates)
        self.workflow['last_activity'] = time.time()
        self.log_action(username, 'updated_workflow', updates)
        return True

    def add_task(self, username: str, task: Dict[str, Any]) -> bool:
        """Add task to workflow"""
        task_id = f"task_{len(self.workflow['tasks'])}"
        task.update({
            'id': task_id,
            'created_by': username,
            'created_at': time.time(),
            'status': 'pending',
            'assigned_to': None
        })
        self.workflow['tasks'].append(task)
        self.log_action(username, 'added_task', {'task_id': task_id})
        return True

    def update_task_status(self, username: str, task_id: str, status: str) -> bool:
        """Update task status"""
        for task in self.workflow['tasks']:
            if task['id'] == task_id:
                task['status'] = status
                task['updated_by'] = username
                task['updated_at'] = time.time()
                self.log_action(username, 'updated_task', {
                    'task_id': task_id,
                    'status': status
                })
                return True
        return False

    def share_data(self, username: str, key: str, data: Any) -> bool:
        """Share data with session participants"""
        self.shared_data[key] = {
            'data': data,
            'shared_by': username,
            'shared_at': time.time(),
            'access_count': 0
        }
        self.log_action(username, 'shared_data', {'key': key})
        return True

    def get_shared_data(self, username: str, key: str) -> Optional[Any]:
        """Get shared data"""
        if key in self.shared_data:
            self.shared_data[key]['access_count'] += 1
            self.log_action(username, 'accessed_data', {'key': key})
            return self.shared_data[key]['data']
        return None

    def log_action(self, username: str, action: str, details: Dict[str, Any]) -> None:
        """Log action for audit trail"""
        audit_entry = {
            'timestamp': time.time(),
            'username': username,
            'action': action,
            'details': details,
            'session_id': self.session_id
        }
        self.audit_log.append(audit_entry)

    def get_audit_trail(self, username: str) -> List[Dict[str, Any]]:
        """Get audit trail for session"""
        self.log_action(username, 'accessed_audit', {})
        return self.audit_log.copy()

    def get_session_state(self) -> Dict[str, Any]:
        """Get complete session state"""
        return {
            'session_id': self.session_id,
            'creator': self.creator,
            'participants': self.participants,
            'workflow': self.workflow,
            'shared_data_keys': list(self.shared_data.keys()),
            'last_activity': self.workflow['last_activity']
        }

class CollaborativeSecurityManager:
    """
    Main manager for collaborative cybersecurity features
    """

    def __init__(self):
        self.user_manager = UserManager()
        self.active_sessions: Dict[str, CollaborativeSession] = {}
        self.session_history: List[Dict[str, Any]] = []

        # Initialize default admin user
        self.user_manager.add_user('admin', 'admin123', 'admin')

        logger.info("Collaborative Security Manager initialized")

    def create_session(self, creator_token: str, session_name: str = None) -> Optional[str]:
        """Create new collaborative session"""
        session_info = self.user_manager.validate_session(creator_token)
        if not session_info:
            return None

        creator = session_info['username']
        session_id = f"collab_{creator}_{int(time.time())}"

        session = CollaborativeSession(session_id, creator)
        if session_name:
            session.workflow['name'] = session_name

        self.active_sessions[session_id] = session

        logger.info(f"Collaborative session created: {session_id} by {creator}")
        return session_id

    def join_session(self, user_token: str, session_id: str) -> bool:
        """Join existing collaborative session"""
        session_info = self.user_manager.validate_session(user_token)
        if not session_info or session_id not in self.active_sessions:
            return False

        username = session_info['username']
        session = self.active_sessions[session_id]

        return session.add_participant(username)

    def leave_session(self, user_token: str, session_id: str) -> bool:
        """Leave collaborative session"""
        session_info = self.user_manager.validate_session(user_token)
        if not session_info or session_id not in self.active_sessions:
            return False

        username = session_info['username']
        session = self.active_sessions[session_id]

        return session.remove_participant(username)

    def end_session(self, user_token: str, session_id: str) -> bool:
        """End collaborative session"""
        session_info = self.user_manager.validate_session(user_token)
        if not session_info or session_id not in self.active_sessions:
            return False

        username = session_info['username']
        session = self.active_sessions[session_id]

        # Only creator can end session
        if username != session.creator:
            return False

        # Archive session
        session.workflow['status'] = 'completed'
        session.workflow['ended_at'] = time.time()
        self.session_history.append(session.workflow)

        # Remove from active sessions
        del self.active_sessions[session_id]

        logger.info(f"Collaborative session ended: {session_id}")
        return True

    def get_session_state(self, user_token: str, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session state for user"""
        session_info = self.user_manager.validate_session(user_token)
        if not session_info or session_id not in self.active_sessions:
            return None

        session = self.active_sessions[session_id]
        return session.get_session_state()

    def update_workflow(self, user_token: str, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update session workflow"""
        session_info = self.user_manager.validate_session(user_token)
        if not session_info or session_id not in self.active_sessions:
            return False

        username = session_info['username']
        session = self.active_sessions[session_id]

        return session.update_workflow(username, updates)

    def add_task(self, user_token: str, session_id: str, task: Dict[str, Any]) -> bool:
        """Add task to session workflow"""
        session_info = self.user_manager.validate_session(user_token)
        if not session_info or session_id not in self.active_sessions:
            return False

        username = session_info['username']
        session = self.active_sessions[session_id]

        return session.add_task(username, task)

    def update_task_status(self, user_token: str, session_id: str, task_id: str, status: str) -> bool:
        """Update task status in workflow"""
        session_info = self.user_manager.validate_session(user_token)
        if not session_info or session_id not in self.active_sessions:
            return False

        username = session_info['username']
        session = self.active_sessions[session_id]

        return session.update_task_status(username, task_id, status)

    def share_data(self, user_token: str, session_id: str, key: str, data: Any) -> bool:
        """Share data with session"""
        session_info = self.user_manager.validate_session(user_token)
        if not session_info or session_id not in self.active_sessions:
            return False

        username = session_info['username']
        session = self.active_sessions[session_id]

        return session.share_data(username, key, data)

    def get_shared_data(self, user_token: str, session_id: str, key: str) -> Optional[Any]:
        """Get shared data from session"""
        session_info = self.user_manager.validate_session(user_token)
        if not session_info or session_id not in self.active_sessions:
            return None

        username = session_info['username']
        session = self.active_sessions[session_id]

        return session.get_shared_data(username, key)

    def get_audit_trail(self, user_token: str, session_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get audit trail for session"""
        session_info = self.user_manager.validate_session(user_token)
        if not session_info or session_id not in self.active_sessions:
            return None

        username = session_info['username']
        session = self.active_sessions[session_id]

        return session.get_audit_trail(username)

    def get_active_sessions(self, user_token: str) -> List[Dict[str, Any]]:
        """Get list of active sessions for user"""
        session_info = self.user_manager.validate_session(user_token)
        if not session_info:
            return []

        sessions = []
        for session_id, session in self.active_sessions.items():
            if session_info['username'] in session.participants:
                sessions.append(session.get_session_state())

        return sessions

    def get_session_history(self, user_token: str) -> List[Dict[str, Any]]:
        """Get session history for user"""
        session_info = self.user_manager.validate_session(user_token)
        if not session_info:
            return []

        username = session_info['username']
        return [s for s in self.session_history if s.get('creator') == username]

    def cleanup_inactive_sessions(self, max_age: int = 3600) -> int:
        """Clean up inactive sessions older than max_age seconds"""
        current_time = time.time()
        to_remove = []

        for session_id, session in self.active_sessions.items():
            if current_time - session.workflow['last_activity'] > max_age:
                # Archive inactive session
                session.workflow['status'] = 'inactive'
                session.workflow['ended_at'] = current_time
                self.session_history.append(session.workflow)
                to_remove.append(session_id)

        for session_id in to_remove:
            del self.active_sessions[session_id]

        logger.info(f"Cleaned up {len(to_remove)} inactive sessions")
        return len(to_remove)

# Global instance
_collab_manager = None

def get_collaborative_manager() -> CollaborativeSecurityManager:
    """Get global collaborative security manager instance"""
    global _collab_manager
    if _collab_manager is None:
        _collab_manager = CollaborativeSecurityManager()
    return _collab_manager

if __name__ == "__main__":
    print("[COLLABORATIVE SECURITY] Sharingan Collaborative Security System")
    print("=" * 70)

    # Test the system
    manager = get_collaborative_manager()

    # Test user management
    admin_token = manager.user_manager.authenticate_user('admin', 'admin123')
    print(f"Admin authentication: {'SUCCESS' if admin_token else 'FAILED'}")

    # Test session creation
    session_id = manager.create_session(admin_token, "Test Penetration Session")
    print(f"Session creation: {'SUCCESS' if session_id else 'FAILED'}")

    # Test session operations
    if session_id:
        success = manager.add_task(admin_token, session_id, {
            'title': 'Network Scan',
            'description': 'Perform comprehensive network scan',
            'type': 'scan'
        })
        print(f"Task addition: {'SUCCESS' if success else 'FAILED'}")

    print("\nCollaborative security system ready!")
    print("Features available:")
    print("- Multi-user authentication")
    print("- Real-time collaborative sessions")
    print("- Shared workflows and tasks")
    print("- Complete audit trails")
    print("- Permission-based access control")