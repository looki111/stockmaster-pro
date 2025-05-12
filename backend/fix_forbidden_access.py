#!/usr/bin/env python3
"""
Fix Forbidden Access Issues in StockMaster Pro

This script addresses common issues that could cause 403 Forbidden errors:
1. Ensures users have proper role assignments
2. Fixes permission entries in the database
3. Repairs role-permission relationships
4. Creates a superuser with full access if needed
"""

import os
import sys
from flask import Flask
from werkzeug.security import generate_password_hash
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create a minimal Flask app for database operations
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/stockmaster.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Import database setup first
from database.db_setup import db
db.init_app(app)

# Import models in proper order to avoid circular dependencies
with app.app_context():
    from database.models import User, Role, Permission, Branch
    # Import roles after database models
    from roles import DEFAULT_PERMISSIONS, DEFAULT_ROLES

def ensure_all_permissions_exist():
    """Ensure all required permissions exist in the database"""
    logger.info("Checking and creating permissions...")
    
    with app.app_context():
        for module, permissions in DEFAULT_PERMISSIONS.items():
            for perm_name, perm_desc in permissions:
                permission = Permission.query.filter_by(name=perm_name).first()
                if not permission:
                    logger.info(f"Creating missing permission: {perm_name}")
                    permission = Permission(
                        name=perm_name,
                        description=perm_desc,
                        module=module
                    )
                    db.session.add(permission)
        
        db.session.commit()
        logger.info("All permissions verified and created if needed.")

def ensure_all_roles_exist():
    """Ensure all required roles exist in the database"""
    logger.info("Checking and creating roles...")
    
    with app.app_context():
        for role_name, role_data in DEFAULT_ROLES.items():
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                logger.info(f"Creating missing role: {role_name}")
                role = Role(
                    name=role_name,
                    description=role_data['description'],
                    is_system=role_data['is_system']
                )
                db.session.add(role)
                db.session.commit()  # Commit to get role.id
            
            # Ensure role has all required permissions
            all_perms_for_role = set(role_data['permissions'])
            existing_perms = set(p.name for p in role.permissions)
            missing_perms = all_perms_for_role - existing_perms
            
            if missing_perms:
                logger.info(f"Adding missing permissions to role {role_name}: {missing_perms}")
                for perm_name in missing_perms:
                    permission = Permission.query.filter_by(name=perm_name).first()
                    if permission:
                        role.permissions.append(permission)
        
        db.session.commit()
        logger.info("All roles verified and created if needed.")

def ensure_superuser_exists():
    """Create a superuser with all permissions if none exists"""
    logger.info("Checking for superuser...")
    
    with app.app_context():
        # Check if superuser attribute exists
        if not hasattr(User, 'is_superuser'):
            logger.warning("User model doesn't have is_superuser attribute, skipping superuser check")
            return
    
        # Check if any superuser exists
        try:
            superusers = User.query.filter_by(is_superuser=True).all()
            superuser_role = Role.query.filter_by(name='superuser').first()
            
            if not superusers:
                logger.info("No superuser found. Creating admin superuser...")
                
                # Ensure we have at least one branch
                branch = Branch.query.first()
                if not branch:
                    logger.info("Creating default branch")
                    branch = Branch(name="Main Branch", is_active=True, is_main=True)
                    db.session.add(branch)
                    db.session.commit()
                
                # Create admin user with superuser privileges
                admin = User(
                    username="admin",
                    password=generate_password_hash("admin123"),
                    email="admin@example.com",
                    is_active=True,
                    is_superuser=True,
                    branch_id=branch.id
                )
                
                # Assign superuser role
                if superuser_role:
                    admin.roles.append(superuser_role)
                
                db.session.add(admin)
                db.session.commit()
                logger.info("Created admin superuser with password 'admin123'")
            else:
                logger.info(f"Found {len(superusers)} superuser(s)")
                
                # Ensure all superusers have the superuser role
                for user in superusers:
                    if superuser_role and superuser_role not in user.roles:
                        logger.info(f"Adding superuser role to user: {user.username}")
                        user.roles.append(superuser_role)
                
                db.session.commit()
        except Exception as e:
            logger.error(f"Error in superuser check: {e}")
            db.session.rollback()

def fix_user_role_assignments():
    """Ensure all users have at least one role"""
    logger.info("Checking user role assignments...")
    
    with app.app_context():
        try:
            users_without_roles = User.query.filter(~User.roles.any()).all()
            cashier_role = Role.query.filter_by(name='cashier').first()
            
            if users_without_roles:
                logger.info(f"Found {len(users_without_roles)} users without any roles")
                
                if cashier_role:
                    for user in users_without_roles:
                        logger.info(f"Assigning cashier role to user: {user.username}")
                        user.roles.append(cashier_role)
                    
                    db.session.commit()
                    logger.info("Assigned default roles to all users")
                else:
                    logger.error("Could not find cashier role to assign as default")
            else:
                logger.info("All users have at least one role assigned")
        except Exception as e:
            logger.error(f"Error in role assignment: {e}")
            db.session.rollback()

def fix_branch_assignments():
    """Ensure all users have a branch assigned"""
    logger.info("Checking user branch assignments...")
    
    with app.app_context():
        try:
            # Get default branch
            main_branch = Branch.query.filter_by(is_main=True).first()
            if not main_branch:
                main_branch = Branch.query.first()
            
            if not main_branch:
                logger.info("Creating main branch")
                main_branch = Branch(name="Main Branch", is_active=True, is_main=True)
                db.session.add(main_branch)
                db.session.commit()
            
            # Find users without branch
            users_without_branch = User.query.filter_by(branch_id=None).all()
            
            if users_without_branch:
                logger.info(f"Found {len(users_without_branch)} users without branch assignment")
                for user in users_without_branch:
                    logger.info(f"Assigning main branch to user: {user.username}")
                    user.branch_id = main_branch.id
                
                db.session.commit()
                logger.info("Assigned branch to all users")
            else:
                logger.info("All users have a branch assigned")
        except Exception as e:
            logger.error(f"Error in branch assignment: {e}")
            db.session.rollback()

def main():
    """Main function - fix all access and permission issues"""
    try:
        logger.info("Starting forbidden access fix script...")
        
        # Fix permissions and roles
        ensure_all_permissions_exist()
        ensure_all_roles_exist()
        
        # Fix user assignments
        fix_user_role_assignments()
        fix_branch_assignments()
        
        # Ensure we have at least one superuser
        ensure_superuser_exists()
        
        logger.info("=========================================")
        logger.info("Forbidden access fix completed successfully!")
        logger.info("If you created a new admin user, the credentials are:")
        logger.info("Username: admin")
        logger.info("Password: admin123")
        logger.info("=========================================")
        
        return 0
    except Exception as e:
        logger.error(f"Error during fix: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 