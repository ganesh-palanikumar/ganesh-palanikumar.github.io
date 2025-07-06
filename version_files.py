#!/usr/bin/env python3
"""
Version Files Script
Reads _config.yml to get the version number and renames all files to include the correct version.
"""

import os
import re
import yaml
import shutil
from pathlib import Path

def load_config():
    """Load the Jekyll configuration file."""
    try:
        with open('_config.yml', 'r') as file:
            config = yaml.safe_load(file)
            return config.get('version', '0.0.1')
    except FileNotFoundError:
        print("Error: _config.yml not found!")
        return None
    except yaml.YAMLError as e:
        print(f"Error parsing _config.yml: {e}")
        return None

def get_version_string(version):
    """Convert version to string format for filenames."""
    return f"v{version}"

def find_files_with_version_patterns():
    """Find all files that need versioning."""
    files_to_version = {
        'layouts': [],
        'includes': [],
        'pages': [],
        'posts': [],
        'css': []
    }
    
    # Find layout files
    layouts_dir = Path('_layouts')
    if layouts_dir.exists():
        for file in layouts_dir.glob('*_v*.html'):
            files_to_version['layouts'].append(file)
    
    # Find include files
    includes_dir = Path('_includes')
    if includes_dir.exists():
        for file in includes_dir.glob('*_v*.html'):
            files_to_version['includes'].append(file)
    
    # Find page files (root directory)
    for file in Path('.').glob('*_v*.md'):
        if file.name != 'README.md':
            files_to_version['pages'].append(file)
    
    for file in Path('.').glob('*_v*.html'):
        if file.name != '404.html':
            files_to_version['pages'].append(file)
    
    # Find post files
    posts_dir = Path('_posts')
    if posts_dir.exists():
        for file in posts_dir.glob('*_v*.md'):
            files_to_version['posts'].append(file)
    
    # Find CSS files
    css_dir = Path('public/css')
    if css_dir.exists():
        for file in css_dir.glob('*_v*.css'):
            files_to_version['css'].append(file)
    
    return files_to_version

def rename_file_with_version(file_path, new_version):
    """Rename a file to include the new version."""
    if not file_path.exists():
        return False
    
    # Extract the base name and extension
    name_parts = file_path.stem.split('_v')
    if len(name_parts) != 2:
        print(f"Warning: {file_path} doesn't follow versioning pattern, skipping...")
        return False
    
    base_name = name_parts[0]
    extension = file_path.suffix
    new_filename = f"{base_name}_v{new_version}{extension}"
    new_path = file_path.parent / new_filename
    
    try:
        # Remove old versioned file if it exists
        if new_path.exists():
            new_path.unlink()
        
        # Rename current file
        file_path.rename(new_path)
        print(f"✓ Renamed: {file_path.name} → {new_filename}")
        return True
    except Exception as e:
        print(f"✗ Error renaming {file_path.name}: {e}")
        return False

def create_new_versioned_files(version):
    """Create new versioned files from non-versioned ones."""
    version_str = get_version_string(version)
    
    # Files to create with versioning
    files_to_create = [
        # Layouts
        ('_layouts/default.html', f'_layouts/default_{version_str}.html'),
        ('_layouts/page.html', f'_layouts/page_{version_str}.html'),
        ('_layouts/post.html', f'_layouts/post_{version_str}.html'),
        
        # Includes
        ('_includes/head.html', f'_includes/head_{version_str}.html'),
        ('_includes/sidebar.html', f'_includes/sidebar_{version_str}.html'),
        
        # Pages
        ('about.md', f'about_{version_str}.md'),
        ('career.md', f'career_{version_str}.md'),
        ('projects.md', f'projects_{version_str}.md'),
        ('stories.md', f'stories_{version_str}.md'),
        ('blog.html', f'blog_{version_str}.html'),
        
        # CSS
        ('public/css/hyde.css', f'public/css/hyde_{version_str}.css'),
    ]
    
    created_count = 0
    for source, dest in files_to_create:
        source_path = Path(source)
        dest_path = Path(dest)
        
        if source_path.exists() and not dest_path.exists():
            try:
                # Create directory if it doesn't exist
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy the file
                shutil.copy2(source_path, dest_path)
                print(f"✓ Created: {dest}")
                created_count += 1
            except Exception as e:
                print(f"✗ Error creating {dest}: {e}")
    
    return created_count

def update_layout_references(version):
    """Update all layout references in files to use the new version."""
    version_str = get_version_string(version)
    
    # Files that might contain layout references
    files_to_update = [
        'index.html',
        '404.html',
        'blog.html',
        'about.md',
        'career.md',
        'projects.md',
        'stories.md',
        '_layouts/page.html',
        '_layouts/post.html',
        '_includes/head.html',
        '_includes/sidebar.html'
    ]
    
    # Add all files in _posts directory
    posts_dir = Path('_posts')
    if posts_dir.exists():
        for post_file in posts_dir.glob('*.md'):
            files_to_update.append(str(post_file))
    
    updated_count = 0
    for file_path in files_to_update:
        path = Path(file_path)
        if not path.exists():
            continue
        
        try:
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Update layout references
            original_content = content
            
            # Update layout: default to layout: default_v{{ site.version }}
            content = re.sub(
                r'layout:\s*default\b',
                f'layout: default_{version_str}',
                content
            )
            
            # Update layout: page to layout: page_v{{ site.version }}
            content = re.sub(
                r'layout:\s*page\b',
                f'layout: page_{version_str}',
                content
            )
            
            # Update layout: post to layout: post_v{{ site.version }}
            content = re.sub(
                r'layout:\s*post\b',
                f'layout: post_{version_str}',
                content
            )
            
            # Update include references
            content = re.sub(
                r'{%\s*include\s+([^}]+)\.html\s*%}',
                f'{{% include \\1_{version_str}.html %}}',
                content
            )
            
            # Update CSS references
            content = re.sub(
                r'href="[^"]*hyde\.css([^"]*)"',
                f'href="{{ site.baseurl }}public/css/hyde_{version_str}.css\\1"',
                content
            )
            
            if content != original_content:
                with open(path, 'w', encoding='utf-8') as file:
                    file.write(content)
                print(f"✓ Updated: {file_path}")
                updated_count += 1
                
        except Exception as e:
            print(f"✗ Error updating {file_path}: {e}")
    
    return updated_count

def main():
    """Main function to orchestrate the versioning process."""
    print("🔄 Version Files Script")
    print("=" * 50)
    
    # Load configuration
    version = load_config()
    if not version:
        return
    
    print(f"📋 Current version: {version}")
    version_str = get_version_string(version)
    print(f"📋 Version string: {version_str}")
    print()
    
    # Step 1: Create new versioned files
    print("📁 Step 1: Creating new versioned files...")
    created_count = create_new_versioned_files(version)
    print(f"   Created {created_count} new versioned files")
    print()
    
    # Step 2: Find and rename existing versioned files
    print("🔄 Step 2: Renaming existing versioned files...")
    files_to_version = find_files_with_version_patterns()
    
    total_renamed = 0
    for category, files in files_to_version.items():
        if files:
            print(f"   {category.capitalize()}:")
            for file_path in files:
                if rename_file_with_version(file_path, version):
                    total_renamed += 1
            print()
    
    print(f"   Renamed {total_renamed} files")
    print()
    
    # Step 3: Update layout references
    print("🔧 Step 3: Updating layout references...")
    updated_count = update_layout_references(version)
    print(f"   Updated {updated_count} files")
    print()
    
    print("✅ Versioning complete!")
    print(f"📝 All files now use version: {version_str}")
    print()
    print("💡 Next steps:")
    print("   1. Review the changes")
    print("   2. Test your site with: bundle exec jekyll build")
    print("   3. Commit the changes to git")

if __name__ == "__main__":
    main() 