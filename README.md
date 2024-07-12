# 🎨 Requirements Maker
![git_header](assets/middlek_git_header.png)

꼭 필요한 패키지만 포함한 효율적인 requirements 생성
<!-- ![git_header](assets/favorfit-git-header.png) -->

## 🚀 Introduction
Requirements Maker는 Python 프로젝트의 의존성을 분석하여 최적화된 requirements.txt 파일을 생성하는 도구입니다. 이 도구는 **프로젝트의 import 구문, 가상환경에 설치된 패키지, 그리고 패키지 간의 의존성을 종합적으로 분석**하여 프로젝트 실행에 **꼭 필요한 패키지만을 추출**합니다.

필자는 이 도구를 이용하여 복잡한 프로젝트의 서버(AWS, NCP) 배포 환경을 빠르게 구축하는데 성공했습니다.

## 💡 Features

- 프로젝트 디렉토리 내의 import 구문 분석
- 현재 가상환경에 설치된 패키지 목록 추출
- 패키지 간 의존성 트리 분석
- 프로젝트 실행에 필수적인 패키지만 필터링
- CUDA 관련 postfix 제거 옵션
- 커스텀 필수 패키지 목록 지원

## 📥 Install

1. 이 레포지토리를 클론합니다:
    ```bash
    git clone https://github.com/your-username/requirements_maker.git
    ```
2. 필요한 의존성을 설치합니다:
    ```bash
    pip install -r requirements.txt
    ```
## 🏃🏻‍♂️ How to use
1. 프로젝트를 위한 가상환경을 실행합니다.
    ```bash
    conda activate {your_env} or source .venv.bin.activate
    ```
2. 이 레포지토리의 루트 디렉토리에서 다음 명령어를 실행합니다:
    ```bash
    python main.py --src /path/to/your/project
    ```
    - `--src`: 분석할 프로젝트 디렉토리 경로

3. CUDA postfix를 제거하려면 다음과 같이 실행합니다:
    ```bash
    python main.py --src /path/to/your/project --rm_cuda_postfix
    ```
    패키지 이름에서 CUDA postfix(ex: +cu121)를 제거할 수 있습니다.
    pip install package 중 해당 postfix가 있으면 작동하지 않는 현상을 고려했습니다.
4. 필수 패키지를 추가하려면 `necessary_packages.txt` 파일을 생성하고 패키지를 나열합니다.

## 📋 Output

프로그램은 `requirements_for_{project_name}.txt` 파일을 생성합니다. 이 파일에는 프로젝트 실행에 필요한 최소한의 패키지 목록만을 필터링하여 생성합니다.

## 🛠 Approach

- ### Background: requirements.txt 작성의 시간 소모
    requirements.txt 파일을 수동으로 작성하는 것은 시간이 많이 소요되는 작업입니다. 프로젝트가 커질수록 의존성 관리는 더욱 복잡해지며, 불필요한 패키지를 포함하거나 필수 패키지를 누락할 위험이 있습니다. 단순히 **pip freeze를 사용하기에는 초기 env를 계획적으로 관리해야하기 때문에 실용성이 떨어집니다.** 그리고 pip freeze는 현재 환경의 모든 패키지를 나열하므로, 프로젝트에 직접적으로 필요하지 않은 패키지들도 포함될 수 있어 **의존성 관리를 오히려 더 복잡하게 만들 수 있습니다.** 이는 특히 여러 프로젝트를 동시에 진행하는 개발자들에게 큰 문제가 될 수 있으며, 프로젝트의 이식성과 재현성을 저해할 수 있습니다.

- ### Background: pipreq의 한계
    pipreq는 유용한 도구이지만 몇 가지 한계가 있습니다. 특히 **디렉토리 이름과 패키지 이름을 명확히 구분하지 못하는 문제**가 있습니다. 예를 들어, 'insightface'라는 안면인식 AI 모델 패키지를 사용하면서 동시에 'insightface'라는 이름의 디렉토리에 모델을 저장할 경우, pipreq는 이 패키지를 무시합니다. 또한, 'package name'과 'install name'의 **구분자('-'와 '_')가 일관되지 않을 경우 패키지를 제대로 리스트업하지 못하는 문제**도 있습니다.

- ### Solution
    다음과 같은 개선사항을 구현했습니다:
    1. 디렉토리 처리 개선: .py 파일이 있는 디렉토리만 패키지명보다 우선시하고, 그렇지 않은 경우 해당 디렉토리를 고려 대상에서 제외합니다. 이를 통해 실제 패키지를 더 정확하게 리스트업할 수 있습니다.
    2. 구분자 처리 개선: '-'와 '_' 구분자를 모두 고려하여 패키지를 탐색하는 로직을 추가했습니다. 이로써 다양한 명명 규칙을 가진 패키지들을 정확히 식별할 수 있게 되었습니다.
    3. 의존성 트리 분석: 단순히 import 구문을 분석하는 것을 넘어, 패키지 간의 의존성 트리를 분석하여 필요한 모든 패키지를 포함시킵니다.

## ⚠️ Caution

- 이 도구는 현재 가상환경의 패키지 정보를 사용합니다. **프로젝트에 맞는 가상환경을 활성화**한 상태에서 실행해주세요.
- 일부 복잡한 의존성 관계나 **동적으로 import되는 패키지는 감지하지 못할 수 있습니다.**
- 해당 프로젝트는 `pipreq`와 `pipdeptree` 패키지를 내부적으로 사용합니다.
- 일부 패키지의 경우, 'package name'과 'install name'이 크게 다를 수 있습니다. 예를 들어, `pytorch-lightning`의 경우 실제 설치 명령어는 `lightning`입니다. 이러한 경우 자동 감지가 어려울 수 있습니다. 이 문제를 해결하기 위해, **necessary_packages.txt 파일을 통해 이러한 패키지를 명시적으로 추가**할 수 있습니다.

## 🤝 Contribution

버그 리포트, 기능 제안, 풀 리퀘스트 등 모든 기여를 환영합니다. 문제가 있거나 제안사항이 있으면 이슈를 열어주세요.

## 📄 License
```
MIT License

Copyright (c) 2024 middlek

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
## 📞 Contact
middlek - middlekcenter@gmail.com

<!-- favorfit - lab@favorfit.ai -->