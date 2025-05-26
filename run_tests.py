#!/usr/bin/env python
"""
自动化测试运行脚本
"""
import os
import sys
import subprocess
import argparse
from datetime import datetime


def run_command(command, description):
    """运行命令并打印结果"""
    print(f"\n{'='*60}")
    print(f"正在执行: {description}")
    print(f"命令: {command}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.stdout:
            print("输出:")
            print(result.stdout)
        
        if result.stderr:
            print("错误:")
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {description} - 成功完成")
        else:
            print(f"❌ {description} - 执行失败 (退出码: {result.returncode})")
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ 执行命令时出错: {e}")
        return False


def run_tests(test_type='all', verbosity=2, keepdb=False, parallel=False):
    """运行测试"""
    base_command = "python manage.py test"
    
    # 构建测试命令
    if test_type == 'unit':
        command = f"{base_command} accounts.tests rooms.tests bookings.tests"
        description = "单元测试"
    elif test_type == 'integration':
        command = f"{base_command} tests.integration_tests"
        description = "集成测试"
    elif test_type == 'performance':
        command = f"{base_command} tests.performance_tests"
        description = "性能测试"
    elif test_type == 'models':
        command = f"{base_command} accounts.tests.UserModelTest rooms.tests.StudyRoomModelTest bookings.tests.BookingModelTest"
        description = "模型测试"
    elif test_type == 'views':
        command = f"{base_command} accounts.tests.UserAuthenticationTest rooms.tests.RoomListViewTest bookings.tests.BookingListViewTest"
        description = "视图测试"
    elif test_type == 'api':
        command = f"{base_command} bookings.tests.BookingAPITest"
        description = "API测试"
    else:
        command = base_command
        description = "所有测试"
    
    # 添加选项
    if verbosity:
        command += f" --verbosity={verbosity}"
    
    if keepdb:
        command += " --keepdb"
    
    if parallel:
        command += " --parallel"
    
    # 添加测试设置
    command += " --settings=study_room_system.settings"
    
    return run_command(command, description)


def generate_coverage_report():
    """生成代码覆盖率报告"""
    commands = [
        ("coverage run --source='.' manage.py test", "运行覆盖率测试"),
        ("coverage report", "生成覆盖率报告"),
        ("coverage html", "生成HTML覆盖率报告")
    ]
    
    success = True
    for command, description in commands:
        if not run_command(command, description):
            success = False
            break
    
    if success:
        print(f"\n📊 覆盖率报告已生成在 htmlcov/index.html")
    
    return success


def run_linting():
    """运行代码检查"""
    commands = [
        ("flake8 .", "Flake8 代码风格检查"),
        ("pylint **/*.py", "Pylint 代码质量检查"),
    ]
    
    success = True
    for command, description in commands:
        print(f"\n尝试运行: {description}")
        try:
            if not run_command(command, description):
                print(f"⚠️  {description} 失败，但继续执行其他检查")
        except Exception as e:
            print(f"⚠️  无法运行 {description}: {e}")
    
    return success


def run_security_checks():
    """运行安全检查"""
    commands = [
        ("python manage.py check --deploy", "Django 部署安全检查"),
        ("bandit -r .", "Bandit 安全漏洞检查"),
        ("safety check", "Safety 依赖安全检查")
    ]
    
    for command, description in commands:
        print(f"\n尝试运行: {description}")
        try:
            run_command(command, description)
        except Exception as e:
            print(f"⚠️  无法运行 {description}: {e}")


def run_all_checks():
    """运行所有检查"""
    print(f"\n🚀 开始完整的自动化测试流程")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success_count = 0
    total_checks = 0
    
    # 1. 运行单元测试
    total_checks += 1
    if run_tests('unit'):
        success_count += 1
    
    # 2. 运行集成测试
    total_checks += 1
    if run_tests('integration'):
        success_count += 1
    
    # 3. 运行性能测试
    total_checks += 1
    if run_tests('performance'):
        success_count += 1
    
    # 4. 生成覆盖率报告
    total_checks += 1
    if generate_coverage_report():
        success_count += 1
    
    # 5. 代码检查
    total_checks += 1
    if run_linting():
        success_count += 1
    
    # 6. 安全检查
    total_checks += 1
    run_security_checks()  # 安全检查可能需要额外工具，不计入成功率
    
    # 总结
    print(f"\n{'='*60}")
    print(f"📋 测试总结")
    print(f"{'='*60}")
    print(f"✅ 成功: {success_count}/{total_checks}")
    print(f"❌ 失败: {total_checks - success_count}/{total_checks}")
    print(f"📊 成功率: {success_count/total_checks*100:.1f}%")
    
    if success_count == total_checks:
        print(f"\n🎉 所有测试都通过了！系统状态良好。")
        return True
    else:
        print(f"\n⚠️  有 {total_checks - success_count} 项检查失败，请检查上述输出。")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='自习室管理系统自动化测试工具')
    
    parser.add_argument(
        'test_type',
        nargs='?',
        default='all',
        choices=['all', 'unit', 'integration', 'performance', 'models', 'views', 'api', 'coverage', 'lint', 'security', 'full'],
        help='测试类型'
    )
    
    parser.add_argument(
        '--verbosity',
        type=int,
        default=2,
        choices=[0, 1, 2, 3],
        help='输出详细级别'
    )
    
    parser.add_argument(
        '--keepdb',
        action='store_true',
        help='保留测试数据库'
    )
    
    parser.add_argument(
        '--parallel',
        action='store_true',
        help='并行运行测试'
    )
    
    args = parser.parse_args()
    
    # 确保在正确的目录中
    if not os.path.exists('manage.py'):
        print("❌ 请在Django项目根目录中运行此脚本")
        sys.exit(1)
    
    print(f"🔧 自习室管理系统自动化测试工具")
    print(f"测试类型: {args.test_type}")
    
    success = True
    
    if args.test_type == 'coverage':
        success = generate_coverage_report()
    elif args.test_type == 'lint':
        success = run_linting()
    elif args.test_type == 'security':
        run_security_checks()
    elif args.test_type == 'full':
        success = run_all_checks()
    else:
        success = run_tests(
            test_type=args.test_type,
            verbosity=args.verbosity,
            keepdb=args.keepdb,
            parallel=args.parallel
        )
    
    if success:
        print(f"\n✅ 测试完成")
        sys.exit(0)
    else:
        print(f"\n❌ 测试失败")
        sys.exit(1)


if __name__ == '__main__':
    main()
