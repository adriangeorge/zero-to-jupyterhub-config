"""Custom spawner with profile-based class selection"""
from kubespawner import KubeSpawner
from jupyterhub import orm


class ClassSelectionSpawner(KubeSpawner):
    """
    Spawner that:
    1. Shows class profiles for students to select
    2. Assigns students to teacher groups based on selection
    3. Filters profiles based on user type
    """
    
    def _options_form_default(self):
        """Filter profiles based on user type - teachers get no form, just default environment"""
        user_groups = {g.name for g in self.user.groups}
        
        # Teachers and admins don't need to select a profile - they get teacher-environment automatically
        if 'teachers' in user_groups or self.user.admin:
            return ''  # No form for teachers, just use default profile
        
        # If already enrolled, skip options entirely (check ORM)
        for group_name in ('teacher-prof-smith', 'teacher-prof-jones', 'teacher-prof-doe'):
            group = self.db.query(orm.Group).filter_by(name=group_name).first()
            if group and self.user.orm_user in group.users:
                return ''

        # If already enrolled (fallback to group list), skip options entirely
        if any(g.startswith('teacher-prof-') for g in user_groups):
            return ''

        # Students see only class profiles (not teacher-environment)
        filtered_profiles = [p for p in self.profile_list if p.get('slug') != 'teacher-environment']
        
        if filtered_profiles:
            original_list = self.profile_list
            self.profile_list = filtered_profiles
            result = super()._options_form_default()
            self.profile_list = original_list
            return result
        
        return super()._options_form_default()
    
    async def start(self):
        """Assign student to teacher group based on profile selection (only once)"""
        user_groups = {g.name for g in self.user.groups}
        username = self.user.name

        # For teachers/admins, automatically set teacher-environment profile
        if 'teachers' in user_groups or self.user.admin:
            if not self.user_options.get('profile'):
                self.user_options['profile'] = 'teacher-environment'
                print(f"Teacher/Admin {username} automatically assigned teacher-environment profile")

        # For students, handle class enrollment
        if 'teachers' not in user_groups and not self.user.admin:
            profile_to_group = {
                'prof-smith-class': 'teacher-prof-smith',
                'prof-jones-class': 'teacher-prof-jones',
                'prof-doe-class': 'teacher-prof-doe',
            }
            group_to_profile = {group: profile for profile, group in profile_to_group.items()}

            # Check if student is already enrolled in any class
            enrolled_group = None
            for group_name in profile_to_group.values():
                group = self.db.query(orm.Group).filter_by(name=group_name).first()
                if group and self.user.orm_user in group.users:
                    enrolled_group = group_name
                    print(f"Student {username} already enrolled in {group_name}, keeping current enrollment")
                    break

            # If already enrolled, clear profile entirely and use default
            if enrolled_group:
                self.user_options['profile'] = ''
                print(f"Student {username} using default profile (enrolled in {enrolled_group})")
            else:
                selected_profile = self.user_options.get('profile', '')
                teacher_group = profile_to_group.get(selected_profile)

                if teacher_group:
                    print(f"Student {username} selected {selected_profile} → {teacher_group} (first enrollment)")

                    group = self.db.query(orm.Group).filter_by(name=teacher_group).first()
                    if group:
                        group.users.append(self.user.orm_user)
                        self.db.commit()
                        print(f"  → Added to {teacher_group}")

        return await super().start()


def configure_spawner(c):
    """Set the custom spawner class"""
    c.JupyterHub.spawner_class = ClassSelectionSpawner
    print("✓ Custom class selection spawner configured")


