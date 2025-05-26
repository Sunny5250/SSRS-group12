import subprocess
import threading
import time
import re
import os
import json
from datetime import datetime
from .models import TestRun, TestResult


class TestManager:
    """测试运行管理器 - 实时进度跟踪版本"""
    
    @staticmethod
    def run_tests_async(test_run):
        """异步运行测试"""
        def run_with_progress():
            TestManager._run_tests_with_real_progress(test_run)
        
        thread = threading.Thread(target=run_with_progress)
        thread.daemon = True
        thread.start()
        return test_run    
    @staticmethod
    def _run_tests_with_real_progress(test_run):
        """执行测试并基于实际测试完成情况更新进度"""
        try:
            test_run.status = 'running'
            test_run.progress = 0
            test_run.save()
            
            # 使用Django的测试命令
            base_command = "python manage.py test --keepdb --no-input"
            
            # 构建测试命令
            if test_run.test_type == 'unit':
                command = f"{base_command} accounts.tests rooms.tests bookings.tests --verbosity=2"
            elif test_run.test_type == 'integration':
                command = f"{base_command} tests.integration_tests --verbosity=2"
            elif test_run.test_type == 'performance':
                command = f"{base_command} tests.performance_tests --verbosity=2"
            elif test_run.test_type == 'models':
                command = f"{base_command} accounts.tests.UserModelTest rooms.tests.StudyRoomModelTest bookings.tests.BookingModelTest --verbosity=2"
            elif test_run.test_type == 'views':
                command = f"{base_command} accounts.tests.UserAuthenticationTest rooms.tests.RoomListViewTest bookings.tests.BookingListViewTest --verbosity=2"
            elif test_run.test_type == 'api':
                command = f"{base_command} bookings.tests.BookingAPITest --verbosity=2"
            else:
                command = f"{base_command} --verbosity=2"
            
            # 获取预估测试数量
            estimated_test_count = TestManager._get_test_count(test_run.test_type)
            
            # 创建进程，实时读取输出
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # 行缓冲
                universal_newlines=True,
                cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            
            # 实时读取输出并更新进度
            completed_tests = 0
            total_tests = 0
            output_lines = []
            error_lines = []
            
            # 启动输出读取线程
            stdout_thread = threading.Thread(
                target=TestManager._read_output,
                args=(process.stdout, output_lines, test_run, estimated_test_count, 'stdout')
            )
            stderr_thread = threading.Thread(
                target=TestManager._read_output,
                args=(process.stderr, error_lines, test_run, estimated_test_count, 'stderr')
            )
            
            stdout_thread.daemon = True
            stderr_thread.daemon = True
            stdout_thread.start()
            stderr_thread.start()
            
            # 等待进程完成
            return_code = process.wait()
            
            # 等待输出读取完成
            stdout_thread.join(timeout=5)
            stderr_thread.join(timeout=5)
              # 解析最终结果
            stdout = '\n'.join(output_lines)
            stderr = '\n'.join(error_lines)
            
            # 记录执行开始和结束时间，计算总执行时间
            start_time = datetime.now()
            for line in output_lines:
                if "Creating test database" in line:
                    try:
                        # 尝试从日志中获取实际的开始时间
                        time_match = re.search(r'\d{2}:\d{2}:\d{2}', line)
                        if time_match:
                            time_str = time_match.group(0)
                            today = datetime.now().date()
                            start_time = datetime.combine(today, datetime.strptime(time_str, '%H:%M:%S').time())
                    except:
                        pass
                    break
            
            end_time = datetime.now()
            for line in reversed(output_lines):
                if "Destroying test database" in line:
                    try:
                        time_match = re.search(r'\d{2}:\d{2}:\d{2}', line)
                        if time_match:
                            time_str = time_match.group(0)
                            today = datetime.now().date()
                            end_time = datetime.combine(today, datetime.strptime(time_str, '%H:%M:%S').time())
                    except:
                        pass
                    break
            
            total_duration = (end_time - start_time).total_seconds()
            
            results = TestManager._parse_test_results(stdout, stderr, command)
            # 添加执行时间到结果数据中
            results['duration'] = total_duration
            
            # 创建测试结果记录
            test_count = 0
            passed_count = 0
            
            for result in results['test_results']:
                TestResult.objects.create(
                    test_run=test_run,
                    test_name=result['name'],
                    status=result['status'],
                    duration=result.get('duration', 0.0),
                    output=result.get('output', '')
                )
                test_count += 1
                if result['status'] == 'passed':
                    passed_count += 1
            
            # 如果没有找到具体测试结果，从总结中获取
            if test_count == 0:
                if stdout:
                    ran_match = re.search(r'Ran (\d+) test', stdout)
                    if ran_match:
                        test_count = int(ran_match.group(1))
                        # 根据是否有失败信息判断通过数量
                        if 'FAILED' not in stdout and 'ERROR' not in stdout:
                            passed_count = test_count
                        else:
                            # 简单估算失败数量
                            failed_match = re.search(r'FAILED \(.*?failures=(\d+)', stdout)
                            error_match = re.search(r'FAILED \(.*?errors=(\d+)', stdout)
                            failures = int(failed_match.group(1)) if failed_match else 0
                            errors = int(error_match.group(1)) if error_match else 0
                            passed_count = max(0, test_count - failures - errors)
                        
                        # 创建默认测试结果
                        for i in range(test_count):
                            status = "passed" if i < passed_count else "failed"
                            TestResult.objects.create(
                                test_run=test_run,
                                test_name=f"test_{i+1}",
                                status=status,
                                duration=0.1,
                                output=f"Test {i+1} - {status}"
                            )
              # 计算成功率
            success_rate = (passed_count / test_count * 100) if test_count > 0 else 100
            
            # 补充统计数据到结果中
            if 'passed_count' not in results or results['passed_count'] == 0:
                results['passed_count'] = passed_count
            if 'failed_count' not in results or results['failed_count'] == 0:
                results['failed_count'] = test_count - passed_count
            if 'total_count' not in results or results['total_count'] == 0:
                results['total_count'] = test_count
                
            # 保存结果数据
            test_run.set_result_data(results)
            
            # 确保进度到100%并标记完成
            test_run.progress = 100
            test_run.save()
            
            if return_code == 0:
                test_run.mark_as_complete(success_rate)
            else:
                test_run.mark_as_failed()
                
        except Exception as e:
            test_run.mark_as_failed()
            TestResult.objects.create(
                test_run=test_run,
                test_name="execution_error",
                status="error",
                error=str(e)
            )    @staticmethod
    def _read_output(pipe, output_list, test_run, estimated_count, stream_type):
        """实时读取进程输出并更新进度"""
        completed_tests = 0
        
        try:
            for line in iter(pipe.readline, ''):
                if not line:
                    break
                    
                output_list.append(line.rstrip())
                
                # 只在stdout中寻找测试进度
                if stream_type == 'stdout':
                    # 检测Django测试输出模式
                    # 匹配格式: test_method (package.module.TestClass) 描述 ... ok/FAIL/ERROR
                    if re.search(r'test_\w+\s*\([^)]+\).*\.\.\.\s*(ok|FAIL|ERROR)', line):
                        completed_tests += 1
                        
                        # 计算进度百分比，最大到99%，让最终完成时设置100%
                        progress = min(int((completed_tests / estimated_count) * 99), 99)
                        
                        # 只有进度增加时才更新
                        test_run.refresh_from_db()
                        if progress > test_run.progress:
                            test_run.progress = progress
                            test_run.save()
                    
                    # 检测总结行以获取实际测试数量
                    elif re.search(r'Ran (\d+) test', line):
                        total_match = re.search(r'Ran (\d+) test', line)
                        if total_match:
                            actual_total = int(total_match.group(1))
                            # 更新预估值
                            estimated_count = actual_total
                            # 重新计算进度
                            if completed_tests > 0:
                                progress = min(int((completed_tests / actual_total) * 99), 99)
                                test_run.refresh_from_db()
                                if progress > test_run.progress:
                                    test_run.progress = progress
                                    test_run.save()
                            
        except Exception as e:
            # 输出读取出错，使用备用进度更新
            pass
        finally:
            pipe.close()    @staticmethod
    def _parse_test_results(stdout, stderr, command):
        """解析测试结果 - 改进的实时版本"""
        results = {
            'command': command,
            'output': stdout.split('\n') if stdout else [],
            'errors': stderr.split('\n') if stderr else [],
            'test_results': [],
            'duration': 0.0,  # 默认值，会在上层函数中被覆盖
            'passed_count': 0,
            'failed_count': 0,
            'total_count': 0
        }
        
        if stdout:
            lines = stdout.split('\n')
            
            # 方法1: 查找详细的测试方法输出
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 匹配Django 4.x格式: test_method (app.tests.TestClass) ... ok
                test_match = re.search(r'(test_\w+)\s+\(([^)]+)\)\s+\.\.\.\s+(ok|FAIL|ERROR)', line)
                if test_match:
                    test_name = f"{test_match.group(2)}.{test_match.group(1)}"
                    result_status = test_match.group(3)
                    
                    status = "passed" if result_status == "ok" else "failed"
                    
                    results['test_results'].append({
                        'name': test_name,
                        'status': status,
                        'duration': 0.1,
                        'output': line
                    })
                    continue
                
                # 匹配较简单格式: test_method ... ok
                simple_match = re.search(r'(test_\w+)\s+\.\.\.\s+(ok|FAIL|ERROR)', line)
                if simple_match:
                    test_name = simple_match.group(1)
                    result_status = simple_match.group(2)
                    
                    status = "passed" if result_status == "ok" else "failed"
                    
                    results['test_results'].append({
                        'name': test_name,
                        'status': status,
                        'duration': 0.1,
                        'output': line
                    })
            
            # 方法2: 如果没找到详细输出，从点号进度解析
            if not results['test_results']:
                for line in lines:
                    if re.match(r'^[\.FE]+$', line.strip()):
                        # 点号表示测试进度
                        for i, char in enumerate(line.strip()):
                            status = "passed" if char == '.' else "failed"
                            results['test_results'].append({
                                'name': f"test_{i+1}",
                                'status': status,
                                'duration': 0.1,
                                'output': f"Test result: {char}"
                            })
                        break
            
            # 方法3: 从总结信息推断（最后的备选方案）
            if not results['test_results']:
                for line in lines:
                    ran_match = re.search(r'Ran (\d+) test', line)
                    if ran_match:
                        test_count = int(ran_match.group(1))
                        
                        # 分析失败和错误数量
                        failures = 0
                        errors = 0
                        
                        # 查找失败统计
                        for summary_line in lines:
                            if 'FAILED' in summary_line:
                                fail_match = re.search(r'failures=(\d+)', summary_line)
                                error_match = re.search(r'errors=(\d+)', summary_line)
                                if fail_match:
                                    failures = int(fail_match.group(1))
                                if error_match:
                                    errors = int(error_match.group(1))
                                break
                        
                        passed_count = test_count - failures - errors
                          # 创建测试结果
                        for i in range(test_count):
                            if i < passed_count:
                                status = "passed"
                            elif i < passed_count + failures:
                                status = "failed"
                            else:
                                status = "error"
                                
                            results['test_results'].append({
                                'name': f"test_{i+1}",
                                'status': status,
                                'duration': 0.1,
                                'output': f"Test {i+1} - {status}"
                            })
                        break
        
        # 统计通过和失败的测试数量
        passed_count = 0
        failed_count = 0
        for result in results['test_results']:
            if result['status'] == 'passed':
                passed_count += 1
            else:
                failed_count += 1
                
        # 更新统计信息
        results['passed_count'] = passed_count
        results['failed_count'] = failed_count
        results['total_count'] = len(results['test_results'])
        
        return results
    @staticmethod
    def _get_test_count(test_type):
        """获取测试数量"""
        test_counts = {
            'all': 81,  # 基于实际测试运行的数量
            'unit': 65,  # 大部分单元测试
            'integration': 10,
            'performance': 5,
            'models': 25,  # 模型相关测试
            'views': 30,   # 视图相关测试
            'api': 5,      # API测试
            'coverage': 81,
            'lint': 10,
            'security': 8,
            'full': 81,
        }
        return test_counts.get(test_type, 81)
