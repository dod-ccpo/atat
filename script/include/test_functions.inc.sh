# test_functions.inc.sh: Functions used by the run_test script

run_python_lint() {
  local python_files="${1}"

  run_command "pylint ${python_files}"
  return $?
}

run_python_typecheck() {
  run_command "mypy --ignore-missing-imports --follow-imports=skip atat/domain/csp/cloud/__init__.py"
  return $?
}

run_python_static_analysis() {
  local python_files="${1}"

  run_command "bandit -c ./.bandit_config -r ${python_files}"
  return $?
}

run_python_unit_tests() {
  run_command "python -m pytest -s --cov-report=xml --ignore=celery_tests"
  return $?
}

run_python_render_vue_component() {
  run_command "python -m pytest tests/render_vue_component.py --no-cov --show-capture=no --tb=no -q --disable-warnings"
  return $?
}

run_javascript_tests() {
  run_command "yarn test:coverage"
  return $?
}

run_celery_tests() {
  run_celery
  run_command "python -m pytest celery_tests/test_celery_check.py --no-cov"
  stop_celery
  return $?
}

run_celery() {
  ../dev_queue
  return $?
}

stop_celery() {
  pkill -9 -f 'celery worker'
  return $?
}