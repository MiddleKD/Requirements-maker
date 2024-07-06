import os
import json
import subprocess

class PackageFilter:
    def __init__(self, project_path, necessary_packages, output_file="requirements.txt"):
        """
        PackageFilter 클래스는 주어진 프로젝트 경로에서 필요한 패키지들을 추출하여 requirements.txt 파일로 출력합니다.
        프로젝트에서 import된 패키지, 설치된 패키지, 의존성 패키지를 모두 고려합니다. 프로젝트를 실행하기 위해 정말 필요한 패키지들만 필터링합니다.

        Args:
        - project_path (str): 프로젝트 디렉토리 경로
        - necessary_packages (dict): 추가해야 할 필수 패키지 목록
        - output_file (str): 출력할 requirements.txt 파일 경로 (기본값: 'requirements.txt')
        """
        self.project_path = project_path
        self.output_file = output_file
        self.necessary_packages = necessary_packages

    def run_command(self, command):
        """
        주어진 쉘 명령어를 실행하고 결과를 반환합니다.

        Args:
        - command (str): 실행할 쉘 명령어

        Returns:
        - str: 명령어 실행 결과 (표준 출력)
        
        Raises:
        - Exception: 명령어 실행 실패 시 예외 발생
        """
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        if result.returncode != 0:
            raise Exception(f"Command failed: {command}\n{result.stderr}")
        return result.stdout

    def get_installed_packages(self):
        """
        현재 환경에 설치된 모든 패키지와 그 버전을 사전 형태로 반환합니다.

        Returns:
        - dict: 설치된 패키지 이름을 키로 하고 버전 정보를 값으로 하는 사전
        """
        output = self.run_command("pip freeze")
        return {line.split('==')[0]: line for line in output.splitlines()}

    def get_project_dependencies(self):
        """
        프로젝트의 의존성 패키지 목록을 추출하여 반환합니다.
        pipreqs 패키지를 사용합니다. 여기서 .py 파일이 포함되지 않은 디렉토리는 무시해 디렉토리와 패키지 이름이 충돌하는 현상을 최소화합니다.

        Returns:
        - set: 프로젝트에 필요한 패키지 이름 집합
        """
        ignore_dirs = self._get_dirs_without_py()
        ignore_option = "--ignore " + ",".join(f'"{dir}"' for dir in ignore_dirs)
        self.run_command(f"pipreqs {self.project_path} --force --savepath requirements_temp.txt {ignore_option}")

        with open("requirements_temp.txt", "r") as file:
            project_requirements = {line.split('==')[0] for line in file}
        os.remove("requirements_temp.txt")
        return project_requirements

    def get_dependency_tree(self):
        """
        현재 환경의 패키지 의존성 트리를 JSON 형식으로 추출하여 반환합니다.
        pipdeptree 패키지를 사용합니다.

        Returns:
        - dict: 패키지 의존성 트리 (JSON 형식)
        """
        output = self.run_command("pipdeptree --json")
        return json.loads(output)

    def filter_needed_packages(self):
        """
        필요한 패키지들만을 필터링하여 반환합니다.
        프로젝트에서 import된 패키지, 설치된 패키지, 의존성 패키지를 모두 고려합니다.
        정말 필요한 패키지들만 필터링합니다.

        Returns:
        - dict: 필요한 패키지 이름을 키로 하고 설치된 패키지 정보를 값으로 하는 사전
        """
        print("get installed packages from env...")
        installed_packages = self.get_installed_packages()
        print("get imported packages on project...")
        project_dependencies = self.get_project_dependencies()
        print("get dependecy tree from env...")
        dependency_tree = self.get_dependency_tree()

        needed_packages = set()

        def add_package(package_name):
            # 패키지가 project_dependencies에 없다면 스킵
            if package_name in project_dependencies and package_name not in needed_packages:
                needed_packages.add(package_name)
                for dependency in dependency_tree:
                    # 패키지를 설치하기 위한 dependency_tree를 탐색하여 필요한 모든 패키지를 recursive하게 추가
                    if dependency['package']['key'] == package_name:
                        for req in dependency.get('dependencies', []):
                            add_package(req['package_name'])

        print("filter needed packages...")
        for package in project_dependencies:
            add_package(package)
        
        # 패키지의 설치 명령어와 패키지 이름이 '_'나 '-'로 통일되지 않았을 때 처리하여 반환
        return {
            pkg: installed_packages[pkg] if pkg in installed_packages else installed_packages[pkg.replace("_", "-")]
            for pkg in needed_packages
            if pkg.replace("_", "-") in installed_packages
        }

    def _remove_cuda_postfix(self, package_dict):
        """
        패키지 이름에서 CUDA postfix(ex: +cu121)를 제거한 사전을 반환합니다.
        pip install -r requirements.txt에서 해당 postfix가 있으면 작동하지 않는 현상을 고려한 것.

        Args:
        - package_dict (dict): 패키지 이름을 키로 하고 버전 정보를 값으로 하는 사전

        Returns:
        - dict: CUDA 포스트픽스가 제거된 패키지 정보를 담은 사전
        """
        cleaned_package_dict = {}
        for pkg, value in package_dict.items():
            cleaned_package_dict[pkg] = value.split("+cu")[0]
        return cleaned_package_dict

    def _get_dirs_without_py(self):
        """
        프로젝트 디렉토리에서 .py 파일이 없는 디렉토리들의 리스트를 반환합니다.
        pipreq는 디렉토리 이름과 패키지 이름이 같을 경우 해당 패키지를 목록화하지 않습니다.
        여기서는 .py가 없는 디렉토리는 무시하여 중요한 패키지를 빠트릴 확률을 낮춥니다.

        Returns:
        - list: .py 파일이 없는 디렉토리 이름 리스트
        """
        dirs_without_py_files = set()

        for dirpath, _, filenames in os.walk(self.project_path):
            dir_name = os.path.basename(dirpath)
            if not any(file.endswith('.py') for file in filenames):
                dirs_without_py_files.add(dir_name)
            else:
                if dir_name in dirs_without_py_files:
                    dirs_without_py_files.remove(dir_name)
                
        return list(dirs_without_py_files)

    def write_requirements_file(self, remove_cuda_postfix=False):
        """
        필요한 패키지들을 requirements.txt 파일에 작성합니다.
        작성과정에서 necessary_packages.txt에 포함된 패키지를 추가합니다.
        패키지 이름: 'pytorch-lightning' 설치 이름: 'lightning'과 같이 패키지 이름과 설치 이름이 다를 경우 유용합니다.

        Args:
        - remove_cuda_postfix (bool): CUDA 포스트픽스를 제거할지 여부 (기본값: False)
        """
        needed_packages = self.filter_needed_packages()
        needed_packages.update(self.necessary_packages)
        if remove_cuda_postfix:
            needed_packages = self._remove_cuda_postfix(needed_packages)
        
        print(f"write {self.output_file}...")
        with open(self.output_file, "w") as file:
            for package in needed_packages.values():
                file.write(f"{package}\n")
