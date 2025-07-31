#!/usr/bin/env python3
"""
Sacred Environment Setup Script for Codex: The Living Scrying Mirror
Consecrates the digital sanctuary and verifies all sacred tools are prepared
"""

import os
import sys
import subprocess
import argparse
import json
from pathlib import Path
from datetime import datetime

# Ceremonial constants
SACRED_GREETING = "Sa-lum-nah, O Guardian Architect"
SETUP_COMPLETE = "🌟 SACRED SETUP RITUAL COMPLETE 🌟"
CEREMONIAL_SEP = "=" * 70
PHASE_SEP = "-" * 50

def print_sacred_header():
    """Display the sacred header for the setup ritual"""
    print("\n" + CEREMONIAL_SEP)
    print("🌀 CODEX: THE LIVING SCRYING MIRROR - SACRED SETUP RITUAL 🌀")
    print(CEREMONIAL_SEP)
    print(f"{SACRED_GREETING}.")
    print("Initiating consecration of the Digital Sanctuary...\n")

def check_python_version(min_version=(3, 13)):
    """Verify required Python version is installed with graceful fallback"""
    print("🔍 Checking Python version...")
    version = sys.version_info
    
    if version.major >= min_version[0] and version.minor >= min_version[1]:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Sacred language ready")
        return True
    else:
        print(f"⚠️ Python {version.major}.{version.minor}.{version.micro} found")
        print(f"   Recommendation: Python {min_version[0]}.{min_version[1]}+ required for full sacred protocols")
        print("   Proceeding with limited ceremony - some advanced features may be constrained")
        return False

def check_docker():
    """Verify Docker Desktop is installed and running with enhanced diagnostics"""
    print("🔍 Checking Docker installation...")
    try:
        version_result = subprocess.run(
            ['docker', '--version'], 
            capture_output=True, 
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        
        if version_result.returncode == 0:
            print(f"✅ Docker found: {version_result.stdout.strip()}")
            
            # Check Docker daemon status
            daemon_result = subprocess.run(
                ['docker', 'info'],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            if daemon_result.returncode == 0:
                print("   Docker daemon is running - Container sanctuary ready")
                return True
            else:
                print("⚠️ Docker installed but daemon not running")
                print("   Please start Docker Desktop and ensure the whale icon is active")
                return False
        else:
            print("❌ Docker not found in system PATH")
            print("   Visit https://www.docker.com/products/docker-desktop to install")
            return False
    except Exception as e:
        print(f"❌ Docker check failed: {str(e)}")
        return False

def check_wsl():
    """Verify WSL 2 is available with platform-aware messaging"""
    if os.name != 'nt':  # Not Windows
        print("🔍 WSL check: Not required on non-Windows systems")
        return True

    print("🔍 Checking WSL 2 status...")
    try:
        result = subprocess.run(
            ['wsl', '--status'],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        if result.returncode == 0:
            if "version: 2" in result.stdout.lower():
                print("✅ WSL 2 is available - Linux integration ready")
                return True
            else:
                print("⚠️ WSL found but version 2 not confirmed")
                print("   Consider upgrading with: wsl --update")
                return True
        else:
            print("⚠️ WSL not available")
            print("   Enable with: wsl --install")
            return False
    except FileNotFoundError:
        print("❌ WSL command not found. Please install WSL 2")
        return False
    except Exception as e:
        print(f"❌ WSL check failed: {str(e)}")
        return False

def create_project_structure(base_path="codex-living-mirror"):
    """Create the sacred directory structure with enhanced resilience"""
    print("🏗️ Creating sacred project structure...")
    
    base_dir = Path(base_path)
    directories = [
        "backend/api",
        "backend/core",
        "backend/models",
        "backend/services",
        "frontend/src/components",
        "frontend/src/pages",
        "frontend/src/styles",
        "database/migrations",
        "database/seeds",
        "ai-guardians/kel-torun",
        "ai-guardians/xah-moru",
        "encryption/ml-kem",
        "tests/unit",
        "tests/integration",
        "docker/dev",
        "docker/prod",
        "scripts/setup",
        "scripts/deploy",
        "docs/api",
        "docs/ceremonies"
    ]
    
    created_count = 0
    try:
        base_dir.mkdir(exist_ok=True)
        
        for directory in directories:
            full_path = base_dir / directory
            full_path.mkdir(parents=True, exist_ok=True)
            
            # Create __init__.py files for Python packages
            if any(part in directory for part in ['backend', 'ai-guardians']):
                init_file = full_path / "__init__.py"
                if not init_file.exists():
                    init_file.touch()
                    created_count += 1
        
        print(f"✅ Sacred structure created with {len(directories)} directories")
        print(f"   Location: {base_dir.absolute()}")
        return True
    except Exception as e:
        print(f"❌ Error creating project structure: {str(e)}")
        return False

def create_virtual_environment(venv_name="codex_env", base_path="codex-living-mirror"):
    """Create and prepare the sacred Python environment with cross-platform support"""
    print("🔮 Creating sacred Python environment...")
    
    project_dir = Path(base_path)
    venv_path = project_dir / venv_name
    
    try:
        # Create virtual environment
        subprocess.run(
            [sys.executable, "-m", "venv", str(venv_path)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Determine activation commands
        activation_guide = "\n   To activate:\n"
        if os.name == 'nt':  # Windows
            activation_guide += f"     cd {base_path}\n     .\\{venv_name}\\Scripts\\activate"
            pip_path = venv_path / "Scripts" / "pip.exe"
        else:  # Unix/Linux/MacOS
            activation_guide += f"     cd {base_path}\n     source ./{venv_name}/bin/activate"
            pip_path = venv_path / "bin" / "pip"
        
        print(f"✅ Virtual environment '{venv_name}' created")
        print(activation_guide)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating virtual environment: {str(e)}")
        print("   Ensure virtualenv module is available: python -m pip install virtualenv")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def create_requirements_file(base_path="codex-living-mirror"):
    """Create the requirements.txt with sacred dependencies"""
    print("📜 Creating sacred dependencies manifest...")
    
    requirements = [
        "# Sacred Dependencies for Codex: The Living Scrying Mirror",
        f"# Generated on {datetime.now().isoformat()}",
        "",
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.4.0",
        "python-multipart>=0.0.6",
        "supabase>=2.0.0",
        "python-dotenv>=1.0.0",
        "cryptography>=41.0.0",
        "pytest>=7.4.0",
        "pytest-asyncio>=0.21.0",
        "httpx>=0.25.0",  # For testing FastAPI
        "black>=23.0.0",  # Code formatting
        "flake8>=6.0.0",  # Linting
        "loguru>=0.7.0",  # Enhanced logging
        "python-dateutil>=2.8.2",  # Date handling
        "jsonschema>=4.19.0"  # Configuration validation
    ]
    
    try:
        requirements_path = Path(base_path) / "requirements.txt"
        with open(requirements_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(requirements))
        
        print(f"✅ Requirements file created: {requirements_path}")
        return True
    except Exception as e:
        print(f"❌ Error creating requirements file: {str(e)}")
        return False

def create_sacred_charter(base_path="codex-living-mirror"):
    """Create the SACRED_CHARTER.md documentation file with updated principles"""
    print("📖 Creating Sacred Charter documentation...")
    
    charter_content = f"""# SACRED_CHARTER.md

# Codex: The Living Scrying Mirror - Sacred Development Charter

*Sa-lum-nah, O Guardians of the Living Mirror.*

### Sacred Mission

The Codex serves as a digital sanctuary for spiritual practice, honoring indigenous wisdom while embracing technological sovereignty. Every line of code is written with reverence for both ancient knowledge and cutting-edge innovation.

### Guiding Principles

#### OCAP (Ownership, Control, Access, Possession)
- Indigenous communities maintain ownership of their cultural knowledge
- Control over how knowledge is shared and represented
- Access decisions remain with knowledge holders
- Possession of data sovereignty is non-negotiable

#### CARE (Collective Benefit, Authority to Control, Responsibility, Ethics)
- Collective benefit for communities takes precedence over individual gain  
- Authority to control data remains with originating communities  
- Responsibility for ethical use guides all development decisions  
- Ethics of reciprocity and respectful relationship building  

### 6 Sacred Circle Roles

#### Spiritual Technologist
- Develops backend systems with reverence for data sanctity  
- Implements quantum-safe encryption (ML-KEM 1024)  
- Ensures AI guardians serve wisdom, not replace it  

#### Indigenous Knowledge Keeper
- Validates cultural integrity and protocol adherence  
- Guides OCAP/CARE implementation  
- Reviews ceremonial integration for authenticity  

#### UX/UI Alchemist
- Crafts interfaces that honor sacred design principles  
- Ensures accessibility across all abilities and backgrounds  
- Integrates indigenous symbolism with contemporary usability  

### Development Log

#### Setup Phase - {datetime.now().strftime("%Y-%m-%d")}
- Digital sanctuary environment consecrated  
- Sacred project structure established  
- Virtual environment prepared for ceremonial coding  
- Dependencies manifest created for sacred tools  

#### Next Phases
- [ ] Backend API foundation with FastAPI  
- [ ] Supabase integration for data sovereignty  
- [ ] AI Guardians implementation (KEL-TORUN, XAH-MORU)  
- [ ] Frontend sanctuary interface  
- [ ] Community feedback integration  

### Ceremonial Notes

*Use this space to document insights, obstacles, and sacred inspirations throughout development...*

---

**Sa-lum-nah** - May this code serve the highest good and honor all relations.
"""
    
    try:
        charter_path = Path(base_path) / "SACRED_CHARTER.md"
        with open(charter_path, 'w', encoding='utf-8') as f:
            f.write(charter_content)
        
        print(f"✅ Sacred Charter created: {charter_path}")
        return True
    except Exception as e:
        print(f"❌ Error creating Sacred Charter: {str(e)}")
        return False

def create_env_template(base_path="codex-living-mirror"):
    """Create .env.template file for environment variables"""
    print("🔐 Creating environment template...")
    
    env_template = """# Codex: The Living Scrying Mirror - Environment Variables

# Copy this file to .env and fill in your sacred credentials

# ===== SUPABASE CONFIGURATION =====
SUPABASE_URL=your_supabase_url_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here

# ===== DATABASE CONFIGURATION =====
# (For local PostgreSQL development)
DATABASE_URL=postgresql://username:password@localhost:5432/codex_db

# ===== AI GUARDIAN CONFIGURATION =====
KEL_TORUN_SENSITIVITY=0.65  # Bias detection threshold
XAH_MORU_EMOTION_MODEL=default  # Emotional analysis model

# ===== APPLICATION SETTINGS =====
DEBUG=True
SECRET_KEY=your_secret_key_here
ALLOWED_HOSTS=localhost,127.0.0.1
TIMEZONE=UTC
LOG_LEVEL=INFO

# ===== CEREMONIAL PARAMETERS =====
RITUAL_MODE=standard  # [standard | advanced | minimal]
GUARDIAN_INVOCATION_DELAY=0.5  # Seconds between guardian activations
"""
    
    try:
        env_path = Path(base_path) / ".env.template"
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(env_template)
        
        print(f"✅ Environment template created: {env_path}")
        print("   Remember to create .env with actual credentials")
        return True
    except Exception as e:
        print(f"❌ Error creating environment template: {str(e)}")
        return False

def create_gitignore(base_path="codex-living-mirror"):
    """Create .gitignore file for the project with comprehensive patterns"""
    print("🔒 Creating sacred .gitignore...")
    
    gitignore_content = """# Codex: The Living Scrying Mirror - Git Ignore Rules

# ===== ENVIRONMENT/CONFIGURATION =====
.env
*.env
.env.local
config_secret.json

# ===== PYTHON ARTIFACTS =====
__pycache__/
*.py[cod]
*$py.class
*.so
.python-version
.pytest_cache/
.mypy_cache/

# Virtual environments
.env/
venv/
codex_env/
ENV/
env.bak/
venv.bak/

# ===== DEVELOPMENT TOOLS =====
.vscode/
.idea/
*.swp
*.swo
*~
*.log
logs/

# ===== SYSTEM ARTIFACTS =====
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# ===== BUILD/DEPLOYMENT =====
dist/
build/
*.egg-info/
*.egg
.coverage
.coverage.*
htmlcov/

# ===== DATABASE =====
*.db
*.sqlite3
*.sqlite
*.dump

# ===== MEDIA/STORAGE =====
media/
uploads/
staticfiles/

# ===== NOTEBOOKS =====
*.ipynb_checkpoints

# ===== AI/MODELS =====
*.h5
*.pth
*.pt
*.joblib
*.pkl
"""
    
    try:
        gitignore_path = Path(base_path) / ".gitignore"
        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        
        print(f"✅ .gitignore created: {gitignore_path}")
        return True
    except Exception as e:
        print(f"❌ Error creating .gitignore: {str(e)}")
        return False

def init_git_repository(base_path="codex-living-mirror"):
    """Initialize Git repository with ceremonial first commit"""
    print("📘 Initializing sacred Git repository...")
    
    try:
        os.chdir(base_path)
        
        # Initialize repository
        subprocess.run(
            ['git', 'init'], 
            check=True, 
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Add all files
        subprocess.run(
            ['git', 'add', '.'], 
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Create sacred first commit
        commit_message = (
            "feat: 🌀 Sacred initialization: Digital sanctuary consecrated\n\n"
            "Sa-lum-nah - The Codex: Living Scrying Mirror begins its manifestation.\n"
            "Sacred structure established, dependencies blessed, charter inscribed."
        )
        
        subprocess.run(
            ['git', 'commit', '-m', commit_message],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        os.chdir("..")
        print("✅ Sacred Git repository initialized with blessed first commit")
        return True
    except subprocess.CalledProcessError as e:
        os.chdir("..")
        print(f"⚠️ Git command failed: {str(e)}")
        return False
    except Exception as e:
        os.chdir("..")
        print(f"❌ Unexpected error with Git: {str(e)}")
        return False

def print_next_steps(successful_steps, base_path="codex-living-mirror"):
    """Print ceremonial next steps based on successful setup actions"""
    print("\n" + CEREMONIAL_SEP)
    print(f"{SETUP_COMPLETE} - {successful_steps}/9 STEPS SUCCEEDED")
    print(CEREMONIAL_SEP)
    
    if successful_steps >= 6:
        print("✅ Digital sanctuary successfully consecrated!")
        print("\n🌀 Next sacred steps:")
        print(f"1. cd {base_path}")
        
        if successful_steps >= 3:  # If venv was created
            print("2. Activate your environment:")
            if os.name == 'nt':  # Windows
                print(f"   .\\codex_env\\Scripts\\activate")
            else:
                print(f"   source ./codex_env/bin/activate")
                
            if successful_steps >= 4:  # If requirements were created
                print("3. Install sacred dependencies:")
                print("   pip install -r requirements.txt")
                
        print("4. Begin the sacred coding ritual with:")
        print("   cd backend")
        print("   python main.py")
    else:
        print("⚠️ Partial consecration - review errors above")
        print("   Some components may require manual setup")
    
    print("\n🧿 Sa-lum-nah - May your code serve the highest good")
    print(CEREMONIAL_SEP)

def main():
    """Main setup ritual orchestrator with ceremonial flow"""
    parser = argparse.ArgumentParser(description="Consecrate the Digital Sanctuary")
    parser.add_argument('--base-dir', default="codex-living-mirror", help="Project base directory")
    args = parser.parse_args()
    
    print_sacred_header()
    successful_steps = 0
    base_path = args.base_dir

    # Phase 1: Environment Verification
    print("🔍 PHASE I: SACRED ENVIRONMENT VERIFICATION")
    print(PHASE_SEP)
    
    if check_python_version():
        successful_steps += 1
    
    if check_docker():
        successful_steps += 1
    
    if check_wsl():
        successful_steps += 1

    # Phase 2: Project Structure Creation
    print("\n🏗️ PHASE II: SACRED STRUCTURE MANIFESTATION")
    print(PHASE_SEP)
    
    if create_project_structure(base_path):
        successful_steps += 1
    
    if create_virtual_environment(base_path=base_path):
        successful_steps += 1
    
    if create_requirements_file(base_path):
        successful_steps += 1
    
    if create_sacred_charter(base_path):
        successful_steps += 1

    # Phase 3: Configuration and Documentation
    print("\n📜 PHASE III: SACRED CONFIGURATION")
    print(PHASE_SEP)
    
    if create_env_template(base_path):
        successful_steps += 1
    
    if create_gitignore(base_path):
        successful_steps += 1

    # Optional Git initialization
    try:
        git_check = subprocess.run(
            ["git", "--version"], 
            capture_output=True, 
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        if git_check.returncode == 0:
            if init_git_repository(base_path):
                successful_steps += 1
        else:
            print("ℹ️ Git not available - repository initialization skipped")
    except FileNotFoundError:
        print("ℹ️ Git not found - repository initialization skipped")

    print_next_steps(successful_steps, base_path)

if __name__ == "__main__":
    main()