#!/usr/bin/env bash
# 安装 OfficeCLI
# 用法: ./harness/scripts/install-officecli.sh

set -e

echo "============================================"
echo "  OfficeCLI 安装脚本"
echo "============================================"
echo ""

# 检测平台
OS="$(uname -s)"
ARCH="$(uname -m)"

case "${OS}" in
    Linux*)     PLATFORM="linux";;
    Darwin*)    PLATFORM="mac";;
    *)          echo "不支持的操作系统: ${OS}"; exit 1;;
esac

case "${ARCH}" in
    x86_64*)    ARCH_SUFFIX="x64";;
    arm64*)     ARCH_SUFFIX="arm64";;
    aarch64*)   ARCH_SUFFIX="arm64";;
    *)          echo "不支持的架构: ${ARCH}"; exit 1;;
esac

echo "检测到平台: ${PLATFORM}-${ARCH_SUFFIX}"
echo ""

# 方式1: 使用官方安装脚本
echo "方式1: 尝试使用官方安装脚本..."
if command -v curl &> /dev/null; then
    curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.sh | bash || {
        echo "官方脚本安装失败，尝试手动下载..."
    }
else
    echo "curl 未安装，跳过官方脚本"
fi

# 检查是否安装成功
if command -v officecli &> /dev/null; then
    echo ""
    echo "✅ OfficeCLI 安装成功！"
    officecli --version
    exit 0
fi

echo ""
echo "方式2: 手动下载二进制文件..."

# 从 GitHub Releases 下载
VERSION="latest"
BINARY_NAME="officecli-${PLATFORM}-${ARCH_SUFFIX}"
DOWNLOAD_URL="https://github.com/iOfficeAI/OfficeCLI/releases/${VERSION}/download/${BINARY_NAME}"

INSTALL_DIR="${HOME}/.local/bin"
mkdir -p "${INSTALL_DIR}"

echo "下载: ${DOWNLOAD_URL}"
echo "保存到: ${INSTALL_DIR}/officecli"

if command -v curl &> /dev/null; then
    curl -fsSL -o "${INSTALL_DIR}/officecli" "${DOWNLOAD_URL}" || {
        echo "下载失败，请检查网络连接"
        echo "也可以手动从以下地址下载: ${DOWNLOAD_URL}"
        exit 1
    }
elif command -v wget &> /dev/null; then
    wget -q -O "${INSTALL_DIR}/officecli" "${DOWNLOAD_URL}" || {
        echo "下载失败，请检查网络连接"
        exit 1
    }
else
    echo "错误: 未找到 curl 或 wget"
    exit 1
fi

chmod +x "${INSTALL_DIR}/officecli"

# 添加到 PATH（如果还没有）
if [[ ":$PATH:" != *":${INSTALL_DIR}:"* ]]; then
    echo "将 ${INSTALL_DIR} 添加到 PATH..."
    export PATH="${INSTALL_DIR}:$PATH"
    echo 'export PATH="${HOME}/.local/bin:$PATH"' >> ~/.bashrc
fi

echo ""
echo "✅ OfficeCLI 安装完成！"
echo ""

# 验证安装
if command -v officecli &> /dev/null; then
    officecli --version
    echo ""
    echo "运行 'officecli install' 完成自安装（可选）"
else
    echo "⚠️  未找到 officecli 命令，请检查 PATH 配置"
fi
