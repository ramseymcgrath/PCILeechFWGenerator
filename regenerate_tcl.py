#!/usr/bin/env python3
"""
올바른 TCL 스크립트 재생성
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from templating.tcl_builder import TCLBuilder

def regenerate_tcl():
    print("🔧 올바른 hex 형식으로 TCL 스크립트 재생성 중...")
    
    try:
        tcl_builder = TCLBuilder()
        
        # 테스트용 build context 생성
        build_context = tcl_builder.create_build_context(
            board="pcileech_75t484_x1",
            vendor_id=0x10ec,
            device_id=0x8125,
            revision_id=0x04,
            subsys_vendor_id=0x10ec,
            subsys_device_id=0x8125
        )
        
        # TCL 스크립트 생성
        tcl_content = tcl_builder.build_pcileech_project_script(build_context)
        
        # output 디렉터리에 저장
        output_file = "output/vivado_generate_project_fixed.tcl"
        with open(output_file, 'w') as f:
            f.write(tcl_content)
            
        print(f"✅ 수정된 TCL 스크립트 생성됨: {output_file}")
        
        # hex 값 형식 확인
        lines = tcl_content.split('\n')
        for i, line in enumerate(lines):
            if 'CONFIG.Subsystem' in line:
                print(f"   Line {i+1}: {line.strip()}")
                
        return True
        
    except Exception as e:
        print(f"❌ TCL 재생성 실패: {e}")
        return False

if __name__ == "__main__":
    success = regenerate_tcl()
    if success:
        print("\n🎉 이제 다음 명령어로 실행하세요:")
        print("cd output")
        print("vivado -mode batch -source vivado_generate_project_fixed.tcl")
    else:
        print("\n💥 재생성 실패!")
        sys.exit(1)
