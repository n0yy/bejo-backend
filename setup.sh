#!/bin/bash

# Warna untuk output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
DEFAULT_LLM_MODEL="qwen2.5:3b"
DEFAULT_EMBEDDING_MODEL="nomic-embed-text"
DEFAULT_COMPUTE_TYPE="cpu"

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

show_help() {
    echo "Setup script untuk Bejo Backend dengan dukungan CPU/GPU"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  build           Build dan start services"
    echo "  pull-models     Pull model AI saja"
    echo "  start           Start services yang sudah ada"
    echo "  stop            Stop semua services"
    echo "  clean           Hapus semua containers dan volumes"
    echo "  check-models    Cek status model"
    echo "  list-models     List model yang tersedia"
    echo ""
    echo "Options:"
    echo "  --gpu                    Gunakan GPU (default: CPU)"
    echo "  --cpu                    Gunakan CPU (default)"
    echo "  --llm-model MODEL        Set LLM model (default: $DEFAULT_LLM_MODEL)"
    echo "  --embedding-model MODEL  Set embedding model (default: $DEFAULT_EMBEDDING_MODEL)"
    echo "  --with-model            Download model AI saat build"
    echo "  --help, -h              Show help"
    echo ""
    echo "Model presets:"
    echo "  Small (CPU):     qwen2.5:3b, llama3.2:3b, gemma2:2b"
    echo "  Medium (CPU/GPU): qwen2.5:7b, llama3.2:7b, gemma2:9b"
    echo "  Large (GPU):     qwen2.5:14b, llama3.1:8b, gemma2:27b"
    echo "  Code:           qwen2.5-coder:7b, codellama:13b"
    echo ""
    echo "Examples:"
    echo "  $0 build                                    # Build dengan CPU dan model default"
    echo "  $0 build --gpu --llm-model qwen2.5:7b      # Build dengan GPU dan model 7b"
    echo "  $0 start --gpu                              # Start dengan GPU"
    echo "  $0 pull-models --llm-model llama3.2:7b     # Download model Llama 7b"
    echo ""
    echo "Note: GPU membutuhkan nvidia-docker runtime"
}

check_gpu_support() {
    if command -v nvidia-docker &> /dev/null || docker info | grep -q "nvidia"; then
        print_success "GPU support terdeteksi"
        return 0
    else
        print_warning "GPU support tidak terdeteksi, akan menggunakan CPU"
        return 1
    fi
}

set_environment() {
    local llm_model="${1:-$DEFAULT_LLM_MODEL}"
    local embedding_model="${2:-$DEFAULT_EMBEDDING_MODEL}"
    
    export OLLAMA_LLM_MODEL="$llm_model"
    export OLLAMA_EMBEDDING_MODEL="$embedding_model"
    
    print_info "Environment variables set:"
    print_info "  LLM Model: $OLLAMA_LLM_MODEL"
    print_info "  Embedding Model: $OLLAMA_EMBEDDING_MODEL"
}

get_compose_profile() {
    local compute_type="$1"
    
    if [[ "$compute_type" == "gpu" ]]; then
        if check_gpu_support; then
            echo "gpu"
        else
            print_warning "GPU tidak tersedia, menggunakan CPU"
            echo "cpu"
        fi
    else
        echo "cpu"
    fi
}

check_models() {
    print_info "Checking model status..."
    
    local profile=$(get_compose_profile "$DEFAULT_COMPUTE_TYPE")
    
    if ! docker-compose --profile "$profile" ps ollama | grep -q "Up"; then
        print_error "Ollama service tidak running. Jalankan '$0 start' dulu."
        return 1
    fi
    
    models=$(docker-compose --profile "$profile" exec ollama ollama list 2>/dev/null)
    if [[ $? -eq 0 ]]; then
        print_success "Model yang tersedia:"
        echo "$models"
    else
        print_error "Gagal mengecek model. Pastikan Ollama service running."
    fi
}

list_models() {
    print_info "Daftar model yang direkomendasikan dan pastikan mendukung tools:"
    echo ""
    echo "📱 Small Models (CPU-friendly, <4GB RAM):"
    echo "  • qwen2.5:3b        - Bahasa Indonesia bagus, cepat"
    echo "  • llama3.2:3b       - Umum, stabil"
    echo ""
    echo "🖥️  Medium Models (CPU/GPU, 4-8GB RAM):"
    echo "  • qwen2.5:7b        - Bahasa Indonesia excellent"
    echo "  • llama3.2:7b       - Balanced performance"
    echo ""
    echo "🚀 Large Models (GPU recommended, >8GB RAM):"
    echo "  • qwen2.5:14b       - Bahasa Indonesia terbaik"
    echo "  • llama3.1:8b       - Meta's flagship"
    echo ""
    echo "🧠 Embedding Models:"
    echo "  • nomic-embed-text  - Default, bagus untuk RAG"
    echo "  • all-minilm:l6-v2  - Alternatif ringan"
}

pull_models() {
    local llm_model="$DEFAULT_LLM_MODEL"
    local embedding_model="$DEFAULT_EMBEDDING_MODEL"
    local compute_type="$DEFAULT_COMPUTE_TYPE"
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --llm-model)
                llm_model="$2"
                shift 2
                ;;
            --embedding-model)
                embedding_model="$2"
                shift 2
                ;;
            --gpu)
                compute_type="gpu"
                shift
                ;;
            --cpu)
                compute_type="cpu"
                shift
                ;;
            *)
                shift
                ;;
        esac
    done
    
    local profile=$(get_compose_profile "$compute_type")
    
    print_info "Memulai proses download model AI..."
    print_info "Compute: $compute_type, LLM: $llm_model, Embedding: $embedding_model"
    print_warning "⏳ Proses ini bisa memakan waktu 5-30 menit tergantung model dan koneksi"
    
    # Set environment variables
    set_environment "$llm_model" "$embedding_model"
    
    # Start ollama service dengan profile yang sesuai
    docker-compose --profile "$profile" up -d ollama
    
    # Tunggu ollama ready
    print_info "Menunggu Ollama service ready..."
    local attempts=0
    local max_attempts=40
    
    while ! docker-compose --profile "$profile" exec ollama ollama list > /dev/null 2>&1; do
        attempts=$((attempts + 1))
        if [ $attempts -ge $max_attempts ]; then
            print_error "Ollama service tidak ready setelah 2 menit."
            exit 1
        fi
        echo "😴 Ollama warming up... ($attempts/$max_attempts)"
        sleep 3
    done
    
    print_success "Ollama service ready!"
    
    # Estimate model size
    estimate_model_size "$llm_model"
    
    # Pull models
    print_info "📦 Mengunduh LLM model: $llm_model"
    docker-compose --profile "$profile" exec ollama ollama pull "$llm_model"
    
    print_info "🧠 Mengunduh embedding model: $embedding_model"
    docker-compose --profile "$profile" exec ollama ollama pull "$embedding_model"
    
    print_success "Semua model berhasil didownload!"
    
    # Restart backend service
    print_info "Restart backend service..."
    docker-compose --profile "$profile" restart bejo-backend
}

estimate_model_size() {
    local model="$1"
    
    case "$model" in
        *"2b"*)
            print_info "📊 Estimasi ukuran: ~1.5GB"
            ;;
        *"3b"*)
            print_info "📊 Estimasi ukuran: ~2GB"
            ;;
        *"7b"*)
            print_info "📊 Estimasi ukuran: ~4GB"
            ;;
        *"8b"*)
            print_info "📊 Estimasi ukuran: ~5GB"
            ;;
        *"9b"*)
            print_info "📊 Estimasi ukuran: ~6GB"
            ;;
        *"13b"*)
            print_info "📊 Estimasi ukuran: ~8GB"
            ;;
        *"14b"*)
            print_info "📊 Estimasi ukuran: ~9GB"
            ;;
        *"27b"*)
            print_info "📊 Estimasi ukuran: ~16GB"
            ;;
        "nomic-embed-text")
            print_info "📊 Estimasi ukuran: ~274MB"
            ;;
        *)
            print_info "📊 Estimasi ukuran: Tidak diketahui"
            ;;
    esac
}

build_services() {
    local with_model=false
    local llm_model="$DEFAULT_LLM_MODEL"
    local embedding_model="$DEFAULT_EMBEDDING_MODEL"
    local compute_type="$DEFAULT_COMPUTE_TYPE"
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --with-model)
                with_model=true
                shift
                ;;
            --llm-model)
                llm_model="$2"
                shift 2
                ;;
            --embedding-model)
                embedding_model="$2"
                shift 2
                ;;
            --gpu)
                compute_type="gpu"
                shift
                ;;
            --cpu)
                compute_type="cpu"
                shift
                ;;
            *)
                shift
                ;;
        esac
    done
    
    local profile=$(get_compose_profile "$compute_type")
    
    print_info "Building services dengan konfigurasi:"
    print_info "  Compute: $compute_type"
    print_info "  Profile: $profile"
    print_info "  LLM Model: $llm_model"
    print_info "  Embedding Model: $embedding_model"
    
    # Set environment variables
    set_environment "$llm_model" "$embedding_model"
    
    # Build dan start services
    docker-compose --profile "$profile" up -d --build
    
    if [ "$with_model" = true ]; then
        print_info "Flag --with-model detected, akan download model..."
        sleep 5  # Wait for services to start
        pull_models --llm-model "$llm_model" --embedding-model "$embedding_model" --"$compute_type"
    else
        print_warning "Model tidak didownload. Jalankan '$0 pull-models' untuk download."
    fi
    
    print_success "Services berhasil dibangun dan dijalankan!"
    print_info "Backend available di: http://localhost:8000"
    print_info "Qdrant available di: http://localhost:6333"
    print_info "Ollama available di: http://localhost:11434"
}

start_services() {
    local llm_model="$DEFAULT_LLM_MODEL"
    local embedding_model="$DEFAULT_EMBEDDING_MODEL"
    local compute_type="$DEFAULT_COMPUTE_TYPE"
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --llm-model)
                llm_model="$2"
                shift 2
                ;;
            --embedding-model)
                embedding_model="$2"
                shift 2
                ;;
            --gpu)
                compute_type="gpu"
                shift
                ;;
            --cpu)
                compute_type="cpu"
                shift
                ;;
            *)
                shift
                ;;
        esac
    done
    
    local profile=$(get_compose_profile "$compute_type")
    
    print_info "Starting services dengan konfigurasi:"
    print_info "  Compute: $compute_type"
    print_info "  Profile: $profile"
    print_info "  LLM Model: $llm_model"
    print_info "  Embedding Model: $embedding_model"
    
    # Set environment variables
    set_environment "$llm_model" "$embedding_model"
    
    # Start services
    docker-compose --profile "$profile" up -d
    
    print_success "Services started!"
    print_info "Backend: http://localhost:8000"
    print_info "Qdrant: http://localhost:6333"
    print_info "Ollama: http://localhost:11434"
}

stop_services() {
    print_info "Stopping services..."
    
    # Stop both CPU and GPU profiles
    docker-compose --profile cpu down 2>/dev/null
    docker-compose --profile gpu down 2>/dev/null
    
    print_success "Services stopped!"
}

clean_services() {
    print_warning "Ini akan menghapus semua containers, images, dan volumes!"
    read -p "Apakah Anda yakin? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Cleaning up..."
        
        # Clean both profiles
        docker-compose --profile cpu down -v --rmi all 2>/dev/null
        docker-compose --profile gpu down -v --rmi all 2>/dev/null
        
        docker system prune -f
        print_success "Cleanup complete!"
    else
        print_info "Cleanup dibatalkan."
    fi
}

# Main script
case "$1" in
    build)
        shift
        build_services "$@"
        ;;
    pull-models)
        shift
        pull_models "$@"
        ;;
    start)
        shift
        start_services "$@"
        ;;
    stop)
        stop_services
        ;;
    clean)
        clean_services
        ;;
    check-models)
        check_models
        ;;
    list-models)
        list_models
        ;;
    --help|-h|help)
        show_help
        ;;
    *)
        print_error "Command tidak dikenali: $1"
        echo ""
        show_help
        exit 1
        ;;
esac