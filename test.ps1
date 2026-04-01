# PyWeChat Bridge 测试脚本 (Windows)
# 用法: .\test.ps1

$BRIDGE_URL = $env:PYWECHAT_BRIDGE_URL
if (-not $BRIDGE_URL) {
    $BRIDGE_URL = "http://127.0.0.1:8765"
}

Write-Host "=== PyWeChat Bridge 测试 ===" -ForegroundColor Cyan
Write-Host "Bridge URL: $BRIDGE_URL"
Write-Host ""

# 测试服务状态
Write-Host "1. 测试服务状态..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$BRIDGE_URL/" -Method GET -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ 服务运行正常" -ForegroundColor Green
    $response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 3
} catch {
    Write-Host "❌ 服务未运行，请先启动: .\start.bat" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "2. 测试发送消息 (模拟)..." -ForegroundColor Yellow

$body = @{
    to = "测试用户"
    message = "测试消息"
    message_type = "text"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "$BRIDGE_URL/send" -Method POST `
        -ContentType "application/json" -Body $body -TimeoutSec 10

    if ($response.Content -match "success") {
        Write-Host "✅ API 调用正常" -ForegroundColor Green
        Write-Host "响应: $($response.Content)"
    } else {
        Write-Host "⚠️ API 调用返回异常" -ForegroundColor Yellow
        Write-Host "响应: $($response.Content)"
    }
} catch {
    Write-Host "⚠️ API 调用可能失败 (可能是微信未连接)" -ForegroundColor Yellow
    Write-Host "错误: $($_.Exception.Message)"
}

Write-Host ""
Write-Host "=== 测试完成 ===" -ForegroundColor Green
