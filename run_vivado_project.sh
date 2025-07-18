#!/bin/bash

echo "🚀 PCILeech Vivado 프로젝트 생성 시작..."

# output 디렉터리로 이동
cd /home/muttti/123/output

# Vivado 환경 확인
if ! command -v vivado &> /dev/null; then
    echo "❌ Vivado를 찾을 수 없습니다. 환경 변수를 설정하세요:"
    echo "source /tools/Xilinx/Vivado/YYYY.X/settings64.sh"
    exit 1
fi

echo "✅ Vivado 환경 확인됨"

# TCL 스크립트 실행
echo "📝 TCL 스크립트 실행 중..."
vivado -mode batch -source vivado_generate_project.tcl -log project_generation.log -journal project_generation.jou

# 결과 확인
if [ -d "vivado_project" ]; then
    echo "🎉 프로젝트 생성 완료!"
    echo "📁 프로젝트 위치: $(pwd)/vivado_project"
    echo "🔍 로그 파일: $(pwd)/project_generation.log"
    echo ""
    echo "프로젝트 열기:"
    echo "vivado $(pwd)/vivado_project/*.xpr"
else
    echo "❌ 프로젝트 생성 실패. 로그를 확인하세요:"
    echo "cat project_generation.log"
    exit 1
fi
