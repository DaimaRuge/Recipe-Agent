.PHONY: install dev test lint format clean run

# 安装依赖
install:
	pip install -e .

# 安装开发依赖
dev:
	pip install -e ".[dev]"
	pre-commit install

# 运行测试
test:
	pytest tests/ -v --cov=src/recipe_agent --cov-report=html

# 代码检查
lint:
	ruff check src/ tests/
	mypy src/

# 格式化代码
format:
	black src/ tests/
	ruff check --fix src/ tests/

# 清理
clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache .coverage htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +

# 运行服务
run:
	uvicorn recipe_agent.main:app --reload --host 0.0.0.0 --port 8000

# Docker 构建
docker-build:
	docker build -t recipe-agent:latest .

# Docker 运行
docker-run:
	docker run -p 8000:8000 recipe-agent:latest
