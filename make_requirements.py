
import subprocess
import json
from pathlib import Path

class PackageFilter:
    def __init__(self, project_path, necessary_package_list, output_file="requirements_production.txt"):
        self.project_path = project_path
        self.output_file = output_file
        self.necessary_package_list = necessary_package_list

    def run_command(self, command):
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        if result.returncode != 0:
            raise Exception(f"Command failed: {command}\n{result.stderr}")
        return result.stdout

    def get_installed_packages(self):
        output = self.run_command("pip freeze")
        return {line.split('==')[0]: line for line in output.splitlines()}

    def get_project_dependencies(self):
        self.run_command(f"pipreqs {self.project_path} --force --savepath requirements_temp.txt")
        with open("requirements_temp.txt", "r") as file:
            project_requirements = {line.split('==')[0] for line in file}
        Path("requirements_temp.txt").unlink()
        return project_requirements

    def get_dependency_tree(self):
        output = self.run_command("pipdeptree --json")
        return json.loads(output)

    def filter_needed_packages(self):
        installed_packages = self.get_installed_packages()
        project_dependencies = self.get_project_dependencies()
        dependency_tree = self.get_dependency_tree()

        needed_packages = set()

        def add_package(package_name):
            if package_name in project_dependencies and package_name not in needed_packages:
                needed_packages.add(package_name)
                for dependency in dependency_tree:
                    if dependency['package']['key'] == package_name:
                        for req in dependency.get('dependencies', []):
                            add_package(req['package_name'])

        for package in project_dependencies:
            add_package(package)
        
        return {pkg: installed_packages[pkg] for pkg in needed_packages if pkg in installed_packages}

    def write_requirements_file(self):
        needed_packages = self.filter_needed_packages()

        with open(self.output_file, "w") as file:
            for package in needed_packages.values():
                file.write(f"{package}\n")

        with open(self.output_file, "a") as file:
            for package in self.necessary_package_list:
                file.write(f"{package}\n")

        print(f"Filtered requirements written to {self.output_file}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", type=str)
    args = parser.parse_args()

    filter_instance = PackageFilter(
        project_path=args.src, 
        necessary_package_list=[
            "open-clip-torch==2.24.0",
            "lightning==2.2.5",
            "insightface==0.7.3",
            "cupy-cuda12x==12.3.0",
            "python-magic==0.4.27",
            "requests_toolbelt==1.0.0",
        ],
        output_file="requirements_production.txt")
    
    filter_instance.write_requirements_file()
