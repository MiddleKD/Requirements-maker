import os
import argparse
from package_filter import PackageFilter

def open_necessary_packages(fn):
    """
    필수 패키지 목록 파일을 열어 사전 형태로 반환합니다.

    Args:
    - fn (str): 필수 패키지 목록 파일 경로

    Returns:
    - dict: 패키지 이름을 키로 하고 패키지 정보를 값으로 하는 사전
    """

    print("load necessary packages...")
    if not os.path.isfile(fn):
        return {}
    
    with open(fn, mode="r") as f:
        pkg_list = f.readlines()
        pkg_list = [cur.strip() for cur in pkg_list]
    return {pkg.split("==")[0]: pkg for pkg in pkg_list}


if __name__ == "__main__":
    # 인자 파싱
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", type=str, help="프로젝트 디렉토리 경로.")
    parser.add_argument("--rm_cuda_postfix", action="store_true", help="패키지 버전에서 CUDA postfix를 제거할지 여부.")
    args = parser.parse_args()

    print("--START MAKE REQUIREMENTS--")
    # 필요한 패키지 파일에서 로드
    necessary_packages = open_necessary_packages("necessary_packages.txt")

    # PackageFilter 인스턴스 생성
    filter_instance = PackageFilter(
        project_path=args.src, 
        necessary_packages=necessary_packages,
        output_file=f"requirements_for_{os.path.basename(args.src)}.txt")
    
    # 필터링된 요구 사항 파일로 저장
    filter_instance.write_requirements_file(remove_cuda_postfix=args.rm_cuda_postfix)
    print("--MAKE REQUIREMENTS DONE--")
