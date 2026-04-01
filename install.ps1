# PyWeChat for OpenClaw 安装脚本 (Windows)
# 以管理员身份运行 PowerShell 后执行: .\install.ps1

$ErrorActionPreference = "Stop"
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "=== PyWeChat for OpenClaw 安装 ===" -ForegroundColor Cyan
Write-Host ""

# 检查 Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "❌ 错误: 未找到 Python，请先安装 Python 3.8+" -ForegroundColor Red
    Write-Host "   下载地址: https://www.python.org/downloads/"
    exit 1
}

$PYTHON_VERSION = & python --version 2>&1
Write-Host "✅ Python 版本: $PYTHON_VERSION" -ForegroundColor Green

# 检查 pip
$pip = Get-Command pip -ErrorAction SilentlyContinue
if (-not $pip) {
    Write-Host "❌ 错误: 未找到 pip" -ForegroundColor Red
    exit 1
}
Write-Host "✅ pip 已安装" -ForegroundColor Green

# 安装 Python 依赖
Write-Host ""
Write-Host "=== 安装 Python 依赖 ===" -ForegroundColor Cyan
Set-Location $SCRIPT_DIR
pip install -q -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Python 依赖安装完成" -ForegroundColor Green
} else {
    Write-Host "⚠️ 部分依赖安装失败" -ForegroundColor Yellow
}

# 安装 pywechat
Write-Host ""
Write-Host "=== 安装 PyWeChat ===" -ForegroundColor Cyan
pip install -q pywin32 comtypes 2>$null

# 尝试克隆并安装 pywechat
$PYWECHAT_PATH = "$env:USERPROFILE\Documents\pywechat"
if (-not (Test-Path $PYWECHAT_PATH)) {
    Write-Host "正在克隆 pywechat..." -ForegroundColor Yellow
    git clone https://github.com/Hello-Mr-Crab/pywechat.git $PYWECHAT_PATH 2>$null
    if (Test-Path $PYWECHAT_PATH) {
        Set-Location $PYWECHAT_PATH
        pip install -e . -q
        Write-Host "✅ PyWeChat 安装完成" -ForegroundColor Green
    } else {
        Write-Host "⚠️ PyWechat 克隆失败，将使用模拟模式" -ForegroundColor Yellow
    }
} else {
    Write-Host "✅ PyWeChat 已存在: $PYWECHAT_PATH" -ForegroundColor Green
}

# 添加防火墙规则
Write-Host ""
Write-Host "=== 配置 Windows 防火墙 ===" -ForegroundColor Cyan
$firewallRule = Get-NetFirewallRule -DisplayName "PyWeChat Bridge" -ErrorAction SilentlyContinue
if (-not $firewallRule) {
    try {
        New-NetFirewallRule -DisplayName "PyWeChat Bridge" -Direction Inbound -Protocol TCP -LocalPort 8765 -Action Allow | Out-Null
        Write-Host "✅ 防火墙规则已添加 (端口 8765)" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ 无法添加防火墙规则，请以管理员身份运行" -ForegroundColor Yellow
    }
} else {
    Write-Host "✅ 防火墙规则已存在" -ForegroundColor Green
}

# 显示完成信息
Write-Host ""
Write-Host "=== 安装完成 ===" -ForegroundColor Green
Write-Host ""
Write-Host "使用步骤:" -ForegroundColor Cyan
Write-Host "1. 启动 PyWeChat Bridge:" -ForegroundColor White
Write-Host "   .\start.bat"
Write-Host ""
Write-Host "2. 测试服务:" -ForegroundColor White
Write-Host "   .\test.ps1"
Write-Host ""
Write-Host "3. 打开浏览器访问:" -ForegroundColor White
Write-Host "   http://localhost:8765"
Write-Host ""
Write-Host "更多信息请查看: README.md" -ForegroundColor Gray
